import { useState } from 'react';
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
import DatabaseSettingsDialog from './DatabaseSettingsDialog';
import { fetchApi } from '../api';
import { useEffect } from 'react';


const drawerWidth = 240;

const openedMixin = (theme: Theme) => ({
  width: drawerWidth,
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen,
  }),
  overflowX: 'hidden',
});

const closedMixin = (theme: Theme) => ({
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  overflowX: 'hidden',
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
  // necessary for content to be below app bar
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
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [settingsMenuOpen, setSettingsMenuOpen] = useState(false);

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

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" open={open} elevation={0} sx={{ borderBottom: '1px solid #e0e0e0', backgroundColor: '#fff', color: '#333' }}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={handleDrawerOpen}
            edge="start"
            sx={{
              marginRight: 5,
              ...(open && { display: 'none' }),
            }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 600, color: theme.palette.primary.main, flexGrow: 1 }}>
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
        <List>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding sx={{ display: 'block' }}>
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
            </ListItem>
          ))}
        </List>
        <Box sx={{ flexGrow: 1 }} />
        <Divider />
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
                    <ListItemText primary="Database" sx={{ opacity: open ? 1 : 0 }} />
                  </ListItemButton>
                  <ListItemButton sx={{ pl: open ? 4 : 2, justifyContent: open ? 'initial' : 'center' }} selected={location.pathname === '/settings/limits'} onClick={() => navigate('/settings/limits')}>
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
                  </ListItemButton>
                </List>
              </Collapse>
            </>
          )}
        </List>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3, backgroundColor: theme.palette.background.default, minHeight: '100vh' }}>
        <DrawerHeader />
        <Outlet />

      </Box>
      <DatabaseSettingsDialog open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </Box>
  );
}

