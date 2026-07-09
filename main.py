from fastapi import FastAPI, Request, Depends, HTTPException, BackgroundTasks, status, WebSocket, WebSocketDisconnect, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
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
def get_project_with_role(db: Session, project_id: str, user_id: int):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        return None, None
    if project.user_id == user_id:
        return project, "owner"
    
    member = db.query(models.ProjectMember).filter(models.ProjectMember.project_id == project_id, models.ProjectMember.user_id == user_id).first()
    if member:
        return project, member.role
    
    return None, None

@app.get("/api/projects", response_model=List[schemas.Project])
def read_projects(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    owned_projects = db.query(models.Project).filter(models.Project.user_id == current_user.id).all()
    for p in owned_projects:
        p.my_role = "owner"
        
    member_projects_records = db.query(models.ProjectMember).filter(models.ProjectMember.user_id == current_user.id).all()
    shared_projects = []
    for mp in member_projects_records:
        if mp.project:
            mp.project.my_role = mp.role
            shared_projects.append(mp.project)
            
    return owned_projects + shared_projects

@app.post("/api/projects", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    new_project = models.Project(name=project.name, description=project.description, user_id=current_user.id)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@app.put("/api/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: str, project_data: schemas.ProjectCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    project, role = get_project_with_role(db, project_id, current_user.id)
    if not project or role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="Not authorized to edit this project")
    
    project.name = project_data.name
    project.description = project_data.description
    db.commit()
    db.refresh(project)
    project.my_role = role
    return project

@app.get("/api/endpoints", response_model=List[schemas.Endpoint])
def read_endpoints(project_id: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    project, role = get_project_with_role(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=403, detail="Not authorized to view this project")
    return db.query(models.Endpoint).filter(models.Endpoint.project_id == project_id).all()

@app.post("/api/endpoints", response_model=schemas.Endpoint)
def create_endpoint(endpoint: schemas.EndpointCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if not re.match(r"^[a-z0-9-]+$", endpoint.slug):
        raise HTTPException(status_code=400, detail="Slug can only contain lowercase letters, numbers, and hyphens")
        
    # Verify project belongs to user
    project, role = get_project_with_role(db, endpoint.project_id, current_user.id)
    if not project or role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="Not authorized to create endpoints in this project")
        
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
    endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
        
    project, role = get_project_with_role(db, endpoint.project_id, current_user.id)
    if not project or role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="Not authorized to edit endpoints in this project")
        
    endpoint.name = endpoint_update.name
    endpoint.slug = endpoint_update.slug
    endpoint.auth_type = endpoint_update.auth_type
    endpoint.auth_config = endpoint_update.auth_config
    
    db.commit()
    db.refresh(endpoint)
    return endpoint

@app.post("/api/endpoints/{endpoint_id}/destinations", response_model=schemas.Destination)
def create_destination(endpoint_id: int, destination: schemas.DestinationCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
        
    project, role = get_project_with_role(db, endpoint.project_id, current_user.id)
    if not project or role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="Not authorized to add destinations in this project")
    
    new_dest = models.Destination(
        url=destination.url, 
        is_active=destination.is_active, 
        auth_type=destination.auth_type,
        auth_config=destination.auth_config,
        endpoint_id=endpoint_id
    )
    db.add(new_dest)
    db.commit()
    db.refresh(new_dest)
    return new_dest

@app.put("/api/endpoints/{endpoint_id}/destinations/{destination_id}", response_model=schemas.Destination)
def update_destination(endpoint_id: int, destination_id: int, destination_update: schemas.DestinationCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
        
    project, role = get_project_with_role(db, endpoint.project_id, current_user.id)
    if not project or role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="Not authorized to edit destinations in this project")
        
    destination = db.query(models.Destination).filter(models.Destination.id == destination_id, models.Destination.endpoint_id == endpoint_id).first()
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
        
    destination.url = destination_update.url
    destination.is_active = destination_update.is_active
    destination.auth_type = destination_update.auth_type
    destination.auth_config = destination_update.auth_config
    
    db.commit()
    db.refresh(destination)
    return destination

class TestDestinationRequest(BaseModel):
    url: str
    auth_type: str = "none"
    auth_config: Optional[str] = None

@app.post("/api/utils/test-destination")
async def test_destination(request: TestDestinationRequest, current_user: models.User = Depends(auth.get_current_user)):
    import httpx
    from pydantic import AnyHttpUrl
    import json
    import base64
    
    headers = {}
    auth_type = request.auth_type
    auth_config_str = request.auth_config or "{}"
    
    try:
        auth_config = json.loads(auth_config_str)
    except:
        auth_config = {}
        
    if auth_type == "basic":
        username = auth_config.get("username", "")
        password = auth_config.get("password", "")
        auth_str = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers["Authorization"] = f"Basic {auth_str}"
    elif auth_type == "bearer":
        token = auth_config.get("token", "")
        headers["Authorization"] = f"Bearer {token}"
    elif auth_type == "custom_header":
        header_name = auth_config.get("header_name", "")
        header_value = auth_config.get("header_value", "")
        if header_name:
            headers[header_name] = header_value
    elif auth_type == "query_param":
        param_name = auth_config.get("param_name", "")
        param_value = auth_config.get("param_value", "")
        if param_name:
            separator = "&" if "?" in request.url else "?"
            request.url = f"{request.url}{separator}{param_name}={param_value}"
    elif auth_type == "hmac":
        import hmac
        import hashlib
        header_name = auth_config.get("header_name", "X-Hub-Signature-256")
        secret = auth_config.get("secret", "")
        algorithm = auth_config.get("algorithm", "sha256")
        
        content_bytes = b"{}" # dummy payload for testing
        if algorithm == "sha256":
            signature = hmac.new(secret.encode(), content_bytes, hashlib.sha256).hexdigest()
            headers[header_name] = f"sha256={signature}"
        elif algorithm == "sha1":
            signature = hmac.new(secret.encode(), content_bytes, hashlib.sha1).hexdigest()
            headers[header_name] = f"sha1={signature}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(request.url, json={"test": True}, headers=headers)
            return {
                "status": "success", 
                "message": f"Connection successful. Server returned {res.status_code}",
                "status_code": res.status_code
            }
    except httpx.ConnectTimeout:
        raise HTTPException(status_code=400, detail="Connection timed out. Server might be down.")
    except httpx.RequestError as e:
        raise HTTPException(status_code=400, detail=f"Request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error connecting: {str(e)}")

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    project, role = get_project_with_role(db, project_id, current_user.id)
    if not project or role != "owner":
        raise HTTPException(status_code=403, detail="Only the owner can delete the project")
    db.delete(project)
    db.commit()
    return {"status": "success"}

@app.delete("/api/endpoints/{endpoint_id}")
def delete_endpoint(endpoint_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
        
    project, role = get_project_with_role(db, endpoint.project_id, current_user.id)
    if not project or role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete endpoints in this project")
    db.delete(endpoint)
    db.commit()
    return {"status": "success"}

@app.get("/api/logs", response_model=schemas.PaginatedLogs)
def get_logs(
    endpoint_id: int, 
    page: int = 1, 
    limit: int = 20, 
    sort: str = "desc", 
    current_user: models.User = Depends(auth.get_current_user), 
    db: Session = Depends(get_db)
):
    endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
        
    project, role = get_project_with_role(db, endpoint.project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=403, detail="Not authorized to view this project")
        
    query = db.query(models.DeliveryLog).filter(models.DeliveryLog.endpoint_id == endpoint_id)
    
    total = query.count()
    
    if sort == "asc":
        query = query.order_by(models.DeliveryLog.created_at.asc())
    else:
        query = query.order_by(models.DeliveryLog.created_at.desc())
        
    items = query.offset((page - 1) * limit).limit(limit).all()
    
    import math
    pages = math.ceil(total / limit) if total > 0 else 1
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": pages,
        "limit": limit
    }

@app.delete("/api/logs/{log_id}")
def delete_log(log_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    log = db.query(models.DeliveryLog).filter(models.DeliveryLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
        
    endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == log.endpoint_id).first()
    if endpoint:
        project, role = get_project_with_role(db, endpoint.project_id, current_user.id)
        if not project or role not in ["owner", "editor"]:
            raise HTTPException(status_code=403, detail="Not authorized to delete logs in this project")
    
    db.delete(log)
    db.commit()
    return {"status": "success"}

@app.delete("/api/endpoints/{endpoint_id}/logs")
def clear_logs(endpoint_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
        
    project, role = get_project_with_role(db, endpoint.project_id, current_user.id)
    if not project or role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="Not authorized to clear logs in this project")
        
    db.query(models.DeliveryLog).filter(models.DeliveryLog.endpoint_id == endpoint_id).delete()
    db.commit()
    return {"status": "success"}

@app.put("/api/logs/{log_id}/read")
def mark_log_read(log_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    log = db.query(models.DeliveryLog).filter(models.DeliveryLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
        
    endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == log.endpoint_id).first()
    if endpoint:
        project, role = get_project_with_role(db, endpoint.project_id, current_user.id)
        if not project or role not in ["owner", "editor", "viewer"]:
            raise HTTPException(status_code=403, detail="Not authorized")
            
    log.is_read = True
    db.commit()
    return {"status": "success"}

@app.put("/api/endpoints/{endpoint_id}/logs/read")
def mark_all_logs_read(endpoint_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
        
    project, role = get_project_with_role(db, endpoint.project_id, current_user.id)
    if not project or role not in ["owner", "editor", "viewer"]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db.query(models.DeliveryLog).filter(models.DeliveryLog.endpoint_id == endpoint_id, models.DeliveryLog.is_read == False).update({"is_read": True})
    db.commit()
    return {"status": "success"}

@app.post("/api/logs/{log_id}/resend")
async def resend_log(log_id: int, background_tasks: BackgroundTasks, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    log = db.query(models.DeliveryLog).filter(models.DeliveryLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
        
    endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == log.endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
        
    project, role = get_project_with_role(db, endpoint.project_id, current_user.id)
    if not project or role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="Not authorized to resend webhooks in this project")
        
    # Get active destinations for this endpoint
    destinations = db.query(models.Destination).filter(models.Destination.endpoint_id == endpoint.id, models.Destination.is_active == True).all()
    
    if not destinations:
        raise HTTPException(status_code=400, detail="No active destinations to resend to")

    req_meta = {
        "http_method": log.http_method,
        "client_ip": log.client_ip,
        "headers": log.headers,
        "query_params": log.query_params,
        "is_resend": True
    }
    
    from forwarder import forward_webhook
    background_tasks.add_task(forward_webhook, endpoint.id, log.payload, destinations, req_meta)
    
    return {"status": "success", "message": "Resend triggered"}

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


# --- Project Member Routes ---

@app.get("/api/projects/{project_id}/members", response_model=List[schemas.ProjectMember])
def get_project_members(project_id: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    project, role = get_project_with_role(db, project_id, current_user.id)
    if not project or role not in ["owner", "editor", "viewer"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this project")
    return db.query(models.ProjectMember).filter(models.ProjectMember.project_id == project_id).all()

@app.post("/api/projects/{project_id}/members", response_model=schemas.ProjectMember)
def add_project_member(project_id: str, member_in: schemas.ProjectMemberCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    project, role = get_project_with_role(db, project_id, current_user.id)
    if not project or role != "owner":
        raise HTTPException(status_code=403, detail="Only the owner can add members")
        
    target_user = db.query(models.User).filter(models.User.email == member_in.email).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User with this email not found")
        
    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot add yourself as a member")
        
    existing_member = db.query(models.ProjectMember).filter(models.ProjectMember.project_id == project_id, models.ProjectMember.user_id == target_user.id).first()
    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a member of this project")
        
    if member_in.role not in ["viewer", "editor"]:
        raise HTTPException(status_code=400, detail="Invalid role")
        
    new_member = models.ProjectMember(project_id=project_id, user_id=target_user.id, role=member_in.role)
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

@app.put("/api/projects/{project_id}/members/{member_id}", response_model=schemas.ProjectMember)
def update_project_member(project_id: str, member_id: int, member_in: schemas.ProjectMemberBase, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    project, role = get_project_with_role(db, project_id, current_user.id)
    if not project or role != "owner":
        raise HTTPException(status_code=403, detail="Only the owner can update members")
        
    member = db.query(models.ProjectMember).filter(models.ProjectMember.id == member_id, models.ProjectMember.project_id == project_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
        
    if member_in.role not in ["viewer", "editor"]:
        raise HTTPException(status_code=400, detail="Invalid role")
        
    member.role = member_in.role
    db.commit()
    db.refresh(member)
    return member

@app.delete("/api/projects/{project_id}/members/{member_id}")
def delete_project_member(project_id: str, member_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    project, role = get_project_with_role(db, project_id, current_user.id)
    if not project or role != "owner":
        raise HTTPException(status_code=403, detail="Only the owner can remove members")
        
    member = db.query(models.ProjectMember).filter(models.ProjectMember.id == member_id, models.ProjectMember.project_id == project_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
        
    db.delete(member)
    db.commit()
    return {"status": "success"}

@app.post("/api/projects/{project_id}/transfer")
def transfer_project_ownership(project_id: str, member_in: schemas.ProjectMemberCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    project, role = get_project_with_role(db, project_id, current_user.id)
    if not project or role != "owner":
        raise HTTPException(status_code=403, detail="Only the owner can transfer ownership")
        
    target_user = db.query(models.User).filter(models.User.email == member_in.email).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User with this email not found")
        
    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot transfer ownership to yourself")
        
    # Remove target user from project_members if they exist
    existing_member = db.query(models.ProjectMember).filter(models.ProjectMember.project_id == project_id, models.ProjectMember.user_id == target_user.id).first()
    if existing_member:
        db.delete(existing_member)
        
    # Transfer ownership
    project.user_id = target_user.id
    
    # Add current user as an editor so they don't lose access completely
    new_editor = models.ProjectMember(project_id=project_id, user_id=current_user.id, role="editor")
    db.add(new_editor)
    
    db.commit()
    return {"status": "success", "message": "Ownership transferred successfully"}

from pydantic import BaseModel
import os
from sqlalchemy import create_engine
from database import Base, get_db, SQLALCHEMY_DATABASE_URL
from models import User

class DbConfig(BaseModel):
    url: str

def check_super_admin(current_user: User):
    if current_user.id != 1:
        raise HTTPException(status_code=403, detail="Super Admin access required")

@app.get("/api/settings/db")
def get_db_settings(current_user: User = Depends(auth.get_current_user)):
    check_super_admin(current_user)
    
    # mask password if it's not sqlite
    url = SQLALCHEMY_DATABASE_URL
    masked_url = url
    if "://" in url and "@" in url:
        # e.g. postgresql://user:pass@host/db
        parts = url.split("://")
        auth_host = parts[1].split("@")
        if ":" in auth_host[0]:
            user, pw = auth_host[0].split(":", 1)
            masked_url = f"{parts[0]}://{user}:********@{auth_host[1]}"
            
    engine_type = "sqlite"
    if url.startswith("postgres"): engine_type = "postgresql"
    elif url.startswith("mysql"): engine_type = "mysql"
    
    return {
        "engine": engine_type,
        "url": masked_url,
        "raw_url": url # Only for super admin
    }

@app.post("/api/settings/db/test")
def test_db_connection(config: DbConfig, current_user: User = Depends(auth.get_current_user)):
    check_super_admin(current_user)
    try:
        test_engine = create_engine(config.url)
        with test_engine.connect() as conn:
            pass
        return {"status": "success", "message": "Connection successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

@app.post("/api/settings/db/create")
def create_database(config: DbConfig, current_user: User = Depends(auth.get_current_user)):
    check_super_admin(current_user)
    try:
        # Parse URL to get DB name and base URL
        # format: dialect://user:pass@host:port/dbname
        if config.url.startswith("sqlite"):
            return {"status": "success", "message": "SQLite database is a file and will be created automatically."}
            
        base_url, db_name = config.url.rsplit('/', 1)
        
        # Connect to server without db_name (connect to default db 'postgres' or 'mysql')
        if base_url.startswith("postgres"):
            admin_url = base_url + "/postgres"
        else:
            admin_url = base_url # MySQL connects without db
            
        test_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
        with test_engine.connect() as conn:
            conn.execute(f"CREATE DATABASE {db_name}")
            
        return {"status": "success", "message": f"Database '{db_name}' created successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create database: {str(e)}")

@app.post("/api/settings/db/migrate")
def migrate_database(config: DbConfig, current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    check_super_admin(current_user)
    try:
        # 1. Connect to new DB
        new_engine = create_engine(config.url)
        
        # 2. Create tables
        Base.metadata.create_all(new_engine)
        
        # 3. We cannot easily bulk copy using ORM dynamically because we have relationships.
        # But for a simple migration, we can fetch all records and insert them.
        from sqlalchemy.orm import sessionmaker
        NewSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=new_engine)
        new_db = NewSessionLocal()
        
        # In order of foreign key dependencies:
        import models
        tables = [
            models.User,
            models.Project,
            models.ProjectMember,
            models.Endpoint,
            models.Destination,
            models.DeliveryLog
        ]
        
        for table in tables:
            records = db.query(table).all()
            for record in records:
                # Expunge from old session and merge to new session
                db.expunge(record)
                from sqlalchemy.orm import make_transient
                make_transient(record)
                new_db.add(record)
            
            try:
                new_db.commit()
            except Exception as e:
                new_db.rollback()
                raise Exception(f"Failed to migrate table {table.__tablename__}: {str(e)}")
        
        new_db.close()
        
        # 4. Write to .env
        env_file = ".env"
        env_lines = []
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                env_lines = f.readlines()
                
        # Update or add SQLALCHEMY_DATABASE_URL
        found = False
        for i, line in enumerate(env_lines):
            if line.startswith("SQLALCHEMY_DATABASE_URL="):
                env_lines[i] = f"SQLALCHEMY_DATABASE_URL={config.url}\n"
                found = True
                break
        
        if not found:
            env_lines.append(f"\nSQLALCHEMY_DATABASE_URL={config.url}\n")
            
        with open(env_file, "w") as f:
            f.writelines(env_lines)
            
        return {"status": "success", "message": "Migration completed successfully. Please restart the backend service."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Migration failed: {str(e)}")



@app.post("/api/settings/restart")
def restart_server(current_user: User = Depends(auth.get_current_user)):
    check_super_admin(current_user)
    import threading
    import time
    import os
    import signal
    
    def kill_server():
        time.sleep(2)
        os.kill(os.getpid(), signal.SIGTERM)
        
    threading.Thread(target=kill_server).start()
    return {"status": "success", "message": "Restarting server in 2 seconds..."}

@app.get("/api/settings/system")
def get_system_settings_api(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    check_super_admin(current_user)
    return {
        "max_projects_per_user": int(get_system_setting(db, "max_projects_per_user", "5")),
        "max_endpoints_per_project": int(get_system_setting(db, "max_endpoints_per_project", "10")),
        "max_logs_per_endpoint": int(get_system_setting(db, "max_logs_per_endpoint", "1000"))
    }

@app.put("/api/settings/system")
def update_system_settings_api(settings: schemas.SystemSettingUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    check_super_admin(current_user)
    
    settings_dict = {
        "max_projects_per_user": str(settings.max_projects_per_user),
        "max_endpoints_per_project": str(settings.max_endpoints_per_project),
        "max_logs_per_endpoint": str(settings.max_logs_per_endpoint)
    }
    
    for key, value in settings_dict.items():
        db_setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == key).first()
        if db_setting:
            db_setting.value = value
        else:
            db_setting = models.SystemSetting(key=key, value=value)
            db.add(db_setting)
            
    db.commit()
    return {"status": "success"}


@app.get("/api/admin/users", response_model=List[schemas.UserOutAdmin])
def get_all_users(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    check_super_admin(current_user)
    users = db.query(models.User).all()
    # Ensure user ID 1 is marked as admin
    for u in users:
        if u.id == 1:
            u.is_admin = True
    return users

@app.put("/api/admin/users/{user_id}", response_model=schemas.UserOutAdmin)
def update_user_admin(user_id: int, user_update: schemas.UserAdminUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    check_super_admin(current_user)
    if user_id == 1:
        raise HTTPException(status_code=400, detail="Cannot modify the primary super admin")
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot modify your own admin status")
        
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    db_user.is_admin = user_update.is_admin
    db_user.is_blocked = user_update.is_blocked
    if user_update.is_blocked:
        db_user.block_reason = user_update.block_reason
    else:
        db_user.block_reason = None
    db_user.limit_projects = user_update.limit_projects
    db_user.limit_endpoints = user_update.limit_endpoints
    db_user.limit_logs = user_update.limit_logs
    
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/api/endpoints/{endpoint_id}/reactivate")
def reactivate_endpoint(endpoint_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
        
    project, role = get_project_with_role(db, endpoint.project_id, current_user.id)
    if not project or role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    endpoint.is_active = True
    # Reset rate limit in memory just in case
    if endpoint.slug in RATE_LIMITS:
        RATE_LIMITS[endpoint.slug] = []
        
    db.commit()
    return {"status": "success"}
