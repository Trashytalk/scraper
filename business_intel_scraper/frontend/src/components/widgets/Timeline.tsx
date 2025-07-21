import React, { useEffect, useRef, useState } from 'react';
import { Timeline as VisTimeline, DataSet } from 'vis-timeline/standalone';
import 'vis-timeline/styles/vis-timeline-graph2d.css';

interface TimelineEvent {
  id: string;
  content: string;
  start: string;
  end?: string;
  group?: string;
  className?: string;
  type?: 'point' | 'box' | 'range' | 'background';
  title?: string;
}

interface TimelineGroup {
  id: string;
  content: string;
  className?: string;
}

interface TimelineProps {
  events: TimelineEvent[];
  groups?: TimelineGroup[];
  onEventSelect?: (event: TimelineEvent) => void;
  onRangeChanged?: (start: Date, end: Date) => void;
  height?: string;
  style?: React.CSSProperties;
  options?: any;
}

export const Timeline: React.FC<TimelineProps> = ({ 
  events, 
  groups,
  onEventSelect,
  onRangeChanged,
  height = '300px',
  style = {},
  options = {}
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const timelineRef = useRef<VisTimeline | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    if (!containerRef.current) return;

    // Create timeline items dataset
    const items = new DataSet(events.map(event => ({
      ...event,
      start: new Date(event.start),
      end: event.end ? new Date(event.end) : undefined,
      type: event.type || 'point'
    })));

    // Create groups dataset if provided
    const groupsDataSet = groups ? new DataSet(groups) : undefined;

    // Timeline configuration
    const timelineOptions = {
      orientation: 'top',
      stack: true,
      showCurrentTime: true,
      zoomable: true,
      moveable: true,
      selectable: true,
      multiselect: false,
      editable: false,
      tooltip: {
        followMouse: true,
        overflowMethod: 'cap'
      },
      format: {
        minorLabels: {
          millisecond: 'SSS',
          second: 's',
          minute: 'HH:mm',
          hour: 'HH:mm',
          weekday: 'ddd D',
          day: 'D',
          week: 'w',
          month: 'MMM',
          year: 'YYYY'
        },
        majorLabels: {
          millisecond: 'HH:mm:ss',
          second: 'D MMMM HH:mm',
          minute: 'ddd D MMMM',
          hour: 'ddd D MMMM',
          weekday: 'MMMM YYYY',
          day: 'MMMM YYYY',
          week: 'MMMM YYYY',
          month: 'YYYY',
          year: ''
        }
      },
      ...options
    };

    // Create timeline instance
    timelineRef.current = new VisTimeline(
      containerRef.current,
      items,
      groupsDataSet,
      timelineOptions
    );

    // Event selection handler
    timelineRef.current.on('select', (properties) => {
      if (properties.items.length > 0) {
        const selectedId = properties.items[0];
        setSelectedEvent(selectedId);
        
        const selectedEventData = events.find(e => e.id === selectedId);
        if (selectedEventData && onEventSelect) {
          onEventSelect(selectedEventData);
        }
      } else {
        setSelectedEvent(null);
      }
    });

    // Range change handler
    timelineRef.current.on('rangechanged', (properties) => {
      if (onRangeChanged) {
        onRangeChanged(properties.start, properties.end);
      }
    });

    // Update current time periodically
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date());
      if (timelineRef.current) {
        timelineRef.current.setCurrentTime(new Date());
      }
    }, 60000); // Update every minute

    return () => {
      clearInterval(timeInterval);
      timelineRef.current?.destroy();
    };
  }, [events, groups, onEventSelect, onRangeChanged, options]);

  // Control functions
  const zoomIn = () => {
    if (timelineRef.current) {
      timelineRef.current.zoomIn(0.2);
    }
  };

  const zoomOut = () => {
    if (timelineRef.current) {
      timelineRef.current.zoomOut(0.2);
    }
  };

  const fit = () => {
    if (timelineRef.current) {
      timelineRef.current.fit();
    }
  };

  const moveToNow = () => {
    if (timelineRef.current) {
      timelineRef.current.moveTo(new Date());
    }
  };

  return (
    <div style={{ position: 'relative', ...style }}>
      {/* Timeline controls */}
      <div style={{
        position: 'absolute',
        top: '10px',
        left: '10px',
        zIndex: 1000,
        display: 'flex',
        gap: '5px',
        flexWrap: 'wrap'
      }}>
        <button
          onClick={zoomIn}
          style={{
            padding: '4px 8px',
            fontSize: '12px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            backgroundColor: '#fff',
            cursor: 'pointer'
          }}
          title="Zoom In"
        >
          🔍+
        </button>
        <button
          onClick={zoomOut}
          style={{
            padding: '4px 8px',
            fontSize: '12px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            backgroundColor: '#fff',
            cursor: 'pointer'
          }}
          title="Zoom Out"
        >
          🔍-
        </button>
        <button
          onClick={fit}
          style={{
            padding: '4px 8px',
            fontSize: '12px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            backgroundColor: '#fff',
            cursor: 'pointer'
          }}
          title="Fit All"
        >
          📏
        </button>
        <button
          onClick={moveToNow}
          style={{
            padding: '4px 8px',
            fontSize: '12px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            backgroundColor: '#fff',
            cursor: 'pointer'
          }}
          title="Go to Now"
        >
          🕒
        </button>
      </div>

      {/* Timeline stats */}
      <div style={{
        position: 'absolute',
        top: '10px',
        right: '10px',
        zIndex: 1000,
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        padding: '8px',
        borderRadius: '4px',
        fontSize: '12px',
        border: '1px solid #ddd'
      }}>
        <div>Events: {events.length}</div>
        {groups && <div>Groups: {groups.length}</div>}
        {selectedEvent && <div>Selected: {selectedEvent}</div>}
      </div>

      {/* Main timeline container */}
      <div 
        ref={containerRef} 
        style={{ 
          width: '100%', 
          height,
          border: '1px solid #ddd',
          borderRadius: '4px',
          backgroundColor: '#fff'
        }} 
      />
    </div>
  );
};
