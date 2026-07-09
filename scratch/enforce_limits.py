import os

# Update main.py
main_path = "d:/Project/Python/webhook_forwarder/main.py"
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add limit checking logic in create_project
old_create_proj = """def create_project(project: schemas.ProjectCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    new_project = models.Project(name=project.name, description=project.description, user_id=current_user.id)
    db.add(new_project)"""

new_create_proj = """def create_project(project: schemas.ProjectCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # Check limits
    current_count = db.query(models.Project).filter(models.Project.user_id == current_user.id).count()
    if current_user.limit_projects is not None:
        max_projects = current_user.limit_projects
    else:
        max_projects = int(get_system_setting(db, "max_projects_per_user", "5"))
        
    if current_count >= max_projects:
        raise HTTPException(status_code=400, detail=f"Project limit reached. Maximum allowed is {max_projects}.")

    new_project = models.Project(name=project.name, description=project.description, user_id=current_user.id)
    db.add(new_project)"""

content = content.replace(old_create_proj, new_create_proj)

# 2. Add limit checking logic in create_endpoint
old_create_end = """def create_endpoint(endpoint: schemas.EndpointCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if not re.match(r"^[a-z0-9-]+$", endpoint.slug):
        raise HTTPException(status_code=400, detail="Slug can only contain lowercase letters, numbers, and hyphens")
        
    # Verify project belongs to user
    project, role = get_project_with_role(db, endpoint.project_id, current_user.id)
    if not project or role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="Not authorized to add endpoints to this project")"""

new_create_end = """def create_endpoint(endpoint: schemas.EndpointCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if not re.match(r"^[a-z0-9-]+$", endpoint.slug):
        raise HTTPException(status_code=400, detail="Slug can only contain lowercase letters, numbers, and hyphens")
        
    # Verify project belongs to user
    project, role = get_project_with_role(db, endpoint.project_id, current_user.id)
    if not project or role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="Not authorized to add endpoints to this project")
        
    # Check limits
    owner = db.query(models.User).filter(models.User.id == project.user_id).first()
    current_count = db.query(models.Endpoint).filter(models.Endpoint.project_id == project.id).count()
    
    if owner and owner.limit_endpoints is not None:
        max_endpoints = owner.limit_endpoints
    else:
        max_endpoints = int(get_system_setting(db, "max_endpoints_per_project", "10"))
        
    if current_count >= max_endpoints:
        raise HTTPException(status_code=400, detail=f"Endpoint limit reached for this project. Maximum allowed is {max_endpoints}.")"""

content = content.replace(old_create_end, new_create_end)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

# Update forwarder.py
fw_path = "d:/Project/Python/webhook_forwarder/forwarder.py"
with open(fw_path, "r", encoding="utf-8") as f:
    fw_content = f.read()

old_log_limit = """        # Enforce log limits
        try:
            max_logs = int(get_system_setting(db, "max_logs_per_endpoint", "1000"))
            log_count = db.query(models.DeliveryLog).filter(models.DeliveryLog.endpoint_id == endpoint_id).count()"""

new_log_limit = """        # Enforce log limits
        try:
            max_logs = int(get_system_setting(db, "max_logs_per_endpoint", "1000"))
            # Check user custom limit
            endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == endpoint_id).first()
            if endpoint and endpoint.project and endpoint.project.owner:
                owner = endpoint.project.owner
                if owner.limit_logs is not None:
                    max_logs = owner.limit_logs
            
            log_count = db.query(models.DeliveryLog).filter(models.DeliveryLog.endpoint_id == endpoint_id).count()"""

fw_content = fw_content.replace(old_log_limit, new_log_limit)

with open(fw_path, "w", encoding="utf-8") as f:
    f.write(fw_content)

print("Updated limits in main.py and forwarder.py")
