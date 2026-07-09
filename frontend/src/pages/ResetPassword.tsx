import React, { useState, useEffect } from 'react';
import { useSearchParams, Link as RouterLink } from 'react-router-dom';
import { fetchApi } from '../api';
import toast from 'react-hot-toast';
import { Container, Box, Typography, TextField, Button, Paper, Alert } from '@mui/material';

export default function ResetPassword() {
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token') || '';
    const email = searchParams.get('email') || '';

    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);
    const [errorMsg, setErrorMsg] = useState('');

    useEffect(() => {
        document.title = "Reset Password - Webhook Forwarder";
        if (!token || !email) {
            setErrorMsg('Invalid or missing password reset link parameter.');
        }
    }, [token, email]);

    const handleResetPassword = async (e: React.FormEvent) => {
        e.preventDefault();
        if (password !== confirmPassword) {
            toast.error('Passwords do not match');
            return;
        }
        setIsLoading(true);
        try {
            await fetchApi('/api/auth/reset-password', {
                method: 'POST',
                body: JSON.stringify({ email, token, new_password: password })
            });
            setIsSuccess(true);
            toast.success('Password reset successfully!');
        } catch (err: any) {
            toast.error(err.message || 'Failed to reset password');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Container component="main" maxWidth="xs" sx={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Paper elevation={3} sx={{ p: 4, width: '100%', borderRadius: 2 }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <Typography component="h1" variant="h5" sx={{ fontWeight: 600 }} color="primary" gutterBottom>
                        Webhook Forwarder
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        Reset Password
                    </Typography>

                    {errorMsg && (
                        <Box sx={{ width: '100%' }}>
                            <Alert severity="error" sx={{ mb: 3 }}>
                                {errorMsg}
                            </Alert>
                            <Button component={RouterLink} to="/login" fullWidth variant="contained">
                                Back to Login
                            </Button>
                        </Box>
                    )}

                    {!errorMsg && isSuccess && (
                        <Box sx={{ width: '100%' }}>
                            <Alert severity="success" sx={{ mb: 3 }}>
                                Your password has been successfully reset. You can now log in with your new password.
                            </Alert>
                            <Button component={RouterLink} to="/login" fullWidth variant="contained">
                                Go to Login
                            </Button>
                        </Box>
                    )}

                    {!errorMsg && !isSuccess && (
                        <Box component="form" onSubmit={handleResetPassword} sx={{ mt: 1, width: '100%' }}>
                            <Typography variant="body2" sx={{ mb: 2 }}>
                                Please enter your new password below.
                            </Typography>
                            <TextField
                                margin="normal"
                                required
                                fullWidth
                                label="New Password"
                                type="password"
                                value={password}
                                onChange={e => setPassword(e.target.value)}
                                autoFocus
                            />
                            <TextField
                                margin="normal"
                                required
                                fullWidth
                                label="Confirm New Password"
                                type="password"
                                value={confirmPassword}
                                onChange={e => setConfirmPassword(e.target.value)}
                            />
                            <Button
                                type="submit"
                                fullWidth
                                variant="contained"
                                disabled={isLoading}
                                sx={{ mt: 3, mb: 2, py: 1.2 }}
                            >
                                {isLoading ? 'Resetting Password...' : 'Reset Password'}
                            </Button>
                        </Box>
                    )}
                </Box>
            </Paper>
        </Container>
    );
}
