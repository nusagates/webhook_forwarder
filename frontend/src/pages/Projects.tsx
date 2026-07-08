import React, { useEffect, useState } from 'react';
import { fetchApi } from '../api';
import toast from 'react-hot-toast';
import { Typography, Box, TextField, Button, Card, CardContent, CardActions, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';

interface Project { id: string; name: string; description?: string; }

export default function Projects() {
    const [projects, setProjects] = useState<Project[]>([]);
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    
    // Form State
    const [editId, setEditId] = useState<string | null>(null);
    const [projName, setProjName] = useState('');
    const [projDesc, setProjDesc] = useState('');

    useEffect(() => { loadProjects(); }, []);

    const loadProjects = async () => {
        try {
            const data = await fetchApi('/api/projects');
            setProjects(data);
        } catch (err) { console.error(err); }
    };

    const handleOpenDialog = (project?: Project) => {
        if (project) {
            setEditId(project.id);
            setProjName(project.name);
            setProjDesc(project.description || '');
        } else {
            setEditId(null);
            setProjName('');
            setProjDesc('');
        }
        setIsDialogOpen(true);
    };

    const handleCloseDialog = () => {
        setIsDialogOpen(false);
    };

    const handleSaveProject = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        try {
            if (editId) {
                // Edit mode
                await fetchApi(`/api/projects/${editId}`, {
                    method: 'PUT',
                    body: JSON.stringify({ name: projName, description: projDesc })
                });
                toast.success('Project updated!');
            } else {
                // Create mode
                await fetchApi('/api/projects', {
                    method: 'POST',
                    body: JSON.stringify({ name: projName, description: projDesc })
                });
                toast.success('Project created!');
            }
            handleCloseDialog();
            loadProjects();
        } catch (err: any) { 
            toast.error(err.message || 'Failed to save project'); 
        } finally { 
            setIsSaving(false); 
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm('Are you sure you want to delete this project? All endpoints and destinations will be lost!')) return;
        try {
            await fetchApi(`/api/projects/${id}`, { method: 'DELETE' });
            loadProjects();
            toast.success('Project deleted');
        } catch (err: any) { toast.error(err.message); }
    };

    return (
        <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
                <Box>
                    <Typography variant="h4" sx={{ fontWeight: 600 }} gutterBottom>Projects</Typography>
                    <Typography variant="body1" color="text.secondary">
                        Manage your webhook projects
                    </Typography>
                </Box>
                <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenDialog()}>
                    New Project
                </Button>
            </Box>

            {projects.length === 0 ? (
                <Typography color="text.secondary">No projects found. Create one to get started!</Typography>
            ) : (
                <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' }, gap: 3 }}>
                    {projects.map(p => (
                        <Card elevation={1} key={p.id}>
                            <CardContent>
                                <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>{p.name}</Typography>
                                <Typography variant="body2" color="text.secondary" sx={{ mt: 1, minHeight: '40px' }}>
                                    {p.description || 'No description provided.'}
                                </Typography>
                            </CardContent>
                            <CardActions sx={{ justifyContent: 'flex-end', gap: 1, px: 2, pb: 2 }}>
                                <Button size="small" variant="outlined" startIcon={<EditIcon />} onClick={() => handleOpenDialog(p)}>
                                    Edit
                                </Button>
                                <Button size="small" color="error" variant="outlined" startIcon={<DeleteIcon />} onClick={() => handleDelete(p.id)}>
                                    Delete
                                </Button>
                            </CardActions>
                        </Card>
                    ))}
                </Box>
            )}

            <Dialog open={isDialogOpen} onClose={handleCloseDialog} fullWidth maxWidth="sm">
                <form onSubmit={handleSaveProject}>
                    <DialogTitle>{editId ? 'Edit Project' : 'Create New Project'}</DialogTitle>
                    <DialogContent>
                        <TextField
                            margin="dense"
                            label="Project Name"
                            fullWidth
                            variant="outlined"
                            value={projName}
                            onChange={e => setProjName(e.target.value)}
                            required
                            autoFocus
                            sx={{ mb: 2, mt: 1 }}
                        />
                        <TextField
                            margin="dense"
                            label="Description"
                            fullWidth
                            variant="outlined"
                            multiline
                            rows={3}
                            value={projDesc}
                            onChange={e => setProjDesc(e.target.value)}
                            placeholder="e.g. Production webhooks for MyApp"
                        />
                    </DialogContent>
                    <DialogActions sx={{ p: 2 }}>
                        <Button onClick={handleCloseDialog} color="inherit">Cancel</Button>
                        <Button type="submit" variant="contained" disabled={isSaving}>
                            {isSaving ? 'Saving...' : 'Save'}
                        </Button>
                    </DialogActions>
                </form>
            </Dialog>
        </Box>
    );
}
