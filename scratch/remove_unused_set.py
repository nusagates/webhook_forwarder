import os

def remove_unused_set_selected():
    # Endpoints
    path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/Endpoints.tsx"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("const { projects, selectedProjectId, setSelectedProjectId } = useProject();", "const { projects, selectedProjectId } = useProject();")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        
    # LiveLogs
    path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/LiveLogs.tsx"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("const { projects, selectedProjectId, setSelectedProjectId } = useProject();", "const { projects, selectedProjectId } = useProject();")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

remove_unused_set_selected()
print("Removed unused setSelectedProjectId")
