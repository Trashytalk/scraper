import React, { useState, useEffect } from "react";
import PageViewerModal from "./components/PageViewerModal";
import AdminDashboard from "./components/AdminDashboard";

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

interface JobProgress {
  job_id: number;
  status: string;
  progress_percentage: number;
  current_results: number;
  estimated_target: number;
  runtime_seconds: number;
  eta_seconds?: number;
  recent_activity: Array<{
    url: string;
    timestamp: string;
  }>;
  last_updated: string;
}

interface NewJob {
  name: string;
  url: string;
  type: "intelligent" | "custom" | "basic" | "e_commerce" | "news" | "social_media" | "api";  // For backend compatibility
  scraper_type: "intelligent" | "custom";
  config?: {
    batch_mode?: boolean;
    batch_size?: number;
    // Basic settings
    extract_full_html?: boolean;
    save_to_database?: boolean;
    // Crawling protocols
    crawl_links?: boolean;
    follow_internal_links?: boolean;
    follow_external_links?: boolean;
    crawl_entire_domain?: boolean;
    // Data extraction
    include_images?: boolean;
    include_forms?: boolean;
    include_scripts?: boolean;
    extract_metadata?: boolean;
    // System parameters
    max_depth?: number;
    max_pages?: number;
    delay_between_requests?: number;
    user_agent?: string;
    // Advanced options
    respect_robots_txt?: boolean;
    handle_javascript?: boolean;
    extract_emails?: boolean;
    extract_phone_numbers?: boolean;
  };
}

interface CrawlerJob {
  id: number;
  name: string;
  created_at: string;
}

interface Analytics {
  total_jobs: number;
  completed_jobs: number;
  running_jobs: number;
  failed_jobs: number;
}

const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState("operations");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [jobResults, setJobResults] = useState<JobResults | null>(null);
  const [jobDetails, setJobDetails] = useState<Job | null>(null);
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [crawlerJobs, setCrawlerJobs] = useState<CrawlerJob[]>([]);
  const [selectedCrawlerJob, setSelectedCrawlerJob] = useState<number | null>(null);
  const [extractedUrls, setExtractedUrls] = useState<string[]>([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [loginError, setLoginError] = useState('');
  const [token, setToken] = useState("");
  const [showPageViewer, setShowPageViewer] = useState(false);
  const [pageViewerJobId, setPageViewerJobId] = useState<number | null>(null);
  const [pageViewerUrl, setPageViewerUrl] = useState<string | undefined>(undefined);
  
  // Admin dashboard state
  const [showAdminDashboard, setShowAdminDashboard] = useState(false);
  
  // Progress tracking state
  const [jobProgress, setJobProgress] = useState<{[key: number]: JobProgress}>({});
  const [progressIntervals, setProgressIntervals] = useState<{[key: number]: NodeJS.Timeout}>({});
  const [newJob, setNewJob] = useState<NewJob>({
    name: "",
    url: "",
    type: "intelligent",  // Changed from scraper_type to type for backend compatibility
    scraper_type: "intelligent",
    config: { 
      batch_mode: false, 
      batch_size: 10,
      // Basic settings
      extract_full_html: true,   // Always extract full HTML
      save_to_database: true,   // Always save to database
      // Crawling protocols
      crawl_links: true,
      follow_internal_links: true,
      follow_external_links: false,
      crawl_entire_domain: false,
      // Data extraction
      include_images: true,      // Always include images
      include_forms: true,       // Always include forms
      include_scripts: false,
      extract_metadata: false,
      // System parameters
      max_depth: 3,
      max_pages: 100,
      delay_between_requests: 1000,
      user_agent: "Mozilla/5.0 (compatible; TacticalScraper/1.0)",
      // Advanced options
      respect_robots_txt: true,
      handle_javascript: false,
      extract_emails: false,
      extract_phone_numbers: false
    }
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Test backend connection on mount
  useEffect(() => {
    fetch("http://localhost:8000/api/health")
      .then(() => setIsBackendConnected(true))
      .catch(() => setIsBackendConnected(false));
  }, []);

  // Monitor job status changes to start/stop progress tracking
  useEffect(() => {
    console.log('🔄 Jobs effect triggered, current jobs:', jobs.map(j => ({ id: j.id, status: j.status })));
    jobs.forEach(job => {
      if (job.status === "running" && !progressIntervals[job.id]) {
        console.log(`🚀 Job ${job.id} is running, starting progress tracking`);
        startProgressTracking(job.id);
      } else if (job.status !== "running" && progressIntervals[job.id]) {
        console.log(`⏹️ Job ${job.id} is no longer running, stopping progress tracking`);
        stopProgressTracking(job.id);
      }
    });

    // Cleanup intervals for deleted jobs
    Object.keys(progressIntervals).forEach(jobIdStr => {
      const jobId = parseInt(jobIdStr);
      if (!jobs.find(job => job.id === jobId)) {
        console.log(`🧹 Cleaning up progress tracking for deleted job ${jobId}`);
        stopProgressTracking(jobId);
      }
    });

    // Cleanup on unmount
    return () => {
      Object.values(progressIntervals).forEach(interval => {
        clearInterval(interval);
      });
    };
  }, [jobs]);

  // Helper function for authenticated API calls
  const authenticatedFetch = async (url: string, options: RequestInit = {}) => {
    // Prefer state token; fall back to localStorage for early calls before state is hydrated
    const effectiveToken = token || localStorage.getItem('token') || '';
    
    const headers = {
      'Content-Type': 'application/json',
      ...(effectiveToken && { 'Authorization': `Bearer ${effectiveToken}` }),
      ...options.headers,
    };
    
    // If URL starts with /api, make it a full URL to the backend server
    const fullUrl = url.startsWith('/api') ? `http://localhost:8000${url}` : url;
    
    const response = await fetch(fullUrl, {
      ...options,
      headers,
    });
    
    // Handle 401 errors by automatically logging out
    if (response.status === 401) {
      console.log('🔒 Token expired or invalid, logging out');
      handleLogout();
    }
    
    return response;
  };

  // Fetch data when authentication state changes
  useEffect(() => {
    if (isAuthenticated && token) {
      // Fetch jobs with authentication
      authenticatedFetch("/api/jobs")
        .then(res => res.json())
        .then(data => {
          // Backend returns jobs array directly, not wrapped in {jobs: [...]}
          const jobsArray = Array.isArray(data) ? data : (data.jobs || []);
          setJobs(jobsArray);
          console.log("✅ Jobs loaded on auth:", jobsArray.length, "jobs");
        })
        .catch(console.error);

      // Fetch analytics with authentication - use the correct endpoint
      authenticatedFetch("/api/analytics/dashboard")
        .then(res => {
          if (res.ok) {
            return res.json();
          } else {
            throw new Error(`Analytics API returned ${res.status}`);
          }
        })
        .then(data => setAnalytics(data))
        .catch(error => {
          console.warn("Analytics not available:", error);
          // Set default analytics if endpoint fails
          setAnalytics({
            total_jobs: jobs.length,
            completed_jobs: 0,
            running_jobs: 0,
            failed_jobs: 0
          });
        });
    }
  }, [isAuthenticated, token]);

  // Authentication functions
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError('');
    
    console.log('🔐 Attempting login with:', { username: loginForm.username, password: '***' });
    
    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginForm),
      });
      
      console.log('📡 Login response status:', response.status);
      console.log('📡 Login response headers:', Object.fromEntries(response.headers.entries()));
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Login successful');
        setToken(data.access_token);
        setIsAuthenticated(true);
        localStorage.setItem('token', data.access_token);
        console.log('✅ Authentication complete');
      } else {
        const errorData = await response.json();
        console.error('❌ Login failed:', errorData);
        setLoginError(errorData.detail || 'Login failed');
      }
    } catch (error) {
      console.error('❌ Network error during login:', error);
      setLoginError('Network error - please try again');
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setToken("");
    setJobs([]);
    setAnalytics(null);
    setJobResults(null);
    setJobDetails(null);
    localStorage.removeItem('token');
    setLoginForm({ username: '', password: '' });
  };

  // Check for stored token on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      setIsAuthenticated(true);
    }
  }, []);

  const getJobResults = async (jobId: number) => {
    try {
      console.log("🔍 Fetching results for job ID:", jobId);
      const response = await authenticatedFetch(`/api/jobs/${jobId}/results`);
      const data = await response.json();
      console.log("✅ Raw job results received:", data);
      
      // Find the job to get its name
      const job = jobs.find(j => j.id === jobId);
      const jobName = job ? job.name : `Job ${jobId}`;
      
      // Extract crawled data from the API response structure
      let crawledData = [];
      if (Array.isArray(data) && data.length > 0) {
        // The API returns an array with job info, extract crawled_data
        crawledData = data[0]?.crawled_data || [];
      }
      
      console.log("🔍 Extracted crawled data:", crawledData);
      
      // Format the results to match the expected interface
      const formattedResults: JobResults = {
        job_name: jobName,
        data: crawledData
      };
      
      console.log("✅ Formatted job results for modal:", formattedResults);
      setJobResults(formattedResults);
      
      // Scroll to top when modal opens
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
      console.error("❌ Failed to fetch job results:", error);
    }
  };

  const startJob = async (jobId: number) => {
    try {
      const response = await authenticatedFetch(`/api/jobs/${jobId}/start`, {
        method: "POST",
      });
      if (response.ok) {
        // Refresh jobs list with authentication
        const jobsResponse = await authenticatedFetch("/api/jobs");
        if (jobsResponse.ok) {
          const jobsData = await jobsResponse.json();
          const jobsArray = Array.isArray(jobsData) ? jobsData : (jobsData.jobs || []);
          setJobs(jobsArray);
          console.log(`✅ Job ${jobId} started successfully`);
        }
      } else {
        const errorData = await response.json();
        console.error(`❌ Failed to start job ${jobId}:`, errorData);
      }
    } catch (error) {
      console.error("Failed to start job:", error);
    }
  };

  const getJobDetails = async (jobId: number) => {
    try {
      console.log("🔍 Fetching details for job ID:", jobId);
      const response = await authenticatedFetch(`/api/jobs/${jobId}`);
      if (response.ok) {
        const data = await response.json();
        console.log("✅ Job details:", data);
        setJobDetails(data);
        // Scroll to top when modal opens
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        const errorData = await response.json();
        console.error(`❌ Failed to fetch job ${jobId} details:`, errorData);
      }
    } catch (error) {
      console.error("❌ Failed to fetch job details:", error);
    }
  };

  const deleteJob = async (jobId: number) => {
    try {
      console.log("🗑️ Deleting job ID:", jobId);
      const response = await authenticatedFetch(`/api/jobs/${jobId}`, {
        method: "DELETE",
      });
      if (response.ok) {
        console.log(`✅ Job ${jobId} deleted successfully`);
        // Refresh jobs list
        const jobsResponse = await authenticatedFetch("/api/jobs");
        if (jobsResponse.ok) {
          const jobsData = await jobsResponse.json();
          const jobsArray = Array.isArray(jobsData) ? jobsData : (jobsData.jobs || []);
          setJobs(jobsArray);
        }
      } else {
        const errorData = await response.json();
        console.error(`❌ Failed to delete job ${jobId}:`, errorData);
        alert(`Failed to delete job: ${errorData.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error("❌ Failed to delete job:", error);
      alert("Failed to delete job. Please try again.");
    }
  };

  // Progress tracking functions
  const fetchJobProgress = async (jobId: number) => {
    try {
      console.log(`🔄 Fetching progress for job ${jobId}`);
      const response = await authenticatedFetch(`/api/jobs/${jobId}/progress`);
      if (response.ok) {
        const progress = await response.json();
        console.log(`📊 Progress for job ${jobId}:`, progress);
        setJobProgress(prev => ({
          ...prev,
          [jobId]: progress
        }));
      } else {
        console.error(`❌ Progress API error for job ${jobId}:`, response.status, response.statusText);
      }
    } catch (error) {
      console.error('❌ Failed to fetch progress for job', jobId, error);
    }
  };

  const startProgressTracking = (jobId: number) => {
    console.log(`▶️ Starting progress tracking for job ${jobId}`);
    // Clear existing interval if any
    if (progressIntervals[jobId]) {
      clearInterval(progressIntervals[jobId]);
    }

    // Start tracking progress every 3 seconds
    const interval = setInterval(() => {
      fetchJobProgress(jobId);
    }, 3000);

    setProgressIntervals(prev => ({
      ...prev,
      [jobId]: interval
    }));

    // Fetch immediately
    fetchJobProgress(jobId);
  };

  const stopProgressTracking = (jobId: number) => {
    if (progressIntervals[jobId]) {
      clearInterval(progressIntervals[jobId]);
      setProgressIntervals(prev => {
        const updated = { ...prev };
        delete updated[jobId];
        return updated;
      });
    }
  };

  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ${seconds % 60}s`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ${minutes % 60}m`;
  };

  const formatETA = (seconds?: number): string => {
    if (!seconds || seconds <= 0) return "Calculating...";
    return `~${formatTime(seconds)} remaining`;
  };

  const fetchCrawlerJobs = async () => {
    try {
      const response = await authenticatedFetch("/api/crawler-jobs");
      if (response.ok) {
        const data = await response.json();
        setCrawlerJobs(data.jobs || []);
      } else {
        console.error("❌ Failed to fetch crawler jobs:", response.status);
      }
    } catch (error) {
      console.error("Failed to fetch crawler jobs:", error);
    }
  };

  const extractUrlsFromCrawler = async (crawlerJobId: number) => {
    try {
      const response = await authenticatedFetch(`/api/crawler-jobs/${crawlerJobId}/urls`);
      if (response.ok) {
        const data = await response.json();
        setExtractedUrls(data.urls || []);
        return data.urls || [];
      } else {
        console.error("❌ Failed to extract URLs from crawler job:", response.status);
        return [];
      }
    } catch (error) {
      console.error("Failed to extract URLs from crawler job:", error);
      return [];
    }
  };

  const createBatchScrapingJobs = async (urls: string[], batchSize: number) => {
    setIsSubmitting(true);
    try {
      const batches = [];
      for (let i = 0; i < urls.length; i += batchSize) {
        batches.push(urls.slice(i, i + batchSize));
      }

      for (let i = 0; i < batches.length; i++) {
        const batchJob = {
          name: `${newJob.name} - Batch ${i + 1}`,
          urls: batches[i],
          scraper_type: newJob.scraper_type,
          config: { batch_mode: true }
        };

        const response = await authenticatedFetch("/api/jobs/batch", {
          method: "POST",
          body: JSON.stringify(batchJob),
        });

        if (response.ok) {
          const createdJob = await response.json();
          setJobs(prev => [createdJob, ...prev]);
        } else {
          const errorData = await response.json();
          console.error(`❌ Failed to create batch job ${i + 1}:`, errorData);
        }
      }

      setNewJob({ 
        name: "", 
        url: "", 
        scraper_type: "intelligent",
        config: { batch_mode: false, batch_size: 10 }
      });
      setExtractedUrls([]);
      setSelectedCrawlerJob(null);
      
      console.log(`Created ${batches.length} batch jobs`);
    } catch (error) {
      console.error("Error creating batch jobs:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const submitJob = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      const response = await authenticatedFetch("/api/jobs", {
        method: "POST",
        body: JSON.stringify(newJob),
      });
      
      if (response.ok) {
        const createdJob = await response.json();
        console.log("Job created successfully:", createdJob);
        
        // Refresh the jobs list from server to get complete data
        try {
          const jobsResponse = await authenticatedFetch("/api/jobs");
          if (jobsResponse.ok) {
            const jobsData = await jobsResponse.json();
            // Backend returns jobs array directly, not wrapped in {jobs: [...]}
            const jobsArray = Array.isArray(jobsData) ? jobsData : (jobsData.jobs || []);
            setJobs(jobsArray);
            console.log("Jobs list refreshed:", jobsArray.length, "jobs");
          }
        } catch (error) {
          console.error("Failed to refresh jobs list:", error);
          // Fallback: try to add the created job to local state
          if (createdJob.id) {
            setJobs(prev => [createdJob, ...prev]);
          }
        }
        
        setNewJob({ 
          name: "", 
          url: "", 
          type: "intelligent",
          scraper_type: "intelligent",
          config: { 
            batch_mode: false, 
            batch_size: 10,
            // Basic settings
            extract_full_html: true,   // Always extract full HTML
            save_to_database: true,    // Always save to database
            // Crawling protocols
            crawl_links: true,
            follow_internal_links: true,
            follow_external_links: false,
            crawl_entire_domain: false,
            // Data extraction
            include_images: true,      // Always include images
            include_forms: true,       // Always include forms
            include_scripts: false,
            extract_metadata: false,
            // System parameters
            max_depth: 3,
            max_pages: 100,
            delay_between_requests: 1000,
            user_agent: "Mozilla/5.0 (compatible; TacticalScraper/1.0)",
            // Advanced options
            respect_robots_txt: true,
            handle_javascript: false,
            extract_emails: false,
            extract_phone_numbers: false
          }
        });
      } else {
        const errorData = await response.json();
        console.error("Failed to create job:", errorData);
      }
    } catch (error) {
      console.error("Error creating job:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Login interface for unauthenticated users
  if (!isAuthenticated) {
    return (
      <div style={{
        minHeight: "100vh",
        background: "var(--bg-primary)",
        color: "var(--text-primary)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "'Rajdhani', sans-serif"
      }}>
        <div className="cyber-glass" style={{
          padding: "40px",
          maxWidth: "400px",
          width: "90%",
          textAlign: "center",
          border: "1px solid var(--metal-silver)",
          borderRadius: "12px",
          background: "rgba(25, 25, 25, 0.95)"
        }}>
          <h1 style={{
            marginBottom: "30px",
            fontSize: "28px",
            color: "var(--metal-gold)",
            fontFamily: "'Orbitron', monospace",
            textShadow: "0 0 10px rgba(212, 175, 55, 0.3)"
          }}>
            🔐 TACTICAL ACCESS
          </h1>
          
          <form onSubmit={handleLogin} style={{ marginBottom: "20px" }}>
            <div style={{ marginBottom: "20px" }}>
              <input
                type="text"
                placeholder="Username"
                value={loginForm.username}
                onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                required
                style={{
                  width: "100%",
                  padding: "12px",
                  background: "var(--bg-tertiary)",
                  border: "1px solid var(--border-primary)",
                  borderRadius: "6px",
                  color: "var(--text-primary)",
                  fontFamily: "'Rajdhani', sans-serif",
                  fontSize: "16px"
                }}
              />
            </div>
            
            <div style={{ marginBottom: "25px" }}>
              <input
                type="password"
                placeholder="Password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                required
                style={{
                  width: "100%",
                  padding: "12px",
                  background: "var(--bg-tertiary)",
                  border: "1px solid var(--border-primary)",
                  borderRadius: "6px",
                  color: "var(--text-primary)",
                  fontFamily: "'Rajdhani', sans-serif",
                  fontSize: "16px"
                }}
              />
            </div>
            
            {loginError && (
              <div style={{
                marginBottom: "20px",
                padding: "12px",
                background: "rgba(239, 68, 68, 0.1)",
                border: "1px solid var(--accent-red)",
                borderRadius: "6px",
                color: "var(--accent-red)",
                fontSize: "14px"
              }}>
                {loginError}
              </div>
            )}
            
            <button
              type="submit"
              style={{
                width: "100%",
                padding: "14px",
                background: "linear-gradient(45deg, var(--metal-gold), var(--metal-copper))",
                border: "none",
                borderRadius: "6px",
                color: "var(--bg-primary)",
                fontFamily: "'Orbitron', monospace",
                fontSize: "16px",
                fontWeight: "600",
                cursor: "pointer",
                textTransform: "uppercase",
                letterSpacing: "1px"
              }}
            >
              🚀 Initiate Connection
            </button>
          </form>
          
          <div style={{
            fontSize: "12px",
            color: "var(--text-secondary)",
            fontStyle: "italic"
          }}>
            Default credentials: admin / admin123
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="cyber-glass" style={{ 
      padding: "20px", 
      minHeight: "100vh",
      fontFamily: "'Rajdhani', sans-serif",
      background: "var(--bg-primary)",
      color: "var(--text-primary)"
    }}>
      <header style={{ 
        marginBottom: "30px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "20px",
        background: "var(--bg-secondary)",
        borderRadius: "8px",
        border: "1px solid var(--border-primary)"
      }}>
        <div>
          <h1 style={{
            margin: "0",
            fontSize: "28px",
            background: "linear-gradient(45deg, var(--metal-silver), var(--metal-chrome))",
            backgroundClip: "text",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent"
          }}>
            🔬 TACTICAL INTELLIGENCE SCRAPER
          </h1>
          <div style={{
            marginTop: "10px",
            padding: "5px 10px",
            borderRadius: "4px",
            fontSize: "14px",
            background: isBackendConnected ? "var(--metal-gold)" : "var(--metal-copper)",
            color: "var(--bg-primary)"
          }}>
            SYSTEM: {isBackendConnected ? "ONLINE" : "OFFLINE"}
          </div>
        </div>
        <button
          onClick={() => setShowAdminDashboard(true)}
          style={{
            background: "linear-gradient(45deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.1))",
            border: "1px solid var(--metal-silver)",
            color: "var(--metal-silver)",
            padding: "12px 20px",
            borderRadius: "6px",
            cursor: "pointer",
            fontFamily: "'Rajdhani', sans-serif",
            fontWeight: "600",
            fontSize: "14px",
            transition: "all 0.3s ease",
            marginRight: "10px"
          }}
        >
          🛠️ ADMIN
        </button>
        <button
          onClick={handleLogout}
          style={{
            background: "linear-gradient(45deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.1))",
            border: "1px solid var(--metal-copper)",
            color: "var(--metal-copper)",
            padding: "12px 20px",
            borderRadius: "6px",
            cursor: "pointer",
            fontFamily: "'Rajdhani', sans-serif",
            fontWeight: "600",
            fontSize: "14px",
            transition: "all 0.3s ease"
          }}
        >
          🚫 TERMINATE SESSION
        </button>
      </header>

      {/* Navigation */}
      <nav style={{ 
        marginBottom: "30px",
        display: "flex",
        gap: "8px",
        padding: "8px",
        background: "var(--bg-secondary)",
        borderRadius: "8px",
        border: "1px solid var(--border-primary)",
        flexWrap: "wrap"
      }}>
        <button 
          onClick={() => setCurrentTab("operations")}
          style={{ 
            padding: "10px 16px",
            background: currentTab === "operations" ? "var(--metal-gold)" : "var(--bg-tertiary)",
            color: currentTab === "operations" ? "var(--bg-primary)" : "var(--text-primary)",
            border: `1px solid ${currentTab === "operations" ? "var(--metal-gold)" : "var(--border-primary)"}`,
            borderRadius: "6px",
            cursor: "pointer",
            fontFamily: "'Rajdhani', sans-serif",
            fontWeight: "600",
            fontSize: "14px",
            transition: "all 0.3s ease"
          }}
        >
          ⚙️ Operations
        </button>
        <button 
          onClick={() => setCurrentTab("dashboard")}
          style={{ 
            padding: "10px 16px",
            background: currentTab === "dashboard" ? "var(--metal-gold)" : "var(--bg-tertiary)",
            color: currentTab === "dashboard" ? "var(--bg-primary)" : "var(--text-primary)",
            border: `1px solid ${currentTab === "dashboard" ? "var(--metal-gold)" : "var(--border-primary)"}`,
            borderRadius: "6px",
            cursor: "pointer",
            fontFamily: "'Rajdhani', sans-serif",
            fontWeight: "600",
            fontSize: "14px",
            transition: "all 0.3s ease"
          }}
        >
          📊 Dashboard
        </button>
        <button 
          onClick={() => setCurrentTab("analytics")}
          style={{ 
            padding: "10px 16px",
            background: currentTab === "analytics" ? "var(--metal-gold)" : "var(--bg-tertiary)",
            color: currentTab === "analytics" ? "var(--bg-primary)" : "var(--text-primary)",
            border: `1px solid ${currentTab === "analytics" ? "var(--metal-gold)" : "var(--border-primary)"}`,
            borderRadius: "6px",
            cursor: "pointer",
            fontFamily: "'Rajdhani', sans-serif",
            fontWeight: "600",
            fontSize: "14px",
            transition: "all 0.3s ease"
          }}
        >
          📈 Analytics
        </button>
        <button 
          onClick={() => setCurrentTab("network")}
          style={{ 
            padding: "10px 16px",
            background: currentTab === "network" ? "var(--metal-gold)" : "var(--bg-tertiary)",
            color: currentTab === "network" ? "var(--bg-primary)" : "var(--text-primary)",
            border: `1px solid ${currentTab === "network" ? "var(--metal-gold)" : "var(--border-primary)"}`,
            borderRadius: "6px",
            cursor: "pointer",
            fontFamily: "'Rajdhani', sans-serif",
            fontWeight: "600",
            fontSize: "14px",
            transition: "all 0.3s ease"
          }}
        >
          🔗 Network
        </button>
        <button 
          onClick={() => setCurrentTab("osint")}
          style={{ 
            padding: "10px 16px",
            background: currentTab === "osint" ? "var(--metal-gold)" : "var(--bg-tertiary)",
            color: currentTab === "osint" ? "var(--bg-primary)" : "var(--text-primary)",
            border: `1px solid ${currentTab === "osint" ? "var(--metal-gold)" : "var(--border-primary)"}`,
            borderRadius: "6px",
            cursor: "pointer",
            fontFamily: "'Rajdhani', sans-serif",
            fontWeight: "600",
            fontSize: "14px",
            transition: "all 0.3s ease"
          }}
        >
          🎯 OSINT
        </button>
        <button 
          onClick={() => setCurrentTab("data-enrichment")}
          style={{ 
            padding: "10px 16px",
            background: currentTab === "data-enrichment" ? "var(--metal-gold)" : "var(--bg-tertiary)",
            color: currentTab === "data-enrichment" ? "var(--bg-primary)" : "var(--text-primary)",
            border: `1px solid ${currentTab === "data-enrichment" ? "var(--metal-gold)" : "var(--border-primary)"}`,
            borderRadius: "6px",
            cursor: "pointer",
            fontFamily: "'Rajdhani', sans-serif",
            fontWeight: "600",
            fontSize: "14px",
            transition: "all 0.3s ease"
          }}
        >
          💎 Enrichment
        </button>
        <button 
          onClick={() => setCurrentTab("performance")}
          style={{ 
            padding: "10px 16px",
            background: currentTab === "performance" ? "var(--metal-gold)" : "var(--bg-tertiary)",
            color: currentTab === "performance" ? "var(--bg-primary)" : "var(--text-primary)",
            border: `1px solid ${currentTab === "performance" ? "var(--metal-gold)" : "var(--border-primary)"}`,
            borderRadius: "6px",
            cursor: "pointer",
            fontFamily: "'Rajdhani', sans-serif",
            fontWeight: "600",
            fontSize: "14px",
            transition: "all 0.3s ease"
          }}
        >
          ⚡ Performance
        </button>
        <button 
          onClick={() => setCurrentTab("ai-analytics")}
          style={{ 
            padding: "10px 16px",
            background: currentTab === "ai-analytics" ? "var(--metal-gold)" : "var(--bg-tertiary)",
            color: currentTab === "ai-analytics" ? "var(--bg-primary)" : "var(--text-primary)",
            border: `1px solid ${currentTab === "ai-analytics" ? "var(--metal-gold)" : "var(--border-primary)"}`,
            borderRadius: "6px",
            cursor: "pointer",
            fontFamily: "'Rajdhani', sans-serif",
            fontWeight: "600",
            fontSize: "14px",
            transition: "all 0.3s ease"
          }}
        >
          🤖 AI Core
        </button>
      </nav>

      {/* Operations Tab */}
      {currentTab === "operations" && (
        <div>
          <div style={{
            background: "var(--bg-secondary)",
            padding: "25px",
            borderRadius: "8px",
            border: "1px solid var(--border-primary)",
            marginBottom: "30px"
          }}>
            <h2 style={{ 
              margin: "0 0 20px 0",
              color: "var(--metal-silver)",
              fontSize: "20px"
            }}>
              ⚙️ OPERATION CONTROL - TARGET CONFIGURATION
            </h2>

            {/* Job Mode Selection */}
            <div style={{ marginBottom: "25px" }}>
              <div style={{ display: "flex", gap: "20px", marginBottom: "20px" }}>
                <label style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  cursor: "pointer",
                  padding: "12px",
                  background: !newJob.config?.batch_mode ? "rgba(0, 255, 255, 0.1)" : "transparent",
                  border: `1px solid ${!newJob.config?.batch_mode ? "var(--metal-silver)" : "var(--border-primary)"}`,
                  borderRadius: "8px",
                  transition: "all 0.3s ease"
                }}>
                  <input
                    type="radio"
                    name="jobMode"
                    checked={!newJob.config?.batch_mode}
                    onChange={() => {
                      setNewJob((prev) => ({
                        ...prev,
                        config: { ...prev.config, batch_mode: false },
                      }));
                      setSelectedCrawlerJob(null);
                      setExtractedUrls([]);
                    }}
                    style={{ accentColor: "var(--metal-silver)" }}
                  />
                  <span style={{ fontWeight: "600", color: "var(--metal-silver)" }}>
                    🎯 SINGLE TARGET ACQUISITION
                  </span>
                </label>
                <label style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  cursor: "pointer",
                  padding: "12px",
                  background: !!newJob.config?.batch_mode ? "rgba(255, 140, 0, 0.1)" : "transparent",
                  border: `1px solid ${!!newJob.config?.batch_mode ? "var(--metal-copper)" : "var(--border-primary)"}`,
                  borderRadius: "8px",
                  transition: "all 0.3s ease"
                }}>
                  <input
                    type="radio"
                    name="jobMode"
                    checked={!!newJob.config?.batch_mode}
                    onChange={() => {
                      setNewJob((prev) => ({
                        ...prev,
                        config: { ...prev.config, batch_mode: true },
                      }));
                      fetchCrawlerJobs();
                    }}
                    style={{ accentColor: "var(--metal-copper)" }}
                  />
                  <span style={{ fontWeight: "600", color: "var(--metal-copper)" }}>
                    🕷️ BATCH OPERATION PROTOCOL
                  </span>
                </label>
              </div>
            </div>

            {/* Batch Mode Configuration */}
            {newJob.config?.batch_mode && (
              <div style={{
                padding: "20px",
                marginBottom: "25px",
                border: "1px solid var(--metal-copper)",
                background: "rgba(255, 140, 0, 0.05)",
                borderRadius: "8px"
              }}>
                <h4 style={{ 
                  margin: "0 0 15px 0", 
                  color: "var(--metal-copper)",
                  fontSize: "16px"
                }}>
                  🔄 CRAWLER-TO-SCRAPER PIPELINE
                </h4>

                <div style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "20px",
                  marginBottom: "20px"
                }}>
                  <div>
                    <label style={{
                      display: "block",
                      marginBottom: "8px",
                      fontWeight: "600",
                      color: "var(--metal-silver)"
                    }}>
                      SELECT CRAWLER JOB:
                    </label>
                    <select
                      value={selectedCrawlerJob || ""}
                      onChange={async (e) => {
                        const jobId = parseInt(e.target.value);
                        setSelectedCrawlerJob(jobId);
                        if (jobId) {
                          const urls = await extractUrlsFromCrawler(jobId);
                          console.log(`Extracted ${urls.length} URLs from crawler job ${jobId}`);
                        }
                      }}
                      style={{
                        width: "100%",
                        padding: "12px",
                        background: "var(--bg-tertiary)",
                        border: "1px solid var(--border-primary)",
                        borderRadius: "6px",
                        color: "var(--text-primary)",
                        fontFamily: "'Rajdhani', sans-serif"
                      }}
                    >
                      <option value="">Choose a completed crawler job...</option>
                      {crawlerJobs.map((job) => (
                        <option key={job.id} value={job.id}>
                          {job.name} ({new Date(job.created_at).toLocaleDateString()})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label style={{
                      display: "block",
                      marginBottom: "8px",
                      fontWeight: "600",
                      color: "var(--metal-silver)"
                    }}>
                      BATCH SIZE:
                    </label>
                    <select
                      value={newJob.config?.batch_size || 10}
                      onChange={(e) =>
                        setNewJob((prev) => ({
                          ...prev,
                          config: {
                            ...prev.config,
                            batch_size: parseInt(e.target.value),
                          },
                        }))
                      }
                      style={{
                        width: "100%",
                        padding: "12px",
                        background: "var(--bg-tertiary)",
                        border: "1px solid var(--border-primary)",
                        borderRadius: "6px",
                        color: "var(--text-primary)",
                        fontFamily: "'Rajdhani', sans-serif"
                      }}
                    >
                      <option value={5}>5 URLs per job</option>
                      <option value={10}>10 URLs per job</option>
                      <option value={25}>25 URLs per job</option>
                      <option value={50}>50 URLs per job</option>
                    </select>
                  </div>
                </div>

                {extractedUrls.length > 0 && (
                  <div style={{
                    padding: "15px",
                    border: "1px solid var(--metal-gold)",
                    background: "rgba(212, 175, 55, 0.05)",
                    borderRadius: "6px"
                  }}>
                    <div style={{
                      fontWeight: "600",
                      color: "var(--metal-gold)",
                      marginBottom: "10px",
                      fontFamily: "'Orbitron', monospace"
                    }}>
                      ✅ TARGETS ACQUIRED: {extractedUrls.length} URLs
                    </div>
                    <div style={{
                      maxHeight: "120px",
                      overflow: "auto",
                      fontSize: "14px",
                      background: "var(--bg-tertiary)",
                      padding: "10px",
                      borderRadius: "6px",
                      fontFamily: "'Rajdhani', monospace"
                    }}>
                      {extractedUrls.slice(0, 10).map((url, index) => (
                        <div key={index} style={{ 
                          padding: "4px 0", 
                          borderBottom: "1px solid var(--border-primary)",
                          color: "var(--text-secondary)"
                        }}>
                          <span style={{ color: "var(--metal-silver)" }}>
                            {(index + 1).toString().padStart(2, '0')}.
                          </span> {url}
                        </div>
                      ))}
                      {extractedUrls.length > 10 && (
                        <div style={{ 
                          fontStyle: "italic", 
                          color: "var(--text-secondary)",
                          textAlign: "center",
                          padding: "8px 0"
                        }}>
                          ... and {extractedUrls.length - 10} more targets
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Advanced Configuration Section */}
            <div style={{
              padding: "20px",
              marginBottom: "25px",
              border: "1px solid var(--metal-silver)",
              background: "rgba(192, 192, 192, 0.05)",
              borderRadius: "8px"
            }}>
              <h4 style={{ 
                margin: "0 0 20px 0", 
                color: "var(--metal-silver)",
                fontSize: "16px",
                fontFamily: "'Orbitron', monospace"
              }}>
                ⚙️ ADVANCED CONFIGURATION
              </h4>

              {/* Crawling Protocols */}
              <div style={{ marginBottom: "25px" }}>
                <h5 style={{
                  margin: "0 0 15px 0",
                  color: "var(--metal-gold)",
                  fontSize: "14px",
                  fontFamily: "'Orbitron', monospace"
                }}>
                  🔗 CRAWLING PROTOCOLS
                </h5>
                
                <div style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "15px"
                }}>
                  <label style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    cursor: "pointer",
                    color: "var(--text-primary)",
                    fontFamily: "'Rajdhani', sans-serif"
                  }}>
                    <input
                      type="checkbox"
                      checked={newJob.config?.crawl_links !== false}
                      onChange={(e) =>
                        setNewJob((prev) => ({
                          ...prev,
                          config: {
                            ...prev.config,
                            crawl_links: e.target.checked,
                          },
                        }))
                      }
                      style={{
                        accentColor: "var(--metal-gold)",
                        transform: "scale(1.2)"
                      }}
                    />
                    Crawl Links
                  </label>

                  <label style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    cursor: "pointer",
                    color: "var(--text-primary)",
                    fontFamily: "'Rajdhani', sans-serif"
                  }}>
                    <input
                      type="checkbox"
                      checked={newJob.config?.follow_internal_links !== false}
                      onChange={(e) =>
                        setNewJob((prev) => ({
                          ...prev,
                          config: {
                            ...prev.config,
                            follow_internal_links: e.target.checked,
                          },
                        }))
                      }
                      style={{
                        accentColor: "var(--metal-gold)",
                        transform: "scale(1.2)"
                      }}
                    />
                    Follow Internal Links
                  </label>

                  <label style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    cursor: "pointer",
                    color: "var(--text-primary)",
                    fontFamily: "'Rajdhani', sans-serif"
                  }}>
                    <input
                      type="checkbox"
                      checked={newJob.config?.follow_external_links || false}
                      onChange={(e) =>
                        setNewJob((prev) => ({
                          ...prev,
                          config: {
                            ...prev.config,
                            follow_external_links: e.target.checked,
                          },
                        }))
                      }
                      style={{
                        accentColor: "var(--metal-gold)",
                        transform: "scale(1.2)"
                      }}
                    />
                    Follow External Links
                  </label>

                  <label style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    cursor: "pointer",
                    color: "var(--text-primary)",
                    fontFamily: "'Rajdhani', sans-serif"
                  }}>
                    <input
                      type="checkbox"
                      checked={newJob.config?.crawl_entire_domain || false}
                      onChange={(e) =>
                        setNewJob((prev) => ({
                          ...prev,
                          config: {
                            ...prev.config,
                            crawl_entire_domain: e.target.checked,
                          },
                        }))
                      }
                      style={{
                        accentColor: "var(--metal-gold)",
                        transform: "scale(1.2)"
                      }}
                    />
                    Crawl Entire Domain
                  </label>
                </div>
                
                {/* Domain Crawling Tips */}
                {newJob.config?.crawl_entire_domain && (
                  <div style={{
                    marginTop: "15px",
                    padding: "15px",
                    background: "rgba(0, 255, 255, 0.05)",
                    border: "1px solid var(--metal-silver)",
                    borderRadius: "8px",
                    fontSize: "12px",
                    color: "var(--text-secondary)",
                    fontFamily: "'Rajdhani', sans-serif"
                  }}>
                    <div style={{ 
                      color: "var(--accent-cyan)", 
                      fontWeight: "bold", 
                      marginBottom: "8px",
                      fontSize: "13px" 
                    }}>
                      💡 Domain Crawling Tips:
                    </div>
                    <ul style={{ margin: "0", paddingLeft: "20px", lineHeight: "1.4" }}>
                      <li>Works best with sites that have internal navigation (e.g., news sites, documentation)</li>
                      <li>Sites like "example.com" may show 0 results as they only have external links</li>
                      <li>Try: Wikipedia articles, news sites, or documentation sites for better results</li>
                      <li>Enable "Follow External Links" if you want to crawl beyond the domain</li>
                    </ul>
                  </div>
                )}
              </div>

              {/* Data Extraction */}
              <div style={{ marginBottom: "25px" }}>
                <h5 style={{
                  margin: "0 0 15px 0",
                  color: "var(--accent-green)",
                  fontSize: "14px",
                  fontFamily: "'Orbitron', monospace"
                }}>
                  📊 DATA EXTRACTION
                </h5>
                
                <div style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "15px"
                }}>
                  <label style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    cursor: "pointer",
                    color: "var(--text-primary)",
                    fontFamily: "'Rajdhani', sans-serif"
                  }}>
                    <input
                      type="checkbox"
                      checked={newJob.config?.include_scripts || false}
                      onChange={(e) =>
                        setNewJob((prev) => ({
                          ...prev,
                          config: {
                            ...prev.config,
                            include_scripts: e.target.checked,
                          },
                        }))
                      }
                      style={{
                        accentColor: "var(--accent-green)",
                        transform: "scale(1.2)"
                      }}
                    />
                    Include Scripts
                  </label>

                  <label style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    cursor: "pointer",
                    color: "var(--text-primary)",
                    fontFamily: "'Rajdhani', sans-serif"
                  }}>
                    <input
                      type="checkbox"
                      checked={newJob.config?.extract_metadata || false}
                      onChange={(e) =>
                        setNewJob((prev) => ({
                          ...prev,
                          config: {
                            ...prev.config,
                            extract_metadata: e.target.checked,
                          },
                        }))
                      }
                      style={{
                        accentColor: "var(--accent-green)",
                        transform: "scale(1.2)"
                      }}
                    />
                    Extract Metadata
                  </label>
                </div>
              </div>

              {/* System Parameters */}
              <div style={{ marginBottom: "25px" }}>
                <h5 style={{
                  margin: "0 0 15px 0",
                  color: "var(--accent-red)",
                  fontSize: "14px",
                  fontFamily: "'Orbitron', monospace"
                }}>
                  🔧 SYSTEM PARAMETERS
                </h5>
                
                <div style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "20px"
                }}>
                  <div>
                    <label style={{
                      display: "block",
                      marginBottom: "8px",
                      fontWeight: "600",
                      color: "var(--text-primary)",
                      fontFamily: "'Rajdhani', sans-serif"
                    }}>
                      Max Depth:
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={newJob.config?.max_depth || 3}
                      onChange={(e) =>
                        setNewJob((prev) => ({
                          ...prev,
                          config: {
                            ...prev.config,
                            max_depth: parseInt(e.target.value),
                          },
                        }))
                      }
                      style={{
                        width: "100%",
                        padding: "10px",
                        background: "var(--bg-tertiary)",
                        border: "1px solid var(--border-primary)",
                        borderRadius: "6px",
                        color: "var(--text-primary)",
                        fontFamily: "'Rajdhani', sans-serif"
                      }}
                    />
                  </div>

                  <div>
                    <label style={{
                      display: "block",
                      marginBottom: "8px",
                      fontWeight: "600",
                      color: "var(--text-primary)",
                      fontFamily: "'Rajdhani', sans-serif"
                    }}>
                      Max Pages:
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="1000"
                      value={newJob.config?.max_pages || 100}
                      onChange={(e) =>
                        setNewJob((prev) => ({
                          ...prev,
                          config: {
                            ...prev.config,
                            max_pages: parseInt(e.target.value),
                          },
                        }))
                      }
                      style={{
                        width: "100%",
                        padding: "10px",
                        background: "var(--bg-tertiary)",
                        border: "1px solid var(--border-primary)",
                        borderRadius: "6px",
                        color: "var(--text-primary)",
                        fontFamily: "'Rajdhani', sans-serif"
                      }}
                    />
                  </div>

                  <div>
                    <label style={{
                      display: "block",
                      marginBottom: "8px",
                      fontWeight: "600",
                      color: "var(--text-primary)",
                      fontFamily: "'Rajdhani', sans-serif"
                    }}>
                      Delay (ms):
                    </label>
                    <input
                      type="number"
                      min="100"
                      max="10000"
                      step="100"
                      value={newJob.config?.delay_between_requests || 1000}
                      onChange={(e) =>
                        setNewJob((prev) => ({
                          ...prev,
                          config: {
                            ...prev.config,
                            delay_between_requests: parseInt(e.target.value),
                          },
                        }))
                      }
                      style={{
                        width: "100%",
                        padding: "10px",
                        background: "var(--bg-tertiary)",
                        border: "1px solid var(--border-primary)",
                        borderRadius: "6px",
                        color: "var(--text-primary)",
                        fontFamily: "'Rajdhani', sans-serif"
                      }}
                    />
                  </div>

                  <div>
                    <label style={{
                      display: "block",
                      marginBottom: "8px",
                      fontWeight: "600",
                      color: "var(--text-primary)",
                      fontFamily: "'Rajdhani', sans-serif"
                    }}>
                      User Agent:
                    </label>
                    <select
                      value={newJob.config?.user_agent || "Mozilla/5.0 (compatible; TacticalScraper/1.0)"}
                      onChange={(e) =>
                        setNewJob((prev) => ({
                          ...prev,
                          config: {
                            ...prev.config,
                            user_agent: e.target.value,
                          },
                        }))
                      }
                      style={{
                        width: "100%",
                        padding: "10px",
                        background: "var(--bg-tertiary)",
                        border: "1px solid var(--border-primary)",
                        borderRadius: "6px",
                        color: "var(--text-primary)",
                        fontFamily: "'Rajdhani', sans-serif"
                      }}
                    >
                      <option value="Mozilla/5.0 (compatible; TacticalScraper/1.0)">Default Scraper</option>
                      <option value="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36">Chrome Desktop</option>
                      <option value="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36">Chrome Mac</option>
                      <option value="Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15">iPhone Safari</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Advanced Options */}
              <div>
                <h5 style={{
                  margin: "0 0 15px 0",
                  color: "var(--metal-silver)",
                  fontSize: "14px",
                  fontFamily: "'Orbitron', monospace"
                }}>
                  🚀 ADVANCED OPTIONS
                </h5>
                
                <div style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "15px"
                }}>
                  <label style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    cursor: "pointer",
                    color: "var(--text-primary)",
                    fontFamily: "'Rajdhani', sans-serif"
                  }}>
                    <input
                      type="checkbox"
                      checked={newJob.config?.respect_robots_txt !== false}
                      onChange={(e) =>
                        setNewJob((prev) => ({
                          ...prev,
                          config: {
                            ...prev.config,
                            respect_robots_txt: e.target.checked,
                          },
                        }))
                      }
                      style={{
                        accentColor: "var(--metal-silver)",
                        transform: "scale(1.2)"
                      }}
                    />
                    Respect robots.txt
                  </label>

                  <label style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    cursor: "pointer",
                    color: "var(--text-primary)",
                    fontFamily: "'Rajdhani', sans-serif"
                  }}>
                    <input
                      type="checkbox"
                      checked={newJob.config?.handle_javascript || false}
                      onChange={(e) =>
                        setNewJob((prev) => ({
                          ...prev,
                          config: {
                            ...prev.config,
                            handle_javascript: e.target.checked,
                          },
                        }))
                      }
                      style={{
                        accentColor: "var(--metal-silver)",
                        transform: "scale(1.2)"
                      }}
                    />
                    Handle JavaScript
                  </label>

                  <label style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    cursor: "pointer",
                    color: "var(--text-primary)",
                    fontFamily: "'Rajdhani', sans-serif"
                  }}>
                    <input
                      type="checkbox"
                      checked={newJob.config?.extract_emails || false}
                      onChange={(e) =>
                        setNewJob((prev) => ({
                          ...prev,
                          config: {
                            ...prev.config,
                            extract_emails: e.target.checked,
                          },
                        }))
                      }
                      style={{
                        accentColor: "var(--metal-silver)",
                        transform: "scale(1.2)"
                      }}
                    />
                    Extract Emails
                  </label>

                  <label style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    cursor: "pointer",
                    color: "var(--text-primary)",
                    fontFamily: "'Rajdhani', sans-serif"
                  }}>
                    <input
                      type="checkbox"
                      checked={newJob.config?.extract_phone_numbers || false}
                      onChange={(e) =>
                        setNewJob((prev) => ({
                          ...prev,
                          config: {
                            ...prev.config,
                            extract_phone_numbers: e.target.checked,
                          },
                        }))
                      }
                      style={{
                        accentColor: "var(--metal-silver)",
                        transform: "scale(1.2)"
                      }}
                    />
                    Extract Phone Numbers
                  </label>
                </div>
              </div>
            </div>

            <form
              onSubmit={async (e) => {
                e.preventDefault();
                if (newJob.config?.batch_mode && extractedUrls.length > 0) {
                  await createBatchScrapingJobs(
                    extractedUrls,
                    newJob.config?.batch_size || 10,
                  );
                } else {
                  await submitJob(e);
                }
              }}
              style={{
                display: "grid",
                gridTemplateColumns: newJob.config?.batch_mode
                  ? "1fr 1fr auto"
                  : "1fr 1fr 1fr auto",
                gap: "20px",
                alignItems: "end",
              }}
            >
              <div>
                <label style={{
                  display: "block",
                  marginBottom: "8px",
                  fontWeight: "600",
                  color: "var(--metal-silver)"
                }}>
                  OPERATION NAME:
                </label>
                <input
                  type="text"
                  value={newJob.name}
                  onChange={(e) => setNewJob({ ...newJob, name: e.target.value })}
                  required
                  placeholder={
                    newJob.config?.batch_mode
                      ? "Batch Scraper from Crawler"
                      : "My Scraping Job"
                  }
                  style={{
                    width: "100%",
                    padding: "12px",
                    background: "var(--bg-tertiary)",
                    border: "1px solid var(--border-primary)",
                    borderRadius: "6px",
                    color: "var(--text-primary)",
                    fontFamily: "'Rajdhani', sans-serif"
                  }}
                />
              </div>

              {!newJob.config?.batch_mode && (
                <div>
                  <label style={{
                    display: "block",
                    marginBottom: "8px",
                    fontWeight: "600",
                    color: "var(--metal-silver)"
                  }}>
                    TARGET URL:
                  </label>
                  <input
                    type="url"
                    value={newJob.url}
                    onChange={(e) => setNewJob({ ...newJob, url: e.target.value })}
                    required
                    placeholder="https://example.com"
                    style={{
                      width: "100%",
                      padding: "12px",
                      background: "var(--bg-tertiary)",
                      border: "1px solid var(--border-primary)",
                      borderRadius: "6px",
                      color: "var(--text-primary)",
                      fontFamily: "'Rajdhani', sans-serif"
                    }}
                  />
                  
                  {/* Domain Crawling URL Suggestions */}
                  {newJob.config?.crawl_entire_domain && (
                    <div style={{
                      marginTop: "10px",
                      padding: "12px",
                      background: "rgba(0, 255, 255, 0.05)",
                      border: "1px solid var(--accent-cyan)",
                      borderRadius: "4px",
                      fontSize: "12px"
                    }}>
                      <div style={{ 
                        color: "var(--accent-cyan)", 
                        fontWeight: "bold", 
                        marginBottom: "6px" 
                      }}>
                        💡 Recommended URLs for domain crawling:
                      </div>
                      <div style={{ 
                        color: "var(--text-secondary)",
                        fontFamily: "'Monaco', 'Consolas', monospace"
                      }}>
                        <button
                          type="button"
                          onClick={() => setNewJob({ ...newJob, url: "https://en.wikipedia.org/wiki/Web_scraping" })}
                          style={{
                            background: "none",
                            border: "none",
                            color: "var(--accent-cyan)",
                            textDecoration: "underline",
                            cursor: "pointer",
                            fontSize: "12px",
                            fontFamily: "'Monaco', 'Consolas', monospace",
                            padding: "2px 0",
                            margin: "0 5px 0 0"
                          }}
                        >
                          Wikipedia article
                        </button> |
                        <button
                          type="button"
                          onClick={() => setNewJob({ ...newJob, url: "https://httpbin.org" })}
                          style={{
                            background: "none",
                            border: "none",
                            color: "var(--accent-cyan)",
                            textDecoration: "underline",
                            cursor: "pointer",
                            fontSize: "12px",
                            fontFamily: "'Monaco', 'Consolas', monospace",
                            padding: "2px 0",
                            margin: "0 5px"
                          }}
                        >
                          HTTPBin.org
                        </button> |
                        <button
                          type="button"
                          onClick={() => setNewJob({ ...newJob, url: "https://news.ycombinator.com" })}
                          style={{
                            background: "none",
                            border: "none",
                            color: "var(--accent-cyan)",
                            textDecoration: "underline",
                            cursor: "pointer",
                            fontSize: "12px",
                            fontFamily: "'Monaco', 'Consolas', monospace",
                            padding: "2px 0",
                            margin: "0 0 0 5px"
                          }}
                        >
                          Hacker News
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              <div>
                <label style={{
                  display: "block",
                  marginBottom: "8px",
                  fontWeight: "600",
                  color: "var(--metal-silver)"
                }}>
                  OPERATION TYPE:
                </label>
                <select
                  value={newJob.scraper_type}
                  onChange={(e) => setNewJob({
                    ...newJob,
                    scraper_type: e.target.value as "intelligent" | "custom"
                  })}
                  style={{
                    width: "100%",
                    padding: "12px",
                    background: "var(--bg-tertiary)",
                    border: "1px solid var(--border-primary)",
                    borderRadius: "6px",
                    color: "var(--text-primary)",
                    fontFamily: "'Rajdhani', sans-serif"
                  }}
                >
                  <option value="intelligent">🤖 Intelligent Scraping</option>
                  <option value="custom">⚙️ Custom Selectors</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={isSubmitting || (!newJob.url && !newJob.config?.batch_mode)}
                style={{
                  minWidth: "140px",
                  padding: "12px 20px",
                  background: (isSubmitting || (!newJob.url && !newJob.config?.batch_mode)) ? "var(--bg-tertiary)" : "var(--metal-gold)",
                  color: (isSubmitting || (!newJob.url && !newJob.config?.batch_mode)) ? "var(--text-secondary)" : "var(--bg-primary)",
                  border: `1px solid ${(isSubmitting || (!newJob.url && !newJob.config?.batch_mode)) ? "var(--border-primary)" : "var(--metal-gold)"}`,
                  borderRadius: "6px",
                  cursor: (isSubmitting || (!newJob.url && !newJob.config?.batch_mode)) ? "not-allowed" : "pointer",
                  fontFamily: "'Rajdhani', sans-serif",
                  fontWeight: "600",
                  fontSize: "14px"
                }}
              >
                {isSubmitting ? (
                  <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <div style={{
                      width: "16px",
                      height: "16px",
                      border: "2px solid var(--text-secondary)",
                      borderTop: "2px solid var(--metal-silver)",
                      borderRadius: "50%",
                      animation: "spin 1s linear infinite"
                    }}></div>
                    PROCESSING...
                  </span>
                ) : newJob.config?.batch_mode ? (
                  "🚀 LAUNCH BATCH"
                ) : (
                  "⚡ DEPLOY"
                )}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Dashboard Tab */}
      {currentTab === "dashboard" && (
        <div>
          <div style={{
            background: "var(--bg-secondary)",
            padding: "20px",
            borderRadius: "8px",
            border: "1px solid var(--border-primary)"
          }}>
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "20px"
            }}>
              <h2 style={{ 
                margin: "0",
                color: "var(--metal-silver)",
                fontSize: "20px"
              }}>
                🔄 Recent Operations
              </h2>
              <button
                onClick={async () => {
                  console.log("🔄 Manually refreshing jobs list...");
                  try {
                    const response = await authenticatedFetch("/api/jobs");
                    if (response.ok) {
                      const data = await response.json();
                      // Backend returns jobs array directly, not wrapped in {jobs: [...]}
                      const jobsArray = Array.isArray(data) ? data : (data.jobs || []);
                      setJobs(jobsArray);
                      console.log("✅ Jobs refreshed:", jobsArray.length, "jobs found");
                    } else {
                      console.error("❌ Failed to refresh jobs:", response.status);
                    }
                  } catch (error) {
                    console.error("❌ Error refreshing jobs:", error);
                  }
                }}
                style={{
                  padding: "8px 16px",
                  background: "var(--metal-steel)",
                  border: "1px solid var(--border-primary)",
                  color: "var(--text-primary)",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontFamily: "'Rajdhani', sans-serif",
                  fontSize: "14px"
                }}
              >
                🔄 Refresh
              </button>
            </div>
            
            {console.log("🔍 Dashboard - Current jobs state:", jobs)}
            {jobs.length === 0 ? (
              <div style={{
                textAlign: "center",
                padding: "40px",
                color: "var(--text-secondary)"
              }}>
                No jobs found. Create your first operation in the Operations tab.
              </div>
            ) : (
              jobs.map((job) => (
                <div key={job.id} data-job-id={job.id} style={{ 
                  border: "1px solid var(--border-primary)", 
                  background: "var(--bg-tertiary)",
                  padding: "20px", 
                  marginBottom: "15px",
                  borderRadius: "6px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center"
                }}>
                  <div>
                    <strong style={{ 
                      color: "var(--text-primary)",
                      fontSize: "16px",
                      display: "block",
                      marginBottom: "5px"
                    }}>
                      {job.name}
                    </strong>
                    <div style={{ 
                      fontSize: "12px", 
                      color: "var(--text-secondary)",
                      marginBottom: "5px"
                    }}>
                      Created: {new Date(job.created_at).toLocaleString()}
                    </div>
                    <div style={{ 
                      fontSize: "12px", 
                      color: "var(--text-secondary)"
                    }}>
                      URL: {job.url}
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                    {/* Progress Bar for Running Jobs */}
                    {job.status === "running" && jobProgress[job.id] && (
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginRight: "10px" }}>
                        <div style={{
                          width: "120px",
                          height: "8px",
                          backgroundColor: "#e9ecef",
                          borderRadius: "4px",
                          overflow: "hidden"
                        }}>
                          <div style={{
                            width: `${jobProgress[job.id].progress_percentage}%`,
                            height: "100%",
                            backgroundColor: "var(--metal-steel)",
                            borderRadius: "4px",
                            transition: "width 0.3s ease"
                          }} />
                        </div>
                        <span style={{ fontSize: "11px", color: "var(--text-secondary)", minWidth: "35px" }}>
                          {jobProgress[job.id].progress_percentage.toFixed(0)}%
                        </span>
                      </div>
                    )}
                    
                    <span style={{
                      padding: "6px 12px",
                      borderRadius: "12px",
                      fontSize: "12px",
                      fontWeight: "600",
                      backgroundColor: job.status === "completed" ? "var(--metal-gold)" : 
                                     job.status === "failed" ? "var(--metal-copper)" : 
                                     job.status === "running" ? "var(--metal-steel)" : "var(--bg-tertiary)",
                      color: job.status === "completed" ? "var(--bg-primary)" :
                             job.status === "failed" ? "var(--text-primary)" :
                             job.status === "running" ? "var(--text-primary)" : "var(--text-secondary)"
                    }}>
                      {job.status ? job.status.toUpperCase() : 'PENDING'}
                    </span>
                    <button
                      onClick={() => getJobDetails(job.id)}
                      style={{
                        padding: "6px 12px",
                        fontSize: "12px",
                        background: "var(--bg-tertiary)",
                        color: "var(--text-primary)",
                        border: "1px solid var(--border-primary)",
                        borderRadius: "4px",
                        cursor: "pointer",
                        fontFamily: "'Rajdhani', sans-serif",
                        fontWeight: "600"
                      }}
                    >
                      Details
                    </button>
                    {job.status === "pending" && (
                      <button
                        onClick={() => startJob(job.id)}
                        style={{
                          padding: "6px 12px",
                          fontSize: "12px",
                          background: "var(--metal-gold)",
                          color: "var(--bg-primary)",
                          border: "1px solid var(--metal-gold)",
                          borderRadius: "4px",
                          cursor: "pointer",
                          fontFamily: "'Rajdhani', sans-serif",
                          fontWeight: "600"
                        }}
                      >
                        Start
                      </button>
                    )}
                    {job.status === "completed" && (
                      <>
                        <button
                          onClick={() => getJobResults(job.id)}
                          style={{
                            padding: "6px 12px",
                            fontSize: "12px",
                            background: "var(--metal-silver)",
                            color: "var(--bg-primary)",
                            border: "1px solid var(--metal-silver)",
                            borderRadius: "4px",
                            cursor: "pointer",
                            fontFamily: "'Rajdhani', sans-serif",
                            fontWeight: "600",
                            marginRight: "8px"
                          }}
                        >
                          View Results
                        </button>
                        <button
                          onClick={() => {
                            setPageViewerJobId(job.id);
                            setPageViewerUrl(undefined);
                            setShowPageViewer(true);
                          }}
                          style={{
                            padding: "6px 12px",
                            fontSize: "12px",
                            background: "var(--accent-electric-blue)",
                            color: "white",
                            border: "1px solid var(--accent-electric-blue)",
                            borderRadius: "4px",
                            cursor: "pointer",
                            fontFamily: "'Rajdhani', sans-serif",
                            fontWeight: "600",
                            marginRight: "8px"
                          }}
                        >
                          🔍 Advanced View
                        </button>
                      </>
                    )}
                    
                    {/* Delete Button - Available for all non-running jobs */}
                    {job.status !== "running" && (
                      <button
                        onClick={() => {
                          const jobName = job.name || `Job #${job.id}`;
                          if (confirm(`Are you sure you want to delete "${jobName}"? This action cannot be undone.`)) {
                            deleteJob(job.id);
                          }
                        }}
                        style={{
                          padding: "6px 12px",
                          fontSize: "12px",
                          background: "var(--metal-copper)",
                          color: "white",
                          border: "1px solid var(--metal-copper)",
                          borderRadius: "4px",
                          cursor: "pointer",
                          fontFamily: "'Rajdhani', sans-serif",
                          fontWeight: "600"
                        }}
                        title="Delete this job permanently"
                      >
                        🗑️ Delete
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Analytics Tab */}
      {currentTab === "analytics" && (
        <div>
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
            gap: "20px",
            marginBottom: "30px"
          }}>
            {analytics && (
              <>
                <div style={{
                  background: "var(--bg-secondary)",
                  padding: "25px",
                  borderRadius: "8px",
                  border: "1px solid var(--border-primary)",
                  textAlign: "center"
                }}>
                  <h3 style={{ 
                    margin: "0 0 15px 0", 
                    color: "var(--metal-silver)",
                    fontSize: "16px"
                  }}>
                    Total Jobs
                  </h3>
                  <div style={{ 
                    fontSize: "3em", 
                    fontWeight: "bold", 
                    color: "var(--metal-chrome)",
                    fontFamily: "'Orbitron', monospace"
                  }}>
                    {analytics.total_jobs}
                  </div>
                </div>

                <div style={{
                  background: "var(--bg-secondary)",
                  padding: "25px",
                  borderRadius: "8px",
                  border: "1px solid var(--metal-gold)",
                  textAlign: "center"
                }}>
                  <h3 style={{ 
                    margin: "0 0 15px 0", 
                    color: "var(--metal-gold)",
                    fontSize: "16px"
                  }}>
                    Completed
                  </h3>
                  <div style={{ 
                    fontSize: "3em", 
                    fontWeight: "bold", 
                    color: "var(--metal-gold)",
                    fontFamily: "'Orbitron', monospace"
                  }}>
                    {analytics.completed_jobs}
                  </div>
                </div>

                <div style={{
                  background: "var(--bg-secondary)",
                  padding: "25px",
                  borderRadius: "8px",
                  border: "1px solid var(--metal-steel)",
                  textAlign: "center"
                }}>
                  <h3 style={{ 
                    margin: "0 0 15px 0", 
                    color: "var(--metal-steel)",
                    fontSize: "16px"
                  }}>
                    Running
                  </h3>
                  <div style={{ 
                    fontSize: "3em", 
                    fontWeight: "bold", 
                    color: "var(--metal-steel)",
                    fontFamily: "'Orbitron', monospace"
                  }}>
                    {analytics.running_jobs}
                  </div>
                </div>

                <div style={{
                  background: "var(--bg-secondary)",
                  padding: "25px",
                  borderRadius: "8px",
                  border: "1px solid var(--metal-copper)",
                  textAlign: "center"
                }}>
                  <h3 style={{ 
                    margin: "0 0 15px 0", 
                    color: "var(--metal-copper)",
                    fontSize: "16px"
                  }}>
                    Failed
                  </h3>
                  <div style={{ 
                    fontSize: "3em", 
                    fontWeight: "bold", 
                    color: "var(--metal-copper)",
                    fontFamily: "'Orbitron', monospace"
                  }}>
                    {analytics.failed_jobs}
                  </div>
                </div>
              </>
            )}
          </div>

          {!analytics && (
            <div style={{
              background: "var(--bg-secondary)",
              padding: "40px",
              borderRadius: "8px",
              border: "1px solid var(--border-primary)",
              textAlign: "center"
            }}>
              <div style={{ color: "var(--text-secondary)" }}>
                Loading analytics data...
              </div>
            </div>
          )}
        </div>
      )}

      {/* Network Tab */}
      {currentTab === "network" && (
        <div>
          <div style={{
            background: "var(--bg-secondary)",
            padding: "25px",
            borderRadius: "8px",
            border: "1px solid var(--border-primary)"
          }}>
            <h2 style={{ 
              margin: "0 0 20px 0",
              color: "var(--metal-silver)",
              fontSize: "20px"
            }}>
              🔗 Network Analysis & Monitoring
            </h2>
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
              gap: "20px"
            }}>
              <div style={{
                background: "var(--bg-tertiary)",
                padding: "20px",
                borderRadius: "6px",
                border: "1px solid var(--border-primary)"
              }}>
                <h3 style={{ color: "var(--metal-gold)", margin: "0 0 15px 0" }}>Connection Status</h3>
                <div style={{ color: "var(--text-primary)" }}>
                  Backend: {isBackendConnected ? "🟢 Connected" : "🔴 Disconnected"}
                </div>
              </div>
              <div style={{
                background: "var(--bg-tertiary)",
                padding: "20px",
                borderRadius: "6px",
                border: "1px solid var(--border-primary)"
              }}>
                <h3 style={{ color: "var(--metal-gold)", margin: "0 0 15px 0" }}>Network Performance</h3>
                <div style={{ color: "var(--text-primary)" }}>
                  Latency: Measuring...
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* OSINT Tab */}
      {currentTab === "osint" && (
        <div>
          <div style={{
            background: "var(--bg-secondary)",
            padding: "25px",
            borderRadius: "8px",
            border: "1px solid var(--border-primary)"
          }}>
            <h2 style={{ 
              margin: "0 0 20px 0",
              color: "var(--metal-silver)",
              fontSize: "20px"
            }}>
              🎯 OSINT Intelligence Gathering
            </h2>
            <div style={{
              background: "var(--bg-tertiary)",
              padding: "20px",
              borderRadius: "6px",
              border: "1px solid var(--border-primary)",
              textAlign: "center"
            }}>
              <div style={{ color: "var(--text-secondary)", fontSize: "16px" }}>
                Open Source Intelligence tools and analysis coming soon...
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Data Enrichment Tab */}
      {currentTab === "data-enrichment" && (
        <div>
          <div style={{
            background: "var(--bg-secondary)",
            padding: "25px",
            borderRadius: "8px",
            border: "1px solid var(--border-primary)"
          }}>
            <h2 style={{ 
              margin: "0 0 20px 0",
              color: "var(--metal-silver)",
              fontSize: "20px"
            }}>
              💎 Data Enrichment & Enhancement
            </h2>
            <div style={{
              background: "var(--bg-tertiary)",
              padding: "20px",
              borderRadius: "6px",
              border: "1px solid var(--border-primary)",
              textAlign: "center"
            }}>
              <div style={{ color: "var(--text-secondary)", fontSize: "16px" }}>
                Data enrichment pipeline and ML enhancement tools...
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Performance Tab */}
      {currentTab === "performance" && (
        <div>
          <div style={{
            background: "var(--bg-secondary)",
            padding: "25px",
            borderRadius: "8px",
            border: "1px solid var(--border-primary)"
          }}>
            <h2 style={{ 
              margin: "0 0 20px 0",
              color: "var(--metal-silver)",
              fontSize: "20px"
            }}>
              ⚡ Performance Monitoring & Optimization
            </h2>
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
              gap: "20px"
            }}>
              <div style={{
                background: "var(--bg-tertiary)",
                padding: "20px",
                borderRadius: "6px",
                border: "1px solid var(--metal-steel)",
                textAlign: "center"
              }}>
                <h3 style={{ color: "var(--metal-steel)", margin: "0 0 10px 0" }}>CPU Usage</h3>
                <div style={{ fontSize: "2em", color: "var(--metal-steel)" }}>--</div>
              </div>
              <div style={{
                background: "var(--bg-tertiary)",
                padding: "20px",
                borderRadius: "6px",
                border: "1px solid var(--metal-steel)",
                textAlign: "center"
              }}>
                <h3 style={{ color: "var(--metal-steel)", margin: "0 0 10px 0" }}>Memory</h3>
                <div style={{ fontSize: "2em", color: "var(--metal-steel)" }}>--</div>
              </div>
              <div style={{
                background: "var(--bg-tertiary)",
                padding: "20px",
                borderRadius: "6px",
                border: "1px solid var(--metal-steel)",
                textAlign: "center"
              }}>
                <h3 style={{ color: "var(--metal-steel)", margin: "0 0 10px 0" }}>Response Time</h3>
                <div style={{ fontSize: "2em", color: "var(--metal-steel)" }}>--</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI Analytics Tab */}
      {currentTab === "ai-analytics" && (
        <div>
          <div style={{
            background: "var(--bg-secondary)",
            padding: "25px",
            borderRadius: "8px",
            border: "1px solid var(--border-primary)"
          }}>
            <h2 style={{ 
              margin: "0 0 20px 0",
              color: "var(--metal-silver)",
              fontSize: "20px"
            }}>
              🤖 AI Core & Machine Learning Analytics
            </h2>
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
              gap: "20px"
            }}>
              <div style={{
                background: "var(--bg-tertiary)",
                padding: "20px",
                borderRadius: "6px",
                border: "1px solid var(--metal-chrome)"
              }}>
                <h3 style={{ color: "var(--metal-chrome)", margin: "0 0 15px 0" }}>AI Model Status</h3>
                <div style={{ color: "var(--text-primary)" }}>
                  NLP Engine: 🟢 Active<br/>
                  Classification: 🟢 Ready<br/>
                  Sentiment Analysis: 🟢 Online
                </div>
              </div>
              <div style={{
                background: "var(--bg-tertiary)",
                padding: "20px",
                borderRadius: "6px",
                border: "1px solid var(--metal-chrome)"
              }}>
                <h3 style={{ color: "var(--metal-chrome)", margin: "0 0 15px 0" }}>Processing Queue</h3>
                <div style={{ color: "var(--text-primary)" }}>
                  Pending Tasks: 0<br/>
                  Processing: 0<br/>
                  Completed Today: 0
                </div>
              </div>
            </div>
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
          backgroundColor: "rgba(0,0,0,0.85)",
          display: "flex",
          justifyContent: "center",
          alignItems: "flex-start", // Changed from center to flex-start
          zIndex: 9999,
          paddingTop: "20px", // Add padding from top
          paddingBottom: "20px",
          overflow: "auto" // Allow scrolling within the modal backdrop
        }}
        onClick={(e) => {
          // Close modal when clicking on backdrop
          if (e.target === e.currentTarget) {
            setJobResults(null);
          }
        }}
        >
          <div style={{
            background: "var(--bg-secondary)",
            color: "var(--text-primary)",
            padding: "30px",
            borderRadius: "12px",
            maxWidth: "900px",
            width: "90%",
            maxHeight: "calc(100vh - 40px)", // Ensure modal doesn't exceed viewport
            overflow: "auto",
            border: "1px solid var(--border-primary)",
            boxShadow: "0 20px 40px rgba(0,0,0,0.5)",
            position: "relative", // Ensure proper positioning
            margin: "0 auto" // Center horizontally
          }}
          onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside modal
          >
            <div style={{ 
              display: "flex", 
              justifyContent: "space-between", 
              alignItems: "center", 
              marginBottom: "25px",
              borderBottom: "1px solid var(--border-primary)",
              paddingBottom: "15px",
              position: "sticky", // Make header sticky
              top: "0",
              background: "var(--bg-secondary)", // Match modal background
              zIndex: "10"
            }}>
              <h2 style={{ 
                margin: "0",
                color: "var(--metal-gold)",
                fontSize: "22px"
              }}>
                📊 Job Results: {jobResults.job_name}
              </h2>
              <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                <button
                  onClick={() => {
                    // Scroll back to the job in the list
                    const jobElement = document.querySelector(`[data-job-id="${jobs.find(j => j.name === jobResults.job_name)?.id}"]`);
                    if (jobElement) {
                      setJobResults(null);
                      setTimeout(() => {
                        jobElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                      }, 100);
                    } else {
                      setJobResults(null);
                    }
                  }}
                  style={{
                    background: "var(--metal-steel)",
                    color: "var(--text-primary)",
                    border: "1px solid var(--metal-steel)",
                    padding: "8px 16px",
                    borderRadius: "6px",
                    cursor: "pointer",
                    fontFamily: "'Rajdhani', sans-serif",
                    fontWeight: "600",
                    fontSize: "12px"
                  }}
                >
                  📍 Go to Job
                </button>
                <button
                  onClick={() => setJobResults(null)}
                  style={{
                    background: "var(--metal-copper)",
                    color: "var(--text-primary)",
                    border: "1px solid var(--metal-copper)",
                    padding: "10px 20px",
                    borderRadius: "6px",
                    cursor: "pointer",
                    fontFamily: "'Rajdhani', sans-serif",
                    fontWeight: "600"
                  }}
                >
                  ✕ Close
                </button>
              </div>
            </div>
            <div>
              {Array.isArray(jobResults.data) && jobResults.data.length > 0 ? (
                <div>
                  <div style={{
                    marginBottom: "20px",
                    padding: "15px",
                    background: "var(--bg-tertiary)",
                    borderRadius: "6px",
                    border: "1px solid var(--border-primary)"
                  }}>
                    <h3 style={{ 
                      margin: "0 0 10px 0", 
                      color: "var(--metal-silver)",
                      fontSize: "16px"
                    }}>
                      📈 Summary
                    </h3>
                    <div style={{ color: "var(--text-primary)" }}>
                      <strong>Total Results:</strong> {jobResults.data.length}<br/>
                      <strong>First URL:</strong> {jobResults.data[0]?.url || 'N/A'}<br/>
                      <strong>Status:</strong> {jobResults.data[0]?.status || 'N/A'}<br/>
                      <strong>Images Collected:</strong> {jobResults.data.reduce((total: number, result: any) => 
                        total + (result.images ? result.images.length : 0), 0
                      )}
                    </div>
                  </div>
                  
                  {jobResults.data.map((result: any, index: number) => (
                    <div key={index} style={{
                      marginBottom: "20px",
                      padding: "20px",
                      background: "var(--bg-tertiary)",
                      borderRadius: "8px",
                      border: "1px solid var(--border-primary)"
                    }}>
                      <h4 style={{ 
                        margin: "0 0 15px 0", 
                        color: "var(--metal-gold)",
                        fontSize: "18px"
                      }}>
                        🔗 {result.headline || result.url || `Result ${index + 1}`}
                      </h4>
                      
                      <div style={{ 
                        display: "grid", 
                        gridTemplateColumns: "1fr 1fr", 
                        gap: "15px",
                        marginBottom: "15px"
                      }}>
                        <div>
                          <strong style={{ color: "var(--metal-silver)" }}>URL:</strong><br/>
                          <a href={result.url} target="_blank" rel="noopener noreferrer" style={{
                            color: "var(--metal-chrome)",
                            textDecoration: "none",
                            fontSize: "12px",
                            wordBreak: "break-all"
                          }}>
                            {result.url}
                          </a>
                        </div>
                        <div>
                          <strong style={{ color: "var(--metal-silver)" }}>Status:</strong><br/>
                          <span style={{
                            color: result.status === 'success' ? "var(--accent-green)" : "var(--metal-copper)",
                            fontWeight: "600"
                          }}>
                            {result.status || 'Unknown'}
                          </span>
                        </div>
                        {result.images && result.images.length > 0 && (
                          <div>
                            <strong style={{ color: "var(--metal-silver)" }}>Images:</strong><br/>
                            <span style={{ 
                              color: "var(--accent-green)",
                              fontWeight: "600"
                            }}>
                              {result.images.length} collected
                            </span>
                          </div>
                        )}
                        {result.word_count && (
                          <div>
                            <strong style={{ color: "var(--metal-silver)" }}>Word Count:</strong><br/>
                            <span style={{ color: "var(--text-primary)" }}>{result.word_count.toLocaleString()}</span>
                          </div>
                        )}
                        {result.reading_time && (
                          <div>
                            <strong style={{ color: "var(--metal-silver)" }}>Reading Time:</strong><br/>
                            <span style={{ color: "var(--text-primary)" }}>{result.reading_time}</span>
                          </div>
                        )}
                        {result.author && (
                          <div>
                            <strong style={{ color: "var(--metal-silver)" }}>Author:</strong><br/>
                            <span style={{ color: "var(--text-primary)", fontSize: "12px" }}>
                              {result.author.length > 50 ? result.author.substring(0, 50) + '...' : result.author}
                            </span>
                          </div>
                        )}
                        {result.publish_date && (
                          <div>
                            <strong style={{ color: "var(--metal-silver)" }}>Published:</strong><br/>
                            <span style={{ color: "var(--text-primary)" }}>{result.publish_date}</span>
                          </div>
                        )}
                      </div>
                      
                      {result.article_content && (
                        <div style={{ marginTop: "15px" }}>
                          <strong style={{ color: "var(--metal-silver)" }}>Content Preview:</strong>
                          <div style={{
                            marginTop: "8px",
                            padding: "15px",
                            background: "var(--bg-primary)",
                            borderRadius: "6px",
                            border: "1px solid var(--border-primary)",
                            fontSize: "12px",
                            lineHeight: "1.4",
                            maxHeight: "150px",
                            overflow: "auto",
                            color: "var(--text-secondary)"
                          }}>
                            {result.article_content.length > 500 
                              ? result.article_content.substring(0, 500) + '...' 
                              : result.article_content || 'No content available'}
                          </div>
                        </div>
                      )}
                      
                      {/* Image Gallery */}
                      {result.images && result.images.length > 0 && (
                        <div style={{
                          marginTop: "15px",
                          padding: "15px",
                          background: "rgba(0, 255, 255, 0.05)",
                          border: "1px solid var(--accent-cyan)",
                          borderRadius: "6px"
                        }}>
                          <h4 style={{
                            margin: "0 0 10px 0",
                            color: "var(--accent-cyan)",
                            fontSize: "14px",
                            fontWeight: "600"
                          }}>
                            🖼️ Images ({result.images.length})
                          </h4>
                          <div style={{
                            display: "grid",
                            gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))",
                            gap: "10px",
                            maxHeight: "200px",
                            overflowY: "auto"
                          }}>
                            {result.images.slice(0, 12).map((img: any, imgIndex: number) => (
                              <div key={imgIndex} style={{
                                border: "1px solid var(--border-primary)",
                                borderRadius: "4px",
                                overflow: "hidden",
                                background: "var(--bg-primary)"
                              }}>
                                <img 
                                  src={img.src} 
                                  alt={img.alt || `Image ${imgIndex + 1}`}
                                  style={{
                                    width: "100%",
                                    height: "80px",
                                    objectFit: "cover",
                                    cursor: "pointer"
                                  }}
                                  onClick={() => window.open(img.src, '_blank')}
                                  onError={(e) => {
                                    (e.target as HTMLImageElement).style.display = 'none';
                                  }}
                                />
                                <div style={{
                                  padding: "5px",
                                  fontSize: "10px",
                                  color: "var(--text-secondary)",
                                  textAlign: "center",
                                  wordBreak: "break-all"
                                }}>
                                  {img.alt || `Image ${imgIndex + 1}`}
                                </div>
                              </div>
                            ))}
                          </div>
                          {result.images.length > 12 && (
                            <div style={{
                              marginTop: "10px",
                              fontSize: "12px",
                              color: "var(--text-secondary)",
                              textAlign: "center"
                            }}>
                              Showing first 12 of {result.images.length} images
                            </div>
                          )}
                        </div>
                      )}
                      
                      <div style={{ 
                        marginTop: "15px",
                        fontSize: "11px",
                        color: "var(--text-secondary)",
                        borderTop: "1px solid var(--border-primary)",
                        paddingTop: "10px"
                      }}>
                        <strong>Retrieved:</strong> {result.retrieved_at || result.timestamp || 'Unknown'}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{
                  padding: "40px",
                  textAlign: "center",
                  background: "var(--bg-tertiary)",
                  borderRadius: "8px",
                  border: "1px solid var(--border-primary)"
                }}>
                  <div style={{ 
                    fontSize: "16px", 
                    color: "var(--text-secondary)",
                    marginBottom: "15px"
                  }}>
                    No results found for this job.
                  </div>
                  
                  {/* Enhanced guidance for domain crawling */}
                  <div style={{
                    marginTop: "20px",
                    padding: "20px",
                    background: "rgba(255, 165, 0, 0.05)",
                    border: "1px solid var(--metal-copper)",
                    borderRadius: "6px",
                    textAlign: "left"
                  }}>
                    <div style={{ 
                      color: "var(--metal-copper)", 
                      fontWeight: "bold", 
                      marginBottom: "12px",
                      fontSize: "14px"
                    }}>
                      🔍 Why might this happen with domain crawling?
                    </div>
                    <ul style={{ 
                      margin: "0", 
                      paddingLeft: "20px", 
                      lineHeight: "1.6",
                      fontSize: "13px",
                      color: "var(--text-secondary)"
                    }}>
                      <li><strong>External Links Only:</strong> Some sites (like example.com) only have external links that get filtered out</li>
                      <li><strong>No Internal Navigation:</strong> The website may not have internal links to discover</li>
                      <li><strong>Configuration:</strong> Check if "Follow External Links" should be enabled for your use case</li>
                      <li><strong>Better Test Sites:</strong> Try Wikipedia articles, news sites, or documentation sites</li>
                    </ul>
                    
                    <div style={{
                      marginTop: "15px",
                      padding: "12px",
                      background: "rgba(0, 255, 255, 0.05)",
                      border: "1px solid var(--accent-cyan)",
                      borderRadius: "4px"
                    }}>
                      <div style={{ 
                        color: "var(--accent-cyan)", 
                        fontWeight: "bold", 
                        fontSize: "12px",
                        marginBottom: "6px"
                      }}>
                        💡 Recommended Test URLs:
                      </div>
                      <div style={{ 
                        fontSize: "12px", 
                        color: "var(--text-secondary)",
                        fontFamily: "'Monaco', 'Consolas', monospace"
                      }}>
                        • https://en.wikipedia.org/wiki/Web_scraping<br/>
                        • https://httpbin.org<br/>
                        • Any news website homepage
                      </div>
                    </div>
                  </div>
                  
                  <details style={{ marginTop: "20px" }}>
                    <summary style={{ 
                      cursor: "pointer", 
                      color: "var(--metal-copper)",
                      fontWeight: "600"
                    }}>
                      Show Raw Data
                    </summary>
                    <pre style={{ 
                      background: "var(--bg-primary)", 
                      padding: "15px", 
                      borderRadius: "6px",
                      overflow: "auto",
                      fontSize: "11px",
                      fontFamily: "'Monaco', 'Consolas', monospace",
                      border: "1px solid var(--border-primary)",
                      lineHeight: "1.4",
                      marginTop: "10px",
                      textAlign: "left"
                    }}>
                      {JSON.stringify(jobResults.data, null, 2)}
                    </pre>
                  </details>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Job Details Modal */}
      {jobDetails && (
        <div style={{
          position: "fixed",
          top: "0",
          left: "0",
          right: "0",
          bottom: "0",
          backgroundColor: "rgba(0,0,0,0.85)",
          display: "flex",
          justifyContent: "center",
          alignItems: "flex-start",
          zIndex: 9999,
          paddingTop: "20px",
          paddingBottom: "20px",
          overflow: "auto"
        }}
        onClick={(e) => {
          if (e.target === e.currentTarget) {
            setJobDetails(null);
          }
        }}
        >
          <div style={{
            background: "var(--bg-secondary)",
            color: "var(--text-primary)",
            padding: "30px",
            borderRadius: "12px",
            maxWidth: "800px",
            width: "90%",
            maxHeight: "calc(100vh - 40px)",
            overflow: "auto",
            border: "1px solid var(--border-primary)",
            boxShadow: "0 20px 40px rgba(0,0,0,0.5)",
            position: "relative",
            margin: "0 auto"
          }}
          onClick={(e) => e.stopPropagation()}
          >
            <div style={{ 
              display: "flex", 
              justifyContent: "space-between", 
              alignItems: "center", 
              marginBottom: "25px",
              borderBottom: "1px solid var(--border-primary)",
              paddingBottom: "15px",
              position: "sticky",
              top: "0",
              background: "var(--bg-secondary)",
              zIndex: "10"
            }}>
              <h2 style={{ 
                margin: "0",
                color: "var(--metal-gold)",
                fontSize: "22px"
              }}>
                📋 Job Details: {jobDetails.name}
              </h2>
              <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                <button
                  onClick={() => {
                    const jobElement = document.querySelector(`[data-job-id="${jobDetails.id}"]`);
                    if (jobElement) {
                      setJobDetails(null);
                      setTimeout(() => {
                        jobElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                      }, 100);
                    } else {
                      setJobDetails(null);
                    }
                  }}
                  style={{
                    background: "var(--metal-steel)",
                    color: "var(--text-primary)",
                    border: "1px solid var(--metal-steel)",
                    padding: "8px 16px",
                    borderRadius: "6px",
                    cursor: "pointer",
                    fontFamily: "'Rajdhani', sans-serif",
                    fontWeight: "600",
                    fontSize: "12px"
                  }}
                >
                  📍 Go to Job
                </button>
                <button
                  onClick={() => setJobDetails(null)}
                  style={{
                    background: "var(--metal-copper)",
                    color: "var(--text-primary)",
                    border: "1px solid var(--metal-copper)",
                    padding: "10px 20px",
                    borderRadius: "6px",
                    cursor: "pointer",
                    fontFamily: "'Rajdhani', sans-serif",
                    fontWeight: "600"
                  }}
                >
                  ✕ Close
                </button>
              </div>
            </div>
            
            <div>
              {/* Basic Job Information */}
              <div style={{
                marginBottom: "25px",
                padding: "20px",
                background: "var(--bg-tertiary)",
                borderRadius: "8px",
                border: "1px solid var(--border-primary)"
              }}>
                <h3 style={{ 
                  margin: "0 0 15px 0", 
                  color: "var(--metal-silver)",
                  fontSize: "18px"
                }}>
                  📊 General Information
                </h3>
                
                <div style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "15px"
                }}>
                  <div>
                    <strong style={{ color: "var(--metal-silver)" }}>Job ID:</strong><br/>
                    <span style={{ color: "var(--text-primary)" }}>{jobDetails.id}</span>
                  </div>
                  <div>
                    <strong style={{ color: "var(--metal-silver)" }}>Name:</strong><br/>
                    <span style={{ color: "var(--text-primary)" }}>{jobDetails.name}</span>
                  </div>
                  <div>
                    <strong style={{ color: "var(--metal-silver)" }}>Status:</strong><br/>
                    <span style={{
                      color: jobDetails.status === 'completed' ? "var(--accent-green)" : 
                             jobDetails.status === 'failed' ? "var(--metal-copper)" : 
                             jobDetails.status === 'running' ? "var(--metal-steel)" : "var(--text-primary)",
                      fontWeight: "600",
                      textTransform: "uppercase"
                    }}>
                      {jobDetails.status || 'PENDING'}
                    </span>
                  </div>
                  <div>
                    <strong style={{ color: "var(--metal-silver)" }}>Type:</strong><br/>
                    <span style={{ color: "var(--text-primary)" }}>{jobDetails.type}</span>
                  </div>
                  <div>
                    <strong style={{ color: "var(--metal-silver)" }}>Created:</strong><br/>
                    <span style={{ color: "var(--text-primary)" }}>
                      {new Date(jobDetails.created_at).toLocaleString()}
                    </span>
                  </div>
                  {jobDetails.results_count && (
                    <div>
                      <strong style={{ color: "var(--metal-silver)" }}>Last Results:</strong><br/>
                      <span style={{ color: "var(--text-primary)" }}>
                        {new Date(jobDetails.results_count).toLocaleString()}
                      </span>
                    </div>
                  )}
                </div>
                
                {jobDetails.config?.url && (
                  <div style={{ marginTop: "15px" }}>
                    <strong style={{ color: "var(--metal-silver)" }}>Target URL:</strong><br/>
                    <a href={jobDetails.config.url} target="_blank" rel="noopener noreferrer" style={{
                      color: "var(--metal-chrome)",
                      textDecoration: "none",
                      fontSize: "14px",
                      wordBreak: "break-all"
                    }}>
                      {jobDetails.config.url}
                    </a>
                  </div>
                )}
              </div>

              {/* Configuration Details */}
              {jobDetails.config?.config && (
                <div style={{
                  marginBottom: "25px",
                  padding: "20px",
                  background: "var(--bg-tertiary)",
                  borderRadius: "8px",
                  border: "1px solid var(--border-primary)"
                }}>
                  <h3 style={{ 
                    margin: "0 0 15px 0", 
                    color: "var(--metal-gold)",
                    fontSize: "18px"
                  }}>
                    ⚙️ Configuration
                  </h3>
                  
                  <div style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: "15px"
                  }}>
                    {jobDetails.config.config.max_pages && (
                      <div>
                        <strong style={{ color: "var(--metal-silver)" }}>Max Pages:</strong><br/>
                        <span style={{ color: "var(--text-primary)" }}>{jobDetails.config.config.max_pages}</span>
                      </div>
                    )}
                    {jobDetails.config.config.max_depth && (
                      <div>
                        <strong style={{ color: "var(--metal-silver)" }}>Max Depth:</strong><br/>
                        <span style={{ color: "var(--text-primary)" }}>{jobDetails.config.config.max_depth}</span>
                      </div>
                    )}
                    <div>
                      <strong style={{ color: "var(--metal-silver)" }}>Crawl Links:</strong><br/>
                      <span style={{ color: jobDetails.config.config.crawl_links ? "var(--accent-green)" : "var(--metal-copper)" }}>
                        {jobDetails.config.config.crawl_links ? "✅ Enabled" : "❌ Disabled"}
                      </span>
                    </div>
                    <div>
                      <strong style={{ color: "var(--metal-silver)" }}>Follow Internal Links:</strong><br/>
                      <span style={{ color: jobDetails.config.config.follow_internal_links ? "var(--accent-green)" : "var(--metal-copper)" }}>
                        {jobDetails.config.config.follow_internal_links ? "✅ Enabled" : "❌ Disabled"}
                      </span>
                    </div>
                    <div>
                      <strong style={{ color: "var(--metal-silver)" }}>Follow External Links:</strong><br/>
                      <span style={{ color: jobDetails.config.config.follow_external_links ? "var(--accent-green)" : "var(--metal-copper)" }}>
                        {jobDetails.config.config.follow_external_links ? "✅ Enabled" : "❌ Disabled"}
                      </span>
                    </div>
                    <div>
                      <strong style={{ color: "var(--metal-silver)" }}>Include Images:</strong><br/>
                      <span style={{ color: jobDetails.config.config.include_images ? "var(--accent-green)" : "var(--metal-copper)" }}>
                        {jobDetails.config.config.include_images ? "✅ Enabled" : "❌ Disabled"}
                      </span>
                    </div>
                    <div>
                      <strong style={{ color: "var(--metal-silver)" }}>Save to Database:</strong><br/>
                      <span style={{ color: jobDetails.config.config.save_to_database ? "var(--accent-green)" : "var(--metal-copper)" }}>
                        {jobDetails.config.config.save_to_database ? "✅ Enabled" : "❌ Disabled"}
                      </span>
                    </div>
                    <div>
                      <strong style={{ color: "var(--metal-silver)" }}>Extract Full HTML:</strong><br/>
                      <span style={{ color: jobDetails.config.config.extract_full_html ? "var(--accent-green)" : "var(--metal-copper)" }}>
                        {jobDetails.config.config.extract_full_html ? "✅ Enabled" : "❌ Disabled"}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Raw Details */}
              <details style={{ marginTop: "20px" }}>
                <summary style={{ 
                  cursor: "pointer", 
                  color: "var(--metal-copper)",
                  fontWeight: "600",
                  marginBottom: "15px"
                }}>
                  🔧 Show Raw Job Data
                </summary>
                <pre style={{ 
                  background: "var(--bg-primary)", 
                  padding: "15px", 
                  borderRadius: "6px",
                  overflow: "auto",
                  fontSize: "11px",
                  fontFamily: "'Monaco', 'Consolas', monospace",
                  border: "1px solid var(--border-primary)",
                  lineHeight: "1.4",
                  color: "var(--text-secondary)"
                }}>
                  {JSON.stringify(jobDetails, null, 2)}
                </pre>
              </details>
            </div>
          </div>
        </div>
      )}

      {/* Page Viewer Modal */}
      <PageViewerModal
        show={showPageViewer}
        onHide={() => {
          setShowPageViewer(false);
          setPageViewerJobId(null);
          setPageViewerUrl(undefined);
        }}
        jobId={pageViewerJobId!}
        selectedUrl={pageViewerUrl}
      />

      {/* Admin Dashboard Modal */}
      <AdminDashboard
        show={showAdminDashboard}
        onHide={() => setShowAdminDashboard(false)}
      />
    </div>
  );
};

export default App;
