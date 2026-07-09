import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { fetchApi } from '../api';
import toast from 'react-hot-toast';
import { Container, Box, Typography, TextField, Button, Paper, Link, Alert } from '@mui/material';

export default function ForgotPassword() {
    const [email, setEmail] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);

    useEffect(() => {
        document.title = "Forgot Password - Webhook Forwarder";
    }, []);

    const handleForgotPassword = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            await fetchApi('/api/auth/forgot-password', {
                method: 'POST',
                body: JSON.stringify({ email })
            });
            setIsSuccess(true);
            toast.success('Password reset link sent!');
        } catch (err: any) {
            toast.error(err.message || 'Failed to request password reset');
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
                        Forgot Password
                    </Typography>
                    {isSuccess ? (
                        <Box sx={{ width: '100%' }}>
                            <Alert severity="success" sx={{ mb: 3 }}>
                                If an account exists with that email address, a password reset link has been sent. Please check your inbox.
                            </Alert>
                            <Button component={RouterLink} to="/login" fullWidth variant="contained">
                                Back to Login
                            </Button>
                        </Box>
                    ) : (
                        <Box component="form" onSubmit={handleForgotPassword} sx={{ mt: 1, width: '100%' }}>
                            <Typography variant="body2" sx={{ mb: 2 }}>
                                Enter your email address below and we'll send you a link to reset your password.
                            </Typography>
                            <TextField
                                margin="normal"
                                required
                                fullWidth
                                label="Email Address"
                                type="email"
                                value={email}
                                onChange={e => setEmail(e.target.value)}
                                autoFocus
                            />
                            <Button
                                type="submit"
                                fullWidth
                                variant="contained"
                                disabled={isLoading}
                                sx={{ mt: 3, mb: 2, py: 1.2 }}
                            >
                                {isLoading ? 'Sending Link...' : 'Send Reset Link'}
                            </Button>
                            <Box sx={{ textAlign: 'center' }}>
                                <Link component={RouterLink} to="/login" variant="body2">
                                    {"Remember your password? Sign In"}
                                </Link>
                            </Box>
                        </Box>
                    )}
                </Box>
            </Paper>
        </Container>
    );
}
