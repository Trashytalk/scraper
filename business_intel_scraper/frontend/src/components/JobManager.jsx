import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  IconButton,
  Tooltip,
  LinearProgress,
  Badge,
  Alert,
  Collapse,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Delete,
  Refresh,
  Add,
  Visibility,
  ExpandMore,
  ExpandLess,
  Download,
  Upload,
  Schedule,
  Settings,
  Error,
  Pause
} from '@mui/icons-material';
import { useJobs } from '../contexts/JobContext';
import { useJobNotifications } from './NotificationSystem';
import SearchAndFilter from './SearchAndFilter';
import ExportImportManager from './ExportImportManager';

const JobManager = () => {
  const { 
    jobs, 
    loading, 
    error,
    startJob, 
    stopJob, 
    deleteJob, 
    createJob, 
    getJobStats,
    loadJobLogs,
    getJobData,
    refreshJobs,
    clearError,
    JOB_STATUS 
  } = useJobs();

  const {
    notifyJobStarted,
    notifyJobCompleted,
    notifyJobFailed,
    notifyJobCancelled,
    notifyJobError,
    notifyJobSuccess
  } = useJobNotifications();
  
  const [createJobOpen, setCreateJobOpen] = useState(false);
  const [jobDetailsOpen, setJobDetailsOpen] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [expandedJobs, setExpandedJobs] = useState(new Set());
  const [jobLogs, setJobLogs] = useState({});
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [showExportImport, setShowExportImport] = useState(false);
  const [newJob, setNewJob] = useState({
    name: '',
    url: '',
    scraper_type: 'beautiful_soup',
    schedule: 'manual',
    config: {}
  });
  const [formErrors, setFormErrors] = useState({});

  // Filter configuration for jobs
  const jobFilterConfig = {
    status: {
      type: 'select',
      label: 'Status',
      options: ['pending', 'running', 'completed', 'failed', 'cancelled'],
      icon: <Schedule />
    },
    scraper_type: {
      type: 'multiSelect',
      label: 'Scraper Type',
      options: ['beautiful_soup', 'scrapy', 'selenium', 'playwright'],
      icon: <Settings />
    },
    dateRange: {
      type: 'dateRange',
      label: 'Date Range',
    }
  };

  useEffect(() => {
    if (jobs.length > 0 && filteredJobs.length === 0) {
      setFilteredJobs(jobs);
    }
  }, [jobs, filteredJobs.length]);

  const validateJobForm = () => {
    const errors = {};
    
    if (!newJob.name.trim()) {
      errors.name = 'Job name is required';
    } else if (newJob.name.length < 3) {
      errors.name = 'Job name must be at least 3 characters';
    }
    
    if (!newJob.url.trim()) {
      errors.url = 'URL is required';
    } else {
      try {
        new URL(newJob.url);
      } catch {
        errors.url = 'Please enter a valid URL';
      }
    }
    
    if (!newJob.scraper_type) {
      errors.scraper_type = 'Please select a scraper type';
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleCreateJob = async () => {
    if (!validateJobForm()) {
      return;
    }

    try {
      await createJob({
        name: newJob.name,
        url: newJob.url,
        scraper_type: newJob.scraper_type,
        schedule: 'manual',
        config: {}
      });
      
      notifyJobSuccess(`Job "${newJob.name}" created successfully`);
      
    } catch (error) {
      console.error('Failed to create job:', error);
      
      // Set form errors based on API response
      if (error.response?.status === 422) {
        const detail = error.response.data?.detail;
        if (typeof detail === 'string') {
          if (detail.includes('name')) {
            setFormErrors({ name: detail });
          } else if (detail.includes('URL')) {
            setFormErrors({ url: detail });
          } else if (detail.includes('scraper')) {
            setFormErrors({ scraper_type: detail });
          } else {
            setFormErrors({ general: detail });
          }
        } else if (Array.isArray(detail)) {
          const fieldErrors = {};
          detail.forEach(err => {
            if (err.loc && err.loc.length > 1) {
              fieldErrors[err.loc[1]] = err.msg;
            }
          });
          setFormErrors(fieldErrors);
        } else {
          setFormErrors({ general: 'Validation failed. Please check your input.' });
        }
      } else {
        setFormErrors({ general: error.message || 'Failed to create job' });
      }
      return;
    }

    // Reset form on success
    setNewJob({
      name: '',
      url: '',
      scraper_type: 'beautiful_soup',
      schedule: 'manual',
      config: {}
    });
    setFormErrors({});
    setCreateJobOpen(false);
  };

  const handleStartJob = async (jobId) => {
    try {
      const jobToStart = jobs.find(j => j.id === jobId);
      if (!jobToStart) {
        throw new Error('Job not found');
      }
      
      if (jobToStart.status === JOB_STATUS.RUNNING) {
        notifyJobError('Job is already running');
        return;
      }
      
      await startJob(jobId);
      notifyJobStarted(jobToStart.name, `Job started at ${new Date().toLocaleTimeString()}`);
      
    } catch (error) {
      console.error('Failed to start job:', error);
      const message = error.message || 'Failed to start job. Please try again.';
      notifyJobError(message);
    }
  };

  const handleStopJob = async (jobId) => {
    try {
      const jobToStop = jobs.find(j => j.id === jobId);
      if (!jobToStop) {
        throw new Error('Job not found');
      }
      
      if (jobToStop.status !== JOB_STATUS.RUNNING && jobToStop.status !== JOB_STATUS.PENDING) {
        notifyJobError('Job is not currently running');
        return;
      }
      
      await stopJob(jobId);
      notifyJobCancelled(jobToStop.name, `Job stopped at ${new Date().toLocaleTimeString()}`);
      
    } catch (error) {
      console.error('Failed to stop job:', error);
      const message = error.message || 'Failed to stop job. Please try again.';
      notifyJobError(message);
    }
  };

  const handleDeleteJob = async (jobId) => {
    try {
      if (!jobId || typeof jobId !== 'number') {
        throw new Error('Invalid job ID');
      }

      const jobToDelete = jobs.find(j => j.id === jobId);
      if (!jobToDelete) {
        throw new Error('Job not found');
      }

      // Check if job is running and ask for confirmation
      if (jobToDelete.status === JOB_STATUS.RUNNING) {
        if (!window.confirm('This job is currently running. Do you want to stop and delete it?')) {
          return;
        }
        
        try {
          await stopJob(jobId);
        } catch (stopError) {
          console.warn('Failed to stop job before deletion:', stopError);
        }
      } else {
        if (!window.confirm('Are you sure you want to delete this job? This action cannot be undone.')) {
          return;
        }
      }
      
      await deleteJob(jobId);
      
      notifyJobSuccess(`Job "${jobToDelete?.name || jobId}" deleted successfully`);
      
      // Clean up local state
      setJobLogs(prev => {
        const updated = { ...prev };
        delete updated[jobId];
        return updated;
      });
      
      setExpandedJobs(prev => {
        const updated = new Set(prev);
        updated.delete(jobId);
        return updated;
      });
      
    } catch (error) {
      console.error('Failed to delete job:', error);
      const message = error.message || 'Failed to delete job. Please try again.';
      notifyJobError(message);
    }
  };

  const handleToggleExpanded = async (jobId) => {
    const newExpanded = new Set(expandedJobs);
    
    if (newExpanded.has(jobId)) {
      newExpanded.delete(jobId);
    } else {
      newExpanded.add(jobId);
      
      // Load logs if not already loaded
      if (!jobLogs[jobId]) {
        try {
          const logs = await loadJobLogs(jobId);
          setJobLogs(prev => ({
            ...prev,
            [jobId]: logs
          }));
        } catch (error) {
          console.error('Failed to load job logs:', error);
        }
      }
    }
    
    setExpandedJobs(newExpanded);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case JOB_STATUS.RUNNING:
        return 'primary';
      case JOB_STATUS.COMPLETED:
        return 'success';
      case JOB_STATUS.FAILED:
        return 'error';
      case JOB_STATUS.PENDING:
        return 'warning';
      case JOB_STATUS.CANCELLED:
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case JOB_STATUS.RUNNING:
        return <PlayArrow color="primary" />;
      case JOB_STATUS.COMPLETED:
        return <Visibility color="success" />;
      case JOB_STATUS.FAILED:
        return <Error color="error" />;
      case JOB_STATUS.PENDING:
        return <Pause color="warning" />;
      case JOB_STATUS.CANCELLED:
        return <Stop color="action" />;
      default:
        return <Schedule color="action" />;
    }
  };

  const handleFilteredDataChange = (filtered) => {
    setFilteredJobs(filtered);
  };

  // Calculate stats from filtered jobs
  const filteredStats = {
    total: filteredJobs.length,
    running: filteredJobs.filter(job => job.status === JOB_STATUS.RUNNING).length,
    completed: filteredJobs.filter(job => job.status === JOB_STATUS.COMPLETED).length,
    failed: filteredJobs.filter(job => job.status === JOB_STATUS.FAILED).length,
    pending: filteredJobs.filter(job => job.status === JOB_STATUS.PENDING).length
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Job Manager
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={() => setShowExportImport(true)}
          >
            Export/Import
          </Button>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={refreshJobs}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setCreateJobOpen(true)}
          >
            Create Job
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 2 }}
          onClose={clearError}
        >
          {error}
        </Alert>
      )}

      {/* Loading Progress */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="h6">
                Total Jobs
              </Typography>
              <Typography variant="h4">
                {filteredStats.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="h6">
                Running
              </Typography>
              <Typography variant="h4" color="primary">
                {filteredStats.running}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="h6">
                Completed
              </Typography>
              <Typography variant="h4" color="success.main">
                {filteredStats.completed}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="h6">
                Failed
              </Typography>
              <Typography variant="h4" color="error.main">
                {filteredStats.failed}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="h6">
                Pending
              </Typography>
              <Typography variant="h4" color="warning.main">
                {filteredStats.pending}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search and Filter */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <SearchAndFilter
            data={jobs}
            onFilteredDataChange={handleFilteredDataChange}
            placeholder="Search jobs by name, URL, or type..."
            searchFields={['name', 'url', 'scraper_type']}
            filterConfig={jobFilterConfig}
          />
        </CardContent>
      </Card>

      {/* Running Jobs Alert */}
      {filteredStats.running > 0 && (
        <Alert severity="info" sx={{ mb: 2 }}>
          You have {filteredStats.running} job{filteredStats.running !== 1 ? 's' : ''} currently running.
          <Button size="small" onClick={refreshJobs} sx={{ ml: 2 }}>
            Refresh Status
          </Button>
        </Alert>
      )}

      {/* Jobs Table */}
      <Card>
        <CardContent>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>URL</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredJobs.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography variant="body2" color="textSecondary">
                        {jobs.length === 0 ? 'No jobs created yet' : 'No jobs match your filters'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredJobs.map((job) => (
                    <React.Fragment key={job.id}>
                      <TableRow>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {getStatusIcon(job.status)}
                            <Typography variant="body2" fontWeight="medium">
                              {job.name}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography 
                            variant="body2" 
                            sx={{ 
                              maxWidth: 200, 
                              overflow: 'hidden', 
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap'
                            }}
                          >
                            {job.url}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={job.scraper_type} 
                            size="small" 
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={job.status} 
                            color={getStatusColor(job.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {new Date(job.created_at).toLocaleDateString()}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            {job.status === JOB_STATUS.RUNNING ? (
                              <Tooltip title="Stop Job">
                                <IconButton
                                  size="small"
                                  onClick={() => handleStopJob(job.id)}
                                  color="warning"
                                >
                                  <Stop />
                                </IconButton>
                              </Tooltip>
                            ) : (
                              <Tooltip title="Start Job">
                                <IconButton
                                  size="small"
                                  onClick={() => handleStartJob(job.id)}
                                  color="primary"
                                  disabled={job.status === JOB_STATUS.RUNNING}
                                >
                                  <PlayArrow />
                                </IconButton>
                              </Tooltip>
                            )}
                            
                            <Tooltip title="View Details">
                              <IconButton
                                size="small"
                                onClick={() => handleToggleExpanded(job.id)}
                              >
                                {expandedJobs.has(job.id) ? <ExpandLess /> : <ExpandMore />}
                              </IconButton>
                            </Tooltip>
                            
                            <Tooltip title="Delete Job">
                              <IconButton
                                size="small"
                                onClick={() => handleDeleteJob(job.id)}
                                color="error"
                              >
                                <Delete />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                      
                      {/* Expanded Row */}
                      <TableRow>
                        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
                          <Collapse in={expandedJobs.has(job.id)} timeout="auto" unmountOnExit>
                            <Box sx={{ margin: 1 }}>
                              <Typography variant="h6" gutterBottom component="div">
                                Job Details
                              </Typography>
                              
                              <Grid container spacing={2}>
                                <Grid item xs={12} md={6}>
                                  <Typography variant="subtitle2">Configuration:</Typography>
                                  <pre style={{ fontSize: '12px', overflow: 'auto' }}>
                                    {JSON.stringify(job.config || {}, null, 2)}
                                  </pre>
                                </Grid>
                                
                                <Grid item xs={12} md={6}>
                                  <Typography variant="subtitle2">Recent Logs:</Typography>
                                  {jobLogs[job.id] ? (
                                    <List dense>
                                      {jobLogs[job.id].slice(-5).map((log, index) => (
                                        <ListItem key={index}>
                                          <ListItemText
                                            primary={log.message}
                                            secondary={new Date(log.timestamp).toLocaleString()}
                                          />
                                        </ListItem>
                                      ))}
                                    </List>
                                  ) : (
                                    <Typography variant="body2" color="textSecondary">
                                      No logs available
                                    </Typography>
                                  )}
                                </Grid>
                              </Grid>
                            </Box>
                          </Collapse>
                        </TableCell>
                      </TableRow>
                    </React.Fragment>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Create Job Dialog */}
      <Dialog open={createJobOpen} onClose={() => setCreateJobOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Job</DialogTitle>
        <DialogContent>
          {formErrors.general && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {formErrors.general}
            </Alert>
          )}
          
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Job Name"
                value={newJob.name}
                onChange={(e) => setNewJob(prev => ({ ...prev, name: e.target.value }))}
                error={!!formErrors.name}
                helperText={formErrors.name}
                placeholder="e.g., News Scraper"
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Target URL"
                value={newJob.url}
                onChange={(e) => setNewJob(prev => ({ ...prev, url: e.target.value }))}
                error={!!formErrors.url}
                helperText={formErrors.url}
                placeholder="https://example.com"
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormControl fullWidth error={!!formErrors.scraper_type}>
                <InputLabel>Scraper Type</InputLabel>
                <Select
                  value={newJob.scraper_type}
                  label="Scraper Type"
                  onChange={(e) => setNewJob(prev => ({ ...prev, scraper_type: e.target.value }))}
                >
                  <MenuItem value="beautiful_soup">Beautiful Soup</MenuItem>
                  <MenuItem value="scrapy">Scrapy</MenuItem>
                  <MenuItem value="selenium">Selenium</MenuItem>
                  <MenuItem value="playwright">Playwright</MenuItem>
                </Select>
                {formErrors.scraper_type && (
                  <Typography variant="caption" color="error" sx={{ mt: 1 }}>
                    {formErrors.scraper_type}
                  </Typography>
                )}
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateJobOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateJob} variant="contained">
            Create Job
          </Button>
        </DialogActions>
      </Dialog>

      {/* Export/Import Dialog */}
      <Dialog open={showExportImport} onClose={() => setShowExportImport(false)} maxWidth="lg" fullWidth>
        <DialogTitle>Export / Import Jobs</DialogTitle>
        <DialogContent>
          <ExportImportManager
            data={jobs}
            dataType="jobs"
            onImportComplete={(importedJobs) => {
              // Refresh jobs after import
              refreshJobs();
              setShowExportImport(false);
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowExportImport(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default JobManager;
