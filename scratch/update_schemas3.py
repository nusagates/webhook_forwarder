import os

schemas_path = "d:/Project/Python/webhook_forwarder/schemas.py"
with open(schemas_path, "r", encoding="utf-8") as f:
    content = f.read()

old_out = """    is_admin: bool
    is_blocked: bool
    limit_projects: Optional[int]"""

new_out = """    is_admin: bool
    is_blocked: bool
    block_reason: Optional[str]
    limit_projects: Optional[int]"""

old_update = """    is_admin: bool
    is_blocked: bool
    limit_projects: Optional[int] = None"""

new_update = """    is_admin: bool
    is_blocked: bool
    block_reason: Optional[str] = None
    limit_projects: Optional[int] = None"""

content = content.replace(old_out, new_out)
content = content.replace(old_update, new_update)

with open(schemas_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated schemas.py with block_reason")
