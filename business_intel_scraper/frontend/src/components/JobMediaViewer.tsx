import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  Card,
  CardMedia,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  TextField,
  InputAdornment
} from '@mui/material';
import {
  Close as CloseIcon,
  Download as DownloadIcon,
  Search as SearchIcon,
  Image as ImageIcon,
  VideoFile as VideoIcon
} from '@mui/icons-material';

interface JobMediaViewerProps {
  open: boolean;
  onClose: () => void;
  jobId: number;
}

interface MediaAsset {
  url: string;
  content_type: string;
  size: number;
  data_url?: string;
  alt_text?: string;
  title?: string;
  width?: string | number;
  height?: string | number;
  video_type?: string;
  platform?: string;
  page_url?: string;
}

export const JobMediaViewer: React.FC<JobMediaViewerProps> = ({ open, onClose, jobId }) => {
  const [loading, setLoading] = useState(false);
  const [mediaAssets, setMediaAssets] = useState<MediaAsset[]>([]);
  const [filteredAssets, setFilteredAssets] = useState<MediaAsset[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'images' | 'videos'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (open && jobId) {
      fetchJobMedia();
    }
  }, [open, jobId]);

  useEffect(() => {
    // Apply filters
    let filtered = mediaAssets;

    // Filter by type
    if (filter === 'images') {
      filtered = filtered.filter(asset => asset.content_type.startsWith('image/'));
    } else if (filter === 'videos') {
      filtered = filtered.filter(asset => 
        asset.content_type.startsWith('video/') || asset.video_type
      );
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(asset =>
        asset.url.toLowerCase().includes(query) ||
        asset.alt_text?.toLowerCase().includes(query) ||
        asset.title?.toLowerCase().includes(query) ||
        asset.page_url?.toLowerCase().includes(query)
      );
    }

    setFilteredAssets(filtered);
  }, [mediaAssets, filter, searchQuery]);

  const fetchJobMedia = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/jobs/${jobId}/media`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch media: ${response.status}`);
      }

      const data = await response.json();
      
      // Filter out placeholder and empty assets
      const validAssets = data.assets.filter((asset: MediaAsset) =>
        asset.size > 0 &&
        !asset.url.toLowerCase().includes('placeholder') &&
        !asset.url.toLowerCase().includes('loading') &&
        !asset.url.toLowerCase().includes('spacer') &&
        asset.url !== 'data:,'
      );

      setMediaAssets(validAssets);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (asset: MediaAsset) => {
    if (asset.data_url) {
      const link = document.createElement('a');
      link.href = asset.data_url;
      link.download = asset.url.split('/').pop() || 'media_file';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } else {
      window.open(asset.url, '_blank');
    }
  };

  const renderMediaCard = (asset: MediaAsset, index: number) => {
    const isImage = asset.content_type.startsWith('image/');
    const isVideo = asset.content_type.startsWith('video/') || asset.video_type;

    return (
      <Grid item xs={12} sm={6} md={4} lg={3} key={index}>
        <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ position: 'relative', paddingTop: '75%', backgroundColor: '#f5f5f5' }}>
            {isImage ? (
              <CardMedia
                component="img"
                image={asset.data_url || asset.url}
                alt={asset.alt_text || `Media ${index + 1}`}
                sx={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover'
                }}
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtc2l6ZT0iMTgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5JbWFnZSBOb3QgRm91bmQ8L3RleHQ+PC9zdmc+';
                }}
              />
            ) : isVideo ? (
              <Box sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: '#000'
              }}>
                <VideoIcon sx={{ fontSize: 48, color: '#fff' }} />
                {asset.platform && (
                  <Chip 
                    label={asset.platform}
                    size="small"
                    sx={{ position: 'absolute', top: 8, right: 8 }}
                  />
                )}
              </Box>
            ) : null}
          </Box>
          
          <CardContent sx={{ flexGrow: 1, p: 1 }}>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
              {isImage && <ImageIcon sx={{ fontSize: 14, mr: 0.5 }} />}
              {isVideo && <VideoIcon sx={{ fontSize: 14, mr: 0.5 }} />}
              {asset.content_type}
              {asset.size > 0 && ` • ${(asset.size / 1024).toFixed(1)} KB`}
            </Typography>
            
            <Typography variant="body2" sx={{ mb: 1, wordBreak: 'break-all' }}>
              <strong>URL:</strong> {asset.url.length > 40 ? asset.url.substring(0, 40) + '...' : asset.url}
            </Typography>
            
            {asset.alt_text && (
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                <strong>Alt:</strong> {asset.alt_text}
              </Typography>
            )}
            
            {asset.page_url && (
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                <strong>From:</strong> {asset.page_url.length > 30 ? asset.page_url.substring(0, 30) + '...' : asset.page_url}
              </Typography>
            )}
          </CardContent>
          
          <Box sx={{ p: 1 }}>
            <Button
              size="small"
              startIcon={<DownloadIcon />}
              onClick={() => handleDownload(asset)}
              fullWidth
            >
              {isVideo ? 'Watch' : 'Download'}
            </Button>
          </Box>
        </Card>
      </Grid>
    );
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xl" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">
            Job #{jobId} - All Media Assets
          </Typography>
          <Button onClick={onClose}>
            <CloseIcon />
          </Button>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        ) : (
          <>
            {/* Filters */}
            <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Filter</InputLabel>
                <Select
                  value={filter}
                  label="Filter"
                  onChange={(e) => setFilter(e.target.value as any)}
                >
                  <MenuItem value="all">All Media</MenuItem>
                  <MenuItem value="images">Images Only</MenuItem>
                  <MenuItem value="videos">Videos Only</MenuItem>
                </Select>
              </FormControl>
              
              <TextField
                size="small"
                placeholder="Search assets..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
                sx={{ minWidth: 200 }}
              />
              
              <Typography variant="body2" color="text.secondary">
                Showing {filteredAssets.length} of {mediaAssets.length} assets
              </Typography>
            </Box>

            {/* Media Grid */}
            {filteredAssets.length === 0 ? (
              <Alert severity="info">
                {mediaAssets.length === 0 
                  ? 'No media assets found in this job' 
                  : 'No assets match the current filters'}
              </Alert>
            ) : (
              <Grid container spacing={2}>
                {filteredAssets.map((asset, index) => renderMediaCard(asset, index))}
              </Grid>
            )}
          </>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};
