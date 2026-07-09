import { useConfirm } from './ConfirmDialog';
import { useState, useEffect } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, FormControl, InputLabel, Select, MenuItem, Box, Alert } from '@mui/material';
import { fetchApi } from '../api';
import toast from 'react-hot-toast';

interface DatabaseSettingsDialogProps {
    open: boolean;
    onClose: () => void;
}

export default function DatabaseSettingsDialog({ open, onClose }: DatabaseSettingsDialogProps) {
    const handleClose = () => {
        setConsoleOutput(null);
        onClose();
    };
    const confirm = useConfirm();

    const [engine, setEngine] = useState('sqlite');
    const [host, setHost] = useState('localhost');
    const [port, setPort] = useState('');
    const [user, setUser] = useState('');
    const [password, setPassword] = useState('');
    const [dbName, setDbName] = useState('');
    
    const [currentUrl, setCurrentUrl] = useState('');
    const [currentEngine, setCurrentEngine] = useState('');
    const [consoleOutput, setConsoleOutput] = useState<{ type: 'info' | 'success' | 'error', text: string } | null>(null);

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
        setConsoleOutput({ type: 'info', text: 'Testing connection...' });
        try {
            await fetchApi('/api/settings/db/test', {
                method: 'POST',
                body: JSON.stringify({ url })
            });
            setConsoleOutput({ type: 'success', text: 'Connection successful! Database is reachable.' });
        } catch (e: any) {
            setConsoleOutput({ type: 'error', text: e.message || 'Connection failed' });
        }
    };

    const handleCreate = async () => {
        const url = buildConnectionString();
        if (engine === 'sqlite') {
            setConsoleOutput({ type: 'info', text: 'SQLite database is created automatically.' });
            return;
        }
        
        setConsoleOutput({ type: 'info', text: 'Creating database...' });
        try {
            const res = await fetchApi('/api/settings/db/create', {
                method: 'POST',
                body: JSON.stringify({ url })
            });
            setConsoleOutput({ type: 'success', text: res.message });
        } catch (e: any) {
            setConsoleOutput({ type: 'error', text: e.message || 'Failed to create database' });
        }
    };

    
    const handleRestart = async () => {
        if (!await confirm({ message: "Are you sure you want to restart the backend service? Active webhooks might be dropped during the restart.", isDanger: true })) return;
        
        try {
            const res = await fetchApi('/api/settings/restart', { method: 'POST' });
            setConsoleOutput({ type: 'success', text: res.message + '\n\nThe application will reload automatically.' });
            setTimeout(() => {
                window.location.reload();
            }, 3000);
        } catch (e: any) {
            setConsoleOutput({ type: 'error', text: e.message || 'Failed to restart service' });
        }
    };

    const handleMigrate = async () => {
        if (!await confirm({ message: "Are you sure you want to migrate all data to the new database? This process may take a while depending on your log volume.", isDanger: true })) return;
        
        const url = buildConnectionString();
        setConsoleOutput({ type: 'info', text: 'Migrating database... Please wait, this might take a while.' });
        try {
            const res = await fetchApi('/api/settings/db/migrate', {
                method: 'POST',
                body: JSON.stringify({ url })
            });
            setConsoleOutput({ type: 'success', text: res.message + '\n\nMigration completed successfully. You can close this dialog.' });
        } catch (e: any) {
            setConsoleOutput({ type: 'error', text: e.message || 'Migration failed' });
        }
    };

    return (
        <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
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

                {consoleOutput && (
                    <Box sx={{ 
                        mt: 2, 
                        p: 2, 
                        bgcolor: '#1e1e1e', 
                        color: consoleOutput.type === 'error' ? '#ff6b6b' : consoleOutput.type === 'success' ? '#69db7c' : '#4dabf7', 
                        borderRadius: 1,
                        fontFamily: 'monospace',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-all',
                        maxHeight: '200px',
                        overflowY: 'auto',
                        position: 'relative'
                    }}>
                        <Button 
                            size="small" 
                            sx={{ position: 'absolute', top: 5, right: 5, color: '#fff' }}
                            onClick={() => {
                                navigator.clipboard.writeText(consoleOutput.text);
                                toast.success('Copied to clipboard');
                            }}
                        >
                            Copy
                        </Button>
                        {consoleOutput.text}
                    </Box>
                )}
            </DialogContent>
            <DialogActions sx={{ p: 2, justifyContent: 'space-between' }}>
                <Box>
                    <Button onClick={handleTest} color="primary" variant="outlined" sx={{ mr: 1 }}>Test Connection</Button>
                    {engine !== 'sqlite' && <Button onClick={handleCreate} color="secondary" variant="outlined" sx={{ mr: 1 }}>Create DB</Button>}
                    <Button onClick={handleRestart} color="error" variant="outlined">Restart Service</Button>
                </Box>
                <Box>
                    <Button onClick={handleClose} sx={{ mr: 1 }}>Cancel</Button>
                    <Button onClick={handleMigrate} variant="contained" color="warning">Migrate & Save</Button>
                </Box>
            </DialogActions>
        </Dialog>
    );
}
