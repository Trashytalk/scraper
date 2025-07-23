import React, { createContext, useContext, useEffect, useState, useRef } from 'react';
import {
  Box,
  Typography,
  Chip,
  Alert,
  IconButton,
  Badge,
  Tooltip,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Fab,
  Zoom
} from '@mui/material';
import {
  Wifi,
  WifiOff,
  Notifications,
  NotificationsActive,
  Refresh,
  Circle,
  TrendingUp,
  TrendingDown,
  Speed,
  Error,
  CheckCircle,
  Warning,
  Info
} from '@mui/icons-material';
import { useNotifications } from './NotificationSystem';

// WebSocket Context
const WebSocketContext = createContext(null);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

// WebSocket Provider Component
export const WebSocketProvider = ({ children, url = 'ws://localhost:8000/ws' }) => {
  const [socket, setSocket] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');
  const [lastMessage, setLastMessage] = useState(null);
  const [messageHistory, setMessageHistory] = useState([]);
  const [subscriptions, setSubscriptions] = useState(new Map());
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const { showNotification } = useNotifications();

  const connect = () => {
    try {
      const ws = new WebSocket(url);
      
      ws.onopen = () => {
        setConnectionStatus('Connected');
        setSocket(ws);
        reconnectAttempts.current = 0;
        showNotification('Real-time connection established', 'success');
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setLastMessage(message);
          setMessageHistory(prev => [message, ...prev.slice(0, 99)]); // Keep last 100 messages
          
          // Handle subscriptions
          subscriptions.forEach((callback, topic) => {
            if (message.topic === topic || topic === '*') {
              callback(message);
            }
          });
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onclose = (event) => {
        setConnectionStatus('Disconnected');
        setSocket(null);
        
        if (!event.wasClean && reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000);
          
          showNotification(
            `Connection lost. Reconnecting in ${delay/1000}s... (${reconnectAttempts.current}/${maxReconnectAttempts})`,
            'warning'
          );
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else if (reconnectAttempts.current >= maxReconnectAttempts) {
          showNotification('Failed to reconnect. Please refresh the page.', 'error');
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('Error');
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionStatus('Error');
    }
  };

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (socket) {
      socket.close();
    }
  };

  const subscribe = (topic, callback) => {
    const unsubscribeId = Date.now() + Math.random();
    setSubscriptions(prev => new Map(prev.set(`${topic}_${unsubscribeId}`, callback)));
    
    return () => {
      setSubscriptions(prev => {
        const newMap = new Map(prev);
        newMap.delete(`${topic}_${unsubscribeId}`);
        return newMap;
      });
    };
  };

  const sendMessage = (message) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
      return true;
    }
    return false;
  };

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [url]);

  const value = {
    socket,
    connectionStatus,
    lastMessage,
    messageHistory,
    connect,
    disconnect,
    subscribe,
    sendMessage,
    isConnected: connectionStatus === 'Connected'
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

// Connection Status Indicator
export const ConnectionStatus = ({ showDetails = false }) => {
  const { connectionStatus, isConnected } = useWebSocket();

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'Connected': return 'success';
      case 'Connecting': return 'warning';
      case 'Disconnected': return 'default';
      case 'Error': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = () => {
    return isConnected ? <Wifi /> : <WifiOff />;
  };

  if (showDetails) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {getStatusIcon()}
        <Chip 
          label={connectionStatus}
          color={getStatusColor()}
          size="small"
          variant="outlined"
        />
      </Box>
    );
  }

  return (
    <Tooltip title={`Connection: ${connectionStatus}`}>
      <IconButton color={isConnected ? 'success' : 'error'}>
        <Badge 
          variant="dot" 
          color={getStatusColor()}
          invisible={!isConnected}
        >
          {getStatusIcon()}
        </Badge>
      </IconButton>
    </Tooltip>
  );
};

// Real-time Job Status Updates
export const RealTimeJobStatus = () => {
  const [jobUpdates, setJobUpdates] = useState([]);
  const { subscribe, isConnected } = useWebSocket();

  useEffect(() => {
    const unsubscribe = subscribe('job_status', (message) => {
      setJobUpdates(prev => [message.data, ...prev.slice(0, 9)]); // Keep last 10 updates
    });

    return unsubscribe;
  }, [subscribe]);

  if (!isConnected) {
    return (
      <Alert severity="warning" sx={{ mb: 2 }}>
        Real-time updates unavailable - connection lost
      </Alert>
    );
  }

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <NotificationsActive color="primary" />
          <Typography variant="h6">Live Job Updates</Typography>
          <Badge badgeContent={jobUpdates.length} color="primary">
            <Circle fontSize="small" />
          </Badge>
        </Box>

        {jobUpdates.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No recent updates
          </Typography>
        ) : (
          <List dense>
            {jobUpdates.map((update, index) => (
              <JobUpdateItem key={index} update={update} />
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );
};

const JobUpdateItem = ({ update }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle color="success" />;
      case 'failed': return <Error color="error" />;
      case 'running': return <Speed color="primary" />;
      case 'warning': return <Warning color="warning" />;
      default: return <Info color="info" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'running': return 'primary';
      case 'warning': return 'warning';
      default: return 'default';
    }
  };

  return (
    <>
      <ListItem>
        <ListItemIcon>
          {getStatusIcon(update.status)}
        </ListItemIcon>
        <ListItemText
          primary={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2">
                Job #{update.jobId}
              </Typography>
              <Chip 
                label={update.status} 
                size="small" 
                color={getStatusColor(update.status)}
                variant="outlined"
              />
            </Box>
          }
          secondary={
            <Box>
              <Typography variant="caption" display="block">
                {update.message}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {new Date(update.timestamp).toLocaleTimeString()}
              </Typography>
            </Box>
          }
        />
      </ListItem>
      <Divider />
    </>
  );
};

// Real-time Metrics Dashboard
export const RealTimeMetrics = () => {
  const [metrics, setMetrics] = useState({
    activeJobs: 0,
    completedToday: 0,
    errorRate: 0,
    avgResponseTime: 0,
    dataProcessed: 0
  });
  
  const { subscribe, isConnected } = useWebSocket();

  useEffect(() => {
    const unsubscribe = subscribe('metrics', (message) => {
      setMetrics(prev => ({ ...prev, ...message.data }));
    });

    return unsubscribe;
  }, [subscribe]);

  const metricCards = [
    {
      label: 'Active Jobs',
      value: metrics.activeJobs,
      icon: <Speed />,
      color: 'primary'
    },
    {
      label: 'Completed Today',
      value: metrics.completedToday,
      icon: <CheckCircle />,
      color: 'success'
    },
    {
      label: 'Error Rate',
      value: `${(metrics.errorRate * 100).toFixed(1)}%`,
      icon: <TrendingDown />,
      color: metrics.errorRate > 0.1 ? 'error' : 'success'
    },
    {
      label: 'Avg Response',
      value: `${metrics.avgResponseTime}ms`,
      icon: <TrendingUp />,
      color: 'info'
    }
  ];

  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2, mb: 2 }}>
      {metricCards.map((metric, index) => (
        <Zoom in key={index} style={{ transitionDelay: `${index * 100}ms` }}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Box sx={{ color: `${metric.color}.main`, mb: 1 }}>
                {metric.icon}
              </Box>
              <Typography variant="h4" component="div" color={`${metric.color}.main`}>
                {metric.value}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {metric.label}
              </Typography>
              {!isConnected && (
                <Box sx={{ mt: 1 }}>
                  <Chip label="Offline" size="small" color="warning" />
                </Box>
              )}
            </CardContent>
          </Card>
        </Zoom>
      ))}
    </Box>
  );
};

// Live Activity Feed
export const LiveActivityFeed = ({ maxItems = 20 }) => {
  const [activities, setActivities] = useState([]);
  const { subscribe, isConnected } = useWebSocket();

  useEffect(() => {
    const unsubscribe = subscribe('*', (message) => {
      const activity = {
        id: Date.now() + Math.random(),
        type: message.topic,
        data: message.data,
        timestamp: new Date().toISOString()
      };
      
      setActivities(prev => [activity, ...prev.slice(0, maxItems - 1)]);
    });

    return unsubscribe;
  }, [subscribe, maxItems]);

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <NotificationsActive color="primary" />
          <Typography variant="h6">Live Activity</Typography>
          <ConnectionStatus />
        </Box>

        {!isConnected && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            Activity feed is offline
          </Alert>
        )}

        <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
          {activities.length === 0 ? (
            <Typography variant="body2" color="text.secondary" textAlign="center" sx={{ py: 4 }}>
              No recent activity
            </Typography>
          ) : (
            <List dense>
              {activities.map((activity) => (
                <ActivityItem key={activity.id} activity={activity} />
              ))}
            </List>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

const ActivityItem = ({ activity }) => {
  const getActivityIcon = (type) => {
    switch (type) {
      case 'job_status': return <Speed />;
      case 'user_action': return <Info />;
      case 'system_alert': return <Warning />;
      case 'metrics': return <TrendingUp />;
      default: return <Circle />;
    }
  };

  const getActivityColor = (type) => {
    switch (type) {
      case 'job_status': return 'primary';
      case 'user_action': return 'info';
      case 'system_alert': return 'warning';
      case 'metrics': return 'success';
      default: return 'default';
    }
  };

  return (
    <>
      <ListItem>
        <ListItemIcon>
          <Box sx={{ color: `${getActivityColor(activity.type)}.main` }}>
            {getActivityIcon(activity.type)}
          </Box>
        </ListItemIcon>
        <ListItemText
          primary={
            <Typography variant="body2">
              {activity.type.replace('_', ' ').toUpperCase()}
            </Typography>
          }
          secondary={
            <Box>
              <Typography variant="caption" display="block">
                {JSON.stringify(activity.data, null, 2).slice(0, 100)}...
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {new Date(activity.timestamp).toLocaleTimeString()}
              </Typography>
            </Box>
          }
        />
      </ListItem>
      <Divider />
    </>
  );
};

// Auto-refresh Hook for non-WebSocket data
export const useAutoRefresh = (callback, interval = 5000, enabled = true) => {
  const intervalRef = useRef(null);

  useEffect(() => {
    if (enabled) {
      intervalRef.current = setInterval(callback, interval);
      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    }
  }, [callback, interval, enabled]);

  const refresh = () => {
    callback();
  };

  return { refresh };
};

// Manual Refresh Button
export const RefreshButton = ({ onRefresh, loading = false }) => {
  return (
    <Tooltip title="Refresh Data">
      <Fab
        size="small"
        onClick={onRefresh}
        disabled={loading}
        sx={{
          position: 'fixed',
          bottom: 80,
          right: 16,
          zIndex: 1000
        }}
      >
        <Refresh 
          sx={{ 
            animation: loading ? 'spin 1s linear infinite' : 'none',
            '@keyframes spin': {
              '0%': { transform: 'rotate(0deg)' },
              '100%': { transform: 'rotate(360deg)' }
            }
          }} 
        />
      </Fab>
    </Tooltip>
  );
};

export default WebSocketProvider;
