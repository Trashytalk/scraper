import React from "react";

interface DebugProps {
  token: string;
  jobs: any[];
  analytics: any;
  performance: any;
}

const DebugInterface: React.FC<DebugProps> = ({ token, jobs, analytics, performance }) => {
  return (
    <div style={{
      padding: "20px",
      backgroundColor: "#f8f9fa",
      borderRadius: "8px",
      margin: "20px 0"
    }}>
      <h2>🐛 Debug Information</h2>
      <div style={{ marginBottom: "20px" }}>
        <h3>Authentication Status</h3>
        <p><strong>Token:</strong> {token ? `${token.substring(0, 20)}...` : "No token"}</p>
        <p><strong>Token Length:</strong> {token ? token.length : 0}</p>
      </div>
      
      <div style={{ marginBottom: "20px" }}>
        <h3>Jobs Data</h3>
        <p><strong>Jobs Count:</strong> {jobs ? jobs.length : 0}</p>
        <pre style={{ backgroundColor: "#e9ecef", padding: "10px", borderRadius: "4px", fontSize: "12px" }}>
          {JSON.stringify(jobs, null, 2)}
        </pre>
      </div>
      
      <div style={{ marginBottom: "20px" }}>
        <h3>Analytics Data</h3>
        <pre style={{ backgroundColor: "#e9ecef", padding: "10px", borderRadius: "4px", fontSize: "12px" }}>
          {JSON.stringify(analytics, null, 2)}
        </pre>
      </div>
      
      <div style={{ marginBottom: "20px" }}>
        <h3>Performance Data</h3>
        <pre style={{ backgroundColor: "#e9ecef", padding: "10px", borderRadius: "4px", fontSize: "12px" }}>
          {JSON.stringify(performance, null, 2)}
        </pre>
      </div>
    </div>
  );
};

export default DebugInterface;
