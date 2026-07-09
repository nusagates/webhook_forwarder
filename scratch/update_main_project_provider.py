import os

main_path = "d:/Project/Python/webhook_forwarder/frontend/src/main.tsx"
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

if "ProjectProvider" not in content:
    content = content.replace("import { ConfirmProvider } from './components/ConfirmDialog';",
        "import { ConfirmProvider } from './components/ConfirmDialog';\nimport { ProjectProvider } from './contexts/ProjectContext';")
    content = content.replace("<ConfirmProvider>\n    <App />\n    </ConfirmProvider>",
        "<ConfirmProvider>\n      <ProjectProvider>\n        <App />\n      </ProjectProvider>\n    </ConfirmProvider>")
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(content)
print("Updated main.tsx successfully")
