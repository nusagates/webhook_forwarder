import os

file_path = "d:/Project/Python/webhook_forwarder/frontend/src/App.tsx"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

if "import SystemLimits from './pages/SystemLimits';" not in content:
    content = content.replace("import Profile from './pages/Profile';",
        "import Profile from './pages/Profile';\nimport SystemLimits from './pages/SystemLimits';")

if "<Route path=\"settings/limits\" element={<SystemLimits />} />" not in content:
    content = content.replace("<Route path=\"profile\" element={<Profile />} />",
        "<Route path=\"profile\" element={<Profile />} />\n              <Route path=\"settings/limits\" element={<SystemLimits />} />")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated App.tsx successfully")
