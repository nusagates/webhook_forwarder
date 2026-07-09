import { useState, useEffect } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, FormControl, InputLabel, Select, MenuItem, Box, Alert } from '@mui/material';
import { fetchApi } from '../api';
import toast from 'react-hot-toast';

interface DatabaseSettingsDialogProps {
    open: boolean;
    onClose: () => void;
}

export default function DatabaseSettingsDialog({ open, onClose }: DatabaseSettingsDialogProps) {
    const [engine, setEngine] = useState('sqlite');
    const [host, setHost] = useState('localhost');
    const [port, setPort] = useState('');
    const [user, setUser] = useState('');
    const [password, setPassword] = useState('');
    const [dbName, setDbName] = useState('');
    
    const [currentUrl, setCurrentUrl] = useState('');
    const [currentEngine, setCurrentEngine] = useState('');

    useEffect(() => {
        if (open) {
            loadCurrentSettings();
        }
    }, [open]);

    const loadCurrentSettings = async () => {
        try {
            const data = await fetchApi('/api/settings/db');
            setCurrentUrl(data.url);
            setCurrentEngine(data.engine);
        } catch (e: any) {
            toast.error(e.message || "Failed to load database settings");
        }
    };

    const buildConnectionString = () => {
        if (engine === 'sqlite') {
            return `sqlite:///./webhook.db`;
        }
        const p = port ? `:${port}` : '';
        if (engine === 'postgresql') {
            return `postgresql://${user}:${password}@${host}${p}/${dbName}`;
        }
        if (engine === 'mysql') {
            return `mysql+pymysql://${user}:${password}@${host}${p}/${dbName}`;
        }
        return '';
    };

    const handleTest = async () => {
        const url = buildConnectionString();
        const tid = toast.loading('Testing connection...');
        try {
            await fetchApi('/api/settings/db/test', {
                method: 'POST',
                body: JSON.stringify({ url })
            });
            toast.success('Connection successful!', { id: tid });
        } catch (e: any) {
            toast.error(e.message || 'Connection failed', { id: tid });
        }
    };

    const handleCreate = async () => {
        const url = buildConnectionString();
        if (engine === 'sqlite') {
            toast.success("SQLite database is created automatically.");
            return;
        }
        
        const tid = toast.loading('Creating database...');
        try {
            const res = await fetchApi('/api/settings/db/create', {
                method: 'POST',
                body: JSON.stringify({ url })
            });
            toast.success(res.message, { id: tid });
        } catch (e: any) {
            toast.error(e.message || 'Failed to create database', { id: tid });
        }
    };

    const handleMigrate = async () => {
        if (!confirm("Are you sure you want to migrate all data to the new database? This process may take a while depending on your log volume.")) return;
        
        const url = buildConnectionString();
        const tid = toast.loading('Migrating database...');
        try {
            const res = await fetchApi('/api/settings/db/migrate', {
                method: 'POST',
                body: JSON.stringify({ url })
            });
            toast.success(res.message, { id: tid, duration: 8000 });
            onClose();
        } catch (e: any) {
            toast.error(e.message || 'Migration failed', { id: tid, duration: 5000 });
        }
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle>Database Settings & Migration</DialogTitle>
            <DialogContent dividers sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Alert severity="info" sx={{ mb: 1 }}>
                    <strong>Current Active Database:</strong><br />
                    Engine: {currentEngine}<br />
                    URL: {currentUrl}
                </Alert>

                <FormControl fullWidth size="small">
                    <InputLabel>Database Engine</InputLabel>
                    <Select value={engine} label="Database Engine" onChange={e => setEngine(e.target.value)}>
                        <MenuItem value="sqlite">SQLite (Local File)</MenuItem>
                        <MenuItem value="postgresql">PostgreSQL</MenuItem>
                        <MenuItem value="mysql">MariaDB / MySQL</MenuItem>
                    </Select>
                </FormControl>

                {engine !== 'sqlite' && (
                    <>
                        <Box sx={{ display: 'flex', gap: 2 }}>
                            <TextField size="small" label="Host" value={host} onChange={e => setHost(e.target.value)} fullWidth />
                            <TextField size="small" label="Port" value={port} onChange={e => setPort(e.target.value)} placeholder={engine === 'postgresql' ? '5432' : '3306'} sx={{ width: '150px' }} />
                        </Box>
                        <Box sx={{ display: 'flex', gap: 2 }}>
                            <TextField size="small" label="Username" value={user} onChange={e => setUser(e.target.value)} fullWidth />
                            <TextField size="small" label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} fullWidth />
                        </Box>
                        <TextField size="small" label="Database Name" value={dbName} onChange={e => setDbName(e.target.value)} fullWidth />
                    </>
                )}
            </DialogContent>
            <DialogActions sx={{ p: 2, justifyContent: 'space-between' }}>
                <Box>
                    <Button onClick={handleTest} color="primary" variant="outlined" sx={{ mr: 1 }}>Test Connection</Button>
                    {engine !== 'sqlite' && <Button onClick={handleCreate} color="secondary" variant="outlined">Create DB</Button>}
                </Box>
                <Box>
                    <Button onClick={onClose} sx={{ mr: 1 }}>Cancel</Button>
                    <Button onClick={handleMigrate} variant="contained" color="warning">Migrate & Save</Button>
                </Box>
            </DialogActions>
        </Dialog>
    );
}
