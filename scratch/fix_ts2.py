import os

# Fix Blocked.tsx textTransform
blocked_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/Blocked.tsx"
with open(blocked_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('textTransform="uppercase" sx={{ fontWeight: "bold" }}', 'sx={{ textTransform: "uppercase", fontWeight: "bold" }}')

with open(blocked_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed TS errors")
