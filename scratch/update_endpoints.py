import os

file_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/Endpoints.tsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Destination Interface
content = content.replace(
    "interface Destination { id: number; url: string; is_active: boolean; }",
    "interface Destination { id: number; url: string; is_active: boolean; auth_type?: string; auth_config?: string; endpoint_id?: number; }"
)

# 2. Add editDestination state
content = content.replace(
    "const [editEndpoint, setEditEndpoint] = useState<Endpoint | null>(null);",
    "const [editEndpoint, setEditEndpoint] = useState<Endpoint | null>(null);\n    const [editDestination, setEditDestination] = useState<Destination | null>(null);"
)

# 3. Add handleUpdateDestination
handle_update_dest_code = """
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

    const handleTestExistingDestination = async (dest: Destination, epId: number) => {
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
"""
content = content.replace(
    "    const handleDeleteEndpoint = async",
    handle_update_dest_code + "\n    const handleDeleteEndpoint = async"
)

# 4. Add Buttons to Destination List
dest_list_item = """
                                                <ListItemText 
                                                    primary={dest.url} 
                                                    secondary={dest.is_active ? 'Active' : 'Inactive'} 
                                                />
                                                {!isViewer && (
                                                    <Box sx={{ display: 'flex', gap: 1 }}>
                                                        <Button size="small" color="primary" onClick={() => handleTestExistingDestination(dest, ep.id)}>
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
"""
content = content.replace(
    """                                                <ListItemText 
                                                    primary={dest.url} 
                                                    secondary={dest.is_active ? 'Active' : 'Inactive'} 
                                                />
                                                {!isViewer && (
                                                    <Button size="small" color="error" onClick={() => handleDeleteDestination(ep.id, dest.id)}>
                                                        <DeleteIcon fontSize="small" />
                                                    </Button>
                                                )}""",
    dest_list_item
)

# 5. Add new auth types to Create form
new_auth_types = """
                                                            <MenuItem value="none">None</MenuItem>
                                                            <MenuItem value="basic">Basic Auth</MenuItem>
                                                            <MenuItem value="bearer">Bearer Token</MenuItem>
                                                            <MenuItem value="custom_header">Custom Header</MenuItem>
                                                            <MenuItem value="query_param">API Key (Query Param)</MenuItem>
                                                            <MenuItem value="hmac">HMAC Signature</MenuItem>
"""
content = content.replace(
    """                                                            <MenuItem value="none">None</MenuItem>
                                                            <MenuItem value="basic">Basic Auth</MenuItem>
                                                            <MenuItem value="bearer">Bearer Token</MenuItem>
                                                            <MenuItem value="custom_header">Custom Header</MenuItem>""",
    new_auth_types
)

new_auth_fields = """
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
"""
content = content.replace(
    """                                                    {newDestAuthType === 'custom_header' && (
                                                        <Box sx={{ display: 'flex', gap: 1, flex: 1 }}>
                                                            <TextField size="small" placeholder="Header Name (e.g., x-api-key)" fullWidth onChange={e => setNewDestAuthConfig({...newDestAuthConfig, header_name: e.target.value})} />
                                                            <TextField size="small" placeholder="Header Value" fullWidth onChange={e => setNewDestAuthConfig({...newDestAuthConfig, header_value: e.target.value})} />
                                                        </Box>
                                                    )}""",
    new_auth_fields
)

# 6. Add Edit Destination Dialog
edit_dest_dialog = """

            {editDestination && (
                <Dialog open={!!editDestination} onClose={() => setEditDestination(null)} maxWidth="sm" fullWidth>
                    <DialogTitle>Edit Destination</DialogTitle>
                    <Box component="form" onSubmit={handleUpdateDestination}>
                        <DialogContent dividers sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                            <TextField size="small" label="URL" value={editDestination.url} onChange={e => setEditDestination({...editDestination, url: e.target.value})} required fullWidth />
                            
                            <FormControl fullWidth size="small">
                                <InputLabel>Authentication Type</InputLabel>
                                <Select value={editDestination.auth_type || 'none'} label="Authentication Type" onChange={e => setEditDestination({...editDestination, auth_type: e.target.value, auth_config: null})}>
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
"""

content = content.replace(
    "        </Box>\n    );\n}",
    edit_dest_dialog + "    );\n}"
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated Endpoints.tsx successfully!")
