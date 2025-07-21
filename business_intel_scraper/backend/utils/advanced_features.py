"""
Advanced Features Module for Visual Analytics Platform
Real-time collaboration, advanced filtering, and custom dashboard builder
"""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional, Set, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
from websockets.server import serve as websocket_serve
from websockets.exceptions import ConnectionClosed, WebSocketException
import logging
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy import and_, or_, func, text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class EventType(Enum):
    """WebSocket event types for real-time collaboration"""
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    CURSOR_MOVED = "cursor_moved"
    SELECTION_CHANGED = "selection_changed"
    DATA_FILTERED = "data_filtered"
    VIEW_CHANGED = "view_changed"
    ANNOTATION_ADDED = "annotation_added"
    ANNOTATION_UPDATED = "annotation_updated"
    ANNOTATION_DELETED = "annotation_deleted"
    DASHBOARD_UPDATED = "dashboard_updated"
    BROADCAST = "broadcast"

@dataclass
class CollaborationEvent:
    """Data structure for collaboration events"""
    event_type: EventType
    user_id: str
    session_id: str
    timestamp: datetime
    data: Dict[str, Any]
    room_id: str = "default"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class FilterCriteria:
    """Advanced filtering criteria structure"""
    field: str
    operator: str  # eq, ne, gt, lt, gte, lte, in, not_in, contains, regex
    value: Any
    data_type: str = "string"  # string, number, date, boolean, array
    
class AdvancedFilters:
    """Advanced filtering system with complex query building"""
    
    OPERATORS = {
        'eq': '==',
        'ne': '!=', 
        'gt': '>',
        'lt': '<',
        'gte': '>=',
        'lte': '<=',
        'in': 'IN',
        'not_in': 'NOT IN',
        'contains': 'LIKE',
        'not_contains': 'NOT LIKE',
        'starts_with': 'LIKE',
        'ends_with': 'LIKE',
        'regex': 'REGEXP',
        'is_null': 'IS NULL',
        'is_not_null': 'IS NOT NULL',
        'between': 'BETWEEN'
    }
    
    def __init__(self):
        self.active_filters: Dict[str, List[FilterCriteria]] = {}
        self.filter_groups: Dict[str, Dict] = {}
        self.saved_filters: Dict[str, Dict] = {}
    
    def add_filter(self, group_id: str, criteria: FilterCriteria):
        """Add a filter criteria to a group"""
        if group_id not in self.active_filters:
            self.active_filters[group_id] = []
        
        self.active_filters[group_id].append(criteria)
        logger.debug(f"Added filter to group {group_id}: {criteria}")
    
    def remove_filter(self, group_id: str, field: str):
        """Remove filter by field name"""
        if group_id in self.active_filters:
            self.active_filters[group_id] = [
                f for f in self.active_filters[group_id] 
                if f.field != field
            ]
    
    def clear_group(self, group_id: str):
        """Clear all filters in a group"""
        if group_id in self.active_filters:
            del self.active_filters[group_id]
    
    def build_sql_query(self, base_query, model_class) -> str:
        """Build SQL query with filters applied"""
        conditions = []
        
        for group_id, filters in self.active_filters.items():
            group_conditions = []
            
            for criteria in filters:
                condition = self._build_condition(criteria, model_class)
                if condition is not None:
                    group_conditions.append(condition)
            
            if group_conditions:
                # Join conditions within group with AND
                if len(group_conditions) == 1:
                    conditions.append(group_conditions[0])
                else:
                    conditions.append(and_(*group_conditions))
        
        # Join groups with OR (each group is an alternative set of conditions)
        if conditions:
            if len(conditions) == 1:
                return base_query.filter(conditions[0])
            else:
                return base_query.filter(or_(*conditions))
        
        return base_query
    
    def _build_condition(self, criteria: FilterCriteria, model_class):
        """Build individual filter condition"""
        try:
            # Get the model attribute
            if not hasattr(model_class, criteria.field):
                logger.warning(f"Field {criteria.field} not found in model {model_class}")
                return None
            
            attr = getattr(model_class, criteria.field)
            
            # Handle different operators
            if criteria.operator == 'eq':
                return attr == criteria.value
            elif criteria.operator == 'ne':
                return attr != criteria.value
            elif criteria.operator == 'gt':
                return attr > criteria.value
            elif criteria.operator == 'lt':
                return attr < criteria.value
            elif criteria.operator == 'gte':
                return attr >= criteria.value
            elif criteria.operator == 'lte':
                return attr <= criteria.value
            elif criteria.operator == 'in':
                return attr.in_(criteria.value if isinstance(criteria.value, list) else [criteria.value])
            elif criteria.operator == 'not_in':
                return ~attr.in_(criteria.value if isinstance(criteria.value, list) else [criteria.value])
            elif criteria.operator == 'contains':
                return attr.contains(criteria.value)
            elif criteria.operator == 'not_contains':
                return ~attr.contains(criteria.value)
            elif criteria.operator == 'starts_with':
                return attr.startswith(criteria.value)
            elif criteria.operator == 'ends_with':
                return attr.endswith(criteria.value)
            elif criteria.operator == 'is_null':
                return attr.is_(None)
            elif criteria.operator == 'is_not_null':
                return attr.isnot(None)
            elif criteria.operator == 'between':
                if isinstance(criteria.value, list) and len(criteria.value) == 2:
                    return attr.between(criteria.value[0], criteria.value[1])
            elif criteria.operator == 'regex':
                return attr.op('REGEXP')(criteria.value)
            
            logger.warning(f"Unsupported operator: {criteria.operator}")
            return None
            
        except Exception as e:
            logger.error(f"Error building filter condition: {e}")
            return None
    
    def save_filter_set(self, name: str, description: str = ""):
        """Save current filter configuration"""
        self.saved_filters[name] = {
            'filters': {k: [asdict(f) for f in v] for k, v in self.active_filters.items()},
            'description': description,
            'created_at': datetime.utcnow().isoformat()
        }
    
    def load_filter_set(self, name: str) -> bool:
        """Load saved filter configuration"""
        if name in self.saved_filters:
            saved = self.saved_filters[name]
            self.active_filters = {}
            
            for group_id, filters in saved['filters'].items():
                self.active_filters[group_id] = [
                    FilterCriteria(**f) for f in filters
                ]
            return True
        return False
    
    def get_filter_summary(self) -> Dict[str, Any]:
        """Get summary of active filters"""
        summary = {
            'total_groups': len(self.active_filters),
            'total_filters': sum(len(filters) for filters in self.active_filters.values()),
            'groups': {}
        }
        
        for group_id, filters in self.active_filters.items():
            summary['groups'][group_id] = {
                'count': len(filters),
                'fields': list(set(f.field for f in filters)),
                'operators': list(set(f.operator for f in filters))
            }
        
        return summary

class CollaborationManager:
    """Real-time collaboration management"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.room_participants: Dict[str, Set[str]] = {}
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}
        self.user_cursors: Dict[str, Dict] = {}
        self.shared_annotations: Dict[str, List[Dict]] = {}
    
    async def add_participant(self, websocket: WebSocket, user_id: str, room_id: str = "default"):
        """Add participant to collaboration session"""
        session_id = str(uuid.uuid4())
        
        # Accept WebSocket connection
        await websocket.accept()
        
        # Store connection info
        self.websocket_connections[session_id] = websocket
        self.active_sessions[session_id] = {
            'user_id': user_id,
            'room_id': room_id,
            'joined_at': datetime.utcnow(),
            'last_activity': datetime.utcnow()
        }
        
        # Add to room
        if room_id not in self.room_participants:
            self.room_participants[room_id] = set()
        self.room_participants[room_id].add(session_id)
        
        # Notify others about new participant
        event = CollaborationEvent(
            event_type=EventType.USER_JOINED,
            user_id=user_id,
            session_id=session_id,
            room_id=room_id,
            timestamp=datetime.utcnow(),
            data={'user_id': user_id}
        )
        
        await self.broadcast_to_room(room_id, event, exclude_session=session_id)
        
        # Send current state to new participant
        await self._send_current_state(websocket, room_id)
        
        logger.info(f"User {user_id} joined room {room_id} (session: {session_id})")
        return session_id
    
    async def remove_participant(self, session_id: str):
        """Remove participant from collaboration session"""
        if session_id not in self.active_sessions:
            return
        
        session_info = self.active_sessions[session_id]
        room_id = session_info['room_id']
        user_id = session_info['user_id']
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        # Remove from room
        if room_id in self.room_participants:
            self.room_participants[room_id].discard(session_id)
            if not self.room_participants[room_id]:
                del self.room_participants[room_id]
        
        # Remove WebSocket connection
        if session_id in self.websocket_connections:
            del self.websocket_connections[session_id]
        
        # Remove user cursor
        if user_id in self.user_cursors:
            del self.user_cursors[user_id]
        
        # Notify others
        event = CollaborationEvent(
            event_type=EventType.USER_LEFT,
            user_id=user_id,
            session_id=session_id,
            room_id=room_id,
            timestamp=datetime.utcnow(),
            data={'user_id': user_id}
        )
        
        await self.broadcast_to_room(room_id, event)
        
        logger.info(f"User {user_id} left room {room_id} (session: {session_id})")
    
    async def handle_event(self, session_id: str, event_data: Dict[str, Any]):
        """Handle incoming collaboration event"""
        if session_id not in self.active_sessions:
            return
        
        session_info = self.active_sessions[session_id]
        session_info['last_activity'] = datetime.utcnow()
        
        try:
            event_type = EventType(event_data['event_type'])
            
            event = CollaborationEvent(
                event_type=event_type,
                user_id=session_info['user_id'],
                session_id=session_id,
                room_id=session_info['room_id'],
                timestamp=datetime.utcnow(),
                data=event_data.get('data', {})
            )
            
            # Handle specific event types
            if event_type == EventType.CURSOR_MOVED:
                self.user_cursors[session_info['user_id']] = event.data
            elif event_type == EventType.ANNOTATION_ADDED:
                room_id = session_info['room_id']
                if room_id not in self.shared_annotations:
                    self.shared_annotations[room_id] = []
                self.shared_annotations[room_id].append({
                    'id': str(uuid.uuid4()),
                    'user_id': session_info['user_id'],
                    'created_at': datetime.utcnow().isoformat(),
                    **event.data
                })
            elif event_type == EventType.ANNOTATION_DELETED:
                room_id = session_info['room_id']
                annotation_id = event.data.get('id')
                if room_id in self.shared_annotations and annotation_id:
                    self.shared_annotations[room_id] = [
                        a for a in self.shared_annotations[room_id]
                        if a['id'] != annotation_id
                    ]
            
            # Broadcast event to room participants
            await self.broadcast_to_room(
                session_info['room_id'], 
                event, 
                exclude_session=session_id
            )
            
            # Call registered event handlers
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.error(f"Event handler error: {e}")
            
        except ValueError as e:
            logger.error(f"Invalid event type: {e}")
        except Exception as e:
            logger.error(f"Error handling collaboration event: {e}")
    
    async def broadcast_to_room(self, room_id: str, event: CollaborationEvent, exclude_session: str = None):
        """Broadcast event to all participants in a room"""
        if room_id not in self.room_participants:
            return
        
        message = json.dumps(event.to_dict())
        disconnected_sessions = []
        
        for session_id in self.room_participants[room_id]:
            if session_id == exclude_session:
                continue
            
            if session_id in self.websocket_connections:
                try:
                    websocket = self.websocket_connections[session_id]
                    await websocket.send_text(message)
                except (ConnectionClosed, WebSocketDisconnect, WebSocketException):
                    disconnected_sessions.append(session_id)
                except Exception as e:
                    logger.error(f"Error broadcasting to session {session_id}: {e}")
                    disconnected_sessions.append(session_id)
        
        # Clean up disconnected sessions
        for session_id in disconnected_sessions:
            await self.remove_participant(session_id)
    
    async def _send_current_state(self, websocket: WebSocket, room_id: str):
        """Send current room state to new participant"""
        state = {
            'event_type': 'room_state',
            'data': {
                'participants': [
                    {
                        'user_id': self.active_sessions[session_id]['user_id'],
                        'joined_at': self.active_sessions[session_id]['joined_at'].isoformat()
                    }
                    for session_id in self.room_participants.get(room_id, set())
                ],
                'cursors': self.user_cursors,
                'annotations': self.shared_annotations.get(room_id, [])
            }
        }
        
        try:
            await websocket.send_text(json.dumps(state))
        except Exception as e:
            logger.error(f"Error sending room state: {e}")
    
    def register_event_handler(self, event_type: EventType, handler: Callable):
        """Register event handler for specific event type"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def get_room_stats(self, room_id: str) -> Dict[str, Any]:
        """Get statistics for a room"""
        if room_id not in self.room_participants:
            return {'participants': 0, 'annotations': 0}
        
        return {
            'participants': len(self.room_participants[room_id]),
            'annotations': len(self.shared_annotations.get(room_id, [])),
            'active_cursors': len([
                cursor for cursor in self.user_cursors.values()
                if cursor.get('room_id') == room_id
            ])
        }

class CustomDashboardBuilder:
    """Custom dashboard configuration builder"""
    
    def __init__(self):
        self.dashboard_configs: Dict[str, Dict] = {}
        self.widget_templates: Dict[str, Dict] = self._init_widget_templates()
        self.layout_templates: Dict[str, Dict] = self._init_layout_templates()
    
    def _init_widget_templates(self) -> Dict[str, Dict]:
        """Initialize available widget templates"""
        return {
            'network_graph': {
                'type': 'network',
                'title': 'Network Visualization',
                'config': {
                    'layout': 'force',
                    'node_size': 'degree',
                    'edge_width': 'weight',
                    'color_scheme': 'category'
                },
                'size': {'w': 6, 'h': 4}
            },
            'timeline_chart': {
                'type': 'timeline',
                'title': 'Timeline Analysis',
                'config': {
                    'time_range': '30d',
                    'granularity': 'day',
                    'metrics': ['count', 'unique']
                },
                'size': {'w': 6, 'h': 3}
            },
            'geo_map': {
                'type': 'geographic',
                'title': 'Geographic Distribution',
                'config': {
                    'map_type': 'choropleth',
                    'center': 'auto',
                    'zoom': 'auto'
                },
                'size': {'w': 6, 'h': 4}
            },
            'metrics_card': {
                'type': 'metric',
                'title': 'Key Metrics',
                'config': {
                    'metrics': ['total_nodes', 'total_edges', 'avg_degree'],
                    'format': 'number',
                    'show_trend': True
                },
                'size': {'w': 3, 'h': 2}
            },
            'data_table': {
                'type': 'table',
                'title': 'Data Table',
                'config': {
                    'columns': ['id', 'name', 'type', 'created_at'],
                    'sortable': True,
                    'filterable': True,
                    'paginated': True
                },
                'size': {'w': 6, 'h': 4}
            },
            'filter_panel': {
                'type': 'filter',
                'title': 'Advanced Filters',
                'config': {
                    'fields': ['type', 'status', 'date_range'],
                    'operators': ['eq', 'in', 'between'],
                    'save_presets': True
                },
                'size': {'w': 3, 'h': 4}
            }
        }
    
    def _init_layout_templates(self) -> Dict[str, Dict]:
        """Initialize layout templates"""
        return {
            'default': {
                'name': 'Default Layout',
                'description': 'Standard dashboard layout',
                'layout': [
                    {'i': 'metrics', 'x': 0, 'y': 0, 'w': 3, 'h': 2},
                    {'i': 'network', 'x': 3, 'y': 0, 'w': 6, 'h': 4},
                    {'i': 'timeline', 'x': 9, 'y': 0, 'w': 3, 'h': 4},
                    {'i': 'filters', 'x': 0, 'y': 4, 'w': 3, 'h': 4},
                    {'i': 'table', 'x': 3, 'y': 4, 'w': 9, 'h': 4}
                ]
            },
            'analysis_focused': {
                'name': 'Analysis Focused',
                'description': 'Large visualization area with compact controls',
                'layout': [
                    {'i': 'filters', 'x': 0, 'y': 0, 'w': 2, 'h': 6},
                    {'i': 'network', 'x': 2, 'y': 0, 'w': 8, 'h': 6},
                    {'i': 'timeline', 'x': 10, 'y': 0, 'w': 2, 'h': 3},
                    {'i': 'metrics', 'x': 10, 'y': 3, 'w': 2, 'h': 3}
                ]
            },
            'monitoring': {
                'name': 'Monitoring Dashboard',
                'description': 'Real-time monitoring layout',
                'layout': [
                    {'i': 'metrics_1', 'x': 0, 'y': 0, 'w': 3, 'h': 2},
                    {'i': 'metrics_2', 'x': 3, 'y': 0, 'w': 3, 'h': 2},
                    {'i': 'metrics_3', 'x': 6, 'y': 0, 'w': 3, 'h': 2},
                    {'i': 'metrics_4', 'x': 9, 'y': 0, 'w': 3, 'h': 2},
                    {'i': 'timeline', 'x': 0, 'y': 2, 'w': 12, 'h': 3},
                    {'i': 'geo_map', 'x': 0, 'y': 5, 'w': 6, 'h': 3},
                    {'i': 'network', 'x': 6, 'y': 5, 'w': 6, 'h': 3}
                ]
            }
        }
    
    def create_dashboard(self, user_id: str, name: str, template: str = 'default') -> str:
        """Create new dashboard configuration"""
        dashboard_id = str(uuid.uuid4())
        
        layout_template = self.layout_templates.get(template, self.layout_templates['default'])
        
        config = {
            'id': dashboard_id,
            'name': name,
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'template': template,
            'layout': layout_template['layout'].copy(),
            'widgets': {},
            'global_filters': [],
            'theme': 'default',
            'auto_refresh': False,
            'refresh_interval': 300  # 5 minutes
        }
        
        # Add default widgets based on layout
        for item in config['layout']:
            widget_id = item['i']
            if widget_id in self.widget_templates:
                config['widgets'][widget_id] = self.widget_templates[widget_id].copy()
            else:
                # Create a placeholder widget
                config['widgets'][widget_id] = {
                    'type': 'placeholder',
                    'title': f'Widget {widget_id}',
                    'config': {},
                    'size': {'w': item['w'], 'h': item['h']}
                }
        
        self.dashboard_configs[dashboard_id] = config
        
        logger.info(f"Created dashboard {dashboard_id} for user {user_id}")
        return dashboard_id
    
    def update_dashboard(self, dashboard_id: str, updates: Dict[str, Any]) -> bool:
        """Update dashboard configuration"""
        if dashboard_id not in self.dashboard_configs:
            return False
        
        config = self.dashboard_configs[dashboard_id]
        
        # Update allowed fields
        allowed_updates = ['name', 'layout', 'widgets', 'global_filters', 'theme', 'auto_refresh', 'refresh_interval']
        
        for field, value in updates.items():
            if field in allowed_updates:
                config[field] = value
        
        config['updated_at'] = datetime.utcnow().isoformat()
        
        logger.info(f"Updated dashboard {dashboard_id}")
        return True
    
    def add_widget(self, dashboard_id: str, widget_type: str, position: Dict[str, int] = None) -> Optional[str]:
        """Add widget to dashboard"""
        if dashboard_id not in self.dashboard_configs:
            return None
        
        if widget_type not in self.widget_templates:
            return None
        
        widget_id = str(uuid.uuid4())[:8]  # Short ID for widgets
        config = self.dashboard_configs[dashboard_id]
        
        # Add widget configuration
        config['widgets'][widget_id] = self.widget_templates[widget_type].copy()
        
        # Add to layout
        widget_layout = {
            'i': widget_id,
            'x': position.get('x', 0) if position else 0,
            'y': position.get('y', 0) if position else 0,
            'w': position.get('w') if position else config['widgets'][widget_id]['size']['w'],
            'h': position.get('h') if position else config['widgets'][widget_id]['size']['h']
        }
        
        config['layout'].append(widget_layout)
        config['updated_at'] = datetime.utcnow().isoformat()
        
        logger.info(f"Added widget {widget_id} to dashboard {dashboard_id}")
        return widget_id
    
    def remove_widget(self, dashboard_id: str, widget_id: str) -> bool:
        """Remove widget from dashboard"""
        if dashboard_id not in self.dashboard_configs:
            return False
        
        config = self.dashboard_configs[dashboard_id]
        
        # Remove from widgets
        if widget_id in config['widgets']:
            del config['widgets'][widget_id]
        
        # Remove from layout
        config['layout'] = [
            item for item in config['layout']
            if item['i'] != widget_id
        ]
        
        config['updated_at'] = datetime.utcnow().isoformat()
        
        logger.info(f"Removed widget {widget_id} from dashboard {dashboard_id}")
        return True
    
    def get_dashboard(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """Get dashboard configuration"""
        return self.dashboard_configs.get(dashboard_id)
    
    def list_dashboards(self, user_id: str = None) -> List[Dict[str, Any]]:
        """List dashboards (optionally filtered by user)"""
        dashboards = list(self.dashboard_configs.values())
        
        if user_id:
            dashboards = [d for d in dashboards if d['user_id'] == user_id]
        
        # Return summary info
        return [
            {
                'id': d['id'],
                'name': d['name'],
                'user_id': d['user_id'],
                'created_at': d['created_at'],
                'updated_at': d['updated_at'],
                'template': d['template'],
                'widget_count': len(d['widgets'])
            }
            for d in dashboards
        ]
    
    def duplicate_dashboard(self, dashboard_id: str, user_id: str, new_name: str = None) -> Optional[str]:
        """Duplicate existing dashboard"""
        if dashboard_id not in self.dashboard_configs:
            return None
        
        original = self.dashboard_configs[dashboard_id]
        new_dashboard_id = str(uuid.uuid4())
        
        # Create copy
        new_config = original.copy()
        new_config.update({
            'id': new_dashboard_id,
            'name': new_name or f"Copy of {original['name']}",
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        })
        
        # Deep copy widgets and layout
        new_config['widgets'] = json.loads(json.dumps(original['widgets']))
        new_config['layout'] = json.loads(json.dumps(original['layout']))
        
        self.dashboard_configs[new_dashboard_id] = new_config
        
        logger.info(f"Duplicated dashboard {dashboard_id} as {new_dashboard_id}")
        return new_dashboard_id

# Global instances
advanced_filters = AdvancedFilters()
collaboration_manager = CollaborationManager()
dashboard_builder = CustomDashboardBuilder()

# Export for easy import
__all__ = [
    'AdvancedFilters', 'CollaborationManager', 'CustomDashboardBuilder',
    'FilterCriteria', 'CollaborationEvent', 'EventType',
    'advanced_filters', 'collaboration_manager', 'dashboard_builder'
]
