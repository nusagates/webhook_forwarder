import React, { useEffect, useState } from 'react';
import { fetchApi } from '../api';
import toast from 'react-hot-toast';
import { 
    Dialog, DialogTitle, DialogContent, DialogActions, Button, 
    TextField, Box, Typography, Select, MenuItem, IconButton, 
    Divider, FormControl
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';

export interface ProjectShareDialogProps {
    open: boolean;
    onClose: () => void;
    projectId: string;
    projectRole: string; // 'owner' | 'editor' | 'viewer'
}

interface Member {
    id: number;
    project_id: string;
    user_id: number;
    role: string;
    user: {
        id: number;
        email: string;
        full_name?: string;
    };
}

export default function ProjectShareDialog({ open, onClose, projectId, projectRole }: ProjectShareDialogProps) {
    const [members, setMembers] = useState<Member[]>([]);
    const [email, setEmail] = useState('');
    const [role, setRole] = useState('viewer');
    const [isAdding, setIsAdding] = useState(false);
    
    // Transfer ownership state
    const [isTransferring, setIsTransferring] = useState(false);
    const [transferEmail, setTransferEmail] = useState('');

    useEffect(() => {
        if (open && projectId) {
            loadMembers();
        }
    }, [open, projectId]);

    const loadMembers = async () => {
        try {
            const data = await fetchApi(`/api/projects/${projectId}/members`);
            setMembers(data);
        } catch (err: any) {
            toast.error(err.message || 'Failed to load members');
        }
    };

    const handleAddMember = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsAdding(true);
        try {
            await fetchApi(`/api/projects/${projectId}/members`, {
                method: 'POST',
                body: JSON.stringify({ email, role })
            });
            toast.success('Member added successfully');
            setEmail('');
            loadMembers();
        } catch (err: any) {
            toast.error(err.message || 'Failed to add member');
        } finally {
            setIsAdding(false);
        }
    };

    const handleRemoveMember = async (memberId: number) => {
        if (!confirm('Are you sure you want to remove this member?')) return;
        try {
            await fetchApi(`/api/projects/${projectId}/members/${memberId}`, { method: 'DELETE' });
            toast.success('Member removed');
            loadMembers();
        } catch (err: any) {
            toast.error(err.message || 'Failed to remove member');
        }
    };

    const handleUpdateRole = async (memberId: number, newRole: string) => {
        try {
            await fetchApi(`/api/projects/${projectId}/members/${memberId}`, {
                method: 'PUT',
                body: JSON.stringify({ role: newRole })
            });
            toast.success('Role updated');
            loadMembers();
        } catch (err: any) {
            toast.error(err.message || 'Failed to update role');
        }
    };

    const handleTransferOwnership = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!confirm('DANGER: Are you sure you want to transfer ownership? You will lose Owner privileges.')) return;
        
        setIsTransferring(true);
        try {
            await fetchApi(`/api/projects/${projectId}/transfer`, {
                method: 'POST',
                body: JSON.stringify({ email: transferEmail, role: 'owner' }) // role is ignored in backend but required by schema
            });
            toast.success('Ownership transferred successfully');
            setTransferEmail('');
            onClose(); // Close dialog since we are no longer owner
        } catch (err: any) {
            toast.error(err.message || 'Failed to transfer ownership');
        } finally {
            setIsTransferring(false);
        }
    };

    return (
        <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
            <DialogTitle sx={{ fontWeight: 600 }}>Project Sharing</DialogTitle>
            <DialogContent dividers>
                {projectRole !== 'owner' ? (
                    <Typography color="text.secondary">
                        You are a <strong>{projectRole}</strong> on this project. Only the Owner can manage members.
                    </Typography>
                ) : (
                    <Box>
                        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>Add Member</Typography>
                        <form onSubmit={handleAddMember} style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
                            <TextField 
                                size="small" 
                                placeholder="Email Address" 
                                value={email} 
                                onChange={e => setEmail(e.target.value)} 
                                required 
                                type="email"
                                sx={{ flexGrow: 1 }}
                            />
                            <FormControl size="small" sx={{ width: '120px' }}>
                                <Select value={role} onChange={e => setRole(e.target.value)}>
                                    <MenuItem value="viewer">Viewer</MenuItem>
                                    <MenuItem value="editor">Editor</MenuItem>
                                </Select>
                            </FormControl>
                            <Button type="submit" variant="contained" disabled={isAdding}>Add</Button>
                        </form>
                    </Box>
                )}

                <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>Current Members</Typography>
                {members.length === 0 ? (
                    <Typography variant="body2" color="text.secondary">No members added yet.</Typography>
                ) : (
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                        {members.map(m => (
                            <Box key={m.id} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', bgcolor: '#f5f5f5', p: 1, borderRadius: 1 }}>
                                <Box>
                                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{m.user.full_name || 'User'} ({m.user.email})</Typography>
                                </Box>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <Select 
                                        size="small" 
                                        value={m.role} 
                                        onChange={e => handleUpdateRole(m.id, e.target.value)}
                                        disabled={projectRole !== 'owner'}
                                        sx={{ width: '100px', '& .MuiSelect-select': { py: 0.5 } }}
                                    >
                                        <MenuItem value="viewer">Viewer</MenuItem>
                                        <MenuItem value="editor">Editor</MenuItem>
                                    </Select>
                                    {projectRole === 'owner' && (
                                        <IconButton size="small" color="error" onClick={() => handleRemoveMember(m.id)}>
                                            <DeleteIcon fontSize="small" />
                                        </IconButton>
                                    )}
                                </Box>
                            </Box>
                        ))}
                    </Box>
                )}

                {projectRole === 'owner' && (
                    <>
                        <Divider sx={{ my: 3 }} />
                        <Box sx={{ bgcolor: '#fff0f0', p: 2, borderRadius: 1, border: '1px solid #ffcccc' }}>
                            <Typography variant="subtitle2" color="error" sx={{ mb: 1, fontWeight: 'bold' }}>Transfer Ownership</Typography>
                            <Typography variant="body2" sx={{ mb: 2, color: '#666' }}>
                                Transfer this project to another user. You will become an editor and lose owner privileges.
                            </Typography>
                            <form onSubmit={handleTransferOwnership} style={{ display: 'flex', gap: '8px' }}>
                                <TextField 
                                    size="small" 
                                    placeholder="New Owner Email" 
                                    value={transferEmail} 
                                    onChange={e => setTransferEmail(e.target.value)} 
                                    required 
                                    type="email"
                                    sx={{ flexGrow: 1, bgcolor: 'white' }}
                                />
                                <Button type="submit" variant="outlined" color="error" disabled={isTransferring}>Transfer</Button>
                            </form>
                        </Box>
                    </>
                )}
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} variant="contained">Done</Button>
            </DialogActions>
        </Dialog>
    );
}
