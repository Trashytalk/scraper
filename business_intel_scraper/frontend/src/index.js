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

function JobsTable({ jobs }) {
  return (
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
  );
}

function LogViewer({ logs }) {
  const ref = React.useRef(null);
  React.useEffect(() => {
    if (ref.current) {
      ref.current.scrollTop = ref.current.scrollHeight;
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
