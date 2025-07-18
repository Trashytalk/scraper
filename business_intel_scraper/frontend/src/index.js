const { BrowserRouter, Routes, Route, Link } = ReactRouterDOM;

function ResultsTable({ data }) {
  if (!data.length) return <p>No results</p>;
  const headers = Object.keys(data[0]);
  return (
    <table className="table">
      <thead>
        <tr>{headers.map((h) => (<th key={h}>{h}</th>))}</tr>
      </thead>
      <tbody>
        {data.map((row, idx) => (
          <tr key={idx}>
            {headers.map((h) => (
              <td key={h}>{String(row[h])}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function ResultsPage({ data, refresh }) {
  React.useEffect(() => {
    const id = setInterval(refresh, 5000);
    return () => clearInterval(id);
  }, []);
  return (
    <section>
      <div className="section-header">
        <h2>Scraped Results</h2>
        <button onClick={refresh}>Refresh</button>
      </div>
      <ResultsTable data={data} />
    </section>
  );
}

function JobsPage({ jobs, refresh, startJob, logs }) {
  const logRef = React.useRef(null);
  React.useEffect(() => {
    const id = setInterval(refresh, 5000);
    return () => clearInterval(id);
  }, []);
  React.useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logs]);
  return (
    <section>
      <div className="section-header">
        <h2>Job Management</h2>
        <div>
          <button onClick={refresh}>Refresh</button>
          <button onClick={startJob}>Start Job</button>
        </div>
      </div>
      <table className="table">
        <thead>
          <tr>
            <th>Job ID</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(jobs).map(([id, job]) => (
            <tr key={id}>
              <td>{id}</td>
              <td>
                {job.status}
                {job.status === 'running' && <span className="progress" />}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <h3>Logs</h3>
      <pre ref={logRef} className="logs">{logs.join('\n')}</pre>
    </section>
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
    const id = setInterval(() => {
      loadData();
      loadJobs();
    }, 5000);
    return () => clearInterval(id);
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
      <header>
        <nav>
          <Link to="/results">Results</Link>
          <Link to="/jobs">Jobs</Link>
        </nav>
      </header>
      <main>
        <Routes>
          <Route
            path="/jobs"
            element={<JobsPage jobs={jobs} refresh={loadJobs} startJob={startJob} logs={logs} />}
          />
          <Route path="/*" element={<ResultsPage data={data} refresh={loadData} />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
