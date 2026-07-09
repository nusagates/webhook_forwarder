import os
import re

projects_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/Projects.tsx"
with open(projects_path, "r", encoding="utf-8") as f:
    content = f.read()

if "import { useProject } from '../contexts/ProjectContext';" not in content:
    content = content.replace("import { fetchApi } from '../api';", "import { fetchApi } from '../api';\nimport { useProject } from '../contexts/ProjectContext';")

if "const { refreshProjects } = useProject();" not in content:
    content = content.replace("const confirmDialog = useConfirm();", "const confirmDialog = useConfirm();\n    const { refreshProjects } = useProject();")

content = content.replace("await fetchProjects();\n            setNewProjectName('');", "await fetchProjects();\n            await refreshProjects();\n            setNewProjectName('');")
content = content.replace("fetchProjects();\n        } catch", "fetchProjects();\n            refreshProjects();\n        } catch")

with open(projects_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated Projects.tsx successfully")
