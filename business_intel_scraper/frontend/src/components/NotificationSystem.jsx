import React, { useState, useEffect, createContext, useContext } from 'react';
import {
  Snackbar,
  Alert,
  AlertTitle,
  Slide,
  Stack,
  IconButton,
  Typography,
  Box
} from '@mui/material';
import {
  Close as CloseIcon,
  CheckCircle,
  Error,
  Warning,
  Info,
  Notifications as NotificationsIcon
} from '@mui/icons-material';

// Notification Context
const NotificationContext = createContext();

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

// Notification types
export const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
};

// Slide transition component
const SlideTransition = (props) => {
  return <Slide {...props} direction="left" />;
};

// Individual notification component
const NotificationItem = ({ notification, onClose }) => {
  const getIcon = (type) => {
    switch (type) {
      case NOTIFICATION_TYPES.SUCCESS:
        return <CheckCircle />;
      case NOTIFICATION_TYPES.ERROR:
        return <Error />;
      case NOTIFICATION_TYPES.WARNING:
        return <Warning />;
      case NOTIFICATION_TYPES.INFO:
        return <Info />;
      default:
        return <Info />;
    }
  };

  return (
    <Snackbar
      open={true}
      autoHideDuration={notification.autoHide ? notification.duration || 6000 : null}
      onClose={() => onClose(notification.id)}
      TransitionComponent={SlideTransition}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      sx={{
        position: 'relative',
        '& .MuiSnackbar-root': {
          position: 'relative',
          transform: 'none',
          left: 'auto',
          right: 'auto',
          top: 'auto',
          bottom: 'auto'
        }
      }}
    >
      <Alert
        severity={notification.type}
        onClose={() => onClose(notification.id)}
        variant="filled"
        icon={getIcon(notification.type)}
        sx={{
          minWidth: 300,
          maxWidth: 500,
          '& .MuiAlert-message': {
            width: '100%'
          }
        }}
        action={
          notification.actions ? (
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              {notification.actions.map((action, index) => (
                <IconButton
                  key={index}
                  size="small"
                  color="inherit"
                  onClick={() => {
                    action.onClick();
                    onClose(notification.id);
                  }}
                >
                  {action.icon}
                </IconButton>
              ))}
            </Box>
          ) : null
        }
      >
        {notification.title && <AlertTitle>{notification.title}</AlertTitle>}
        <Typography variant="body2">{notification.message}</Typography>
        {notification.details && (
          <Typography variant="caption" sx={{ mt: 1, display: 'block', opacity: 0.8 }}>
            {notification.details}
          </Typography>
        )}
      </Alert>
    </Snackbar>
  );
};

// Notification container
const NotificationContainer = ({ notifications, onClose }) => {
  return (
    <Box
      sx={{
        position: 'fixed',
        top: 80,
        right: 16,
        zIndex: 9999,
        display: 'flex',
        flexDirection: 'column',
        gap: 1,
        maxHeight: 'calc(100vh - 100px)',
        overflow: 'hidden'
      }}
    >
      <Stack spacing={1}>
        {notifications.slice(0, 5).map((notification) => (
          <NotificationItem
            key={notification.id}
            notification={notification}
            onClose={onClose}
          />
        ))}
        {notifications.length > 5 && (
          <Alert severity="info" variant="outlined">
            <Typography variant="caption">
              +{notifications.length - 5} more notifications
            </Typography>
          </Alert>
        )}
      </Stack>
    </Box>
  );
};

// Notification Provider Component
export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);

  // Add notification
  const addNotification = (notification) => {
    const id = Date.now() + Math.random();
    const newNotification = {
      id,
      type: NOTIFICATION_TYPES.INFO,
      autoHide: true,
      duration: 6000,
      ...notification
    };

    setNotifications(prev => [newNotification, ...prev]);

    // Auto-remove if autoHide is enabled
    if (newNotification.autoHide) {
      setTimeout(() => {
        removeNotification(id);
      }, newNotification.duration);
    }

    return id;
  };

  // Remove notification
  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  // Clear all notifications
  const clearAllNotifications = () => {
    setNotifications([]);
  };

  // Convenience methods
  const showSuccess = (message, options = {}) => {
    return addNotification({
      type: NOTIFICATION_TYPES.SUCCESS,
      message,
      ...options
    });
  };

  const showError = (message, options = {}) => {
    return addNotification({
      type: NOTIFICATION_TYPES.ERROR,
      message,
      autoHide: false, // Errors should be manually dismissed
      ...options
    });
  };

  const showWarning = (message, options = {}) => {
    return addNotification({
      type: NOTIFICATION_TYPES.WARNING,
      message,
      duration: 8000, // Warnings stay longer
      ...options
    });
  };

  const showInfo = (message, options = {}) => {
    return addNotification({
      type: NOTIFICATION_TYPES.INFO,
      message,
      ...options
    });
  };

  // Job-specific notifications
  const showJobNotification = (jobName, status, details = '') => {
    const statusConfig = {
      started: {
        type: NOTIFICATION_TYPES.INFO,
        title: 'Job Started',
        message: `${jobName} has begun processing`,
        details
      },
      completed: {
        type: NOTIFICATION_TYPES.SUCCESS,
        title: 'Job Completed',
        message: `${jobName} finished successfully`,
        details
      },
      failed: {
        type: NOTIFICATION_TYPES.ERROR,
        title: 'Job Failed',
        message: `${jobName} encountered an error`,
        details,
        autoHide: false
      },
      cancelled: {
        type: NOTIFICATION_TYPES.WARNING,
        title: 'Job Cancelled',
        message: `${jobName} was cancelled by user`,
        details
      }
    };

    const config = statusConfig[status] || statusConfig.info;
    return addNotification(config);
  };

  // System notifications
  const showSystemNotification = (type, message, details = '') => {
    const typeConfig = {
      maintenance: {
        type: NOTIFICATION_TYPES.WARNING,
        title: 'System Maintenance',
        autoHide: false
      },
      update: {
        type: NOTIFICATION_TYPES.INFO,
        title: 'System Update'
      },
      alert: {
        type: NOTIFICATION_TYPES.ERROR,
        title: 'System Alert',
        autoHide: false
      }
    };

    const config = typeConfig[type] || { type: NOTIFICATION_TYPES.INFO };
    return addNotification({
      ...config,
      message,
      details
    });
  };

  const contextValue = {
    notifications,
    addNotification,
    removeNotification,
    clearAllNotifications,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showJobNotification,
    showSystemNotification
  };

  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
      <NotificationContainer
        notifications={notifications}
        onClose={removeNotification}
      />
    </NotificationContext.Provider>
  );
};

// Hook for job-related notifications
export const useJobNotifications = () => {
  const { showJobNotification, showError, showSuccess } = useNotifications();

  return {
    notifyJobStarted: (jobName, details) => 
      showJobNotification(jobName, 'started', details),
    notifyJobCompleted: (jobName, details) => 
      showJobNotification(jobName, 'completed', details),
    notifyJobFailed: (jobName, error) => 
      showJobNotification(jobName, 'failed', error),
    notifyJobCancelled: (jobName, reason) => 
      showJobNotification(jobName, 'cancelled', reason),
    notifyJobError: (message) => 
      showError(message, { title: 'Job Error' }),
    notifyJobSuccess: (message) => 
      showSuccess(message, { title: 'Job Success' })
  };
};

export default NotificationProvider;
