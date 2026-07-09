import os

models_path = "d:/Project/Python/webhook_forwarder/models.py"
with open(models_path, "r", encoding="utf-8") as f:
    content = f.read()

old_user = """    is_admin = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    limit_projects = Column(Integer, nullable=True)"""

new_user = """    is_admin = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    block_reason = Column(String, nullable=True)
    limit_projects = Column(Integer, nullable=True)"""

content = content.replace(old_user, new_user)

with open(models_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated models.py with block_reason")
