import os
import re

# Fix LiveLogs.tsx
livelogs_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/LiveLogs.tsx"
with open(livelogs_path, "r", encoding="utf-8") as f:
    content = f.read()

old_load_projects = """    const loadProjects = async () => {
        try { setProjects(await fetchApi('/api/projects')); }
        catch (err) { console.error(err); }
    };"""
content = content.replace(old_load_projects, "")

with open(livelogs_path, "w", encoding="utf-8") as f:
    f.write(content)

# Fix Projects.tsx
projects_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/Projects.tsx"
with open(projects_path, "r", encoding="utf-8") as f:
    content = f.read()

# I want to call refreshProjects() after a successful POST, PUT, DELETE of project
content = content.replace("fetchProjects();\n            closeDialog();", "fetchProjects();\n            refreshProjects();\n            closeDialog();")
content = content.replace("fetchProjects();\n        } catch", "fetchProjects();\n            refreshProjects();\n        } catch")

with open(projects_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed TS errors part 2")
