import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  TextField,
  Tabs,
  Tab,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  LinearProgress
} from '@mui/material';
import {
  Search,
  Security,
  Language,
  Email,
  Phone,
  Business,
  Person,
  LocationOn,
  Visibility,
  Download,
  Share,
  Warning,
  CheckCircle
} from '@mui/icons-material';

const OSINTCenter = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('domain');
  const [investigations, setInvestigations] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [createInvestigationOpen, setCreateInvestigationOpen] = useState(false);

  const searchTypes = [
    { value: 'domain', label: 'Domain Intelligence', icon: <Language /> },
    { value: 'email', label: 'Email Investigation', icon: <Email /> },
    { value: 'phone', label: 'Phone Number Lookup', icon: <Phone /> },
    { value: 'company', label: 'Company Research', icon: <Business /> },
    { value: 'person', label: 'Person Search', icon: <Person /> },
    { value: 'ip', label: 'IP Address Analysis', icon: <Security /> }
  ];

  useEffect(() => {
    fetchInvestigations();
  }, []);

  const fetchInvestigations = async () => {
    try {
      // Mock data
      const mockInvestigations = [
        {
          id: 1,
          name: 'Competitor Analysis - TechCorp',
          target: 'techcorp.com',
          type: 'domain',
          status: 'completed',
          created: '2025-07-22T09:00:00Z',
          findings: 15,
          risk_level: 'medium'
        },
        {
          id: 2,
          name: 'Executive Background Check',
          target: 'john.doe@example.com',
          type: 'email',
          status: 'running',
          created: '2025-07-22T10:30:00Z',
          findings: 8,
          risk_level: 'low'
        },
        {
          id: 3,
          name: 'Vendor Security Assessment',
          target: '192.168.1.100',
          type: 'ip',
          status: 'pending',
          created: '2025-07-22T11:15:00Z',
          findings: 0,
          risk_level: 'unknown'
        }
      ];
      setInvestigations(mockInvestigations);
    } catch (error) {
      console.error('Failed to fetch investigations:', error);
    }
  };

  const performSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    try {
      // Mock search results
      const mockResults = [
        {
          source: 'WHOIS Database',
          data: {
            domain: searchQuery,
            registrar: 'Example Registrar Inc.',
            created: '2020-01-15',
            expires: '2026-01-15',
            status: 'Active'
          },
          confidence: 95
        },
        {
          source: 'DNS Records',
          data: {
            a_records: ['192.168.1.1', '192.168.1.2'],
            mx_records: ['mail.example.com'],
            ns_records: ['ns1.example.com', 'ns2.example.com']
          },
          confidence: 100
        },
        {
          source: 'Social Media Scan',
          data: {
            platforms: ['LinkedIn', 'Twitter', 'Facebook'],
            mentions: 142,
            sentiment: 'Neutral'
          },
          confidence: 78
        },
        {
          source: 'Security Scan',
          data: {
            ssl_certificate: 'Valid',
            vulnerabilities: 2,
            security_grade: 'B+'
          },
          confidence: 88
        }
      ];
      setSearchResults(mockResults);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const TabPanel = ({ children, value, index, ...other }) => (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'primary';
      case 'pending': return 'warning';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        OSINT Intelligence Center
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        <strong>Legal Notice:</strong> All OSINT activities must comply with applicable laws and regulations. 
        Only gather intelligence from publicly available sources.
      </Alert>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentTab} onChange={(e, newValue) => setCurrentTab(newValue)}>
          <Tab icon={<Search />} label="Intelligence Search" />
          <Tab icon={<Security />} label="Active Investigations" />
          <Tab icon={<Warning />} label="Threat Intelligence" />
        </Tabs>
      </Box>

      {/* Intelligence Search Tab */}
      <TabPanel value={currentTab} index={0}>
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Open Source Intelligence Search
            </Typography>
            
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Search Type</InputLabel>
                  <Select
                    value={searchType}
                    onChange={(e) => setSearchType(e.target.value)}
                    label="Search Type"
                  >
                    {searchTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {type.icon}
                          {type.label}
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={7}>
                <TextField
                  fullWidth
                  label="Search Target"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Enter domain, email, IP address, etc."
                  onKeyPress={(e) => e.key === 'Enter' && performSearch()}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <Button
                  variant="contained"
                  fullWidth
                  onClick={performSearch}
                  disabled={loading || !searchQuery.trim()}
                  startIcon={<Search />}
                >
                  Search
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {loading && <LinearProgress sx={{ mb: 2 }} />}

        {searchResults.length > 0 && (
          <Grid container spacing={3}>
            {searchResults.map((result, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6">{result.source}</Typography>
                      <Chip 
                        label={`${result.confidence}% confidence`}
                        color={result.confidence > 90 ? 'success' : result.confidence > 70 ? 'warning' : 'default'}
                        size="small"
                      />
                    </Box>
                    
                    <Box>
                      {Object.entries(result.data).map(([key, value]) => (
                        <Typography key={key} variant="body2" sx={{ mb: 1 }}>
                          <strong>{key.replace('_', ' ').toUpperCase()}:</strong>{' '}
                          {Array.isArray(value) ? value.join(', ') : value}
                        </Typography>
                      ))}
                    </Box>

                    <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                      <Button size="small" startIcon={<Visibility />}>
                        Details
                      </Button>
                      <Button size="small" startIcon={<Download />}>
                        Export
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </TabPanel>

      {/* Active Investigations Tab */}
      <TabPanel value={currentTab} index={1}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5">Active Investigations</Typography>
          <Button
            variant="contained"
            startIcon={<Security />}
            onClick={() => setCreateInvestigationOpen(true)}
          >
            New Investigation
          </Button>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Investigation Name</TableCell>
                <TableCell>Target</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Findings</TableCell>
                <TableCell>Risk Level</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {investigations.map((investigation) => (
                <TableRow key={investigation.id}>
                  <TableCell>{investigation.name}</TableCell>
                  <TableCell>{investigation.target}</TableCell>
                  <TableCell>
                    <Chip 
                      label={investigation.type}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={investigation.status}
                      color={getStatusColor(investigation.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{investigation.findings}</TableCell>
                  <TableCell>
                    <Chip 
                      label={investigation.risk_level}
                      color={getRiskColor(investigation.risk_level)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {new Date(investigation.created).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton size="small">
                        <Visibility />
                      </IconButton>
                      <IconButton size="small">
                        <Download />
                      </IconButton>
                      <IconButton size="small">
                        <Share />
                      </IconButton>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      {/* Threat Intelligence Tab */}
      <TabPanel value={currentTab} index={2}>
        <Typography variant="h5" gutterBottom>
          Threat Intelligence Dashboard
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Active Threats
                </Typography>
                <Typography variant="h2" color="error">
                  3
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Requires immediate attention
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Monitored Assets
                </Typography>
                <Typography variant="h2" color="primary">
                  127
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Domains, IPs, and entities
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Intelligence Reports
                </Typography>
                <Typography variant="h2" color="success.main">
                  45
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Generated this month
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Threat Indicators
            </Typography>
            <Alert severity="warning" sx={{ mb: 2 }}>
              <strong>High Priority:</strong> Suspicious domain registration detected: suspicious-domain.com
            </Alert>
            <Alert severity="info" sx={{ mb: 2 }}>
              <strong>Intelligence Update:</strong> New vulnerability disclosed affecting monitored systems
            </Alert>
            <Alert severity="success">
              <strong>All Clear:</strong> No new threats detected in the last 24 hours
            </Alert>
          </CardContent>
        </Card>
      </TabPanel>

      {/* Create Investigation Dialog */}
      <Dialog open={createInvestigationOpen} onClose={() => setCreateInvestigationOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Investigation</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Investigation Name"
                placeholder="Enter a descriptive name for this investigation"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Target"
                placeholder="Domain, email, IP address, etc."
              />
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Investigation Type</InputLabel>
                <Select label="Investigation Type">
                  {searchTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select label="Priority">
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="critical">Critical</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Investigation Notes"
                placeholder="Enter any additional context or requirements..."
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateInvestigationOpen(false)}>Cancel</Button>
          <Button variant="contained">Start Investigation</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OSINTCenter;
