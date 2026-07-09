import os

main_path = "d:/Project/Python/webhook_forwarder/main.py"
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# Make sure we don't duplicate
if "@app.get(\"/api/admin/users\"" not in content:
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
    content += "\n" + user_management_api

if "@app.post(\"/api/endpoints/{endpoint_id}/reactivate\")" not in content:
    reactivate_api = """
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
"""
    content += "\n" + reactivate_api

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Appended missing routes to main.py")
