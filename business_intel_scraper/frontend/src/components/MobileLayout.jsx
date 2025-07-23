import React, { useState, useEffect } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  useTheme,
  useMediaQuery,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Collapse,
  Paper,
  Container,
  Grid,
  Card,
  CardContent,
  Slide,
  Zoom,
  Grow
} from '@mui/material';
import {
  Menu,
  Close,
  Add,
  PlayArrow,
  Settings,
  Dashboard,
  DataUsage,
  Schedule,
  Notifications,
  Search,
  FilterList,
  MoreVert,
  SwipeUp,
  TouchApp
} from '@mui/icons-material';

// Mobile responsive layout hook
export const useMobileLayout = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg'));
  const isDesktop = useMediaQuery(theme.breakpoints.up('lg'));
  
  const [drawerOpen, setDrawerOpen] = useState(!isMobile);
  const [orientation, setOrientation] = useState('portrait');

  useEffect(() => {
    const handleOrientationChange = () => {
      setOrientation(window.innerHeight > window.innerWidth ? 'portrait' : 'landscape');
    };

    window.addEventListener('resize', handleOrientationChange);
    handleOrientationChange();

    return () => window.removeEventListener('resize', handleOrientationChange);
  }, []);

  useEffect(() => {
    if (isMobile) {
      setDrawerOpen(false);
    } else {
      setDrawerOpen(true);
    }
  }, [isMobile]);

  return {
    isMobile,
    isTablet,
    isDesktop,
    orientation,
    drawerOpen,
    setDrawerOpen,
    drawerWidth: isMobile ? '100%' : isTablet ? 240 : 280
  };
};

// Mobile Navigation Component
export const MobileNavigation = ({ 
  children, 
  navigationItems = [], 
  onNavigate = () => {},
  currentPage = 'dashboard' 
}) => {
  const { 
    isMobile, 
    isTablet, 
    drawerOpen, 
    setDrawerOpen, 
    drawerWidth 
  } = useMobileLayout();
  
  const [speedDialOpen, setSpeedDialOpen] = useState(false);

  const quickActions = [
    { icon: <Add />, name: 'New Job', action: () => onNavigate('create-job') },
    { icon: <PlayArrow />, name: 'Start Scraping', action: () => onNavigate('run-job') },
    { icon: <Search />, name: 'Search', action: () => onNavigate('search') },
    { icon: <Settings />, name: 'Settings', action: () => onNavigate('settings') }
  ];

  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      {/* Mobile App Bar */}
      {isMobile && (
        <AppBar 
          position="fixed" 
          sx={{ 
            zIndex: (theme) => theme.zIndex.drawer + 1,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
          }}
        >
          <Toolbar>
            <IconButton
              color="inherit"
              edge="start"
              onClick={toggleDrawer}
              sx={{ mr: 2 }}
            >
              <Menu />
            </IconButton>
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
              Business Intel Scraper
            </Typography>
            <IconButton color="inherit">
              <MoreVert />
            </IconButton>
          </Toolbar>
        </AppBar>
      )}

      {/* Mobile Drawer */}
      <Drawer
        variant={isMobile ? 'temporary' : 'persistent'}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        ModalProps={{
          keepMounted: true // Better mobile performance
        }}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            ...(isMobile && {
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)'
            })
          }
        }}
      >
        {isMobile && (
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            p: 2,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white'
          }}>
            <Typography variant="h6">Menu</Typography>
            <IconButton color="inherit" onClick={() => setDrawerOpen(false)}>
              <Close />
            </IconButton>
          </Box>
        )}
        
        <NavigationList 
          items={navigationItems}
          currentPage={currentPage}
          onNavigate={onNavigate}
          isMobile={isMobile}
          onItemClick={() => isMobile && setDrawerOpen(false)}
        />
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          ...(isMobile && {
            mt: 8 // Account for app bar height
          }),
          transition: (theme) => theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          ...(drawerOpen && !isMobile && {
            ml: `${drawerWidth}px`,
            transition: (theme) => theme.transitions.create('margin', {
              easing: theme.transitions.easing.easeOut,
              duration: theme.transitions.duration.enteringScreen,
            })
          })
        }}
      >
        {children}
      </Box>

      {/* Mobile Speed Dial */}
      {isMobile && (
        <SpeedDial
          ariaLabel="Quick Actions"
          sx={{ 
            position: 'fixed', 
            bottom: 16, 
            right: 16,
            '& .MuiFab-primary': {
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            }
          }}
          icon={<SpeedDialIcon />}
          open={speedDialOpen}
          onClose={() => setSpeedDialOpen(false)}
          onOpen={() => setSpeedDialOpen(true)}
        >
          {quickActions.map((action) => (
            <SpeedDialAction
              key={action.name}
              icon={action.icon}
              tooltipTitle={action.name}
              onClick={() => {
                action.action();
                setSpeedDialOpen(false);
              }}
            />
          ))}
        </SpeedDial>
      )}
    </Box>
  );
};

// Navigation List Component
const NavigationList = ({ 
  items, 
  currentPage, 
  onNavigate, 
  isMobile, 
  onItemClick 
}) => {
  return (
    <Box sx={{ overflow: 'auto', flex: 1 }}>
      {items.map((item, index) => (
        <NavigationItem
          key={item.id || index}
          item={item}
          isActive={currentPage === item.id}
          onClick={() => {
            onNavigate(item.id);
            onItemClick();
          }}
          isMobile={isMobile}
        />
      ))}
    </Box>
  );
};

// Navigation Item Component
const NavigationItem = ({ item, isActive, onClick, isMobile }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <Box>
      <Box
        onClick={() => {
          if (item.children) {
            setExpanded(!expanded);
          } else {
            onClick();
          }
        }}
        sx={{
          display: 'flex',
          alignItems: 'center',
          p: isMobile ? 2 : 1.5,
          cursor: 'pointer',
          backgroundColor: isActive ? 'primary.main' : 'transparent',
          color: isActive ? 'primary.contrastText' : 'text.primary',
          '&:hover': {
            backgroundColor: isActive ? 'primary.dark' : 'action.hover'
          },
          transition: 'all 0.2s ease-in-out'
        }}
      >
        {item.icon && (
          <Box sx={{ mr: 2, display: 'flex', alignItems: 'center' }}>
            {item.icon}
          </Box>
        )}
        <Typography variant={isMobile ? 'body1' : 'body2'} sx={{ flexGrow: 1 }}>
          {item.label}
        </Typography>
        {item.children && (
          <IconButton size="small">
            {expanded ? <Close /> : <Add />}
          </IconButton>
        )}
      </Box>
      
      {item.children && (
        <Collapse in={expanded}>
          <Box sx={{ pl: 4 }}>
            {item.children.map((child, index) => (
              <NavigationItem
                key={child.id || index}
                item={child}
                isActive={false}
                onClick={onClick}
                isMobile={isMobile}
              />
            ))}
          </Box>
        </Collapse>
      )}
    </Box>
  );
};

// Responsive Grid Layout
export const ResponsiveGrid = ({ children, spacing = 2 }) => {
  const { isMobile, isTablet } = useMobileLayout();
  
  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      <Grid container spacing={spacing}>
        {React.Children.map(children, (child, index) => {
          if (React.isValidElement(child)) {
            // Default responsive breakpoints
            const defaultProps = {
              xs: 12,
              sm: isMobile ? 12 : 6,
              md: isTablet ? 6 : 4,
              lg: 3
            };
            
            return React.cloneElement(child, {
              ...defaultProps,
              ...child.props
            });
          }
          return child;
        })}
      </Grid>
    </Container>
  );
};

// Mobile-friendly Card Component
export const MobileCard = ({ 
  title, 
  children, 
  actions = [], 
  collapsible = false,
  defaultExpanded = true,
  ...props 
}) => {
  const { isMobile } = useMobileLayout();
  const [expanded, setExpanded] = useState(defaultExpanded);

  return (
    <Grow in timeout={300}>
      <Card 
        {...props}
        sx={{
          mb: 2,
          ...(isMobile && {
            borderRadius: 2,
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }),
          ...props.sx
        }}
      >
        <Box
          onClick={collapsible ? () => setExpanded(!expanded) : undefined}
          sx={{
            cursor: collapsible ? 'pointer' : 'default',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            p: 2,
            ...(collapsible && {
              '&:hover': {
                backgroundColor: 'action.hover'
              }
            })
          }}
        >
          <Typography variant={isMobile ? 'h6' : 'h6'} component="h2">
            {title}
          </Typography>
          {collapsible && (
            <IconButton size="small">
              {expanded ? <Close /> : <Add />}
            </IconButton>
          )}
        </Box>
        
        <Collapse in={expanded}>
          <CardContent sx={{ pt: 0 }}>
            {children}
          </CardContent>
          
          {actions.length > 0 && (
            <Box sx={{ p: 2, pt: 0, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {actions.map((action, index) => (
                <Box key={index}>
                  {action}
                </Box>
              ))}
            </Box>
          )}
        </Collapse>
      </Card>
    </Grow>
  );
};

// Touch-friendly Button Group
export const MobileButtonGroup = ({ 
  buttons = [], 
  orientation = 'horizontal',
  fullWidth = false 
}) => {
  const { isMobile } = useMobileLayout();
  
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: orientation === 'vertical' || isMobile ? 'column' : 'row',
        gap: 1,
        width: fullWidth ? '100%' : 'auto'
      }}
    >
      {buttons.map((button, index) => (
        <Box key={index} sx={{ flex: fullWidth ? 1 : 'none' }}>
          {React.cloneElement(button, {
            fullWidth: fullWidth || isMobile,
            size: isMobile ? 'large' : 'medium',
            ...button.props
          })}
        </Box>
      ))}
    </Box>
  );
};

// Swipe Gesture Handler
export const SwipeablePanel = ({ 
  children, 
  onSwipeLeft = () => {}, 
  onSwipeRight = () => {},
  onSwipeUp = () => {},
  onSwipeDown = () => {}
}) => {
  const [touchStart, setTouchStart] = useState(null);
  const [touchEnd, setTouchEnd] = useState(null);

  const minSwipeDistance = 50;

  const onTouchStart = (e) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
  };

  const onTouchMove = (e) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;

    if (isLeftSwipe) {
      onSwipeLeft();
    } else if (isRightSwipe) {
      onSwipeRight();
    }
  };

  return (
    <Box
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
      sx={{ width: '100%', height: '100%' }}
    >
      {children}
    </Box>
  );
};

// Mobile Optimized Table
export const MobileTable = ({ 
  data = [], 
  columns = [], 
  onRowClick = () => {},
  maxHeight = '400px'
}) => {
  const { isMobile } = useMobileLayout();
  
  if (isMobile) {
    return (
      <Box sx={{ maxHeight, overflow: 'auto' }}>
        {data.map((row, index) => (
          <Paper
            key={index}
            sx={{
              p: 2,
              mb: 1,
              cursor: 'pointer',
              '&:hover': {
                backgroundColor: 'action.hover'
              }
            }}
            onClick={() => onRowClick(row)}
          >
            {columns.map((column) => (
              <Box key={column.key} sx={{ mb: 1, display: 'flex' }}>
                <Typography variant="body2" color="text.secondary" sx={{ minWidth: 100 }}>
                  {column.label}:
                </Typography>
                <Typography variant="body2" sx={{ ml: 1 }}>
                  {row[column.key]}
                </Typography>
              </Box>
            ))}
          </Paper>
        ))}
      </Box>
    );
  }

  // Desktop table view would be rendered here
  return null;
};

export default MobileNavigation;
