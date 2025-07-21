## Detailed Implementation Plan: Visual Analytics & Interactive Exploration

### Phase 1: Foundation Setup (Weeks 1-4)

#### 1.1 Frontend Package Dependencies
```json
{
  "dependencies": {
    "d3": "^7.8.5",
    "@types/d3": "^7.4.0",
    "cytoscape": "^3.26.0",
    "cytoscape-cola": "^2.5.1",
    "cytoscape-dagre": "^2.5.0",
    "vis-timeline": "^7.7.3",
    "vis-network": "^9.1.6",
    "leaflet": "^1.9.4",
    "@types/leaflet": "^1.9.8",
    "plotly.js": "^2.26.0",
    "three": "^0.156.1",
    "@types/three": "^0.156.0",
    "react-grid-layout": "^1.4.4",
    "react-dnd": "^16.0.1"
  }
}
```

#### 1.2 Backend API Structure
```python
# business_intel_scraper/backend/api/visualization.py
from fastapi import APIRouter, WebSocket, Depends
from typing import Dict, List, Any
import json

router = APIRouter(prefix="/api/v1/visualization", tags=["visualization"])

@router.get("/graph-data/{entity_type}")
async def get_graph_data(entity_type: str, filters: Dict = None):
    """Get network graph data for visualization"""
    pass

@router.get("/timeline-data/{entity_id}")
async def get_timeline_data(entity_id: str, time_range: str = "30d"):
    """Get temporal data for timeline visualization"""
    pass

@router.get("/geospatial-data")
async def get_geospatial_data(bounds: str = None):
    """Get geospatial data for map visualization"""
    pass

@router.websocket("/live-updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time visualization updates"""
    pass
```

### Phase 2: Dashboard Builder Implementation

#### 2.1 Dashboard Builder Component
```typescript
// frontend/src/components/dashboard/DashboardBuilder.tsx
import React, { useState, useCallback } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { WidgetLibrary } from './WidgetLibrary';
import { DragDropCanvas } from './DragDropCanvas';

interface DashboardConfig {
  id: string;
  name: string;
  widgets: WidgetConfig[];
  layout: LayoutItem[];
}

interface WidgetConfig {
  id: string;
  type: 'network-graph' | 'timeline' | 'map' | 'metrics' | 'custom-query';
  title: string;
  config: Record<string, any>;
}

export const DashboardBuilder: React.FC = () => {
  const [dashboard, setDashboard] = useState<DashboardConfig | null>(null);
  const [isEditMode, setIsEditMode] = useState(false);

  const handleWidgetAdd = useCallback((widgetType: string) => {
    // Add widget to dashboard
  }, []);

  const handleLayoutChange = useCallback((newLayout: LayoutItem[]) => {
    // Update dashboard layout
  }, []);

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="dashboard-builder">
        <div className="toolbar">
          <button onClick={() => setIsEditMode(!isEditMode)}>
            {isEditMode ? 'Exit Edit' : 'Edit Dashboard'}
          </button>
        </div>
        
        {isEditMode && <WidgetLibrary onWidgetAdd={handleWidgetAdd} />}
        
        <DragDropCanvas
          widgets={dashboard?.widgets || []}
          layout={dashboard?.layout || []}
          isEditMode={isEditMode}
          onLayoutChange={handleLayoutChange}
        />
      </div>
    </DndProvider>
  );
};
```

#### 2.2 Network Graph Widget
```typescript
// frontend/src/components/widgets/NetworkGraphWidget.tsx
import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import cola from 'cytoscape-cola';

cytoscape.use(cola);

interface NetworkGraphProps {
  data: {
    nodes: Array<{ id: string; label: string; group?: string }>;
    edges: Array<{ source: string; target: string; weight?: number }>;
  };
  layout: 'cola' | 'circle' | 'grid' | 'random';
  onNodeClick?: (node: any) => void;
}

export const NetworkGraphWidget: React.FC<NetworkGraphProps> = ({ 
  data, 
  layout, 
  onNodeClick 
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    cyRef.current = cytoscape({
      container: containerRef.current,
      elements: [
        ...data.nodes.map(node => ({ data: node })),
        ...data.edges.map(edge => ({ data: edge }))
      ],
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#666',
            'label': 'data(label)',
            'width': 30,
            'height': 30
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 3,
            'line-color': '#ccc',
            'target-arrow-color': '#ccc',
            'target-arrow-shape': 'triangle'
          }
        }
      ],
      layout: { name: layout }
    });

    cyRef.current.on('tap', 'node', (event) => {
      if (onNodeClick) {
        onNodeClick(event.target.data());
      }
    });

    return () => {
      cyRef.current?.destroy();
    };
  }, [data, layout, onNodeClick]);

  return <div ref={containerRef} style={{ width: '100%', height: '400px' }} />;
};
```

### Phase 3: Timeline Visualization

#### 3.1 Timeline Component
```typescript
// frontend/src/components/temporal/TimelineVisualization.tsx
import React, { useEffect, useRef } from 'react';
import { Timeline, DataSet } from 'vis-timeline/standalone';

interface TimelineEvent {
  id: string;
  content: string;
  start: Date;
  end?: Date;
  group?: string;
  className?: string;
}

interface TimelineProps {
  events: TimelineEvent[];
  groups?: Array<{ id: string; content: string }>;
  onEventSelect?: (event: TimelineEvent) => void;
}

export const TimelineVisualization: React.FC<TimelineProps> = ({ 
  events, 
  groups, 
  onEventSelect 
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const timelineRef = useRef<Timeline | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const items = new DataSet(events);
    const groupsDataSet = groups ? new DataSet(groups) : undefined;

    timelineRef.current = new Timeline(
      containerRef.current,
      items,
      groupsDataSet,
      {
        orientation: 'top',
        stack: true,
        showCurrentTime: true,
        zoomable: true,
        moveable: true
      }
    );

    timelineRef.current.on('select', (properties) => {
      if (onEventSelect && properties.items.length > 0) {
        const selectedEvent = events.find(e => e.id === properties.items[0]);
        if (selectedEvent) onEventSelect(selectedEvent);
      }
    });

    return () => {
      timelineRef.current?.destroy();
    };
  }, [events, groups, onEventSelect]);

  return <div ref={containerRef} style={{ width: '100%', height: '300px' }} />;
};
```

### Phase 4: Geospatial Visualization

#### 4.1 Interactive Map Component
```typescript
// frontend/src/components/geo/InteractiveMap.tsx
import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface MapPoint {
  id: string;
  lat: number;
  lng: number;
  popup?: string;
  icon?: string;
}

interface InteractiveMapProps {
  points: MapPoint[];
  center?: [number, number];
  zoom?: number;
  onPointClick?: (point: MapPoint) => void;
}

export const InteractiveMap: React.FC<InteractiveMapProps> = ({ 
  points, 
  center = [0, 0], 
  zoom = 2,
  onPointClick 
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!mapRef.current) return;

    mapInstanceRef.current = L.map(mapRef.current).setView(center, zoom);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(mapInstanceRef.current);

    return () => {
      mapInstanceRef.current?.remove();
    };
  }, []);

  useEffect(() => {
    if (!mapInstanceRef.current) return;

    // Clear existing markers
    mapInstanceRef.current.eachLayer((layer) => {
      if (layer instanceof L.Marker) {
        mapInstanceRef.current?.removeLayer(layer);
      }
    });

    // Add new markers
    points.forEach(point => {
      const marker = L.marker([point.lat, point.lng])
        .addTo(mapInstanceRef.current!);

      if (point.popup) {
        marker.bindPopup(point.popup);
      }

      marker.on('click', () => {
        if (onPointClick) onPointClick(point);
      });
    });
  }, [points, onPointClick]);

  return <div ref={mapRef} style={{ width: '100%', height: '400px' }} />;
};
```

### Phase 5: Real-time & Collaboration

#### 5.1 WebSocket Integration
```python
# business_intel_scraper/backend/websocket/visualization_handler.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio

class VisualizationConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_sessions: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        self.user_sessions[websocket] = session_id

    def disconnect(self, websocket: WebSocket):
        session_id = self.user_sessions.get(websocket)
        if session_id and session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
        if websocket in self.user_sessions:
            del self.user_sessions[websocket]

    async def broadcast_to_session(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    self.disconnect(connection)

manager = VisualizationConnectionManager()

async def handle_visualization_websocket(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message["type"] == "visualization_update":
                await manager.broadcast_to_session(session_id, {
                    "type": "visualization_changed",
                    "data": message["data"]
                })
            elif message["type"] == "cursor_move":
                await manager.broadcast_to_session(session_id, {
                    "type": "user_cursor",
                    "user_id": message["user_id"],
                    "position": message["position"]
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### Phase 6: Export & Sharing System

#### 6.1 Export Engine
```python
# business_intel_scraper/backend/export/visualization_exporter.py
from typing import Dict, Any, Optional
import base64
import io
from PIL import Image
import plotly.graph_objects as go
import plotly.io as pio

class VisualizationExporter:
    def __init__(self):
        self.supported_formats = ["png", "svg", "pdf", "html", "json"]

    async def export_visualization(
        self, 
        viz_config: Dict[str, Any], 
        format: str,
        width: int = 1200,
        height: int = 800
    ) -> bytes:
        """Export visualization in specified format"""
        
        if format not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format}")

        if viz_config["type"] == "network_graph":
            return await self._export_network_graph(viz_config, format, width, height)
        elif viz_config["type"] == "timeline":
            return await self._export_timeline(viz_config, format, width, height)
        elif viz_config["type"] == "map":
            return await self._export_map(viz_config, format, width, height)
        else:
            raise ValueError(f"Unknown visualization type: {viz_config['type']}")

    async def _export_network_graph(
        self, 
        config: Dict[str, Any], 
        format: str, 
        width: int, 
        height: int
    ) -> bytes:
        """Export network graph visualization"""
        # Implementation for network graph export
        pass

    async def generate_embed_code(self, viz_id: str, config: Dict[str, Any]) -> str:
        """Generate embeddable HTML/JS code for visualization"""
        embed_template = f"""
        <div id="visualization-{viz_id}" style="width: 100%; height: 400px;"></div>
        <script src="https://your-domain.com/embed.js"></script>
        <script>
            renderVisualization('{viz_id}', {config}, 'visualization-{viz_id}');
        </script>
        """
        return embed_template
```

### Implementation Order Summary

**Phase 1 (Weeks 1-4): Foundation**
1. Install visualization libraries
2. Create basic API structure
3. Set up WebSocket infrastructure
4. Database schema updates

**Phase 2 (Weeks 5-8): Dashboard Builder**
1. Drag-and-drop interface
2. Widget library
3. Layout management
4. Configuration persistence

**Phase 3 (Weeks 9-12): Network Graphs**
1. Cytoscape.js integration
2. Advanced layouts
3. Filtering system
4. Node/edge interactions

**Phase 4 (Weeks 13-16): Timeline**
1. vis.js Timeline integration
2. Event visualization
3. Animation controls
4. Time-based filtering

**Phase 5 (Weeks 17-20): Geospatial**
1. Leaflet.js integration
2. Map layers
3. Geographic clustering
4. Location search

**Phase 6 (Weeks 21-24): Real-time**
1. WebSocket handlers
2. Live updates
3. Collaborative editing
4. Conflict resolution

**Phase 7 (Weeks 25-28): Advanced Analytics**
1. Statistical overlays
2. ML integration
3. Anomaly detection
4. Predictive visualization

**Phase 8 (Weeks 29-32): Export/Share**
1. Export engine
2. Multiple formats
3. Embed system
4. Permission management

**Phase 9 (Weeks 33-36): Storyboarding**
1. Story builder
2. Presentation mode
3. Guided tours
4. Interactive tutorials

Each phase builds upon the previous ones, ensuring a working system at each milestone while progressively adding advanced features.
