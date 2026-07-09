from fastapi import FastAPI, Request, Depends, HTTPException, BackgroundTasks, status, WebSocket, WebSocketDisconnect, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import re
import json
import hmac
import hashlib
import base64

import models, schemas, forwarder, auth
from database import engine, get_db

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Webhook Forwarder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Webhook Receiver Route (Public) ---
@app.post("/webhook/{project_id}/{slug}")
@app.post("/webhook/{project_id}/{slug}/")
@app.get("/webhook/{project_id}/{slug}")
@app.get("/webhook/{project_id}/{slug}/")
async def receive_webhook(project_id: str, slug: str, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    endpoint = db.query(models.Endpoint).filter(models.Endpoint.slug == slug, models.Endpoint.project_id == project_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
        
    auth_type = endpoint.auth_type
    auth_config_str = endpoint.auth_config or "{}"
    try:
        auth_config = json.loads(auth_config_str)
    except:
        auth_config = {}

    # Meta (Facebook/WhatsApp) Verification Handshake
    if auth_type == "meta" and request.method == "GET" and request.query_params.get("hub.mode") == "subscribe":
        challenge = request.query_params.get("hub.challenge", "")
        verify_token = request.query_params.get("hub.verify_token", "")
        expected_token = auth_config.get("verify_token", "")
        
        if expected_token and verify_token != expected_token:
            raise HTTPException(status_code=403, detail="Invalid Meta verify token")
            
        return Response(content=challenge, media_type="text/plain")

    # Read raw body for HMAC and general payload processing
    body = await request.body()

    # Basic Auth Check
    if auth_type == "basic":
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Basic "):
            raise HTTPException(status_code=401, detail="Unauthorized: Missing Basic Auth")
        try:
            decoded = base64.b64decode(auth_header.split(" ")[1]).decode("utf-8")
            username, password = decoded.split(":", 1)
            if username != auth_config.get("username") or password != auth_config.get("password"):
                raise HTTPException(status_code=401, detail="Unauthorized: Invalid credentials")
        except:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid Basic Auth format")

    # Bearer Token Check
    if auth_type == "bearer":
        auth_header = request.headers.get("Authorization", "")
        query_token = request.query_params.get("token", "")
        expected_token = auth_config.get("token")
        
        token_valid = False
        if auth_header.startswith("Bearer ") and auth_header.split(" ")[1] == expected_token:
            token_valid = True
        elif query_token == expected_token:
            token_valid = True
            
        if not token_valid:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid Bearer token")

    # HMAC Signature Check
    if auth_type == "hmac":
        header_name = auth_config.get("header_name", "x-hub-signature")
        secret = auth_config.get("secret", "")
        algo_name = auth_config.get("algorithm", "sha256")
        
        signature = request.headers.get(header_name)
        if not signature:
            raise HTTPException(status_code=401, detail=f"Unauthorized: Missing {header_name} header")
            
        hash_func = hashlib.sha256 if algo_name == "sha256" else hashlib.sha1
        expected_mac = hmac.new(secret.encode('utf-8'), body, hash_func).hexdigest()
        
        # Sometimes signatures come with a prefix like 'sha256='
        actual_signature = signature.split("=")[-1]
        
        if not hmac.compare_digest(actual_signature, expected_mac):
            raise HTTPException(status_code=401, detail="Unauthorized: HMAC signature mismatch")

    try:
        if body:
            payload_data = json.loads(body.decode("utf-8"))
            payload = json.dumps(payload_data)
        else:
            payload = ""
    except Exception:
        payload = body.decode("utf-8", errors="replace")
        
    req_meta = {
        "http_method": request.method,
        "client_ip": request.client.host if request.client else None,
        "headers": json.dumps(dict(request.headers)),
        "query_params": json.dumps(dict(request.query_params))
    }
        
    destinations = db.query(models.Destination).filter(models.Destination.endpoint_id == endpoint.id).all()
    background_tasks.add_task(forwarder.forward_webhook, endpoint.id, payload, destinations, req_meta)
    
    return {"status": "success", "message": "Webhook received and queued for forwarding"}

# --- Auth API Routes ---
@app.post("/api/auth/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/auth/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user
@app.put("/api/auth/me", response_model=schemas.User)
def update_user(request: schemas.UserUpdateRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if not auth.verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )
    
    # Check if email is being changed
    if request.email and request.email != current_user.email:
        existing_user = db.query(models.User).filter(models.User.email == request.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = request.email
        
    if request.full_name is not None:
        current_user.full_name = request.full_name
    
    if request.new_password:
        current_user.hashed_password = auth.get_password_hash(request.new_password)
        
    db.commit()
    db.refresh(current_user)
    return current_user
@app.delete("/api/auth/me")
def delete_user(request: schemas.UserDeleteRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if not auth.verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )
    db.delete(current_user)
    db.commit()
    return {"status": "success", "message": "User deleted successfully"}

# --- Project API Routes ---
@app.get("/api/projects", response_model=List[schemas.Project])
def read_projects(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Project).filter(models.Project.user_id == current_user.id).all()

@app.post("/api/projects", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    new_project = models.Project(name=project.name, description=project.description, user_id=current_user.id)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@app.put("/api/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: str, project_data: schemas.ProjectCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.name = project_data.name
    project.description = project_data.description
    db.commit()
    db.refresh(project)
    return project

@app.get("/api/endpoints", response_model=List[schemas.Endpoint])
def read_endpoints(project_id: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db.query(models.Endpoint).filter(models.Endpoint.project_id == project_id).all()

@app.post("/api/endpoints", response_model=schemas.Endpoint)
def create_endpoint(endpoint: schemas.EndpointCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if not re.match(r"^[a-z0-9-]+$", endpoint.slug):
        raise HTTPException(status_code=400, detail="Slug can only contain lowercase letters, numbers, and hyphens")
        
    # Verify project belongs to user
    project = db.query(models.Project).filter(models.Project.id == endpoint.project_id, models.Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    db_endpoint = db.query(models.Endpoint).filter(models.Endpoint.slug == endpoint.slug, models.Endpoint.project_id == endpoint.project_id).first()
    if db_endpoint:
        raise HTTPException(status_code=400, detail="Slug already exists in this project")
    
    new_endpoint = models.Endpoint(
        name=endpoint.name, 
        slug=endpoint.slug, 
        project_id=endpoint.project_id,
        auth_type=endpoint.auth_type,
        auth_config=endpoint.auth_config
    )
    db.add(new_endpoint)
    db.commit()
    db.refresh(new_endpoint)
    return new_endpoint

@app.put("/api/endpoints/{endpoint_id}", response_model=schemas.Endpoint)
def update_endpoint(endpoint_id: int, endpoint_update: schemas.EndpointCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    endpoint = db.query(models.Endpoint).join(models.Project).filter(models.Endpoint.id == endpoint_id, models.Project.user_id == current_user.id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
        
    endpoint.name = endpoint_update.name
    endpoint.slug = endpoint_update.slug
    endpoint.auth_type = endpoint_update.auth_type
    endpoint.auth_config = endpoint_update.auth_config
    
    db.commit()
    db.refresh(endpoint)
    return endpoint

@app.post("/api/endpoints/{endpoint_id}/destinations", response_model=schemas.Destination)
def create_destination(endpoint_id: int, destination: schemas.DestinationCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    endpoint = db.query(models.Endpoint).join(models.Project).filter(models.Endpoint.id == endpoint_id, models.Project.user_id == current_user.id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    new_dest = models.Destination(url=destination.url, is_active=destination.is_active, endpoint_id=endpoint_id)
    db.add(new_dest)
    db.commit()
    db.refresh(new_dest)
    return new_dest

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"status": "success"}

@app.delete("/api/endpoints/{endpoint_id}")
def delete_endpoint(endpoint_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    endpoint = db.query(models.Endpoint).join(models.Project).filter(models.Endpoint.id == endpoint_id, models.Project.user_id == current_user.id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    db.delete(endpoint)
    db.commit()
    return {"status": "success"}

@app.get("/api/logs", response_model=List[schemas.DeliveryLog])
def get_logs(endpoint_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    endpoint = db.query(models.Endpoint).join(models.Project).filter(models.Endpoint.id == endpoint_id, models.Project.user_id == current_user.id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return db.query(models.DeliveryLog).filter(models.DeliveryLog.endpoint_id == endpoint_id).order_by(models.DeliveryLog.created_at.desc()).limit(100).all()

@app.delete("/api/logs/{log_id}")
def delete_log(log_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    log = db.query(models.DeliveryLog).join(models.Endpoint).join(models.Project).filter(
        models.DeliveryLog.id == log_id, 
        models.Project.user_id == current_user.id
    ).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    db.delete(log)
    db.commit()
    return {"status": "success"}

from ws_manager import manager

@app.websocket("/api/ws/logs/{endpoint_id}")
async def websocket_endpoint(websocket: WebSocket, endpoint_id: int):
    # Note: For production, we should authenticate the websocket connection
    # using a token passed in query params or headers.
    await manager.connect(websocket, endpoint_id)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, endpoint_id)

