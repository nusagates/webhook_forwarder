import os

main_path = "d:/Project/Python/webhook_forwarder/main.py"
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add get_setting helper
get_setting_func = """
def get_system_setting(db: Session, key: str, default: str):
    setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == key).first()
    if setting:
        return setting.value
    return default
"""
if "def get_system_setting" not in content:
    content = content.replace("app = FastAPI()", "app = FastAPI()\n\n" + get_setting_func)

# 1. Update create_project
old_create_project = """
@app.post("/api/projects", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_project = models.Project(name=project.name, description=project.description, user_id=current_user.id)
"""
new_create_project = """
@app.post("/api/projects", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    max_projects = int(get_system_setting(db, "max_projects_per_user", "5"))
    current_count = db.query(models.Project).filter(models.Project.user_id == current_user.id).count()
    if current_count >= max_projects:
        raise HTTPException(status_code=400, detail=f"Limit reached: You can only create up to {max_projects} projects.")

    db_project = models.Project(name=project.name, description=project.description, user_id=current_user.id)
"""
content = content.replace(old_create_project, new_create_project)

# 2. Update create_endpoint
old_create_endpoint = """
@app.post("/api/projects/{project_id}/endpoints", response_model=schemas.Endpoint)
def create_endpoint(project_id: str, endpoint: schemas.EndpointCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    project, role = get_project_with_role(db, project_id, current_user.id)
    if not project or role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="Not authorized to add endpoints")
"""
new_create_endpoint = """
@app.post("/api/projects/{project_id}/endpoints", response_model=schemas.Endpoint)
def create_endpoint(project_id: str, endpoint: schemas.EndpointCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    project, role = get_project_with_role(db, project_id, current_user.id)
    if not project or role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="Not authorized to add endpoints")
        
    max_endpoints = int(get_system_setting(db, "max_endpoints_per_project", "10"))
    current_count = db.query(models.Endpoint).filter(models.Endpoint.project_id == project_id).count()
    if current_count >= max_endpoints:
        raise HTTPException(status_code=400, detail=f"Limit reached: You can only create up to {max_endpoints} endpoints per project.")
"""
content = content.replace(old_create_endpoint, new_create_endpoint)

# 3. Add Settings APIs
settings_api = """
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
"""

if "@app.get(\"/api/settings/system\")" not in content:
    if "if __name__ == \"__main__\":" in content:
        content = content.replace("if __name__ == \"__main__\":", settings_api + "\nif __name__ == \"__main__\":")
    else:
        content += "\n" + settings_api

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated main.py successfully")
