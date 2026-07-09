import os

# Fix Blocked.tsx
blocked_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/Blocked.tsx"
with open(blocked_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("import { useNavigate } from 'react-router-dom';", "")
content = content.replace("const navigate = useNavigate();\n    ", "")
content = content.replace('fontWeight="bold" gutterBottom', 'sx={{ fontWeight: "bold" }} gutterBottom')
content = content.replace('paragraph', 'sx={{ mb: 2 }}')
content = content.replace('textTransform="uppercase" fontWeight="bold" gutterBottom', 'sx={{ textTransform: "uppercase", fontWeight: "bold" }} gutterBottom')
content = content.replace('fontWeight={500}', 'sx={{ fontWeight: 500 }}')

with open(blocked_path, "w", encoding="utf-8") as f:
    f.write(content)

# Fix UserManagement.tsx
user_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/UserManagement.tsx"
with open(user_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('<Typography paragraph>', '<Typography sx={{ mb: 2 }}>')

with open(user_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed TS errors")
