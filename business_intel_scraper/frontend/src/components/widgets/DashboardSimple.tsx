import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography, Box, Tab, Tabs, IconButton, Card, CardContent } from '@mui/material';
import { Refresh, Settings } from '@mui/icons-material';

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
          <Tab label="API Testing" />
        </Tabs>
      </Paper>

      {/* Main Content Area */}
      <Paper sx={{ minHeight: '600px', p: 2 }}>
        {activeTab === 0 && (
          <Box>
            <Typography variant="h6" gutterBottom>Entity Relationship Network</Typography>
            <Typography>Network visualization component will be displayed here.</Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
              The NetworkGraph component with Cytoscape.js integration is ready but has TypeScript compatibility issues.
              Once resolved, it will display interactive network graphs with layout controls, zoom, and node interactions.
            </Typography>
          </Box>
        )}

        {activeTab === 1 && (
          <Box>
            <Typography variant="h6" gutterBottom>Entity Discovery Timeline</Typography>
            <Typography>Timeline visualization component will be displayed here.</Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
              The Timeline component with vis.js integration is ready but has TypeScript compatibility issues.
              Once resolved, it will show temporal data with zoom controls, event selection, and group management.
            </Typography>
          </Box>
        )}

        {activeTab === 2 && (
          <Box>
            <Typography variant="h6" gutterBottom>Geographic Distribution</Typography>
            <Typography>Geographic map component will be displayed here.</Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
              The GeospatialMap component with Leaflet integration is ready but has TypeScript compatibility issues.
              Once resolved, it will display interactive maps with markers, clustering, and geographic data.
            </Typography>
          </Box>
        )}

        {activeTab === 3 && (
          <Box>
            <Typography variant="h6" gutterBottom>API Testing Panel</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>Network Data API</Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    GET /api/visualization/network-data
                  </Typography>
                  <button 
                    onClick={() => fetch('/api/visualization/network-data').then(r => r.json()).then(console.log)}
                    style={{ padding: '8px 16px', cursor: 'pointer' }}
                  >
                    Test Network API
                  </button>
                </Paper>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>Timeline Data API</Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    GET /api/visualization/timeline-data
                  </Typography>
                  <button 
                    onClick={() => fetch('/api/visualization/timeline-data').then(r => r.json()).then(console.log)}
                    style={{ padding: '8px 16px', cursor: 'pointer' }}
                  >
                    Test Timeline API
                  </button>
                </Paper>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>Geospatial Data API</Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    GET /api/visualization/geospatial-data
                  </Typography>
                  <button 
                    onClick={() => fetch('/api/visualization/geospatial-data').then(r => r.json()).then(console.log)}
                    style={{ padding: '8px 16px', cursor: 'pointer' }}
                  >
                    Test Geospatial API
                  </button>
                </Paper>
              </Grid>
            </Grid>
          </Box>
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
