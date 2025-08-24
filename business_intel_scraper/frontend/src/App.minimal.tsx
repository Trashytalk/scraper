import React, { useState, useEffect } from "react";
import "./styles/enhanced-ui.css";

interface Job {
  id: number;
  name: string;
  url: string;
  status: string;
  created_at: string;
  scraper_type: string;
}

interface JobResults {
  job_name: string;
  data: any;
}

const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState("operations");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [jobResults, setJobResults] = useState<JobResults | null>(null);
  const [isBackendConnected, setIsBackendConnected] = useState(false);

  useEffect(() => {
    // Test backend connection
    fetch("/api/health")
      .then(() => setIsBackendConnected(true))
      .catch(() => setIsBackendConnected(false));

    // Fetch jobs
    fetch("/api/jobs")
      .then(res => res.json())
      .then(data => setJobs(data.jobs || []))
      .catch(console.error);
  }, []);

  const getJobResults = async (jobId: number) => {
    try {
      const response = await fetch(`/api/jobs/${jobId}/results`);
      const data = await response.json();
      console.log("Setting job results:", data);
      setJobResults(data);
    } catch (error) {
      console.error("Failed to fetch job results:", error);
    }
  };

  return (
    <div className="cyber-glass" style={{ padding: "20px", minHeight: "100vh" }}>
      <header style={{ marginBottom: "30px" }}>
        <h1>Business Intelligence Scraper</h1>
        <div>Status: {isBackendConnected ? "Online" : "Offline"}</div>
      </header>

      {/* Navigation */}
      <nav style={{ marginBottom: "30px" }}>
        <button 
          onClick={() => setCurrentTab("operations")}
          style={{ 
            marginRight: "10px",
            background: currentTab === "operations" ? "#007acc" : "#333",
            color: "white",
            border: "1px solid #555",
            padding: "10px",
            borderRadius: "4px"
          }}
        >
          Operations
        </button>
        <button 
          onClick={() => setCurrentTab("dashboard")}
          style={{ 
            background: currentTab === "dashboard" ? "#007acc" : "#333",
            color: "white",
            border: "1px solid #555",
            padding: "10px",
            borderRadius: "4px"
          }}
        >
          Dashboard
        </button>
      </nav>

      {/* Operations Tab */}
      {currentTab === "operations" && (
        <div>
          <h2>Operations</h2>
          <div style={{ marginBottom: "20px" }}>
            <h3>Create New Job</h3>
            <form>
              <input type="text" placeholder="Job Name" style={{ marginRight: "10px", padding: "8px" }} />
              <input type="url" placeholder="Target URL" style={{ marginRight: "10px", padding: "8px" }} />
              <button type="submit" style={{ padding: "8px 16px" }}>Create Job</button>
            </form>
          </div>
        </div>
      )}

      {/* Dashboard Tab */}
      {currentTab === "dashboard" && (
        <div>
          <h2>Dashboard</h2>
          <div>
            <h3>Recent Jobs</h3>
            {jobs.map((job) => (
              <div key={job.id} style={{ 
                border: "1px solid #555", 
                padding: "15px", 
                marginBottom: "10px",
                borderRadius: "4px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center"
              }}>
                <div>
                  <strong>{job.name}</strong>
                  <div style={{ fontSize: "12px", color: "#888" }}>
                    Created: {new Date(job.created_at).toLocaleString()}
                  </div>
                </div>
                <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                  <span style={{
                    padding: "4px 8px",
                    borderRadius: "12px",
                    fontSize: "12px",
                    backgroundColor: job.status === "completed" ? "#28a745" : 
                                   job.status === "failed" ? "#dc3545" : 
                                   job.status === "running" ? "#007bff" : "#6c757d",
                    color: "white"
                  }}>
                    {job.status}
                  </span>
                  {job.status === "completed" && (
                    <button
                      onClick={() => getJobResults(job.id)}
                      style={{
                        padding: "4px 8px",
                        fontSize: "12px",
                        background: "#007acc",
                        color: "white",
                        border: "1px solid #555",
                        borderRadius: "4px",
                        cursor: "pointer"
                      }}
                    >
                      View Results
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Global Results Modal */}
      {jobResults && (
        <div style={{
          position: "fixed",
          top: "0",
          left: "0",
          right: "0",
          bottom: "0",
          backgroundColor: "rgba(0,0,0,0.7)",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          zIndex: 9999
        }}>
          <div style={{
            background: "#1e1e1e",
            color: "white",
            padding: "20px",
            borderRadius: "8px",
            maxWidth: "800px",
            width: "90%",
            maxHeight: "80vh",
            overflow: "auto",
            border: "1px solid #555"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <h2 style={{ margin: "0" }}>Job Results: {jobResults.job_name}</h2>
              <button
                onClick={() => setJobResults(null)}
                style={{
                  background: "#dc3545",
                  color: "white",
                  border: "none",
                  padding: "8px 16px",
                  borderRadius: "4px",
                  cursor: "pointer"
                }}
              >
                Close
              </button>
            </div>
            <div>
              <pre style={{ 
                background: "#2d2d2d", 
                padding: "15px", 
                borderRadius: "4px",
                overflow: "auto",
                fontSize: "12px"
              }}>
                {JSON.stringify(jobResults, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
