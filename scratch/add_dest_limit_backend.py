import os
import re

# 1. Update models.py
models_path = "d:/Project/Python/webhook_forwarder/models.py"
with open(models_path, "r", encoding="utf-8") as f:
    content = f.read()

if "limit_destinations" not in content:
    content = content.replace("limit_logs = Column(Integer, nullable=True)", "limit_logs = Column(Integer, nullable=True)\n    limit_destinations = Column(Integer, nullable=True)")
    with open(models_path, "w", encoding="utf-8") as f:
        f.write(content)

# 2. Update schemas.py if needed? Wait, if we return users, does schemas.User have limit_destinations?
schemas_path = "d:/Project/Python/webhook_forwarder/schemas.py"
with open(schemas_path, "r", encoding="utf-8") as f:
    schema_content = f.read()

if "limit_destinations" not in schema_content:
    schema_content = schema_content.replace("limit_logs: Optional[int] = None", "limit_logs: Optional[int] = None\n    limit_destinations: Optional[int] = None")
    with open(schemas_path, "w", encoding="utf-8") as f:
        f.write(schema_content)

# 3. Update main.py
main_path = "d:/Project/Python/webhook_forwarder/main.py"
with open(main_path, "r", encoding="utf-8") as f:
    main_content = f.read()

# Update create_destination
old_create_dest = """def create_destination(endpoint_id: str, dest: schemas.DestinationCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    project, role = get_project_with_role(db, endpoint_id, current_user.id, is_endpoint_id=True)
    if not project or role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="Not authorized to add destinations")
        
    new_dest = models.Destination(
        endpoint_id=endpoint_id,
        name=dest.name,
        url=dest.url,"""

new_create_dest = """def create_destination(endpoint_id: str, dest: schemas.DestinationCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    project, role = get_project_with_role(db, endpoint_id, current_user.id, is_endpoint_id=True)
    if not project or role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="Not authorized to add destinations")
        
    # Check limits
    owner = db.query(models.User).filter(models.User.id == project.user_id).first()
    current_count = db.query(models.Destination).filter(models.Destination.endpoint_id == endpoint_id).count()
    
    if owner and owner.limit_destinations is not None:
        max_dests = owner.limit_destinations
    else:
        max_dests = int(get_system_setting(db, "max_destinations_per_endpoint", "5"))
        
    if current_count >= max_dests:
        raise HTTPException(status_code=400, detail=f"Destination limit reached for this endpoint. Maximum allowed is {max_dests}.")
        
    new_dest = models.Destination(
        endpoint_id=endpoint_id,
        name=dest.name,
        url=dest.url,"""

main_content = main_content.replace(old_create_dest, new_create_dest)

# Update get_system_settings_api
old_settings = """"max_endpoints_per_project": int(get_system_setting(db, "max_endpoints_per_project", "10")),
        "max_logs_per_endpoint": int(get_system_setting(db, "max_logs_per_endpoint", "1000"))"""

new_settings = """"max_endpoints_per_project": int(get_system_setting(db, "max_endpoints_per_project", "10")),
        "max_logs_per_endpoint": int(get_system_setting(db, "max_logs_per_endpoint", "1000")),
        "max_destinations_per_endpoint": int(get_system_setting(db, "max_destinations_per_endpoint", "5"))"""

main_content = main_content.replace(old_settings, new_settings)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(main_content)

print("Updated models, schemas, and main.py for limit_destinations")
