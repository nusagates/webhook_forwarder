import { useConfirm } from '../components/ConfirmDialog';
import { useState, useEffect } from 'react';
import {
    Box, Typography, Paper, Alert, Button, TextField,
    FormControl, InputLabel, Select, MenuItem, Divider, Chip
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import SyncAltIcon from '@mui/icons-material/SyncAlt';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import StorageIcon from '@mui/icons-material/Storage';
import VerifiedIcon from '@mui/icons-material/Verified';
import AddCircleIcon from '@mui/icons-material/AddCircle';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { fetchApi } from '../api';
import toast from 'react-hot-toast';

export default function DatabaseSettings() {
    const confirm = useConfirm();

    const [engine, setEngine] = useState('sqlite');
    const [host, setHost] = useState('localhost');
    const [port, setPort] = useState('');
    const [user, setUser] = useState('');
    const [password, setPassword] = useState('');
    const [dbName, setDbName] = useState('');

    const [currentUrl, setCurrentUrl] = useState('');
    const [currentEngine, setCurrentEngine] = useState('');
    const [consoleOutput, setConsoleOutput] = useState<{ type: 'info' | 'success' | 'error'; text: string } | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        document.title = 'Database Settings - Webhook Forwarder';
        loadCurrentSettings();
    }, []);

    const loadCurrentSettings = async () => {
        setLoading(true);
        try {
            const data = await fetchApi('/api/settings/db');
            setCurrentUrl(data.url);
            setCurrentEngine(data.engine);

            if (data.raw_url && data.engine !== 'sqlite') {
                setEngine(data.engine);
                try {
                    const parseUrl = data.raw_url.replace('+pymysql', '');
                    const urlObj = new URL(parseUrl);
                    setHost(urlObj.hostname);
                    setPort(urlObj.port || '');
                    setUser(decodeURIComponent(urlObj.username));
                    setPassword(decodeURIComponent(urlObj.password));
                    setDbName(urlObj.pathname.substring(1));
                } catch (err) {
                    console.error('Failed to parse raw_url', err);
                }
            } else {
                setEngine('sqlite');
            }
        } catch (e: any) {
            toast.error(e.message || 'Failed to load database settings');
        } finally {
            setLoading(false);
        }
    };

    const buildConnectionString = () => {
        if (engine === 'sqlite') return `sqlite:///./webhook.db`;
        const p = port ? `:${port}` : '';
        if (engine === 'postgresql') return `postgresql://${user}:${password}@${host}${p}/${dbName}`;
        if (engine === 'mysql') return `mysql+pymysql://${user}:${password}@${host}${p}/${dbName}`;
        return '';
    };

    const handleVerify = async () => {
        const url = buildConnectionString();
        setConsoleOutput({ type: 'info', text: 'Verifying data on target database...' });
        try {
            const res = await fetchApi('/api/settings/db/verify', { method: 'POST', body: JSON.stringify({ url }) });
            setConsoleOutput({ type: 'success', text: res.message });
        } catch (e: any) {
            setConsoleOutput({ type: 'error', text: e.message || 'Verification failed' });
        }
    };

    const handleTest = async () => {
        const url = buildConnectionString();
        setConsoleOutput({ type: 'info', text: 'Testing connection...' });
        try {
            await fetchApi('/api/settings/db/test', { method: 'POST', body: JSON.stringify({ url }) });
            setConsoleOutput({ type: 'success', text: 'Connection successful! Database is reachable.' });
        } catch (e: any) {
            setConsoleOutput({ type: 'error', text: e.message || 'Connection failed' });
        }
    };

    const handleCreate = async () => {
        if (engine === 'sqlite') {
            setConsoleOutput({ type: 'info', text: 'SQLite database is created automatically.' });
            return;
        }
        setConsoleOutput({ type: 'info', text: 'Creating database...' });
        try {
            const res = await fetchApi('/api/settings/db/create', { method: 'POST', body: JSON.stringify({ url: buildConnectionString() }) });
            setConsoleOutput({ type: 'success', text: res.message });
        } catch (e: any) {
            setConsoleOutput({ type: 'error', text: e.message || 'Failed to create database' });
        }
    };

    const handleRestart = async () => {
        if (!await confirm({ message: 'Are you sure you want to restart the backend service? Active webhooks might be dropped during the restart.', isDanger: true })) return;
        try {
            const res = await fetchApi('/api/settings/restart', { method: 'POST' });
            setConsoleOutput({ type: 'success', text: res.message + '\n\nThe application will reload automatically.' });
            setTimeout(() => window.location.reload(), 3000);
        } catch (e: any) {
            setConsoleOutput({ type: 'error', text: e.message || 'Failed to restart service' });
        }
    };

    const handleSwitch = async () => {
        if (!await confirm({ message: 'Are you sure you want to switch the database? (This does NOT copy data, it only points the app to the new database).', isDanger: true })) return;
        setConsoleOutput({ type: 'info', text: 'Switching database...' });
        try {
            const res = await fetchApi('/api/settings/db/switch', { method: 'POST', body: JSON.stringify({ url: buildConnectionString() }) });
            setConsoleOutput({ type: 'success', text: res.message + '\n\nPlease click Restart Service to apply changes.' });
        } catch (e: any) {
            setConsoleOutput({ type: 'error', text: e.message || 'Switch failed' });
        }
    };

    const handleMigrate = async () => {
        if (!await confirm({ message: 'Are you sure you want to migrate all data to the new database? This process may take a while depending on your log volume.', isDanger: true })) return;
        setConsoleOutput({ type: 'info', text: 'Migrating database... Please wait, this might take a while.' });
        try {
            const res = await fetchApi('/api/settings/db/migrate', { method: 'POST', body: JSON.stringify({ url: buildConnectionString() }) });
            setConsoleOutput({ type: 'success', text: res.message + '\n\nMigration completed successfully.' });
        } catch (e: any) {
            setConsoleOutput({ type: 'error', text: e.message || 'Migration failed' });
        }
    };

    if (loading) return null;

    return (
        <Box sx={{ maxWidth: 760, mx: 'auto' }}>
            <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>Database Settings</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Configure the database connection and migrate data between databases.
            </Typography>

            {/* Current status */}
            <Paper variant="outlined" sx={{ p: 2.5, mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
                <StorageIcon color="primary" />
                <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 600, textTransform: 'uppercase', fontSize: '0.7rem', letterSpacing: 1 }}>
                        Active Database
                    </Typography>
                    <Typography variant="body1" sx={{ fontFamily: 'monospace', fontSize: '0.85rem', wordBreak: 'break-all' }}>
                        {currentUrl}
                    </Typography>
                </Box>
                <Chip
                    label={currentEngine.toUpperCase()}
                    color={currentEngine === 'sqlite' ? 'default' : 'primary'}
                    size="small"
                    variant="outlined"
                />
            </Paper>

            {/* Connection form */}
            <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }} elevation={0} variant="outlined">
                <Typography variant="h6" sx={{ mb: 2.5, fontWeight: 600 }}>Target Database Configuration</Typography>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
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
                                <TextField size="small" label="Port" value={port} onChange={e => setPort(e.target.value)} placeholder={engine === 'postgresql' ? '5432' : '3306'} sx={{ width: 130 }} />
                            </Box>
                            <Box sx={{ display: 'flex', gap: 2 }}>
                                <TextField size="small" label="Username" value={user} onChange={e => setUser(e.target.value)} fullWidth />
                                <TextField size="small" label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} fullWidth />
                            </Box>
                            <TextField size="small" label="Database Name" value={dbName} onChange={e => setDbName(e.target.value)} fullWidth />

                            {/* Connection string preview */}
                            <Alert severity="info" icon={false} sx={{ fontFamily: 'monospace', fontSize: '0.78rem', wordBreak: 'break-all' }}>
                                <strong>Connection string:</strong><br />{buildConnectionString()}
                            </Alert>
                        </>
                    )}
                </Box>
            </Paper>

            {/* Console output */}
            {consoleOutput && (
                <Paper variant="outlined" sx={{ mb: 3, overflow: 'hidden' }}>
                    <Box sx={{
                        p: 2,
                        bgcolor: '#1e1e1e',
                        color: consoleOutput.type === 'error' ? '#ff6b6b' : consoleOutput.type === 'success' ? '#69db7c' : '#4dabf7',
                        fontFamily: 'monospace',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-all',
                        maxHeight: 220,
                        overflowY: 'auto',
                        fontSize: '0.85rem',
                        position: 'relative',
                    }}>
                        <Button
                            size="small"
                            startIcon={<ContentCopyIcon fontSize="small" />}
                            sx={{ position: 'absolute', top: 8, right: 8, color: '#fff', minWidth: 'auto', fontSize: '0.7rem' }}
                            onClick={() => { navigator.clipboard.writeText(consoleOutput.text); toast.success('Copied'); }}
                        >
                            Copy
                        </Button>
                        {consoleOutput.text}
                    </Box>
                </Paper>
            )}

            {/* Actions */}
            <Paper variant="outlined" sx={{ p: 2.5 }}>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2, fontWeight: 600 }}>Actions</Typography>

                {/* Utility tools */}
                <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap', mb: 2 }}>
                    <Button onClick={handleTest} variant="outlined" startIcon={<PlayArrowIcon />} size="small">
                        Test Connection
                    </Button>
                    {engine !== 'sqlite' && (
                        <Button onClick={handleVerify} variant="outlined" color="info" startIcon={<VerifiedIcon />} size="small">
                            Verify Data
                        </Button>
                    )}
                    {engine !== 'sqlite' && (
                        <Button onClick={handleCreate} variant="outlined" color="secondary" startIcon={<AddCircleIcon />} size="small">
                            Create DB
                        </Button>
                    )}
                    <Button onClick={handleRestart} variant="outlined" color="error" startIcon={<RestartAltIcon />} size="small">
                        Restart Service
                    </Button>
                </Box>

                <Divider sx={{ my: 2 }} />

                {/* Primary actions */}
                <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                    {engine !== 'sqlite' && (
                        <Button onClick={handleSwitch} variant="contained" color="primary" startIcon={<SaveIcon />}>
                            Save &amp; Switch DB
                        </Button>
                    )}
                    <Button onClick={handleMigrate} variant="contained" color="warning" startIcon={<SyncAltIcon />}>
                        Migrate Data
                    </Button>
                </Box>
            </Paper>
        </Box>
    );
}
