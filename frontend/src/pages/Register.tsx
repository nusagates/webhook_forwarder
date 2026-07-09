import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { fetchApi } from '../api';
import toast from 'react-hot-toast';
import { Container, Box, Typography, TextField, Button, Paper, Link, LinearProgress } from '@mui/material';

export default function Register() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    const calculateStrength = (pwd: string) => {
        if (!pwd) return 0;
        let score = 0;
        if (pwd.length >= 8) score += 25;
        if (/[a-z]/.test(pwd)) score += 25;
        if (/[A-Z]/.test(pwd)) score += 25;
        if (/[0-9!@#$%^&*]/.test(pwd)) score += 25;
        return score;
    };

    const strength = calculateStrength(password);
    const strengthColor = strength < 50 ? 'error' : strength < 75 ? 'warning' : 'success';
    const strengthLabel = strength === 0 ? '' : strength < 50 ? 'Weak' : strength < 75 ? 'Fair' : strength < 100 ? 'Good' : 'Strong';

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        if (password.length < 8) {
            toast.error('Password must be at least 8 characters long');
            return;
        }
        setIsLoading(true);
        try {
            await fetchApi('/api/auth/register', {
                method: 'POST',
                body: JSON.stringify({ email, password })
            });
            toast.success('Registration successful! Redirecting...');
            setTimeout(() => navigate('/login'), 2000);
        } catch (err: any) {
            toast.error(err.message || 'Registration failed');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Container component="main" maxWidth="xs" sx={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Paper elevation={3} sx={{ p: 4, width: '100%', borderRadius: 2 }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <Typography component="h1" variant="h5" sx={{ fontWeight: 600 }} color="primary" gutterBottom>
                        Create Account
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        Join Webhook Forwarder today
                    </Typography>
                    <Box component="form" onSubmit={handleRegister} sx={{ mt: 1, width: '100%' }}>
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
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            label="Password"
                            type="password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                        />
                        {password && (
                            <Box sx={{ width: '100%', mt: 1, mb: 1 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                    <Typography variant="caption" color="text.secondary">Password Strength</Typography>
                                    <Typography variant="caption" color={`${strengthColor}.main`}>{strengthLabel}</Typography>
                                </Box>
                                <LinearProgress variant="determinate" value={strength} color={strengthColor as any} />
                            </Box>
                        )}
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            disabled={isLoading}
                            sx={{ mt: 3, mb: 2, py: 1.2 }}
                        >
                            {isLoading ? 'Registering...' : 'Sign Up'}
                        </Button>
                        <Box sx={{ textAlign: 'center' }}>
                            <Link component={RouterLink} to="/login" variant="body2">
                                {"Already have an account? Sign In"}
                            </Link>
                        </Box>
                    </Box>
                </Box>
            </Paper>
        </Container>
    );
}
