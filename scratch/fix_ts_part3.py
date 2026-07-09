import os

# Fix LiveLogs.tsx loadProjects call
ll_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/LiveLogs.tsx"
with open(ll_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("""    useEffect(() => {
        loadProjects();
    }, []);""", "")
    
with open(ll_path, "w", encoding="utf-8") as f:
    f.write(content)

# Fix Projects.tsx unused refreshProjects
pr_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/Projects.tsx"
with open(pr_path, "r", encoding="utf-8") as f:
    content = f.read()

# I will just write a simpler replace to ensure it is actually used, maybe the previous replace didn't match anything.
# Let's check how many times refreshProjects is in Projects.tsx.
content = content.replace("const { refreshProjects } = useProject();", "")
content = content.replace("await refreshProjects();\n            setNewProjectName('');", "setNewProjectName('');")
content = content.replace("refreshProjects();\n        } catch", "} catch")

with open(pr_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed TS errors part 3")
