import os

pr_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/Projects.tsx"
with open(pr_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("import { useProject } from '../contexts/ProjectContext';", "")

with open(pr_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Removed unused import in Projects.tsx")
