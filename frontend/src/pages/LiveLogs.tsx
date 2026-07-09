import React, { useEffect, useState, useRef } from 'react';
import { fetchApi } from '../api';
import toast from 'react-hot-toast';
import { Typography, Box, FormControl, InputLabel, Select, MenuItem, Chip, Checkbox, FormControlLabel, Button, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Pagination } from '@mui/material';
import FileCopyIcon from '@mui/icons-material/FileCopy';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import ClearIcon from '@mui/icons-material/Clear';
import ReplayIcon from '@mui/icons-material/Replay';
import ChecklistIcon from '@mui/icons-material/Checklist';

interface DeliveryLog { 
    id: number;
    status_code: number | null;
    http_method: string;
    client_ip: string | null;
    headers: string | null;
    query_params: string | null;
    payload: string;
    response_body: string | null;
    is_read: boolean;
    created_at: string;
}
interface Endpoint { id: number; name: string; slug: string; project_id: string; }
interface Project { id: string; name: string; my_role?: string; }

export default function LiveLogs() {
    const [projects, setProjects] = useState<Project[]>([]);
    const [selectedProjectId, setSelectedProjectId] = useState<string>('');
    const [endpoints, setEndpoints] = useState<Endpoint[]>([]);
    const [selectedEndpointId, setSelectedEndpointId] = useState<string>('');
    const [logs, setLogs] = useState<DeliveryLog[]>([]);
    const [selectedLogId, setSelectedLogId] = useState<number | null>(null);
    const [formatJson, setFormatJson] = useState(true);
    const [clearDialogOpen, setClearDialogOpen] = useState(false);
    
    // Pagination & Sorting State
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalLogs, setTotalLogs] = useState(0);
    const [sortBy, setSortBy] = useState('desc');
    const limit = 20;

    const wsRef = useRef<WebSocket | null>(null);

    const loadLogs = async (epId: number, currentPage = 1, currentSort = 'desc') => {
        try {
            const res = await fetchApi(`/api/logs?endpoint_id=${epId}&page=${currentPage}&limit=${limit}&sort=${currentSort}`);
            setLogs(res.items);
            setTotalPages(res.pages);
            setTotalLogs(res.total);
            setPage(currentPage);
        } catch (err) {
            console.error('Failed to load logs', err);
        }
    };

    useEffect(() => {
        loadProjects();
    }, []);

    useEffect(() => {
        const unreadCount = logs.filter(l => !l.is_read).length;
        if (unreadCount > 0) {
            document.title = `(${unreadCount}) Live Logs - Webhook Forwarder`;
        } else {
            document.title = "Live Logs - Webhook Forwarder";
        }
    }, [logs]);
    
    useEffect(() => {
        if (selectedProjectId) loadEndpoints(selectedProjectId);
        else { setEndpoints([]); setSelectedEndpointId(''); }
    }, [selectedProjectId]);

    useEffect(() => {
        if (selectedEndpointId) {
            loadLogs(selectedEndpointId as unknown as number, 1, sortBy);
        } else {
            setLogs([]);
            setTotalPages(1);
            setTotalLogs(0);
            if (wsRef.current) wsRef.current.close();
            return;
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/api/ws/logs/${selectedEndpointId}`;
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => toast.success('Connected to Live Stream');
        ws.onmessage = (event) => {
            try {
                const newLog = JSON.parse(event.data);
                newLog.is_read = false;
                
                setLogs(prev => {
                    if (page === 1 && sortBy === 'desc') {
                        const updated = [newLog, ...prev];
                        if (updated.length > limit) updated.pop();
                        return updated;
                    }
                    return prev;
                });
                
                if (page === 1 && sortBy === 'desc') {
                    setTotalLogs(prev => prev + 1);
                }
            } catch (e) {
                console.error("Error parsing websocket message", e);
            }
        };
        ws.onerror = () => toast.error('WebSocket connection error');
        ws.onclose = () => console.log('WebSocket closed');

        return () => { ws.close(); };
    }, [selectedEndpointId]);

    const handleDeleteLog = async (e: React.MouseEvent, id: number) => {
        e.stopPropagation();
        try {
            await fetchApi(`/api/logs/${id}`, { method: 'DELETE' });
            setLogs(prev => prev.filter(l => l.id !== id));
            if (selectedLogId === id) setSelectedLogId(null);
        } catch (err: any) {
            toast.error(err.message || 'Failed to delete log');
        }
    };

    const handlePageChange = (_event: React.ChangeEvent<unknown>, value: number) => {
        if (selectedEndpointId) {
            loadLogs(selectedEndpointId as unknown as number, value, sortBy);
        }
    };

    const handleSortChange = (event: any) => {
        const newSort = event.target.value;
        setSortBy(newSort);
        if (selectedEndpointId) {
            loadLogs(selectedEndpointId as unknown as number, 1, newSort);
        }
    };

    const handleResendLog = async (id: number) => {
        try {
            await fetchApi(`/api/logs/${id}/resend`, { method: 'POST' });
            toast.success('Webhook resend triggered!');
        } catch (err: any) {
            toast.error(err.message || 'Failed to resend webhook');
        }
    };

    const handleLogSelect = async (log: DeliveryLog) => {
        setSelectedLogId(log.id);
        if (!log.is_read) {
            setLogs(prev => prev.map(l => l.id === log.id ? { ...l, is_read: true } : l));
            try {
                await fetchApi(`/api/logs/${log.id}/read`, { method: 'PUT' });
            } catch (err) {
                console.error('Failed to mark read', err);
            }
        }
    };

    const handleMarkAllRead = async () => {
        if (!selectedEndpointId) return;
        setLogs(prev => prev.map(l => ({ ...l, is_read: true })));
        try {
            await fetchApi(`/api/endpoints/${selectedEndpointId}/logs/read`, { method: 'PUT' });
        } catch (err) {
            console.error('Failed to mark all as read', err);
        }
    };

    const handleClearLogs = async () => {
        if (!selectedEndpointId) return;
        try {
            await fetchApi(`/api/endpoints/${selectedEndpointId}/logs`, { method: 'DELETE' });
            setLogs([]);
            setSelectedLogId(null);
            setClearDialogOpen(false);
            toast.success('All logs cleared for this endpoint');
        } catch (err: any) {
            toast.error(err.message || 'Failed to clear logs');
        }
    };

    const loadProjects = async () => {
        try { setProjects(await fetchApi('/api/projects')); }
        catch (err) { console.error(err); }
    };

    const loadEndpoints = async (projId: string) => {
        try { setEndpoints(await fetchApi(`/api/endpoints?project_id=${projId}`)); }
        catch (err) { console.error(err); }
    };

    const selectedLog = logs.find(l => l.id === selectedLogId) || logs[0];
    const selectedProject = projects.find(p => p.id === selectedProjectId);
    const isViewer = selectedProject?.my_role === 'viewer';

    const getFormattedPayload = (payload: string) => {
        if (!formatJson) return payload;
        try {
            return JSON.stringify(JSON.parse(payload), null, 2);
        } catch {
            return payload; // Not JSON
        }
    };

    return (
        <Box sx={{ height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3, mb: 2 }}>
                <FormControl fullWidth size="small">
                    <InputLabel id="project-select-label">Select Project</InputLabel>
                    <Select
                        labelId="project-select-label"
                        value={selectedProjectId}
                        label="Select Project"
                        onChange={e => setSelectedProjectId(e.target.value)}
                    >
                        <MenuItem value=""><em>-- Choose Project --</em></MenuItem>
                        {projects.map(p => <MenuItem key={p.id} value={p.id}>{p.name}</MenuItem>)}
                    </Select>
                </FormControl>
                <FormControl fullWidth size="small" disabled={!selectedProjectId}>
                    <InputLabel id="endpoint-select-label">Select Endpoint</InputLabel>
                    <Select
                        labelId="endpoint-select-label"
                        value={selectedEndpointId}
                        label="Select Endpoint"
                        onChange={e => setSelectedEndpointId(e.target.value)}
                    >
                        <MenuItem value=""><em>-- Choose Endpoint --</em></MenuItem>
                        {endpoints.map(ep => <MenuItem key={ep.id} value={ep.id}>{ep.name}</MenuItem>)}
                    </Select>
                </FormControl>
            </Box>

            {selectedEndpointId && (() => {
                const ep = endpoints.find(e => e.id.toString() === selectedEndpointId);
                if (!ep) return null;
                const webhookUrl = `${window.location.origin}/webhook/${ep.project_id}/${ep.slug}`;
                return (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2, bgcolor: '#e3f2fd', p: 1.5, borderRadius: 1 }}>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>Your Unique Webhook URL:</Typography>
                        <Typography variant="body2" color="primary" sx={{ fontFamily: 'monospace', flex: 1 }}>{webhookUrl}</Typography>
                        <Button 
                            variant="contained" 
                            size="small" 
                            startIcon={<ContentCopyIcon />}
                            onClick={() => {
                                navigator.clipboard.writeText(webhookUrl);
                                toast.success('Webhook URL Copied!');
                            }}
                            sx={{ textTransform: 'none' }}
                        >
                            Copy to Clipboard
                        </Button>
                    </Box>
                );
            })()}

            {!selectedEndpointId ? (
                <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Typography color="text.secondary">Select an endpoint to start monitoring...</Typography>
                </Box>
            ) : (
                <Box sx={{ flex: 1, display: 'flex', borderTop: '1px solid #e0e0e0', overflow: 'hidden' }}>
                    {/* LEFT SIDEBAR: Log List */}
                    <Box sx={{ width: '320px', borderRight: '1px solid #e0e0e0', display: 'flex', flexDirection: 'column', bgcolor: '#f9f9f9' }}>
                        <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0', bgcolor: '#fff', display: 'flex', flexDirection: 'column', gap: 1 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Typography variant="subtitle2" color="text.secondary">INBOX ({totalLogs})</Typography>
                                <Box sx={{ display: 'flex', gap: 1 }}>
                                    {logs.some(l => !l.is_read) && (
                                        <Button size="small" onClick={handleMarkAllRead} startIcon={<ChecklistIcon />}>Mark Read</Button>
                                    )}
                                    {!isViewer && logs.length > 0 && (
                                        <Button size="small" color="error" onClick={() => setClearDialogOpen(true)}>Clear</Button>
                                    )}
                                </Box>
                            </Box>
                            <FormControl size="small" fullWidth sx={{ mt: 1 }}>
                                <Select value={sortBy} onChange={handleSortChange}>
                                    <MenuItem value="desc">Newest First</MenuItem>
                                    <MenuItem value="asc">Oldest First</MenuItem>
                                </Select>
                            </FormControl>
                        </Box>
                        
                        <Box sx={{ flex: 1, overflowY: 'auto' }}>
                            {logs.length === 0 ? (
                                <Typography color="text.secondary" sx={{ p: 3, fontStyle: 'italic', textAlign: 'center' }}>
                                    Waiting for webhooks...
                                </Typography>
                            ) : (
                                logs.map(log => (
                                <Box 
                                    key={log.id} 
                                    onClick={() => handleLogSelect(log)}
                                    sx={{ 
                                        p: 2, 
                                        borderBottom: '1px solid #e0e0e0', 
                                        cursor: 'pointer',
                                        position: 'relative',
                                        bgcolor: selectedLogId === log.id ? '#e3f2fd' : (!log.is_read ? '#f0f7ff' : 'transparent'),
                                        color: selectedLogId === log.id ? '#3582c4' : 'inherit',
                                        '&:hover': { bgcolor: selectedLogId === log.id ? '#e3f2fd' : '#f5f5f5' },
                                        '& .delete-btn': { display: 'none' },
                                        '&:hover .delete-btn': { display: 'flex' }
                                    }}
                                >
                                    {!log.is_read && (
                                        <Box sx={{ position: 'absolute', top: 10, right: 10, width: 8, height: 8, bgcolor: 'primary.main', borderRadius: '50%' }} />
                                    )}
                                    <Box sx={{ display: 'flex', gap: 1, mb: 1, alignItems: 'center' }}>
                                        <Chip 
                                            label={log.http_method} 
                                            size="small" 
                                            sx={{ 
                                                bgcolor: selectedLogId === log.id ? 'rgba(53,130,196,0.2)' : '#5bc0de',
                                                color: selectedLogId === log.id ? '#3582c4' : '#fff',
                                                fontWeight: 'bold', height: '20px', fontSize: '0.7rem' 
                                            }} 
                                        />
                                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>#{log.id.toString().substring(0,8)}</Typography>
                                        <Typography variant="caption" sx={{ ml: 'auto', opacity: 0.8, pr: 2 }}>
                                            {log.client_ip || 'Unknown IP'}
                                        </Typography>
                                    </Box>
                                    <Typography variant="caption" sx={{ opacity: 0.8 }}>
                                        {new Date(log.created_at).toLocaleString()}
                                    </Typography>
                                    {!isViewer && (
                                        <Box 
                                            className="delete-btn"
                                            onClick={(e) => handleDeleteLog(e, log.id)}
                                            sx={{
                                                position: 'absolute',
                                                right: 8,
                                                top: '50%',
                                                transform: 'translateY(-50%)',
                                                bgcolor: '#d9534f',
                                                color: '#fff',
                                                borderRadius: 1,
                                                width: 24,
                                                height: 24,
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                cursor: 'pointer',
                                                '&:hover': { bgcolor: '#c9302c' }
                                            }}
                                        >
                                            <ClearIcon sx={{ fontSize: 16 }} />
                                        </Box>
                                    )}
                                </Box>
                            ))
                        )}
                        </Box>
                        
                        {totalPages > 1 && (
                            <Box sx={{ p: 1, borderTop: '1px solid #e0e0e0', bgcolor: '#fff', display: 'flex', justifyContent: 'center' }}>
                                <Pagination 
                                    count={totalPages} 
                                    page={page} 
                                    onChange={handlePageChange} 
                                    size="small" 
                                    siblingCount={0}
                                    boundaryCount={1}
                                />
                            </Box>
                        )}
                    </Box>

                    {/* RIGHT MAIN PANEL: Log Details */}
                    <Box sx={{ flex: 1, overflowY: 'auto', bgcolor: '#fff', p: 0 }}>
                        {selectedLog ? (
                            <Box>
                                {/* Request Details Header */}
                                <Box sx={{ bgcolor: '#f5f5f5', p: 1.5, borderBottom: '1px solid #e0e0e0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 1 }}>
                                        Request Details & Headers
                                    </Typography>
                                    {!isViewer && (
                                        <Button 
                                            variant="outlined" 
                                            size="small" 
                                            startIcon={<ReplayIcon />}
                                            onClick={() => handleResendLog(selectedLog.id)}
                                        >
                                            Resend Webhook
                                        </Button>
                                    )}
                                </Box>
                                
                                <Box sx={{ p: 3 }}>
                                    <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 4 }}>
                                        {/* Left col info */}
                                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                                            <Box sx={{ display: 'flex' }}><Typography sx={{ width: '100px', color: 'text.secondary', fontSize: '0.875rem' }}>Method</Typography><Chip size="small" label={selectedLog.http_method} color="info" sx={{ fontWeight: 'bold', height: '24px' }}/></Box>
                                            <Box sx={{ display: 'flex' }}><Typography sx={{ width: '100px', color: 'text.secondary', fontSize: '0.875rem' }}>Host / IP</Typography><Typography variant="body2" sx={{ fontFamily: 'monospace' }}>{selectedLog.client_ip || 'N/A'}</Typography></Box>
                                            <Box sx={{ display: 'flex' }}><Typography sx={{ width: '100px', color: 'text.secondary', fontSize: '0.875rem' }}>Date</Typography><Typography variant="body2" sx={{ color: '#1976d2' }}>{new Date(selectedLog.created_at).toLocaleString()}</Typography></Box>
                                            <Box sx={{ display: 'flex' }}><Typography sx={{ width: '100px', color: 'text.secondary', fontSize: '0.875rem' }}>ID</Typography><Typography variant="body2">{selectedLog.id}</Typography></Box>
                                        </Box>
                                        {/* Right col headers */}
                                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                            {selectedLog.headers ? (
                                                Object.entries(JSON.parse(selectedLog.headers)).map(([key, val]) => (
                                                    <Box key={key} sx={{ display: 'flex' }}>
                                                        <Typography sx={{ width: '120px', color: 'text.secondary', fontSize: '0.875rem', overflow: 'hidden', textOverflow: 'ellipsis' }}>{key}</Typography>
                                                        <Typography variant="body2" sx={{ fontFamily: 'monospace', bgcolor: '#f5f5f5', px: 1, borderRadius: 1, flex: 1, overflowWrap: 'break-word' }}>{val as string}</Typography>
                                                    </Box>
                                                ))
                                            ) : (
                                                <Typography variant="body2" color="text.secondary">No headers recorded</Typography>
                                            )}
                                        </Box>
                                    </Box>

                                    {/* Query Strings */}
                                    <Box sx={{ mt: 4, pt: 2, borderTop: '1px solid #e0e0e0' }}>
                                        <Typography variant="subtitle2" gutterBottom>Query strings</Typography>
                                        {selectedLog.query_params && selectedLog.query_params !== "{}" ? (
                                            <Typography variant="body2" sx={{ fontFamily: 'monospace', bgcolor: '#f5f5f5', p: 1, borderRadius: 1 }}>
                                                {selectedLog.query_params}
                                            </Typography>
                                        ) : (
                                            <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>None</Typography>
                                        )}
                                    </Box>
                                </Box>

                                {/* Request Content */}
                                <Box sx={{ bgcolor: '#f5f5f5', p: 1.5, borderTop: '1px solid #e0e0e0', borderBottom: '1px solid #e0e0e0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>Request Content</Typography>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                        <FormControlLabel 
                                            control={<Checkbox size="small" checked={formatJson} onChange={e => setFormatJson(e.target.checked)} />} 
                                            label={<Typography variant="body2">Format JSON</Typography>}
                                        />
                                        <Button size="small" startIcon={<FileCopyIcon />} sx={{ textTransform: 'none' }} onClick={() => {navigator.clipboard.writeText(selectedLog.payload); toast.success('Copied!');}}>Copy</Button>
                                    </Box>
                                </Box>
                                <Box sx={{ p: 3 }}>
                                    <Box sx={{ bgcolor: '#f8f9fa', border: '1px solid #e9ecef', borderRadius: 1, p: 2, overflowX: 'auto' }}>
                                        <Typography component="pre" sx={{ m: 0, fontFamily: 'monospace', fontSize: '0.875rem', color: '#28a745', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                                            {getFormattedPayload(selectedLog.payload)}
                                        </Typography>
                                    </Box>
                                </Box>

                                {/* Destination Response */}
                                <Box sx={{ bgcolor: '#f5f5f5', p: 1.5, borderTop: '1px solid #e0e0e0', borderBottom: '1px solid #e0e0e0' }}>
                                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>Forwarding Response</Typography>
                                </Box>
                                <Box sx={{ p: 3 }}>
                                    {selectedLog.status_code ? (
                                        <Box>
                                            <Chip 
                                                label={`HTTP ${selectedLog.status_code}`} 
                                                color={selectedLog.status_code >= 200 && selectedLog.status_code < 300 ? 'success' : 'error'}
                                                size="small"
                                                sx={{ mb: 2, fontWeight: 'bold' }}
                                            />
                                            <Box sx={{ bgcolor: '#f8f9fa', border: '1px solid #e9ecef', borderRadius: 1, p: 2, overflowX: 'auto' }}>
                                                <Typography component="pre" sx={{ m: 0, fontFamily: 'monospace', fontSize: '0.875rem', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                                                    {selectedLog.response_body || 'No response body'}
                                                </Typography>
                                            </Box>
                                        </Box>
                                    ) : (
                                        <Typography variant="body2" color="text.secondary">
                                            {selectedLog.response_body || 'No response from destination.'}
                                        </Typography>
                                    )}
                                </Box>
                                
                            </Box>
                        ) : (
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyItems: 'center', height: '100%', p: 4 }}>
                                <Typography color="text.secondary">Select a request from the left panel to view details.</Typography>
                            </Box>
                        )}
                    </Box>
                </Box>
            )}

            {/* Clear Logs Confirmation Dialog */}
            <Dialog open={clearDialogOpen} onClose={() => setClearDialogOpen(false)}>
                <DialogTitle>Clear All Logs</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Are you sure you want to delete all logs for this endpoint? This action cannot be undone.
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setClearDialogOpen(false)}>Cancel</Button>
                    <Button onClick={handleClearLogs} color="error" variant="contained">Clear All</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}
