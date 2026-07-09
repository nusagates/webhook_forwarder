import os
import re

layout_path = "d:/Project/Python/webhook_forwarder/frontend/src/components/Layout.tsx"
with open(layout_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add states
if "const [projectAnchorEl, setProjectAnchorEl]" not in content:
    content = content.replace("const [settingsMenuOpen, setSettingsMenuOpen] = useState(false);",
        "const [settingsMenuOpen, setSettingsMenuOpen] = useState(false);\n  const [projectAnchorEl, setProjectAnchorEl] = useState<null | HTMLElement>(null);")

# 2. Replace the Select UI with a Button + Menu
old_project_ui = """                <FormControl fullWidth size="small" sx={{ opacity: open ? 1 : 0, transition: 'opacity 0.2s', display: open ? 'block' : 'none' }}>
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
                )}"""

new_project_ui = """                <ListItemButton 
                    onClick={(e) => setProjectAnchorEl(e.currentTarget)}
                    sx={{ 
                        borderRadius: 1, 
                        border: open ? '1px solid #e0e0e0' : 'none',
                        justifyContent: open ? 'space-between' : 'center',
                        px: open ? 2 : 1,
                        py: 1
                    }}
                >
                    {open ? (
                        <>
                            <Box sx={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                                <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 'bold' }}>Active Project</Typography>
                                <Typography variant="body2" noWrap sx={{ fontWeight: 500 }}>
                                    {projects.find(p => p.id === selectedProjectId)?.name || 'Select Project'}
                                </Typography>
                            </Box>
                            <ExpandMore color="action" />
                        </>
                    ) : (
                        <StorageIcon color="action" />
                    )}
                </ListItemButton>
                
                <Menu
                    anchorEl={projectAnchorEl}
                    open={Boolean(projectAnchorEl)}
                    onClose={() => setProjectAnchorEl(null)}
                    PaperProps={{ sx: { width: 220, maxHeight: 300 } }}
                    anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
                    transformOrigin={{ vertical: 'bottom', horizontal: 'center' }}
                >
                    {projects.map((p) => (
                        <MenuItem 
                            key={p.id} 
                            selected={p.id === selectedProjectId}
                            onClick={() => {
                                setSelectedProjectId(p.id);
                                setProjectAnchorEl(null);
                            }}
                        >
                            <Typography noWrap>{p.name}</Typography>
                        </MenuItem>
                    ))}
                </Menu>"""

content = content.replace(old_project_ui, new_project_ui)

with open(layout_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated Layout.tsx with new Project Switcher UI")
