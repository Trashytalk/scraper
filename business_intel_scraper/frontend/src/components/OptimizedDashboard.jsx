"""
Optimized Dashboard Components
High-performance React components with caching, virtualization, and optimizations
"""

import React, { 
  memo, 
  useState, 
  useEffect, 
  useCallback, 
  useMemo,
  Suspense,
  lazy
} from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Chip,
  Button,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Refresh,
  Settings,
  Speed,
  Memory,
  TrendingUp,
  TrendingDown,
  Visibility,
  VisibilityOff
} from '@mui/icons-material';

// Import performance utilities
import { 
  EnhancedMemo,
  VirtualScrollList,
  OptimizedImage,
  withOptimizations,
  useOptimizedFetch,
  useDebouncedSearch
} from '../utils/performance-optimizations';

import {
  useCachedAPI,
  useCachedState,
  useCachedUserPreference,
  CacheStatistics
} from '../utils/caching-system';

// Lazy load heavy components
const NetworkVisualization = lazy(() => import('./widgets/NetworkGraph'));
const TimelineChart = lazy(() => import('./widgets/TimelineSimple'));
const GeospatialMap = lazy(() => import('./widgets/GeospatialMap'));

// Optimized Metric Card Component
export const OptimizedMetricCard = EnhancedMemo(({ 
  title, 
  value, 
  trend, 
  icon, 
  color = 'primary',
  loading = false,
  onClick
}) => {
  const trendIcon = trend > 0 ? <TrendingUp /> : trend < 0 ? <TrendingDown /> : null;
  const trendColor = trend > 0 ? 'success' : trend < 0 ? 'error' : 'default';

  return (
    <Card 
      sx={{ 
        height: '100%', 
        cursor: onClick ? 'pointer' : 'default',
        transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
        '&:hover': onClick ? {
          transform: 'translateY(-2px)',
          boxShadow: 2
        } : {}
      }}
      onClick={onClick}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box flex={1}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              {title}
            </Typography>
            {loading ? (
              <CircularProgress size={24} />
            ) : (
              <Typography variant="h4" color={`${color}.main`} component="div">
                {typeof value === 'number' ? value.toLocaleString() : value}
              </Typography>
            )}
          </Box>
          
          <Box display="flex" flexDirection="column" alignItems="center" gap={1}>
            {icon && (
              <Box color={`${color}.main`}>
                {icon}
              </Box>
            )}
            {trend !== undefined && (
              <Chip
                icon={trendIcon}
                label={`${trend > 0 ? '+' : ''}${trend}%`}
                size="small"
                color={trendColor}
                variant="outlined"
              />
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}, 
// Custom comparison function for better memoization
(prevProps, nextProps) => {
  return (
    prevProps.title === nextProps.title &&
    prevProps.value === nextProps.value &&
    prevProps.trend === nextProps.trend &&
    prevProps.loading === nextProps.loading &&
    prevProps.color === nextProps.color
  );
},
'OptimizedMetricCard'
);

// Virtualized Data Table Component
export const VirtualizedDataTable = memo(({ 
  data = [], 
  columns = [], 
  itemHeight = 60,
  maxHeight = 400 
}) => {
  const renderTableRow = useCallback((item, index) => (
    <Box
      key={index}
      display="flex"
      alignItems="center"
      px={2}
      py={1}
      borderBottom="1px solid #e0e0e0"
      bgcolor={index % 2 === 0 ? 'grey.50' : 'white'}
    >
      {columns.map((column, colIndex) => (
        <Box 
          key={colIndex}
          flex={column.flex || 1}
          minWidth={column.minWidth || 100}
        >
          <Typography variant="body2">
            {column.render ? column.render(item[column.key], item) : item[column.key]}
          </Typography>
        </Box>
      ))}
    </Box>
  ), [columns]);

  if (!data.length) {
    return (
      <Box textAlign="center" py={4}>
        <Typography color="text.secondary">No data available</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Table Header */}
      <Box
        display="flex"
        alignItems="center"
        px={2}
        py={1}
        bgcolor="grey.100"
        fontWeight="bold"
      >
        {columns.map((column, index) => (
          <Box 
            key={index}
            flex={column.flex || 1}
            minWidth={column.minWidth || 100}
          >
            <Typography variant="subtitle2" fontWeight="bold">
              {column.label}
            </Typography>
          </Box>
        ))}
      </Box>

      {/* Virtualized Rows */}
      <VirtualScrollList
        items={data}
        renderItem={renderTableRow}
        itemHeight={itemHeight}
        containerHeight={Math.min(maxHeight, data.length * itemHeight + 100)}
      />
    </Box>
  );
});

// Optimized Dashboard Component
export const OptimizedDashboard = withOptimizations(() => {
  // Cached user preferences
  const [showPerformanceMetrics, setShowPerformanceMetrics] = useCachedUserPreference(
    'dashboard_performance_metrics', 
    false
  );
  const [autoRefresh, setAutoRefresh] = useCachedUserPreference('dashboard_auto_refresh', true);
  const [refreshInterval, setRefreshInterval] = useCachedUserPreference('dashboard_refresh_interval', 30000);

  // Cached component state
  const [selectedView, setSelectedView] = useCachedState('dashboard_view', 'overview');
  const [filters, setFilters] = useCachedState('dashboard_filters', {});

  // Cached API data
  const { 
    data: metricsData, 
    loading: metricsLoading, 
    error: metricsError,
    refresh: refreshMetrics 
  } = useCachedAPI('/api/dashboard/metrics', {
    cacheTtl: refreshInterval,
    params: filters
  });

  const {
    data: performanceData,
    loading: performanceLoading,
    refresh: refreshPerformance
  } = useCachedAPI('/api/performance/metrics', {
    cacheTtl: 60000 // 1 minute cache
  });

  // Auto-refresh functionality
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      refreshMetrics();
      if (showPerformanceMetrics) {
        refreshPerformance();
      }
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, refreshMetrics, refreshPerformance, showPerformanceMetrics]);

  // Memoized metric cards data
  const metricCards = useMemo(() => {
    if (!metricsData) return [];

    return [
      {
        title: 'Total Records',
        value: metricsData.total_records || 0,
        trend: metricsData.records_trend || 0,
        icon: <Speed />,
        color: 'primary'
      },
      {
        title: 'Active Jobs',
        value: metricsData.active_jobs || 0,
        trend: metricsData.jobs_trend || 0,
        icon: <TrendingUp />,
        color: 'success'
      },
      {
        title: 'Success Rate',
        value: `${metricsData.success_rate || 0}%`,
        trend: metricsData.success_trend || 0,
        icon: <TrendingUp />,
        color: 'info'
      },
      {
        title: 'Avg Response Time',
        value: `${metricsData.avg_response_time || 0}ms`,
        trend: metricsData.response_trend || 0,
        icon: <Memory />,
        color: 'warning'
      }
    ];
  }, [metricsData]);

  // Memoized performance cards
  const performanceCards = useMemo(() => {
    if (!showPerformanceMetrics || !performanceData) return [];

    return [
      {
        title: 'Memory Usage',
        value: `${performanceData.memory_usage || 0}%`,
        trend: performanceData.memory_trend || 0,
        icon: <Memory />,
        color: 'error'
      },
      {
        title: 'Cache Hit Rate',
        value: `${performanceData.cache_hit_rate || 0}%`,
        trend: performanceData.cache_trend || 0,
        icon: <Speed />,
        color: 'success'
      }
    ];
  }, [showPerformanceMetrics, performanceData]);

  const handleRefresh = useCallback(() => {
    refreshMetrics();
    if (showPerformanceMetrics) {
      refreshPerformance();
    }
  }, [refreshMetrics, refreshPerformance, showPerformanceMetrics]);

  if (metricsError) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Failed to load dashboard data: {metricsError.message}
      </Alert>
    );
  }

  return (
    <Box p={3}>
      {/* Dashboard Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Business Intelligence Dashboard
        </Typography>

        <Box display="flex" alignItems="center" gap={2}>
          <FormControlLabel
            control={
              <Switch
                checked={showPerformanceMetrics}
                onChange={(e) => setShowPerformanceMetrics(e.target.checked)}
                size="small"
              />
            }
            label="Performance Metrics"
          />

          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                size="small"
              />
            }
            label="Auto Refresh"
          />

          <Tooltip title="Refresh Dashboard">
            <IconButton onClick={handleRefresh} disabled={metricsLoading}>
              <Refresh />
            </IconButton>
          </Tooltip>

          <Tooltip title="Dashboard Settings">
            <IconButton>
              <Settings />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Performance Metrics (if enabled) */}
      {showPerformanceMetrics && (
        <Box mb={3}>
          <Typography variant="h6" gutterBottom>
            Performance Metrics
          </Typography>
          <Grid container spacing={2}>
            {performanceCards.map((card, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <OptimizedMetricCard
                  {...card}
                  loading={performanceLoading}
                />
              </Grid>
            ))}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <CacheStatistics />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}

      {/* Main Metrics */}
      <Box mb={3}>
        <Typography variant="h6" gutterBottom>
          Key Metrics
        </Typography>
        <Grid container spacing={2}>
          {metricCards.map((card, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <OptimizedMetricCard
                {...card}
                loading={metricsLoading}
                onClick={() => console.log(`Clicked ${card.title}`)}
              />
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Visualization Panels */}
      <Grid container spacing={3}>
        {/* Network Visualization */}
        <Grid item xs={12} lg={6}>
          <Card sx={{ height: 500 }}>
            <CardContent sx={{ height: '100%' }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Network Overview</Typography>
                <Tooltip title="Toggle Visibility">
                  <IconButton size="small">
                    <Visibility />
                  </IconButton>
                </Tooltip>
              </Box>
              <Suspense fallback={
                <Box display="flex" justifyContent="center" alignItems="center" height="400px">
                  <CircularProgress />
                </Box>
              }>
                <NetworkVisualization height={400} />
              </Suspense>
            </CardContent>
          </Card>
        </Grid>

        {/* Timeline Visualization */}
        <Grid item xs={12} lg={6}>
          <Card sx={{ height: 500 }}>
            <CardContent sx={{ height: '100%' }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Activity Timeline</Typography>
                <Tooltip title="Export Data">
                  <IconButton size="small">
                    <Settings />
                  </IconButton>
                </Tooltip>
              </Box>
              <Suspense fallback={
                <Box display="flex" justifyContent="center" alignItems="center" height="400px">
                  <CircularProgress />
                </Box>
              }>
                <TimelineChart height={400} />
              </Suspense>
            </CardContent>
          </Card>
        </Grid>

        {/* Data Table */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activities
              </Typography>
              {metricsData?.recent_activities && (
                <VirtualizedDataTable
                  data={metricsData.recent_activities}
                  columns={[
                    { key: 'timestamp', label: 'Time', flex: 1 },
                    { key: 'activity', label: 'Activity', flex: 2 },
                    { key: 'status', label: 'Status', flex: 1, 
                      render: (value) => (
                        <Chip 
                          label={value} 
                          size="small" 
                          color={value === 'success' ? 'success' : 'error'}
                        />
                      )
                    },
                    { key: 'duration', label: 'Duration', flex: 1 }
                  ]}
                  maxHeight={300}
                />
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}, {
  memo: true,
  monitoring: true,
  errorBoundary: true
});

// Optimized Search Component
export const OptimizedSearch = memo(({ onSearch, placeholder = "Search..." }) => {
  const { searchTerm, setSearchTerm, results, loading } = useDebouncedSearch(
    onSearch,
    300 // 300ms debounce
  );

  return (
    <Box position="relative">
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder={placeholder}
        style={{
          width: '100%',
          padding: '8px 12px',
          border: '1px solid #ccc',
          borderRadius: '4px',
          fontSize: '14px'
        }}
      />
      
      {loading && (
        <Box position="absolute" right={8} top="50%" sx={{ transform: 'translateY(-50%)' }}>
          <CircularProgress size={16} />
        </Box>
      )}
      
      {results.length > 0 && (
        <Box
          position="absolute"
          top="100%"
          left={0}
          right={0}
          bgcolor="white"
          boxShadow={2}
          borderRadius={1}
          zIndex={1000}
          maxHeight={200}
          overflow="auto"
        >
          {results.map((result, index) => (
            <Box
              key={index}
              p={1}
              borderBottom="1px solid #eee"
              sx={{ '&:hover': { bgcolor: 'grey.100' } }}
            >
              {result.title || result.name || JSON.stringify(result)}
            </Box>
          ))}
        </Box>
      )}
    </Box>
  );
});

// Optimized Image Gallery
export const OptimizedImageGallery = memo(({ images = [] }) => {
  const [selectedImage, setSelectedImage] = useState(null);

  return (
    <Box>
      <Grid container spacing={2}>
        {images.map((image, index) => (
          <Grid item xs={6} sm={4} md={3} key={index}>
            <Box
              sx={{ 
                cursor: 'pointer',
                '&:hover': { transform: 'scale(1.05)' },
                transition: 'transform 0.2s'
              }}
              onClick={() => setSelectedImage(image)}
            >
              <OptimizedImage
                src={image.thumbnail || image.url}
                alt={image.alt || `Image ${index + 1}`}
                width="100%"
                height={150}
                lazy={true}
                placeholder={<Box bgcolor="grey.200" height={150} />}
              />
            </Box>
          </Grid>
        ))}
      </Grid>

      {/* Image Modal would go here */}
    </Box>
  );
});

export {
  OptimizedDashboard as default,
  OptimizedMetricCard,
  VirtualizedDataTable,
  OptimizedSearch,
  OptimizedImageGallery
};
