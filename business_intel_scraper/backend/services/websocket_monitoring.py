"""
Real-time Monitoring WebSocket Service
Provides live monitoring data updates for dashboards and real-time applications
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Set, List, Optional
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends
from fastapi.websockets import WebSocketState

from ..services.monitoring_service import monitoring_service
from ..dependencies import get_db


logger = logging.getLogger(__name__)

# WebSocket router
ws_router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time monitoring"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {}  # connection_id -> set of subscription types
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket, connection_id: str, client_info: Dict[str, Any] = None):
        """Accept a WebSocket connection"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        self.subscriptions[connection_id] = set()
        self.connection_metadata[connection_id] = client_info or {}
        
        logger.info(f"WebSocket connected: {connection_id}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat(),
            "available_subscriptions": [
                "system_metrics",
                "alerts",
                "health_status", 
                "performance_data",
                "job_status",
                "anomaly_alerts"
            ]
        }, connection_id)
    
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if connection_id in self.subscriptions:
            del self.subscriptions[connection_id]
        if connection_id in self.connection_metadata:
            del self.connection_metadata[connection_id]
            
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], connection_id: str):
        """Send a message to a specific connection"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                # Remove broken connection
                self.disconnect(connection_id)
    
    async def broadcast_to_subscribers(self, message: Dict[str, Any], subscription_type: str):
        """Broadcast a message to all subscribers of a specific type"""
        disconnected_connections = []
        
        for connection_id, subscriptions in self.subscriptions.items():
            if subscription_type in subscriptions:
                try:
                    await self.send_personal_message(message, connection_id)
                except Exception as e:
                    logger.error(f"Error broadcasting to {connection_id}: {e}")
                    disconnected_connections.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected_connections:
            self.disconnect(connection_id)
    
    def subscribe(self, connection_id: str, subscription_type: str):
        """Subscribe a connection to a specific type of updates"""
        if connection_id in self.subscriptions:
            self.subscriptions[connection_id].add(subscription_type)
            logger.info(f"Connection {connection_id} subscribed to {subscription_type}")
    
    def unsubscribe(self, connection_id: str, subscription_type: str):
        """Unsubscribe a connection from a specific type of updates"""
        if connection_id in self.subscriptions:
            self.subscriptions[connection_id].discard(subscription_type)
            logger.info(f"Connection {connection_id} unsubscribed from {subscription_type}")
    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)
    
    def get_subscription_stats(self) -> Dict[str, int]:
        """Get subscription statistics"""
        stats = {}
        for subscriptions in self.subscriptions.values():
            for sub_type in subscriptions:
                stats[sub_type] = stats.get(sub_type, 0) + 1
        return stats


# Global connection manager
connection_manager = ConnectionManager()


class MonitoringWebSocketService:
    """Service for managing real-time monitoring data streams"""
    
    def __init__(self):
        self.is_broadcasting = False
        self.broadcast_interval = 5  # seconds
        self.last_metrics = None
        self.alert_cache = []
        
    async def start_broadcasting(self):
        """Start broadcasting monitoring data to connected clients"""
        if self.is_broadcasting:
            logger.warning("Broadcasting already active")
            return
            
        self.is_broadcasting = True
        logger.info("Starting real-time monitoring broadcasts")
        
        # Start broadcast tasks
        tasks = [
            self._broadcast_system_metrics(),
            self._broadcast_alerts(),
            self._broadcast_health_status(),
            self._broadcast_performance_data(),
            self._broadcast_job_status()
        ]
        
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error in broadcasting service: {e}")
        finally:
            self.is_broadcasting = False
    
    async def stop_broadcasting(self):
        """Stop broadcasting monitoring data"""
        self.is_broadcasting = False
        logger.info("Stopping real-time monitoring broadcasts")
    
    async def _broadcast_system_metrics(self):
        """Broadcast system metrics updates"""
        while self.is_broadcasting:
            try:
                # Get current metrics
                current_metrics = await monitoring_service.collect_system_metrics(
                    source="websocket_broadcast"
                )
                
                # Check if metrics have changed significantly
                if self._has_significant_change(current_metrics):
                    message = {
                        "type": "system_metrics_update",
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": {
                            "cpu_percent": current_metrics.cpu_percent,
                            "memory_percent": current_metrics.memory_percent,
                            "disk_usage_percent": current_metrics.disk_usage_percent,
                            "network_connections": current_metrics.network_connections_count,
                            "active_threads": current_metrics.active_threads,
                            "open_file_descriptors": current_metrics.open_file_descriptors,
                            "health_status": current_metrics.health_status
                        }
                    }
                    
                    await connection_manager.broadcast_to_subscribers(
                        message, "system_metrics"
                    )
                    
                    self.last_metrics = current_metrics
                
                await asyncio.sleep(self.broadcast_interval)
                
            except Exception as e:
                logger.error(f"Error broadcasting system metrics: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def _broadcast_alerts(self):
        """Broadcast new alerts"""
        while self.is_broadcasting:
            try:
                # Check for new alerts
                db = next(get_db())
                try:
                    from ..db.centralized_data import AlertRecord
                    
                    # Get recent alerts (last 5 minutes)
                    recent_cutoff = datetime.utcnow() - timedelta(minutes=5)
                    recent_alerts = db.query(AlertRecord).filter(
                        AlertRecord.triggered_at >= recent_cutoff,
                        AlertRecord.status == "active"
                    ).order_by(AlertRecord.triggered_at.desc()).limit(10).all()
                    
                    # Check for new alerts not in cache
                    new_alerts = []
                    current_alert_ids = {alert.alert_uuid for alert in recent_alerts}
                    cached_alert_ids = {alert["alert_uuid"] for alert in self.alert_cache}
                    
                    for alert in recent_alerts:
                        if alert.alert_uuid not in cached_alert_ids:
                            new_alerts.append({
                                "alert_uuid": alert.alert_uuid,
                                "severity": alert.severity,
                                "category": alert.category,
                                "title": alert.title,
                                "message": alert.message,
                                "source_component": alert.source_component,
                                "triggered_at": alert.triggered_at.isoformat(),
                                "technical_details": alert.technical_details
                            })
                    
                    # Broadcast new alerts
                    if new_alerts:
                        message = {
                            "type": "new_alerts",
                            "timestamp": datetime.utcnow().isoformat(),
                            "data": {
                                "alerts": new_alerts,
                                "count": len(new_alerts)
                            }
                        }
                        
                        await connection_manager.broadcast_to_subscribers(
                            message, "alerts"
                        )
                    
                    # Update cache
                    self.alert_cache = [
                        {
                            "alert_uuid": alert.alert_uuid,
                            "severity": alert.severity,
                            "triggered_at": alert.triggered_at.isoformat()
                        }
                        for alert in recent_alerts
                    ]
                    
                finally:
                    db.close()
                
                await asyncio.sleep(30)  # Check for alerts every 30 seconds
                
            except Exception as e:
                logger.error(f"Error broadcasting alerts: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _broadcast_health_status(self):
        """Broadcast health status updates"""
        last_health_status = None
        
        while self.is_broadcasting:
            try:
                health_summary = await monitoring_service.get_system_health_summary()
                current_status = health_summary.get("overall_status")
                
                # Only broadcast if status changed
                if current_status != last_health_status:
                    message = {
                        "type": "health_status_update",
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": {
                            "overall_status": current_status,
                            "previous_status": last_health_status,
                            "system_resources": health_summary.get("system_resources", {}),
                            "alerts_count": health_summary.get("alerts", {}).get("total_active", 0),
                            "anomaly_score": health_summary.get("anomaly_score", 0)
                        }
                    }
                    
                    await connection_manager.broadcast_to_subscribers(
                        message, "health_status"
                    )
                    
                    last_health_status = current_status
                
                await asyncio.sleep(15)  # Check health every 15 seconds
                
            except Exception as e:
                logger.error(f"Error broadcasting health status: {e}")
                await asyncio.sleep(30)
    
    async def _broadcast_performance_data(self):
        """Broadcast performance metrics updates"""
        while self.is_broadcasting:
            try:
                if not monitoring_service.metrics_buffer:
                    await asyncio.sleep(10)
                    continue
                
                latest_metrics = monitoring_service.metrics_buffer[-1]
                
                message = {
                    "type": "performance_update",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {
                        "requests_per_minute": latest_metrics.requests_per_minute,
                        "avg_response_time_ms": latest_metrics.avg_response_time_ms,
                        "p95_response_time_ms": latest_metrics.p95_response_time_ms,
                        "error_rate_percent": latest_metrics.error_rate_percent,
                        "cache_hit_rate": latest_metrics.cache_hit_rate,
                        "database_connections_active": latest_metrics.database_connections_active
                    }
                }
                
                await connection_manager.broadcast_to_subscribers(
                    message, "performance_data"
                )
                
                await asyncio.sleep(10)  # Update performance data every 10 seconds
                
            except Exception as e:
                logger.error(f"Error broadcasting performance data: {e}")
                await asyncio.sleep(20)
    
    async def _broadcast_job_status(self):
        """Broadcast job status updates"""
        while self.is_broadcasting:
            try:
                if not monitoring_service.metrics_buffer:
                    await asyncio.sleep(15)
                    continue
                
                latest_metrics = monitoring_service.metrics_buffer[-1]
                
                message = {
                    "type": "job_status_update",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {
                        "active_scraping_jobs": latest_metrics.active_scraping_jobs,
                        "completed_jobs_last_hour": latest_metrics.completed_jobs_last_hour,
                        "failed_jobs_last_hour": latest_metrics.failed_jobs_last_hour,
                        "data_processing_rate_per_min": latest_metrics.data_processing_rate_per_min
                    }
                }
                
                await connection_manager.broadcast_to_subscribers(
                    message, "job_status"
                )
                
                await asyncio.sleep(20)  # Update job status every 20 seconds
                
            except Exception as e:
                logger.error(f"Error broadcasting job status: {e}")
                await asyncio.sleep(30)
    
    def _has_significant_change(self, current_metrics) -> bool:
        """Check if metrics have changed significantly since last broadcast"""
        if not self.last_metrics:
            return True
        
        # Define significance thresholds
        thresholds = {
            "cpu_percent": 5.0,      # 5% change
            "memory_percent": 3.0,    # 3% change
            "disk_usage_percent": 1.0, # 1% change
            "network_connections_count": 10,  # 10 connection change
            "health_status": 0  # Any change in health status
        }
        
        for metric, threshold in thresholds.items():
            current_val = getattr(current_metrics, metric, 0)
            last_val = getattr(self.last_metrics, metric, 0)
            
            if metric == "health_status":
                if current_val != last_val:
                    return True
            else:
                if abs(current_val - last_val) >= threshold:
                    return True
        
        return False


# Global WebSocket service
ws_service = MonitoringWebSocketService()


@ws_router.websocket("/ws/monitoring/{connection_id}")
async def websocket_monitoring_endpoint(websocket: WebSocket, connection_id: str):
    """WebSocket endpoint for real-time monitoring data"""
    client_info = {
        "client_host": websocket.client.host if websocket.client else "unknown",
        "connected_at": datetime.utcnow().isoformat(),
        "user_agent": websocket.headers.get("user-agent", "unknown")
    }
    
    await connection_manager.connect(websocket, connection_id, client_info)
    
    # Start broadcasting service if not already running
    if not ws_service.is_broadcasting:
        asyncio.create_task(ws_service.start_broadcasting())
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            await handle_client_message(message, connection_id)
            
    except WebSocketDisconnect:
        connection_manager.disconnect(connection_id)
        logger.info(f"Client {connection_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {e}")
        connection_manager.disconnect(connection_id)


async def handle_client_message(message: Dict[str, Any], connection_id: str):
    """Handle incoming messages from WebSocket clients"""
    try:
        message_type = message.get("type")
        
        if message_type == "subscribe":
            # Subscribe to specific data types
            subscription_types = message.get("subscription_types", [])
            for sub_type in subscription_types:
                connection_manager.subscribe(connection_id, sub_type)
            
            await connection_manager.send_personal_message({
                "type": "subscription_confirmed",
                "subscriptions": subscription_types,
                "timestamp": datetime.utcnow().isoformat()
            }, connection_id)
        
        elif message_type == "unsubscribe":
            # Unsubscribe from specific data types
            subscription_types = message.get("subscription_types", [])
            for sub_type in subscription_types:
                connection_manager.unsubscribe(connection_id, sub_type)
            
            await connection_manager.send_personal_message({
                "type": "unsubscription_confirmed", 
                "unsubscribed": subscription_types,
                "timestamp": datetime.utcnow().isoformat()
            }, connection_id)
        
        elif message_type == "get_current_data":
            # Send current monitoring data
            await send_current_monitoring_data(connection_id)
        
        elif message_type == "ping":
            # Respond to ping with pong
            await connection_manager.send_personal_message({
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            }, connection_id)
        
        elif message_type == "get_connection_stats":
            # Send connection statistics
            stats = {
                "total_connections": connection_manager.get_connection_count(),
                "subscription_stats": connection_manager.get_subscription_stats(),
                "broadcasting_active": ws_service.is_broadcasting
            }
            
            await connection_manager.send_personal_message({
                "type": "connection_stats",
                "data": stats,
                "timestamp": datetime.utcnow().isoformat()
            }, connection_id)
        
        else:
            # Unknown message type
            await connection_manager.send_personal_message({
                "type": "error",
                "message": f"Unknown message type: {message_type}",
                "timestamp": datetime.utcnow().isoformat()
            }, connection_id)
    
    except Exception as e:
        logger.error(f"Error handling client message: {e}")
        await connection_manager.send_personal_message({
            "type": "error",
            "message": f"Error processing message: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)


async def send_current_monitoring_data(connection_id: str):
    """Send current monitoring data to a specific connection"""
    try:
        # Get current system health
        health_summary = await monitoring_service.get_system_health_summary()
        
        # Get recent metrics
        current_metrics = None
        if monitoring_service.metrics_buffer:
            current_metrics = monitoring_service.metrics_buffer[-1]
        
        # Get recent alerts
        db = next(get_db())
        try:
            from ..db.centralized_data import AlertRecord
            from datetime import timedelta
            
            recent_alerts = db.query(AlertRecord).filter(
                AlertRecord.triggered_at >= datetime.utcnow() - timedelta(hours=1),
                AlertRecord.status == "active"
            ).order_by(AlertRecord.triggered_at.desc()).limit(5).all()
            
            alerts_data = [
                {
                    "alert_uuid": alert.alert_uuid,
                    "severity": alert.severity,
                    "title": alert.title,
                    "triggered_at": alert.triggered_at.isoformat()
                }
                for alert in recent_alerts
            ]
            
        finally:
            db.close()
        
        # Compile current data
        current_data = {
            "type": "current_monitoring_data",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "health_summary": health_summary,
                "current_metrics": {
                    "cpu_percent": current_metrics.cpu_percent if current_metrics else 0,
                    "memory_percent": current_metrics.memory_percent if current_metrics else 0,
                    "disk_usage_percent": current_metrics.disk_usage_percent if current_metrics else 0,
                    "requests_per_minute": current_metrics.requests_per_minute if current_metrics else 0,
                    "avg_response_time_ms": current_metrics.avg_response_time_ms if current_metrics else 0,
                    "error_rate_percent": current_metrics.error_rate_percent if current_metrics else 0,
                    "active_scraping_jobs": current_metrics.active_scraping_jobs if current_metrics else 0,
                    "health_status": current_metrics.health_status if current_metrics else "unknown"
                } if current_metrics else {},
                "recent_alerts": alerts_data,
                "connection_stats": {
                    "total_connections": connection_manager.get_connection_count(),
                    "broadcasting_active": ws_service.is_broadcasting
                }
            }
        }
        
        await connection_manager.send_personal_message(current_data, connection_id)
        
    except Exception as e:
        logger.error(f"Error sending current monitoring data: {e}")
        await connection_manager.send_personal_message({
            "type": "error",
            "message": f"Error retrieving current data: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)


# Additional utility functions for external use

async def broadcast_custom_event(event_type: str, data: Dict[str, Any], subscription_type: str = "alerts"):
    """Broadcast a custom event to subscribers"""
    message = {
        "type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data
    }
    
    await connection_manager.broadcast_to_subscribers(message, subscription_type)


def get_active_connections_count() -> int:
    """Get the number of active WebSocket connections"""
    return connection_manager.get_connection_count()


def get_subscription_statistics() -> Dict[str, int]:
    """Get subscription statistics across all connections"""
    return connection_manager.get_subscription_stats()
