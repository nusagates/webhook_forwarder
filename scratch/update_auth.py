import os

auth_path = "d:/Project/Python/webhook_forwarder/auth.py"
with open(auth_path, "r", encoding="utf-8") as f:
    content = f.read()

old_auth_check = """    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user"""

new_auth_check = """    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    if user.is_blocked:
        raise HTTPException(status_code=403, detail="Your account has been blocked by an administrator.")
    return user"""

content = content.replace(old_auth_check, new_auth_check)

with open(auth_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated auth.py successfully")
