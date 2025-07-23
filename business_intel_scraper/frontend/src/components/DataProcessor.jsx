import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  LinearProgress,
  Paper,
  Tabs,
  Tab
} from '@mui/material';
import {
  DataObject,
  CleaningServices,
  Transform,
  Analytics,
  FileDownload,
  Upload,
  PlayArrow,
  Stop,
  Settings
} from '@mui/icons-material';

const DataProcessor = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [datasets, setDatasets] = useState([]);
  const [pipelines, setPipelines] = useState([]);
  const [processingJobs, setProcessingJobs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Mock data
      const mockDatasets = [
        {
          id: 1,
          name: 'News Articles Q3 2025',
          source: 'news_scraper',
          records: 15420,
          size: '45.2 MB',
          format: 'JSON',
          created: '2025-07-20T10:00:00Z',
          status: 'ready'
        },
        {
          id: 2,
          name: 'Business Contacts',
          source: 'business_scraper',
          records: 8930,
          size: '12.1 MB',
          format: 'CSV',
          created: '2025-07-21T14:30:00Z',
          status: 'processing'
        },
        {
          id: 3,
          name: 'Social Media Posts',
          source: 'social_scraper',
          records: 25600,
          size: '78.5 MB',
          format: 'JSON',
          created: '2025-07-22T09:15:00Z',
          status: 'ready'
        }
      ];

      const mockPipelines = [
        {
          id: 1,
          name: 'Text Cleaning & NLP',
          description: 'Clean text, extract entities, sentiment analysis',
          steps: ['cleaning', 'tokenization', 'entity_extraction', 'sentiment'],
          status: 'active'
        },
        {
          id: 2,
          name: 'Data Deduplication',
          description: 'Remove duplicate records and normalize data',
          steps: ['deduplication', 'normalization', 'validation'],
          status: 'active'
        },
        {
          id: 3,
          name: 'Business Intelligence',
          description: 'Extract business insights and metrics',
          steps: ['categorization', 'trend_analysis', 'reporting'],
          status: 'draft'
        }
      ];

      const mockJobs = [
        {
          id: 1,
          name: 'News Article Processing',
          dataset: 'News Articles Q3 2025',
          pipeline: 'Text Cleaning & NLP',
          progress: 75,
          status: 'running',
          started: '2025-07-22T11:00:00Z',
          estimated_completion: '2025-07-22T12:30:00Z'
        },
        {
          id: 2,
          name: 'Contact Deduplication',
          dataset: 'Business Contacts',
          pipeline: 'Data Deduplication',
          progress: 100,
          status: 'completed',
          started: '2025-07-22T10:00:00Z',
          completed: '2025-07-22T10:45:00Z'
        }
      ];

      setDatasets(mockDatasets);
      setPipelines(mockPipelines);
      setProcessingJobs(mockJobs);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const TabPanel = ({ children, value, index, ...other }) => (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  const getStatusColor = (status) => {
    switch (status) {
      case 'ready': return 'success';
      case 'processing': return 'warning';
      case 'running': return 'primary';
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'active': return 'success';
      case 'draft': return 'default';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Data Processing Center
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentTab} onChange={(e, newValue) => setCurrentTab(newValue)}>
          <Tab icon={<DataObject />} label="Datasets" />
          <Tab icon={<Transform />} label="Pipelines" />
          <Tab icon={<Analytics />} label="Processing Jobs" />
        </Tabs>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Datasets Tab */}
      <TabPanel value={currentTab} index={0}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5">Available Datasets</Typography>
          <Box>
            <Button startIcon={<Upload />} sx={{ mr: 2 }}>
              Upload Dataset
            </Button>
            <Button variant="contained" startIcon={<DataObject />}>
              Import from Scraper
            </Button>
          </Box>
        </Box>

        <Grid container spacing={3}>
          {datasets.map((dataset) => (
            <Grid item xs={12} md={6} lg={4} key={dataset.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" component="div">
                      {dataset.name}
                    </Typography>
                    <Chip 
                      label={dataset.status} 
                      color={getStatusColor(dataset.status)}
                      size="small"
                    />
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Source: {dataset.source}
                  </Typography>
                  
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2">
                      <strong>{dataset.records.toLocaleString()}</strong> records
                    </Typography>
                    <Typography variant="body2">
                      Size: <strong>{dataset.size}</strong>
                    </Typography>
                    <Typography variant="body2">
                      Format: <strong>{dataset.format}</strong>
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Created: {new Date(dataset.created).toLocaleDateString()}
                    </Typography>
                  </Box>

                  <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                    <Button size="small" startIcon={<Analytics />}>
                      Process
                    </Button>
                    <Button size="small" startIcon={<FileDownload />}>
                      Export
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      {/* Pipelines Tab */}
      <TabPanel value={currentTab} index={1}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5">Processing Pipelines</Typography>
          <Button variant="contained" startIcon={<Transform />}>
            Create Pipeline
          </Button>
        </Box>

        <Grid container spacing={3}>
          {pipelines.map((pipeline) => (
            <Grid item xs={12} md={6} key={pipeline.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" component="div">
                      {pipeline.name}
                    </Typography>
                    <Chip 
                      label={pipeline.status} 
                      color={getStatusColor(pipeline.status)}
                      size="small"
                    />
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {pipeline.description}
                  </Typography>
                  
                  <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                    Pipeline Steps:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {pipeline.steps.map((step, index) => (
                      <Chip 
                        key={index}
                        label={step.replace('_', ' ')}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                  </Box>

                  <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                    <Button size="small" startIcon={<PlayArrow />}>
                      Run
                    </Button>
                    <Button size="small" startIcon={<Settings />}>
                      Configure
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      {/* Processing Jobs Tab */}
      <TabPanel value={currentTab} index={2}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5">Active Processing Jobs</Typography>
          <Button variant="contained" startIcon={<PlayArrow />}>
            Start New Job
          </Button>
        </Box>

        <Grid container spacing={3}>
          {processingJobs.map((job) => (
            <Grid item xs={12} key={job.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Box>
                      <Typography variant="h6" component="div">
                        {job.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Dataset: {job.dataset} | Pipeline: {job.pipeline}
                      </Typography>
                    </Box>
                    <Chip 
                      label={job.status} 
                      color={getStatusColor(job.status)}
                      size="small"
                    />
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ width: '100%', mr: 1 }}>
                      <LinearProgress 
                        variant="determinate" 
                        value={job.progress}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                    <Box sx={{ minWidth: 35 }}>
                      <Typography variant="body2" color="text.secondary">
                        {job.progress}%
                      </Typography>
                    </Box>
                  </Box>

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                      <Typography variant="body2">
                        Started: {new Date(job.started).toLocaleString()}
                      </Typography>
                      {job.estimated_completion && (
                        <Typography variant="body2" color="text.secondary">
                          Est. completion: {new Date(job.estimated_completion).toLocaleString()}
                        </Typography>
                      )}
                      {job.completed && (
                        <Typography variant="body2" color="success.main">
                          Completed: {new Date(job.completed).toLocaleString()}
                        </Typography>
                      )}
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      {job.status === 'running' ? (
                        <Button size="small" startIcon={<Stop />} color="warning">
                          Stop
                        </Button>
                      ) : (
                        <Button size="small" startIcon={<PlayArrow />}>
                          Restart
                        </Button>
                      )}
                      <Button size="small" startIcon={<FileDownload />}>
                        Download Results
                      </Button>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>
    </Box>
  );
};

export default DataProcessor;
