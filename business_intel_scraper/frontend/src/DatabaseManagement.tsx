import React, { useState, useEffect } from "react";

interface TableInfo {
  name: string;
  columns: { name: string; type: string; nullable: boolean; primary_key: boolean }[];
  row_count: number;
}

interface TableData {
  table_name: string;
  total_count: number;
  limit: number;
  offset: number;
  data: any[];
}

interface DatabaseManagementProps {
  token: string;
}

const DatabaseManagement: React.FC<DatabaseManagementProps> = ({ token }) => {
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>("");
  const [tableData, setTableData] = useState<TableData | null>(null);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const [pageSize] = useState(50);
  const [customQuery, setCustomQuery] = useState("");
  const [queryResult, setQueryResult] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<"tables" | "query" | "cleanup">("tables");
  const [error, setError] = useState<string>("");

  useEffect(() => {
    loadTables();
  }, [token]);

  const loadTables = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/api/database/tables", {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        setTables(data.tables);
      } else {
        setError("Failed to load database tables");
      }
    } catch (err) {
      setError("Error connecting to database");
    } finally {
      setLoading(false);
    }
  };

  const loadTableData = async (tableName: string, offset: number = 0) => {
    try {
      setLoading(true);
      setError("");
      const response = await fetch(
        `http://localhost:8000/api/database/table/${tableName}?limit=${pageSize}&offset=${offset}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setTableData(data);
        setSelectedTable(tableName);
        setCurrentPage(Math.floor(offset / pageSize));
      } else {
        setError("Failed to load table data");
      }
    } catch (err) {
      setError("Error loading table data");
    } finally {
      setLoading(false);
    }
  };

  const executeQuery = async () => {
    if (!customQuery.trim()) {
      setError("Please enter a query");
      return;
    }

    try {
      setLoading(true);
      setError("");
      const response = await fetch("http://localhost:8000/api/database/query", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: customQuery }),
      });

      if (response.ok) {
        const data = await response.json();
        setQueryResult(data);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Query failed");
      }
    } catch (err) {
      setError("Error executing query");
    } finally {
      setLoading(false);
    }
  };

  const deleteRecord = async (tableName: string, recordId: number) => {
    if (!confirm("Are you sure you want to delete this record?")) {
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(
        `http://localhost:8000/api/database/table/${tableName}/record/${recordId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (response.ok) {
        // Reload current table data
        if (tableData) {
          loadTableData(selectedTable, currentPage * pageSize);
        }
        loadTables(); // Refresh table counts
      } else {
        setError("Failed to delete record");
      }
    } catch (err) {
      setError("Error deleting record");
    } finally {
      setLoading(false);
    }
  };

  const cleanupDatabase = async (cleanupType: string) => {
    if (!confirm(`Are you sure you want to perform ${cleanupType} cleanup?`)) {
      return;
    }

    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/api/database/cleanup", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ type: cleanupType }),
      });

      if (response.ok) {
        const data = await response.json();
        alert(`${data.message}. Deleted ${data.deleted_count} records.`);
        loadTables(); // Refresh table counts
        if (tableData) {
          loadTableData(selectedTable, currentPage * pageSize);
        }
      } else {
        setError("Cleanup failed");
      }
    } catch (err) {
      setError("Error during cleanup");
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (direction: "prev" | "next") => {
    if (!tableData) return;

    const newOffset = direction === "next" 
      ? (currentPage + 1) * pageSize 
      : (currentPage - 1) * pageSize;
    
    if (newOffset >= 0 && newOffset < tableData.total_count) {
      loadTableData(selectedTable, newOffset);
    }
  };

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) {
      return "NULL";
    }
    if (typeof value === "object") {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  };

  const tabStyle = (tabName: string) => ({
    padding: "8px 16px",
    margin: "0 4px",
    border: "1px solid #ddd",
    borderRadius: "4px",
    cursor: "pointer",
    backgroundColor: activeTab === tabName ? "#1976d2" : "#f8f9fa",
    color: activeTab === tabName ? "white" : "#333",
  });

  return (
    <div style={{ padding: "20px", maxWidth: "100%", overflow: "auto" }}>
      <h2>🗄️ Database Management</h2>
      
      {error && (
        <div style={{ 
          backgroundColor: "#ffebee", 
          color: "#c62828", 
          padding: "12px", 
          borderRadius: "4px", 
          marginBottom: "16px" 
        }}>
          {error}
        </div>
      )}

      {/* Tab Navigation */}
      <div style={{ marginBottom: "20px", display: "flex", flexWrap: "wrap" }}>
        <button
          style={tabStyle("tables")}
          onClick={() => setActiveTab("tables")}
        >
          📊 Tables
        </button>
        <button
          style={tabStyle("query")}
          onClick={() => setActiveTab("query")}
        >
          🔍 Custom Query
        </button>
        <button
          style={tabStyle("cleanup")}
          onClick={() => setActiveTab("cleanup")}
        >
          🧹 Cleanup
        </button>
      </div>

      {/* Tables Tab */}
      {activeTab === "tables" && (
        <div>
          <div style={{ display: "flex", gap: "20px", marginBottom: "20px" }}>
            {/* Tables List */}
            <div style={{ minWidth: "300px" }}>
              <h3>Database Tables</h3>
              {loading && <p>Loading tables...</p>}
              <div style={{ border: "1px solid #ddd", borderRadius: "4px" }}>
                {tables.map((table) => (
                  <div
                    key={table.name}
                    style={{
                      padding: "12px",
                      borderBottom: "1px solid #eee",
                      cursor: "pointer",
                      backgroundColor: selectedTable === table.name ? "#e3f2fd" : "white",
                    }}
                    onClick={() => loadTableData(table.name)}
                  >
                    <strong>{table.name}</strong>
                    <div style={{ fontSize: "0.9em", color: "#666" }}>
                      {table.row_count} rows • {table.columns.length} columns
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Table Data */}
            <div style={{ flex: 1 }}>
              {selectedTable && tableData && (
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                    <h3>{tableData.table_name} Data</h3>
                    <div>
                      <span>
                        Showing {tableData.offset + 1}-{Math.min(tableData.offset + pageSize, tableData.total_count)} of {tableData.total_count}
                      </span>
                      <button
                        onClick={() => handlePageChange("prev")}
                        disabled={currentPage === 0}
                        style={{ marginLeft: "10px", padding: "4px 8px" }}
                      >
                        ← Prev
                      </button>
                      <button
                        onClick={() => handlePageChange("next")}
                        disabled={(currentPage + 1) * pageSize >= tableData.total_count}
                        style={{ marginLeft: "5px", padding: "4px 8px" }}
                      >
                        Next →
                      </button>
                    </div>
                  </div>

                  <div style={{ overflowX: "auto", border: "1px solid #ddd", borderRadius: "4px" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse" }}>
                      <thead>
                        <tr style={{ backgroundColor: "#f5f5f5" }}>
                          {tableData.data.length > 0 && Object.keys(tableData.data[0]).map((key) => (
                            <th key={key} style={{ padding: "8px", border: "1px solid #ddd", textAlign: "left" }}>
                              {key}
                            </th>
                          ))}
                          <th style={{ padding: "8px", border: "1px solid #ddd", textAlign: "center" }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {tableData.data.map((row, index) => (
                          <tr key={index}>
                            {Object.values(row).map((value, cellIndex) => (
                              <td key={cellIndex} style={{ padding: "8px", border: "1px solid #ddd", maxWidth: "200px" }}>
                                <div style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                                  {formatValue(value)}
                                </div>
                              </td>
                            ))}
                            <td style={{ padding: "8px", border: "1px solid #ddd", textAlign: "center" }}>
                              {["jobs", "job_results", "analytics"].includes(selectedTable) && (
                                <button
                                  onClick={() => deleteRecord(selectedTable, row.id)}
                                  style={{
                                    padding: "2px 6px",
                                    backgroundColor: "#f44336",
                                    color: "white",
                                    border: "none",
                                    borderRadius: "3px",
                                    fontSize: "0.8em",
                                  }}
                                >
                                  Delete
                                </button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Custom Query Tab */}
      {activeTab === "query" && (
        <div>
          <h3>🔍 Custom SQL Query</h3>
          <p style={{ color: "#666", marginBottom: "16px" }}>
            Execute read-only SELECT queries against the database. Only SELECT statements are allowed for security.
          </p>
          
          <div style={{ marginBottom: "16px" }}>
            <textarea
              value={customQuery}
              onChange={(e) => setCustomQuery(e.target.value)}
              placeholder="SELECT * FROM jobs WHERE status = 'completed' LIMIT 10"
              style={{
                width: "100%",
                height: "100px",
                padding: "8px",
                border: "1px solid #ddd",
                borderRadius: "4px",
                fontFamily: "monospace",
              }}
            />
          </div>
          
          <button
            onClick={executeQuery}
            disabled={loading}
            style={{
              padding: "8px 16px",
              backgroundColor: "#1976d2",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: loading ? "not-allowed" : "pointer",
            }}
          >
            {loading ? "Executing..." : "Execute Query"}
          </button>

          {queryResult && (
            <div style={{ marginTop: "20px" }}>
              <h4>Query Results ({queryResult.result_count} rows)</h4>
              <div style={{ overflowX: "auto", border: "1px solid #ddd", borderRadius: "4px" }}>
                <pre style={{ padding: "16px", backgroundColor: "#f5f5f5", margin: 0 }}>
                  {JSON.stringify(queryResult.data, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Cleanup Tab */}
      {activeTab === "cleanup" && (
        <div>
          <h3>🧹 Database Cleanup</h3>
          <p style={{ color: "#666", marginBottom: "20px" }}>
            Remove old or unnecessary data from the database. Use with caution - these operations cannot be undone.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "16px", maxWidth: "400px" }}>
            <div style={{ padding: "16px", border: "1px solid #ddd", borderRadius: "4px" }}>
              <h4>Failed Jobs</h4>
              <p style={{ fontSize: "0.9em", color: "#666" }}>
                Remove all failed jobs and their associated results.
              </p>
              <button
                onClick={() => cleanupDatabase("failed_jobs")}
                disabled={loading}
                style={{
                  padding: "8px 16px",
                  backgroundColor: "#ff9800",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: loading ? "not-allowed" : "pointer",
                }}
              >
                Clean Failed Jobs
              </button>
            </div>

            <div style={{ padding: "16px", border: "1px solid #ddd", borderRadius: "4px" }}>
              <h4>Old Analytics</h4>
              <p style={{ fontSize: "0.9em", color: "#666" }}>
                Remove analytics data older than 30 days.
              </p>
              <button
                onClick={() => cleanupDatabase("old_analytics")}
                disabled={loading}
                style={{
                  padding: "8px 16px",
                  backgroundColor: "#ff9800",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: loading ? "not-allowed" : "pointer",
                }}
              >
                Clean Old Analytics
              </button>
            </div>

            <div style={{ padding: "16px", border: "1px solid #ddd", borderRadius: "4px" }}>
              <h4>Empty Results</h4>
              <p style={{ fontSize: "0.9em", color: "#666" }}>
                Remove job results that contain no data.
              </p>
              <button
                onClick={() => cleanupDatabase("empty_results")}
                disabled={loading}
                style={{
                  padding: "8px 16px",
                  backgroundColor: "#ff9800",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: loading ? "not-allowed" : "pointer",
                }}
              >
                Clean Empty Results
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DatabaseManagement;
