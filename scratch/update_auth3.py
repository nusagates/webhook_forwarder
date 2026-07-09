import os

auth_path = "d:/Project/Python/webhook_forwarder/auth.py"
with open(auth_path, "r", encoding="utf-8") as f:
    content = f.read()

old_auth = """    if user.is_blocked:
        raise HTTPException(status_code=401, detail="Your account has been blocked by an administrator.")
    return user"""

new_auth = """    if user.is_blocked:
        raise HTTPException(status_code=403, detail={"code": "ACCOUNT_BLOCKED", "reason": user.block_reason or "No reason provided."})
    return user"""

content = content.replace(old_auth, new_auth)

with open(auth_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated auth.py with ACCOUNT_BLOCKED")
