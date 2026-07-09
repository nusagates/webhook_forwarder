import os

# Update App.tsx
app_path = "d:/Project/Python/webhook_forwarder/frontend/src/App.tsx"
with open(app_path, "r", encoding="utf-8") as f:
    app_content = f.read()

if "import UserManagement" not in app_content:
    app_content = app_content.replace("import SystemLimits from './pages/SystemLimits';",
        "import SystemLimits from './pages/SystemLimits';\nimport UserManagement from './pages/UserManagement';")
    app_content = app_content.replace("<Route path=\"settings/limits\" element={<SystemLimits />} />",
        "<Route path=\"settings/limits\" element={<SystemLimits />} />\n              <Route path=\"settings/users\" element={<UserManagement />} />")
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_content)

# Update Layout.tsx
layout_path = "d:/Project/Python/webhook_forwarder/frontend/src/components/Layout.tsx"
with open(layout_path, "r", encoding="utf-8") as f:
    layout_content = f.read()

if "import GroupIcon from '@mui/icons-material/Group';" not in layout_content:
    layout_content = layout_content.replace("import SpeedIcon from '@mui/icons-material/Speed';",
        "import SpeedIcon from '@mui/icons-material/Speed';\nimport GroupIcon from '@mui/icons-material/Group';")

old_limits_menu = """                  <ListItemButton sx={{ pl: open ? 4 : 2, justifyContent: open ? 'initial' : 'center' }} selected={location.pathname === '/settings/limits'} onClick={() => navigate('/settings/limits')}>
                    <ListItemIcon sx={{ minWidth: 0, mr: open ? 2 : 'auto' }}>
                      <SpeedIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Limits" sx={{ opacity: open ? 1 : 0 }} />
                  </ListItemButton>"""

new_users_menu = """                  <ListItemButton sx={{ pl: open ? 4 : 2, justifyContent: open ? 'initial' : 'center' }} selected={location.pathname === '/settings/limits'} onClick={() => navigate('/settings/limits')}>
                    <ListItemIcon sx={{ minWidth: 0, mr: open ? 2 : 'auto' }}>
                      <SpeedIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Limits" sx={{ opacity: open ? 1 : 0 }} />
                  </ListItemButton>
                  <ListItemButton sx={{ pl: open ? 4 : 2, justifyContent: open ? 'initial' : 'center' }} selected={location.pathname === '/settings/users'} onClick={() => navigate('/settings/users')}>
                    <ListItemIcon sx={{ minWidth: 0, mr: open ? 2 : 'auto' }}>
                      <GroupIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Users" sx={{ opacity: open ? 1 : 0 }} />
                  </ListItemButton>"""

if "onClick={() => navigate('/settings/users')}" not in layout_content:
    layout_content = layout_content.replace(old_limits_menu, new_users_menu)
    with open(layout_path, "w", encoding="utf-8") as f:
        f.write(layout_content)

print("Updated App.tsx and Layout.tsx successfully")
