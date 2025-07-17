const { BrowserRouter, Routes, Route, Link } = ReactRouterDOM;

function ResultsPage({ data, refresh }) {
  return (
    <div style={{ fontFamily: 'sans-serif' }}>
      <h1>Scraped Results</h1>
      <button onClick={refresh}>Refresh</button>
      <ul>
        {data.map((item, idx) => (
          <li key={idx}>{JSON.stringify(item)}</li>
        ))}
      </ul>
    </div>
  );
}

function JobsPage({ jobs, refresh, startJob, logs }) {
  return (
    <div style={{ fontFamily: 'sans-serif' }}>
      <h1>Job Management</h1>
      <button onClick={refresh}>Refresh</button>
      <button onClick={startJob}>Start Job</button>
      <ul>
        {Object.entries(jobs).map(([id, job]) => (
          <li key={id}>
            {id}: {job.status}
          </li>
        ))}
      </ul>
      <h2>Logs</h2>
      <pre style={{ maxHeight: '200px', overflow: 'auto', background: '#eee', padding: '0.5rem' }}>
        {logs.join('\n')}
      </pre>
    </div>
  );
}

function App() {
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
      setLogs((l) => [...l.slice(-99), e.data]);
    };
    return () => {
      ws.close();
      es.close();
    };
  }, []);

  return (
    <BrowserRouter>
      <nav style={{ marginBottom: '1rem' }}>
        <Link to="/results">Results</Link> | <Link to="/jobs">Jobs</Link>
      </nav>
      <Routes>
        <Route path="/jobs" element={<JobsPage jobs={jobs} refresh={loadJobs} startJob={startJob} logs={logs} />} />
        <Route path="/*" element={<ResultsPage data={data} refresh={loadData} />} />
      </Routes>
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
