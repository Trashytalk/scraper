import React, { useEffect, useRef, useState } from 'react';
import { Box, CircularProgress, Alert, Typography, IconButton, Tooltip } from '@mui/material';
import { ZoomIn, ZoomOut, Refresh, PlayArrow } from '@mui/icons-material';
import { Timeline as VisTimeline, DataSet } from 'vis-timeline/standalone';
import 'vis-timeline/styles/vis-timeline-graph2d.css';

interface TimelineProps {
  height?: number;
  className?: string;
}

interface TimelineEvent {
  id: string;
  content: string;
  start: string;
  group: string;
  type: string;
  title?: string;
}

interface TimelineGroup {
  id: string;
  content: string;
}

interface TimelineData {
  events: TimelineEvent[];
  groups: TimelineGroup[];
  metadata: {
    total_events: number;
    time_range: string;
    entity_id?: string;
    data_source?: string;
  };
}

const Timeline = ({ 
  height = 400, 
  className 
}: TimelineProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const timelineRef = useRef<VisTimeline | null>(null);
  
  const [data, setData] = useState<TimelineData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<string | null>(null);

  const fetchTimelineData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/visualization/timeline-data');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load timeline data');
      console.error('Error fetching timeline data:', err);
    } finally {
      setLoading(false);
    }
  };

  const initializeTimeline = () => {
    if (!containerRef.current || !data || timelineRef.current) return;

    // Create timeline items dataset
    const items = new DataSet(data.events.map(event => ({
      id: event.id,
      content: event.content,
      start: new Date(event.start),
      group: event.group,
      type: event.type || 'point',
      title: event.title || event.content,
      className: `timeline-${event.group}`
    })));

    // Create groups dataset
    const groups = new DataSet(data.groups.map(group => ({
      id: group.id,
      content: group.content,
      className: `group-${group.id}`
    })));

    // Timeline options
      const options = {
        groupOrder: 'content',
        editable: false,
        showCurrentTime: true,
        height: height,
        margin: {
          item: 10,
          axis: 20
        },
        orientation: 'top',
        zoomMin: 1000 * 60 * 60 * 24, // one day
        zoomMax: 1000 * 60 * 60 * 24 * 365, // one year
        stack: true,
        tooltip: {
          followMouse: true,
          overflowMethod: 'flip' as const
        }
      };    // Create timeline
    const timeline = new VisTimeline(containerRef.current, items, groups, options);

    // Add event listeners
    timeline.on('select', (properties) => {
      const selectedItems = properties.items;
      if (selectedItems && selectedItems.length > 0) {
        setSelectedEvent(selectedItems[0]);
        console.log('Event selected:', selectedItems[0]);
      } else {
        setSelectedEvent(null);
      }
    });

    timeline.on('rangechanged', (properties) => {
      console.log('Timeline range changed:', properties);
    });

    timelineRef.current = timeline;
  };

  useEffect(() => {
    fetchTimelineData();
  }, []);

  useEffect(() => {
    initializeTimeline();
    
    return () => {
      if (timelineRef.current) {
        timelineRef.current.destroy();
        timelineRef.current = null;
      }
    };
  }, [data]);

  const handleZoomIn = () => {
    if (timelineRef.current) {
      timelineRef.current.zoomIn(0.2);
    }
  };

  const handleZoomOut = () => {
    if (timelineRef.current) {
      timelineRef.current.zoomOut(0.2);
    }
  };

  const handleRefresh = () => {
    fetchTimelineData();
  };

  const handleFit = () => {
    if (timelineRef.current) {
      timelineRef.current.fit();
    }
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
        <Typography sx={{ ml: 2 }}>Loading timeline data...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box className={className} sx={{ height: `${height}px`, p: 2 }}>
        <Alert severity="error">
          <Typography variant="body2">
            Error loading timeline: {error}
          </Typography>
        </Alert>
      </Box>
    );
  }

  return (
    <Box className={className} sx={{ position: 'relative', height: `${height}px` }}>
      {/* Timeline Container */}
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
        
        <Tooltip title="Fit to View">
          <IconButton 
            size="small" 
            onClick={handleFit}
            sx={{ 
              backgroundColor: 'white',
              '&:hover': { backgroundColor: 'grey.100' }
            }}
          >
            <PlayArrow />
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
            <strong>Events:</strong> {data.metadata.total_events}
          </Typography>
          <Typography variant="caption" display="block">
            <strong>Range:</strong> {data.metadata.time_range}
          </Typography>
          <Typography variant="caption" display="block">
            <strong>Source:</strong> {data.metadata.data_source || 'Unknown'}
          </Typography>
          {selectedEvent && (
            <Typography variant="caption" display="block" color="primary">
              Selected: {selectedEvent}
            </Typography>
          )}
        </Box>
      )}
    </Box>
  );
};

export default Timeline;
