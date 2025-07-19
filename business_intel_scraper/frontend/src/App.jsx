import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { 
  Activity, 
  Database, 
  Settings, 
  BarChart3, 
  PlayCircle, 
  PauseCircle,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Clock,
  Package,
  TrendingUp
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import SpiderMarketplace from './components/SpiderMarketplace.jsx';
import AnalyticsDashboard from './components/AnalyticsDashboard.jsx';

// Query client for React Query
const queryClient = new QueryClient();

// API utility functions
const api = {
  async get(endpoint) {
    const response = await fetch(`/api${endpoint}`);
    return response.json();
  },
  
  async post(endpoint, data = {}) {
    const response = await fetch(`/api${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  }
};

// WebSocket hook for real-time updates
function useWebSocket(url) {
  const [socket, setSocket] = useState(null);
  const [lastMessage, setLastMessage] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('Connecting');

  useEffect(() => {
    const ws = new WebSocket(url);
    
    ws.onopen = () => {
      setConnectionStatus('Connected');
      setSocket(ws);
    };
    
    ws.onmessage = (event) => {
      setLastMessage(JSON.parse(event.data));
    };
    
    ws.onclose = () => {
      setConnectionStatus('Disconnected');
    };
    
    ws.onerror = () => {
      setConnectionStatus('Error');
    };

    return () => ws.close();
  }, [url]);

  return { socket, lastMessage, connectionStatus };
}

// Dashboard component
function Dashboard() {
  const [jobs, setJobs] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  
  const { lastMessage, connectionStatus } = useWebSocket('ws://localhost:8000/ws/notifications');

  useEffect(() => {
    loadDashboardData();
  }, []);

  useEffect(() => {
    if (lastMessage) {
      console.log('Received real-time update:', lastMessage);
      loadDashboardData(); // Refresh data on updates
    }
  }, [lastMessage]);

  const loadDashboardData = async () => {
    try {
      const [jobsData, healthData] = await Promise.all([
        api.get('/jobs'),
        api.get('/')
      ]);
      
      setJobs(Object.entries(jobsData || {}).map(([id, job]) => ({ id, ...job })));
      
      // Generate mock metrics for demo
      const now = Date.now();
      setMetrics([
        { time: now - 300000, jobs: 5, success: 4 },
        { time: now - 240000, jobs: 8, success: 7 },
        { time: now - 180000, jobs: 12, success: 11 },
        { time: now - 120000, jobs: 15, success: 13 },
        { time: now - 60000, jobs: 20, success: 18 },
        { time: now, jobs: 25, success: 22 }
      ]);
      
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      setIsLoading(false);
    }
  };

  const startNewJob = async () => {
    try {
      const result = await api.post('/scrape');
      console.log('Started new job:', result);
      loadDashboardData();
    } catch (error) {
      console.error('Failed to start job:', error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'running': return <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'failed': return <AlertCircle className="w-4 h-4 text-red-500" />;
      default: return <Clock className="w-4 h-4 text-yellow-500" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-2 text-lg">Loading dashboard...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Business Intelligence Dashboard</h1>
        <div className="flex items-center space-x-4">
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
            connectionStatus === 'Connected' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              connectionStatus === 'Connected' ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span>{connectionStatus}</span>
          </div>
          <button
            onClick={startNewJob}
            className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            <PlayCircle className="w-4 h-4" />
            <span>Start Scraping</span>
          </button>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <Activity className="w-8 h-8 text-blue-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Jobs</p>
              <p className="text-2xl font-bold text-gray-900">
                {jobs.filter(j => j.status === 'running').length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <CheckCircle className="w-8 h-8 text-green-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-gray-900">
                {jobs.filter(j => j.status === 'completed').length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <Database className="w-8 h-8 text-purple-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Jobs</p>
              <p className="text-2xl font-bold text-gray-900">{jobs.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <BarChart3 className="w-8 h-8 text-orange-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">
                {jobs.length > 0 ? Math.round((jobs.filter(j => j.status === 'completed').length / jobs.length) * 100) : 0}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Activity</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={metrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="time" 
                tickFormatter={(time) => new Date(time).toLocaleTimeString()}
              />
              <YAxis />
              <Tooltip 
                labelFormatter={(time) => new Date(time).toLocaleString()}
              />
              <Line type="monotone" dataKey="jobs" stroke="#3B82F6" strokeWidth={2} />
              <Line type="monotone" dataKey="success" stroke="#10B981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Jobs */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Jobs</h3>
          <div className="space-y-3">
            {jobs.slice(0, 6).map((job) => (
              <div key={job.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(job.status)}
                  <div>
                    <p className="font-medium text-gray-900">Job {job.id}</p>
                    <p className="text-sm text-gray-600">Status: {job.status}</p>
                  </div>
                </div>
                <div className="text-sm text-gray-500">
                  {new Date().toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Jobs page
function Jobs() {
  const [jobs, setJobs] = useState([]);
  
  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      const data = await api.get('/jobs');
      setJobs(Object.entries(data || {}).map(([id, job]) => ({ id, ...job })));
    } catch (error) {
      console.error('Failed to load jobs:', error);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">All Jobs</h1>
      
      <div className="bg-white shadow-sm border rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Job ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {jobs.map((job) => (
              <tr key={job.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {job.id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    job.status === 'completed' ? 'bg-green-100 text-green-800' :
                    job.status === 'running' ? 'bg-blue-100 text-blue-800' :
                    job.status === 'failed' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {job.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date().toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button className="text-indigo-600 hover:text-indigo-900">
                    View Details
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Data page
function Data() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const result = await api.get('/data');
      setData(result || []);
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  const exportData = async (format) => {
    try {
      const response = await fetch(`/api/export?format=${format}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `scraped_data.${format}`;
      a.click();
    } catch (error) {
      console.error('Failed to export data:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Scraped Data</h1>
        <div className="flex space-x-2">
          <button 
            onClick={() => exportData('csv')}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
          >
            Export CSV
          </button>
          <button 
            onClick={() => exportData('json')}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Export JSON
          </button>
        </div>
      </div>
      
      <div className="bg-white shadow-sm border rounded-lg overflow-hidden">
        {data.length > 0 ? (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {Object.keys(data[0]).map((key) => (
                  <th key={key} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {key}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.map((item, index) => (
                <tr key={index}>
                  {Object.values(item).map((value, i) => (
                    <td key={i} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {typeof value === 'string' && value.length > 50 
                        ? `${value.substring(0, 50)}...` 
                        : String(value)
                      }
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="text-center py-12">
            <Database className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No data</h3>
            <p className="mt-1 text-sm text-gray-500">Start a scraping job to see data here.</p>
          </div>
        )}
      </div>
    </div>
  );
}

// Navigation component
function Navigation() {
  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Activity className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">BI Scraper</span>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              <Link to="/" className="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                Dashboard
              </Link>
              <Link to="/jobs" className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                Jobs
              </Link>
              <Link to="/data" className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                Data
              </Link>
              <Link to="/marketplace" className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                <Package className="w-4 h-4 mr-1" />
                Marketplace
              </Link>
              <Link to="/analytics" className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                <TrendingUp className="w-4 h-4 mr-1" />
                Analytics
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

// Main App component
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Navigation />
          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/jobs" element={<Jobs />} />
                <Route path="/data" element={<Data />} />
                <Route path="/marketplace" element={<SpiderMarketplace />} />
                <Route path="/analytics" element={<AnalyticsDashboard />} />
              </Routes>
            </div>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

// Mount the app
const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);
