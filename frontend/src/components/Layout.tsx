import { useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { styled, useTheme } from '@mui/material/styles';
import type { Theme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import MuiDrawer from '@mui/material/Drawer';
import MuiAppBar from '@mui/material/AppBar';
import type { AppBarProps as MuiAppBarProps } from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import DashboardIcon from '@mui/icons-material/Dashboard';
import ListAltIcon from '@mui/icons-material/ListAlt';
import TimelineIcon from '@mui/icons-material/Timeline';
import Tooltip from '@mui/material/Tooltip';
import SettingsIcon from '@mui/icons-material/Settings';
import Avatar from '@mui/material/Avatar';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Collapse from '@mui/material/Collapse';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import StorageIcon from '@mui/icons-material/Storage';
import SpeedIcon from '@mui/icons-material/Speed';
import GroupIcon from '@mui/icons-material/Group';
import FolderIcon from '@mui/icons-material/Folder';
import { useProject } from '../contexts/ProjectContext';
import { fetchApi } from '../api';

const drawerWidth = 240;

const openedMixin = (theme: Theme) => ({
  width: drawerWidth,
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen,
  }),
  overflowX: 'hidden' as const,
});

const closedMixin = (theme: Theme) => ({
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  overflowX: 'hidden' as const,
  width: `calc(${theme.spacing(7)} + 1px)`,
  [theme.breakpoints.up('sm')]: {
    width: `calc(${theme.spacing(8)} + 1px)`,
  },
});

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'flex-end',
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
}));

interface AppBarProps extends MuiAppBarProps {
  open?: boolean;
}

const AppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => prop !== 'open',
})<AppBarProps>(({ theme, open }) => ({
  zIndex: theme.zIndex.drawer + 1,
  transition: theme.transitions.create(['width', 'margin'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    marginLeft: drawerWidth,
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const Drawer = styled(MuiDrawer, { shouldForwardProp: (prop) => prop !== 'open' })(
  ({ theme, open }: any) => ({
    width: drawerWidth,
    flexShrink: 0,
    whiteSpace: 'nowrap',
    boxSizing: 'border-box',
    ...(open && {
      ...openedMixin(theme),
      '& .MuiDrawer-paper': openedMixin(theme),
    }),
    ...(!open && {
      ...closedMixin(theme),
      '& .MuiDrawer-paper': closedMixin(theme),
    }),
  }),
);

export default function Layout() {
  const theme = useTheme();
  const [open, setOpen] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [settingsMenuOpen, setSettingsMenuOpen] = useState(false);
  const [projectAnchorEl, setProjectAnchorEl] = useState<null | HTMLElement>(null);
  // Separate anchor for icon-mode settings popover
  const [settingsAnchorEl, setSettingsAnchorEl] = useState<null | HTMLElement>(null);
  const { projects, selectedProjectId, setSelectedProjectId } = useProject();

  useEffect(() => {
    fetchApi('/api/auth/me').then(data => setUser(data)).catch(() => {});
  }, []);

  const navigate = useNavigate();
  const location = useLocation();

  const handleDrawerOpen = () => setOpen(true);
  const handleDrawerClose = () => setOpen(false);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const menuItems = [
    { text: 'Projects', icon: <DashboardIcon />, path: '/projects' },
    { text: 'Endpoints', icon: <ListAltIcon />, path: '/endpoints' },
    { text: 'Live Logs', icon: <TimelineIcon />, path: '/logs' },
  ];

  const selectedProject = projects.find(p => p.id === selectedProjectId);

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" open={open} elevation={0} sx={{ borderBottom: '1px solid #e0e0e0', backgroundColor: '#fff', color: '#333' }}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={handleDrawerOpen}
            edge="start"
            sx={{ marginRight: 5, ...(open && { display: 'none' }) }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 600, color: theme.palette.primary.main, flexGrow: 1 }}>
            Webhook Forwarder
          </Typography>
          {user && (
            <>
              <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} sx={{ p: 0, ml: 2 }}>
                <Avatar sx={{ bgcolor: theme.palette.primary.main }}>
                  {user.full_name ? user.full_name[0].toUpperCase() : user.email[0].toUpperCase()}
                </Avatar>
              </IconButton>
              <Menu
                sx={{ mt: '45px' }}
                anchorEl={anchorEl}
                anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
                keepMounted
                transformOrigin={{ vertical: 'top', horizontal: 'right' }}
                open={Boolean(anchorEl)}
                onClose={() => setAnchorEl(null)}
              >
                <MenuItem onClick={() => { setAnchorEl(null); navigate('/profile'); }}>
                  <Typography align="center">Profile</Typography>
                </MenuItem>
                <MenuItem onClick={() => { setAnchorEl(null); handleLogout(); }}>
                  <Typography align="center" color="error">Logout</Typography>
                </MenuItem>
              </Menu>
            </>
          )}
        </Toolbar>
      </AppBar>

      <Drawer variant="permanent" open={open}>
        <DrawerHeader>
          <IconButton onClick={handleDrawerClose}>
            <ChevronLeftIcon />
          </IconButton>
        </DrawerHeader>
        <Divider />

        {/* Main nav items */}
        <List>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding sx={{ display: 'block' }}>
              <Tooltip title={!open ? item.text : ''} placement="right" arrow>
                <ListItemButton
                  sx={{
                    minHeight: 48,
                    justifyContent: open ? 'initial' : 'center',
                    px: 2.5,
                    ...(location.pathname.startsWith(item.path) && {
                      backgroundColor: 'rgba(26, 115, 232, 0.08)',
                      borderRight: `3px solid ${theme.palette.primary.main}`,
                    })
                  }}
                  onClick={() => navigate(item.path)}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: 0,
                      mr: open ? 3 : 'auto',
                      justifyContent: 'center',
                      color: location.pathname.startsWith(item.path) ? theme.palette.primary.main : 'inherit',
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText primary={item.text} sx={{ opacity: open ? 1 : 0 }} />
                </ListItemButton>
              </Tooltip>
            </ListItem>
          ))}
        </List>

        <Box sx={{ flexGrow: 1 }} />
        <Divider />

        {/* Bottom: Project switcher + Settings */}
        <List sx={{ mt: 'auto', mb: 2 }}>

          {/* Project Switcher */}
          {projects.length > 0 && (
            <ListItem sx={{ display: 'block', px: open ? 2 : 0.5, mb: 1 }}>
              <Tooltip
                title={!open ? `Active: ${selectedProject?.name || 'No project selected'}` : ''}
                placement="right"
                arrow
              >
                <ListItemButton
                  onClick={(e) => setProjectAnchorEl(e.currentTarget)}
                  sx={{
                    borderRadius: 1,
                    border: open ? '1px solid #e0e0e0' : 'none',
                    justifyContent: open ? 'space-between' : 'center',
                    px: open ? 2 : 1,
                    py: 1,
                  }}
                >
                  {open ? (
                    <>
                      <Box sx={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 'bold' }}>Active Project</Typography>
                        <Typography variant="body2" noWrap sx={{ fontWeight: 500 }}>
                          {selectedProject?.name || 'Select Project'}
                        </Typography>
                      </Box>
                      <ExpandMore color="action" />
                    </>
                  ) : (
                    <StorageIcon color={selectedProject ? 'primary' : 'action'} />
                  )}
                </ListItemButton>
              </Tooltip>

              {/* Project dropdown menu — works in both icon and expanded mode */}
              <Menu
                anchorEl={projectAnchorEl}
                open={Boolean(projectAnchorEl)}
                onClose={() => setProjectAnchorEl(null)}
                sx={{ '& .MuiPaper-root': { width: 220, maxHeight: 300 } }}
                anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
                transformOrigin={{ vertical: 'bottom', horizontal: 'left' }}
              >
                {projects.map((p) => (
                  <MenuItem
                    key={p.id}
                    selected={p.id === selectedProjectId}
                    onClick={() => { setSelectedProjectId(p.id); setProjectAnchorEl(null); }}
                  >
                    <Typography noWrap>{p.name}</Typography>
                  </MenuItem>
                ))}
              </Menu>
            </ListItem>
          )}

          <Divider sx={{ mb: 1 }} />

          {/* Settings — Admin only */}
          {user && user.id === 1 && (
            <>
              <ListItem disablePadding sx={{ display: 'block' }}>
                <Tooltip title={!open ? 'Settings' : ''} placement="right" arrow>
                  <ListItemButton
                    onClick={(e) => {
                      if (open) {
                        setSettingsMenuOpen(!settingsMenuOpen);
                      } else {
                        setSettingsAnchorEl(e.currentTarget);
                      }
                    }}
                    sx={{ minHeight: 48, justifyContent: open ? 'initial' : 'center', px: 2.5 }}
                  >
                    <ListItemIcon sx={{ minWidth: 0, mr: open ? 3 : 'auto', justifyContent: 'center' }}>
                      <SettingsIcon />
                    </ListItemIcon>
                    <ListItemText primary="Settings" sx={{ opacity: open ? 1 : 0 }} />
                    {open ? (settingsMenuOpen ? <ExpandLess /> : <ExpandMore />) : null}
                  </ListItemButton>
                </Tooltip>
              </ListItem>

              {/* Expanded sidebar: collapsible sub-menu */}
              <Collapse in={settingsMenuOpen && open} timeout="auto" unmountOnExit>
                <List component="div" disablePadding>
                  <ListItemButton sx={{ pl: 4 }} selected={location.pathname === '/settings/database'} onClick={() => navigate('/settings/database')}>
                    <ListItemIcon sx={{ minWidth: 0, mr: 2 }}><StorageIcon fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Database" />
                  </ListItemButton>
                  <ListItemButton sx={{ pl: 4 }} selected={location.pathname === '/settings/limits'} onClick={() => navigate('/settings/limits')}>
                    <ListItemIcon sx={{ minWidth: 0, mr: 2 }}><SpeedIcon fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Limits" />
                  </ListItemButton>
                  <ListItemButton sx={{ pl: 4 }} selected={location.pathname === '/settings/users'} onClick={() => navigate('/settings/users')}>
                    <ListItemIcon sx={{ minWidth: 0, mr: 2 }}><GroupIcon fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Users" />
                  </ListItemButton>
                  <ListItemButton sx={{ pl: 4 }} selected={location.pathname === '/settings/projects'} onClick={() => navigate('/settings/projects')}>
                    <ListItemIcon sx={{ minWidth: 0, mr: 2 }}><FolderIcon fontSize="small" /></ListItemIcon>
                    <ListItemText primary="All Projects" />
                  </ListItemButton>
                </List>
              </Collapse>

              {/* Icon-only sidebar: floating popover menu */}
              <Menu
                anchorEl={settingsAnchorEl}
                open={Boolean(settingsAnchorEl)}
                onClose={() => setSettingsAnchorEl(null)}
                anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
                transformOrigin={{ vertical: 'bottom', horizontal: 'left' }}
              >
                <MenuItem onClick={() => { setSettingsAnchorEl(null); navigate('/settings/database'); }}>
                  <ListItemIcon><StorageIcon fontSize="small" /></ListItemIcon>
                  Database
                </MenuItem>
                <MenuItem onClick={() => { setSettingsAnchorEl(null); navigate('/settings/limits'); }}>
                  <ListItemIcon><SpeedIcon fontSize="small" /></ListItemIcon>
                  Limits
                </MenuItem>
                <MenuItem onClick={() => { setSettingsAnchorEl(null); navigate('/settings/users'); }}>
                  <ListItemIcon><GroupIcon fontSize="small" /></ListItemIcon>
                  Users
                </MenuItem>
                <MenuItem onClick={() => { setSettingsAnchorEl(null); navigate('/settings/projects'); }}>
                  <ListItemIcon><FolderIcon fontSize="small" /></ListItemIcon>
                  All Projects
                </MenuItem>
              </Menu>
            </>
          )}
        </List>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3, backgroundColor: theme.palette.background.default, minHeight: '100vh' }}>
        <DrawerHeader />
        <Outlet />
      </Box>
    </Box>
  );
}
