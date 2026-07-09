import { useEffect, useState, useCallback } from 'react';
import {
    Box, Typography, Accordion, AccordionSummary, AccordionDetails,
    Chip, Table, TableHead, TableRow, TableCell, TableBody, TableContainer,
    Paper, CircularProgress, Alert, Divider, Tooltip,
    TextField, InputAdornment, TablePagination, Button
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import FolderIcon from '@mui/icons-material/Folder';
import LinkIcon from '@mui/icons-material/Link';
import SendIcon from '@mui/icons-material/Send';
import HistoryIcon from '@mui/icons-material/History';
import PersonIcon from '@mui/icons-material/Person';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import SearchIcon from '@mui/icons-material/Search';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import RefreshIcon from '@mui/icons-material/Refresh';
import PauseIcon from '@mui/icons-material/Pause';
import { useConfirm } from '../components/ConfirmDialog';
import { fetchApi } from '../api';
import toast from 'react-hot-toast';

interface RecentLog {
    id: number;
    status_code: number;
    created_at: string;
    client_ip: string;
}

interface Destination {
    id: number;
    url: string;
    is_active: boolean;
    auth_type: string;
}

interface Endpoint {
    id: number;
    name: string;
    slug: string;
    destinations: Destination[];
    log_count: number;
}

interface Project {
    id: string;
    name: string;
    description: string;
    owner_email: string;
    owner_id: number;
    is_suspended: boolean;
    endpoints: Endpoint[];
}

export default function AdminProjects() {
    const confirm = useConfirm();
    const [projects, setProjects] = useState<Project[]>([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [search, setSearch] = useState('');
    const [searchInput, setSearchInput] = useState('');

    // Dynamic logs loading state
    const [endpointLogs, setEndpointLogs] = useState<Record<number, RecentLog[]>>({});
    const [loadingLogs, setLoadingLogs] = useState<Record<number, boolean>>({});

    const fetchProjects = useCallback(async () => {
        setLoading(true);
        setError('');
        try {
            const params = new URLSearchParams({
                page: String(page + 1),
                limit: String(rowsPerPage),
                search,
            });
            const data = await fetchApi(`/api/admin/projects?${params}`);
            setProjects(data.items);
            setTotal(data.total);
        } catch (e: any) {
            setError(e.message || 'Failed to load projects');
        } finally {
            setLoading(false);
        }
    }, [page, rowsPerPage, search]);

    useEffect(() => {
        document.title = 'All Projects - Admin';
    }, []);

    useEffect(() => {
        fetchProjects();
    }, [fetchProjects]);

    // Debounce search
    useEffect(() => {
        const t = setTimeout(() => {
            setPage(0);
            setSearch(searchInput);
        }, 400);
        return () => clearTimeout(t);
    }, [searchInput]);

    const handleToggleSuspend = async (e: React.MouseEvent, project: Project) => {
        e.stopPropagation();
        const action = project.is_suspended ? 'unsuspend' : 'suspend';
        const msg = `Are you sure you want to ${action} project "${project.name}"? ${action === 'suspend' ? 'This will reject all incoming webhooks for this project.' : ''}`;

        if (!await confirm({ message: msg, isDanger: action === 'suspend' })) return;

        try {
            await fetchApi(`/api/admin/projects/${project.id}/${action}`, { method: 'POST' });
            toast.success(`Project successfully ${action}ed`);
            fetchProjects();
        } catch (err: any) {
            toast.error(err.message || `Failed to ${action} project`);
        }
    };

    const loadLogs = async (endpointId: number) => {
        setLoadingLogs(prev => ({ ...prev, [endpointId]: true }));
        try {
            const logs = await fetchApi(`/api/admin/endpoints/${endpointId}/logs`);
            setEndpointLogs(prev => ({ ...prev, [endpointId]: logs }));
        } catch (e: any) {
            toast.error(e.message || 'Failed to load logs');
        } finally {
            setLoadingLogs(prev => ({ ...prev, [endpointId]: false }));
        }
    };

    const statusColor = (code: number): 'success' | 'error' | 'warning' | 'default' => {
        if (code >= 200 && code < 300) return 'success';
        if (code >= 400) return 'error';
        return 'warning';
    };

    return (
        <Box sx={{ maxWidth: 1100, mx: 'auto' }}>
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Box>
                    <Typography variant="h4" sx={{ fontWeight: 700 }}>All Projects</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                        Admin view — {total} total projects
                    </Typography>
                </Box>
                <Chip label="Admin Only" color="error" size="small" />
            </Box>

            {/* Search bar */}
            <TextField
                fullWidth
                size="small"
                placeholder="Search by project name..."
                value={searchInput}
                onChange={e => setSearchInput(e.target.value)}
                sx={{ mb: 3 }}
                slotProps={{
                    input: {
                        startAdornment: (
                            <InputAdornment position="start">
                                <SearchIcon fontSize="small" />
                            </InputAdornment>
                        )
                    }
                }}
            />

            {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}>
                    <CircularProgress />
                </Box>
            ) : projects.length === 0 ? (
                <Alert severity="info">No projects found{search ? ` matching "${search}"` : ''}.</Alert>
            ) : (
                <>
                    {projects.map(project => (
                        <Accordion
                            key={project.id}
                            sx={{
                                mb: 2,
                                border: project.is_suspended ? '1px solid #ef5350' : '1px solid #e0e0e0',
                                '&:before': { display: 'none' },
                                borderRadius: '8px !important',
                                overflow: 'hidden',
                                opacity: project.is_suspended ? 0.85 : 1
                            }}
                            elevation={0}
                        >
                            <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ py: 1 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%', pr: 2, flexWrap: 'wrap' }}>
                                    <FolderIcon color={project.is_suspended ? 'disabled' : 'primary'} />
                                    <Box sx={{ flexGrow: 1 }}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                                            <Typography variant="subtitle1" sx={{ fontWeight: 700, textDecoration: project.is_suspended ? 'line-through' : 'none' }}>
                                                {project.name}
                                            </Typography>
                                            {project.is_suspended && (
                                                <Chip label="SUSPENDED" color="error" size="small" sx={{ fontWeight: 'bold', height: 20 }} />
                                            )}
                                        </Box>
                                        {project.description && (
                                            <Typography variant="caption" color="text.secondary">{project.description}</Typography>
                                        )}
                                    </Box>
                                    <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center', flexWrap: 'wrap' }}>
                                        {/* Suspend / Unsuspend action button */}
                                        <Button
                                            size="small"
                                            variant="outlined"
                                            color={project.is_suspended ? 'success' : 'error'}
                                            startIcon={project.is_suspended ? <PlayArrowIcon /> : <PauseIcon />}
                                            onClick={(e) => handleToggleSuspend(e, project)}
                                        >
                                            {project.is_suspended ? 'Unsuspend' : 'Suspend'}
                                        </Button>

                                        <Chip icon={<PersonIcon />} label={project.owner_email} size="small" variant="outlined" />
                                        <Chip icon={<LinkIcon />} label={`${project.endpoints.length} endpoints`} size="small" color="primary" variant="outlined" />
                                        <Chip
                                            icon={<HistoryIcon />}
                                            label={`${project.endpoints.reduce((s, e) => s + e.log_count, 0)} logs`}
                                            size="small"
                                            variant="outlined"
                                        />
                                    </Box>
                                </Box>
                            </AccordionSummary>

                            <AccordionDetails sx={{ p: 0 }}>
                                <Divider />
                                {project.endpoints.length === 0 ? (
                                    <Box sx={{ p: 3 }}>
                                        <Typography color="text.secondary" variant="body2">No endpoints in this project.</Typography>
                                    </Box>
                                ) : (
                                    project.endpoints.map((ep, epIdx) => {
                                        const logs = endpointLogs[ep.id];
                                        const isLogLoading = loadingLogs[ep.id];

                                        return (
                                            <Box key={ep.id} sx={{ borderTop: epIdx > 0 ? '1px solid #f0f0f0' : 'none' }}>
                                                {/* Endpoint header */}
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, px: 3, py: 2, bgcolor: '#fafafa' }}>
                                                    <LinkIcon fontSize="small" color="action" />
                                                    <Box sx={{ flexGrow: 1 }}>
                                                        <Typography variant="body1" sx={{ fontWeight: 600 }}>{ep.name}</Typography>
                                                        <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                                                            /webhook/{ep.slug}
                                                        </Typography>
                                                    </Box>
                                                    <Chip icon={<SendIcon />} label={`${ep.destinations.length} dest`} size="small" />
                                                    <Chip icon={<HistoryIcon />} label={`${ep.log_count} logs`} size="small" />
                                                </Box>

                                                {/* Destinations table */}
                                                {ep.destinations.length > 0 && (
                                                    <Box sx={{ px: 3, pb: 1, pt: 1.5 }}>
                                                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1 }}>
                                                            Destinations
                                                        </Typography>
                                                        <TableContainer component={Paper} variant="outlined" sx={{ mt: 1, mb: 2 }}>
                                                            <Table size="small">
                                                                <TableHead>
                                                                    <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                                                                        <TableCell sx={{ fontWeight: 600 }}>URL</TableCell>
                                                                        <TableCell sx={{ fontWeight: 600 }}>Auth</TableCell>
                                                                        <TableCell sx={{ fontWeight: 600 }}>Active</TableCell>
                                                                    </TableRow>
                                                                </TableHead>
                                                                <TableBody>
                                                                    {ep.destinations.map(d => (
                                                                        <TableRow key={d.id} hover>
                                                                            <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.78rem', maxWidth: 400, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                                                <Tooltip title={d.url} arrow>
                                                                                    <span>{d.url}</span>
                                                                                </Tooltip>
                                                                            </TableCell>
                                                                            <TableCell>
                                                                                <Chip label={d.auth_type || 'none'} size="small" variant="outlined" />
                                                                            </TableCell>
                                                                            <TableCell>
                                                                                {d.is_active
                                                                                    ? <CheckCircleIcon fontSize="small" color="success" />
                                                                                    : <CancelIcon fontSize="small" color="disabled" />}
                                                                            </TableCell>
                                                                        </TableRow>
                                                                    ))}
                                                                </TableBody>
                                                            </Table>
                                                        </TableContainer>
                                                    </Box>
                                                )}

                                                {/* Dynamic Logs section */}
                                                <Box sx={{ px: 3, pb: 2, pt: 1 }}>
                                                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1 }}>
                                                                Recent Logs
                                                            </Typography>
                                                            <Button
                                                                size="small"
                                                                startIcon={isLogLoading ? <CircularProgress size={12} /> : <RefreshIcon sx={{ fontSize: 12 }} />}
                                                                onClick={() => loadLogs(ep.id)}
                                                                disabled={isLogLoading}
                                                                sx={{ height: 20, fontSize: '0.65rem', py: 0 }}
                                                            >
                                                                {logs ? 'Refresh Logs' : 'Load Logs'}
                                                            </Button>
                                                        </Box>
                                                        {logs && logs.length > 0 && (
                                                            <Button
                                                                size="small"
                                                                color="inherit"
                                                                onClick={() => setEndpointLogs(prev => {
                                                                    const copy = { ...prev };
                                                                    delete copy[ep.id];
                                                                    return copy;
                                                                })}
                                                                sx={{ height: 20, fontSize: '0.65rem', py: 0 }}
                                                            >
                                                                Hide
                                                            </Button>
                                                        )}
                                                    </Box>

                                                    {isLogLoading && !logs && (
                                                        <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                                                            <CircularProgress size={20} />
                                                        </Box>
                                                    )}

                                                    {logs && logs.length === 0 && (
                                                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                                                            No logs found for this endpoint.
                                                        </Typography>
                                                    )}

                                                    {logs && logs.length > 0 && (
                                                        <TableContainer component={Paper} variant="outlined" sx={{ mt: 1 }}>
                                                            <Table size="small">
                                                                <TableHead>
                                                                    <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                                                                        <TableCell sx={{ fontWeight: 600 }}>Time</TableCell>
                                                                        <TableCell sx={{ fontWeight: 600 }}>Source IP</TableCell>
                                                                        <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                                                                    </TableRow>
                                                                </TableHead>
                                                                <TableBody>
                                                                    {logs.map(log => (
                                                                        <TableRow key={log.id} hover>
                                                                            <TableCell sx={{ fontSize: '0.78rem' }}>
                                                                                {new Date(log.created_at).toLocaleString()}
                                                                            </TableCell>
                                                                            <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.78rem' }}>
                                                                                {log.client_ip || '—'}
                                                                            </TableCell>
                                                                            <TableCell>
                                                                                <Chip
                                                                                    label={log.status_code}
                                                                                    size="small"
                                                                                    color={statusColor(log.status_code)}
                                                                                    variant="outlined"
                                                                                />
                                                                            </TableCell>
                                                                        </TableRow>
                                                                    ))}
                                                                </TableBody>
                                                            </Table>
                                                        </TableContainer>
                                                    )}
                                                </Box>
                                            </Box>
                                        );
                                    })
                                )}
                            </AccordionDetails>
                        </Accordion>
                    ))}

                    {/* Pagination */}
                    <Paper variant="outlined" sx={{ mt: 2 }}>
                        <TablePagination
                            component="div"
                            count={total}
                            page={page}
                            onPageChange={(_, newPage) => setPage(newPage)}
                            rowsPerPage={rowsPerPage}
                            onRowsPerPageChange={e => {
                                setRowsPerPage(parseInt(e.target.value, 10));
                                setPage(0);
                            }}
                            rowsPerPageOptions={[5, 10, 25, 50]}
                            labelRowsPerPage="Projects per page:"
                        />
                    </Paper>
                </>
            )}
        </Box>
    );
}
