import React, { useEffect, useRef, useState } from 'react';
import { Box, CircularProgress, Alert, Typography, IconButton, Tooltip } from '@mui/material';
import { ZoomIn, ZoomOut, MyLocation, Layers } from '@mui/icons-material';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface GeospatialMapProps {
  height?: number;
  className?: string;
}

interface MapPoint {
  id: string;
  lat: number;
  lng: number;
  popup: string;
  cluster?: boolean;
}

interface GeospatialData {
  points: MapPoint[];
  bounds?: {
    north: number;
    south: number;
    east: number;
    west: number;
  };
  metadata: {
    total_points: number;
    zoom_level: number;
    clustering_enabled: boolean;
    data_source?: string;
  };
}

const GeospatialMap = ({ 
  height = 500, 
  className 
}: GeospatialMapProps) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersGroupRef = useRef<L.LayerGroup | null>(null);
  
  const [data, setData] = useState<GeospatialData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showClusters, setShowClusters] = useState(true);

  const fetchGeospatialData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/visualization/geospatial-data');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load geospatial data');
      console.error('Error fetching geospatial data:', err);
    } finally {
      setLoading(false);
    }
  };

  const initializeMap = () => {
    if (!mapRef.current || mapInstanceRef.current) return;

    // Create map instance
    const map = L.map(mapRef.current, {
      center: [39.8283, -98.5795], // Center of USA
      zoom: 4,
      zoomControl: false // We'll add custom controls
    });

    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19
    }).addTo(map);

    // Create markers group
    const markersGroup = L.layerGroup().addTo(map);
    
    mapInstanceRef.current = map;
    markersGroupRef.current = markersGroup;
  };

  const updateMapMarkers = () => {
    if (!mapInstanceRef.current || !markersGroupRef.current || !data) return;

    // Clear existing markers
    markersGroupRef.current.clearLayers();

    // Add new markers
    data.points.forEach((point) => {
      const marker = L.marker([point.lat, point.lng])
        .bindPopup(`
          <div>
            <strong>${point.popup}</strong><br/>
            <small>Lat: ${point.lat.toFixed(4)}, Lng: ${point.lng.toFixed(4)}</small>
          </div>
        `);
      
      markersGroupRef.current!.addLayer(marker);
    });

    // Fit bounds if we have points
    if (data.points.length > 0) {
      const group = new L.featureGroup(markersGroupRef.current.getLayers());
      mapInstanceRef.current.fitBounds(group.getBounds().pad(0.1));
    }
  };

  const handleZoomIn = () => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.zoomIn();
    }
  };

  const handleZoomOut = () => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.zoomOut();
    }
  };

  const handleResetView = () => {
    if (mapInstanceRef.current && data && data.points.length > 0) {
      const group = new L.featureGroup(markersGroupRef.current!.getLayers());
      mapInstanceRef.current.fitBounds(group.getBounds().pad(0.1));
    }
  };

  const toggleClusters = () => {
    setShowClusters(!showClusters);
    // In a full implementation, this would enable/disable marker clustering
  };

  useEffect(() => {
    fetchGeospatialData();
  }, []);

  useEffect(() => {
    initializeMap();
    
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    updateMapMarkers();
  }, [data]);

  if (loading) {
    return (
      <Box 
        className={className}
        sx={{ 
          height: `${height}px`, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center' 
        }}
      >
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading geospatial data...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box className={className} sx={{ height: `${height}px`, p: 2 }}>
        <Alert severity="error">
          <Typography variant="body2">
            Error loading map: {error}
          </Typography>
        </Alert>
      </Box>
    );
  }

  return (
    <Box className={className} sx={{ position: 'relative', height: `${height}px` }}>
      {/* Map Container */}
      <div 
        ref={mapRef} 
        style={{ 
          width: '100%', 
          height: '100%',
          borderRadius: '4px'
        }} 
      />

      {/* Custom Controls */}
      <Box sx={{ 
        position: 'absolute', 
        top: 10, 
        right: 10, 
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        gap: 1
      }}>
        <Tooltip title="Zoom In">
          <IconButton 
            size="small" 
            onClick={handleZoomIn}
            sx={{ 
              backgroundColor: 'white',
              '&:hover': { backgroundColor: 'grey.100' }
            }}
          >
            <ZoomIn />
          </IconButton>
        </Tooltip>
        
        <Tooltip title="Zoom Out">
          <IconButton 
            size="small" 
            onClick={handleZoomOut}
            sx={{ 
              backgroundColor: 'white',
              '&:hover': { backgroundColor: 'grey.100' }
            }}
          >
            <ZoomOut />
          </IconButton>
        </Tooltip>
        
        <Tooltip title="Reset View">
          <IconButton 
            size="small" 
            onClick={handleResetView}
            sx={{ 
              backgroundColor: 'white',
              '&:hover': { backgroundColor: 'grey.100' }
            }}
          >
            <MyLocation />
          </IconButton>
        </Tooltip>
        
        <Tooltip title="Toggle Clustering">
          <IconButton 
            size="small" 
            onClick={toggleClusters}
            sx={{ 
              backgroundColor: showClusters ? 'primary.main' : 'white',
              color: showClusters ? 'white' : 'text.primary',
              '&:hover': { 
                backgroundColor: showClusters ? 'primary.dark' : 'grey.100' 
              }
            }}
          >
            <Layers />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Info Panel */}
      {data && (
        <Box sx={{ 
          position: 'absolute', 
          bottom: 10, 
          left: 10, 
          zIndex: 1000,
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          p: 1,
          borderRadius: 1,
          minWidth: 150
        }}>
          <Typography variant="caption" display="block">
            <strong>Points:</strong> {data.metadata.total_points}
          </Typography>
          <Typography variant="caption" display="block">
            <strong>Source:</strong> {data.metadata.data_source || 'Unknown'}
          </Typography>
          {data.metadata.clustering_enabled && (
            <Typography variant="caption" display="block" color="success.main">
              Clustering enabled
            </Typography>
          )}
        </Box>
      )}
    </Box>
  );
};

export default GeospatialMap;
