import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { 
  CssBaseline, 
  Container, 
  AppBar, 
  Toolbar, 
  Typography, 
  IconButton,
  Menu,
  MenuItem,
  Switch,
  FormControlLabel,
  Box,
  Tooltip
} from '@mui/material';
import { Settings, Brightness4, Brightness7 } from '@mui/icons-material';
import DashboardEnhanced from './components/widgets/DashboardEnhanced';

const App = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const theme = createTheme({
    palette: {
      mode: isDarkMode ? 'dark' : 'light',
      primary: {
        main: '#1976d2',
      },
      secondary: {
        main: '#dc004e',
      },
    },
    typography: {
      h6: {
        fontWeight: 600,
      },
    },
    components: {
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 12,
            boxShadow: '0 2px 12px rgba(0,0,0,0.1)',
          },
        },
      },
    },
  });

  const handleSettingsClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleSettingsClose = () => {
    setAnchorEl(null);
  };

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    handleSettingsClose();
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static" elevation={2}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Business Intelligence Analytics - Phase 3
          </Typography>
          
          <Box display="flex" alignItems="center" gap={1}>
            <Tooltip title="Toggle Dark Mode">
              <IconButton color="inherit" onClick={toggleDarkMode}>
                {isDarkMode ? <Brightness7 /> : <Brightness4 />}
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Settings">
              <IconButton color="inherit" onClick={handleSettingsClick}>
                <Settings />
              </IconButton>
            </Tooltip>
          </Box>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleSettingsClose}
          >
            <MenuItem>
              <FormControlLabel
                control={
                  <Switch
                    checked={isDarkMode}
                    onChange={toggleDarkMode}
                    color="primary"
                  />
                }
                label="Dark Mode"
              />
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="xl" sx={{ mt: 2, mb: 2 }}>
        <DashboardEnhanced />
      </Container>
    </ThemeProvider>
  );
};

export default App;
