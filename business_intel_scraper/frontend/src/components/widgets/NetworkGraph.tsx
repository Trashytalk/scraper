import React, { useEffect, useRef, useState } from 'react';
import { Box, CircularProgress, Alert, Typography, IconButton, Tooltip, FormControl, Select, MenuItem, InputLabel } from '@mui/material';
import { ZoomIn, ZoomOut, CenterFocusStrong, Refresh } from '@mui/icons-material';
import cytoscape from 'cytoscape';
import cola from 'cytoscape-cola';

// Register layout
cytoscape.use(cola);

interface NetworkGraphProps {
  height?: number;
  className?: string;
}

interface NetworkNode {
  id: string;
  label: string;
  group: string;
  size: number;
  color: string;
}

interface NetworkEdge {
  source: string;
  target: string;
  weight: number;
  type: string;
}

interface NetworkData {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  metadata: {
    total_nodes: number;
    total_edges: number;
    entity_type?: string;
    data_source?: string;
  };
}

const NetworkGraph: React.FC<NetworkGraphProps> = ({ 
  height = 500, 
  className 
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  
  const [data, setData] = useState<NetworkData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [layout, setLayout] = useState<string>('cola');

  const fetchNetworkData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/visualization/network-data');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load network data');
      console.error('Error fetching network data:', err);
    } finally {
      setLoading(false);
    }
  };

  const initializeCytoscape = () => {
    if (!containerRef.current || !data || cyRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      elements: [
        ...data.nodes.map(node => ({
          data: {
            id: node.id,
            label: node.label,
            group: node.group,
            size: node.size
          },
          style: {
            'background-color': node.color,
            'width': node.size,
            'height': node.size,
            'label': node.label,
            'text-valign': 'center',
            'color': '#fff',
            'text-outline-width': 2,
            'text-outline-color': '#000',
            'font-size': '12px',
            'cursor': 'pointer'
          }
        })),
        ...data.edges.map(edge => ({
          data: {
            id: `${edge.source}-${edge.target}`,
            source: edge.source,
            target: edge.target,
            weight: edge.weight,
            type: edge.type
          },
          style: {
            'width': Math.max(1, edge.weight * 3),
            'line-color': '#666',
            'target-arrow-color': '#666',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'opacity': 0.8,
            'cursor': 'pointer'
          }
        }))
      ],
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'color': '#fff',
            'text-outline-width': 2,
            'text-outline-color': '#000',
            'font-size': '10px'
          }
        },
        {
          selector: 'edge',
          style: {
            'curve-style': 'bezier',
            'target-arrow-shape': 'triangle',
            'opacity': 0.7
          }
        }
      ],
      layout: {
        name: layout,
        animate: false,
        animationDuration: 1000,
        fit: true,
        padding: 50
      } as any
    });

    // Add event listeners
    cy.on('tap', 'node', function(evt) {
      const node = evt.target;
      const nodeData = node.data();
      console.log('Node clicked:', nodeData);
    });

    cy.on('tap', 'edge', function(evt) {
      const edge = evt.target;
      const edgeData = edge.data();
      console.log('Edge clicked:', edgeData);
    });

    cyRef.current = cy;
  };

  const updateLayout = () => {
    if (cyRef.current) {
      cyRef.current.layout({
        name: layout,
        animate: false,
        animationDuration: 1000,
        fit: true,
        padding: 50
      } as any).run();
    }
  };

  useEffect(() => {
    fetchNetworkData();
  }, []);

  useEffect(() => {
    initializeCytoscape();
    
    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [data, layout]);

  const handleZoomIn = () => {
    if (cyRef.current) {
      cyRef.current.zoom(cyRef.current.zoom() * 1.2);
    }
  };

  const handleZoomOut = () => {
    if (cyRef.current) {
      cyRef.current.zoom(cyRef.current.zoom() * 0.8);
    }
  };

  const handleCenter = () => {
    if (cyRef.current) {
      cyRef.current.fit();
    }
  };

  const handleRefresh = () => {
    fetchNetworkData();
  };

  const handleLayoutChange = (event: any) => {
    setLayout(event.target.value);
  };

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
        <Typography sx={{ ml: 2 }}>Loading network data...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box className={className} sx={{ height: `${height}px`, p: 2 }}>
        <Alert severity="error">
          <Typography variant="body2">
            Error loading network: {error}
          </Typography>
        </Alert>
      </Box>
    );
  }

  return (
    <Box className={className} sx={{ position: 'relative', height: `${height}px` }}>
      {/* Network Container */}
      <div 
        ref={containerRef} 
        style={{ 
          width: '100%', 
          height: '100%',
          backgroundColor: '#fafafa',
          borderRadius: '4px'
        }} 
      />

      {/* Controls */}
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
        
        <Tooltip title="Center View">
          <IconButton 
            size="small" 
            onClick={handleCenter}
            sx={{ 
              backgroundColor: 'white',
              '&:hover': { backgroundColor: 'grey.100' }
            }}
          >
            <CenterFocusStrong />
          </IconButton>
        </Tooltip>
        
        <Tooltip title="Refresh Data">
          <IconButton 
            size="small" 
            onClick={handleRefresh}
            sx={{ 
              backgroundColor: 'white',
              '&:hover': { backgroundColor: 'grey.100' }
            }}
          >
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Layout Selector */}
      <Box sx={{ 
        position: 'absolute', 
        top: 10, 
        left: 10, 
        zIndex: 1000,
        minWidth: 120
      }}>
        <FormControl size="small" fullWidth>
          <InputLabel>Layout</InputLabel>
          <Select
            value={layout}
            label="Layout"
            onChange={handleLayoutChange}
            sx={{ backgroundColor: 'white' }}
          >
            <MenuItem value="cola">Cola</MenuItem>
            <MenuItem value="cose">Cose</MenuItem>
            <MenuItem value="circle">Circle</MenuItem>
            <MenuItem value="grid">Grid</MenuItem>
            <MenuItem value="breadthfirst">Breadth First</MenuItem>
            <MenuItem value="concentric">Concentric</MenuItem>
          </Select>
        </FormControl>
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
            <strong>Nodes:</strong> {data.metadata.total_nodes}
          </Typography>
          <Typography variant="caption" display="block">
            <strong>Edges:</strong> {data.metadata.total_edges}
          </Typography>
          <Typography variant="caption" display="block">
            <strong>Source:</strong> {data.metadata.data_source || 'Unknown'}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default NetworkGraph;
