import React, { useState } from "react";

interface OperationsProps {
  jobs: any[];
  newJob: any;
  setNewJob: (job: any) => void;
  operationsConfig: any;
  updateOperationsConfig: (updates: any) => void;
  toggleSection: (section: string) => void;
  configPanelOpen: boolean;
  toggleConfigPanel: () => void;
  workflowSidebarOpen: boolean;
  setWorkflowSidebarOpen: (open: boolean) => void;
  selectedJobForWorkflow: any;
  setSelectedJobForWorkflow: (job: any) => void;
  isSubmitting: boolean;
  createJob: (e: React.FormEvent) => void;
  fetchJobs: () => void;
  getJobDetails: (id: number) => void;
  getJobResults: (id: number) => void;
  startJob: (id: number) => void;
  resetOperationsConfig: () => void;
}

const OperationsInterface: React.FC<OperationsProps> = ({
  jobs,
  newJob,
  setNewJob,
  isSubmitting,
  createJob,
  fetchJobs,
  getJobDetails,
  getJobResults,
  startJob,
}) => {
  const [activeJobType, setActiveJobType] = useState("intelligent_crawling");
  const [showResults, setShowResults] = useState<{[key: number]: boolean}>({});
  const [jobResults, setJobResults] = useState<{[key: number]: any}>({});

  const updateJobConfig = (key: string, value: any) => {
    setNewJob({
      ...newJob,
      config: {
        ...newJob.config,
        [key]: value,
      },
    });
  };

  const handleGetResults = async (jobId: number) => {
    try {
      const results = await getJobResults(jobId);
      setJobResults({...jobResults, [jobId]: results});
      setShowResults({...showResults, [jobId]: true});
    } catch (error) {
      console.error('Failed to fetch results:', error);
    }
  };

  const toggleResults = (jobId: number) => {
    setShowResults({...showResults, [jobId]: !showResults[jobId]});
  };

  return (
    <div style={{ padding: "20px" }}>
      {/* Operations Header */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "30px",
        padding: "20px",
        backgroundColor: "#f8f9fa",
        borderRadius: "8px",
        border: "1px solid #dee2e6",
      }}>
        <div>
          <h2 style={{ margin: "0 0 10px 0" }}>⚙️ Unified Web Intelligence Collection</h2>
          <p style={{ margin: 0, color: "#666" }}>
            Comprehensive crawling, scraping, and data extraction in one integrated system
          </p>
        </div>
        <button
          onClick={() => fetchJobs()}
          style={{
            padding: "8px 16px",
            backgroundColor: "#17a2b8",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          🔄 Refresh
        </button>
      </div>

      {/* Job Creation Form */}
      <div style={{
        marginBottom: "30px",
        border: "2px solid #28a745",
        borderRadius: "8px",
        padding: "20px",
        backgroundColor: "#f8fff8"
      }}>
        <h3 style={{ 
          margin: "0 0 20px 0", 
          color: "#28a745",
          fontSize: "18px",
          fontWeight: "600"
        }}>
          🚀 Create New Collection Job
        </h3>

        <form onSubmit={createJob} style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
          {/* Job Type Selection */}
          <div>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              Collection Strategy:
            </label>
            <div style={{ display: "flex", gap: "10px", marginBottom: "10px" }}>
              <button
                type="button"
                onClick={() => {
                  setActiveJobType("intelligent_crawling");
                  setNewJob({ ...newJob, type: "intelligent_crawling" });
                }}
                style={{
                  padding: "8px 16px",
                  backgroundColor: activeJobType === "intelligent_crawling" ? "#007bff" : "#f8f9fa",
                  color: activeJobType === "intelligent_crawling" ? "white" : "#333",
                  border: "1px solid #ddd",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                🔗 Intelligent Crawling
              </button>
              <button
                type="button"
                onClick={() => {
                  setActiveJobType("single_page");
                  setNewJob({ ...newJob, type: "single_page" });
                }}
                style={{
                  padding: "8px 16px",
                  backgroundColor: activeJobType === "single_page" ? "#007bff" : "#f8f9fa",
                  color: activeJobType === "single_page" ? "white" : "#333",
                  border: "1px solid #ddd",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                📄 Single Page Extract
              </button>
            </div>
            <p style={{ fontSize: "12px", color: "#666", margin: "5px 0 0 0" }}>
              {activeJobType === "intelligent_crawling" 
                ? "🔗 Discover and extract data from multiple linked pages starting from seed URLs"
                : "📄 Extract specific data from a single target page with custom selectors"
              }
            </p>
          </div>

          {/* Job Name */}
          <div>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              Job Name:
            </label>
            <input
              type="text"
              value={newJob.name || ""}
              onChange={(e) => setNewJob({ ...newJob, name: e.target.value })}
              placeholder="Enter descriptive job name"
              style={{
                width: "100%",
                padding: "8px",
                border: "1px solid #ddd",
                borderRadius: "4px",
                fontSize: "14px",
              }}
            />
          </div>

          {/* URL Input */}
          <div>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              {activeJobType === "intelligent_crawling" ? "Seed URL(s):" : "Target URL:"}
            </label>
            <input
              type="url"
              value={newJob.url || ""}
              onChange={(e) => setNewJob({ ...newJob, url: e.target.value })}
              placeholder={activeJobType === "intelligent_crawling" 
                ? "https://example.com (starting point for crawling)"
                : "https://example.com/specific-page"
              }
              style={{
                width: "100%",
                padding: "8px",
                border: "1px solid #ddd",
                borderRadius: "4px",
                fontSize: "14px",
              }}
            />
            {activeJobType === "intelligent_crawling" && (
              <p style={{ fontSize: "12px", color: "#666", margin: "5px 0 0 0" }}>
                💡 The crawler will discover and follow links from this starting page
              </p>
            )}
          </div>

          {/* Data Extraction Strategy */}
          <div>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              Data Extraction Strategy:
            </label>
            <select
              value={newJob.scraper_type || "intelligent"}
              onChange={(e) => setNewJob({ ...newJob, scraper_type: e.target.value })}
              style={{
                width: "100%",
                padding: "8px",
                border: "1px solid #ddd",
                borderRadius: "4px",
                fontSize: "14px",
              }}
            >
              <option value="intelligent">🧠 Intelligent Auto-Detection</option>
              <option value="e_commerce">🛒 E-commerce Products</option>
              <option value="news">📰 News Articles</option>
              <option value="social_media">📱 Social Media Content</option>
              <option value="directory">📋 Directory Listings</option>
              <option value="job_listings">💼 Job Postings</option>
              <option value="custom">⚙️ Custom Selectors</option>
            </select>
            <p style={{ fontSize: "12px", color: "#666", margin: "5px 0 0 0" }}>
              Choose how to identify and extract relevant data from discovered pages
            </p>
          </div>

          {/* Advanced Configuration */}
          <details style={{ marginTop: "10px" }}>
            <summary style={{ cursor: "pointer", fontWeight: "bold", marginBottom: "10px" }}>
              ⚙️ Advanced Configuration
            </summary>
            <div style={{ padding: "15px", backgroundColor: "#f8f9fa", borderRadius: "4px" }}>
              
              {/* Basic Configuration */}
              <div style={{ marginBottom: "20px" }}>
                <h4 style={{ margin: "0 0 10px 0", color: "#495057" }}>📋 Collection Settings</h4>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                  <div>
                    <label style={{ display: "block", marginBottom: "5px" }}>
                      {activeJobType === "intelligent_crawling" ? "Max Pages to Process:" : "Processing Timeout (s):"}
                    </label>
                    <input
                      type="number"
                      value={activeJobType === "intelligent_crawling" 
                        ? (newJob.config?.max_pages || 50)
                        : (newJob.config?.timeout || 30)
                      }
                      onChange={(e) => updateJobConfig(
                        activeJobType === "intelligent_crawling" ? "max_pages" : "timeout", 
                        parseInt(e.target.value)
                      )}
                      style={{
                        width: "100%",
                        padding: "6px",
                        border: "1px solid #ddd",
                        borderRadius: "4px",
                      }}
                    />
                  </div>
                  {activeJobType === "intelligent_crawling" && (
                    <div>
                      <label style={{ display: "block", marginBottom: "5px" }}>Max Crawl Depth:</label>
                      <input
                        type="number"
                        min="1"
                        max="10"
                        value={newJob.config?.max_depth || 3}
                        onChange={(e) => updateJobConfig("max_depth", parseInt(e.target.value))}
                        style={{
                          width: "100%",
                          padding: "6px",
                          border: "1px solid #ddd",
                          borderRadius: "4px",
                        }}
                      />
                    </div>
                  )}
                  {activeJobType === "single_page" && (
                    <div>
                      <label style={{ display: "block", marginBottom: "5px" }}>Retry Attempts:</label>
                      <input
                        type="number"
                        min="0"
                        max="5"
                        value={newJob.config?.retries || 2}
                        onChange={(e) => updateJobConfig("retries", parseInt(e.target.value))}
                        style={{
                          width: "100%",
                          padding: "6px",
                          border: "1px solid #ddd",
                          borderRadius: "4px",
                        }}
                      />
                    </div>
                  )}
                </div>
              </div>

              {/* Intelligent Crawling Specific Options */}
              {activeJobType === "intelligent_crawling" && (
                <>
                  {/* Link Discovery Configuration */}
                  <div style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#e8f5e8", borderRadius: "6px", border: "1px solid #c3e6c3" }}>
                    <h4 style={{ margin: "0 0 10px 0", color: "#2d5a2d" }}>🔍 Link Discovery & Following</h4>
                    <p style={{ fontSize: "12px", color: "#666", margin: "0 0 10px 0" }}>
                      Configure how the crawler discovers and follows links to new pages
                    </p>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginBottom: "10px" }}>
                      <div>
                        <label style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "13px" }}>
                          <input
                            type="checkbox"
                            checked={newJob.config?.follow_internal_links !== false}
                            onChange={(e) => updateJobConfig("follow_internal_links", e.target.checked)}
                          />
                          Follow Internal Links (same domain)
                        </label>
                      </div>
                      <div>
                        <label style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "13px" }}>
                          <input
                            type="checkbox"
                            checked={newJob.config?.follow_external_links || false}
                            onChange={(e) => updateJobConfig("follow_external_links", e.target.checked)}
                          />
                          Follow External Links (other domains)
                        </label>
                      </div>
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                      <div>
                        <label style={{ display: "block", marginBottom: "5px", fontSize: "13px" }}>
                          URL Patterns to Include:
                          <span style={{ color: "#666", fontSize: "11px" }}> (regex)</span>
                        </label>
                        <input
                          type="text"
                          placeholder=".*product.*|.*article.*"
                          value={newJob.config?.include_patterns || ""}
                          onChange={(e) => updateJobConfig("include_patterns", e.target.value)}
                          style={{
                            width: "100%",
                            padding: "6px",
                            border: "1px solid #ddd",
                            borderRadius: "4px",
                          }}
                        />
                      </div>
                      <div>
                        <label style={{ display: "block", marginBottom: "5px", fontSize: "13px" }}>
                          URL Patterns to Exclude:
                          <span style={{ color: "#666", fontSize: "11px" }}> (regex)</span>
                        </label>
                        <input
                          type="text"
                          placeholder=".*admin.*|.*login.*"
                          value={newJob.config?.exclude_patterns || ""}
                          onChange={(e) => updateJobConfig("exclude_patterns", e.target.value)}
                          style={{
                            width: "100%",
                            padding: "6px",
                            border: "1px solid #ddd",
                            borderRadius: "4px",
                          }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Rate Limiting Configuration */}
                  <div style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#e8f4f8", borderRadius: "6px", border: "1px solid #b8daff" }}>
                    <h4 style={{ margin: "0 0 10px 0", color: "#0056b3" }}>🚦 Crawling Rate & Performance</h4>
                    <p style={{ fontSize: "12px", color: "#666", margin: "0 0 10px 0" }}>
                      Control crawling speed to be respectful to target servers while maintaining efficiency
                    </p>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "10px" }}>
                      <div>
                        <label style={{ display: "block", marginBottom: "5px", fontSize: "13px" }}>
                          Pages/Second:
                          <span style={{ color: "#666", fontSize: "11px" }}> (0.1-5.0)</span>
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          min="0.1"
                          max="5.0"
                          value={newJob.config?.rate_limit?.requests_per_second || 1.0}
                          onChange={(e) => updateJobConfig("rate_limit", { 
                            ...newJob.config?.rate_limit, 
                            requests_per_second: parseFloat(e.target.value) 
                          })}
                          style={{
                            width: "100%",
                            padding: "6px",
                            border: "1px solid #ddd",
                            borderRadius: "4px",
                          }}
                        />
                      </div>
                      <div>
                        <label style={{ display: "block", marginBottom: "5px", fontSize: "13px" }}>
                          Concurrent Workers:
                          <span style={{ color: "#666", fontSize: "11px" }}> (parallel processing)</span>
                        </label>
                        <input
                          type="number"
                          min="1"
                          max="20"
                          value={newJob.config?.max_concurrent_workers || 5}
                          onChange={(e) => updateJobConfig("max_concurrent_workers", parseInt(e.target.value))}
                          style={{
                            width: "100%",
                            padding: "6px",
                            border: "1px solid #ddd",
                            borderRadius: "4px",
                          }}
                        />
                      </div>
                      <div>
                        <label style={{ display: "block", marginBottom: "5px", fontSize: "13px" }}>
                          Delay Variance:
                          <span style={{ color: "#666", fontSize: "11px" }}> (randomness %)</span>
                        </label>
                        <input
                          type="number"
                          step="5"
                          min="0"
                          max="50"
                          value={(newJob.config?.rate_limit?.jitter_factor || 0.1) * 100}
                          onChange={(e) => updateJobConfig("rate_limit", { 
                            ...newJob.config?.rate_limit, 
                            jitter_factor: parseFloat(e.target.value) / 100
                          })}
                          style={{
                            width: "100%",
                            padding: "6px",
                            border: "1px solid #ddd",
                            borderRadius: "4px",
                          }}
                        />
                      </div>
                    </div>
                  </div>
                </>
              )}

              {/* Universal Configuration */}
              <div style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#f8f9fa", borderRadius: "6px", border: "1px solid #dee2e6" }}>
                <h4 style={{ margin: "0 0 10px 0", color: "#495057" }}>⚙️ Universal Settings</h4>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                  <div>
                    <label style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "13px" }}>
                      <input
                        type="checkbox"
                        checked={newJob.config?.enable_js_rendering || false}
                        onChange={(e) => updateJobConfig("enable_js_rendering", e.target.checked)}
                      />
                      Enable JavaScript Rendering
                    </label>
                  </div>
                  <div>
                    <label style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "13px" }}>
                      <input
                        type="checkbox"
                        checked={newJob.config?.enable_ocr || false}
                        onChange={(e) => updateJobConfig("enable_ocr", e.target.checked)}
                      />
                      Enable OCR Processing
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </details>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting || !newJob.name || !newJob.url}
            style={{
              padding: "12px 24px",
              backgroundColor: isSubmitting || !newJob.name || !newJob.url ? "#6c757d" : "#28a745",
              color: "white",
              border: "none",
              borderRadius: "4px",
              fontSize: "16px",
              fontWeight: "bold",
              cursor: isSubmitting || !newJob.name || !newJob.url ? "not-allowed" : "pointer",
              marginTop: "10px",
            }}
          >
            {isSubmitting ? "Creating Collection Job..." : "🚀 Start Collection"}
          </button>
        </form>
      </div>

      {/* Job Queue */}
      <div style={{
        border: "1px solid #dee2e6",
        borderRadius: "8px",
        overflow: "hidden",
      }}>
        <div style={{
          padding: "15px 20px",
          backgroundColor: "#17a2b8",
          color: "white",
          fontSize: "16px",
          fontWeight: "600",
        }}>
          📊 Active Collection Jobs ({jobs.length} jobs)
        </div>
        
        <div style={{ padding: "20px" }}>
          {jobs.length === 0 ? (
            <p style={{ textAlign: "center", color: "#666", margin: "20px 0" }}>
              No collection jobs created yet. Create your first job above!
            </p>
          ) : (
            <div style={{ display: "grid", gap: "15px" }}>
              {jobs.map((job: any) => (
                <div
                  key={job.id}
                  style={{
                    padding: "20px",
                    border: "2px solid #ddd",
                    borderRadius: "8px",
                    backgroundColor: "#ffffff",
                    boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
                  }}
                >
                  {/* Job Header */}
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
                    <div>
                      <h3 style={{ margin: "0 0 5px 0", fontSize: "18px", color: "#333" }}>
                        {job.type === "intelligent_crawling" ? "🔗" : "📄"} {job.name}
                      </h3>
                      <p style={{ margin: "0", fontSize: "13px", color: "#666" }}>
                        {job.type === "intelligent_crawling" ? "Intelligent Crawling" : "Single Page Extract"} • {job.url}
                      </p>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                      <span style={{ 
                        padding: "4px 12px", 
                        backgroundColor: job.status === "completed" ? "#28a745" : job.status === "running" ? "#ffc107" : job.status === "failed" ? "#dc3545" : "#6c757d",
                        color: "white",
                        borderRadius: "16px",
                        fontSize: "12px",
                        fontWeight: "bold"
                      }}>
                        {job.status?.toUpperCase() || "PENDING"}
                      </span>
                    </div>
                  </div>

                  {/* Job Progress & Summary */}
                  {job.status === "running" && (
                    <div style={{ 
                      padding: "12px", 
                      backgroundColor: "#fff3cd", 
                      borderRadius: "6px", 
                      marginBottom: "15px",
                      border: "1px solid #ffeaa7"
                    }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span style={{ fontSize: "13px", color: "#856404" }}>
                          ⏳ Processing... {job.progress || "Starting"}
                        </span>
                        <div style={{ fontSize: "12px", color: "#666" }}>
                          Started: {job.started_at ? new Date(job.started_at).toLocaleString() : "Just now"}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Job Results Summary */}
                  {job.status === "completed" && (
                    <div style={{ 
                      padding: "15px", 
                      backgroundColor: "#d4edda", 
                      borderRadius: "6px", 
                      marginBottom: "15px",
                      border: "1px solid #c3e6cb"
                    }}>
                      <h4 style={{ margin: "0 0 10px 0", color: "#155724", fontSize: "14px" }}>📊 Collection Summary</h4>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: "15px", fontSize: "13px" }}>
                        <div style={{ textAlign: "center" }}>
                          <div style={{ fontSize: "20px", fontWeight: "bold", color: "#155724" }}>
                            {job.summary?.pages_processed || 0}
                          </div>
                          <div style={{ color: "#666" }}>Pages Processed</div>
                        </div>
                        <div style={{ textAlign: "center" }}>
                          <div style={{ fontSize: "20px", fontWeight: "bold", color: "#0056b3" }}>
                            {job.summary?.urls_discovered || 0}
                          </div>
                          <div style={{ color: "#666" }}>URLs Discovered</div>
                        </div>
                        <div style={{ textAlign: "center" }}>
                          <div style={{ fontSize: "20px", fontWeight: "bold", color: "#e83e8c" }}>
                            {job.summary?.urls_queued || 0}
                          </div>
                          <div style={{ color: "#666" }}>URLs Queued</div>
                        </div>
                        <div style={{ textAlign: "center" }}>
                          <div style={{ fontSize: "20px", fontWeight: "bold", color: "#fd7e14" }}>
                            {job.summary?.data_extracted || 0}
                          </div>
                          <div style={{ color: "#666" }}>Data Items</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                    {job.status === "pending" && (
                      <button
                        onClick={() => startJob(job.id)}
                        style={{
                          padding: "8px 16px",
                          backgroundColor: "#28a745",
                          color: "white",
                          border: "none",
                          borderRadius: "4px",
                          cursor: "pointer",
                          fontSize: "13px",
                          fontWeight: "bold",
                        }}
                      >
                        ▶️ Start Collection
                      </button>
                    )}
                    
                    <button
                      onClick={() => getJobDetails(job.id)}
                      style={{
                        padding: "8px 16px",
                        backgroundColor: "#17a2b8",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        cursor: "pointer",
                        fontSize: "13px",
                      }}
                    >
                      📋 View Details
                    </button>

                    {job.status === "completed" && (
                      <button
                        onClick={() => handleGetResults(job.id)}
                        style={{
                          padding: "8px 16px",
                          backgroundColor: showResults[job.id] ? "#6c757d" : "#007bff",
                          color: "white",
                          border: "none",
                          borderRadius: "4px",
                          cursor: "pointer",
                          fontSize: "13px",
                        }}
                      >
                        {showResults[job.id] ? "📤 Hide Data" : "📥 Show Collected Data"}
                      </button>
                    )}
                  </div>

                  {/* Inline Results Display */}
                  {showResults[job.id] && jobResults[job.id] && (
                    <div style={{ 
                      marginTop: "15px", 
                      padding: "15px", 
                      backgroundColor: "#f8f9fa", 
                      borderRadius: "6px",
                      border: "1px solid #dee2e6"
                    }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                        <h4 style={{ margin: 0, color: "#495057" }}>📊 Collected Data</h4>
                        <span style={{ fontSize: "12px", color: "#666" }}>
                          {jobResults[job.id]?.length || 0} items collected
                        </span>
                      </div>
                      
                      <div style={{ maxHeight: "400px", overflowY: "auto" }}>
                        {jobResults[job.id]?.slice(0, 10).map((item: any, index: number) => (
                          <div key={index} style={{ 
                            padding: "10px", 
                            marginBottom: "8px", 
                            backgroundColor: "white", 
                            border: "1px solid #ddd", 
                            borderRadius: "4px",
                            fontSize: "13px"
                          }}>
                            <div style={{ fontWeight: "bold", marginBottom: "5px" }}>
                              {item.title || item.name || `Item ${index + 1}`}
                            </div>
                            {item.url && (
                              <div style={{ color: "#007bff", marginBottom: "3px" }}>
                                🔗 {item.url}
                              </div>
                            )}
                            {item.description && (
                              <div style={{ color: "#666" }}>
                                {item.description.substring(0, 150)}...
                              </div>
                            )}
                          </div>
                        ))}
                        {jobResults[job.id]?.length > 10 && (
                          <div style={{ textAlign: "center", padding: "10px", color: "#666" }}>
                            ... and {jobResults[job.id].length - 10} more items
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OperationsInterface;
