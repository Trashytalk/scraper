function App() {
  const [data, setData] = React.useState([]);
  const [jobs, setJobs] = React.useState({});

  React.useEffect(() => {
    fetch('/data')
      .then(res => res.json())
      .then(setData)
      .catch(() => {});
    fetch('/jobs')
      .then(res => res.json())
      .then(setJobs)
      .catch(() => {});
  }, []);

  return (
    <div>
      <h1>Scraped Data</h1>
      <ul>{data.map((item, idx) => <li key={idx}>{JSON.stringify(item)}</li>)}</ul>
      <h1>Job Status</h1>
      <pre>{JSON.stringify(jobs, null, 2)}</pre>
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
