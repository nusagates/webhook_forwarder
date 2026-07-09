import os

main_path = "d:/Project/Python/webhook_forwarder/main.py"
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update check_super_admin
old_check_admin = """def check_super_admin(current_user: models.User):
    if current_user.id != 1:
        raise HTTPException(status_code=403, detail="Super Admin access required")"""

new_check_admin = """def check_super_admin(current_user: models.User):
    if current_user.id != 1 and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")"""

content = content.replace(old_check_admin, new_check_admin)

# 2. Add API for User Management
user_management_api = """
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
    db_user.limit_projects = user_update.limit_projects
    db_user.limit_endpoints = user_update.limit_endpoints
    db_user.limit_logs = user_update.limit_logs
    
    db.commit()
    db.refresh(db_user)
    return db_user
"""

if "@app.get(\"/api/admin/users\"" not in content:
    content = content.replace("if __name__ == \"__main__\":", user_management_api + "\nif __name__ == \"__main__\":")

# 3. Update limit enforcement in create_project
old_create_project = """    max_projects = int(get_system_setting(db, "max_projects_per_user", "5"))
    current_count = db.query(models.Project).filter(models.Project.user_id == current_user.id).count()"""

new_create_project = """    if current_user.is_blocked:
        raise HTTPException(status_code=403, detail="Your account is blocked.")
    max_projects = current_user.limit_projects if current_user.limit_projects is not None else int(get_system_setting(db, "max_projects_per_user", "5"))
    current_count = db.query(models.Project).filter(models.Project.user_id == current_user.id).count()"""

content = content.replace(old_create_project, new_create_project)

# 4. Update limit enforcement in create_endpoint
old_create_endpoint = """    max_endpoints = int(get_system_setting(db, "max_endpoints_per_project", "10"))
    current_count = db.query(models.Endpoint).filter(models.Endpoint.project_id == project_id).count()"""

new_create_endpoint = """    if current_user.is_blocked:
        raise HTTPException(status_code=403, detail="Your account is blocked.")
    max_endpoints = current_user.limit_endpoints if current_user.limit_endpoints is not None else int(get_system_setting(db, "max_endpoints_per_project", "10"))
    current_count = db.query(models.Endpoint).filter(models.Endpoint.project_id == project_id).count()"""

content = content.replace(old_create_endpoint, new_create_endpoint)

# 5. Smart Rate Limiting for Webhooks
# Find the webhook endpoint
old_webhook_def = """@app.post("/webhook/{slug}")
@app.get("/webhook/{slug}")
@app.put("/webhook/{slug}")
@app.delete("/webhook/{slug}")
@app.patch("/webhook/{slug}")
async def handle_webhook(slug: str, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    endpoint = db.query(models.Endpoint).filter(models.Endpoint.slug == slug).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")"""

new_webhook_def = """import time
from collections import defaultdict

# Rate limiter memory store: slug -> list of timestamps
RATE_LIMITS = defaultdict(list)
# Track suspensions: slug -> suspended_until (timestamp)
SUSPENSIONS = {}

@app.post("/webhook/{slug}")
@app.get("/webhook/{slug}")
@app.put("/webhook/{slug}")
@app.delete("/webhook/{slug}")
@app.patch("/webhook/{slug}")
async def handle_webhook(slug: str, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    endpoint = db.query(models.Endpoint).filter(models.Endpoint.slug == slug).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
        
    if not endpoint.is_active:
        raise HTTPException(status_code=403, detail="This webhook endpoint is inactive or has been suspended due to abuse.")
        
    # Smart Rate Limiting Logic
    now = time.time()
    
    # Clean up old timestamps (older than 60 seconds)
    RATE_LIMITS[slug] = [ts for ts in RATE_LIMITS[slug] if now - ts < 60]
    
    # 60 requests per minute threshold
    if len(RATE_LIMITS[slug]) >= 60:
        # Suspend the endpoint if it is being hit way too fast (e.g. 100 requests in a minute)
        if len(RATE_LIMITS[slug]) >= 100:
            endpoint.is_active = False
            db.commit()
            print(f"Endpoint {slug} automatically suspended due to severe abuse.")
            raise HTTPException(status_code=429, detail="Rate limit severely exceeded. Endpoint has been suspended.")
        
        # Standard rate limit response
        raise HTTPException(status_code=429, detail="Too many requests. Limit is 60 requests per minute.")
        
    RATE_LIMITS[slug].append(now)
"""

if "RATE_LIMITS = defaultdict(list)" not in content:
    content = content.replace(old_webhook_def, new_webhook_def)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated main.py successfully")
