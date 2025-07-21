# Sequential Implementation Action Plan
# Visual Analytics & Interactive Exploration Features

## IMMEDIATE NEXT STEPS (Week 1)

### Step 1: Frontend Library Setup
Execute these commands in the frontend directory:

```bash
cd business_intel_scraper/frontend
npm install --save d3 @types/d3
npm install --save cytoscape cytoscape-cola cytoscape-dagre
npm install --save vis-timeline vis-network
npm install --save leaflet @types/leaflet
npm install --save react-grid-layout react-dnd react-dnd-html5-backend
```

### Step 2: Create Basic Directory Structure
```bash
mkdir -p business_intel_scraper/frontend/src/components/visualization
mkdir -p business_intel_scraper/frontend/src/components/dashboard
mkdir -p business_intel_scraper/frontend/src/components/widgets
mkdir -p business_intel_scraper/backend/api/visualization
mkdir -p business_intel_scraper/backend/visualization
```

### Step 3: Create Foundation API Endpoint
Create `business_intel_scraper/backend/api/visualization.py`:

```python
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
import json

router = APIRouter(prefix="/visualization", tags=["visualization"])

@router.get("/network-data")
async def get_network_data(
    entity_type: str = Query("all", description="Entity type to visualize"),
    limit: int = Query(100, description="Maximum number of nodes"),
    filters: Optional[str] = Query(None, description="JSON filters")
) -> Dict[str, Any]:
    """Get network graph data for visualization"""
    # Placeholder implementation
    return {
        "nodes": [
            {"id": "1", "label": "Entity 1", "group": "type_a"},
            {"id": "2", "label": "Entity 2", "group": "type_b"},
        ],
        "edges": [
            {"source": "1", "target": "2", "weight": 1.0}
        ]
    }

@router.get("/timeline-data")
async def get_timeline_data(
    entity_id: Optional[str] = Query(None),
    time_range: str = Query("30d", description="Time range (e.g., 30d, 7d)")
) -> Dict[str, Any]:
    """Get timeline data for temporal visualization"""
    return {
        "events": [
            {
                "id": "1",
                "content": "Entity discovered",
                "start": "2024-01-01T00:00:00Z",
                "group": "discoveries"
            }
        ],
        "groups": [
            {"id": "discoveries", "content": "Discoveries"}
        ]
    }
```

## WEEK 1-2 PRIORITY TASKS

### Task 1: Basic Network Graph Component
Create `business_intel_scraper/frontend/src/components/widgets/NetworkGraph.tsx`:

```typescript
import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';

interface Node {
  id: string;
  label: string;
  group?: string;
}

interface Edge {
  source: string;
  target: string;
  weight?: number;
}

interface NetworkGraphProps {
  nodes: Node[];
  edges: Edge[];
  onNodeClick?: (node: Node) => void;
}

export const NetworkGraph: React.FC<NetworkGraphProps> = ({ 
  nodes, 
  edges, 
  onNodeClick 
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [cy, setCy] = useState<cytoscape.Core | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const cyInstance = cytoscape({
      container: containerRef.current,
      elements: [
        ...nodes.map(node => ({ data: { id: node.id, label: node.label } })),
        ...edges.map(edge => ({ data: { source: edge.source, target: edge.target } }))
      ],
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#3498db',
            'label': 'data(label)',
            'width': 40,
            'height': 40,
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '12px'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#95a5a6',
            'target-arrow-color': '#95a5a6',
            'target-arrow-shape': 'triangle'
          }
        }
      ],
      layout: { name: 'cose' }
    });

    cyInstance.on('tap', 'node', (event) => {
      const nodeData = event.target.data();
      const node = nodes.find(n => n.id === nodeData.id);
      if (node && onNodeClick) {
        onNodeClick(node);
      }
    });

    setCy(cyInstance);

    return () => {
      cyInstance.destroy();
    };
  }, [nodes, edges, onNodeClick]);

  return (
    <div 
      ref={containerRef} 
      style={{ 
        width: '100%', 
        height: '400px', 
        border: '1px solid #ddd',
        borderRadius: '4px'
      }} 
    />
  );
};
```

### Task 2: Integrate into Existing Dashboard
Modify `business_intel_scraper/frontend/src/components/AnalyticsDashboard.jsx` to include the new network graph:

```typescript
// Add import
import { NetworkGraph } from './widgets/NetworkGraph';

// Add to dashboard grid
<div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
  <h3 className="text-lg font-semibold text-gray-900 mb-4">Entity Network</h3>
  <NetworkGraph 
    nodes={networkData.nodes} 
    edges={networkData.edges}
    onNodeClick={(node) => console.log('Selected node:', node)}
  />
</div>
```

## WEEK 3-4 PRIORITY TASKS

### Task 3: Basic Timeline Component
Create `business_intel_scraper/frontend/src/components/widgets/Timeline.tsx`:

```typescript
import React, { useEffect, useRef } from 'react';
import { Timeline as VisTimeline, DataSet } from 'vis-timeline/standalone';

interface TimelineEvent {
  id: string;
  content: string;
  start: string;
  end?: string;
  group?: string;
}

interface TimelineProps {
  events: TimelineEvent[];
  onEventSelect?: (event: TimelineEvent) => void;
}

export const Timeline: React.FC<TimelineProps> = ({ events, onEventSelect }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const items = new DataSet(events);
    const timeline = new VisTimeline(containerRef.current, items, {
      orientation: 'top',
      stack: true,
      showCurrentTime: true
    });

    timeline.on('select', (properties) => {
      if (onEventSelect && properties.items.length > 0) {
        const selectedEvent = events.find(e => e.id === properties.items[0]);
        if (selectedEvent) onEventSelect(selectedEvent);
      }
    });

    return () => {
      timeline.destroy();
    };
  }, [events, onEventSelect]);

  return (
    <div 
      ref={containerRef} 
      style={{ 
        width: '100%', 
        height: '300px',
        border: '1px solid #ddd',
        borderRadius: '4px'
      }} 
    />
  );
};
```

### Task 4: Data Integration Layer
Create `business_intel_scraper/backend/visualization/data_processor.py`:

```python
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from ..db.models import *

class VisualizationDataProcessor:
    def __init__(self, db_session: Session):
        self.db = db_session

    async def get_entity_network_data(
        self, 
        entity_type: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Process database data for network visualization"""
        # Query entities and relationships from database
        # Transform to cytoscape format
        
        nodes = []
        edges = []
        
        # Example query (adapt to your models)
        entities = self.db.query(Entity).limit(limit).all()
        
        for entity in entities:
            nodes.append({
                "id": str(entity.id),
                "label": entity.name or entity.id,
                "group": entity.entity_type
            })
        
        # Query relationships
        relationships = self.db.query(EntityRelationship).limit(limit * 2).all()
        
        for rel in relationships:
            edges.append({
                "source": str(rel.source_entity_id),
                "target": str(rel.target_entity_id),
                "weight": rel.confidence_score or 1.0
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }
        }

    async def get_timeline_data(
        self, 
        entity_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Process temporal data for timeline visualization"""
        events = []
        
        # Query temporal events from database
        # Transform to vis-timeline format
        
        return {
            "events": events,
            "groups": [
                {"id": "discoveries", "content": "Entity Discoveries"},
                {"id": "updates", "content": "Data Updates"},
                {"id": "relationships", "content": "Relationship Changes"}
            ]
        }
```

## IMPLEMENTATION CHECKLIST

### Phase 1 Foundation (Weeks 1-4)
- [ ] Install frontend visualization libraries
- [ ] Create directory structure
- [ ] Build basic API endpoints
- [ ] Create NetworkGraph component
- [ ] Create Timeline component
- [ ] Build data processing layer
- [ ] Integrate with existing dashboard

### Quick Wins to Demonstrate Progress
1. **Week 1**: Working network graph showing existing entity relationships
2. **Week 2**: Timeline showing entity discovery dates
3. **Week 3**: Interactive node selection and filtering
4. **Week 4**: Real-time data updates via API

### Success Metrics
- [ ] Network graph displays 100+ nodes smoothly
- [ ] Timeline shows entity lifecycle events
- [ ] Components integrate with existing dashboard
- [ ] API responses under 500ms
- [ ] No performance degradation to existing features

## TECHNICAL DEPENDENCIES

### Frontend Requirements
```json
{
  "react": ">=18.0.0",
  "typescript": ">=4.5.0",
  "d3": "^7.8.5",
  "cytoscape": "^3.26.0",
  "vis-timeline": "^7.7.3"
}
```

### Backend Requirements
```python
# requirements.txt additions
fastapi-websocket>=0.1.0
plotly>=5.0.0
networkx>=3.0.0
```

### Database Schema Updates
```sql
-- Add visualization configuration table
CREATE TABLE IF NOT EXISTS visualization_configs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    dashboard_name VARCHAR(255),
    config_json JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add indexes for performance
CREATE INDEX idx_entities_type ON entities(entity_type);
CREATE INDEX idx_relationships_entities ON entity_relationships(source_entity_id, target_entity_id);
```

## RISK MITIGATION

### Performance Concerns
- Start with small datasets (100-500 nodes)
- Implement pagination and lazy loading
- Use data virtualization for large graphs

### Browser Compatibility
- Test on Chrome, Firefox, Safari
- Provide fallbacks for older browsers
- Progressive enhancement approach

### Integration Issues
- Create feature flags for new components
- Maintain backward compatibility
- Isolated component development

This plan provides a clear path from the current basic visualization to comprehensive Visual Analytics & Interactive Exploration features, with concrete next steps and measurable milestones.
