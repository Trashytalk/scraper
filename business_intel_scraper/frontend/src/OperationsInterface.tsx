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
      // Show loading state
      setJobResults({...jobResults, [jobId]: "loading"});
      setShowResults({...showResults, [jobId]: true});
      
      // Get results from parent component function
      const results = await getJobResults(jobId);
      console.log("OperationsInterface received results:", results);
      
      // Update state with results
      setJobResults({...jobResults, [jobId]: results});
    } catch (error) {
      console.error('Failed to fetch results:', error);
      setJobResults({...jobResults, [jobId]: { error: "Failed to load results" }});
    }
  };

  const toggleResults = (jobId: number) => {
    setShowResults({...showResults, [jobId]: !showResults[jobId]});
  };

  const handleJobDetails = async (jobId: number) => {
    try {
      console.log("Fetching details for job:", jobId);
      await getJobDetails(jobId);
      // You could add more functionality here, like showing a modal
      alert(`Details for job ${jobId} have been loaded. Check the console for more information.`);
    } catch (error) {
      console.error('Failed to fetch job details:', error);
      alert("Failed to fetch job details");
    }
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
                      <span title="Maximum number of web pages to crawl starting from the seed URL. Higher values discover more content but take longer to complete.">
                        {activeJobType === "intelligent_crawling" ? "Max Pages to Process: ℹ️" : "Processing Timeout (s): ℹ️"}
                      </span>
                    </label>
                    <input
                      type="number"
                      title={activeJobType === "intelligent_crawling" 
                        ? "Maximum number of pages to crawl (recommended: 10-100 for testing, 500+ for comprehensive crawling)"
                        : "Maximum time in seconds to wait for page loading (recommended: 15-60 seconds)"
                      }
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
                      <label style={{ display: "block", marginBottom: "5px" }}>
                        <span title="How many clicks away from the seed URL to follow links. Depth 1 = direct links only, Depth 3 = links of links of links. Higher values discover more content but may include less relevant pages.">
                          Max Crawl Depth: ℹ️
                        </span>
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="10"
                        title="Maximum depth to crawl (1 = seed page only, 2 = seed + direct links, 3 = recommended for most sites)"
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
                      <label style={{ display: "block", marginBottom: "5px" }}>
                        <span title="Number of times to retry if the page fails to load. Useful for handling temporary network issues or server timeouts.">
                          Retry Attempts: ℹ️
                        </span>
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="5"
                        title="How many times to retry if page loading fails (recommended: 2-3 retries)"
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
                            title="Follow links to pages on the same domain as the seed URL. Recommended for comprehensive site crawling."
                            checked={newJob.config?.follow_internal_links !== false}
                            onChange={(e) => updateJobConfig("follow_internal_links", e.target.checked)}
                          />
                          <span title="Follow links to pages on the same domain as the seed URL. Recommended for comprehensive site crawling.">
                            Follow Internal Links (same domain) ℹ️
                          </span>
                        </label>
                      </div>
                      <div>
                        <label style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "13px" }}>
                          <input
                            type="checkbox"
                            title="Follow links to pages on different domains. Use with caution as this can lead to crawling the entire web!"
                            checked={newJob.config?.follow_external_links || false}
                            onChange={(e) => updateJobConfig("follow_external_links", e.target.checked)}
                          />
                          <span title="Follow links to pages on different domains. Use with caution as this can lead to crawling the entire web!">
                            Follow External Links (other domains) ℹ️
                          </span>
                        </label>
                      </div>
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                      <div>
                        <label style={{ display: "block", marginBottom: "5px", fontSize: "13px" }}>
                          <span title="Regular expression patterns to include specific URLs. Examples: .*product.*|.*article.* (includes URLs with 'product' or 'article'), /blog/.* (includes blog pages), .*\\.pdf$ (includes PDF files)">
                            URL Patterns to Include: ℹ️
                          </span>
                          <span style={{ color: "#666", fontSize: "11px" }}> (regex)</span>
                        </label>
                        <input
                          type="text"
                          placeholder=".*product.*|.*article.*"
                          title="Regular expression to match URLs that should be crawled. Leave empty to include all URLs."
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
                          <span title="Regular expression patterns to exclude specific URLs. Examples: .*admin.*|.*login.* (excludes admin/login pages), .*\\.pdf$|.*\\.jpg$ (excludes PDF/image files), /api/.* (excludes API endpoints)">
                            URL Patterns to Exclude: ℹ️
                          </span>
                          <span style={{ color: "#666", fontSize: "11px" }}> (regex)</span>
                        </label>
                        <input
                          type="text"
                          placeholder=".*admin.*|.*login.*"
                          title="Regular expression to match URLs that should be skipped during crawling."
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
                          <span title="Controls how many web pages to request per second. Lower values (0.1-0.5) are more respectful to servers, higher values (2-5) are faster but may trigger rate limiting.">
                            Pages/Second: ℹ️
                          </span>
                          <span style={{ color: "#666", fontSize: "11px" }}> (0.1-5.0)</span>
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          min="0.1"
                          max="5.0"
                          title="Rate limit for crawling speed. 1.0 = 1 page per second. Lower values are more respectful to target servers."
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
                          <span title="Number of pages that can be processed simultaneously. Higher values speed up crawling but use more resources and may overwhelm target servers.">
                            Concurrent Workers: ℹ️
                          </span>
                          <span style={{ color: "#666", fontSize: "11px" }}> (parallel processing)</span>
                        </label>
                        <input
                          type="number"
                          min="1"
                          max="20"
                          title="How many pages to process in parallel. Higher values = faster crawling but more server load."
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
                          <span title="Adds random variance to request timing to appear more human-like. 20% means requests will vary by ±20% from the base rate.">
                            Delay Variance: ℹ️
                          </span>
                          <span style={{ color: "#666", fontSize: "11px" }}> (randomness %)</span>
                        </label>
                        <input
                          type="number"
                          step="5"
                          min="0"
                          max="50"
                          title="Percentage of randomness in request timing (0-50%). Helps avoid detection as automated crawler."
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
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginBottom: "15px" }}>
                  <div>
                    <label style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "13px" }}>
                      <input
                        type="checkbox"
                        title="Use JavaScript engine to render dynamic content. Slower but captures content loaded by JavaScript frameworks (React, Vue, etc.)."
                        checked={newJob.config?.enable_js_rendering || false}
                        onChange={(e) => updateJobConfig("enable_js_rendering", e.target.checked)}
                      />
                      <span title="Use JavaScript engine to render dynamic content. Slower but captures content loaded by JavaScript frameworks (React, Vue, etc.).">
                        Enable JavaScript Rendering ℹ️
                      </span>
                    </label>
                  </div>
                  <div>
                    <label style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "13px" }}>
                      <input
                        type="checkbox"
                        title="Extract text from images using Optical Character Recognition. Useful for capturing text in screenshots, diagrams, or scanned documents."
                        checked={newJob.config?.enable_ocr || false}
                        onChange={(e) => updateJobConfig("enable_ocr", e.target.checked)}
                      />
                      <span title="Extract text from images using Optical Character Recognition. Useful for capturing text in screenshots, diagrams, or scanned documents.">
                        Enable OCR Processing ℹ️
                      </span>
                    </label>
                  </div>
                </div>

                {/* Enhanced Crawling Options */}
                <div style={{ borderTop: "1px solid #dee2e6", paddingTop: "15px" }}>
                  <h5 style={{ margin: "0 0 10px 0", color: "#495057", fontSize: "14px", fontWeight: "600" }}>🚀 Enhanced Crawling Options</h5>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                    <div>
                      <label style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "13px" }}>
                        <input
                          type="checkbox"
                          title="Extract the complete HTML source code of each page. Useful for preserving original formatting and structure."
                          checked={newJob.config?.extract_full_html || false}
                          onChange={(e) => updateJobConfig("extract_full_html", e.target.checked)}
                        />
                        <span title="Extract the complete HTML source code of each page. Useful for preserving original formatting and structure.">
                          Extract Full HTML ℹ️
                        </span>
                      </label>
                    </div>
                    <div>
                      <label style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "13px" }}>
                        <input
                          type="checkbox"
                          title="Automatically crawl all pages within the same domain. When enabled, the crawler will discover and process all reachable pages on the website."
                          checked={newJob.config?.crawl_entire_domain || false}
                          onChange={(e) => updateJobConfig("crawl_entire_domain", e.target.checked)}
                        />
                        <span title="Automatically crawl all pages within the same domain. When enabled, the crawler will discover and process all reachable pages on the website.">
                          Crawl Entire Domain ℹ️
                        </span>
                      </label>
                    </div>
                    <div>
                      <label style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "13px" }}>
                        <input
                          type="checkbox"
                          title="Download and include image files found on pages. Useful for visual content analysis and archival purposes."
                          checked={newJob.config?.include_images || false}
                          onChange={(e) => updateJobConfig("include_images", e.target.checked)}
                        />
                        <span title="Download and include image files found on pages. Useful for visual content analysis and archival purposes.">
                          Include Images ℹ️
                        </span>
                      </label>
                    </div>
                    <div>
                      <label style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "13px" }}>
                        <input
                          type="checkbox"
                          title="Save extracted data to the database for persistence and later analysis. Recommended for most use cases."
                          checked={newJob.config?.save_to_database !== false}
                          onChange={(e) => updateJobConfig("save_to_database", e.target.checked)}
                        />
                        <span title="Save extracted data to the database for persistence and later analysis. Recommended for most use cases.">
                          Save to Database ℹ️
                        </span>
                      </label>
                    </div>
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
            {isSubmitting ? "Creating Job..." : "🚀 Create Job"}
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
                        ▶️ Create Job
                      </button>
                    )}
                    
                    <button
                      onClick={() => handleJobDetails(job.id)}
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
                        onClick={() => {
                          if (showResults[job.id]) {
                            toggleResults(job.id);
                          } else {
                            handleGetResults(job.id);
                          }
                        }}
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
                  {showResults[job.id] && (
                    <div style={{ 
                      marginTop: "15px", 
                      padding: "15px", 
                      backgroundColor: "#f8f9fa", 
                      borderRadius: "6px",
                      border: "1px solid #dee2e6"
                    }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                        <h4 style={{ margin: 0, color: "#495057" }}>📊 Collected Data</h4>
                        {jobResults[job.id] === "loading" ? (
                          <span style={{ fontSize: "12px", color: "#666" }}>Loading...</span>
                        ) : jobResults[job.id]?.error ? (
                          <span style={{ fontSize: "12px", color: "#dc3545" }}>Error loading data</span>
                        ) : (
                          <span style={{ fontSize: "12px", color: "#666" }}>
                            {Array.isArray(jobResults[job.id]) ? jobResults[job.id].length : 
                             jobResults[job.id]?.crawled_data ? jobResults[job.id].crawled_data.length :
                             "1"} items collected
                          </span>
                        )}
                      </div>
                      
                      {jobResults[job.id] === "loading" ? (
                        <div style={{ textAlign: "center", padding: "20px", color: "#666" }}>
                          ⏳ Loading results...
                        </div>
                      ) : jobResults[job.id]?.error ? (
                        <div style={{ textAlign: "center", padding: "20px", color: "#dc3545" }}>
                          ❌ {jobResults[job.id].error}
                        </div>
                      ) : jobResults[job.id] ? (
                        <div style={{ maxHeight: "400px", overflowY: "auto" }}>
                          {/* Handle intelligent crawling results */}
                          {jobResults[job.id].crawled_data ? (
                            <>
                              {/* Summary Information */}
                              {jobResults[job.id].summary && (
                                <div style={{ 
                                  padding: "10px", 
                                  marginBottom: "10px", 
                                  backgroundColor: "#e8f5e8", 
                                  border: "1px solid #c3e6c3", 
                                  borderRadius: "4px",
                                  fontSize: "13px"
                                }}>
                                  <strong>Crawling Summary:</strong> {jobResults[job.id].summary.pages_processed} pages processed, 
                                  {jobResults[job.id].summary.urls_discovered} URLs discovered, 
                                  {jobResults[job.id].summary.data_extracted} items extracted
                                </div>
                              )}
                              
                              {/* Crawled Data */}
                              {jobResults[job.id].crawled_data.slice(0, 10).map((item: any, index: number) => (
                                <div key={index} style={{ 
                                  padding: "10px", 
                                  marginBottom: "8px", 
                                  backgroundColor: "white", 
                                  border: "1px solid #ddd", 
                                  borderRadius: "4px",
                                  fontSize: "13px"
                                }}>
                                  <div style={{ fontWeight: "bold", marginBottom: "5px" }}>
                                    {item.title || item.name || `Page ${index + 1}`}
                                  </div>
                                  {item.url && (
                                    <div style={{ color: "#007bff", marginBottom: "3px" }}>
                                      🔗 {item.url}
                                    </div>
                                  )}
                                  {item.text_content && (
                                    <div style={{ color: "#666" }}>
                                      {item.text_content.substring(0, 150)}...
                                    </div>
                                  )}
                                  {item.meta_description && (
                                    <div style={{ color: "#666" }}>
                                      {item.meta_description.substring(0, 150)}...
                                    </div>
                                  )}
                                </div>
                              ))}
                              
                              {jobResults[job.id].crawled_data.length > 10 && (
                                <div style={{ textAlign: "center", padding: "10px", color: "#666" }}>
                                  ... and {jobResults[job.id].crawled_data.length - 10} more items
                                </div>
                              )}
                            </>
                          ) : Array.isArray(jobResults[job.id]) ? (
                            /* Handle array results (legacy format) */
                            <>
                              {jobResults[job.id].slice(0, 10).map((item: any, index: number) => (
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
                                  {(item.description || item.text_content || item.content) && (
                                    <div style={{ color: "#666" }}>
                                      {(item.description || item.text_content || item.content).substring(0, 150)}...
                                    </div>
                                  )}
                                </div>
                              ))}
                              {jobResults[job.id].length > 10 && (
                                <div style={{ textAlign: "center", padding: "10px", color: "#666" }}>
                                  ... and {jobResults[job.id].length - 10} more items
                                </div>
                              )}
                            </>
                          ) : (
                            /* Handle single result object */
                            <div style={{ 
                              padding: "10px", 
                              backgroundColor: "white", 
                              border: "1px solid #ddd", 
                              borderRadius: "4px",
                              fontSize: "13px"
                            }}>
                              <div style={{ fontWeight: "bold", marginBottom: "5px" }}>
                                {jobResults[job.id].title || "Single Page Result"}
                              </div>
                              {jobResults[job.id].url && (
                                <div style={{ color: "#007bff", marginBottom: "3px" }}>
                                  🔗 {jobResults[job.id].url}
                                </div>
                              )}
                              {jobResults[job.id].text_content && (
                                <div style={{ color: "#666" }}>
                                  {jobResults[job.id].text_content.substring(0, 300)}...
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      ) : (
                        <div style={{ textAlign: "center", padding: "20px", color: "#666" }}>
                          No data available
                        </div>
                      )}
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
