"""
React Router Performance Optimizations
Code splitting, route preloading, and navigation performance improvements
"""

import React, { 
  Suspense, 
  lazy, 
  memo, 
  useEffect, 
  useState, 
  useCallback,
  useMemo
} from 'react';
import { 
  Routes, 
  Route, 
  useNavigate, 
  useLocation, 
  Navigate,
  Outlet
} from 'react-router-dom';
import { Box, CircularProgress, Alert, Fade } from '@mui/material';

// Performance utilities
import { ComponentPreloader } from '../utils/performance-optimizations';
import { useCachedState } from '../utils/caching-system';

// Optimized Loading Component
const OptimizedLoader = memo(({ text = "Loading...", size = 40 }) => (
  <Fade in timeout={300}>
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="200px"
      gap={2}
    >
      <CircularProgress size={size} />
      <Box color="text.secondary" fontSize="14px">
        {text}
      </Box>
    </Box>
  </Fade>
));

// Error Boundary for Route Components
class RouteErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Route Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Alert severity="error" sx={{ m: 2 }}>
          <div>Something went wrong loading this page.</div>
          <div style={{ fontSize: '12px', marginTop: '8px' }}>
            {this.state.error?.message}
          </div>
        </Alert>
      );
    }

    return this.props.children;
  }
}

// Route Component Factory with optimizations
const createOptimizedRoute = (importFn, routeName, preload = false) => {
  // Create lazy component with error handling
  const LazyComponent = lazy(async () => {
    try {
      const module = await importFn();
      
      // Track component load time in development
      if (process.env.NODE_ENV === 'development') {
        console.info(`Route ${routeName} loaded`);
      }
      
      return module;
    } catch (error) {
      console.error(`Failed to load route ${routeName}:`, error);
      
      // Return fallback component
      return {
        default: () => (
          <Alert severity="error" sx={{ m: 2 }}>
            Failed to load {routeName}. Please try refreshing the page.
          </Alert>
        )
      };
    }
  });

  // Preload if requested
  if (preload) {
    ComponentPreloader.preload(importFn, routeName);
  }

  // Return optimized component with error boundary
  return memo((props) => (
    <RouteErrorBoundary>
      <Suspense fallback={<OptimizedLoader text={`Loading ${routeName}...`} />}>
        <LazyComponent {...props} />
      </Suspense>
    </RouteErrorBoundary>
  ));
};

// Lazy load route components with smart preloading
const routes = {
  // Dashboard routes (preloaded)
  Dashboard: createOptimizedRoute(
    () => import('../components/OptimizedDashboard'),
    'Dashboard',
    true
  ),
  
  // Analytics routes
  Analytics: createOptimizedRoute(
    () => import('../components/AnalyticsDashboard'),
    'Analytics'
  ),
  
  // Visualization routes
  NetworkView: createOptimizedRoute(
    () => import('../components/widgets/NetworkGraph'),
    'Network View'
  ),
  
  TimelineView: createOptimizedRoute(
    () => import('../components/widgets/TimelineSimple'),
    'Timeline View'
  ),
  
  MapView: createOptimizedRoute(
    () => import('../components/widgets/GeospatialMap'),
    'Map View'
  ),
  
  // Data management routes
  DataProcessor: createOptimizedRoute(
    () => import('../components/DataProcessor'),
    'Data Processor'
  ),
  
  // Configuration routes
  Settings: createOptimizedRoute(
    () => import('../components/ConfigurationManager'),
    'Settings'
  ),
  
  // Admin routes
  SystemAdmin: createOptimizedRoute(
    () => import('../components/SystemAdmin'),
    'System Admin'
  ),
  
  // Collaboration routes
  TeamCollaboration: createOptimizedRoute(
    () => import('../components/TeamCollaboration'),
    'Team Collaboration'
  ),
  
  // Advanced features
  AdvancedVisualization: createOptimizedRoute(
    () => import('../components/AdvancedVisualization'),
    'Advanced Visualization'
  )
};

// Route Preloader Hook
export const useRoutePreloader = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Preload routes based on current location
  useEffect(() => {
    const currentPath = location.pathname;
    
    // Define preload strategies based on current route
    const preloadStrategies = {
      '/': ['Analytics', 'NetworkView'], // From dashboard, likely to visit analytics
      '/analytics': ['Dashboard', 'AdvancedVisualization'],
      '/network': ['TimelineView', 'MapView'],
      '/data': ['Analytics', 'Settings'],
      '/admin': ['Settings', 'TeamCollaboration']
    };
    
    const toPreload = preloadStrategies[currentPath] || [];
    
    // Preload with a small delay to not interfere with current page
    const preloadTimer = setTimeout(() => {
      toPreload.forEach(routeName => {
        if (routes[routeName]) {
          // Preload the component
          const importFn = getImportFunction(routeName);
          if (importFn) {
            ComponentPreloader.preload(importFn, routeName);
          }
        }
      });
    }, 1000);
    
    return () => clearTimeout(preloadTimer);
  }, [location.pathname]);
  
  // Enhanced navigation with preloading
  const navigateWithPreload = useCallback((to, options = {}) => {
    // Preload destination route if possible
    const routeName = getRouteNameFromPath(to);
    if (routeName && routes[routeName]) {
      const importFn = getImportFunction(routeName);
      if (importFn) {
        ComponentPreloader.preload(importFn, routeName);
      }
    }
    
    navigate(to, options);
  }, [navigate]);
  
  return { navigateWithPreload };
};

// Helper function to get import function by route name
const getImportFunction = (routeName) => {
  const importMap = {
    Dashboard: () => import('../components/OptimizedDashboard'),
    Analytics: () => import('../components/AnalyticsDashboard'),
    NetworkView: () => import('../components/widgets/NetworkGraph'),
    TimelineView: () => import('../components/widgets/TimelineSimple'),
    MapView: () => import('../components/widgets/GeospatialMap'),
    DataProcessor: () => import('../components/DataProcessor'),
    Settings: () => import('../components/ConfigurationManager'),
    SystemAdmin: () => import('../components/SystemAdmin'),
    TeamCollaboration: () => import('../components/TeamCollaboration'),
    AdvancedVisualization: () => import('../components/AdvancedVisualization')
  };
  
  return importMap[routeName];
};

// Helper function to get route name from path
const getRouteNameFromPath = (path) => {
  const pathMap = {
    '/': 'Dashboard',
    '/dashboard': 'Dashboard',
    '/analytics': 'Analytics',
    '/network': 'NetworkView',
    '/timeline': 'TimelineView',
    '/map': 'MapView',
    '/data': 'DataProcessor',
    '/settings': 'Settings',
    '/admin': 'SystemAdmin',
    '/team': 'TeamCollaboration',
    '/visualization': 'AdvancedVisualization'
  };
  
  return pathMap[path];
};

// Navigation Performance Monitor
export const useNavigationPerformance = () => {
  const location = useLocation();
  const [navigationMetrics, setNavigationMetrics] = useCachedState(
    'navigation_metrics',
    { totalNavigations: 0, averageLoadTime: 0, routeMetrics: {} }
  );
  
  useEffect(() => {
    const startTime = performance.now();
    
    // Track navigation start
    const navigationStart = Date.now();
    
    return () => {
      // Track navigation complete
      const endTime = performance.now();
      const loadTime = endTime - startTime;
      
      setNavigationMetrics(prev => {
        const newMetrics = { ...prev };
        newMetrics.totalNavigations += 1;
        
        // Update route-specific metrics
        const routePath = location.pathname;
        if (!newMetrics.routeMetrics[routePath]) {
          newMetrics.routeMetrics[routePath] = {
            visits: 0,
            totalLoadTime: 0,
            averageLoadTime: 0
          };
        }
        
        const routeMetric = newMetrics.routeMetrics[routePath];
        routeMetric.visits += 1;
        routeMetric.totalLoadTime += loadTime;
        routeMetric.averageLoadTime = routeMetric.totalLoadTime / routeMetric.visits;
        
        // Update global average
        const totalLoadTime = Object.values(newMetrics.routeMetrics)
          .reduce((sum, metric) => sum + metric.totalLoadTime, 0);
        newMetrics.averageLoadTime = totalLoadTime / newMetrics.totalNavigations;
        
        return newMetrics;
      });
    };
  }, [location.pathname, setNavigationMetrics]);
  
  return navigationMetrics;
};

// Layout Component with Performance Optimizations
export const OptimizedLayout = memo(({ children }) => {
  const navigationMetrics = useNavigationPerformance();
  
  // Only show performance info in development
  const showPerformanceInfo = process.env.NODE_ENV === 'development';
  
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {showPerformanceInfo && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            right: 0,
            zIndex: 9999,
            bgcolor: 'rgba(0,0,0,0.8)',
            color: 'white',
            p: 1,
            fontSize: '10px',
            maxWidth: 200
          }}
        >
          Nav: {navigationMetrics.totalNavigations} | 
          Avg: {navigationMetrics.averageLoadTime.toFixed(0)}ms
        </Box>
      )}
      
      <Box component="main" sx={{ flexGrow: 1 }}>
        <Outlet />
      </Box>
    </Box>
  );
});

// Main Router Component with Optimizations
export const OptimizedRouter = memo(() => {
  return (
    <Routes>
      <Route path="/" element={<OptimizedLayout />}>
        {/* Dashboard Routes */}
        <Route index element={<routes.Dashboard />} />
        <Route path="dashboard" element={<routes.Dashboard />} />
        
        {/* Analytics Routes */}
        <Route path="analytics" element={<routes.Analytics />} />
        
        {/* Visualization Routes */}
        <Route path="network" element={<routes.NetworkView />} />
        <Route path="timeline" element={<routes.TimelineView />} />
        <Route path="map" element={<routes.MapView />} />
        <Route path="visualization" element={<routes.AdvancedVisualization />} />
        
        {/* Data Management Routes */}
        <Route path="data" element={<routes.DataProcessor />} />
        
        {/* Configuration Routes */}
        <Route path="settings" element={<routes.Settings />} />
        
        {/* Admin Routes */}
        <Route path="admin" element={<routes.SystemAdmin />} />
        
        {/* Collaboration Routes */}
        <Route path="team" element={<routes.TeamCollaboration />} />
        
        {/* Catch-all redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
});

// Performance Analytics Component
export const NavigationAnalytics = memo(() => {
  const metrics = useNavigationPerformance();
  
  const sortedRoutes = useMemo(() => {
    return Object.entries(metrics.routeMetrics || {})
      .sort(([,a], [,b]) => b.visits - a.visits)
      .slice(0, 10); // Top 10 routes
  }, [metrics.routeMetrics]);
  
  if (process.env.NODE_ENV !== 'development') {
    return null;
  }
  
  return (
    <Box sx={{ p: 2, bgcolor: 'grey.100', borderRadius: 1, mt: 2 }}>
      <Box sx={{ fontWeight: 'bold', mb: 1 }}>Navigation Performance</Box>
      <Box sx={{ fontSize: '12px', mb: 1 }}>
        Total Navigations: {metrics.totalNavigations} | 
        Average Load Time: {metrics.averageLoadTime.toFixed(2)}ms
      </Box>
      
      <Box sx={{ fontSize: '11px' }}>
        <div>Top Routes:</div>
        {sortedRoutes.map(([path, metric]) => (
          <div key={path}>
            {path}: {metric.visits} visits, {metric.averageLoadTime.toFixed(1)}ms avg
          </div>
        ))}
      </Box>
    </Box>
  );
});

// Route Performance Configuration
export const RouteConfig = {
  preloadStrategy: {
    immediate: ['Dashboard'], // Preload immediately
    onHover: ['Analytics', 'Settings'], // Preload on navigation hover
    lazy: ['Admin', 'TeamCollaboration'] // Only load when accessed
  },
  
  caching: {
    enabled: true,
    ttl: 300000, // 5 minutes
    maxRoutes: 5
  },
  
  performance: {
    trackMetrics: true,
    slowRouteThreshold: 1000, // 1 second
    enablePreloading: true
  }
};

export {
  OptimizedRouter as default,
  useRoutePreloader,
  useNavigationPerformance,
  OptimizedLayout,
  NavigationAnalytics,
  createOptimizedRoute,
  RouteConfig
};
