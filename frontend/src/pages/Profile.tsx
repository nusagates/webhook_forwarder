import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchApi } from '../api';
import toast from 'react-hot-toast';
import { Box, Typography, Button, Paper, Dialog, DialogTitle, DialogContent, DialogContentText, TextField, DialogActions, Divider } from '@mui/material';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import SaveIcon from '@mui/icons-material/Save';

export default function Profile() {
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  
  const [newPassword, setNewPassword] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  
  const [isSaving, setIsSaving] = useState(false);
  
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const user = await fetchApi('/api/auth/me');
        setEmail(user.email);
        setFullName(user.full_name || '');
      } catch (err) {
        toast.error('Failed to load profile');
      }
    };
    fetchUser();
  }, []);

  const handleSaveProfile = async () => {
    if (!currentPassword) {
      toast.error('Current Password is required to save changes');
      return;
    }
    setIsSaving(true);
    try {
      await fetchApi('/api/auth/me', {
        method: 'PUT',
        body: JSON.stringify({ 
          email, 
          full_name: fullName, 
          new_password: newPassword || null,
          current_password: currentPassword
        })
      });
      toast.success('Profile updated successfully');
      setCurrentPassword('');
      setNewPassword('');
    } catch (err: any) {
      toast.error(err.message || 'Failed to update profile');
    } finally {
      setIsSaving(false);
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
        Account Profile
      </Typography>
      
      <Paper elevation={0} sx={{ p: 4, mb: 4, border: '1px solid #e0e0e0', borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
          Edit Profile Information
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
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
              Change Password (Leave blank to keep current)
            </Typography>
            <TextField
              label="New Password"
              type="password"
              fullWidth
              variant="outlined"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />
          </Box>
          <Box>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="subtitle2" color="error.main" sx={{ mb: 1 }}>
              Required to save any changes
            </Typography>
            <TextField
              label="Current Password"
              type="password"
              fullWidth
              variant="outlined"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
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
            disabled={isSaving}
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </Button>
        </Box>
      </Paper>

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
