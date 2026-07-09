import os

file_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/LiveLogs.tsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update imports
content = content.replace(
    "import { Typography, Box, FormControl, InputLabel, Select, MenuItem, Chip, Checkbox, FormControlLabel, Button, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions } from '@mui/material';",
    "import { Typography, Box, FormControl, InputLabel, Select, MenuItem, Chip, Checkbox, FormControlLabel, Button, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, Pagination } from '@mui/material';"
)

# 2. Add pagination and sorting state
state_declarations = """
    const [selectedLogId, setSelectedLogId] = useState<number | null>(null);
    const [clearDialogOpen, setClearDialogOpen] = useState(false);
    
    // Pagination & Sorting State
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalLogs, setTotalLogs] = useState(0);
    const [sortBy, setSortBy] = useState('desc');
    const limit = 20;
"""
content = content.replace(
    """    const [selectedLogId, setSelectedLogId] = useState<number | null>(null);
    const [clearDialogOpen, setClearDialogOpen] = useState(false);""",
    state_declarations
)

# 3. Update loadLogs
new_load_logs = """
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
        if (selectedEndpointId) {
            loadLogs(selectedEndpointId, 1, sortBy);
        } else {
            setLogs([]);
            setTotalPages(1);
            setTotalLogs(0);
        }
    }, [selectedEndpointId]);
"""

# Replace existing loadLogs and its useEffect
import re
content = re.sub(
    r"    const loadLogs = async.*?    }, \[selectedEndpointId\]\);",
    new_load_logs.strip(),
    content,
    flags=re.DOTALL
)

# 4. Handle pagination and sort changes
handlers = """
    const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
        if (selectedEndpointId) {
            loadLogs(selectedEndpointId, value, sortBy);
        }
    };

    const handleSortChange = (event: any) => {
        const newSort = event.target.value;
        setSortBy(newSort);
        if (selectedEndpointId) {
            loadLogs(selectedEndpointId, 1, newSort); // Reset to page 1 on sort change
        }
    };
"""
content = content.replace(
    "    const handleResendLog = async",
    handlers + "\n    const handleResendLog = async"
)

# 5. Handle WebSocket updates correctly
new_ws_logic = """
                try {
                    const newLog = JSON.parse(event.data);
                    newLog.is_read = false;
                    
                    // If we are on the first page and sorting by newest, we can just prepend
                    // Otherwise, we might just want to reload or increment total
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
"""
content = content.replace(
    """                try {
                    const newLog = JSON.parse(event.data);
                    // newly arrived logs are unread by default unless it matches the selected log?
                    newLog.is_read = false;
                    setLogs(prev => [newLog, ...prev]);
                } catch (e) {""",
    new_ws_logic
)

# 6. Update the UI for Pagination and Sorting
ui_updates = """
                    {/* LEFT SIDEBAR: Log List */}
                    <Box sx={{ width: '320px', borderRight: '1px solid #e0e0e0', display: 'flex', flexDirection: 'column', bgcolor: '#f9f9f9' }}>
                        <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0', bgcolor: '#fff', display: 'flex', flexDirection: 'column', gap: 1 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Typography variant="subtitle2" color="text.secondary">INBOX ({totalLogs})</Typography>
                                <Box sx={{ display: 'flex', gap: 1 }}>
                                    {logs.some(l => !l.is_read) && (
                                        <Button size="small" onClick={handleMarkAllRead} startIcon={<ChecklistIcon />}>Read All</Button>
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
                                    No logs available.
                                </Typography>
                            ) : (
                                logs.map(log => (
"""

content = content.replace(
    """                    {/* LEFT SIDEBAR: Log List */}
                    <Box sx={{ width: '300px', borderRight: '1px solid #e0e0e0', overflowY: 'auto', bgcolor: '#f9f9f9' }}>
                        <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0', bgcolor: '#fff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="subtitle2" color="text.secondary">INBOX ({logs.length})</Typography>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                                {logs.some(l => !l.is_read) && (
                                    <Button size="small" onClick={handleMarkAllRead} startIcon={<ChecklistIcon />}>Mark Read</Button>
                                )}
                                {!isViewer && logs.length > 0 && (
                                    <Button size="small" color="error" onClick={() => setClearDialogOpen(true)}>Clear</Button>
                                )}
                            </Box>
                        </Box>
                        {logs.length === 0 ? (
                            <Typography color="text.secondary" sx={{ p: 3, fontStyle: 'italic', textAlign: 'center' }}>
                                No logs available.
                            </Typography>
                        ) : (
                            logs.map(log => (""",
    ui_updates
)

pagination_ui = """
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
"""

content = content.replace(
    """                                </Box>
                            ))
                        )}
                    </Box>""",
    pagination_ui
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated LiveLogs.tsx successfully!")
