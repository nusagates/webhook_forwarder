import React, { useEffect, useState, useRef } from 'react';
import { fetchApi } from '../api';
import toast from 'react-hot-toast';
import { Typography, Box, FormControl, InputLabel, Select, MenuItem, Chip, Checkbox, FormControlLabel, Button } from '@mui/material';
import FileCopyIcon from '@mui/icons-material/FileCopy';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import ClearIcon from '@mui/icons-material/Clear';

interface DeliveryLog { 
    id: number;
    status_code: number | null;
    http_method: string;
    client_ip: string | null;
    headers: string | null;
    query_params: string | null;
    payload: string;
    response_body: string | null;
    created_at: string;
}
interface Endpoint { id: number; name: string; slug: string; project_id: string; }
interface Project { id: string; name: string; }

export default function LiveLogs() {
    const [projects, setProjects] = useState<Project[]>([]);
    const [selectedProjectId, setSelectedProjectId] = useState<string>('');
    const [endpoints, setEndpoints] = useState<Endpoint[]>([]);
    const [selectedEndpointId, setSelectedEndpointId] = useState<string>('');
    const [logs, setLogs] = useState<DeliveryLog[]>([]);
    const [selectedLogId, setSelectedLogId] = useState<number | null>(null);
    const [formatJson, setFormatJson] = useState(true);
    
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => { loadProjects(); }, []);
    
    useEffect(() => {
        if (selectedProjectId) loadEndpoints(selectedProjectId);
        else { setEndpoints([]); setSelectedEndpointId(''); }
    }, [selectedProjectId]);

    useEffect(() => {
        if (!selectedEndpointId) {
            setLogs([]);
            if (wsRef.current) wsRef.current.close();
            return;
        }
        
        fetchApi(`/api/logs?endpoint_id=${selectedEndpointId}`)
            .then(data => {
                setLogs(data);
                if (data.length > 0) setSelectedLogId(data[0].id);
            })
            .catch(() => toast.error('Failed to load history logs'));

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/api/ws/logs/${selectedEndpointId}`;
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => toast.success('Connected to Live Stream');
        ws.onmessage = (event) => {
            const newLog = JSON.parse(event.data);
            newLog.created_at = new Date().toISOString(); 
            setLogs(prev => {
                // Deduplicate by ID to prevent double hits from StrictMode or race conditions
                if (prev.some(l => l.id === newLog.id)) return prev;
                return [newLog, ...prev];
            });
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

    const loadProjects = async () => {
        try { setProjects(await fetchApi('/api/projects')); }
        catch (err) { console.error(err); }
    };

    const loadEndpoints = async (projId: string) => {
        try { setEndpoints(await fetchApi(`/api/endpoints?project_id=${projId}`)); }
        catch (err) { console.error(err); }
    };

    const selectedLog = logs.find(l => l.id === selectedLogId) || logs[0];

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
                    <Box sx={{ width: '300px', borderRight: '1px solid #e0e0e0', overflowY: 'auto', bgcolor: '#f9f9f9' }}>
                        <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0', bgcolor: '#fff' }}>
                            <Typography variant="subtitle2" color="text.secondary">INBOX ({logs.length}) Newest First</Typography>
                        </Box>
                        {logs.length === 0 ? (
                            <Typography color="text.secondary" sx={{ p: 3, fontStyle: 'italic', textAlign: 'center' }}>
                                Waiting for webhooks...
                            </Typography>
                        ) : (
                            logs.map(log => (
                                <Box 
                                    key={log.id} 
                                    onClick={() => setSelectedLogId(log.id)}
                                    sx={{ 
                                        p: 2, 
                                        borderBottom: '1px solid #e0e0e0', 
                                        cursor: 'pointer',
                                        position: 'relative',
                                        bgcolor: selectedLogId === log.id ? '#3582c4' : 'transparent',
                                        color: selectedLogId === log.id ? '#fff' : 'inherit',
                                        '&:hover': { bgcolor: selectedLogId === log.id ? '#3582c4' : '#f1f1f1' },
                                        '& .delete-btn': { display: 'none' },
                                        '&:hover .delete-btn': { display: 'flex' }
                                    }}
                                >
                                    <Box sx={{ display: 'flex', gap: 1, mb: 1, alignItems: 'center' }}>
                                        <Chip 
                                            label={log.http_method} 
                                            size="small" 
                                            sx={{ 
                                                bgcolor: selectedLogId === log.id ? 'rgba(255,255,255,0.2)' : '#5bc0de',
                                                color: '#fff',
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
                                </Box>
                            ))
                        )}
                    </Box>

                    {/* RIGHT MAIN PANEL: Log Details */}
                    <Box sx={{ flex: 1, overflowY: 'auto', bgcolor: '#fff', p: 0 }}>
                        {selectedLog ? (
                            <Box>
                                {/* Request Details Header */}
                                <Box sx={{ bgcolor: '#f5f5f5', p: 1.5, borderBottom: '1px solid #e0e0e0', display: 'flex', alignItems: 'center' }}>
                                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 1 }}>
                                        Request Details & Headers
                                    </Typography>
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
        </Box>
    );
}
