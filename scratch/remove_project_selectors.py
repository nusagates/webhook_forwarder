import os
import re

def remove_project_select_endpoints():
    path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/Endpoints.tsx"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r'<FormControl fullWidth size="small"(?:[^>]*)>\s*<InputLabel id="project-select-label">Select Project Context</InputLabel>\s*<Select[\s\S]*?</FormControl>'
    content = re.sub(pattern, '', content)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def remove_project_select_livelogs():
    path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/LiveLogs.tsx"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r'<FormControl fullWidth size="small">\s*<InputLabel id="project-select-label">Select Project</InputLabel>\s*<Select[\s\S]*?</FormControl>'
    content = re.sub(pattern, '', content)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

remove_project_select_endpoints()
remove_project_select_livelogs()
print("Removed Project Selectors")
