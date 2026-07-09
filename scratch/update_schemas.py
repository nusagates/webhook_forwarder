import os

schemas_path = "d:/Project/Python/webhook_forwarder/schemas.py"
with open(schemas_path, "r", encoding="utf-8") as f:
    content = f.read()

new_schema = """
class SystemSettingUpdate(BaseModel):
    max_projects_per_user: int
    max_endpoints_per_project: int
    max_logs_per_endpoint: int
"""

if "class SystemSettingUpdate" not in content:
    content += "\n" + new_schema

with open(schemas_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Added SystemSettingUpdate to schemas.py")
