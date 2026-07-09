import os

schemas_path = "d:/Project/Python/webhook_forwarder/schemas.py"
with open(schemas_path, "r", encoding="utf-8") as f:
    content = f.read()

new_schemas = """
class UserOutAdmin(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_admin: bool
    is_blocked: bool
    limit_projects: Optional[int]
    limit_endpoints: Optional[int]
    limit_logs: Optional[int]
    
    class Config:
        orm_mode = True

class UserAdminUpdate(BaseModel):
    is_admin: bool
    is_blocked: bool
    limit_projects: Optional[int] = None
    limit_endpoints: Optional[int] = None
    limit_logs: Optional[int] = None
"""

if "class UserOutAdmin" not in content:
    content += "\n" + new_schemas

with open(schemas_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated schemas.py successfully")
