import os
import re

# 1. Update main.tsx
main_path = "d:/Project/Python/webhook_forwarder/frontend/src/main.tsx"
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

if "ConfirmProvider" not in content:
    content = content.replace("import App from './App.tsx'", "import App from './App.tsx'\nimport { ConfirmProvider } from './components/ConfirmDialog';")
    content = content.replace("<App />", "<ConfirmProvider>\n    <App />\n    </ConfirmProvider>")
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(content)

def replace_in_file(filepath, replacements, import_statement):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    
    if "useConfirm" not in text:
        # Add import
        if "import {" in text:
            text = text.replace("import {", import_statement + "\nimport {", 1)
        else:
            text = import_statement + "\n" + text
            
        # Add hook inside component
        # Find the main component function signature
        # e.g., export default function Projects() {
        # or const DatabaseSettingsDialog = ({ open, onClose }: any) => {
        match = re.search(r'(export default function \w+\(.*?\)\s*{|const \w+ = \(.*?\)\s*=>\s*{)', text)
        if match:
            insert_pos = match.end()
            text = text[:insert_pos] + "\n    const confirm = useConfirm();\n" + text[insert_pos:]
            
    for old, new in replacements:
        text = text.replace(old, new)
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

# 2. Update DatabaseSettingsDialog.tsx
replace_in_file(
    "d:/Project/Python/webhook_forwarder/frontend/src/components/DatabaseSettingsDialog.tsx",
    [('if (!confirm("Are you sure you want to migrate all data to the new database? This process may take a while depending on your log volume.")) return;',
      'if (!await confirm({ message: "Are you sure you want to migrate all data to the new database? This process may take a while depending on your log volume.", isDanger: true })) return;')],
    "import { useConfirm } from './ConfirmDialog';"
)

# 3. Update ProjectShareDialog.tsx
replace_in_file(
    "d:/Project/Python/webhook_forwarder/frontend/src/components/ProjectShareDialog.tsx",
    [("if (!confirm('Are you sure you want to remove this member?')) return;",
      "if (!await confirm({ message: 'Are you sure you want to remove this member?', isDanger: true })) return;"),
     ("if (!confirm('DANGER: Are you sure you want to transfer ownership? You will lose Owner privileges.')) return;",
      "if (!await confirm({ message: 'DANGER: Are you sure you want to transfer ownership? You will lose Owner privileges.', isDanger: true })) return;")],
    "import { useConfirm } from './ConfirmDialog';"
)

# 4. Update Endpoints.tsx
replace_in_file(
    "d:/Project/Python/webhook_forwarder/frontend/src/pages/Endpoints.tsx",
    [("if (!confirm('Delete this endpoint?')) return;",
      "if (!await confirm({ message: 'Delete this endpoint?', isDanger: true })) return;"),
     ("if (!confirm('Remove this destination?')) return;",
      "if (!await confirm({ message: 'Remove this destination?', isDanger: true })) return;")],
    "import { useConfirm } from '../components/ConfirmDialog';"
)

# 5. Update Projects.tsx
replace_in_file(
    "d:/Project/Python/webhook_forwarder/frontend/src/pages/Projects.tsx",
    [("if (!confirm('Are you sure you want to delete this project? All endpoints and destinations will be lost!')) return;",
      "if (!await confirm({ message: 'Are you sure you want to delete this project? All endpoints and destinations will be lost!', isDanger: true })) return;")],
    "import { useConfirm } from '../components/ConfirmDialog';"
)

# 6. Update UserManagement.tsx
replace_in_file(
    "d:/Project/Python/webhook_forwarder/frontend/src/pages/UserManagement.tsx",
    [("if (!confirm(`Are you sure you want to ${user.is_admin ? 'revoke' : 'grant'} Admin rights for ${user.email}?`)) return;",
      "if (!await confirm({ message: `Are you sure you want to ${user.is_admin ? 'revoke' : 'grant'} Admin rights for ${user.email}?`, isDanger: true })) return;"),
     ("if (!confirm(`Are you sure you want to ${user.is_blocked ? 'unblock' : 'block'} ${user.email}?`)) return;",
      "if (!await confirm({ message: `Are you sure you want to ${user.is_blocked ? 'unblock' : 'block'} ${user.email}?`, isDanger: true })) return;")],
    "import { useConfirm } from '../components/ConfirmDialog';"
)

print("Replaced all confirm() usages")
