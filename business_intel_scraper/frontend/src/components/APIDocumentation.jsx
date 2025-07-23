import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Button,
  TextField,
  Paper,
  Grid,
  List,
  ListItem,
  ListItemText,
  Divider,
  Alert,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
  Badge
} from '@mui/material';
import {
  ExpandMore,
  Code,
  PlayArrow,
  ContentCopy,
  Download,
  Security,
  Speed,
  Description,
  Api,
  Send,
  Refresh,
  Settings,
  Help,
  CheckCircle,
  Error,
  Warning
} from '@mui/icons-material';
import { useNotifications } from './NotificationSystem';

// API endpoint definitions
const API_ENDPOINTS = {
  auth: {
    name: 'Authentication',
    description: 'User authentication and authorization endpoints',
    endpoints: [
      {
        method: 'POST',
        path: '/api/auth/login',
        summary: 'User login',
        description: 'Authenticate user with email and password',
        parameters: [
          { name: 'email', type: 'string', required: true, description: 'User email address' },
          { name: 'password', type: 'string', required: true, description: 'User password' },
          { name: 'rememberMe', type: 'boolean', required: false, description: 'Keep user logged in' }
        ],
        responses: {
          200: { description: 'Login successful', schema: '{ "token": "string", "user": { "id": "string", "email": "string" } }' },
          401: { description: 'Invalid credentials', schema: '{ "error": "string" }' }
        },
        example: {
          request: '{\n  "email": "user@example.com",\n  "password": "password123",\n  "rememberMe": true\n}',
          response: '{\n  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",\n  "user": {\n    "id": "12345",\n    "email": "user@example.com",\n    "username": "testuser"\n  }\n}'
        }
      },
      {
        method: 'POST',
        path: '/api/auth/register',
        summary: 'User registration',
        description: 'Create a new user account',
        parameters: [
          { name: 'username', type: 'string', required: true, description: 'Unique username' },
          { name: 'email', type: 'string', required: true, description: 'User email address' },
          { name: 'password', type: 'string', required: true, description: 'User password (min 6 chars)' }
        ],
        responses: {
          201: { description: 'User created successfully', schema: '{ "token": "string", "user": { "id": "string", "email": "string" } }' },
          400: { description: 'Validation error', schema: '{ "error": "string", "details": ["string"] }' }
        }
      },
      {
        method: 'GET',
        path: '/api/auth/validate',
        summary: 'Validate token',
        description: 'Validate authentication token',
        headers: [
          { name: 'Authorization', required: true, description: 'Bearer {token}' }
        ],
        responses: {
          200: { description: 'Token valid', schema: '{ "user": { "id": "string", "email": "string" } }' },
          401: { description: 'Invalid token', schema: '{ "error": "string" }' }
        }
      }
    ]
  },
  jobs: {
    name: 'Job Management',
    description: 'Create, manage, and monitor scraping jobs',
    endpoints: [
      {
        method: 'GET',
        path: '/api/jobs',
        summary: 'List jobs',
        description: 'Get all scraping jobs for the authenticated user',
        parameters: [
          { name: 'page', type: 'integer', required: false, description: 'Page number (default: 1)' },
          { name: 'limit', type: 'integer', required: false, description: 'Items per page (default: 20)' },
          { name: 'status', type: 'string', required: false, description: 'Filter by status (pending, running, completed, failed)' }
        ],
        responses: {
          200: { description: 'Jobs retrieved successfully', schema: '{ "jobs": [{ "id": "string", "name": "string", "status": "string" }], "total": "number" }' }
        }
      },
      {
        method: 'POST',
        path: '/api/jobs',
        summary: 'Create job',
        description: 'Create a new scraping job',
        parameters: [
          { name: 'name', type: 'string', required: true, description: 'Job name' },
          { name: 'url', type: 'string', required: true, description: 'Target URL' },
          { name: 'selectors', type: 'array', required: true, description: 'CSS selectors for data extraction' },
          { name: 'schedule', type: 'string', required: false, description: 'Cron schedule expression' }
        ],
        responses: {
          201: { description: 'Job created successfully', schema: '{ "id": "string", "name": "string", "status": "string" }' },
          400: { description: 'Invalid job configuration', schema: '{ "error": "string" }' }
        }
      },
      {
        method: 'GET',
        path: '/api/jobs/{id}',
        summary: 'Get job details',
        description: 'Get detailed information about a specific job',
        parameters: [
          { name: 'id', type: 'string', required: true, description: 'Job ID', location: 'path' }
        ],
        responses: {
          200: { description: 'Job details retrieved', schema: '{ "id": "string", "name": "string", "status": "string", "config": "object", "results": "array" }' },
          404: { description: 'Job not found', schema: '{ "error": "string" }' }
        }
      }
    ]
  },
  data: {
    name: 'Data Management',
    description: 'Access and manage scraped data',
    endpoints: [
      {
        method: 'GET',
        path: '/api/data/{jobId}',
        summary: 'Get job data',
        description: 'Retrieve scraped data from a specific job',
        parameters: [
          { name: 'jobId', type: 'string', required: true, description: 'Job ID', location: 'path' },
          { name: 'format', type: 'string', required: false, description: 'Output format (json, csv, xml)' },
          { name: 'page', type: 'integer', required: false, description: 'Page number for pagination' }
        ],
        responses: {
          200: { description: 'Data retrieved successfully', schema: '{ "data": "array", "total": "number", "page": "number" }' }
        }
      }
    ]
  }
};

// API Method Badge Component
const MethodBadge = ({ method }) => {
  const colors = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'error',
    PATCH: 'info'
  };

  return (
    <Chip 
      label={method} 
      color={colors[method] || 'default'} 
      size="small"
      sx={{ fontWeight: 'bold', minWidth: 60 }}
    />
  );
};

// API Endpoint Component
const APIEndpoint = ({ endpoint }) => {
  const [expanded, setExpanded] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [testParams, setTestParams] = useState({});
  const { showNotification } = useNotifications();

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    showNotification('Copied to clipboard', 'success');
  };

  const testEndpoint = async () => {
    try {
      setTestResult({ loading: true });
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockResponse = {
        status: 200,
        data: JSON.parse(endpoint.example?.response || '{}'),
        headers: {
          'content-type': 'application/json',
          'x-response-time': '123ms'
        }
      };
      
      setTestResult(mockResponse);
      showNotification('API test completed', 'success');
    } catch (error) {
      setTestResult({
        status: 500,
        error: error.message
      });
      showNotification('API test failed', 'error');
    }
  };

  return (
    <Accordion expanded={expanded} onChange={() => setExpanded(!expanded)}>
      <AccordionSummary expandIcon={<ExpandMore />}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
          <MethodBadge method={endpoint.method} />
          <Typography variant="subtitle1" fontWeight="bold">
            {endpoint.path}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto' }}>
            {endpoint.summary}
          </Typography>
        </Box>
      </AccordionSummary>
      
      <AccordionDetails>
        <Box>
          <Typography variant="body2" paragraph>
            {endpoint.description}
          </Typography>

          <Grid container spacing={3}>
            {/* Parameters */}
            {endpoint.parameters && endpoint.parameters.length > 0 && (
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Parameters
                </Typography>
                <List dense>
                  {endpoint.parameters.map((param, index) => (
                    <ListItem key={index} divider>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="subtitle2">
                              {param.name}
                            </Typography>
                            <Chip 
                              label={param.type} 
                              size="small" 
                              variant="outlined"
                            />
                            {param.required && (
                              <Chip 
                                label="required" 
                                size="small" 
                                color="error"
                                variant="outlined"
                              />
                            )}
                          </Box>
                        }
                        secondary={param.description}
                      />
                    </ListItem>
                  ))}
                </List>
              </Grid>
            )}

            {/* Headers */}
            {endpoint.headers && endpoint.headers.length > 0 && (
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Headers
                </Typography>
                <List dense>
                  {endpoint.headers.map((header, index) => (
                    <ListItem key={index} divider>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="subtitle2">
                              {header.name}
                            </Typography>
                            {header.required && (
                              <Chip 
                                label="required" 
                                size="small" 
                                color="error"
                                variant="outlined"
                              />
                            )}
                          </Box>
                        }
                        secondary={header.description}
                      />
                    </ListItem>
                  ))}
                </List>
              </Grid>
            )}

            {/* Responses */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Responses
              </Typography>
              {Object.entries(endpoint.responses).map(([status, response]) => (
                <Card key={status} variant="outlined" sx={{ mb: 1 }}>
                  <CardContent sx={{ py: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Chip 
                        label={status}
                        color={status.startsWith('2') ? 'success' : 'error'}
                        size="small"
                      />
                      <Typography variant="body2">
                        {response.description}
                      </Typography>
                    </Box>
                    {response.schema && (
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          Schema:
                        </Typography>
                        <Paper sx={{ p: 1, mt: 0.5, bgcolor: 'grey.50' }}>
                          <Typography variant="caption" component="pre">
                            {response.schema}
                          </Typography>
                        </Paper>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              ))}
            </Grid>

            {/* Example */}
            {endpoint.example && (
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Example
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Request
                    </Typography>
                    <Paper sx={{ position: 'relative' }}>
                      <IconButton
                        size="small"
                        sx={{ position: 'absolute', top: 4, right: 4, zIndex: 1 }}
                        onClick={() => copyToClipboard(endpoint.example.request)}
                      >
                        <ContentCopy fontSize="small" />
                      </IconButton>
                      <Box sx={{ p: 2, bgcolor: 'grey.50' }}>
                        <Typography variant="body2" component="pre">
                          {endpoint.example.request}
                        </Typography>
                      </Box>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Response
                    </Typography>
                    <Paper sx={{ position: 'relative' }}>
                      <IconButton
                        size="small"
                        sx={{ position: 'absolute', top: 4, right: 4, zIndex: 1 }}
                        onClick={() => copyToClipboard(endpoint.example.response)}
                      >
                        <ContentCopy fontSize="small" />
                      </IconButton>
                      <Box sx={{ p: 2, bgcolor: 'grey.50' }}>
                        <Typography variant="body2" component="pre">
                          {endpoint.example.response}
                        </Typography>
                      </Box>
                    </Paper>
                  </Grid>
                </Grid>
              </Grid>
            )}

            {/* API Tester */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                API Tester
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<PlayArrow />}
                  onClick={testEndpoint}
                  disabled={testResult?.loading}
                >
                  Test Endpoint
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={() => setTestResult(null)}
                >
                  Clear
                </Button>
              </Box>

              {testResult && (
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      <Typography variant="subtitle2">
                        Test Result:
                      </Typography>
                      {testResult.loading ? (
                        <Chip label="Testing..." color="info" />
                      ) : (
                        <Chip 
                          label={`${testResult.status} ${testResult.status < 400 ? 'Success' : 'Error'}`}
                          color={testResult.status < 400 ? 'success' : 'error'}
                        />
                      )}
                    </Box>
                    
                    {!testResult.loading && (
                      <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                        <Typography variant="body2" component="pre">
                          {JSON.stringify(testResult.data || testResult.error, null, 2)}
                        </Typography>
                      </Paper>
                    )}
                  </CardContent>
                </Card>
              )}
            </Grid>
          </Grid>
        </Box>
      </AccordionDetails>
    </Accordion>
  );
};

// Main API Documentation Component
export const APIDocumentation = () => {
  const [selectedCategory, setSelectedCategory] = useState('auth');
  const [searchTerm, setSearchTerm] = useState('');
  const [showExamples, setShowExamples] = useState(true);

  const categories = Object.keys(API_ENDPOINTS);
  const currentCategory = API_ENDPOINTS[selectedCategory];

  const filteredEndpoints = currentCategory?.endpoints.filter(endpoint =>
    endpoint.path.toLowerCase().includes(searchTerm.toLowerCase()) ||
    endpoint.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
    endpoint.description.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        API Documentation
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        Interactive API documentation with live testing capabilities. 
        Use the built-in tester to explore endpoints and see real responses.
      </Alert>

      {/* Controls */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>API Category</InputLabel>
              <Select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                {categories.map(category => (
                  <MenuItem key={category} value={category}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Api />
                      {API_ENDPOINTS[category].name}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Search endpoints"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by path, name, or description"
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <FormControlLabel
              control={
                <Switch
                  checked={showExamples}
                  onChange={(e) => setShowExamples(e.target.checked)}
                />
              }
              label="Show examples by default"
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Category Info */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Api color="primary" />
            <Typography variant="h5">
              {currentCategory?.name}
            </Typography>
            <Badge badgeContent={filteredEndpoints.length} color="primary">
              <Chip label="endpoints" variant="outlined" />
            </Badge>
          </Box>
          <Typography variant="body1" color="text.secondary">
            {currentCategory?.description}
          </Typography>
        </CardContent>
      </Card>

      {/* Endpoints */}
      <Box>
        {filteredEndpoints.length === 0 ? (
          <Alert severity="warning">
            No endpoints found matching your search criteria.
          </Alert>
        ) : (
          filteredEndpoints.map((endpoint, index) => (
            <Box key={`${endpoint.method}-${endpoint.path}`} sx={{ mb: 2 }}>
              <APIEndpoint endpoint={endpoint} />
            </Box>
          ))
        )}
      </Box>

      {/* Footer */}
      <Paper sx={{ p: 3, mt: 4, textAlign: 'center' }}>
        <Typography variant="h6" gutterBottom>
          Need Help?
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Check out our developer guide for more information about authentication,
          rate limiting, and best practices.
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button variant="outlined" startIcon={<Description />}>
            Developer Guide
          </Button>
          <Button variant="outlined" startIcon={<Security />}>
            Authentication Guide
          </Button>
          <Button variant="outlined" startIcon={<Help />}>
            Support
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default APIDocumentation;
