import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchApi } from '../api';
import toast from 'react-hot-toast';
import { Box, Typography, Button, Paper, Dialog, DialogTitle, DialogContent, DialogContentText, TextField, DialogActions, Divider } from '@mui/material';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import SaveIcon from '@mui/icons-material/Save';
import VpnKeyIcon from '@mui/icons-material/VpnKey';

export default function Profile() {
  const [email, setEmail] = useState('');
  const [originalEmail, setOriginalEmail] = useState('');
  const [fullName, setFullName] = useState('');
  
  const [newPassword, setNewPassword] = useState('');
  const [currentPasswordProfile, setCurrentPasswordProfile] = useState('');
  const [currentPasswordSecurity, setCurrentPasswordSecurity] = useState('');
  
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [isSavingSecurity, setIsSavingSecurity] = useState(false);
  
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const user = await fetchApi('/api/auth/me');
        setEmail(user.email);
        setOriginalEmail(user.email);
        setFullName(user.full_name || '');
      } catch (err) {
        toast.error('Failed to load profile');
      }
    };
    fetchUser();
  }, []);

  const handleSaveProfile = async () => {
    if (!currentPasswordProfile) {
      toast.error('Current Password is required to save profile changes');
      return;
    }
    setIsSavingProfile(true);
    try {
      await fetchApi('/api/auth/me', {
        method: 'PUT',
        body: JSON.stringify({ 
          email, 
          full_name: fullName, 
          current_password: currentPasswordProfile
        })
      });
      toast.success('Profile updated successfully');
      setCurrentPasswordProfile('');
      
      if (email !== originalEmail) {
        toast.success('Email changed. Please log in again.');
        localStorage.removeItem('token');
        navigate('/login');
      } else {
        setOriginalEmail(email);
      }
    } catch (err: any) {
      toast.error(err.message || 'Failed to update profile');
    } finally {
      setIsSavingProfile(false);
    }
  };

  const handleSaveSecurity = async () => {
    if (!currentPasswordSecurity || !newPassword) {
      toast.error('Both current and new passwords are required');
      return;
    }
    setIsSavingSecurity(true);
    try {
      await fetchApi('/api/auth/me', {
        method: 'PUT',
        body: JSON.stringify({ 
          new_password: newPassword,
          current_password: currentPasswordSecurity
        })
      });
      toast.success('Password changed successfully');
      setCurrentPasswordSecurity('');
      setNewPassword('');
    } catch (err: any) {
      toast.error(err.message || 'Failed to change password');
    } finally {
      setIsSavingSecurity(false);
    }
  };

  const handleDeleteOpen = () => setDeleteOpen(true);
  const handleDeleteClose = () => {
    setDeleteOpen(false);
    setDeletePassword('');
  };

  const handleConfirmDelete = async () => {
    if (!deletePassword) {
      toast.error('Password is required');
      return;
    }
    setIsDeleting(true);
    try {
      await fetchApi('/api/auth/me', {
        method: 'DELETE',
        body: JSON.stringify({ password: deletePassword })
      });
      toast.success('Account deleted successfully');
      localStorage.removeItem('token');
      navigate('/login');
    } catch (err: any) {
      toast.error(err.message || 'Failed to delete account');
      setIsDeleting(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 800, margin: '0 auto', mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Account Settings
      </Typography>
      
      {/* Profile Information Section */}
      <Paper elevation={0} sx={{ p: 4, mb: 4, border: '1px solid #e0e0e0', borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
          Profile Information
        </Typography>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
            <Box sx={{ flex: '1 1 calc(50% - 12px)' }}>
              <TextField
                label="Full Name"
                fullWidth
                variant="outlined"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </Box>
            <Box sx={{ flex: '1 1 calc(50% - 12px)' }}>
              <TextField
                label="Email Address"
                fullWidth
                variant="outlined"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </Box>
          </Box>
          <Box>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="subtitle2" color="error.main" sx={{ mb: 1 }}>
              Enter your current password to save profile changes
            </Typography>
            <TextField
              label="Current Password"
              type="password"
              fullWidth
              variant="outlined"
              value={currentPasswordProfile}
              onChange={(e) => setCurrentPasswordProfile(e.target.value)}
              required
            />
          </Box>
        </Box>
        
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<SaveIcon />}
            onClick={handleSaveProfile}
            disabled={isSavingProfile}
          >
            {isSavingProfile ? 'Saving...' : 'Save Profile'}
          </Button>
        </Box>
      </Paper>

      {/* Security Section (Change Password) */}
      <Paper elevation={0} sx={{ p: 4, mb: 4, border: '1px solid #e0e0e0', borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
          Security
        </Typography>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
            <Box sx={{ flex: '1 1 calc(50% - 12px)' }}>
              <TextField
                label="Current Password"
                type="password"
                fullWidth
                variant="outlined"
                value={currentPasswordSecurity}
                onChange={(e) => setCurrentPasswordSecurity(e.target.value)}
              />
            </Box>
            <Box sx={{ flex: '1 1 calc(50% - 12px)' }}>
              <TextField
                label="New Password"
                type="password"
                fullWidth
                variant="outlined"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />
            </Box>
          </Box>
        </Box>
        
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
          <Button 
            variant="contained" 
            color="secondary" 
            startIcon={<VpnKeyIcon />}
            onClick={handleSaveSecurity}
            disabled={isSavingSecurity}
          >
            {isSavingSecurity ? 'Changing...' : 'Change Password'}
          </Button>
        </Box>
      </Paper>

      {/* Danger Zone */}
      <Paper elevation={0} sx={{ p: 4, border: '1px solid #f8d7da', borderRadius: 2, backgroundColor: '#fff5f5' }}>
        <Typography variant="h6" color="error" gutterBottom>
          Danger Zone
        </Typography>
        <Typography variant="body2" sx={{ mb: 3 }}>
          Once you delete your account, there is no going back. Please be certain.
        </Typography>
        <Button 
          variant="outlined" 
          color="error" 
          startIcon={<DeleteForeverIcon />}
          onClick={handleDeleteOpen}
        >
          Delete Account
        </Button>
      </Paper>

      <Dialog open={deleteOpen} onClose={handleDeleteClose}>
        <DialogTitle sx={{ color: 'error.main' }}>Delete Account</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Are you sure you want to delete your account? This action is <b>irreversible</b>. 
            All your projects, endpoints, and delivery logs will be permanently deleted.
            Please enter your password to confirm.
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            label="Password"
            type="password"
            fullWidth
            variant="outlined"
            value={deletePassword}
            onChange={(e) => setDeletePassword(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteClose} disabled={isDeleting}>Cancel</Button>
          <Button onClick={handleConfirmDelete} color="error" variant="contained" disabled={isDeleting}>
            {isDeleting ? 'Deleting...' : 'Delete Account'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
