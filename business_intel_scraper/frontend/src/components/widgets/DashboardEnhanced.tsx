import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Box, 
  Grid, 
  Paper, 
  Typography, 
  Card, 
  CardContent, 
  CardActions,
  Button,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Slider,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  Switch,
  FormControlLabel,
  Divider
} from '@mui/material';
import {
  Refresh,
  FilterList,
  Search,
  Download,
  Settings,
  Notifications,
  PlayArrow,
  Pause,
  Clear
} from '@mui/icons-material';

// Lazy load visualization components
const NetworkGraph = React.lazy(() => import('./NetworkGraph'));
const Timeline = React.lazy(() => import('./TimelineSimple'));
const GeospatialMap = React.lazy(() => import('./GeospatialMap'));

interface FilterState {
  entityType: string;
  dateRange: { start: string; end: string } | null;
  searchTerm: string;
  confidenceThreshold: number;
}

interface DashboardEnhancedProps {
  className?: string;
}

const DashboardEnhanced = ({ className }: DashboardEnhancedProps) => {
  // State management
  const [activeTab, setActiveTab] = useState(0);
  const [filters, setFilters] = useState<FilterState>({
    entityType: '',
    dateRange: null,
    searchTerm: '',
    confidenceThreshold: 0.5
  });
  const [isRealTimeEnabled, setIsRealTimeEnabled] = useState(false);
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null);
  const [notifications, setNotifications] = useState<Array<{
    id: string;
    message: string;
    type: 'info' | 'warning' | 'error' | 'success';
    timestamp: string;
  }>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // WebSocket connection management
  const connectWebSocket = useCallback(() => {
    if (wsConnection?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      addNotification('Connected to real-time updates', 'success');
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket message:', data);
        
        // Add notification for updates
        addNotification(
          `Real-time update: ${data.data?.message || 'New data available'}`,
          data.data?.priority === 'high' ? 'warning' : 'info'
        );
        
        // Trigger data refresh if needed
        if (data.type && isRealTimeEnabled) {
          // You can add logic here to refresh specific components
          handleRefreshData();
        }
      } catch (e) {
        console.error('Error parsing WebSocket message:', e);
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      addNotification('Disconnected from real-time updates', 'warning');
      setWsConnection(null);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      addNotification('WebSocket connection error', 'error');
    };
    
    setWsConnection(ws);
  }, [wsConnection, isRealTimeEnabled]);

  const disconnectWebSocket = useCallback(() => {
    if (wsConnection) {
      wsConnection.close();
      setWsConnection(null);
    }
  }, [wsConnection]);

  // Real-time toggle handler
  const handleRealTimeToggle = (enabled: boolean) => {
    setIsRealTimeEnabled(enabled);
    if (enabled) {
      connectWebSocket();
    } else {
      disconnectWebSocket();
    }
  };

  // Notification management
  const addNotification = (message: string, type: 'info' | 'warning' | 'error' | 'success') => {
    const notification = {
      id: `notification_${Date.now()}`,
      message,
      type,
      timestamp: new Date().toISOString()
    };
    
    setNotifications(prev => [notification, ...prev.slice(0, 4)]); // Keep last 5
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
    }, 5000);
  };

  // Data refresh handler
  const handleRefreshData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Simulate API refresh - in real implementation, you'd trigger component refresh
      await new Promise(resolve => setTimeout(resolve, 1000));
      addNotification('Data refreshed successfully', 'success');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to refresh data';
      setError(errorMessage);
      addNotification(errorMessage, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // Export functionality
  const handleExportData = async (dataType: string, format: string) => {
    try {
      setIsLoading(true);
      const response = await fetch(`/api/export/${dataType}?format=${format}`);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `${dataType}_data.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        addNotification(`${dataType} data exported as ${format}`, 'success');
      } else {
        throw new Error('Export failed');
      }
    } catch (err) {
      addNotification(`Export failed: ${err}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // Filter handlers
  const handleFilterChange = (key: keyof FilterState, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      entityType: '',
      dateRange: null,
      searchTerm: '',
      confidenceThreshold: 0.5
    });
  };

  const hasActiveFilters = useMemo(() => {
    return filters.entityType || 
           filters.searchTerm || 
           filters.dateRange || 
           filters.confidenceThreshold > 0.5;
  }, [filters]);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      disconnectWebSocket();
    };
  }, [disconnectWebSocket]);

  const renderControlPanel = () => (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Dashboard Controls</Typography>
        <Box display="flex" gap={1} alignItems="center">
          <FormControlLabel
            control={
              <Switch
                checked={isRealTimeEnabled}
                onChange={(e) => handleRealTimeToggle(e.target.checked)}
                color="primary"
              />
            }
            label="Real-time Updates"
          />
          <Tooltip title="Refresh Data">
            <IconButton onClick={handleRefreshData} disabled={isLoading}>
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Divider sx={{ mb: 2 }} />

      {/* Filter Controls */}
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel>Entity Type</InputLabel>
            <Select
              value={filters.entityType}
              onChange={(e) => handleFilterChange('entityType', e.target.value)}
              label="Entity Type"
            >
              <MenuItem value="">All Types</MenuItem>
              <MenuItem value="person">Person</MenuItem>
              <MenuItem value="organization">Organization</MenuItem>
              <MenuItem value="location">Location</MenuItem>
              <MenuItem value="event">Event</MenuItem>
              <MenuItem value="document">Document</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={3}>
          <TextField
            fullWidth
            size="small"
            label="Search"
            value={filters.searchTerm}
            onChange={(e) => handleFilterChange('searchTerm', e.target.value)}
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
            }}
          />
        </Grid>

        <Grid item xs={12} md={3}>
          <Box px={1}>
            <Typography variant="body2" gutterBottom>
              Confidence Threshold: {(filters.confidenceThreshold * 100).toFixed(0)}%
            </Typography>
            <Slider
              value={filters.confidenceThreshold}
              onChange={(_, value) => handleFilterChange('confidenceThreshold', value)}
              min={0}
              max={1}
              step={0.1}
              size="small"
            />
          </Box>
        </Grid>

        <Grid item xs={12} md={2}>
          <Box display="flex" gap={1}>
            {hasActiveFilters && (
              <Button
                size="small"
                startIcon={<Clear />}
                onClick={clearFilters}
                variant="outlined"
              >
                Clear
              </Button>
            )}
            <Button
              size="small"
              startIcon={<FilterList />}
              variant="contained"
              onClick={() => addNotification('Filters applied', 'info')}
            >
              Apply
            </Button>
          </Box>
        </Grid>

        <Grid item xs={12} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel>Export</InputLabel>
            <Select
              defaultValue=""
              label="Export"
              onChange={(e) => {
                const [dataType, format] = e.target.value.split('.');
                if (dataType && format) {
                  handleExportData(dataType, format);
                }
              }}
            >
              <MenuItem value="network.json">Network (JSON)</MenuItem>
              <MenuItem value="network.csv">Network (CSV)</MenuItem>
              <MenuItem value="timeline.json">Timeline (JSON)</MenuItem>
              <MenuItem value="timeline.csv">Timeline (CSV)</MenuItem>
              <MenuItem value="geospatial.json">Geospatial (JSON)</MenuItem>
              <MenuItem value="geospatial.csv">Geospatial (CSV)</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      {/* Active Filters Display */}
      {hasActiveFilters && (
        <Box mt={2}>
          <Typography variant="body2" gutterBottom>Active Filters:</Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            {filters.entityType && (
              <Chip 
                label={`Type: ${filters.entityType}`} 
                size="small" 
                onDelete={() => handleFilterChange('entityType', '')}
              />
            )}
            {filters.searchTerm && (
              <Chip 
                label={`Search: ${filters.searchTerm}`} 
                size="small" 
                onDelete={() => handleFilterChange('searchTerm', '')}
              />
            )}
            {filters.confidenceThreshold > 0.5 && (
              <Chip 
                label={`Confidence: >${(filters.confidenceThreshold * 100).toFixed(0)}%`} 
                size="small" 
                onDelete={() => handleFilterChange('confidenceThreshold', 0.5)}
              />
            )}
          </Box>
        </Box>
      )}
    </Paper>
  );

  const renderNotifications = () => {
    if (notifications.length === 0) return null;

    return (
      <Box mb={2}>
        {notifications.map((notification) => (
          <Alert 
            key={notification.id}
            severity={notification.type}
            sx={{ mb: 1 }}
            onClose={() => setNotifications(prev => 
              prev.filter(n => n.id !== notification.id)
            )}
          >
            <Typography variant="body2">{notification.message}</Typography>
            <Typography variant="caption" color="text.secondary">
              {new Date(notification.timestamp).toLocaleTimeString()}
            </Typography>
          </Alert>
        ))}
      </Box>
    );
  };

  return (
    <Box className={className} sx={{ p: 2 }}>
      {/* Control Panel */}
      {renderControlPanel()}

      {/* Notifications */}
      {renderNotifications()}

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Main Dashboard Content */}
      <Grid container spacing={3}>
        {/* Network Visualization */}
        <Grid item xs={12} lg={6}>
          <Card sx={{ height: 500 }}>
            <CardContent sx={{ height: '100%', p: 1 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="h6">Network Graph</Typography>
                <Box>
                  <Tooltip title="Export Network Data">
                    <IconButton 
                      size="small"
                      onClick={() => handleExportData('network', 'json')}
                    >
                      <Download />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
              <React.Suspense fallback={<Box display="flex" justifyContent="center" alignItems="center" height="100%">Loading...</Box>}>
                <NetworkGraph height={430} filters={filters} />
              </React.Suspense>
            </CardContent>
          </Card>
        </Grid>

        {/* Timeline Visualization */}
        <Grid item xs={12} lg={6}>
          <Card sx={{ height: 500 }}>
            <CardContent sx={{ height: '100%', p: 1 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="h6">Timeline</Typography>
                <Box>
                  <Tooltip title="Export Timeline Data">
                    <IconButton 
                      size="small"
                      onClick={() => handleExportData('timeline', 'json')}
                    >
                      <Download />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
              <React.Suspense fallback={<Box display="flex" justifyContent="center" alignItems="center" height="100%">Loading...</Box>}>
                <Timeline height={430} filters={filters} />
              </React.Suspense>
            </CardContent>
          </Card>
        </Grid>

        {/* Geospatial Map */}
        <Grid item xs={12}>
          <Card sx={{ height: 400 }}>
            <CardContent sx={{ height: '100%', p: 1 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="h6">Geospatial Map</Typography>
                <Box>
                  <Tooltip title="Export Geospatial Data">
                    <IconButton 
                      size="small"
                      onClick={() => handleExportData('geospatial', 'json')}
                    >
                      <Download />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
              <React.Suspense fallback={<Box display="flex" justifyContent="center" alignItems="center" height="100%">Loading...</Box>}>
                <GeospatialMap height={350} filters={filters} />
              </React.Suspense>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Connection Status */}
      <Box 
        position="fixed" 
        bottom={16} 
        right={16} 
        zIndex={1000}
      >
        <Chip
          label={wsConnection?.readyState === WebSocket.OPEN ? 'Connected' : 'Disconnected'}
          color={wsConnection?.readyState === WebSocket.OPEN ? 'success' : 'default'}
          size="small"
          icon={wsConnection?.readyState === WebSocket.OPEN ? <PlayArrow /> : <Pause />}
        />
      </Box>
    </Box>
  );
};

export default DashboardEnhanced;
