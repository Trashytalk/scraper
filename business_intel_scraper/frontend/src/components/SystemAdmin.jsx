import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Switch,
  FormControlLabel,
  Slider,
  TextField,
  Alert,
  LinearProgress,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Settings,
  Storage,
  Security,
  NetworkCheck,
  MonitorHeart,
  Warning,
  CheckCircle,
  Error,
  ExpandMore,
  Refresh,
  Save,
  RestoreFromTrash,
  Backup,
  Update
} from '@mui/icons-material';

const SystemAdmin = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [systemHealth, setSystemHealth] = useState({});
  const [services, setServices] = useState([]);
  const [configurations, setConfigurations] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSystemData();
  }, []);

  const fetchSystemData = async () => {
    setLoading(true);
    try {
      // Mock system data
      const mockHealth = {
        cpu_usage: 45.2,
        memory_usage: 78.1,
        disk_usage: 34.8,
        network_io: 1024,
        uptime: '15 days, 6 hours',
        load_average: [1.2, 1.5, 1.8],
        temperature: 52,
        status: 'healthy'
      };

      const mockServices = [
        { name: 'FastAPI Backend', status: 'running', port: 8000, uptime: '15d 6h', memory: '245 MB' },
        { name: 'Database', status: 'running', port: 5432, uptime: '15d 6h', memory: '89 MB' },
        { name: 'Redis Cache', status: 'running', port: 6379, uptime: '15d 6h', memory: '32 MB' },
        { name: 'Celery Workers', status: 'running', port: null, uptime: '15d 6h', memory: '156 MB' },
        { name: 'Nginx Proxy', status: 'running', port: 80, uptime: '15d 6h', memory: '45 MB' },
        { name: 'Monitoring', status: 'warning', port: 9090, uptime: '2d 3h', memory: '78 MB' }
      ];

      const mockConfigs = {
        scraping: {
          max_concurrent_jobs: 10,
          default_delay: 1.0,
          user_agent_rotation: true,
          proxy_enabled: false,
          respect_robots: true
        },
        database: {
          connection_pool_size: 20,
          query_timeout: 30,
          backup_enabled: true,
          backup_interval: 24
        },
        security: {
          jwt_expiration: 24,
          rate_limiting: true,
          ip_whitelist_enabled: false,
          two_factor_required: false
        },
        performance: {
          cache_enabled: true,
          cache_ttl: 3600,
          compression_enabled: true,
          logging_level: 'INFO'
        }
      };

      setSystemHealth(mockHealth);
      setServices(mockServices);
      setConfigurations(mockConfigs);
    } catch (error) {
      console.error('Failed to fetch system data:', error);
    } finally {
      setLoading(false);
    }
  };

  const TabPanel = ({ children, value, index, ...other }) => (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      case 'stopped': return 'default';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running': return <CheckCircle />;
      case 'warning': return <Warning />;
      case 'error': return <Error />;
      default: return <MonitorHeart />;
    }
  };

  const getHealthColor = (value, type) => {
    if (type === 'usage') {
      if (value > 90) return 'error';
      if (value > 70) return 'warning';
      return 'success';
    }
    return 'primary';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        System Administration
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentTab} onChange={(e, newValue) => setCurrentTab(newValue)}>
          <Tab icon={<MonitorHeart />} label="System Health" />
          <Tab icon={<Settings />} label="Services" />
          <Tab icon={<Storage />} label="Database" />
          <Tab icon={<Security />} label="Security" />
          <Tab icon={<NetworkCheck />} label="Configuration" />
        </Tabs>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* System Health Tab */}
      <TabPanel value={currentTab} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  CPU Usage
                </Typography>
                <Typography variant="h3" color={getHealthColor(systemHealth.cpu_usage, 'usage')}>
                  {systemHealth.cpu_usage}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={systemHealth.cpu_usage} 
                  color={getHealthColor(systemHealth.cpu_usage, 'usage')}
                  sx={{ mt: 1 }}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Memory Usage
                </Typography>
                <Typography variant="h3" color={getHealthColor(systemHealth.memory_usage, 'usage')}>
                  {systemHealth.memory_usage}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={systemHealth.memory_usage} 
                  color={getHealthColor(systemHealth.memory_usage, 'usage')}
                  sx={{ mt: 1 }}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Disk Usage
                </Typography>
                <Typography variant="h3" color={getHealthColor(systemHealth.disk_usage, 'usage')}>
                  {systemHealth.disk_usage}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={systemHealth.disk_usage} 
                  color={getHealthColor(systemHealth.disk_usage, 'usage')}
                  sx={{ mt: 1 }}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  System Status
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircle color="success" />
                  <Typography variant="h6" color="success.main">
                    Healthy
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Uptime: {systemHealth.uptime}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  System Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2">
                      <strong>Load Average:</strong> {systemHealth.load_average?.join(', ')}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Network I/O:</strong> {systemHealth.network_io} KB/s
                    </Typography>
                    <Typography variant="body2">
                      <strong>Temperature:</strong> {systemHealth.temperature}°C
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Alert severity="info">
                      System performance is within normal parameters. 
                      All services are running optimally.
                    </Alert>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Services Tab */}
      <TabPanel value={currentTab} index={1}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5">System Services</Typography>
          <Button startIcon={<Refresh />} onClick={fetchSystemData}>
            Refresh Status
          </Button>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Service</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Port</TableCell>
                <TableCell>Uptime</TableCell>
                <TableCell>Memory Usage</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {services.map((service, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getStatusIcon(service.status)}
                      {service.name}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={service.status}
                      color={getStatusColor(service.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{service.port || 'N/A'}</TableCell>
                  <TableCell>{service.uptime}</TableCell>
                  <TableCell>{service.memory}</TableCell>
                  <TableCell>
                    <Button size="small" sx={{ mr: 1 }}>
                      Restart
                    </Button>
                    <Button size="small" color="error">
                      Stop
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      {/* Database Tab */}
      <TabPanel value={currentTab} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Database Status
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <CheckCircle color="success" />
                  <Typography color="success.main">Connected & Healthy</Typography>
                </Box>
                <Typography variant="body2">
                  <strong>Type:</strong> SQLite
                </Typography>
                <Typography variant="body2">
                  <strong>Size:</strong> 45.2 MB
                </Typography>
                <Typography variant="body2">
                  <strong>Tables:</strong> 12
                </Typography>
                <Typography variant="body2">
                  <strong>Records:</strong> 125,430
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Database Operations
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button startIcon={<Backup />} variant="outlined" fullWidth>
                    Create Backup
                  </Button>
                  <Button startIcon={<RestoreFromTrash />} variant="outlined" fullWidth>
                    Restore from Backup
                  </Button>
                  <Button startIcon={<Update />} variant="outlined" fullWidth>
                    Run Migrations
                  </Button>
                  <Button color="warning" variant="outlined" fullWidth>
                    Optimize Database
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Backups
                </Typography>
                <List>
                  <ListItem>
                    <ListItemIcon><Backup /></ListItemIcon>
                    <ListItemText 
                      primary="Automatic Backup - July 22, 2025"
                      secondary="Size: 45.2 MB | Status: Completed"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Backup /></ListItemIcon>
                    <ListItemText 
                      primary="Manual Backup - July 21, 2025"
                      secondary="Size: 44.8 MB | Status: Completed"
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Security Tab */}
      <TabPanel value={currentTab} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Security Status
                </Typography>
                <Alert severity="success" sx={{ mb: 2 }}>
                  All security measures are active and functioning properly.
                </Alert>
                
                <List>
                  <ListItem>
                    <ListItemIcon><Security /></ListItemIcon>
                    <ListItemText 
                      primary="JWT Authentication"
                      secondary="Active - Token expiration: 24 hours"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Security /></ListItemIcon>
                    <ListItemText 
                      primary="Rate Limiting"
                      secondary="Active - 100 requests per minute"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Security /></ListItemIcon>
                    <ListItemText 
                      primary="SSL/TLS Encryption"
                      secondary="Active - Certificate valid until 2026"
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Security Configuration
                </Typography>
                
                <FormControlLabel
                  control={<Switch checked={configurations.security?.rate_limiting} />}
                  label="Rate Limiting"
                  sx={{ mb: 2, display: 'block' }}
                />
                
                <FormControlLabel
                  control={<Switch checked={configurations.security?.ip_whitelist_enabled} />}
                  label="IP Whitelist"
                  sx={{ mb: 2, display: 'block' }}
                />
                
                <FormControlLabel
                  control={<Switch checked={configurations.security?.two_factor_required} />}
                  label="Two-Factor Authentication"
                  sx={{ mb: 2, display: 'block' }}
                />

                <Typography gutterBottom>JWT Token Expiration (hours)</Typography>
                <Slider
                  value={configurations.security?.jwt_expiration || 24}
                  min={1}
                  max={168}
                  marks={[
                    { value: 1, label: '1h' },
                    { value: 24, label: '24h' },
                    { value: 168, label: '7d' }
                  ]}
                  valueLabelDisplay="auto"
                />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Configuration Tab */}
      <TabPanel value={currentTab} index={4}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5">System Configuration</Typography>
          <Button startIcon={<Save />} variant="contained">
            Save Changes
          </Button>
        </Box>

        {Object.entries(configurations).map(([category, settings]) => (
          <Accordion key={category} sx={{ mb: 2 }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>
                {category} Configuration
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                {Object.entries(settings).map(([key, value]) => (
                  <Grid item xs={12} md={6} key={key}>
                    {typeof value === 'boolean' ? (
                      <FormControlLabel
                        control={<Switch checked={value} />}
                        label={key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      />
                    ) : typeof value === 'number' ? (
                      <TextField
                        fullWidth
                        label={key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        type="number"
                        value={value}
                        size="small"
                      />
                    ) : (
                      <TextField
                        fullWidth
                        label={key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        value={value}
                        size="small"
                      />
                    )}
                  </Grid>
                ))}
              </Grid>
            </AccordionDetails>
          </Accordion>
        ))}
      </TabPanel>
    </Box>
  );
};

export default SystemAdmin;
