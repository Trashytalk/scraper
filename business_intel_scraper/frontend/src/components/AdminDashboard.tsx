import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  Box,
  Typography,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  Grid
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Storage as StorageIcon,
  Assignment as AssignmentIcon,
  Error as ErrorIcon
} from '@mui/icons-material';

interface Job {
  id: number;
  name: string;
  type: string;
  status: string;
  created_at: string;
  started_at: string;
  completed_at: string;
  error_message: string;
  results_count: number;
  created_by: string;
}

interface DatabaseStats {
  total_jobs: number;
  jobs_by_status: { [key: string]: number };
  total_results: number;
  total_users: number;
  database_size_bytes: number;
  jobs_last_24h: number;
  currently_running: number;
  stuck_jobs: number;
}

interface AdminDashboardProps {
  show: boolean;
  onHide: () => void;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ show, onHide }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (show) {
      loadData();
    }
  }, [show]);

  const loadData = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Load jobs
      const jobsResponse = await fetch('/api/jobs', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (jobsResponse.ok) {
        const jobsData = await jobsResponse.json();
        setJobs(jobsData);
      }

      // Load database stats (this would need a new endpoint)
      try {
        const statsResponse = await fetch('/api/admin/database-stats', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });
        
        if (statsResponse.ok) {
          const statsData = await statsResponse.json();
          setStats(statsData);
        }
      } catch (e) {
        console.warn('Database stats not available');
      }

    } catch (err) {
      setError(`Failed to load data: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const terminateJob = async (jobId: number) => {
    try {
      const response = await fetch(`/api/jobs/${jobId}/terminate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reason: 'Manual termination from admin panel' }),
      });

      if (response.ok) {
        loadData(); // Refresh data
      } else {
        setError(`Failed to terminate job ${jobId}`);
      }
    } catch (err) {
      setError(`Error terminating job: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  const deleteJob = async (jobId: number) => {
    if (!window.confirm(`Are you sure you want to delete job ${jobId}? This cannot be undone.`)) {
      return;
    }

    try {
      const response = await fetch(`/api/jobs/${jobId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        loadData(); // Refresh data
      } else {
        setError(`Failed to delete job ${jobId}`);
      }
    } catch (err) {
      setError(`Error deleting job: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  const getStatusChip = (status: string) => {
    const statusConfig = {
      completed: { color: 'success' as const, icon: '✅' },
      running: { color: 'primary' as const, icon: '🔄' },
      failed: { color: 'error' as const, icon: '❌' },
      pending: { color: 'warning' as const, icon: '⏳' },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || { color: 'default' as const, icon: '❓' };
    
    return (
      <Chip 
        label={`${config.icon} ${status}`} 
        color={config.color} 
        size="small" 
      />
    );
  };

  const runningJobs = jobs.filter(job => job.status === 'running');
  const failedJobs = jobs.filter(job => job.status === 'failed');

  return (
    <Dialog open={show} onClose={onHide} maxWidth="xl" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">
            🛠️ Admin Dashboard
          </Typography>
          <IconButton onClick={loadData} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {stats && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              📊 Database Overview
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Total Jobs
                    </Typography>
                    <Typography variant="h4">
                      {stats.total_jobs}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Running Jobs
                    </Typography>
                    <Typography variant="h4" color="primary">
                      {stats.currently_running}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Total Results
                    </Typography>
                    <Typography variant="h4">
                      {stats.total_results}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Database Size
                    </Typography>
                    <Typography variant="h4">
                      {(stats.database_size_bytes / (1024 * 1024)).toFixed(1)}MB
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}

        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab label={`📋 All Jobs (${jobs.length})`} />
          <Tab label={`🔄 Running (${runningJobs.length})`} />
          <Tab label={`❌ Failed (${failedJobs.length})`} />
        </Tabs>

        <Box sx={{ mt: 2 }}>
          {activeTab === 0 && (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell>Results</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {jobs.map((job) => (
                    <TableRow key={job.id}>
                      <TableCell>{job.id}</TableCell>
                      <TableCell>{job.name}</TableCell>
                      <TableCell>{job.type}</TableCell>
                      <TableCell>{getStatusChip(job.status)}</TableCell>
                      <TableCell>{new Date(job.created_at).toLocaleDateString()}</TableCell>
                      <TableCell>{job.results_count || 0}</TableCell>
                      <TableCell>
                        {job.status === 'running' && (
                          <Tooltip title="Terminate job">
                            <IconButton 
                              size="small" 
                              color="warning"
                              onClick={() => terminateJob(job.id)}
                            >
                              <StopIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                        <Tooltip title="Delete job">
                          <IconButton 
                            size="small" 
                            color="error"
                            onClick={() => deleteJob(job.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {activeTab === 1 && (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Started</TableCell>
                    <TableCell>Results</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {runningJobs.map((job) => (
                    <TableRow key={job.id}>
                      <TableCell>{job.id}</TableCell>
                      <TableCell>{job.name}</TableCell>
                      <TableCell>{new Date(job.started_at).toLocaleString()}</TableCell>
                      <TableCell>{job.results_count || 0}</TableCell>
                      <TableCell>
                        <Tooltip title="Terminate job">
                          <IconButton 
                            size="small" 
                            color="warning"
                            onClick={() => terminateJob(job.id)}
                          >
                            <StopIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {activeTab === 2 && (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Error</TableCell>
                    <TableCell>Failed At</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {failedJobs.map((job) => (
                    <TableRow key={job.id}>
                      <TableCell>{job.id}</TableCell>
                      <TableCell>{job.name}</TableCell>
                      <TableCell>
                        <Typography variant="body2" color="error">
                          {job.error_message?.substring(0, 50)}...
                        </Typography>
                      </TableCell>
                      <TableCell>{new Date(job.completed_at).toLocaleString()}</TableCell>
                      <TableCell>
                        <Tooltip title="Delete job">
                          <IconButton 
                            size="small" 
                            color="error"
                            onClick={() => deleteJob(job.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onHide}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default AdminDashboard;
