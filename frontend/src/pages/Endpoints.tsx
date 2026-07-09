import React, { useEffect, useState } from 'react';
import { useConfirm } from '../components/ConfirmDialog';
import { fetchApi } from '../api';
import { useProject } from '../contexts/ProjectContext';
import toast from 'react-hot-toast';
import { Typography, Box, Paper, TextField, Button, Select, MenuItem, InputLabel, FormControl, Card, CardContent, Divider, List, ListItem, ListItemIcon, ListItemText, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import SendIcon from '@mui/icons-material/Send';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import EditIcon from '@mui/icons-material/Edit';

interface Destination { id: number; url: string; is_active: boolean; auth_type?: string; auth_config?: string; endpoint_id?: number; }
interface Endpoint { 
    id: number; name: string; slug: string; project_id: string; 
    auth_type: string; 
    auth_config?: string | null; 
    destinations: Destination[]; 
}

export default function Endpoints() {
    const confirm = useConfirm();

    const { projects, selectedProjectId } = useProject();
    const [endpoints, setEndpoints] = useState<Endpoint[]>([]);
    
    const [newEpName, setNewEpName] = useState('');
    const [newEpSlug, setNewEpSlug] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const [newDestUrl, setNewDestUrl] = useState('');
    const [activeEndpointId, setActiveEndpointId] = useState<number | null>(null);
    const [newDestAuthType, setNewDestAuthType] = useState('none');
    const [newDestAuthConfig, setNewDestAuthConfig] = useState<{ [key: string]: string }>({});

    const [newAuthType, setNewAuthType] = useState('none');
    const [newAuthConfig, setNewAuthConfig] = useState<{ [key: string]: string }>({});

    const [editEndpoint, setEditEndpoint] = useState<Endpoint | null>(null);
    const [editDestination, setEditDestination] = useState<Destination | null>(null);

    useEffect(() => {
        document.title = "Endpoints - Webhook Forwarder";
    }, []);
    
    useEffect(() => {
        if (selectedProjectId) loadEndpoints(selectedProjectId);
        else setEndpoints([]);
    }, [selectedProjectId]);

    const loadEndpoints = async (projId: string) => {
        try { setEndpoints(await fetchApi(`/api/endpoints?project_id=${projId}`)); }
        catch (err) { console.error(err); }
    };
    
    const selectedProject = projects.find(p => p.id === selectedProjectId);
    const isViewer = selectedProject?.my_role === 'viewer';

    const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = e.target.value;
        setNewEpName(val);
        setNewEpSlug(val.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)+/g, ''));
    };

    const handleSlugChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setNewEpSlug(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''));
    };

    const handleCreateEndpoint = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsCreating(true);
        try {
            await fetchApi('/api/endpoints', {
                method: 'POST',
                body: JSON.stringify({ 
                    name: newEpName, 
                    slug: newEpSlug, 
                    project_id: selectedProjectId,
                    auth_type: newAuthType,
                    auth_config: Object.keys(newAuthConfig).length > 0 ? JSON.stringify(newAuthConfig) : null
                })
            });
            setNewEpName(''); setNewEpSlug('');
            setNewAuthType('none'); setNewAuthConfig({});
            loadEndpoints(selectedProjectId);
            toast.success('Endpoint created!');
        } catch (err: any) { toast.error(err.message); }
        finally { setIsCreating(false); }
    };

    const handleUpdateEndpoint = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!editEndpoint) return;
        try {
            await fetchApi(`/api/endpoints/${editEndpoint.id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    name: editEndpoint.name,
                    slug: editEndpoint.slug,
                    project_id: editEndpoint.project_id,
                    auth_type: editEndpoint.auth_type,
                    auth_config: editEndpoint.auth_config
                })
            });
            toast.success('Endpoint updated!');
            setEditEndpoint(null);
            loadEndpoints(selectedProjectId);
        } catch (err: any) {
            toast.error(err.message || 'Failed to update endpoint');
        }
    };


    const handleUpdateDestination = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!editDestination || !editDestination.endpoint_id) return;
        try {
            await fetchApi(`/api/endpoints/${editDestination.endpoint_id}/destinations/${editDestination.id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    url: editDestination.url,
                    is_active: editDestination.is_active,
                    auth_type: editDestination.auth_type || 'none',
                    auth_config: editDestination.auth_config || null
                })
            });
            setEditDestination(null);
            loadEndpoints(selectedProjectId);
            toast.success('Destination updated!');
        } catch (err: any) {
            toast.error(err.message || 'Failed to update destination');
        }
    };

    const handleTestExistingDestination = async (dest: Destination) => {
        const tid = toast.loading('Testing connection...');
        try {
            const res = await fetchApi('/api/utils/test-destination', {
                method: 'POST',
                body: JSON.stringify({
                    url: dest.url,
                    auth_type: dest.auth_type || 'none',
                    auth_config: dest.auth_config || null
                })
            });
            toast.success(`Success! ${res.message}`, { id: tid });
        } catch (err: any) {
            toast.error(`Test failed: ${err.message}`, { id: tid });
        }
    };

    const handleDeleteEndpoint = async (id: number) => {
        if (!await confirm({ message: 'Delete this endpoint?', isDanger: true })) return;
        try {
            await fetchApi(`/api/endpoints/${id}`, { method: 'DELETE' });
            loadEndpoints(selectedProjectId);
            toast.success('Endpoint deleted');
        } catch (err: any) { toast.error(err.message); }
    };

    const handleDeleteDestination = async (epId: number, destId: number) => {
        if (!await confirm({ message: 'Remove this destination?', isDanger: true })) return;
        try {
            await fetchApi(`/api/endpoints/${epId}/destinations/${destId}`, { method: 'DELETE' });
            loadEndpoints(selectedProjectId);
            toast.success('Destination removed');
        } catch (err: any) { toast.error(err.message); }
    };

    const handleAddDestination = async (e: React.FormEvent | React.MouseEvent, epId: number) => {
        e.preventDefault();
        
        // Basic URL validation
        try {
            const parsedUrl = new URL(newDestUrl);
            if (parsedUrl.protocol !== 'http:' && parsedUrl.protocol !== 'https:') {
                throw new Error("Must be http or https");
            }
        } catch (err) {
            toast.error('Invalid URL format. Must start with http:// or https://');
            return;
        }
        
        try {
            await fetchApi(`/api/endpoints/${epId}/destinations`, {
                method: 'POST',
                body: JSON.stringify({ 
                    url: newDestUrl,
                    auth_type: newDestAuthType,
                    auth_config: Object.keys(newDestAuthConfig).length > 0 ? JSON.stringify(newDestAuthConfig) : null
                })
            });
            setNewDestUrl('');
            setNewDestAuthType('none');
            setNewDestAuthConfig({});
            setActiveEndpointId(null);
            loadEndpoints(selectedProjectId);
            toast.success('Destination added!');
        } catch (err: any) { toast.error(err.message); }
    };

    const handleTestDestination = async () => {
        try {
            const parsedUrl = new URL(newDestUrl);
            if (parsedUrl.protocol !== 'http:' && parsedUrl.protocol !== 'https:') {
                throw new Error("Must be http or https");
            }
        } catch (err) {
            toast.error('Invalid URL format. Must start with http:// or https://');
            return;
        }

        const tid = toast.loading('Testing connection...');
        try {
            const res = await fetchApi('/api/utils/test-destination', {
                method: 'POST',
                body: JSON.stringify({
                    url: newDestUrl,
                    auth_type: newDestAuthType,
                    auth_config: Object.keys(newDestAuthConfig).length > 0 ? JSON.stringify(newDestAuthConfig) : null
                })
            });
            toast.success(`Success! ${res.message}`, { id: tid });
        } catch (err: any) {
            toast.error(`Test failed: ${err.message}`, { id: tid });
        }
    };

    return (
        <Box>
            <Typography variant="h4" sx={{ fontWeight: 600 }} gutterBottom>Endpoints</Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                Manage webhook receivers and forwarding destinations
            </Typography>

            <Paper sx={{ p: 3, mb: 4 }} elevation={1}>
                
            </Paper>

            {selectedProjectId && !isViewer && (
                <>
                    <Paper sx={{ p: 3, mb: 4 }} elevation={1}>
                        <Typography variant="h6" gutterBottom>New Endpoint</Typography>
                        <Box component="form" onSubmit={handleCreateEndpoint} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                            <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
                                <TextField size="small" label="Name" value={newEpName} onChange={handleNameChange} required fullWidth />
                                <TextField size="small" label="Slug (URL Path)" value={newEpSlug} onChange={handleSlugChange} required fullWidth placeholder="meta-waba-v1" helperText="Only lowercase letters, numbers, and hyphens" />
                            </Box>
                            
                            <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
                                <FormControl fullWidth size="small">
                                    <InputLabel>Authentication Type</InputLabel>
                                    <Select value={newAuthType} label="Authentication Type" onChange={e => { setNewAuthType(e.target.value); setNewAuthConfig({}); }}>
                                        <MenuItem value="none">None (Open)</MenuItem>
                                        <MenuItem value="meta">Meta Challenge Handshake</MenuItem>
                                        <MenuItem value="basic">Basic Auth</MenuItem>
                                        <MenuItem value="bearer">Bearer Token</MenuItem>
                                        <MenuItem value="hmac">HMAC Signature</MenuItem>
                                    </Select>
                                </FormControl>
                            </Box>
                            
                            {newAuthType === 'meta' && (
                                <TextField size="small" label="Verify Token" value={newAuthConfig.verify_token || ''} onChange={e => setNewAuthConfig({...newAuthConfig, verify_token: e.target.value})} required fullWidth helperText="Token configured in Meta App Dashboard" />
                            )}
                            
                            {newAuthType === 'basic' && (
                                <Box sx={{ display: 'flex', gap: 2 }}>
                                    <TextField size="small" label="Username" value={newAuthConfig.username || ''} onChange={e => setNewAuthConfig({...newAuthConfig, username: e.target.value})} required fullWidth />
                                    <TextField size="small" label="Password" type="password" value={newAuthConfig.password || ''} onChange={e => setNewAuthConfig({...newAuthConfig, password: e.target.value})} required fullWidth />
                                </Box>
                            )}

                            {newAuthType === 'bearer' && (
                                <TextField size="small" label="Bearer Token" value={newAuthConfig.token || ''} onChange={e => setNewAuthConfig({...newAuthConfig, token: e.target.value})} required fullWidth helperText="Secret token clients must provide" />
                            )}

                            {newAuthType === 'hmac' && (
                                <Box sx={{ display: 'flex', gap: 2 }}>
                                    <TextField size="small" label="Header Name" value={newAuthConfig.header_name || ''} onChange={e => setNewAuthConfig({...newAuthConfig, header_name: e.target.value})} placeholder="x-hub-signature" required fullWidth />
                                    <TextField size="small" label="Secret Key" value={newAuthConfig.secret || ''} onChange={e => setNewAuthConfig({...newAuthConfig, secret: e.target.value})} required fullWidth />
                                    <FormControl fullWidth size="small">
                                        <InputLabel>Algorithm</InputLabel>
                                        <Select value={newAuthConfig.algorithm || 'sha256'} label="Algorithm" onChange={e => setNewAuthConfig({...newAuthConfig, algorithm: e.target.value})}>
                                            <MenuItem value="sha256">SHA-256</MenuItem>
                                            <MenuItem value="sha1">SHA-1</MenuItem>
                                        </Select>
                                    </FormControl>
                                </Box>
                            )}

                            <Button type="submit" variant="contained" disabled={isCreating} sx={{ alignSelf: 'flex-start', mt: 1 }}>
                                Create Endpoint
                            </Button>
                        </Box>
                    </Paper>
                </>
            )}

            {selectedProjectId && (
                <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', md: 'row' } }}>
                    <Box sx={{ flex: 1, minWidth: '300px' }}>

                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                        {endpoints.map(ep => (
                            <Card key={ep.id} elevation={1}>
                                <CardContent>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                                        <Box>
                                            <Typography variant="h6">{ep.name}</Typography>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, bgcolor: '#f5f5f5', p: 1, borderRadius: 1, mt: 1 }}>
                                                <Typography variant="body2" color="primary" sx={{ fontFamily: 'monospace' }}>
                                                    {window.location.origin}/webhook/{ep.project_id}/{ep.slug}
                                                </Typography>
                                                <Button 
                                                    size="small" 
                                                    onClick={() => {
                                                        navigator.clipboard.writeText(`${window.location.origin}/webhook/${ep.project_id}/${ep.slug}`);
                                                        toast.success('Webhook URL Copied!');
                                                    }}
                                                    sx={{ minWidth: 'auto', p: 0.5 }}
                                                    title="Copy URL"
                                                >
                                                    <ContentCopyIcon fontSize="small" />
                                                </Button>
                                            </Box>
                                        </Box>
                                        <Box sx={{ display: 'flex', gap: 1 }}>
                                            {!isViewer && (
                                                <Button size="small" color="primary" startIcon={<EditIcon />} onClick={() => setEditEndpoint({...ep})}>
                                                    Edit
                                                </Button>
                                            )}
                                            {!isViewer && (
                                                <Button size="small" color="error" startIcon={<DeleteIcon />} onClick={() => handleDeleteEndpoint(ep.id)}>
                                                    Delete
                                                </Button>
                                            )}
                                        </Box>
                                    </Box>
                                    <Divider sx={{ mb: 2 }} />
                                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>FORWARDING DESTINATIONS</Typography>
                                    <List dense>
                                        {ep.destinations.map(dest => (
                                            <ListItem key={dest.id} disablePadding sx={{ mb: 1 }}>
                                                <ListItemIcon sx={{ minWidth: 36 }}><SendIcon color="action" fontSize="small" /></ListItemIcon>

                                                <ListItemText 
                                                    primary={dest.url} 
                                                    secondary={dest.is_active ? 'Active' : 'Inactive'} 
                                                />
                                                {!isViewer && (
                                                    <Box sx={{ display: 'flex', gap: 1 }}>
                                                        <Button size="small" color="primary" onClick={() => handleTestExistingDestination(dest)}>
                                                            Test
                                                        </Button>
                                                        <Button size="small" color="primary" onClick={() => setEditDestination({ ...dest, endpoint_id: ep.id })}>
                                                            <EditIcon fontSize="small" />
                                                        </Button>
                                                        <Button size="small" color="error" onClick={() => handleDeleteDestination(ep.id, dest.id)}>
                                                            <DeleteIcon fontSize="small" />
                                                        </Button>
                                                    </Box>
                                                )}

                                            </ListItem>
                                        ))}
                                    </List>
                                    
                                    {!isViewer && (
                                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, mt: 2, bgcolor: '#f5f5f5', p: 1.5, borderRadius: 1 }}>
                                            <Typography variant="subtitle2">Add New Destination</Typography>
                                            <Box sx={{ display: 'flex', gap: 1 }}>
                                                <TextField 
                                                    size="small" 
                                                    placeholder="Destination URL (http/https)" 
                                                    fullWidth
                                                    value={activeEndpointId === ep.id ? newDestUrl : ''}
                                                    onChange={e => {
                                                        setActiveEndpointId(ep.id);
                                                        setNewDestUrl(e.target.value);
                                                    }}
                                                />
                                                <Button variant="outlined" size="small" onClick={handleTestDestination} disabled={!newDestUrl || activeEndpointId !== ep.id} sx={{ minWidth: 140 }}>
                                                    Test Connection
                                                </Button>
                                                <Button variant="contained" size="small" onClick={(e) => handleAddDestination(e, ep.id)} disabled={!newDestUrl || activeEndpointId !== ep.id}>
                                                    Add
                                                </Button>
                                            </Box>
                                            
                                            {activeEndpointId === ep.id && (
                                                <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                                                    <FormControl size="small" sx={{ minWidth: 150 }}>
                                                        <InputLabel>Auth Type</InputLabel>
                                                        <Select value={newDestAuthType} label="Auth Type" onChange={e => setNewDestAuthType(e.target.value)}>

                                                            <MenuItem value="none">None</MenuItem>
                                                            <MenuItem value="basic">Basic Auth</MenuItem>
                                                            <MenuItem value="bearer">Bearer Token</MenuItem>
                                                            <MenuItem value="custom_header">Custom Header</MenuItem>
                                                            <MenuItem value="query_param">API Key (Query Param)</MenuItem>
                                                            <MenuItem value="hmac">HMAC Signature</MenuItem>

                                                        </Select>
                                                    </FormControl>
                                                    
                                                    {newDestAuthType === 'basic' && (
                                                        <Box sx={{ display: 'flex', gap: 1, flex: 1 }}>
                                                            <TextField size="small" placeholder="Username" fullWidth onChange={e => setNewDestAuthConfig({...newDestAuthConfig, username: e.target.value})} />
                                                            <TextField size="small" placeholder="Password" fullWidth type="password" onChange={e => setNewDestAuthConfig({...newDestAuthConfig, password: e.target.value})} />
                                                        </Box>
                                                    )}
                                                    {newDestAuthType === 'bearer' && (
                                                        <TextField size="small" placeholder="Token" fullWidth onChange={e => setNewDestAuthConfig({...newDestAuthConfig, token: e.target.value})} />
                                                    )}

                                                    {newDestAuthType === 'custom_header' && (
                                                        <Box sx={{ display: 'flex', gap: 1, flex: 1 }}>
                                                            <TextField size="small" placeholder="Header Name (e.g., x-api-key)" fullWidth onChange={e => setNewDestAuthConfig({...newDestAuthConfig, header_name: e.target.value})} />
                                                            <TextField size="small" placeholder="Header Value" fullWidth onChange={e => setNewDestAuthConfig({...newDestAuthConfig, header_value: e.target.value})} />
                                                        </Box>
                                                    )}
                                                    {newDestAuthType === 'query_param' && (
                                                        <Box sx={{ display: 'flex', gap: 1, flex: 1 }}>
                                                            <TextField size="small" placeholder="Param Name (e.g., apikey)" fullWidth onChange={e => setNewDestAuthConfig({...newDestAuthConfig, param_name: e.target.value})} />
                                                            <TextField size="small" placeholder="Param Value" fullWidth onChange={e => setNewDestAuthConfig({...newDestAuthConfig, param_value: e.target.value})} />
                                                        </Box>
                                                    )}
                                                    {newDestAuthType === 'hmac' && (
                                                        <Box sx={{ display: 'flex', gap: 1, flex: 1 }}>
                                                            <TextField size="small" placeholder="Header Name (default: X-Hub-Signature-256)" fullWidth onChange={e => setNewDestAuthConfig({...newDestAuthConfig, header_name: e.target.value})} />
                                                            <TextField size="small" placeholder="Secret Key" fullWidth onChange={e => setNewDestAuthConfig({...newDestAuthConfig, secret: e.target.value})} />
                                                            <FormControl size="small" sx={{ minWidth: 100 }}>
                                                                <Select value={newDestAuthConfig.algorithm || 'sha256'} onChange={e => setNewDestAuthConfig({...newDestAuthConfig, algorithm: e.target.value as string})}>
                                                                    <MenuItem value="sha256">SHA-256</MenuItem>
                                                                    <MenuItem value="sha1">SHA-1</MenuItem>
                                                                </Select>
                                                            </FormControl>
                                                        </Box>
                                                    )}

                                                </Box>
                                            )}
                                        </Box>
                                    )}
                                </CardContent>
                            </Card>
                        ))}
                        </Box>
                    </Box>
                </Box>
            )}

            {editEndpoint && (
                <Dialog open={!!editEndpoint} onClose={() => setEditEndpoint(null)} maxWidth="sm" fullWidth>
                    <DialogTitle>Edit Endpoint</DialogTitle>
                    <Box component="form" onSubmit={handleUpdateEndpoint}>
                        <DialogContent dividers sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                            <TextField size="small" label="Name" value={editEndpoint.name} onChange={e => setEditEndpoint({...editEndpoint, name: e.target.value})} required fullWidth />
                            <TextField size="small" label="Slug (URL Path)" value={editEndpoint.slug} onChange={e => setEditEndpoint({...editEndpoint, slug: e.target.value})} required fullWidth />
                            
                            <FormControl fullWidth size="small">
                                <InputLabel>Authentication Type</InputLabel>
                                <Select value={editEndpoint.auth_type} label="Authentication Type" onChange={e => setEditEndpoint({...editEndpoint, auth_type: e.target.value, auth_config: null})}>
                                    <MenuItem value="none">None (Open)</MenuItem>
                                    <MenuItem value="meta">Meta Challenge Handshake</MenuItem>
                                    <MenuItem value="basic">Basic Auth</MenuItem>
                                    <MenuItem value="bearer">Bearer Token</MenuItem>
                                    <MenuItem value="hmac">HMAC Signature</MenuItem>
                                </Select>
                            </FormControl>

                            {/* Render Auth Config fields based on auth_type, parsing JSON string to object for editing */}
                            {(() => {
                                let config: any = {};
                                try { config = JSON.parse(editEndpoint.auth_config || '{}'); } catch {}
                                
                                const updateConfig = (newCfg: any) => {
                                    setEditEndpoint({...editEndpoint, auth_config: JSON.stringify({...config, ...newCfg})});
                                };

                                if (editEndpoint.auth_type === 'meta') {
                                    return <TextField size="small" label="Verify Token" value={config.verify_token || ''} onChange={e => updateConfig({verify_token: e.target.value})} required fullWidth />;
                                }
                                if (editEndpoint.auth_type === 'basic') {
                                    return (
                                        <Box sx={{ display: 'flex', gap: 2 }}>
                                            <TextField size="small" label="Username" value={config.username || ''} onChange={e => updateConfig({username: e.target.value})} required fullWidth />
                                            <TextField size="small" label="Password" type="password" value={config.password || ''} onChange={e => updateConfig({password: e.target.value})} required fullWidth />
                                        </Box>
                                    );
                                }
                                if (editEndpoint.auth_type === 'bearer') {
                                    return <TextField size="small" label="Bearer Token" value={config.token || ''} onChange={e => updateConfig({token: e.target.value})} required fullWidth />;
                                }
                                if (editEndpoint.auth_type === 'hmac') {
                                    return (
                                        <Box sx={{ display: 'flex', gap: 2 }}>
                                            <TextField size="small" label="Header Name" value={config.header_name || ''} onChange={e => updateConfig({header_name: e.target.value})} required fullWidth />
                                            <TextField size="small" label="Secret Key" value={config.secret || ''} onChange={e => updateConfig({secret: e.target.value})} required fullWidth />
                                            <FormControl fullWidth size="small">
                                                <InputLabel>Algorithm</InputLabel>
                                                <Select value={config.algorithm || 'sha256'} label="Algorithm" onChange={e => updateConfig({algorithm: e.target.value})}>
                                                    <MenuItem value="sha256">SHA-256</MenuItem>
                                                    <MenuItem value="sha1">SHA-1</MenuItem>
                                                </Select>
                                            </FormControl>
                                        </Box>
                                    );
                                }
                                return null;
                            })()}

                        </DialogContent>
                        <DialogActions>
                            <Button onClick={() => setEditEndpoint(null)}>Cancel</Button>
                            <Button type="submit" variant="contained">Save Changes</Button>
                        </DialogActions>
                    </Box>
                </Dialog>
            )}


            {editDestination && (
                <Dialog open={!!editDestination} onClose={() => setEditDestination(null)} maxWidth="sm" fullWidth>
                    <DialogTitle>Edit Destination</DialogTitle>
                    <Box component="form" onSubmit={handleUpdateDestination}>
                        <DialogContent dividers sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                            <TextField size="small" label="URL" value={editDestination.url} onChange={e => setEditDestination({...editDestination, url: e.target.value})} required fullWidth />
                            
                            <FormControl fullWidth size="small">
                                <InputLabel>Authentication Type</InputLabel>
                                <Select value={editDestination.auth_type || 'none'} label="Authentication Type" onChange={e => setEditDestination({...editDestination, auth_type: e.target.value, auth_config: undefined})}>
                                    <MenuItem value="none">None</MenuItem>
                                    <MenuItem value="basic">Basic Auth</MenuItem>
                                    <MenuItem value="bearer">Bearer Token</MenuItem>
                                    <MenuItem value="custom_header">Custom Header</MenuItem>
                                    <MenuItem value="query_param">API Key (Query Param)</MenuItem>
                                    <MenuItem value="hmac">HMAC Signature</MenuItem>
                                </Select>
                            </FormControl>

                            {/* Render Auth Config fields based on auth_type */}
                            {(() => {
                                let config: any = {};
                                try { config = JSON.parse(editDestination.auth_config || '{}'); } catch {}
                                
                                const updateConfig = (newCfg: any) => {
                                    setEditDestination({...editDestination, auth_config: JSON.stringify({...config, ...newCfg})});
                                };

                                if (editDestination.auth_type === 'basic') {
                                    return (
                                        <Box sx={{ display: 'flex', gap: 2 }}>
                                            <TextField size="small" label="Username" value={config.username || ''} onChange={e => updateConfig({username: e.target.value})} required fullWidth />
                                            <TextField size="small" label="Password" type="password" value={config.password || ''} onChange={e => updateConfig({password: e.target.value})} required fullWidth />
                                        </Box>
                                    );
                                }
                                if (editDestination.auth_type === 'bearer') {
                                    return <TextField size="small" label="Bearer Token" value={config.token || ''} onChange={e => updateConfig({token: e.target.value})} required fullWidth />;
                                }
                                if (editDestination.auth_type === 'custom_header') {
                                    return (
                                        <Box sx={{ display: 'flex', gap: 2 }}>
                                            <TextField size="small" label="Header Name" value={config.header_name || ''} onChange={e => updateConfig({header_name: e.target.value})} required fullWidth />
                                            <TextField size="small" label="Header Value" value={config.header_value || ''} onChange={e => updateConfig({header_value: e.target.value})} required fullWidth />
                                        </Box>
                                    );
                                }
                                if (editDestination.auth_type === 'query_param') {
                                    return (
                                        <Box sx={{ display: 'flex', gap: 2 }}>
                                            <TextField size="small" label="Param Name" value={config.param_name || ''} onChange={e => updateConfig({param_name: e.target.value})} required fullWidth />
                                            <TextField size="small" label="Param Value" value={config.param_value || ''} onChange={e => updateConfig({param_value: e.target.value})} required fullWidth />
                                        </Box>
                                    );
                                }
                                if (editDestination.auth_type === 'hmac') {
                                    return (
                                        <Box sx={{ display: 'flex', gap: 2 }}>
                                            <TextField size="small" label="Header Name (default: X-Hub-Signature-256)" value={config.header_name || ''} onChange={e => updateConfig({header_name: e.target.value})} required fullWidth />
                                            <TextField size="small" label="Secret Key" value={config.secret || ''} onChange={e => updateConfig({secret: e.target.value})} required fullWidth />
                                            <FormControl fullWidth size="small">
                                                <InputLabel>Algorithm</InputLabel>
                                                <Select value={config.algorithm || 'sha256'} label="Algorithm" onChange={e => updateConfig({algorithm: e.target.value})}>
                                                    <MenuItem value="sha256">SHA-256</MenuItem>
                                                    <MenuItem value="sha1">SHA-1</MenuItem>
                                                </Select>
                                            </FormControl>
                                        </Box>
                                    );
                                }
                                return null;
                            })()}
                        </DialogContent>
                        <DialogActions>
                            <Button onClick={() => setEditDestination(null)}>Cancel</Button>
                            <Button type="submit" variant="contained">Save Changes</Button>
                        </DialogActions>
                    </Box>
                </Dialog>
            )}
        </Box>
    );
}
