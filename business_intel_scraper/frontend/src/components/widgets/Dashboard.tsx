import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography, Box, Tab, Tabs, IconButton, Card, CardContent } from '@mui/material';
import { Refresh, Fullscreen, Settings } from '@mui/icons-material';

// Import components directly to avoid type issues
const NetworkGraph = React.lazy(() => import('./NetworkGraph'));
const Timeline = React.lazy(() => import('./TimelineSimple'));
const GeospatialMap = React.lazy(() => import('./GeospatialMap'));

interface DashboardProps {
  className?: string;
}

interface MetricsData {
  entity_counts: {
    total: number;
    by_type: Record<string, number>;
  };
  relationship_counts: {
    total: number;
    by_type: Record<string, number>;
  };
  activity_timeline: any[];
  data_quality: {
    score: number;
    issues: string[];
  };
  system_stats: {
    last_update: string;
    processing_time: string;
  };
}

const Dashboard: React.FC<DashboardProps> = ({ className }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchMetrics = async () => {
    try {
      setRefreshing(true);
      const response = await fetch('/api/visualization/metrics');
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      }
    } catch (error) {
      console.error('Error fetching metrics:', error);
    } finally {
      setRefreshing(false);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleRefresh = () => {
    fetchMetrics();
  };

  // Metrics cards component
  const MetricsCards = () => (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Total Entities
            </Typography>
            <Typography variant="h4" component="div">
              {metrics?.entity_counts.total || 0}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Across {Object.keys(metrics?.entity_counts.by_type || {}).length} types
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Relationships
            </Typography>
            <Typography variant="h4" component="div">
              {metrics?.relationship_counts.total || 0}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {Object.keys(metrics?.relationship_counts.by_type || {}).length} relationship types
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Data Quality
            </Typography>
            <Typography variant="h4" component="div" color="success.main">
              {Math.round((metrics?.data_quality.score || 0) * 100)}%
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {metrics?.data_quality.issues.length || 0} issues found
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Processing Time
            </Typography>
            <Typography variant="h4" component="div">
              {metrics?.system_stats.processing_time || 'N/A'}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Last update: {metrics?.system_stats.last_update ? 
                new Date(metrics.system_stats.last_update).toLocaleTimeString() : 'Never'}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  if (loading) {
    return (
      <Box className={className} sx={{ p: 3 }}>
        <Typography>Loading dashboard...</Typography>
      </Box>
    );
  }

  return (
    <Box className={className} sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Visual Analytics Dashboard
        </Typography>
        <Box>
          <IconButton onClick={handleRefresh} disabled={refreshing}>
            <Refresh />
          </IconButton>
          <IconButton>
            <Settings />
          </IconButton>
        </Box>
      </Box>

      {/* Metrics Cards */}
      <MetricsCards />

      {/* Navigation Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange} variant="fullWidth">
          <Tab label="Network Analysis" />
          <Tab label="Timeline View" />
          <Tab label="Geographic Distribution" />
          <Tab label="Multi-View" />
        </Tabs>
      </Paper>

      {/* Main Content Area */}
      <Paper sx={{ minHeight: '600px', p: 2 }}>
        {activeTab === 0 && (
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Entity Relationship Network</Typography>
              <IconButton size="small">
                <Fullscreen />
              </IconButton>
            </Box>
            <NetworkGraph />
          </Box>
        )}

        {activeTab === 1 && (
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Entity Discovery Timeline</Typography>
              <IconButton size="small">
                <Fullscreen />
              </IconButton>
            </Box>
            <Timeline />
          </Box>
        )}

        {activeTab === 2 && (
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Geographic Distribution</Typography>
              <IconButton size="small">
                <Fullscreen />
              </IconButton>
            </Box>
            <GeospatialMap />
          </Box>
        )}

        {activeTab === 3 && (
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, height: '400px' }}>
                <Typography variant="h6" gutterBottom>Network Overview</Typography>
                <NetworkGraph height={350} />
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, height: '400px' }}>
                <Typography variant="h6" gutterBottom>Recent Activity</Typography>
                <Timeline height={350} />
              </Paper>
            </Grid>
            <Grid item xs={12}>
              <Paper sx={{ p: 2, height: '300px' }}>
                <Typography variant="h6" gutterBottom>Geographic View</Typography>
                <GeospatialMap height={250} />
              </Paper>
            </Grid>
          </Grid>
        )}
      </Paper>

      {/* Entity Type Distribution */}
      {metrics && (
        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Entity Types</Typography>
              {Object.entries(metrics.entity_counts.by_type).map(([type, count]) => (
                <Box key={type} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                    {type}
                  </Typography>
                  <Typography variant="body2" color="primary">
                    {count}
                  </Typography>
                </Box>
              ))}
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Relationship Types</Typography>
              {Object.entries(metrics.relationship_counts.by_type).map(([type, count]) => (
                <Box key={type} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                    {type.replace('_', ' ')}
                  </Typography>
                  <Typography variant="body2" color="primary">
                    {count}
                  </Typography>
                </Box>
              ))}
            </Paper>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default Dashboard;
