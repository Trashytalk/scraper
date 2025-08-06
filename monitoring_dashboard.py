#!/usr/bin/env python3
"""
Monitoring Dashboard Web Interface
Business Intelligence Scraper Platform v2.0.0
"""

import os
import sys
import json
import sqlite3
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

import psutil
import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

class MonitoringDashboard:
    """Web dashboard for monitoring system"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(PROJECT_ROOT, "monitoring", "config.json")
        self.config = self._load_config()
        self.app = FastAPI(title="Monitoring Dashboard", version="1.0.0")
        self.websocket_connections: List[WebSocket] = []
        
        # Database path
        self.metrics_db_path = os.path.join(PROJECT_ROOT, "monitoring", "metrics.db")
        
        # Initialize FastAPI app
        self._setup_routes()
        self._setup_templates()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load monitoring configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "dashboard": {
                "enabled": True,
                "port": 8888,
                "refresh_interval": 5
            },
            "services": {
                "api_base_url": "http://localhost:8000"
            }
        }
    
    def _setup_templates(self):
        """Setup Jinja2 templates"""
        template_dir = os.path.join(PROJECT_ROOT, "monitoring", "templates")
        os.makedirs(template_dir, exist_ok=True)
        
        # Create dashboard template if it doesn't exist
        dashboard_template = os.path.join(template_dir, "dashboard.html")
        if not os.path.exists(dashboard_template):
            self._create_dashboard_template(dashboard_template)
        
        self.templates = Jinja2Templates(directory=template_dir)
    
    def _create_dashboard_template(self, template_path: str):
        """Create the dashboard HTML template"""
        template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Business Intelligence Scraper - Monitoring Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
        }
        
        .header h1 {
            font-size: 1.8rem;
            font-weight: 300;
        }
        
        .header .subtitle {
            opacity: 0.8;
            font-size: 0.9rem;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .card h2 {
            color: #4a5568;
            margin-bottom: 1rem;
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 0;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            color: #718096;
            font-weight: 500;
        }
        
        .metric-value {
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .status {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .status.healthy {
            background: #c6f6d5;
            color: #22543d;
        }
        
        .status.warning {
            background: #fef5e7;
            color: #c05621;
        }
        
        .status.critical {
            background: #fed7d7;
            color: #c53030;
        }
        
        .chart-container {
            height: 300px;
            margin-top: 1rem;
        }
        
        .service-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1rem;
        }
        
        .service-item {
            padding: 1rem;
            border-radius: 8px;
            background: #f7fafc;
            border-left: 4px solid #4299e1;
        }
        
        .service-name {
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .service-status {
            font-size: 0.9rem;
        }
        
        .loading {
            text-align: center;
            padding: 2rem;
            color: #718096;
        }
        
        .refresh-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.9);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Business Intelligence Scraper</h1>
        <div class="subtitle">Production Monitoring Dashboard v1.0.0</div>
    </div>
    
    <div class="refresh-indicator" id="refreshIndicator">
        <span id="refreshStatus">Connecting...</span>
    </div>
    
    <div class="container">
        <div class="grid">
            <!-- System Overview -->
            <div class="card">
                <h2>System Overview</h2>
                <div id="systemOverview" class="loading">Loading...</div>
            </div>
            
            <!-- Service Status -->
            <div class="card">
                <h2>Service Status</h2>
                <div id="serviceStatus" class="loading">Loading...</div>
            </div>
            
            <!-- Performance Metrics -->
            <div class="card">
                <h2>Performance</h2>
                <div id="performanceMetrics" class="loading">Loading...</div>
            </div>
            
            <!-- Alert Summary -->
            <div class="card">
                <h2>Recent Alerts</h2>
                <div id="alertSummary" class="loading">Loading...</div>
            </div>
        </div>
        
        <!-- Charts Row -->
        <div class="grid">
            <!-- CPU Usage Chart -->
            <div class="card">
                <h2>CPU Usage</h2>
                <div class="chart-container">
                    <canvas id="cpuChart"></canvas>
                </div>
            </div>
            
            <!-- Memory Usage Chart -->
            <div class="card">
                <h2>Memory Usage</h2>
                <div class="chart-container">
                    <canvas id="memoryChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- API Response Times -->
        <div class="card">
            <h2>API Response Times</h2>
            <div class="chart-container">
                <canvas id="responseTimeChart"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        class MonitoringDashboard {
            constructor() {
                this.socket = null;
                this.charts = {};
                this.data = {
                    cpu: [],
                    memory: [],
                    responseTimes: []
                };
                this.refreshInterval = 5000;
                this.init();
            }
            
            init() {
                this.setupWebSocket();
                this.setupCharts();
                this.startPeriodicRefresh();
            }
            
            setupWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws`;
                
                this.socket = new WebSocket(wsUrl);
                
                this.socket.onopen = () => {
                    console.log('WebSocket connected');
                    this.updateRefreshStatus('Connected', false);
                };
                
                this.socket.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    this.handleRealtimeData(data);
                };
                
                this.socket.onclose = () => {
                    console.log('WebSocket disconnected');
                    this.updateRefreshStatus('Disconnected', true);
                    setTimeout(() => this.setupWebSocket(), 5000);
                };
                
                this.socket.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.updateRefreshStatus('Error', true);
                };
            }
            
            updateRefreshStatus(status, isError = false) {
                const indicator = document.getElementById('refreshStatus');
                indicator.textContent = status;
                indicator.className = isError ? 'pulse' : '';
            }
            
            setupCharts() {
                // CPU Chart
                const cpuCtx = document.getElementById('cpuChart').getContext('2d');
                this.charts.cpu = new Chart(cpuCtx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'CPU Usage (%)',
                            data: [],
                            borderColor: '#4299e1',
                            backgroundColor: 'rgba(66, 153, 225, 0.1)',
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        }
                    }
                });
                
                // Memory Chart
                const memoryCtx = document.getElementById('memoryChart').getContext('2d');
                this.charts.memory = new Chart(memoryCtx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Memory Usage (%)',
                            data: [],
                            borderColor: '#48bb78',
                            backgroundColor: 'rgba(72, 187, 120, 0.1)',
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        }
                    }
                });
                
                // Response Time Chart
                const responseCtx = document.getElementById('responseTimeChart').getContext('2d');
                this.charts.responseTime = new Chart(responseCtx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Response Time (ms)',
                            data: [],
                            borderColor: '#ed8936',
                            backgroundColor: 'rgba(237, 137, 54, 0.1)',
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            }
            
            handleRealtimeData(data) {
                if (data.type === 'metrics') {
                    this.updateCharts(data.payload);
                } else if (data.type === 'status') {
                    this.updateStatus(data.payload);
                }
            }
            
            updateCharts(metrics) {
                const now = new Date().toLocaleTimeString();
                const maxPoints = 20;
                
                // Update CPU chart
                if (metrics.cpu !== undefined) {
                    this.charts.cpu.data.labels.push(now);
                    this.charts.cpu.data.datasets[0].data.push(metrics.cpu);
                    
                    if (this.charts.cpu.data.labels.length > maxPoints) {
                        this.charts.cpu.data.labels.shift();
                        this.charts.cpu.data.datasets[0].data.shift();
                    }
                    this.charts.cpu.update('none');
                }
                
                // Update Memory chart
                if (metrics.memory !== undefined) {
                    this.charts.memory.data.labels.push(now);
                    this.charts.memory.data.datasets[0].data.push(metrics.memory);
                    
                    if (this.charts.memory.data.labels.length > maxPoints) {
                        this.charts.memory.data.labels.shift();
                        this.charts.memory.data.datasets[0].data.shift();
                    }
                    this.charts.memory.update('none');
                }
                
                // Update Response Time chart
                if (metrics.response_time !== undefined) {
                    this.charts.responseTime.data.labels.push(now);
                    this.charts.responseTime.data.datasets[0].data.push(metrics.response_time);
                    
                    if (this.charts.responseTime.data.labels.length > maxPoints) {
                        this.charts.responseTime.data.labels.shift();
                        this.charts.responseTime.data.datasets[0].data.shift();
                    }
                    this.charts.responseTime.update('none');
                }
            }
            
            updateStatus(status) {
                // Update system overview
                const systemOverview = document.getElementById('systemOverview');
                systemOverview.innerHTML = this.renderSystemOverview(status.system || {});
                
                // Update service status
                const serviceStatus = document.getElementById('serviceStatus');
                serviceStatus.innerHTML = this.renderServiceStatus(status.services || {});
                
                // Update performance metrics
                const performanceMetrics = document.getElementById('performanceMetrics');
                performanceMetrics.innerHTML = this.renderPerformanceMetrics(status.performance || {});
                
                // Update alerts
                const alertSummary = document.getElementById('alertSummary');
                alertSummary.innerHTML = this.renderAlertSummary(status.alerts || []);
            }
            
            renderSystemOverview(system) {
                return `
                    <div class="metric">
                        <span class="metric-label">Uptime</span>
                        <span class="metric-value">${system.uptime || 'N/A'}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">CPU Usage</span>
                        <span class="metric-value">${system.cpu_percent || 0}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Memory Usage</span>
                        <span class="metric-value">${system.memory_percent || 0}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Disk Usage</span>
                        <span class="metric-value">${system.disk_percent || 0}%</span>
                    </div>
                `;
            }
            
            renderServiceStatus(services) {
                const serviceHtml = Object.entries(services).map(([name, status]) => `
                    <div class="service-item">
                        <div class="service-name">${name}</div>
                        <div class="service-status">
                            <span class="status ${status.toLowerCase()}">${status}</span>
                        </div>
                    </div>
                `).join('');
                
                return `<div class="service-grid">${serviceHtml}</div>`;
            }
            
            renderPerformanceMetrics(performance) {
                return `
                    <div class="metric">
                        <span class="metric-label">Avg Response Time</span>
                        <span class="metric-value">${performance.avg_response_time || 0}ms</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Requests/min</span>
                        <span class="metric-value">${performance.requests_per_minute || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Error Rate</span>
                        <span class="metric-value">${performance.error_rate || 0}%</span>
                    </div>
                `;
            }
            
            renderAlertSummary(alerts) {
                if (!alerts.length) {
                    return '<div style="text-align: center; color: #68d391;">No recent alerts</div>';
                }
                
                return alerts.slice(0, 5).map(alert => `
                    <div class="metric">
                        <span class="metric-label">${alert.message}</span>
                        <span class="status ${alert.severity}">${alert.severity}</span>
                    </div>
                `).join('');
            }
            
            async startPeriodicRefresh() {
                while (true) {
                    try {
                        const response = await fetch('/api/status');
                        const data = await response.json();
                        this.updateStatus(data);
                        this.updateRefreshStatus('Connected', false);
                    } catch (error) {
                        console.error('Failed to fetch status:', error);
                        this.updateRefreshStatus('Error', true);
                    }
                    
                    await new Promise(resolve => setTimeout(resolve, this.refreshInterval));
                }
            }
        }
        
        // Initialize dashboard when page loads
        document.addEventListener('DOMContentLoaded', () => {
            new MonitoringDashboard();
        });
    </script>
</body>
</html>'''
        
        with open(template_path, 'w') as f:
            f.write(template_content)
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            return self.templates.TemplateResponse("dashboard.html", {"request": request})
        
        @self.app.get("/api/status")
        async def get_status():
            return await self._get_current_status()
        
        @self.app.get("/api/metrics")
        async def get_metrics():
            return await self._get_metrics_history()
        
        @self.app.get("/api/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.websocket_connections.append(websocket)
            try:
                while True:
                    # Send periodic updates
                    status = await self._get_current_status()
                    await websocket.send_json({
                        "type": "status",
                        "payload": status
                    })
                    await asyncio.sleep(self.config.get("dashboard", {}).get("refresh_interval", 5))
            except WebSocketDisconnect:
                self.websocket_connections.remove(websocket)
    
    async def _get_current_status(self) -> Dict[str, Any]:
        """Get current system status"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            uptime_str = f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m"
            
            # Check services
            services = await self._check_services()
            
            # Get recent alerts
            alerts = await self._get_recent_alerts()
            
            # Performance metrics
            performance = await self._get_performance_metrics()
            
            return {
                "system": {
                    "uptime": uptime_str,
                    "cpu_percent": round(cpu_percent, 1),
                    "memory_percent": round(memory.percent, 1),
                    "disk_percent": round((disk.used / disk.total) * 100, 1),
                    "load_average": list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else [0, 0, 0]
                },
                "services": services,
                "alerts": alerts,
                "performance": performance,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_services(self) -> Dict[str, str]:
        """Check status of services"""
        services = {}
        
        # Check if main backend is running
        try:
            import requests
            api_url = self.config.get("services", {}).get("api_base_url", "http://localhost:8000")
            response = requests.get(f"{api_url}/health", timeout=5)
            services["Backend API"] = "Healthy" if response.status_code == 200 else "Warning"
        except:
            services["Backend API"] = "Critical"
        
        # Check database connection
        try:
            # This would need to be implemented based on your database setup
            services["Database"] = "Healthy"  # Placeholder
        except:
            services["Database"] = "Critical"
        
        # Check Redis
        try:
            # This would need to be implemented based on your Redis setup
            services["Redis Cache"] = "Healthy"  # Placeholder
        except:
            services["Redis Cache"] = "Warning"
        
        return services
    
    async def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent alerts from database"""
        try:
            if os.path.exists(self.metrics_db_path):
                conn = sqlite3.connect(self.metrics_db_path)
                cursor = conn.cursor()
                
                # Get recent alerts (last 24 hours)
                yesterday = datetime.now() - timedelta(days=1)
                cursor.execute("""
                    SELECT timestamp, severity, component, message 
                    FROM alerts 
                    WHERE timestamp > ? 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                """, (yesterday.isoformat(),))
                
                alerts = []
                for row in cursor.fetchall():
                    alerts.append({
                        "timestamp": row[0],
                        "severity": row[1],
                        "component": row[2],
                        "message": row[3]
                    })
                
                conn.close()
                return alerts
        except:
            pass
        
        return []
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            if os.path.exists(self.metrics_db_path):
                conn = sqlite3.connect(self.metrics_db_path)
                cursor = conn.cursor()
                
                # Get average response time from last hour
                one_hour_ago = datetime.now() - timedelta(hours=1)
                cursor.execute("""
                    SELECT AVG(response_time) 
                    FROM api_metrics 
                    WHERE timestamp > ?
                """, (one_hour_ago.isoformat(),))
                
                result = cursor.fetchone()
                avg_response_time = round(result[0], 1) if result[0] else 0
                
                # Get request count from last minute
                one_minute_ago = datetime.now() - timedelta(minutes=1)
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM api_metrics 
                    WHERE timestamp > ?
                """, (one_minute_ago.isoformat(),))
                
                result = cursor.fetchone()
                requests_per_minute = result[0] if result else 0
                
                conn.close()
                
                return {
                    "avg_response_time": avg_response_time,
                    "requests_per_minute": requests_per_minute,
                    "error_rate": 0  # Placeholder
                }
        except:
            pass
        
        return {
            "avg_response_time": 0,
            "requests_per_minute": 0,
            "error_rate": 0
        }
    
    async def _get_metrics_history(self) -> Dict[str, List[Any]]:
        """Get historical metrics data"""
        try:
            if os.path.exists(self.metrics_db_path):
                conn = sqlite3.connect(self.metrics_db_path)
                cursor = conn.cursor()
                
                # Get system metrics from last hour
                one_hour_ago = datetime.now() - timedelta(hours=1)
                cursor.execute("""
                    SELECT timestamp, cpu_percent, memory_percent, disk_percent
                    FROM system_metrics 
                    WHERE timestamp > ? 
                    ORDER BY timestamp
                """, (one_hour_ago.isoformat(),))
                
                metrics = {
                    "timestamps": [],
                    "cpu": [],
                    "memory": [],
                    "disk": []
                }
                
                for row in cursor.fetchall():
                    metrics["timestamps"].append(row[0])
                    metrics["cpu"].append(row[1])
                    metrics["memory"].append(row[2])
                    metrics["disk"].append(row[3])
                
                conn.close()
                return metrics
        except:
            pass
        
        return {
            "timestamps": [],
            "cpu": [],
            "memory": [],
            "disk": []
        }
    
    def run(self, host: str = "0.0.0.0", port: int = None):
        """Run the dashboard server"""
        port = port or self.config.get("dashboard", {}).get("port", 8888)
        
        print(f"Starting Monitoring Dashboard on http://{host}:{port}")
        print(f"Dashboard URL: http://localhost:{port}")
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitoring Dashboard")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, help="Port to bind to")
    
    args = parser.parse_args()
    
    dashboard = MonitoringDashboard(config_path=args.config)
    dashboard.run(host=args.host, port=args.port)

if __name__ == "__main__":
    main()
