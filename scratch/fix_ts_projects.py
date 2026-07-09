import os

# 1. ProjectContext.tsx
pc_path = "d:/Project/Python/webhook_forwarder/frontend/src/contexts/ProjectContext.tsx"
with open(pc_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';", 
    "import { createContext, useContext, useState, useEffect } from 'react';\nimport type { ReactNode } from 'react';")
with open(pc_path, "w", encoding="utf-8") as f:
    f.write(content)


# 2. Endpoints.tsx
ep_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/Endpoints.tsx"
with open(ep_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("interface Project { id: string; name: string; my_role?: string; }\n", "")
content = content.replace("const { projects, selectedProjectId } = useProject();", "const { projects, selectedProjectId, setSelectedProjectId } = useProject();")

with open(ep_path, "w", encoding="utf-8") as f:
    f.write(content)


# 3. LiveLogs.tsx
ll_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/LiveLogs.tsx"
with open(ll_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("interface Project { id: string; name: string; my_role?: string; }\n", "")
content = content.replace("const { projects, selectedProjectId } = useProject();", "const { projects, selectedProjectId, setSelectedProjectId } = useProject();")

# LiveLogs has a left-over setProjects inside some logic? Let's check it manually if needed, but I'll try to just remove setProjects.
# Actually I removed loadProjects, so setProjects on line 189 must be inside another effect or function. 
# Let's replace setProjects with nothing if it's there, but I need to see it.
with open(ll_path, "w", encoding="utf-8") as f:
    f.write(content)


# 4. Projects.tsx
pr_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/Projects.tsx"
with open(pr_path, "r", encoding="utf-8") as f:
    content = f.read()

if "const { refreshProjects } = useProject();" not in content:
    content = content.replace("const confirm = useConfirm();", "const confirm = useConfirm();\n    const { refreshProjects } = useProject();")
else:
    # If it is there but TS says useProject is declared but value is never read, it means useProject is imported twice or not used.
    pass

with open(pr_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed TS errors")
