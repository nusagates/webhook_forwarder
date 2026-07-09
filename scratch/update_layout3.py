import os

file_path = "d:/Project/Python/webhook_forwarder/frontend/src/components/Layout.tsx"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix Unused Imports
content = content.replace("import AccountCircleIcon from '@mui/icons-material/AccountCircle';", "")

# Fix the bottom sidebar
old_bottom = """        <Divider />
        <List>
          <ListItem disablePadding sx={{ display: 'block' }}>
            <ListItemButton
              sx={{ minHeight: 48, justifyContent: open ? 'initial' : 'center', px: 2.5 }}
              onClick={handleLogout}
            >
              <ListItemIcon sx={{ minWidth: 0, mr: open ? 3 : 'auto', justifyContent: 'center', color: '#d32f2f' }}>
                <LogoutIcon />
              </ListItemIcon>
              <ListItemText primary="Logout" sx={{ opacity: open ? 1 : 0, color: '#d32f2f' }} />
            </ListItemButton>
          </ListItem>
        </List>"""

new_bottom = """        <Divider />
        <List sx={{ mt: 'auto', mb: 2 }}>
          {user && user.id === 1 && (
            <>
              <ListItem disablePadding sx={{ display: 'block' }}>
                <ListItemButton onClick={() => setSettingsMenuOpen(!settingsMenuOpen)} sx={{ minHeight: 48, justifyContent: open ? 'initial' : 'center', px: 2.5 }}>
                  <ListItemIcon sx={{ minWidth: 0, mr: open ? 3 : 'auto', justifyContent: 'center' }}>
                    <SettingsIcon />
                  </ListItemIcon>
                  <ListItemText primary="Settings" sx={{ opacity: open ? 1 : 0 }} />
                  {open ? (settingsMenuOpen ? <ExpandLess /> : <ExpandMore />) : null}
                </ListItemButton>
              </ListItem>
              <Collapse in={settingsMenuOpen && open} timeout="auto" unmountOnExit>
                <List component="div" disablePadding>
                  <ListItemButton sx={{ pl: open ? 4 : 2, justifyContent: open ? 'initial' : 'center' }} onClick={() => setSettingsOpen(true)}>
                    <ListItemIcon sx={{ minWidth: 0, mr: open ? 2 : 'auto' }}>
                      <StorageIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Database" primaryTypographyProps={{ fontSize: '0.9rem' }} sx={{ opacity: open ? 1 : 0 }} />
                  </ListItemButton>
                  <ListItemButton sx={{ pl: open ? 4 : 2, justifyContent: open ? 'initial' : 'center' }} selected={location.pathname === '/settings/limits'} onClick={() => navigate('/settings/limits')}>
                    <ListItemIcon sx={{ minWidth: 0, mr: open ? 2 : 'auto' }}>
                      <SpeedIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Limits" primaryTypographyProps={{ fontSize: '0.9rem' }} sx={{ opacity: open ? 1 : 0 }} />
                  </ListItemButton>
                </List>
              </Collapse>
            </>
          )}
        </List>"""

if "onClick={handleLogout}" in content:
    content = content.replace(old_bottom, new_bottom)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated Layout.tsx successfully")
