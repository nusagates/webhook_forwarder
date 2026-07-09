import os

layout_path = "d:/Project/Python/webhook_forwarder/frontend/src/components/Layout.tsx"
with open(layout_path, "r", encoding="utf-8") as f:
    content = f.read()

# Imports
if "import { useProject } from '../contexts/ProjectContext';" not in content:
    content = content.replace("import DatabaseSettingsDialog from './DatabaseSettingsDialog';",
        "import DatabaseSettingsDialog from './DatabaseSettingsDialog';\nimport { useProject } from '../contexts/ProjectContext';\nimport Select from '@mui/material/Select';\nimport FormControl from '@mui/material/FormControl';\nimport InputLabel from '@mui/material/InputLabel';")

# useProject hook inside Layout
if "const { projects, selectedProjectId, setSelectedProjectId } = useProject();" not in content:
    content = content.replace("const [settingsMenuOpen, setSettingsMenuOpen] = useState(false);",
        "const [settingsMenuOpen, setSettingsMenuOpen] = useState(false);\n  const { projects, selectedProjectId, setSelectedProjectId } = useProject();")

# Project Switcher UI
project_switcher_ui = """        <List sx={{ mt: 'auto', mb: 2 }}>
          {/* Project Switcher */}
          {projects.length > 0 && (
            <ListItem sx={{ display: 'block', px: 2, mb: 2 }}>
                <FormControl fullWidth size="small" sx={{ opacity: open ? 1 : 0, transition: 'opacity 0.2s', display: open ? 'block' : 'none' }}>
                    <InputLabel id="project-select-label">Active Project</InputLabel>
                    <Select
                        labelId="project-select-label"
                        id="project-select"
                        value={selectedProjectId}
                        label="Active Project"
                        onChange={(e) => setSelectedProjectId(e.target.value as string)}
                    >
                        {projects.map((p) => (
                            <MenuItem key={p.id} value={p.id}>{p.name}</MenuItem>
                        ))}
                    </Select>
                </FormControl>
                {!open && (
                    <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                        <StorageIcon color="action" />
                    </Box>
                )}
            </ListItem>
          )}
          <Divider sx={{ mb: 1 }} />"""

content = content.replace("<List sx={{ mt: 'auto', mb: 2 }}>", project_switcher_ui)

with open(layout_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated Layout.tsx successfully")
