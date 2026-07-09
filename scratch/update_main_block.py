import os

main_path = "d:/Project/Python/webhook_forwarder/main.py"
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

old_update_user = """    db_user.is_admin = user_update.is_admin
    db_user.is_blocked = user_update.is_blocked
    db_user.limit_projects = user_update.limit_projects"""

new_update_user = """    db_user.is_admin = user_update.is_admin
    db_user.is_blocked = user_update.is_blocked
    if user_update.is_blocked:
        db_user.block_reason = user_update.block_reason
    else:
        db_user.block_reason = None
    db_user.limit_projects = user_update.limit_projects"""

content = content.replace(old_update_user, new_update_user)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated main.py with block_reason")
