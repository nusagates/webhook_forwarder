import { Box, Typography, Paper, Button } from '@mui/material';
import BlockIcon from '@mui/icons-material/Block';


export default function Blocked() {
    const reason = localStorage.getItem('block_reason') || 'No specific reason was provided.';

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('block_reason');
        window.location.href = '/login';
    };

    return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
            <Paper sx={{ p: 5, maxWidth: 500, textAlign: 'center', borderRadius: 3 }}>
                <BlockIcon color="error" sx={{ fontSize: 80, mb: 2 }} />
                <Typography variant="h4" color="error" sx={{ fontWeight: "bold" }} gutterBottom>
                    Account Suspended
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                    Your access to Webhook Forwarder has been blocked by an administrator.
                </Typography>
                <Box sx={{ my: 4, p: 3, backgroundColor: 'rgba(211, 47, 47, 0.05)', borderLeft: '4px solid #d32f2f', textAlign: 'left' }}>
                    <Typography variant="subtitle2" color="text.secondary" sx={{ textTransform: "uppercase", fontWeight: "bold" }} gutterBottom>
                        Reason for Suspension
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 500 }}>
                        "{reason}"
                    </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    If you believe this is a mistake, please contact your system administrator.
                </Typography>
                <Button variant="outlined" color="primary" onClick={handleLogout} sx={{ mt: 2 }}>
                    Return to Login
                </Button>
            </Paper>
        </Box>
    );
}
