#!/bin/bash

# Visual Analytics Implementation Starter Script
# This script sets up the foundation for Visual Analytics features

echo "🚀 Starting Visual Analytics Implementation Setup..."

# Check if we're in the right directory
if [ ! -f "business_intel_scraper/frontend/package.json" ]; then
    echo "❌ Error: Run this script from the scraper root directory"
    exit 1
fi

echo "📦 Installing frontend visualization libraries..."
cd business_intel_scraper/frontend

# Install core visualization libraries
npm install --save d3 @types/d3
npm install --save cytoscape cytoscape-cola cytoscape-dagre
npm install --save vis-timeline vis-network
npm install --save leaflet @types/leaflet
npm install --save react-grid-layout react-dnd react-dnd-html5-backend

echo "📁 Creating directory structure..."
cd ../../

# Create visualization directories
mkdir -p business_intel_scraper/frontend/src/components/visualization
mkdir -p business_intel_scraper/frontend/src/components/dashboard  
mkdir -p business_intel_scraper/frontend/src/components/widgets
mkdir -p business_intel_scraper/backend/api/visualization
mkdir -p business_intel_scraper/backend/visualization

echo "📄 Creating initial component files..."

# Create basic NetworkGraph component
cat > business_intel_scraper/frontend/src/components/widgets/NetworkGraph.tsx << 'EOF'
import React, { useEffect, useRef, useState } from 'react';

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

  useEffect(() => {
    // TODO: Implement Cytoscape.js integration
    console.log('NetworkGraph: nodes=', nodes.length, 'edges=', edges.length);
  }, [nodes, edges]);

  return (
    <div 
      ref={containerRef} 
      style={{ 
        width: '100%', 
        height: '400px', 
        border: '1px solid #ddd',
        borderRadius: '4px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#f8f9fa'
      }} 
    >
      <div style={{ textAlign: 'center', color: '#666' }}>
        <div>Network Graph Component</div>
        <div style={{ fontSize: '14px', marginTop: '8px' }}>
          {nodes.length} nodes, {edges.length} edges
        </div>
        <div style={{ fontSize: '12px', marginTop: '4px' }}>
          Cytoscape.js integration pending
        </div>
      </div>
    </div>
  );
};
EOF

# Create basic Timeline component
cat > business_intel_scraper/frontend/src/components/widgets/Timeline.tsx << 'EOF'
import React, { useRef } from 'react';

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

  return (
    <div 
      ref={containerRef} 
      style={{ 
        width: '100%', 
        height: '300px',
        border: '1px solid #ddd',
        borderRadius: '4px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#f8f9fa'
      }}
    >
      <div style={{ textAlign: 'center', color: '#666' }}>
        <div>Timeline Component</div>
        <div style={{ fontSize: '14px', marginTop: '8px' }}>
          {events.length} events
        </div>
        <div style={{ fontSize: '12px', marginTop: '4px' }}>
          vis.js Timeline integration pending
        </div>
      </div>
    </div>
  );
};
EOF

# Create visualization API endpoint
cat > business_intel_scraper/backend/api/visualization.py << 'EOF'
from fastapi import APIRouter, Query
from typing import Dict, List, Any, Optional

router = APIRouter(prefix="/visualization", tags=["visualization"])

@router.get("/network-data")
async def get_network_data(
    entity_type: str = Query("all", description="Entity type to visualize"),
    limit: int = Query(100, description="Maximum number of nodes")
) -> Dict[str, Any]:
    """Get network graph data for visualization"""
    # TODO: Integrate with actual database
    return {
        "nodes": [
            {"id": "1", "label": "Sample Entity 1", "group": "type_a"},
            {"id": "2", "label": "Sample Entity 2", "group": "type_b"},
            {"id": "3", "label": "Sample Entity 3", "group": "type_a"},
        ],
        "edges": [
            {"source": "1", "target": "2", "weight": 1.0},
            {"source": "2", "target": "3", "weight": 0.8},
        ],
        "metadata": {
            "total_nodes": 3,
            "total_edges": 2,
            "status": "demo_data"
        }
    }

@router.get("/timeline-data")
async def get_timeline_data(
    entity_id: Optional[str] = Query(None),
    time_range: str = Query("30d", description="Time range")
) -> Dict[str, Any]:
    """Get timeline data for temporal visualization"""
    # TODO: Integrate with actual database
    return {
        "events": [
            {
                "id": "1",
                "content": "Entity discovered",
                "start": "2024-01-01T00:00:00Z",
                "group": "discoveries"
            },
            {
                "id": "2", 
                "content": "Data updated",
                "start": "2024-01-15T00:00:00Z",
                "group": "updates"
            }
        ],
        "groups": [
            {"id": "discoveries", "content": "Discoveries"},
            {"id": "updates", "content": "Updates"}
        ]
    }
EOF

# Create data processor
cat > business_intel_scraper/backend/visualization/data_processor.py << 'EOF'
from typing import Dict, List, Any, Optional

class VisualizationDataProcessor:
    """Process database data for visualization components"""
    
    def __init__(self):
        pass

    async def get_entity_network_data(
        self, 
        entity_type: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Process database data for network visualization"""
        # TODO: Implement actual database integration
        
        nodes = [
            {"id": "1", "label": "Entity 1", "group": "type_a"},
            {"id": "2", "label": "Entity 2", "group": "type_b"},
        ]
        
        edges = [
            {"source": "1", "target": "2", "weight": 1.0}
        ]
        
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
        # TODO: Implement actual database integration
        
        events = []
        
        return {
            "events": events,
            "groups": [
                {"id": "discoveries", "content": "Entity Discoveries"},
                {"id": "updates", "content": "Data Updates"},
            ]
        }
EOF

# Create __init__.py files
touch business_intel_scraper/backend/visualization/__init__.py

echo "📝 Creating integration guide..."
cat > VISUALIZATION_INTEGRATION_GUIDE.md << 'EOF'
# Visual Analytics Integration Guide

## What was set up:

### Frontend Components Created:
- `business_intel_scraper/frontend/src/components/widgets/NetworkGraph.tsx`
- `business_intel_scraper/frontend/src/components/widgets/Timeline.tsx`

### Backend API Created:
- `business_intel_scraper/backend/api/visualization.py`
- `business_intel_scraper/backend/visualization/data_processor.py`

### Libraries Installed:
- d3, cytoscape, vis-timeline, leaflet
- react-grid-layout, react-dnd

## Next Steps:

### 1. Register the API router
Add to `business_intel_scraper/backend/api/main.py`:
```python
from .visualization import router as visualization_router
app.include_router(visualization_router)
```

### 2. Import and use components
In your dashboard file, add:
```typescript
import { NetworkGraph } from './widgets/NetworkGraph';
import { Timeline } from './widgets/Timeline';

// Use in component:
<NetworkGraph nodes={networkData.nodes} edges={networkData.edges} />
<Timeline events={timelineData.events} />
```

### 3. Implement Cytoscape.js integration
In NetworkGraph.tsx, replace the placeholder with:
```typescript
import cytoscape from 'cytoscape';
// Add actual cytoscape implementation
```

### 4. Connect to real data
Replace placeholder data in visualization.py with actual database queries.

## Test the setup:
1. Start the backend server
2. Visit `/docs` to see the new visualization endpoints
3. Import and test the components in your frontend

## Phase 1 Complete Checklist:
- [ ] API endpoints returning data
- [ ] Components rendering placeholders
- [ ] Cytoscape.js integration
- [ ] Timeline integration
- [ ] Database connection
- [ ] Integration with existing dashboard
EOF

echo "✅ Visual Analytics foundation setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Register the API router in main.py"
echo "2. Import components in your dashboard"
echo "3. Implement Cytoscape.js integration"
echo "4. Connect to real database data"
echo ""
echo "📖 See VISUALIZATION_INTEGRATION_GUIDE.md for detailed instructions"
echo ""
echo "🧪 Test the API endpoints at: http://localhost:8000/docs"
