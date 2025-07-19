// Business Intelligence Scraper Dashboard
const { useState, useEffect, useRef } = React;

// API base URL
const API_BASE = window.location.origin;

// Utility functions
const formatTimestamp = (timestamp) => {
  return new Date(timestamp).toLocaleString();
};

const getStatusColor = (status) => {
  const colors = {
    running: '#ffa726',
    completed: '#66bb6a',
    failed: '#ef5350',
    pending: '#42a5f5',
  };
  return colors[status] || '#757575';
};

// Components
function StatusBadge({ status }) {
  const style = {
    padding: '4px 8px',
    borderRadius: '4px',
    color: 'white',
    backgroundColor: getStatusColor(status),
    fontSize: '12px',
    fontWeight: 'bold',
  };
  
  return <span style={style}>{status}</span>;
}

function ResultsTable({ data }) {
  if (!data.length) {
    return (
      <div className="empty-state">
        <p>No results available</p>
        <small>Start a scraping job to see data here</small>
      </div>
    );
  }
  
  const headers = Object.keys(data[0]);
  
  return (
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            {headers.map((h) => (
              <th key={h}>{h.replace(/_/g, ' ').toUpperCase()}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx}>
              {headers.map((h) => (
                <td key={h} title={String(row[h])}>
                  {String(row[h]).length > 50 
                    ? String(row[h]).substring(0, 50) + '...'
                    : String(row[h])
                  }
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function JobsTable({ jobs, onRefresh }) {
  const handleRefresh = () => {
    onRefresh();
  };

  return (
    <div className="jobs-section">
      <div className="section-header">
        <h3>Active Jobs</h3>
        <button onClick={handleRefresh} className="btn btn-small">
          🔄 Refresh
        </button>
      </div>
      
      {Object.keys(jobs).length === 0 ? (
        <div className="empty-state">
          <p>No active jobs</p>
          <small>Start a new scraping job below</small>
        </div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Job ID</th>
              <th>Status</th>
              <th>Started</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(jobs).map(([id, job]) => (
              <tr key={id}>
                <td>
                  <code>{id.substring(0, 8)}...</code>
                </td>
                <td>
                  <StatusBadge status={job.status || 'unknown'} />
                  {job.status === 'running' && (
                    <span className="progress-indicator">⏳</span>
                  )}
                </td>
                <td>
                  {job.started_at ? formatTimestamp(job.started_at) : 'Unknown'}
                </td>
                <td>
                  <button 
                    className="btn btn-small"
                    onClick={() => window.open(`/tasks/${id}`, '_blank')}
                  >
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function LogViewer({ logs }) {
  const ref = useRef(null);
  
  useEffect(() => {
    if (ref.current) {
      ref.current.scrollTop = ref.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="log-viewer">
      <div className="section-header">
        <h3>Live Logs</h3>
        <span className="log-count">{logs.length} entries</span>
      </div>
      <div ref={ref} className="log-content">
        {logs.length === 0 ? (
          <div className="empty-state">
            <p>No logs yet</p>
            <small>Logs will appear here when jobs are running</small>
          </div>
        ) : (
          logs.map((log, idx) => (
            <div key={idx} className={`log-entry log-${log.level || 'info'}`}>
              <span className="log-timestamp">
                {formatTimestamp(log.timestamp)}
              </span>
              <span className="log-level">{log.level || 'INFO'}</span>
              <span className="log-message">{log.message}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function JobLauncher({ onJobStarted }) {
  const [isLoading, setIsLoading] = useState(false);
  const [selectedSpider, setSelectedSpider] = useState('example');
  
  const spiderOptions = [
    { value: 'example', label: 'Example Spider (Demo)' },
    { value: 'national_company_registry', label: 'Company Registry' },
    { value: 'market_news', label: 'Market News' },
  ];

  const handleStartJob = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/scrape`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          spider: selectedSpider,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        onJobStarted(data);
      } else {
        alert('Failed to start job');
      }
    } catch (error) {
      alert('Error starting job: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="job-launcher">
      <div className="section-header">
        <h3>Start New Job</h3>
      </div>
      
      <div className="form-group">
        <label>Select Spider:</label>
        <select 
          value={selectedSpider} 
          onChange={(e) => setSelectedSpider(e.target.value)}
          className="form-control"
        >
          {spiderOptions.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
      
      <button 
        onClick={handleStartJob} 
        disabled={isLoading}
        className="btn btn-primary"
      >
        {isLoading ? '🚀 Starting...' : '🚀 Start Job'}
      </button>
    </div>
  );
}

function SystemStatus({ status }) {
  const getSystemStatusColor = (status) => {
    return status === 'healthy' ? '#66bb6a' : '#ef5350';
  };

  return (
    <div className="system-status">
      <div className="status-item">
        <span className="status-label">API Status:</span>
        <span 
          className="status-value"
          style={{ color: getSystemStatusColor(status.api) }}
        >
          {status.api || 'unknown'}
        </span>
      </div>
      <div className="status-item">
        <span className="status-label">Database:</span>
        <span 
          className="status-value"
          style={{ color: getSystemStatusColor(status.database) }}
        >
          {status.database || 'unknown'}
        </span>
      </div>
      <div className="status-item">
        <span className="status-label">Workers:</span>
        <span className="status-value">
          {status.workers || 0} active
        </span>
      </div>
    </div>
  );
}

// Main Dashboard Component
function Dashboard() {
  const [data, setData] = useState([]);
  const [jobs, setJobs] = useState({});
  const [logs, setLogs] = useState([]);
  const [status, setStatus] = useState({});
  const [activeTab, setActiveTab] = useState('jobs');

  // Fetch data from API
  const fetchData = async () => {
    try {
      const response = await fetch(`${API_BASE}/data`);
      if (response.ok) {
        const result = await response.json();
        setData(result);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const fetchJobs = async () => {
    try {
      const response = await fetch(`${API_BASE}/jobs`);
      if (response.ok) {
        const result = await response.json();
        setJobs(result);
      }
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/`);
      if (response.ok) {
        const result = await response.json();
        setStatus({
          api: 'healthy',
          database: result.database_url ? 'healthy' : 'disconnected',
          workers: 1,
        });
      }
    } catch (error) {
      setStatus({
        api: 'disconnected',
        database: 'unknown',
        workers: 0,
      });
    }
  };

  // Setup live updates
  useEffect(() => {
    // Initial fetch
    fetchData();
    fetchJobs();
    fetchStatus();

    // Setup periodic refresh
    const interval = setInterval(() => {
      fetchJobs();
      fetchStatus();
    }, 5000);

    // Setup WebSocket for real-time logs (if available)
    try {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const ws = new WebSocket(`${wsProtocol}//${window.location.host}/ws/notifications`);
      
      ws.onmessage = (event) => {
        const logEntry = {
          timestamp: new Date().toISOString(),
          level: 'info',
          message: event.data,
        };
        setLogs(prev => [...prev.slice(-99), logEntry]); // Keep last 100 logs
      };

      return () => {
        clearInterval(interval);
        ws.close();
      };
    } catch (error) {
      console.error('WebSocket not available:', error);
      return () => clearInterval(interval);
    }
  }, []);

  const handleJobStarted = (jobData) => {
    setLogs(prev => [...prev, {
      timestamp: new Date().toISOString(),
      level: 'info',
      message: `Started job: ${jobData.task_id}`,
    }]);
    fetchJobs(); // Refresh jobs list
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>🔍 Business Intelligence Scraper</h1>
        <SystemStatus status={status} />
      </header>

      <nav className="dashboard-nav">
        <button 
          className={`nav-btn ${activeTab === 'jobs' ? 'active' : ''}`}
          onClick={() => setActiveTab('jobs')}
        >
          📋 Jobs
        </button>
        <button 
          className={`nav-btn ${activeTab === 'data' ? 'active' : ''}`}
          onClick={() => setActiveTab('data')}
        >
          📊 Data
        </button>
        <button 
          className={`nav-btn ${activeTab === 'logs' ? 'active' : ''}`}
          onClick={() => setActiveTab('logs')}
        >
          📝 Logs
        </button>
      </nav>

      <main className="dashboard-content">
        {activeTab === 'jobs' && (
          <div className="tab-content">
            <div className="grid">
              <div className="grid-item">
                <JobLauncher onJobStarted={handleJobStarted} />
              </div>
              <div className="grid-item grid-span-2">
                <JobsTable jobs={jobs} onRefresh={fetchJobs} />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'data' && (
          <div className="tab-content">
            <div className="section-header">
              <h2>Scraped Data</h2>
              <button onClick={fetchData} className="btn btn-small">
                🔄 Refresh
              </button>
            </div>
            <ResultsTable data={data} />
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="tab-content">
            <LogViewer logs={logs} />
          </div>
        )}
      </main>
    </div>
  );
}

// Mount the app
ReactDOM.render(<Dashboard />, document.getElementById('root'));
    }
  }, [logs]);
  return <pre ref={ref} className="logs">{logs.join('\n')}</pre>;
}

function Dashboard() {
  const [data, setData] = React.useState([]);
  const [jobs, setJobs] = React.useState({});
  const [logs, setLogs] = React.useState([]);

  const loadData = () => {
    fetch('/data')
      .then((res) => res.json())
      .then(setData)
      .catch(() => {});
  };

  const loadJobs = () => {
    fetch('/jobs')
      .then((res) => res.json())
      .then(setJobs)
      .catch(() => {});
  };

  const startJob = () => {
    fetch('/scrape', { method: 'POST' })
      .then((res) => res.json())
      .then((res) => {
        setJobs((j) => ({ ...j, [res.task_id]: { status: 'running' } }));
      })
      .catch(() => {});
  };

  React.useEffect(() => {
    loadData();
    loadJobs();
    const dataId = setInterval(loadData, 5000);
    const jobId = setInterval(loadJobs, 5000);
    return () => {
      clearInterval(dataId);
      clearInterval(jobId);
    };
  }, []);

  React.useEffect(() => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${wsProtocol}://${window.location.host}/ws/notifications`);
    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        setJobs((j) => ({ ...j, [msg.job_id]: { status: msg.status } }));
      } catch {}
    };
    const es = new EventSource('/logs/stream');
    es.onmessage = (e) => {
      setLogs((l) => [...l.slice(-199), e.data]);
    };
    return () => {
      ws.close();
      es.close();
    };
  }, []);

  return (
    <div className="dashboard">
      <section className="dashboard-column">
        <div className="section-header">
          <h2>Jobs</h2>
          <button onClick={startJob}>Start Job</button>
        </div>
        <JobsTable jobs={jobs} />
      </section>
      <section className="dashboard-column">
        <div className="section-header">
          <h2>Logs</h2>
        </div>
        <LogViewer logs={logs} />
      </section>
      <section className="dashboard-column dashboard-wide">
        <div className="section-header">
          <h2>Scraped Results</h2>
          <button onClick={loadData}>Refresh</button>
        </div>
        <ResultsTable data={data} />
      </section>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<Dashboard />);
