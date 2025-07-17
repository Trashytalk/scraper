function App() {
  const [data, setData] = React.useState([]);
  const [jobs, setJobs] = React.useState({});
  const loadData = () => {
    fetch('/data')
      .then((res) => res.json())
      .then(setData)
      .catch(() => {});
    fetch('/jobs')
      .then((res) => res.json())
      .then(setJobs)
      .catch(() => {});
  };

  React.useEffect(loadData, []);

  return (
    <div style={{ fontFamily: 'sans-serif' }}>
      <h1>Scraped Results</h1>
      <button onClick={loadData}>Refresh</button>
      <ul>
        {data.map((item, idx) => (
          <li key={idx}>{JSON.stringify(item)}</li>
        ))}
      </ul>

      <h2>Job Status</h2>
      <ul>
        {Object.entries(jobs).map(([id, job]) => (
          <li key={id}>
            {id}: {job.status}
          </li>
        ))}
      </ul>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
