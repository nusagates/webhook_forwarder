import { useConfirm } from '../components/ConfirmDialog';
import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, IconButton, Chip, Dialog, DialogTitle, DialogContent, DialogActions, TextField, CircularProgress } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import BlockIcon from '@mui/icons-material/Block';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import { fetchApi } from '../api';
import toast from 'react-hot-toast';

export default function UserManagement() {
    const confirm = useConfirm();

    const [users, setUsers] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    
    // Edit Dialog state
    const [editOpen, setEditOpen] = useState(false);
    const [blockOpen, setBlockOpen] = useState(false);
    const [blockReason, setBlockReason] = useState('');
    const [userToBlock, setUserToBlock] = useState<any>(null);
    const [selectedUser, setSelectedUser] = useState<any>(null);
    const [limits, setLimits] = useState({
        limit_projects: '',
        limit_endpoints: '',
        limit_logs: '',
        limit_destinations: ''
    });
    const [resetPasswordOpen, setResetPasswordOpen] = useState(false);
    const [resetPasswordVal, setResetPasswordVal] = useState('');

    useEffect(() => {
        document.title = "User Management - Admin";
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        try {
            const data = await fetchApi('/api/admin/users');
            setUsers(data);
        } catch (e: any) {
            toast.error(e.message || "Failed to fetch users");
        } finally {
            setLoading(false);
        }
    };

    const toggleAdmin = async (user: any) => {
        if (!await confirm({ message: `Are you sure you want to ${user.is_admin ? 'revoke' : 'grant'} Admin rights for ${user.email}?`, isDanger: true })) return;
        try {
            await fetchApi(`/api/admin/users/${user.id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    is_admin: !user.is_admin,
                    is_blocked: user.is_blocked,
                    limit_projects: user.limit_projects,
                    limit_endpoints: user.limit_endpoints,
                    limit_logs: user.limit_logs,
                    limit_destinations: user.limit_destinations
                })
            });
            toast.success('Admin status updated');
            fetchUsers();
        } catch (e: any) {
            toast.error(e.message || "Failed to update admin status");
        }
    };

    const toggleBlock = async (user: any) => {
        if (!user.is_blocked) {
            setUserToBlock(user);
            setBlockReason('');
            setBlockOpen(true);
            return;
        }
        
        if (!await confirm({ message: `Are you sure you want to unblock ${user.email}?`, isDanger: true })) return;
        executeBlockToggle(user, false, "");
    };

    const executeBlockToggle = async (user: any, block: boolean, reason: string) => {
        try {
            await fetchApi(`/api/admin/users/${user.id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    is_admin: user.is_admin,
                    is_blocked: block,
                    block_reason: block ? reason : null,
                    limit_projects: user.limit_projects,
                    limit_endpoints: user.limit_endpoints,
                    limit_logs: user.limit_logs,
                    limit_destinations: user.limit_destinations
                })
            });
            toast.success(block ? 'User blocked' : 'User unblocked');
            fetchUsers();
        } catch (e: any) {
            toast.error(e.message || "Failed to update block status");
        }
    };
    
    const submitBlock = () => {
        if (!userToBlock) return;
        executeBlockToggle(userToBlock, true, blockReason);
        setBlockOpen(false);
    };

    const openEditDialog = (user: any) => {
        setSelectedUser(user);
        setLimits({
            limit_projects: user.limit_projects != null ? user.limit_projects.toString() : '',
            limit_endpoints: user.limit_endpoints != null ? user.limit_endpoints.toString() : '',
            limit_logs: user.limit_logs != null ? user.limit_logs.toString() : '',
            limit_destinations: user.limit_destinations != null ? user.limit_destinations.toString() : ''
        });
        setEditOpen(true);
    };

    const openResetPasswordDialog = (user: any) => {
        setSelectedUser(user);
        setResetPasswordVal('');
        setResetPasswordOpen(true);
    };

    const handleResetPassword = async () => {
        if (!selectedUser || !resetPasswordVal) return;
        const tid = toast.loading('Resetting password...');
        try {
            await fetchApi(`/api/admin/users/${selectedUser.id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    is_admin: selectedUser.is_admin,
                    is_blocked: selectedUser.is_blocked,
                    limit_projects: selectedUser.limit_projects,
                    limit_endpoints: selectedUser.limit_endpoints,
                    limit_logs: selectedUser.limit_logs,
                    limit_destinations: selectedUser.limit_destinations,
                    password: resetPasswordVal
                })
            });
            toast.success('Password reset successfully', { id: tid });
            setResetPasswordOpen(false);
        } catch (e: any) {
            toast.error(e.message || "Failed to reset password", { id: tid });
        }
    };

    const handleSaveLimits = async () => {
        if (!selectedUser) return;
        const tid = toast.loading('Saving limits...');
        try {
            await fetchApi(`/api/admin/users/${selectedUser.id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    is_admin: selectedUser.is_admin,
                    is_blocked: selectedUser.is_blocked,
                    limit_projects: limits.limit_projects ? parseInt(limits.limit_projects) : null,
                    limit_endpoints: limits.limit_endpoints ? parseInt(limits.limit_endpoints) : null,
                    limit_logs: limits.limit_logs ? parseInt(limits.limit_logs) : null,
                    limit_destinations: limits.limit_destinations ? parseInt(limits.limit_destinations) : null
                })
            });
            toast.success('Limits updated successfully', { id: tid });
            setEditOpen(false);
            fetchUsers();
        } catch (e: any) {
            toast.error(e.message || "Failed to update limits", { id: tid });
        }
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}>
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box>
            <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
                User Management
            </Typography>

            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>ID</TableCell>
                            <TableCell>Email</TableCell>
                            <TableCell>Name</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Limits Override</TableCell>
                            <TableCell align="right">Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {users.map(user => (
                            <TableRow key={user.id}>
                                <TableCell>{user.id}</TableCell>
                                <TableCell>{user.email}</TableCell>
                                <TableCell>{user.full_name || '-'}</TableCell>
                                <TableCell>
                                    <Box sx={{ display: 'flex', gap: 1 }}>
                                        {user.is_admin && <Chip label="Admin" color="primary" size="small" />}
                                        {user.is_blocked ? (
                                            <Chip label="Blocked" color="error" size="small" />
                                        ) : (
                                            <Chip label="Active" color="success" size="small" />
                                        )}
                                    </Box>
                                </TableCell>
                                <TableCell>
                                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                        {user.limit_projects !== null && <Chip label={`Proj: ${user.limit_projects}`} size="small" variant="outlined" />}
                                        {user.limit_endpoints !== null && <Chip label={`Endp: ${user.limit_endpoints}`} size="small" variant="outlined" />}
                                        {user.limit_logs !== null && <Chip label={`Logs: ${user.limit_logs}`} size="small" variant="outlined" />}
                                        {user.limit_projects === null && user.limit_endpoints === null && user.limit_logs === null && (
                                            <Typography variant="body2" color="text.secondary">Global Default</Typography>
                                        )}
                                    </Box>
                                </TableCell>
                                <TableCell align="right">
                                    <IconButton onClick={() => toggleAdmin(user)} color={user.is_admin ? "primary" : "default"} title="Toggle Admin" disabled={user.id === 1}>
                                        <AdminPanelSettingsIcon />
                                    </IconButton>
                                    <IconButton onClick={() => toggleBlock(user)} color={user.is_blocked ? "error" : "default"} title="Toggle Block" disabled={user.id === 1 || user.is_admin}>
                                        {user.is_blocked ? <CheckCircleIcon /> : <BlockIcon />}
                                    </IconButton>
                                    <IconButton onClick={() => openEditDialog(user)} color="info" title="Edit Limits" disabled={user.id === 1}>
                                        <EditIcon />
                                    </IconButton>
                                    <IconButton onClick={() => openResetPasswordDialog(user)} color="warning" title="Reset Password" disabled={user.id === 1}>
                                        <VpnKeyIcon />
                                    </IconButton>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>

            {/* Edit Limits Dialog */}
            <Dialog open={editOpen} onClose={() => setEditOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Edit User Limits - {selectedUser?.email}</DialogTitle>
                <DialogContent dividers>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        Leave blank to use the global system limits. Enter a number to set a custom limit for this user.
                    </Typography>
                    
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                        <TextField
                            label="Max Projects"
                            type="number"
                            fullWidth
                            value={limits.limit_projects}
                            onChange={e => setLimits({ ...limits, limit_projects: e.target.value })}
                            helperText="Leave blank = use global limit. Set -1 for unlimited."
                        />
                        <TextField
                            label="Max Endpoints per Project"
                            type="number"
                            fullWidth
                            value={limits.limit_endpoints}
                            onChange={e => setLimits({ ...limits, limit_endpoints: e.target.value })}
                            helperText="Leave blank = use global limit. Set -1 for unlimited."
                        />
                        <TextField
                            label="Max Logs Retention"
                            type="number"
                            fullWidth
                            value={limits.limit_logs}
                            onChange={e => setLimits({ ...limits, limit_logs: e.target.value })}
                            helperText="Leave blank = use global limit. Set -1 for unlimited."
                        />
                        <TextField
                            label="Max Destinations per Endpoint"
                            type="number"
                            fullWidth
                            value={limits.limit_destinations}
                            onChange={e => setLimits({ ...limits, limit_destinations: e.target.value })}
                            helperText="Leave blank = use global limit. Set -1 for unlimited."
                        />
                    </Box>
                </DialogContent>
                <DialogActions sx={{ p: 2 }}>
                    <Button onClick={() => setEditOpen(false)}>Cancel</Button>
                    <Button onClick={handleSaveLimits} variant="contained" color="primary">Save Limits</Button>
                </DialogActions>
            </Dialog>

            {/* Reset Password Dialog */}
            <Dialog open={resetPasswordOpen} onClose={() => setResetPasswordOpen(false)} maxWidth="xs" fullWidth>
                <DialogTitle>Reset Password - {selectedUser?.email}</DialogTitle>
                <DialogContent dividers>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                            Enter a new password for this user. This will immediately override their old password.
                        </Typography>
                        <TextField
                            label="New Password"
                            type="text"
                            fullWidth
                            autoFocus
                            value={resetPasswordVal}
                            onChange={e => setResetPasswordVal(e.target.value)}
                        />
                    </Box>
                </DialogContent>
                <DialogActions sx={{ p: 2 }}>
                    <Button onClick={() => setResetPasswordOpen(false)}>Cancel</Button>
                    <Button onClick={handleResetPassword} variant="contained" color="warning" disabled={!resetPasswordVal}>
                        Reset Password
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Block Dialog */}
            <Dialog open={blockOpen} onClose={() => setBlockOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Block User</DialogTitle>
                <DialogContent>
                    <Typography sx={{ mb: 2 }}>
                        Please provide a reason for blocking <strong>{userToBlock?.email}</strong>. This reason will be shown to the user when they try to access the application.
                    </Typography>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Reason for suspension"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={blockReason}
                        onChange={(e) => setBlockReason(e.target.value)}
                        placeholder="e.g. Violation of terms of service"
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setBlockOpen(false)}>Cancel</Button>
                    <Button onClick={submitBlock} color="error" variant="contained">Block User</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}
