import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Typography,
  Box,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton,
  FormControlLabel,
  Checkbox,
  Divider
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Person,
  Email,
  Lock,
  Login,
  PersonAdd,
  Google,
  GitHub
} from '@mui/icons-material';
import { useNotifications } from './NotificationSystem';
import { authService } from '../services/api';

// Auth Context
const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authDialog, setAuthDialog] = useState(false);
  const { showNotification } = useNotifications();

  // Check for existing auth on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        if (authService.isAuthenticated()) {
          const userData = await authService.getCurrentUser();
          setUser(userData);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        authService.logout();
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email, password, rememberMe = false) => {
    try {
      // For demo, use email as username if it contains @, otherwise use as username
      const username = email.includes('@') ? email.split('@')[0] : email;
      const result = await authService.login(username, password);
      
      setUser(result.user);
      setAuthDialog(false);
      showNotification('Login successful!', 'success');
      return { success: true };
    } catch (error) {
      console.error('Login failed:', error);
      return { success: false, error: error.message || 'Login failed' };
    }
  };

  const register = async (username, email, password) => {
    try {
      // For demo purposes, registration is not implemented in backend yet
      showNotification('Registration not available in demo. Use admin/admin123 to login.', 'info');
      return { success: false, error: 'Registration not available in demo' };
    } catch (error) {
      return { success: false, error: 'Network error occurred' };
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    showNotification('Logged out successfully', 'info');
  };

  const openAuthDialog = () => setAuthDialog(true);
  const closeAuthDialog = () => setAuthDialog(false);

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      register,
      logout,
      openAuthDialog,
      closeAuthDialog,
      isAuthenticated: !!user
    }}>
      {children}
      <AuthDialog open={authDialog} onClose={closeAuthDialog} />
    </AuthContext.Provider>
  );
};

// Auth Dialog Component
const AuthDialog = ({ open, onClose }) => {
  const [tab, setTab] = useState(0); // 0 = login, 1 = register
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const { login, register } = useAuth();
  const { showNotification } = useNotifications();

  const handleTabChange = (event, newValue) => {
    setTab(newValue);
    setErrors({});
    setFormData({
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    });
  };

  const handleInputChange = (field) => (event) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (tab === 1 && !formData.username.trim()) {
      newErrors.username = 'Username is required';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    if (tab === 1 && formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    
    try {
      let result;
      if (tab === 0) {
        // Login
        result = await login(formData.email, formData.password, rememberMe);
      } else {
        // Register
        result = await register(formData.username, formData.email, formData.password);
      }

      if (!result.success) {
        setErrors({ submit: result.error });
      }
    } catch (error) {
      setErrors({ submit: 'An unexpected error occurred' });
    } finally {
      setLoading(false);
    }
  };

  const handleSocialLogin = (provider) => {
    showNotification(`${provider} login integration coming soon!`, 'info');
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="sm" 
      fullWidth
      PaperProps={{
        sx: { borderRadius: 2 }
      }}
    >
      <DialogTitle>
        <Box sx={{ textAlign: 'center', pb: 1 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Welcome
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Sign in to access your scraper dashboard
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ px: 3 }}>
        <Tabs 
          value={tab} 
          onChange={handleTabChange} 
          variant="fullWidth"
          sx={{ mb: 3, borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab 
            icon={<Login />} 
            label="Sign In" 
            iconPosition="start"
          />
          <Tab 
            icon={<PersonAdd />} 
            label="Sign Up" 
            iconPosition="start"
          />
        </Tabs>

        {errors.submit && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {errors.submit}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit}>
          {tab === 1 && (
            <TextField
              fullWidth
              label="Username"
              value={formData.username}
              onChange={handleInputChange('username')}
              error={!!errors.username}
              helperText={errors.username}
              margin="normal"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Person />
                  </InputAdornment>
                )
              }}
            />
          )}

          <TextField
            fullWidth
            label="Email"
            type="email"
            value={formData.email}
            onChange={handleInputChange('email')}
            error={!!errors.email}
            helperText={errors.email}
            margin="normal"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Email />
                </InputAdornment>
              )
            }}
          />

          <TextField
            fullWidth
            label="Password"
            type={showPassword ? 'text' : 'password'}
            value={formData.password}
            onChange={handleInputChange('password')}
            error={!!errors.password}
            helperText={errors.password}
            margin="normal"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Lock />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => setShowPassword(!showPassword)}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              )
            }}
          />

          {tab === 1 && (
            <TextField
              fullWidth
              label="Confirm Password"
              type={showPassword ? 'text' : 'password'}
              value={formData.confirmPassword}
              onChange={handleInputChange('confirmPassword')}
              error={!!errors.confirmPassword}
              helperText={errors.confirmPassword}
              margin="normal"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock />
                  </InputAdornment>
                )
              }}
            />
          )}

          {tab === 0 && (
            <FormControlLabel
              control={
                <Checkbox
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
              }
              label="Remember me"
              sx={{ mt: 1 }}
            />
          )}
        </Box>

        <Divider sx={{ my: 3 }}>
          <Typography variant="body2" color="text.secondary">
            OR
          </Typography>
        </Divider>

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            fullWidth
            variant="outlined"
            startIcon={<Google />}
            onClick={() => handleSocialLogin('Google')}
            sx={{ textTransform: 'none' }}
          >
            Google
          </Button>
          <Button
            fullWidth
            variant="outlined"
            startIcon={<GitHub />}
            onClick={() => handleSocialLogin('GitHub')}
            sx={{ textTransform: 'none' }}
          >
            GitHub
          </Button>
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 1 }}>
        <Button 
          onClick={onClose}
          disabled={loading}
        >
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : null}
          sx={{ minWidth: 120 }}
        >
          {loading ? 'Processing...' : (tab === 0 ? 'Sign In' : 'Sign Up')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// Auth Guard Component
export const AuthGuard = ({ children, fallback = null }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh' 
      }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return fallback;
  }

  return children;
};

// User Profile Component
export const UserProfile = () => {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
      <Typography variant="body2">
        Welcome, {user.username || user.email}
      </Typography>
      <Button
        size="small"
        onClick={logout}
        variant="outlined"
      >
        Logout
      </Button>
    </Box>
  );
};

export default AuthProvider;
