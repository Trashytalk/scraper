import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { 
  CssBaseline, 
  Container, 
  Typography, 
  Box, 
  Switch, 
  FormControlLabel, 
  Card, 
  CardContent, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText,
  Tabs,
  Tab,
  AppBar,
  Toolbar,
  IconButton,
  Button
} from '@mui/material';
import { 
  CheckCircle, 
  Storage, 
  Api, 
  Security, 
  Dashboard as DashboardIcon,
  Store as StoreIcon,
  Settings as SettingsIcon,
  Menu as MenuIcon,
  Work as JobIcon,
  DataObject as DataIcon,
  SecurityOutlined as OSINTIcon,
  AdminPanelSettings as AdminIcon,
  Login as LoginIcon,
  Analytics as AnalyticsIcon,
  Build as BuildIcon,
  Description as DescriptionIcon,
  Group as GroupIcon
} from '@mui/icons-material';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import SpiderMarketplace from './components/SpiderMarketplace';
import JobManager from './components/JobManager';
import DataProcessor from './components/DataProcessor';
import OSINTCenter from './components/OSINTCenter';
import SystemAdmin from './components/SystemAdmin';
import { JobProvider } from './contexts/JobContext';
import { NotificationProvider } from './components/NotificationSystem';
import { AuthProvider, useAuth, UserProfile, AuthGuard } from './components/AuthSystem';
import { ConfigProvider, useConfig } from './components/ConfigurationManager';
import { MobileNavigation, useMobileLayout } from './components/MobileLayout';
import { WebSocketProvider, ConnectionStatus, RealTimeMetrics } from './components/RealTimeUpdates';
import { AdvancedAnalyticsDashboard } from './components/AdvancedVisualization';
import { WorkflowBuilder } from './components/WorkflowBuilder';
import { APIDocumentation } from './components/APIDocumentation';
import { TeamCollaboration } from './components/TeamCollaboration';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 0 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

// Main App Component
function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [systemStatus, setSystemStatus] = useState({
    frontend: { status: 'Running', port: '5174' },
    backend: { status: 'Unknown', port: '8000' },
    database: { status: 'Unknown' }
  });

  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: '#2196f3',
      },
      secondary: {
        main: '#ff9800',
      },
    },
  });

  useEffect(() => {
    // Check backend status
    const checkBackendStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/');
        if (response.ok) {
          const data = await response.json();
          setSystemStatus(prev => ({
            ...prev,
            backend: { status: 'Running', port: '8000' },
            database: { status: 'Connected', type: data.database_url?.includes('sqlite') ? 'SQLite' : 'PostgreSQL' }
          }));
        }
      } catch (error) {
        setSystemStatus(prev => ({
          ...prev,
          backend: { status: 'Offline', port: '8000' },
          database: { status: 'Disconnected' }
        }));
      }
    };

    checkBackendStatus();
  }, []);

  return (
    <NotificationProvider>
      <AuthProvider>
        <ConfigProvider>
          <WebSocketProvider>
            <JobProvider>
              <ThemeProvider theme={theme}>
                <CssBaseline />
                <MainApp 
                  darkMode={darkMode} 
                  setDarkMode={setDarkMode}
                  systemStatus={systemStatus}
                />
              </ThemeProvider>
            </JobProvider>
          </WebSocketProvider>
        </ConfigProvider>
      </AuthProvider>
    </NotificationProvider>
  );
}

// Main App Component with Authentication
function MainApp({ darkMode, setDarkMode, systemStatus }) {
  const { isAuthenticated, openAuthDialog } = useAuth();
  const { openConfigDialog } = useConfig();
  const { isMobile } = useMobileLayout();
  const [currentTab, setCurrentTab] = useState(0);

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
    { id: 'jobs', label: 'Job Manager', icon: <JobIcon /> },
    { id: 'marketplace', label: 'Spider Marketplace', icon: <StoreIcon /> },
    { id: 'data', label: 'Data Processor', icon: <DataIcon /> },
    { id: 'osint', label: 'OSINT Center', icon: <OSINTIcon /> },
    { id: 'admin', label: 'System Admin', icon: <AdminIcon /> },
    { id: 'settings', label: 'Settings', icon: <SettingsIcon /> },
    { id: 'advanced-analytics', label: 'Advanced Analytics', icon: <AnalyticsIcon /> },
    { id: 'workflow-builder', label: 'Workflow Builder', icon: <BuildIcon /> },
    { id: 'api-docs', label: 'API Documentation', icon: <DescriptionIcon /> },
    { id: 'team-collaboration', label: 'Team Collaboration', icon: <GroupIcon /> }
  ];

  const handleNavigation = (pageId) => {
    const pageIndex = navigationItems.findIndex(item => item.id === pageId);
    if (pageIndex !== -1) {
      setCurrentTab(pageIndex);
    }
  };

  const renderTabContent = () => {
    switch (currentTab) {
      case 0: return <DashboardWithMetrics />;
      case 1: return <JobManager />;
      case 2: return <SpiderMarketplace />;
      case 3: return <DataProcessor />;
      case 4: return <OSINTCenter />;
      case 5: return <SystemAdmin />;
      case 6: return <ConfigurationPanel />;
      case 7: return <AdvancedAnalyticsDashboard />;
      case 8: return <WorkflowBuilder />;
      case 9: return <APIDocumentation />;
      case 10: return <TeamCollaboration />;
      default: return <DashboardWithMetrics />;
    }
  };

  return (
    <MobileNavigation
      navigationItems={navigationItems}
      onNavigate={handleNavigation}
      currentPage={navigationItems[currentTab]?.id}
    >
      {!isMobile && (
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Business Intelligence Scraper Platform
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <ConnectionStatus showDetails />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={darkMode}
                    onChange={(e) => setDarkMode(e.target.checked)}
                    color="secondary"
                  />
                }
                label="Dark Mode"
              />

              {isAuthenticated ? (
                <UserProfile />
              ) : (
                <Button 
                  color="inherit" 
                  startIcon={<LoginIcon />}
                  onClick={openAuthDialog}
                >
                  Sign In
                </Button>
              )}
              
              <IconButton color="inherit" onClick={openConfigDialog}>
                <SettingsIcon />
              </IconButton>
            </Box>
          </Toolbar>
        </AppBar>
      )}

      <AuthGuard fallback={<UnauthenticatedView />}>
        {!isMobile && (
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs 
              value={currentTab} 
              onChange={(e, newValue) => setCurrentTab(newValue)}
              aria-label="platform tabs"
              variant="scrollable"
              scrollButtons="auto"
            >
              {navigationItems.map((item, index) => (
                <Tab 
                  key={item.id}
                  icon={item.icon} 
                  label={item.label} 
                  iconPosition="start"
                />
              ))}
            </Tabs>
          </Box>
        )}

        <Container maxWidth="xl" sx={{ mt: 2, mb: 4 }}>
          <RealTimeMetrics />
          {renderTabContent()}
        </Container>
      </AuthGuard>
    </MobileNavigation>
  );
}

// Dashboard with Real-time Metrics
function DashboardWithMetrics() {
  return (
    <Box>
      <AnalyticsDashboard />
    </Box>
  );
}

// Configuration Panel
function ConfigurationPanel() {
  const { openConfigDialog } = useConfig();
  
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Configuration Settings
      </Typography>
      <Typography variant="body1" paragraph>
        Manage your scraper configuration, proxy settings, notifications, and more.
      </Typography>
      <Button variant="contained" onClick={openConfigDialog} size="large">
        Open Configuration Manager
      </Button>
    </Box>
  );
}

// Unauthenticated View
function UnauthenticatedView() {
  const { openAuthDialog } = useAuth();
  
  return (
    <Container maxWidth="md" sx={{ mt: 8, textAlign: 'center' }}>
      <Typography variant="h3" gutterBottom>
        Business Intelligence Scraper
      </Typography>
      <Typography variant="h6" color="text.secondary" paragraph>
        A comprehensive platform for web scraping, data collection, and OSINT operations
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Please sign in to access the platform and manage your scraping jobs
      </Typography>
      <Button 
        variant="contained" 
        size="large" 
        startIcon={<LoginIcon />}
        onClick={openAuthDialog}
        sx={{ mt: 3 }}
      >
        Sign In to Continue
      </Button>
      
      <Box sx={{ mt: 6 }}>
        <Typography variant="h6" gutterBottom>
          Platform Features
        </Typography>
        <List>
          <ListItem>
            <ListItemIcon><DashboardIcon /></ListItemIcon>
            <ListItemText primary="Real-time Analytics Dashboard" secondary="Monitor your scraping operations in real-time" />
          </ListItem>
          <ListItem>
            <ListItemIcon><JobIcon /></ListItemIcon>
            <ListItemText primary="Advanced Job Management" secondary="Create, schedule, and monitor scraping jobs" />
          </ListItem>
          <ListItem>
            <ListItemIcon><StoreIcon /></ListItemIcon>
            <ListItemText primary="Spider Marketplace" secondary="Browse and install pre-built scrapers" />
          </ListItem>
          <ListItem>
            <ListItemIcon><OSINTIcon /></ListItemIcon>
            <ListItemText primary="OSINT Center" secondary="Open Source Intelligence gathering tools" />
          </ListItem>
        </List>
      </Box>
    </Container>
  );
}

export default App;
