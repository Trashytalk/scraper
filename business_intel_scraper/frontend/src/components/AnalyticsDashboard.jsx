import React, { useState, useEffect, useRef } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { analyticsService } from '../services/api';
import { useAuth } from './AuthSystem';
import { 
  Alert, 
  CircularProgress, 
  Box, 
  Typography,
  Card,
  CardContent,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';

// Analytics Dashboard Component
const AnalyticsDashboard = () => {
  const { isAuthenticated } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [performanceCharts, setPerformanceCharts] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState(6); // hours

  const wsRef = useRef(null);

  // Fetch dashboard data
  const fetchDashboardData = async () => {
    try {
      if (isAuthenticated) {
        const data = await analyticsService.getDashboardAnalytics();
        setDashboardData(data);
        setAlerts(data.alerts?.recent_alerts || []);
      } else {
        // Show demo data for non-authenticated users
        setDashboardData({
          jobs: { total: 0, running: 0, completed: 0, failed: 0, pending: 0 },
          results: { total: 0, today: 0, this_week: 0 },
          performance: { avg_processing_time: "0s", success_rate: "0%", data_quality_score: "0%" }
        });
      }
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError('Failed to fetch dashboard data');
    }
  };

  const fetchPerformanceCharts = async (hours = 6) => {
    try {
      if (isAuthenticated) {
        const data = await analyticsService.getMetrics();
        setPerformanceCharts(data);
      } else {
        // Use mock data for demo
        const mockCharts = {
          job_completion_rate: [
            { timestamp: "09:00", value: 85, label: "09:00" },
            { timestamp: "10:00", value: 92, label: "10:00" },
            { timestamp: "11:00", value: 88, label: "11:00" },
            { timestamp: "12:00", value: 95, label: "12:00" }
          ],
          data_processing: [
            { timestamp: "09:00", value: 156, label: "09:00" },
            { timestamp: "10:00", value: 189, label: "10:00" },
            { timestamp: "11:00", value: 203, label: "11:00" },
            { timestamp: "12:00", value: 221, label: "12:00" }
          ]
        };
        setPerformanceCharts(mockCharts);
      }
    } catch (err) {
      console.error('Failed to fetch performance charts:', err);
    }
  };  const fetchInsights = async () => {
    try {
      const response = await fetch('/analytics/insights');
      if (response.ok) {
        const insightsData = await response.json();
        setInsights(insightsData);
      }
    } catch (err) {
      console.error('Failed to fetch insights:', err);
    }
  };

  // Initialize dashboard
  useEffect(() => {
    const initDashboard = async () => {
      setLoading(true);
      try {
        await Promise.all([
          fetchDashboardData(),
          fetchPerformanceCharts(timeRange),
          fetchInsights()
        ]);
      } finally {
        setLoading(false);
      }
    };

    initDashboard();

    // Set up periodic refresh
    const interval = setInterval(() => {
      fetchDashboardData();
      fetchPerformanceCharts(timeRange);
    }, 30000); // Refresh every 30 seconds

    // Set up WebSocket for real-time updates
    const setupWebSocket = () => {
      try {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        wsRef.current = new WebSocket(`${wsProtocol}//${window.location.host}/analytics/ws`);
        
        wsRef.current.onmessage = (event) => {
          const message = JSON.parse(event.data);
          if (message.type === 'metrics_update') {
            // Update real-time metrics
            setDashboardData(prev => prev ? {
              ...prev,
              overview: {
                ...prev.overview,
                key_metrics: {
                  ...prev.overview.key_metrics,
                  ...message.data
                }
              }
            } : null);
          }
        };

        wsRef.current.onerror = (error) => {
          console.warn('WebSocket error:', error);
        };

      } catch (err) {
        console.warn('WebSocket not available:', err);
      }
    };

    setupWebSocket();

    return () => {
      clearInterval(interval);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [timeRange]);

  const handleTimeRangeChange = (hours) => {
    setTimeRange(hours);
    fetchPerformanceCharts(hours);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          Error: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
          <p className="text-gray-600">Monitor system performance, data quality, and insights</p>
        </div>

        {/* System Status Overview */}
        <SystemStatusOverview data={dashboardData?.overview} />

        {/* Key Metrics Cards */}
        <MetricsCards data={dashboardData?.overview?.key_metrics} />

        {/* Time Range Selector */}
        <TimeRangeSelector timeRange={timeRange} onChange={handleTimeRangeChange} />

        {/* Performance Charts */}
        <PerformanceCharts charts={performanceCharts} />

        {/* Alerts and Insights */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <AlertsPanel alerts={alerts} />
          <InsightsPanel insights={insights} />
        </div>

        {/* Job Analytics and Data Quality */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <JobAnalytics data={dashboardData?.jobs} />
          <DataQualityPanel data={dashboardData?.data_quality} />
        </div>
      </div>
    </div>
  );
};

// System Status Overview Component
const SystemStatusOverview = ({ data }) => {
  if (!data) return null;

  const getStatusColor = (status) => {
    const colors = {
      healthy: 'bg-green-100 text-green-800',
      warning: 'bg-yellow-100 text-yellow-800',
      degraded: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900">System Status</h2>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(data.status)}`}>
          {data.status?.charAt(0).toUpperCase() + data.status?.slice(1)}
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">
            {data.system_health?.cpu_percent?.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600">CPU Usage</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">
            {data.system_health?.memory_percent?.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600">Memory Usage</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600">
            {data.alerts_count || 0}
          </div>
          <div className="text-sm text-gray-600">Active Alerts</div>
        </div>
      </div>
    </div>
  );
};

// Metrics Cards Component
const MetricsCards = ({ data }) => {
  if (!data) return null;

  const metrics = [
    {
      title: 'Requests/Min',
      value: data.requests_per_minute?.toFixed(1) || '0',
      change: '+5.2%',
      changeType: 'positive',
      icon: '📊'
    },
    {
      title: 'Avg Response Time',
      value: `${data.avg_response_time?.toFixed(2) || '0'}s`,
      change: '-2.1%',
      changeType: 'positive',
      icon: '⏱️'
    },
    {
      title: 'Success Rate',
      value: `${(data.success_rate * 100)?.toFixed(1) || '0'}%`,
      change: '+0.5%',
      changeType: 'positive',
      icon: '✅'
    },
    {
      title: 'Active Jobs',
      value: data.active_jobs || '0',
      change: '+3',
      changeType: 'neutral',
      icon: '🔧'
    },
    {
      title: 'Data Quality',
      value: `${(data.data_quality_score * 100)?.toFixed(1) || '0'}%`,
      change: '+1.2%',
      changeType: 'positive',
      icon: '🎯'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
      {metrics.map((metric, index) => (
        <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <div className="text-2xl">{metric.icon}</div>
            <div className={`text-sm font-medium ${
              metric.changeType === 'positive' ? 'text-green-600' : 
              metric.changeType === 'negative' ? 'text-red-600' : 
              'text-gray-600'
            }`}>
              {metric.change}
            </div>
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-1">{metric.value}</div>
          <div className="text-sm text-gray-600">{metric.title}</div>
        </div>
      ))}
    </div>
  );
};

// Time Range Selector Component
const TimeRangeSelector = ({ timeRange, onChange }) => {
  const ranges = [
    { label: '6 Hours', value: 6 },
    { label: '24 Hours', value: 24 },
    { label: '7 Days', value: 168 },
  ];

  return (
    <div className="mb-6">
      <div className="flex space-x-2">
        {ranges.map((range) => (
          <button
            key={range.value}
            onClick={() => onChange(range.value)}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              timeRange === range.value
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            {range.label}
          </button>
        ))}
      </div>
    </div>
  );
};

// Performance Charts Component
const PerformanceCharts = ({ charts }) => {
  if (!charts || Object.keys(charts).length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Performance Metrics</h2>
        <div className="text-center text-gray-500 py-8">
          No performance data available
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      {/* Response Time Chart */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Response Time</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={charts.response_times || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="timestamp" 
              tickFormatter={(value) => new Date(value).toLocaleTimeString()}
            />
            <YAxis />
            <Tooltip 
              labelFormatter={(value) => new Date(value).toLocaleString()}
              formatter={(value) => [`${value}s`, 'Response Time']}
            />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="#3B82F6" 
              strokeWidth={2}
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* System CPU Chart */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">CPU Usage</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={charts.system_cpu || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="timestamp" 
              tickFormatter={(value) => new Date(value).toLocaleTimeString()}
            />
            <YAxis />
            <Tooltip 
              labelFormatter={(value) => new Date(value).toLocaleString()}
              formatter={(value) => [`${value}%`, 'CPU Usage']}
            />
            <Area 
              type="monotone" 
              dataKey="value" 
              stroke="#10B981" 
              fill="#10B981" 
              fillOpacity={0.3}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Memory Usage Chart */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Memory Usage</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={charts.system_memory || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="timestamp" 
              tickFormatter={(value) => new Date(value).toLocaleTimeString()}
            />
            <YAxis />
            <Tooltip 
              labelFormatter={(value) => new Date(value).toLocaleString()}
              formatter={(value) => [`${value}%`, 'Memory Usage']}
            />
            <Area 
              type="monotone" 
              dataKey="value" 
              stroke="#F59E0B" 
              fill="#F59E0B" 
              fillOpacity={0.3}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Data Quality Chart */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Quality Score</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={charts.data_quality || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="timestamp" 
              tickFormatter={(value) => new Date(value).toLocaleTimeString()}
            />
            <YAxis domain={[0, 1]} />
            <Tooltip 
              labelFormatter={(value) => new Date(value).toLocaleString()}
              formatter={(value) => [`${(value * 100).toFixed(1)}%`, 'Quality Score']}
            />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="#8B5CF6" 
              strokeWidth={2}
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

// Alerts Panel Component
const AlertsPanel = ({ alerts }) => {
  const getSeverityColor = (severity) => {
    const colors = {
      high: 'bg-red-100 text-red-800 border-red-200',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      low: 'bg-blue-100 text-blue-800 border-blue-200'
    };
    return colors[severity] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getSeverityIcon = (severity) => {
    const icons = {
      high: '🚨',
      medium: '⚠️',
      low: 'ℹ️'
    };
    return icons[severity] || '📌';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Alerts</h3>
      
      {(!alerts || alerts.length === 0) ? (
        <div className="text-center text-gray-500 py-8">
          <div className="text-4xl mb-2">✅</div>
          <div>No alerts - system running smoothly</div>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {alerts.slice(0, 10).map((alert, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg border ${getSeverityColor(alert.severity)}`}
            >
              <div className="flex items-start space-x-3">
                <div className="text-lg">
                  {getSeverityIcon(alert.severity)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm">
                    {alert.title || alert.message}
                  </div>
                  {alert.description && (
                    <div className="text-xs mt-1 opacity-75">
                      {alert.description}
                    </div>
                  )}
                  <div className="text-xs mt-2 opacity-60">
                    {alert.timestamp ? new Date(alert.timestamp).toLocaleString() : 'Just now'}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Insights Panel Component
const InsightsPanel = ({ insights }) => {
  if (!insights) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Insights</h3>
        <div className="text-center text-gray-500 py-8">
          Loading insights...
        </div>
      </div>
    );
  }

  const allInsights = [
    ...(insights.insights?.performance || []),
    ...(insights.insights?.capacity || []),
    ...(insights.insights?.anomalies || [])
  ].slice(0, 5);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">AI Insights</h3>
        <div className="text-sm text-gray-500">
          Health Score: {insights.health_score?.toFixed(0)}%
        </div>
      </div>

      {allInsights.length === 0 ? (
        <div className="text-center text-gray-500 py-8">
          <div className="text-4xl mb-2">🤖</div>
          <div>No insights available</div>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {allInsights.map((insight, index) => (
            <div key={index} className="p-3 rounded-lg bg-gray-50 border border-gray-200">
              <div className="font-medium text-sm text-gray-900 mb-1">
                {insight.title}
              </div>
              <div className="text-xs text-gray-600 mb-2">
                {insight.description}
              </div>
              {insight.recommendation && (
                <div className="text-xs text-blue-600 bg-blue-50 p-2 rounded">
                  💡 {insight.recommendation}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Job Analytics Component
const JobAnalytics = ({ data }) => {
  if (!data) return null;

  const statusColors = {
    completed: '#10B981',
    failed: '#EF4444',
    running: '#F59E0B',
    pending: '#6B7280'
  };

  const pieData = Object.entries(data.status_distribution || {}).map(([status, count]) => ({
    name: status,
    value: count,
    fill: statusColors[status] || '#6B7280'
  }));

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Analytics</h3>
      
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">
            {data.summary?.total_jobs || 0}
          </div>
          <div className="text-sm text-gray-600">Total Jobs</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">
            {((data.summary?.success_rate || 0) * 100).toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600">Success Rate</div>
        </div>
      </div>

      {pieData.length > 0 && (
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={40}
              outerRadius={80}
              dataKey="value"
              label={({ name, value }) => `${name}: ${value}`}
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};

// Data Quality Panel Component
const DataQualityPanel = ({ data }) => {
  if (!data) return null;

  const qualityMetrics = [
    {
      label: 'Completeness',
      value: ((data.metrics?.completeness_rate || 0) * 100).toFixed(1),
      color: 'text-green-600'
    },
    {
      label: 'Accuracy',
      value: ((data.metrics?.accuracy_rate || 0) * 100).toFixed(1),
      color: 'text-blue-600'
    },
    {
      label: 'Overall Score',
      value: ((data.current_score || 0) * 100).toFixed(1),
      color: 'text-purple-600'
    }
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Quality</h3>
      
      <div className="space-y-4 mb-6">
        {qualityMetrics.map((metric, index) => (
          <div key={index} className="flex justify-between items-center">
            <span className="text-sm text-gray-600">{metric.label}</span>
            <span className={`text-lg font-bold ${metric.color}`}>
              {metric.value}%
            </span>
          </div>
        ))}
      </div>

      {data.issues && data.issues.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-2">Issues:</h4>
          <div className="space-y-1">
            {data.issues.map((issue, index) => (
              <div key={index} className="text-xs text-red-600 bg-red-50 p-2 rounded">
                ⚠️ {issue}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-4 text-xs text-gray-500">
        Trend: {data.trend === 'improving' ? '📈' : data.trend === 'declining' ? '📉' : '➡️'} {data.trend}
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
