import os

main_path = "d:/Project/Python/webhook_forwarder/main.py"
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add get_system_setting after imports
helper_fn = """
def get_system_setting(db: Session, key: str, default: str):
    setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == key).first()
    if setting:
        return setting.value
    return default
"""

# Insert it before get_project_with_role or after auth import
if "def get_system_setting(" not in content:
    content = content.replace("def get_project_with_role(", helper_fn + "\ndef get_project_with_role(")

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Added get_system_setting to main.py")
