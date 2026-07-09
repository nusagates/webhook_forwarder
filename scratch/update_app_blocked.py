import os

app_path = "d:/Project/Python/webhook_forwarder/frontend/src/App.tsx"
with open(app_path, "r", encoding="utf-8") as f:
    content = f.read()

if "import Blocked from './pages/Blocked';" not in content:
    content = content.replace("import UserManagement from './pages/UserManagement';",
        "import UserManagement from './pages/UserManagement';\nimport Blocked from './pages/Blocked';")
    content = content.replace("<Route path=\"/login\" element={<Login />} />",
        "<Route path=\"/login\" element={<Login />} />\n        <Route path=\"/blocked\" element={<Blocked />} />")
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(content)
print("Updated App.tsx successfully")
