import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, TextField, Button, CircularProgress, Alert, Divider } from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import { fetchApi } from '../api';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

export default function SystemLimits() {
    const [limits, setLimits] = useState({
        max_projects_per_user: 5,
        max_endpoints_per_project: 10,
        max_logs_per_endpoint: 1000,
        max_destinations_per_endpoint: 5
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        document.title = "System Limits - Webhook Forwarder";
        fetchLimits();
    }, []);

    const fetchLimits = async () => {
        try {
            const data = await fetchApi('/api/settings/system');
            setLimits(data);
        } catch (err: any) {
            toast.error(err.message || 'Failed to fetch system limits');
            if (err.status === 403) {
                navigate('/');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        const tid = toast.loading('Saving system limits...');
        try {
            await fetchApi('/api/settings/system', {
                method: 'PUT',
                body: JSON.stringify(limits)
            });
            toast.success('System limits updated successfully', { id: tid });
        } catch (err: any) {
            toast.error(err.message || 'Failed to save system limits', { id: tid });
        } finally {
            setSaving(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setLimits(prev => ({
            ...prev,
            [name]: parseInt(value) || 0
        }));
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}>
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
            <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
                System Limits
            </Typography>

            <Paper sx={{ p: 4, borderRadius: 2 }}>
                <Alert severity="info" sx={{ mb: 4 }}>
                    These limits apply globally to all users on this Webhook Forwarder instance.
                </Alert>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                    <Box>
                        <Typography variant="h6" sx={{ mb: 1 }}>Projects per User</Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            The maximum number of projects a single user can create.
                        </Typography>
                        <TextField
                            fullWidth
                            type="number"
                            name="max_projects_per_user"
                            value={limits.max_projects_per_user}
                            onChange={handleChange}
                        />
                    </Box>

                    <Box>
                        <Typography variant="h6" sx={{ mb: 1 }}>Endpoints per Project</Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            The maximum number of webhook endpoints allowed inside a single project.
                        </Typography>
                        <TextField
                            fullWidth
                            type="number"
                            name="max_endpoints_per_project"
                            value={limits.max_endpoints_per_project}
                            onChange={handleChange}
                        />
                    </Box>

                    <Box>
                        <Typography variant="h6" sx={{ mb: 1 }}>Logs per Endpoint (Retention)</Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            The maximum number of delivery logs kept for each endpoint. When this limit is reached, older logs are automatically deleted to save database space.
                        </Typography>
                        <TextField
                            fullWidth
                            type="number"
                            name="max_logs_per_endpoint"
                            value={limits.max_logs_per_endpoint}
                            onChange={handleChange}
                        />
                    </Box>

                    <Divider />

                    <Box>
                        <Typography variant="h6" sx={{ mb: 1 }}>Destinations per Endpoint</Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            The maximum number of forwarding destinations allowed per webhook endpoint.
                        </Typography>
                        <TextField
                            fullWidth
                            type="number"
                            name="max_destinations_per_endpoint"
                            value={limits.max_destinations_per_endpoint}
                            onChange={handleChange}
                        />
                    </Box>
                </Box>

                <Box sx={{ mt: 5, display: 'flex', justifyContent: 'flex-end' }}>
                    <Button 
                        variant="contained" 
                        color="primary" 
                        startIcon={<SaveIcon />}
                        onClick={handleSave}
                        disabled={saving}
                        size="large"
                    >
                        Save Settings
                    </Button>
                </Box>
            </Paper>
        </Box>
    );
}
