import React, { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Tabs,
  Tab,
  Box,
  CircularProgress,
  Alert,
  Chip,
  Card,
  CardContent,
  CardMedia,
  Grid,
  Typography,
  FormControl,
  Select,
  MenuItem,
  IconButton,
  Paper
} from '@mui/material';
import {
  Close as CloseIcon,
  Download as DownloadIcon,
  Image as ImageIcon,
  Web as WebIcon,
  AccountTree as NetworkIcon,
  BugReport as DebugIcon,
  PlayArrow as PlayArrowIcon
} from '@mui/icons-material';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  MiniMap,
  Background,
  BackgroundVariant,
  Position,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface TabPanelProps {
  children?: React.ReactNode;
  index: string;
  value: string;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 0 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

interface PageViewerModalProps {
  show: boolean;
  onHide: () => void;
  jobId: number;
  selectedUrl?: string;
}

interface PageData {
  url: string;
  manifest: any;
  main_content: string;
  assets: Array<{
    url: string;
    content_type: string;
    size: number;
    data_url: string;
    discovered_via: string;
    alt_text?: string;
    title?: string;
    width?: string | number;
    height?: string | number;
    css_class?: string;
    video_type?: string;
    platform?: string;
    type?: string;
    poster?: string;
  }>;
  status: number;
  content_type: string;
}

interface JobDebugInfo {
  job_id: number;
  status: string;
  error_logs: Array<{
    timestamp: string;
    level: string;
    message: string;
    url?: string;
    error_code?: string;
  }>;
  crawl_stats: {
    total_attempted: number;
    total_successful: number;
    total_failed: number;
    domains_attempted: number;
    domains_successful: number;
  };
  failed_urls: Array<{
    url: string;
    error: string;
    status_code?: number;
    timestamp: string;
  }>;
}

interface NetworkNode {
  id: string;
  url: string;
  title: string;
  status: number;
  depth: number;
  discovery_order: number;
  domain: string;
  size: number;
}

interface NetworkEdge {
  source: string;
  target: string;
  type: string;
  link_text: string;
}

interface NetworkDiagram {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  metadata: {
    run_id: string;
    total_pages: number;
    total_domains: number;
    crawl_depth: number;
  };
}

const PageViewerModal: React.FC<PageViewerModalProps> = ({ show, onHide, jobId, selectedUrl }) => {
  const [activeTab, setActiveTab] = useState('page-view');
  const [pageData, setPageData] = useState<PageData | null>(null);
  const [networkDiagram, setNetworkDiagram] = useState<NetworkDiagram | null>(null);
  const [jobDebugInfo, setJobDebugInfo] = useState<JobDebugInfo | null>(null);
  const [availableUrls, setAvailableUrls] = useState<string[]>([]);
  const [currentUrl, setCurrentUrl] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [debugLoading, setDebugLoading] = useState(false);
  const [networkLayout, setNetworkLayout] = useState<'hierarchical' | 'force' | 'circular' | 'grid'>('hierarchical');
  const [showNetworkControls, setShowNetworkControls] = useState(false);

  useEffect(() => {
    if (show && jobId) {
      loadJobUrls();
      loadNetworkDiagram();
      loadJobDebugInfo();
    }
  }, [show, jobId]);

  useEffect(() => {
    if (selectedUrl) {
      setCurrentUrl(selectedUrl);
      loadPageData(selectedUrl);
    } else if (availableUrls.length > 0) {
      setCurrentUrl(availableUrls[0]);
      loadPageData(availableUrls[0]);
    }
  }, [selectedUrl, availableUrls]);

  const loadJobUrls = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/jobs/${jobId}/urls`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to load URLs: ${response.statusText}`);
      }

      const urls = await response.json();
      setAvailableUrls(urls);
    } catch (err) {
      setError(`Failed to load URLs: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const loadPageData = async (url: string) => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch(`/api/cfpl/page-content`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ url, render_html: true }),
      });

      if (!response.ok) {
        throw new Error(`Failed to load page: ${response.statusText}`);
      }

      const data = await response.json();
      setPageData(data);
    } catch (err) {
      setError(`Failed to load page: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const loadJobDebugInfo = async () => {
    try {
      setDebugLoading(true);
      const response = await fetch(`/api/jobs/${jobId}/debug`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        console.warn(`Debug info not available: ${response.statusText}`);
        return;
      }

      const debugInfo = await response.json();
      setJobDebugInfo(debugInfo);
    } catch (err) {
      console.warn('Failed to load debug info:', err);
    } finally {
      setDebugLoading(false);
    }
  };

  const loadNetworkDiagram = async () => {
    try {
      const response = await fetch(`/api/cfpl/network-diagram/${jobId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to load network diagram: ${response.statusText}`);
      }

      const diagram = await response.json();
      setNetworkDiagram(diagram);
    } catch (err) {
      console.error('Failed to load network diagram:', err);
    }
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusChipColor = (status: number): "success" | "warning" | "error" | "default" => {
    if (status >= 200 && status < 300) return 'success';
    if (status >= 300 && status < 400) return 'warning';
    return 'error';
  };

  const renderDebugPanel = () => {
    if (debugLoading) {
      return (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 5 }}>
          <CircularProgress />
          <Typography sx={{ mt: 2 }}>Loading debug information...</Typography>
        </Box>
      );
    }

    if (!jobDebugInfo) {
      return (
        <Alert severity="info" sx={{ m: 2 }}>
          🔍 Debug information not available for this job
        </Alert>
      );
    }

    const { job_id, status, error_logs, crawl_stats, failed_urls } = jobDebugInfo;

    return (
      <Box sx={{ p: 2 }}>
        {/* Job Status Overview */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            🔍 Job #{job_id} Debug Information
          </Typography>
          
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ textAlign: 'center' }}>
                <CardContent>
                  <Typography variant="h4" color={status === 'completed' ? 'success.main' : status === 'failed' ? 'error.main' : 'warning.main'}>
                    {status.toUpperCase()}
                  </Typography>
                  <Typography variant="caption">Job Status</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ textAlign: 'center' }}>
                <CardContent>
                  <Typography variant="h4" color="primary">
                    {crawl_stats.total_attempted}
                  </Typography>
                  <Typography variant="caption">URLs Attempted</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ textAlign: 'center' }}>
                <CardContent>
                  <Typography variant="h4" color="success.main">
                    {crawl_stats.total_successful}
                  </Typography>
                  <Typography variant="caption">Successfully Crawled</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ textAlign: 'center' }}>
                <CardContent>
                  <Typography variant="h4" color="error.main">
                    {crawl_stats.total_failed}
                  </Typography>
                  <Typography variant="caption">Failed</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>

        {/* Error Logs */}
        {error_logs.length > 0 && (
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              ⚠️ Error Logs ({error_logs.length} entries)
            </Typography>
            <Paper sx={{ maxHeight: 300, overflow: 'auto', p: 2 }}>
              {error_logs.map((log, index) => (
                <Box key={index} sx={{ mb: 2, borderBottom: '1px solid #eee', pb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Chip 
                      label={log.level} 
                      size="small"
                      color={log.level === 'ERROR' ? 'error' : log.level === 'WARNING' ? 'warning' : 'default'}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {new Date(log.timestamp).toLocaleString()}
                    </Typography>
                    {log.error_code && (
                      <Chip label={log.error_code} size="small" variant="outlined" />
                    )}
                  </Box>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.85em' }}>
                    {log.message}
                  </Typography>
                  {log.url && (
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                      URL: {log.url}
                    </Typography>
                  )}
                </Box>
              ))}
            </Paper>
          </Box>
        )}

        {/* Failed URLs */}
        {failed_urls.length > 0 && (
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              ❌ Failed URLs ({failed_urls.length} entries)
            </Typography>
            <Paper sx={{ maxHeight: 400, overflow: 'auto' }}>
              <Grid container spacing={1} sx={{ p: 2 }}>
                {failed_urls.map((failedUrl, index) => (
                  <Grid item xs={12} key={index}>
                    <Card variant="outlined" sx={{ p: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                        <Typography variant="body2" sx={{ fontWeight: 'bold', maxWidth: '70%', wordBreak: 'break-all' }}>
                          {failedUrl.url}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          {failedUrl.status_code && (
                            <Chip 
                              label={failedUrl.status_code} 
                              size="small" 
                              color={failedUrl.status_code >= 400 ? 'error' : 'warning'}
                            />
                          )}
                          <Typography variant="caption" color="text.secondary">
                            {new Date(failedUrl.timestamp).toLocaleTimeString()}
                          </Typography>
                        </Box>
                      </Box>
                      <Typography variant="body2" color="error.main" sx={{ fontSize: '0.85em' }}>
                        {failedUrl.error}
                      </Typography>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Paper>
          </Box>
        )}

        {/* Success Rate */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            📊 Crawl Performance
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1">Success Rate</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
                  <Box 
                    sx={{ 
                      flexGrow: 1, 
                      height: 10, 
                      backgroundColor: '#f0f0f0', 
                      borderRadius: 1,
                      overflow: 'hidden'
                    }}
                  >
                    <Box 
                      sx={{ 
                        height: '100%', 
                        backgroundColor: crawl_stats.total_successful > 0 ? '#4caf50' : '#f44336',
                        width: `${crawl_stats.total_attempted > 0 ? (crawl_stats.total_successful / crawl_stats.total_attempted) * 100 : 0}%`
                      }} 
                    />
                  </Box>
                  <Typography variant="body2">
                    {crawl_stats.total_attempted > 0 ? 
                      Math.round((crawl_stats.total_successful / crawl_stats.total_attempted) * 100) : 0}%
                  </Typography>
                </Box>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1">Domain Success Rate</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
                  <Box 
                    sx={{ 
                      flexGrow: 1, 
                      height: 10, 
                      backgroundColor: '#f0f0f0', 
                      borderRadius: 1,
                      overflow: 'hidden'
                    }}
                  >
                    <Box 
                      sx={{ 
                        height: '100%', 
                        backgroundColor: crawl_stats.domains_successful > 0 ? '#2196f3' : '#f44336',
                        width: `${crawl_stats.domains_attempted > 0 ? (crawl_stats.domains_successful / crawl_stats.domains_attempted) * 100 : 0}%`
                      }} 
                    />
                  </Box>
                  <Typography variant="body2">
                    {crawl_stats.domains_attempted > 0 ? 
                      Math.round((crawl_stats.domains_successful / crawl_stats.domains_attempted) * 100) : 0}%
                  </Typography>
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </Box>

        {/* No Results Warning */}
        {crawl_stats.total_successful === 0 && (
          <Alert severity="warning" sx={{ mt: 2 }}>
            <Typography variant="h6">🚨 No Successful Results</Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              This job attempted to crawl {crawl_stats.total_attempted} URLs but none were successful. 
              Common causes include:
            </Typography>
            <ul>
              <li>Network connectivity issues</li>
              <li>Invalid or unreachable URLs</li>
              <li>Server blocking automated requests (403/429 errors)</li>
              <li>SSL/TLS certificate problems</li>
              <li>Timeout issues</li>
              <li>Authentication requirements</li>
            </ul>
            <Typography variant="body2">
              Check the error logs and failed URLs above for specific failure reasons.
            </Typography>
          </Alert>
        )}
      </Box>
    );
  };

  const renderPageView = () => {
    if (!pageData) {
      // Show helpful message when no data is available
      return (
        <Box sx={{ p: 2 }}>
          <Alert severity="info" sx={{ mb: 2 }}>
            📭 No page data available for this job
          </Alert>
          {availableUrls.length === 0 && (
            <Alert severity="warning">
              <Typography variant="h6">No URLs Found</Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                This job has no successfully crawled URLs. This could indicate:
              </Typography>
              <ul>
                <li>The crawl failed to process any pages</li>
                <li>All attempted URLs resulted in errors</li>
                <li>The job is still running or hasn't started yet</li>
              </ul>
              <Typography variant="body2" sx={{ mt: 1 }}>
                Check the <strong>Debug Info</strong> tab for detailed error information.
              </Typography>
            </Alert>
          )}
        </Box>
      );
    }

    return (
      <Box sx={{ p: 2 }}>
        <Box sx={{ mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={8}>
              <Typography variant="h6" component="h3" sx={{ mb: 1 }}>
                🌐 {pageData.url}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip 
                  label={pageData.status} 
                  color={getStatusChipColor(pageData.status)}
                  size="small"
                />
                <Chip 
                  label={pageData.content_type} 
                  variant="outlined"
                  size="small"
                />
                <Chip 
                  label={`${pageData.assets.length} assets`} 
                  variant="outlined"
                  size="small"
                />
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth size="small">
                <Select
                  value={currentUrl}
                  onChange={(e) => {
                    setCurrentUrl(e.target.value);
                    loadPageData(e.target.value);
                  }}
                >
                  {availableUrls.map(url => (
                    <MenuItem key={url} value={url}>{url}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Box>
        
        <Box 
          sx={{ 
            height: '600px', 
            border: '1px solid #ddd', 
            borderRadius: 1,
            overflow: 'auto' 
          }}
        >
          {pageData.main_content && (
            <iframe
              srcDoc={pageData.main_content}
              style={{ width: '100%', height: '100%', border: 'none' }}
              sandbox="allow-same-origin"
              title={`Rendered page: ${pageData.url}`}
            />
          )}
        </Box>
      </Box>
    );
  };

  const renderImageGallery = () => {
    if (!pageData) return null;

    // Filter out placeholder images and empty assets
    const images = pageData.assets.filter(asset => 
      asset.content_type.startsWith('image/') &&
      asset.size > 0 &&
      !asset.url.toLowerCase().includes('placeholder') &&
      !asset.url.toLowerCase().includes('loading') &&
      !asset.url.toLowerCase().includes('spacer') &&
      asset.url !== 'data:,' // Empty data URL
    );
    
    const videos = pageData.assets.filter(asset => 
      (asset.content_type.startsWith('video/') || asset.video_type) &&
      asset.size > 0 &&
      !asset.url.toLowerCase().includes('placeholder')
    );
    
    const totalMedia = images.length + videos.length;

    if (totalMedia === 0) {
      return (
        <Alert severity="info" sx={{ m: 2 }}>
          📷 No media content found in this page
        </Alert>
      );
    }

    return (
      <Box sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            🎬 Media Gallery ({images.length} images, {videos.length} videos)
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip 
              label={`📸 ${images.length} Images`} 
              size="small" 
              color="primary" 
              variant="outlined" 
            />
            <Chip 
              label={`🎥 ${videos.length} Videos`} 
              size="small" 
              color="secondary" 
              variant="outlined" 
            />
          </Box>
        </Box>

        {/* Images Section */}
        {images.length > 0 && (
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>
              📸 Images ({images.length})
            </Typography>
            <Grid container spacing={2}>
              {images.map((image, index) => (
                <Grid item xs={12} sm={6} md={4} key={`image_${index}`}>
                  <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <CardMedia
                      component="img"
                      height="200"
                      image={image.data_url}
                      alt={image.alt_text || `Image ${index + 1}`}
                      sx={{ objectFit: 'cover' }}
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtc2l6ZT0iMTgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5JbWFnZSBOb3QgRm91bmQ8L3RleHQ+PC9zdmc+';
                      }}
                    />
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        <strong>URL:</strong> <a href={image.url} target="_blank" rel="noopener">{image.url.length > 50 ? image.url.substring(0, 50) + '...' : image.url}</a>
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Type:</strong> {image.content_type}
                      </Typography>
                      {image.alt_text && (
                        <Typography variant="body2" color="text.secondary">
                          <strong>Alt Text:</strong> {image.alt_text}
                        </Typography>
                      )}
                      {image.title && (
                        <Typography variant="body2" color="text.secondary">
                          <strong>Title:</strong> {image.title}
                        </Typography>
                      )}
                      {(image.width || image.height) && (
                        <Typography variant="body2" color="text.secondary">
                          <strong>Dimensions:</strong> {image.width || '?'} × {image.height || '?'}
                        </Typography>
                      )}
                      <Typography variant="body2" color="text.secondary">
                        <strong>Size:</strong> {formatBytes(image.size)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Found via:</strong> {image.discovered_via}
                      </Typography>
                      <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                        <Button 
                          variant="outlined" 
                          size="small"
                          startIcon={<DownloadIcon />}
                          onClick={() => {
                            const link = document.createElement('a');
                            link.href = image.data_url;
                            link.download = `image_${index + 1}`;
                            link.click();
                          }}
                        >
                          Download
                        </Button>
                        <Button 
                          variant="outlined" 
                          size="small"
                          onClick={() => window.open(image.url, '_blank')}
                        >
                          Open
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Videos Section */}
        {videos.length > 0 && (
          <Box>
            <Typography variant="h6" sx={{ mb: 2, color: 'secondary.main' }}>
              🎥 Videos ({videos.length})
            </Typography>
            <Grid container spacing={2}>
              {videos.map((video, index) => (
                <Grid item xs={12} sm={6} md={4} key={`video_${index}`}>
                  <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <Box sx={{ height: 200, bgcolor: 'grey.100', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
                      {video.platform === 'youtube' && video.url.includes('embed') ? (
                        <iframe
                          width="100%"
                          height="200"
                          src={video.url}
                          title={video.title || `Video ${index + 1}`}
                          frameBorder="0"
                          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                          allowFullScreen
                        />
                      ) : video.platform === 'vimeo' && video.url.includes('player.vimeo.com') ? (
                        <iframe
                          width="100%"
                          height="200"
                          src={video.url}
                          title={video.title || `Video ${index + 1}`}
                          frameBorder="0"
                          allow="autoplay; fullscreen; picture-in-picture"
                          allowFullScreen
                        />
                      ) : video.type === 'video' && video.url.includes('.mp4') ? (
                        <video
                          width="100%"
                          height="200"
                          controls
                          poster={video.poster}
                        >
                          <source src={video.url} type="video/mp4" />
                          Your browser does not support the video tag.
                        </video>
                      ) : (
                        <Box sx={{ textAlign: 'center', p: 2 }}>
                          <PlayArrowIcon sx={{ fontSize: 48, color: 'grey.600', mb: 1 }} />
                          <Typography variant="body2" color="text.secondary">
                            Video Preview
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {video.platform?.toUpperCase() || 'VIDEO'}
                          </Typography>
                        </Box>
                      )}
                      <Chip
                        label={video.platform?.toUpperCase() || video.type?.toUpperCase() || 'VIDEO'}
                        size="small"
                        sx={{ position: 'absolute', top: 8, right: 8, bgcolor: 'rgba(0,0,0,0.7)', color: 'white' }}
                      />
                    </Box>
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        <strong>URL:</strong> <a href={video.url} target="_blank" rel="noopener">{video.url.length > 50 ? video.url.substring(0, 50) + '...' : video.url}</a>
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Type:</strong> {video.video_type || video.type}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>Platform:</strong> {video.platform || 'Unknown'}
                      </Typography>
                      {video.title && (
                        <Typography variant="body2" color="text.secondary">
                          <strong>Title:</strong> {video.title}
                        </Typography>
                      )}
                      {(video.width || video.height) && (
                        <Typography variant="body2" color="text.secondary">
                          <strong>Dimensions:</strong> {video.width || '?'} × {video.height || '?'}
                        </Typography>
                      )}
                      <Typography variant="body2" color="text.secondary">
                        <strong>Found via:</strong> {video.discovered_via}
                      </Typography>
                      <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                        <Button 
                          variant="outlined" 
                          size="small"
                          startIcon={<PlayArrowIcon />}
                          onClick={() => window.open(video.url, '_blank')}
                        >
                          Watch
                        </Button>
                        {video.url.includes('.mp4') && (
                          <Button 
                            variant="outlined" 
                            size="small"
                            startIcon={<DownloadIcon />}
                            onClick={() => {
                              const link = document.createElement('a');
                              link.href = video.url;
                              link.download = `video_${index + 1}.mp4`;
                              link.click();
                            }}
                          >
                            Download
                          </Button>
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </Box>
    );
  };

  // Enhanced layout calculation functions
  const calculateNodePositions = (nodes: NetworkNode[], layout: string) => {
    const positions: { [id: string]: { x: number; y: number } } = {};
    
    switch (layout) {
      case 'hierarchical':
        // Group by depth
        const nodesByDepth: { [depth: number]: NetworkNode[] } = {};
        nodes.forEach(node => {
          if (!nodesByDepth[node.depth]) nodesByDepth[node.depth] = [];
          nodesByDepth[node.depth].push(node);
        });
        
        const verticalSpacing = 200;
        const horizontalSpacing = 250;
        
        Object.keys(nodesByDepth).forEach(depthStr => {
          const depth = parseInt(depthStr);
          const nodesAtDepth = nodesByDepth[depth];
          const totalWidth = (nodesAtDepth.length - 1) * horizontalSpacing;
          const startX = -totalWidth / 2;
          
          nodesAtDepth.forEach((node, index) => {
            positions[node.id] = {
              x: startX + (index * horizontalSpacing),
              y: depth * verticalSpacing
            };
          });
        });
        break;
        
      case 'force':
        // Simple force-directed layout approximation
        nodes.forEach((node, index) => {
          const angle = (index * 2 * Math.PI) / nodes.length;
          const radius = 200 + (node.depth * 100);
          positions[node.id] = {
            x: Math.cos(angle) * radius,
            y: Math.sin(angle) * radius
          };
        });
        break;
        
      case 'circular':
        // Circular layout with depth-based rings
        const depthNodes: { [depth: number]: NetworkNode[] } = {};
        nodes.forEach(node => {
          if (!depthNodes[node.depth]) depthNodes[node.depth] = [];
          depthNodes[node.depth].push(node);
        });
        
        Object.keys(depthNodes).forEach(depthStr => {
          const depth = parseInt(depthStr);
          const nodesAtDepth = depthNodes[depth];
          const radius = (depth + 1) * 180;
          
          nodesAtDepth.forEach((node, index) => {
            const angle = (index * 2 * Math.PI) / nodesAtDepth.length;
            positions[node.id] = {
              x: Math.cos(angle) * radius,
              y: Math.sin(angle) * radius
            };
          });
        });
        break;
        
      case 'grid':
        // Grid layout
        const cols = Math.ceil(Math.sqrt(nodes.length));
        const cellSize = 200;
        
        nodes.forEach((node, index) => {
          const row = Math.floor(index / cols);
          const col = index % cols;
          positions[node.id] = {
            x: col * cellSize,
            y: row * cellSize
          };
        });
        break;
        
      default:
        // Default positions
        nodes.forEach((node, index) => {
          positions[node.id] = {
            x: (index % 5) * 200,
            y: Math.floor(index / 5) * 200
          };
        });
    }
    
    return positions;
  };

  const renderNetworkDiagram = () => {
    if (!networkDiagram) {
      return (
        <Box sx={{ p: 2 }}>
          <Alert severity="info" sx={{ mb: 2 }}>
            🔄 Loading network diagram...
          </Alert>
          {availableUrls.length === 0 && (
            <Alert severity="warning">
              <Typography variant="h6">No Network Data Available</Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                Cannot generate network diagram because no URLs were successfully crawled.
                Check the <strong>Debug Info</strong> tab to understand why the crawl failed.
              </Typography>
            </Alert>
          )}
        </Box>
      );
    }

    const { nodes, edges, metadata } = networkDiagram;

    // Calculate positions using selected layout
    const nodePositions = calculateNodePositions(nodes, networkLayout);

    // Create React Flow nodes with enhanced styling
    const reactFlowNodes: Node[] = nodes.map((node) => {
      const position = nodePositions[node.id] || { x: 0, y: 0 };
      
      // Determine node color and style based on type and depth
      let backgroundColor, borderColor, textColor;
      if (node.status === 0) { // External/unvisited
        backgroundColor = '#e9ecef';
        borderColor = '#adb5bd';
        textColor = '#6c757d';
      } else if (node.depth === 0) { // Root
        backgroundColor = '#ff6b6b';
        borderColor = '#e55555';
        textColor = '#ffffff';
      } else if (node.depth === 1) {
        backgroundColor = '#4ecdc4';
        borderColor = '#42b8b1';
        textColor = '#ffffff';
      } else if (node.depth === 2) {
        backgroundColor = '#45b7d1';
        borderColor = '#3a9bc1';
        textColor = '#ffffff';
      } else {
        backgroundColor = '#96ceb4';
        borderColor = '#82b89f';
        textColor = '#ffffff';
      }

      return {
        id: node.id,
        type: 'default',
        position,
        data: {
          label: (
            <div style={{ 
              textAlign: 'center', 
              padding: '8px',
              minWidth: '120px',
              maxWidth: '180px'
            }}>
              <div style={{ 
                fontSize: '11px', 
                fontWeight: 'bold',
                marginBottom: '4px'
              }}>
                {node.title?.substring(0, 25) || new URL(node.url).pathname.split('/').pop() || 'Page'}
                {node.title && node.title.length > 25 && '...'}
              </div>
              <div style={{ 
                fontSize: '9px', 
                opacity: 0.8,
                marginBottom: '2px'
              }}>
                Depth: {node.depth} | #{node.discovery_order + 1}
              </div>
              {node.domain && (
                <div style={{ 
                  fontSize: '8px', 
                  opacity: 0.7,
                  backgroundColor: 'rgba(255,255,255,0.2)',
                  borderRadius: '3px',
                  padding: '1px 4px'
                }}>
                  {node.domain}
                </div>
              )}
            </div>
          )
        },
        style: {
          backgroundColor,
          border: `2px solid ${borderColor}`,
          borderRadius: '8px',
          color: textColor,
          width: 140,
          fontSize: '11px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }
      };
    });
            height: 80,
            fontSize: '10px',
            boxShadow: node.depth === 0 ? '0 4px 8px rgba(255, 107, 107, 0.3)' : '0 2px 4px rgba(0,0,0,0.1)',
          },
          sourcePosition: Position.Bottom,
          targetPosition: Position.Top,
        });
      });
    });

    // Create hierarchical edges based on actual crawl relationships
    const reactFlowEdges: Edge[] = [];
    
    // Build parent-child relationships based on how pages were discovered
    const parentChildMap: { [childId: string]: string } = {};
    
    // For each edge in the original data, find the parent-child relationship
    edges.forEach(edge => {
      const sourceNode = nodes.find(n => n.id === edge.source);
      const targetNode = nodes.find(n => n.id === edge.target);
      
      if (sourceNode && targetNode && targetNode.depth === sourceNode.depth + 1) {
        // This is a parent-child relationship (source discovered target)
        if (!parentChildMap[targetNode.id] || 
            nodes.find(n => n.id === parentChildMap[targetNode.id])!.discovery_order > sourceNode.discovery_order) {
          parentChildMap[targetNode.id] = sourceNode.id;
        }
      }
    });

    // Create edges for hierarchical relationships
    Object.entries(parentChildMap).forEach(([childId, parentId]) => {
      const childNode = nodes.find(n => n.id === childId);
      const parentNode = nodes.find(n => n.id === parentId);
      
      if (childNode && parentNode) {
        reactFlowEdges.push({
          id: `hierarchy-${parentId}-${childId}`,
          source: parentId,
          target: childId,
          type: 'smoothstep',
          style: { 
            stroke: '#2196f3', 
            strokeWidth: 3,
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: '#2196f3',
            width: 20,
            height: 20,
          },
          label: `discovered`,
          labelStyle: { fontSize: '10px', fontWeight: 'bold' },
        });
      }
    });

    // Add cross-links (same depth or backwards links) with different styling
    edges.slice(0, 15).forEach((edge, index) => {
      const sourceNode = nodes.find(n => n.id === edge.source);
      const targetNode = nodes.find(n => n.id === edge.target);
      
      if (sourceNode && targetNode && 
          edge.source !== edge.target && 
          parentChildMap[targetNode.id] !== sourceNode.id &&
          targetNode.depth <= sourceNode.depth) {
        
        reactFlowEdges.push({
          id: `crosslink-${index}`,
          source: edge.source,
          target: edge.target,
          type: 'default',
          style: { 
            stroke: '#ff9800', 
            strokeWidth: 1, 
            strokeDasharray: '5,5',
            opacity: 0.6
          },
          markerEnd: {
            type: MarkerType.Arrow,
            color: '#ff9800',
          },
          label: edge.link_text ? edge.link_text.substring(0, 15) + '...' : 'link',
          labelStyle: { fontSize: '9px', fill: '#ff9800' },
        });
      }
    });

    return (
      <Box sx={{ p: 2, height: '100%' }}>
        {/* Statistics Cards */}
        <Box sx={{ mb: 4 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ textAlign: 'center' }}>
                <CardContent>
                  <Typography variant="h4" color="primary">
                    {metadata.total_pages}
                  </Typography>
                  <Typography variant="caption">
                    Pages Crawled
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ textAlign: 'center' }}>
                <CardContent>
                  <Typography variant="h4" color="success.main">
                    {metadata.total_domains}
                  </Typography>
                  <Typography variant="caption">
                    Domains
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ textAlign: 'center' }}>
                <CardContent>
                  <Typography variant="h4" color="warning.main">
                    {metadata.crawl_depth}
                  </Typography>
                  <Typography variant="caption">
                    Max Depth
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ textAlign: 'center' }}>
                <CardContent>
                  <Typography variant="h4" color="info.main">
                    {reactFlowEdges.length}
                  </Typography>
                  <Typography variant="caption">
                    Connections
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>

        {/* Legend and Layout Controls */}
        <Paper sx={{ p: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">🗺️ Network Visualization</Typography>
            <Button
              variant="outlined"
              size="small"
              onClick={() => setShowNetworkControls(!showNetworkControls)}
            >
              {showNetworkControls ? 'Hide Controls' : 'Show Controls'}
            </Button>
          </Box>
          
          {showNetworkControls && (
            <Box sx={{ mb: 2, p: 2, backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Layout Algorithm:</Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {[
                  { key: 'hierarchical', label: 'Hierarchical', desc: 'Depth-based tree layout' },
                  { key: 'force', label: 'Force-directed', desc: 'Physics simulation' },
                  { key: 'circular', label: 'Circular', desc: 'Concentric circles' },
                  { key: 'grid', label: 'Grid', desc: 'Regular grid pattern' }
                ].map(layout => (
                  <Button
                    key={layout.key}
                    variant={networkLayout === layout.key ? 'contained' : 'outlined'}
                    size="small"
                    onClick={() => setNetworkLayout(layout.key as any)}
                    sx={{ minWidth: '100px' }}
                  >
                    {layout.label}
                  </Button>
                ))}
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Selected: <strong>{networkLayout}</strong> - 
                {networkLayout === 'hierarchical' && 'Organizes nodes by crawl depth'}
                {networkLayout === 'force' && 'Physics-based layout with attraction/repulsion'}
                {networkLayout === 'circular' && 'Arranges nodes in concentric circles by depth'}
                {networkLayout === 'grid' && 'Regular grid arrangement for easy scanning'}
              </Typography>
            </Box>
          )}

          <Typography variant="subtitle2" sx={{ mb: 1 }}>Legend:</Typography>
          <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 20, height: 20, background: '#ff6b6b', border: '2px solid #e55555', borderRadius: '4px' }} />
              <Typography variant="caption">Root Page</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 20, height: 20, background: '#4ecdc4', border: '2px solid #42b8b1', borderRadius: '4px' }} />
              <Typography variant="caption">Depth 1</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 20, height: 20, background: '#45b7d1', border: '2px solid #3a9bc1', borderRadius: '4px' }} />
              <Typography variant="caption">Depth 2</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 20, height: 20, background: '#96ceb4', border: '2px solid #82b89f', borderRadius: '4px' }} />
              <Typography variant="caption">Depth 3+</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 20, height: 20, background: '#e9ecef', border: '2px dashed #adb5bd', borderRadius: '4px' }} />
              <Typography variant="caption">External Links</Typography>
            </Box>
          </Box>
        </Paper>

        {/* Interactive Network Graph */}
        <Paper sx={{ height: 600, border: '1px solid #ddd' }}>
          <ReactFlow
            nodes={reactFlowNodes}
            edges={reactFlowEdges}
            fitView
            attributionPosition="bottom-left"
            nodesDraggable={true}
            elementsSelectable={true}
            selectNodesOnDrag={false}
            fitViewOptions={{
              padding: 50,
              minZoom: 0.1,
              maxZoom: 2
            }}
          >
            <Background variant={BackgroundVariant.Dots} gap={20} size={1} />
            <Controls />
            <MiniMap 
              nodeStrokeColor="#666"
              nodeColor="#fff"
              nodeBorderRadius={8}
              style={{
                background: '#f8f9fa',
                border: '1px solid #ddd'
              }}
            />
          </ReactFlow>
        </Paper>

        {/* Domain Breakdown */}
        <Typography variant="h6" sx={{ mt: 4, mb: 2 }}>
          🌐 Domain Breakdown
        </Typography>
        {Array.from(new Set(nodes.map(n => n.domain))).map(domain => {
          const domainNodes = nodes.filter(n => n.domain === domain);
          return (
            <Box key={domain} sx={{ mb: 1 }}>
              <Chip 
                label={domain} 
                variant="outlined" 
                color="info"
                sx={{ mr: 1 }}
              />
              <Typography variant="body2" component="span" color="text.secondary">
                {domainNodes.length} pages, {formatBytes(domainNodes.reduce((sum, n) => sum + n.size, 0))}
              </Typography>
            </Box>
          );
        })}
      </Box>
    );
  };

  return (
    <Dialog 
      open={show} 
      onClose={onHide} 
      maxWidth="xl" 
      fullWidth
      PaperProps={{
        sx: { 
          minHeight: '90vh',
          maxHeight: '95vh',
          height: '90vh'
        }
      }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h6" component="div">
          🔍 Advanced Page Viewer - Job #{jobId}
        </Typography>
        <IconButton onClick={onHide} size="small">
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      
      <DialogContent sx={{ p: 0 }}>
        {error && (
          <Alert severity="error" sx={{ m: 2 }}>
            ❌ {error}
          </Alert>
        )}

        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab 
            value="page-view" 
            label="📄 Page View" 
            icon={<WebIcon />}
            iconPosition="start"
          />
          <Tab 
            value="images" 
            label="🖼️ Image Gallery" 
            icon={<ImageIcon />}
            iconPosition="start"
          />
          <Tab 
            value="network" 
            label="🕸️ Network Diagram"
            icon={<NetworkIcon />}
            iconPosition="start"
          />
          <Tab 
            value="debug" 
            label="🔍 Debug Info"
            icon={<DebugIcon />}
            iconPosition="start"
          />
        </Tabs>

        <TabPanel value={activeTab} index="page-view">
          {loading ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 5 }}>
              <CircularProgress />
              <Typography sx={{ mt: 2 }}>Loading page content...</Typography>
            </Box>
          ) : (
            renderPageView()
          )}
        </TabPanel>

        <TabPanel value={activeTab} index="images">
          {loading ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 5 }}>
              <CircularProgress />
              <Typography sx={{ mt: 2 }}>Loading images...</Typography>
            </Box>
          ) : (
            renderImageGallery()
          )}
        </TabPanel>

        <TabPanel value={activeTab} index="network">
          {renderNetworkDiagram()}
        </TabPanel>

        <TabPanel value={activeTab} index="debug">
          {renderDebugPanel()}
        </TabPanel>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onHide} variant="outlined">
          Close
        </Button>
        {pageData && (
          <Button 
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={() => {
              // Export page bundle functionality
              fetch(`/api/cfpl/export-bundle`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${localStorage.getItem('token')}`,
                },
                body: JSON.stringify({ url: currentUrl }),
              })
              .then(response => response.blob())
              .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `page_bundle_${Date.now()}.zip`;
                a.click();
                window.URL.revokeObjectURL(url);
              });
            }}
          >
            📦 Export Bundle
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default PageViewerModal;
