import React, { useState, useEffect, createContext, useContext } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Tabs,
  Tab,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Slider,
  Chip,
  Paper,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Card,
  CardContent,
  CardActions
} from '@mui/material';
import {
  Settings,
  ExpandMore,
  Save,
  RestoreFromTrash,
  Download,
  Upload,
  Refresh,
  Delete,
  Add,
  Edit,
  Visibility,
  Security,
  Speed,
  Cloud,
  Database,
  Network,
  Schedule,
  Notifications,
  Storage,
  Code
} from '@mui/icons-material';
import { useNotifications } from './NotificationSystem';

// Configuration Context
const ConfigContext = createContext(null);

export const useConfig = () => {
  const context = useContext(ConfigContext);
  if (!context) {
    throw new Error('useConfig must be used within a ConfigProvider');
  }
  return context;
};

// Default configuration structure
const DEFAULT_CONFIG = {
  general: {
    appName: 'Business Intelligence Scraper',
    theme: 'light',
    language: 'en',
    timezone: 'UTC',
    autoSave: true,
    debugMode: false
  },
  scraping: {
    maxConcurrentJobs: 5,
    defaultTimeout: 30,
    retryAttempts: 3,
    respectRobotsTxt: true,
    userAgent: 'BusinessIntelScraper/1.0',
    delayBetweenRequests: 1000,
    enableJavaScript: true,
    screenshotMode: 'disabled'
  },
  proxy: {
    enabled: false,
    type: 'http',
    host: '',
    port: 8080,
    username: '',
    password: '',
    rotateProxies: false,
    proxyList: []
  },
  storage: {
    outputFormat: 'json',
    compressionEnabled: true,
    backupEnabled: true,
    retentionDays: 30,
    storageLocation: 'local',
    cloudProvider: 'aws',
    bucketName: ''
  },
  notifications: {
    emailEnabled: false,
    slackEnabled: false,
    webhookEnabled: false,
    emailSettings: {
      smtpHost: '',
      smtpPort: 587,
      username: '',
      password: '',
      fromAddress: ''
    },
    slackSettings: {
      webhookUrl: '',
      channel: '#general'
    },
    webhookSettings: {
      url: '',
      method: 'POST',
      headers: {}
    }
  },
  security: {
    encryptionEnabled: true,
    apiKeyRotation: 30,
    sessionTimeout: 24,
    ipWhitelist: [],
    rateLimiting: {
      enabled: true,
      requestsPerMinute: 60,
      burstLimit: 100
    }
  },
  performance: {
    cacheEnabled: true,
    cacheTtl: 3600,
    memoryLimit: '2GB',
    diskSpaceLimit: '10GB',
    logLevel: 'info',
    metricsEnabled: true
  }
};

// Configuration Provider
export const ConfigProvider = ({ children }) => {
  const [config, setConfig] = useState(DEFAULT_CONFIG);
  const [loading, setLoading] = useState(true);
  const [configDialog, setConfigDialog] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const { showNotification } = useNotifications();

  // Load configuration on mount
  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/config');
      if (response.ok) {
        const configData = await response.json();
        setConfig({ ...DEFAULT_CONFIG, ...configData });
      } else {
        // Use default config if none exists
        setConfig(DEFAULT_CONFIG);
      }
    } catch (error) {
      console.error('Failed to load config:', error);
      setConfig(DEFAULT_CONFIG);
      showNotification('Failed to load configuration, using defaults', 'warning');
    } finally {
      setLoading(false);
    }
  };

  const saveConfig = async (newConfig = config) => {
    try {
      const response = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newConfig)
      });

      if (response.ok) {
        setConfig(newConfig);
        setHasUnsavedChanges(false);
        showNotification('Configuration saved successfully', 'success');
        return true;
      } else {
        throw new Error('Save failed');
      }
    } catch (error) {
      console.error('Failed to save config:', error);
      showNotification('Failed to save configuration', 'error');
      return false;
    }
  };

  const updateConfig = (section, key, value) => {
    setConfig(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }));
    setHasUnsavedChanges(true);
  };

  const resetConfig = () => {
    setConfig(DEFAULT_CONFIG);
    setHasUnsavedChanges(true);
    showNotification('Configuration reset to defaults', 'info');
  };

  const exportConfig = () => {
    const blob = new Blob([JSON.stringify(config, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scraper-config-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showNotification('Configuration exported', 'success');
  };

  const importConfig = (file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importedConfig = JSON.parse(e.target.result);
        setConfig({ ...DEFAULT_CONFIG, ...importedConfig });
        setHasUnsavedChanges(true);
        showNotification('Configuration imported successfully', 'success');
      } catch (error) {
        showNotification('Invalid configuration file', 'error');
      }
    };
    reader.readAsText(file);
  };

  return (
    <ConfigContext.Provider value={{
      config,
      loading,
      hasUnsavedChanges,
      updateConfig,
      saveConfig,
      resetConfig,
      exportConfig,
      importConfig,
      openConfigDialog: () => setConfigDialog(true),
      closeConfigDialog: () => setConfigDialog(false)
    }}>
      {children}
      <ConfigDialog 
        open={configDialog} 
        onClose={() => setConfigDialog(false)} 
      />
    </ConfigContext.Provider>
  );
};

// Configuration Dialog Component
const ConfigDialog = ({ open, onClose }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [tempConfig, setTempConfig] = useState({});
  const { 
    config, 
    hasUnsavedChanges, 
    updateConfig, 
    saveConfig, 
    resetConfig, 
    exportConfig, 
    importConfig 
  } = useConfig();

  useEffect(() => {
    if (open) {
      setTempConfig(config);
    }
  }, [open, config]);

  const handleSave = async () => {
    const saved = await saveConfig(tempConfig);
    if (saved) {
      onClose();
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const updateTempConfig = (section, key, value) => {
    setTempConfig(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }));
  };

  const tabs = [
    { label: 'General', icon: <Settings />, key: 'general' },
    { label: 'Scraping', icon: <Code />, key: 'scraping' },
    { label: 'Proxy', icon: <Network />, key: 'proxy' },
    { label: 'Storage', icon: <Storage />, key: 'storage' },
    { label: 'Notifications', icon: <Notifications />, key: 'notifications' },
    { label: 'Security', icon: <Security />, key: 'security' },
    { label: 'Performance', icon: <Speed />, key: 'performance' }
  ];

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: { height: '90vh' }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">
            Configuration Settings
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Export Configuration">
              <IconButton onClick={exportConfig} size="small">
                <Download />
              </IconButton>
            </Tooltip>
            <Tooltip title="Import Configuration">
              <IconButton 
                component="label" 
                size="small"
              >
                <Upload />
                <input
                  type="file"
                  accept=".json"
                  hidden
                  onChange={(e) => {
                    if (e.target.files[0]) {
                      importConfig(e.target.files[0]);
                    }
                  }}
                />
              </IconButton>
            </Tooltip>
            <Tooltip title="Reset to Defaults">
              <IconButton onClick={resetConfig} size="small">
                <RestoreFromTrash />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 0 }}>
        <Box sx={{ display: 'flex', height: '100%' }}>
          <Box sx={{ width: 200, borderRight: 1, borderColor: 'divider' }}>
            <Tabs
              orientation="vertical"
              value={activeTab}
              onChange={handleTabChange}
              sx={{ '.MuiTab-root': { minHeight: 48 } }}
            >
              {tabs.map((tab, index) => (
                <Tab
                  key={tab.key}
                  icon={tab.icon}
                  label={tab.label}
                  iconPosition="start"
                  sx={{ justifyContent: 'flex-start' }}
                />
              ))}
            </Tabs>
          </Box>

          <Box sx={{ flex: 1, p: 3, overflow: 'auto' }}>
            {activeTab === 0 && (
              <GeneralSettings 
                config={tempConfig.general || {}} 
                onChange={(key, value) => updateTempConfig('general', key, value)}
              />
            )}
            {activeTab === 1 && (
              <ScrapingSettings 
                config={tempConfig.scraping || {}} 
                onChange={(key, value) => updateTempConfig('scraping', key, value)}
              />
            )}
            {activeTab === 2 && (
              <ProxySettings 
                config={tempConfig.proxy || {}} 
                onChange={(key, value) => updateTempConfig('proxy', key, value)}
              />
            )}
            {activeTab === 3 && (
              <StorageSettings 
                config={tempConfig.storage || {}} 
                onChange={(key, value) => updateTempConfig('storage', key, value)}
              />
            )}
            {activeTab === 4 && (
              <NotificationSettings 
                config={tempConfig.notifications || {}} 
                onChange={(key, value) => updateTempConfig('notifications', key, value)}
              />
            )}
            {activeTab === 5 && (
              <SecuritySettings 
                config={tempConfig.security || {}} 
                onChange={(key, value) => updateTempConfig('security', key, value)}
              />
            )}
            {activeTab === 6 && (
              <PerformanceSettings 
                config={tempConfig.performance || {}} 
                onChange={(key, value) => updateTempConfig('performance', key, value)}
              />
            )}
          </Box>
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 3, borderTop: 1, borderColor: 'divider' }}>
        {hasUnsavedChanges && (
          <Alert severity="info" sx={{ flex: 1, mr: 2 }}>
            You have unsaved changes
          </Alert>
        )}
        <Button onClick={onClose}>
          Cancel
        </Button>
        <Button variant="contained" onClick={handleSave}>
          Save Configuration
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// Individual Settings Components
const GeneralSettings = ({ config, onChange }) => (
  <Box>
    <Typography variant="h6" gutterBottom>General Settings</Typography>
    
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Application Name"
          value={config.appName || ''}
          onChange={(e) => onChange('appName', e.target.value)}
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Theme</InputLabel>
          <Select
            value={config.theme || 'light'}
            onChange={(e) => onChange('theme', e.target.value)}
          >
            <MenuItem value="light">Light</MenuItem>
            <MenuItem value="dark">Dark</MenuItem>
            <MenuItem value="auto">Auto</MenuItem>
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Language</InputLabel>
          <Select
            value={config.language || 'en'}
            onChange={(e) => onChange('language', e.target.value)}
          >
            <MenuItem value="en">English</MenuItem>
            <MenuItem value="es">Spanish</MenuItem>
            <MenuItem value="fr">French</MenuItem>
            <MenuItem value="de">German</MenuItem>
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Timezone</InputLabel>
          <Select
            value={config.timezone || 'UTC'}
            onChange={(e) => onChange('timezone', e.target.value)}
          >
            <MenuItem value="UTC">UTC</MenuItem>
            <MenuItem value="America/New_York">Eastern Time</MenuItem>
            <MenuItem value="America/Chicago">Central Time</MenuItem>
            <MenuItem value="America/Denver">Mountain Time</MenuItem>
            <MenuItem value="America/Los_Angeles">Pacific Time</MenuItem>
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12}>
        <FormControlLabel
          control={
            <Switch
              checked={config.autoSave || false}
              onChange={(e) => onChange('autoSave', e.target.checked)}
            />
          }
          label="Enable Auto-save"
        />
      </Grid>

      <Grid item xs={12}>
        <FormControlLabel
          control={
            <Switch
              checked={config.debugMode || false}
              onChange={(e) => onChange('debugMode', e.target.checked)}
            />
          }
          label="Debug Mode"
        />
      </Grid>
    </Grid>
  </Box>
);

const ScrapingSettings = ({ config, onChange }) => (
  <Box>
    <Typography variant="h6" gutterBottom>Scraping Configuration</Typography>
    
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Typography gutterBottom>Max Concurrent Jobs: {config.maxConcurrentJobs || 5}</Typography>
        <Slider
          value={config.maxConcurrentJobs || 5}
          onChange={(e, value) => onChange('maxConcurrentJobs', value)}
          min={1}
          max={20}
          marks
          valueLabelDisplay="auto"
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Default Timeout (seconds)"
          type="number"
          value={config.defaultTimeout || 30}
          onChange={(e) => onChange('defaultTimeout', parseInt(e.target.value))}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Retry Attempts"
          type="number"
          value={config.retryAttempts || 3}
          onChange={(e) => onChange('retryAttempts', parseInt(e.target.value))}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Delay Between Requests (ms)"
          type="number"
          value={config.delayBetweenRequests || 1000}
          onChange={(e) => onChange('delayBetweenRequests', parseInt(e.target.value))}
        />
      </Grid>

      <Grid item xs={12}>
        <TextField
          fullWidth
          label="User Agent"
          value={config.userAgent || ''}
          onChange={(e) => onChange('userAgent', e.target.value)}
        />
      </Grid>

      <Grid item xs={12}>
        <FormControlLabel
          control={
            <Switch
              checked={config.respectRobotsTxt || true}
              onChange={(e) => onChange('respectRobotsTxt', e.target.checked)}
            />
          }
          label="Respect robots.txt"
        />
      </Grid>

      <Grid item xs={12}>
        <FormControlLabel
          control={
            <Switch
              checked={config.enableJavaScript || true}
              onChange={(e) => onChange('enableJavaScript', e.target.checked)}
            />
          }
          label="Enable JavaScript"
        />
      </Grid>
    </Grid>
  </Box>
);

// ... Additional setting components would follow the same pattern
const ProxySettings = ({ config, onChange }) => (
  <Box>
    <Typography variant="h6" gutterBottom>Proxy Configuration</Typography>
    <Alert severity="info" sx={{ mb: 2 }}>
      Configure proxy settings for enhanced anonymity and bypass restrictions.
    </Alert>
    {/* Proxy settings form fields would go here */}
  </Box>
);

const StorageSettings = ({ config, onChange }) => (
  <Box>
    <Typography variant="h6" gutterBottom>Storage Configuration</Typography>
    {/* Storage settings form fields would go here */}
  </Box>
);

const NotificationSettings = ({ config, onChange }) => (
  <Box>
    <Typography variant="h6" gutterBottom>Notification Settings</Typography>
    {/* Notification settings form fields would go here */}
  </Box>
);

const SecuritySettings = ({ config, onChange }) => (
  <Box>
    <Typography variant="h6" gutterBottom>Security Settings</Typography>
    {/* Security settings form fields would go here */}
  </Box>
);

const PerformanceSettings = ({ config, onChange }) => (
  <Box>
    <Typography variant="h6" gutterBottom>Performance Settings</Typography>
    {/* Performance settings form fields would go here */}
  </Box>
);

export default ConfigProvider;
