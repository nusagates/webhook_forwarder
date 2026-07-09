import os

file_path = "d:/Project/Python/webhook_forwarder/frontend/src/components/Layout.tsx"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Imports
if "import Avatar from '@mui/material/Avatar';" not in content:
    content = content.replace("import SettingsIcon from '@mui/icons-material/Settings';", 
        "import SettingsIcon from '@mui/icons-material/Settings';\nimport Avatar from '@mui/material/Avatar';\nimport Menu from '@mui/material/Menu';\nimport MenuItem from '@mui/material/MenuItem';\nimport Collapse from '@mui/material/Collapse';\nimport ExpandLess from '@mui/icons-material/ExpandLess';\nimport ExpandMore from '@mui/icons-material/ExpandMore';\nimport StorageIcon from '@mui/icons-material/Storage';\nimport SpeedIcon from '@mui/icons-material/Speed';")

# 2. Add new states
if "const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);" not in content:
    content = content.replace("const [settingsOpen, setSettingsOpen] = useState(false);",
        "const [settingsOpen, setSettingsOpen] = useState(false);\n  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);\n  const [settingsMenuOpen, setSettingsMenuOpen] = useState(false);")

# 3. Modify Navbar
old_toolbar = """          <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 600, color: theme.palette.primary.main, flexGrow: 1 }}>
            Webhook Forwarder
          </Typography>
          {user && user.id === 1 && (
            <IconButton color="primary" onClick={() => setSettingsOpen(true)}>
              <SettingsIcon />
            </IconButton>
          )}"""

new_toolbar = """          <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 600, color: theme.palette.primary.main, flexGrow: 1 }}>
            Webhook Forwarder
          </Typography>
          {user && (
            <>
              <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} sx={{ p: 0, ml: 2 }}>
                <Avatar sx={{ bgcolor: theme.palette.primary.main }}>{user.full_name ? user.full_name[0].toUpperCase() : user.email[0].toUpperCase()}</Avatar>
              </IconButton>
              <Menu
                sx={{ mt: '45px' }}
                id="menu-appbar"
                anchorEl={anchorEl}
                anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
                keepMounted
                transformOrigin={{ vertical: 'top', horizontal: 'right' }}
                open={Boolean(anchorEl)}
                onClose={() => setAnchorEl(null)}
              >
                <MenuItem onClick={() => { setAnchorEl(null); navigate('/profile'); }}>
                  <Typography textAlign="center">Profile</Typography>
                </MenuItem>
                <MenuItem onClick={() => { setAnchorEl(null); handleLogout(); }}>
                  <Typography textAlign="center" color="error">Logout</Typography>
                </MenuItem>
              </Menu>
            </>
          )}"""

content = content.replace(old_toolbar, new_toolbar)

# 4. Modify Sidebar items
# Remove Profile and Logout from main menuItems array
if "{ text: 'Profile', icon: <AccountCircleIcon />, path: '/profile' }," in content:
    content = content.replace("{ text: 'Profile', icon: <AccountCircleIcon />, path: '/profile' },", "")
    
# Change the bottom list where Logout was
old_logout_list = """        <List sx={{ mt: 'auto', mb: 2 }}>
          {/* Profile & Logout */}
          <Divider sx={{ mb: 2 }} />
          <ListItem disablePadding sx={{ display: 'block' }}>
            <ListItemButton
              onClick={() => navigate('/profile')}
              selected={location.pathname === '/profile'}
              sx={{ minHeight: 48, justifyContent: open ? 'initial' : 'center', px: 2.5 }}
            >
              <ListItemIcon sx={{ minWidth: 0, mr: open ? 3 : 'auto', justifyContent: 'center' }}>
                <AccountCircleIcon />
              </ListItemIcon>
              <ListItemText primary="Profile" sx={{ opacity: open ? 1 : 0 }} />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding sx={{ display: 'block' }}>
            <ListItemButton
              onClick={handleLogout}
              sx={{ minHeight: 48, justifyContent: open ? 'initial' : 'center', px: 2.5 }}
            >
              <ListItemIcon sx={{ minWidth: 0, mr: open ? 3 : 'auto', justifyContent: 'center' }}>
                <LogoutIcon />
              </ListItemIcon>
              <ListItemText primary="Logout" sx={{ opacity: open ? 1 : 0, color: '#d32f2f' }} />
            </ListItemButton>
          </ListItem>
        </List>"""

new_sidebar_bottom = """        <List sx={{ mt: 'auto', mb: 2 }}>
          {user && user.id === 1 && (
            <>
              <Divider sx={{ mb: 1 }} />
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
                  <ListItemButton sx={{ pl: 4 }} onClick={() => setSettingsOpen(true)}>
                    <ListItemIcon sx={{ minWidth: 0, mr: 2 }}>
                      <StorageIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Database" primaryTypographyProps={{ fontSize: '0.9rem' }} />
                  </ListItemButton>
                  <ListItemButton sx={{ pl: 4 }} selected={location.pathname === '/settings/limits'} onClick={() => navigate('/settings/limits')}>
                    <ListItemIcon sx={{ minWidth: 0, mr: 2 }}>
                      <SpeedIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="System Limits" primaryTypographyProps={{ fontSize: '0.9rem' }} />
                  </ListItemButton>
                </List>
              </Collapse>
            </>
          )}
        </List>"""

if "onClick={handleLogout}" in content:
    content = content.replace(old_logout_list, new_sidebar_bottom)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated Layout.tsx successfully")
