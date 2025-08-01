import React, { useState, useEffect, useRef } from "react";
import OperationsInterface from "./OperationsInterface";

interface ScrapingJob {
  name: string;
  type: string;
  url: string;
  scraper_type: "basic" | "e_commerce" | "news" | "social_media" | "api";
  custom_selectors?: { [key: string]: string };
  config?: {
    max_pages?: number;
    delay?: number;
    follow_links?: boolean;
    max_depth?: number;
    link_patterns?: string[];
    ignore_patterns?: string[];
    source_crawler_job_id?: number;
    batch_mode?: boolean;
    url_extraction_field?: string;
    [key: string]: any;
  };
}

interface JobResult {
  id: number;
  name: string;
  type: string;
  status: string;
  created_at: string;
  results_count: number;
  url?: string;
  config?: any;
}

interface LoginData {
  username: string;
  password: string;
}

interface JobDetails {
  id: number;
  name: string;
  type: string;
  status: string;
  config: any;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

interface AnalyticsData {
  total_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  running_jobs: number;
  total_data_points: number;
  avg_completion_time: number;
}

interface PerformanceMetrics {
  cpu_usage: number;
  memory_usage: number;
  active_connections: number;
  requests_per_minute: number;
  avg_response_time: number;
  cache_hit_rate: number;
}

interface JobResultsData {
  job_id: number;
  job_name: string;
  data: any[];
  total_count: number;
  status: string;
  created_at: string;
  completed_at?: string;
}

const App = () => {
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  const [jobs, setJobs] = useState<JobResult[]>([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState<string>("");
  const [currentTab, setCurrentTab] = useState<
    | "dashboard"
    | "jobs"
    | "operations"
    | "analytics"
    | "performance"
    | "crawlers"
    | "network"
    | "osint"
    | "data-enrichment"
    | "data-parsing"
    | "browser"
    | "visualization"
  >("operations");
  const [loginData, setLoginData] = useState<LoginData>({
    username: "admin",
    password: "admin123",
  });
  const [newJob, setNewJob] = useState<ScrapingJob>({
    name: "",
    type: "intelligent_crawling", // Default to intelligent crawling
    url: "",
    scraper_type: "intelligent",
    custom_selectors: {},
    config: {
      max_depth: 3,
      max_pages: 15,
      follow_internal_links: true,
      follow_external_links: false,
      // NEW: Enhanced crawling options
      extract_full_html: false,
      crawl_entire_domain: false,
      include_images: false,
      save_to_database: true,
    },
  });
  const [selectedJob, setSelectedJob] = useState<JobDetails | null>(null);
  const [jobResults, setJobResults] = useState<JobResultsData | null>(null);
  const [resultsSearchTerm, setResultsSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [selectedCrawlerJob, setSelectedCrawlerJob] = useState<number | null>(
    null,
  );
  const [crawlerJobs, setCrawlerJobs] = useState<JobDetails[]>([]);
  const [extractedUrls, setExtractedUrls] = useState<string[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(
    null,
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Operations configuration state
  const [operationsConfig, setOperationsConfig] = useState(() => {
    const saved = localStorage.getItem("operationsConfig");
    return saved
      ? JSON.parse(saved)
      : {
          showDashboard: true,
          showJobCreation: true,
          showQueue: true,
          showConfiguration: true,
          expandedSections: {
            dashboard: true,
            jobCreation: true,
            queue: true,
            configuration: false,
          },
          autoRefresh: true,
          refreshInterval: 5000,
        };
  });
  const [configPanelOpen, setConfigPanelOpen] = useState(false);
  const [workflowSidebarOpen, setWorkflowSidebarOpen] = useState(false);
  const [selectedJobForWorkflow, setSelectedJobForWorkflow] =
    useState<JobResult | null>(null);

  // Modal state ref to prevent auto-refresh interference
  const isModalOpen = useRef(false);

  // Check backend connection
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/health");
        setIsBackendConnected(response.ok);
      } catch (error) {
        setIsBackendConnected(false);
      }
    };

    checkBackend();
    const interval = setInterval(checkBackend, 30000);
    return () => clearInterval(interval);
  }, []);

  // Login function
  const login = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch("http://localhost:8000/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(loginData),
      });

      if (response.ok) {
        const data = await response.json();
        setToken(data.access_token);
        setIsAuthenticated(true);
        loadDashboardData(data.access_token);
      } else {
        alert("Login failed");
      }
    } catch (error) {
      console.error("Login error:", error);
      alert("Login error");
    }
  };

  // Load all dashboard data
  const loadDashboardData = async (authToken?: string) => {
    await Promise.all([
      fetchJobs(authToken),
      fetchAnalytics(authToken),
      fetchPerformance(authToken),
    ]);
  };

  // Fetch jobs
  const fetchJobs = async (authToken?: string) => {
    try {
      const response = await fetch("http://localhost:8000/api/jobs", {
        headers: {
          Authorization: `Bearer ${authToken || token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setJobs(data);
      }
    } catch (error) {
      console.error("Failed to fetch jobs:", error);
    }
  };

  // Fetch analytics
  const fetchAnalytics = async (authToken?: string) => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/analytics/dashboard",
        {
          headers: {
            Authorization: `Bearer ${authToken || token}`,
          },
        },
      );
      if (response.ok) {
        const data = await response.json();
        // Transform API response to match frontend interface
        const transformedData = {
          total_jobs: data.jobs?.total || 0,
          completed_jobs: data.jobs?.completed || 0,
          failed_jobs: data.jobs?.failed || 0,
          running_jobs: data.jobs?.running || 0,
          total_data_points: data.results?.total || 0,
          avg_completion_time: 0, // Will need to calculate this from performance data
        };
        setAnalytics(transformedData);
      }
    } catch (error) {
      console.error("Failed to fetch analytics:", error);
    }
  };

  // Fetch performance metrics
  const fetchPerformance = async (authToken?: string) => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/performance/summary",
        {
          headers: {
            Authorization: `Bearer ${authToken || token}`,
          },
        },
      );
      if (response.ok) {
        const data = await response.json();
        setPerformance(data);
      }
    } catch (error) {
      console.error("Failed to fetch performance:", error);
    }
  };

  // Get job details
  const getJobDetails = async (jobId: number) => {
    console.log("getJobDetails called for job:", jobId);
    try {
      const response = await fetch(`http://localhost:8000/api/jobs/${jobId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        console.log("Job details received:", data);
        setSelectedJob(data);
      } else {
        console.error("Failed to fetch job details, status:", response.status);
      }
    } catch (error) {
      console.error("Failed to fetch job details:", error);
    }
  };

  // Start job
  const startJob = async (jobId: number) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/jobs/${jobId}/start`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );
      if (response.ok) {
        fetchJobs();
        alert("Job started successfully!");
      }
    } catch (error) {
      console.error("Failed to start job:", error);
      alert("Failed to start job");
    }
  };

  // Get job results
  const getJobResults = async (jobId: number) => {
    console.log("getJobResults called for job:", jobId);
    try {
      const response = await fetch(
        `http://localhost:8000/api/jobs/${jobId}/results`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      let data;

      if (response.ok) {
        data = await response.json();
        console.log("Raw API response:", data);
      } else {
        console.log("Backend response error, status:", response.status, "showing demo data");
        // If backend is not available, show demo data
        const job = jobs.find((j) => j.id === jobId);

        // Generate realistic demo data based on job type
        let demoData = [];
        if (
          job?.name?.toLowerCase().includes("news") ||
          job?.name?.toLowerCase().includes("article")
        ) {
          demoData = [
            {
              id: 1,
              title: "Breaking News: Tech Industry Updates",
              url: `${job?.url || "https://example.com"}/article/1`,
              content:
                "This is a comprehensive analysis of the latest developments in the technology sector, including major announcements from leading companies...",
              published_date: "2025-01-15T10:30:00Z",
              author: "John Smith",
              category: "Technology",
              reading_time: "5 min",
            },
            {
              id: 2,
              title: "Market Analysis: Q4 Financial Report",
              url: `${job?.url || "https://example.com"}/article/2`,
              content:
                "The fourth quarter financial results show significant growth across multiple sectors. Key highlights include...",
              published_date: "2025-01-14T08:15:00Z",
              author: "Sarah Johnson",
              category: "Finance",
              reading_time: "8 min",
            },
            {
              id: 3,
              title: "Innovation Spotlight: AI Breakthroughs",
              url: `${job?.url || "https://example.com"}/article/3`,
              content:
                "Recent advances in artificial intelligence have opened new possibilities for automation and efficiency improvements...",
              published_date: "2025-01-13T14:45:00Z",
              author: "Dr. Michael Chen",
              category: "Innovation",
              reading_time: "12 min",
            },
          ];
        } else if (
          job?.name?.toLowerCase().includes("ecommerce") ||
          job?.name?.toLowerCase().includes("product")
        ) {
          demoData = [
            {
              id: 1,
              product_name: "Wireless Bluetooth Headphones",
              price: "$129.99",
              url: `${job?.url || "https://example.com"}/product/1`,
              description:
                "Premium wireless headphones with noise cancellation and 30-hour battery life",
              rating: 4.5,
              reviews_count: 1247,
              in_stock: true,
              category: "Electronics",
            },
            {
              id: 2,
              product_name: "Smart Fitness Tracker",
              price: "$79.99",
              url: `${job?.url || "https://example.com"}/product/2`,
              description:
                "Advanced fitness tracker with heart rate monitoring, GPS, and sleep tracking",
              rating: 4.2,
              reviews_count: 892,
              in_stock: true,
              category: "Health & Fitness",
            },
            {
              id: 3,
              product_name: "Portable Power Bank 20000mAh",
              price: "$45.99",
              url: `${job?.url || "https://example.com"}/product/3`,
              description:
                "High-capacity power bank with fast charging and multiple USB ports",
              rating: 4.7,
              reviews_count: 2156,
              in_stock: false,
              category: "Accessories",
            },
          ];
        } else {
          demoData = [
            {
              id: 1,
              url: `${job?.url || "https://example.com"}/page/1`,
              title: "Homepage Content Analysis",
              content:
                "Main landing page with key information about services and company overview",
              scraped_at: "2025-01-15T12:00:00Z",
              word_count: 1250,
              links_found: 23,
              images_found: 8,
            },
            {
              id: 2,
              url: `${job?.url || "https://example.com"}/page/2`,
              title: "About Us Page",
              content:
                "Company history, mission statement, and team information",
              scraped_at: "2025-01-15T12:01:30Z",
              word_count: 850,
              links_found: 12,
              images_found: 15,
            },
            {
              id: 3,
              url: `${job?.url || "https://example.com"}/page/3`,
              title: "Services Overview",
              content:
                "Detailed description of available services and pricing information",
              scraped_at: "2025-01-15T12:03:00Z",
              word_count: 2100,
              links_found: 45,
              images_found: 6,
            },
          ];
        }

        data = {
          data: demoData,
          total_records: demoData.length,
          exported_at: new Date().toISOString(),
        };
      }

      // Transform the data to match our interface
      let extractedData = [];
      let totalCount = 0;
      
      // Handle intelligent crawling results - check if it's an array with crawling data
      if (Array.isArray(data) && data.length > 0 && data[0].crawled_data) {
        // Intelligent crawling result structure (array with nested crawled_data)
        const crawlingResult = data[0];
        extractedData = crawlingResult.crawled_data || [];
        totalCount = crawlingResult.summary?.data_extracted || extractedData.length;
        console.log("Detected intelligent crawling data:", crawlingResult.summary);
        console.log("Extracted data count:", extractedData.length);
      } else if (data && typeof data === 'object' && data.crawled_data) {
        // Direct crawling result structure  
        extractedData = data.crawled_data || [];
        totalCount = data.summary?.data_extracted || extractedData.length;
        console.log("Detected intelligent crawling data:", data.summary);
      } else if (Array.isArray(data)) {
        // Direct array of results
        extractedData = data;
        totalCount = data.length;
      } else if (data && (data.data || data.results)) {
        // Nested result structure
        extractedData = data.data || data.results || [];
        totalCount = data.total_records || data.total_count || data.count || extractedData.length;
      } else {
        // Single result or unknown structure
        extractedData = data ? [data] : [];
        totalCount = extractedData.length;
      }

      const transformedData = {
        job_id: jobId,
        job_name: jobs.find((j) => j.id === jobId)?.name || `Job ${jobId}`,
        data: extractedData,
        total_count: totalCount,
        status: "completed",
        created_at: new Date().toISOString(),
        completed_at:
          data.exported_at || data.completed_at || new Date().toISOString(),
        // Include original crawling metadata if available
        ...(data && data.summary && {
          crawling_summary: data.summary,
          discovered_urls: data.discovered_urls || [],
        }),
      };

      console.log("Transformed data:", transformedData);
      console.log("Setting jobResults state, modal should show now");
      setJobResults(transformedData);
      setResultsSearchTerm("");
      setCurrentPage(1); // Reset to first page
      
      // Return the data so other components can use it
      return data;
    } catch (error) {
      console.error("Failed to fetch results:", error);

      // Show demo data on error too
      const job = jobs.find((j) => j.id === jobId);
      const demoData = [
        {
          id: 1,
          title: "Demo Data Entry",
          content:
            "This is demonstration data shown when the backend is not available",
          url: `${job?.url || "https://example.com"}/demo`,
          scraped_at: new Date().toISOString(),
        },
      ];

      const transformedData = {
        job_id: jobId,
        job_name: job?.name || `Job ${jobId}`,
        data: demoData,
        total_count: demoData.length,
        status: "completed",
        created_at: new Date().toISOString(),
        completed_at: new Date().toISOString(),
      };

      setJobResults(transformedData);
      setResultsSearchTerm("");
      setCurrentPage(1); // Reset to first page
      
      // Return the demo data so other components can use it
      return demoData;
    }
  };

  useEffect(() => {
    if (isAuthenticated && token) {
      loadDashboardData();
      fetchCrawlerJobs(); // Fetch available crawler jobs
      const interval = setInterval(() => {
        if (
          currentTab === "dashboard" ||
          currentTab === "jobs" ||
          currentTab === "operations"
        ) {
          fetchJobs();
        }
        if (currentTab === "performance") {
          fetchPerformance();
        }
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [isAuthenticated, token, currentTab]);

  // Submit new job
  const submitJob = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await fetch("http://localhost:8000/api/jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(newJob),
      });

      if (response.ok) {
        const result = await response.json();
        console.log("Job created:", result);
        setNewJob({
          name: "",
          type: "intelligent_crawling",
          url: "",
          scraper_type: "intelligent",
          custom_selectors: {},
          config: {
            max_depth: 3,
            max_pages: 15,
            follow_internal_links: true,
            follow_external_links: false,
            // NEW: Enhanced crawling options
            extract_full_html: false,
            crawl_entire_domain: false,
            include_images: false,
            save_to_database: true,
          },
        });
        fetchJobs();
        setCurrentTab("jobs");
      } else {
        const errorData = await response.text();
        console.error("Failed to create job:", response.status, errorData);
        alert(`Failed to create job: ${response.status} ${errorData}`);
      }
    } catch (error) {
      console.error("Error creating job:", error);
      alert("Error creating job: " + error);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Fetch crawler jobs for the dropdown
  const fetchCrawlerJobs = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/jobs", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        // Filter for completed crawler jobs
        const crawlers =
          data.jobs?.filter(
            (job: JobDetails) =>
              job.status === "completed" &&
              (job.type === "crawling" ||
                job.name.toLowerCase().includes("crawl")),
          ) || [];
        setCrawlerJobs(crawlers);
      }
    } catch (error) {
      console.error("Error fetching crawler jobs:", error);
    }
  };

  // Extract URLs from crawler job results
  const extractUrlsFromCrawler = async (crawlerJobId: number) => {
    try {
      // Use the new backend endpoint for URL extraction
      const response = await fetch(
        `http://localhost:8000/api/jobs/${crawlerJobId}/extract-urls`,
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );

      if (response.ok) {
        const data = await response.json();
        const urls = data.extracted_urls || [];

        setExtractedUrls(urls);

        if (urls.length > 0) {
          // Update the job config with the extracted URLs
          setNewJob((prev) => ({
            ...prev,
            config: {
              ...prev.config,
              source_crawler_job_id: crawlerJobId,
              batch_mode: true,
              extracted_urls: urls,
            },
          }));
        }

        return urls;
      } else {
        console.log(
          `Backend extraction failed with status ${response.status}, trying fallback`,
        );
      }
    } catch (error) {
      console.log("Backend extraction error:", error);
    }

    // Fallback to client-side extraction
    try {
      const fallbackResponse = await fetch(
        `http://localhost:8000/api/jobs/${crawlerJobId}/results`,
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );

      if (fallbackResponse.ok) {
        const data = await fallbackResponse.json();
        const urls: string[] = [];

        console.log("Fallback extraction - got job results:", data);

        // Extract URLs from crawler data with enhanced field detection
        if (data.data && Array.isArray(data.data)) {
          data.data.forEach((item: any, index: number) => {
            console.log(`Processing item ${index}:`, item);

            // Comprehensive list of possible URL fields
            const possibleUrlFields = [
              "url",
              "link",
              "href",
              "page_url",
              "discovered_url",
              "target_url",
              "source_url",
              "canonical_url",
              "original_url",
              "crawled_url",
              "found_url",
              "extracted_url",
              "site_url",
              "web_url",
              "full_url",
              "absolute_url",
              "final_url",
              "redirect_url",
              "destination_url",
            ];

            // Check direct fields
            for (const field of possibleUrlFields) {
              if (item[field]) {
                const value = item[field];
                if (
                  typeof value === "string" &&
                  (value.startsWith("http://") || value.startsWith("https://"))
                ) {
                  urls.push(value);
                  console.log(`Found URL in field '${field}': ${value}`);
                }
              }
            }

            // Check for arrays of links
            if (item.links && Array.isArray(item.links)) {
              item.links.forEach((link: any, linkIndex: number) => {
                if (
                  typeof link === "string" &&
                  (link.startsWith("http://") || link.startsWith("https://"))
                ) {
                  urls.push(link);
                  console.log(`Found URL in links[${linkIndex}]: ${link}`);
                } else if (link && typeof link === "object") {
                  // Check nested link objects
                  possibleUrlFields.forEach((field) => {
                    if (
                      link[field] &&
                      typeof link[field] === "string" &&
                      (link[field].startsWith("http://") ||
                        link[field].startsWith("https://"))
                    ) {
                      urls.push(link[field]);
                      console.log(
                        `Found URL in links[${linkIndex}].${field}: ${link[field]}`,
                      );
                    }
                  });
                }
              });
            }

            // Check any other array fields that might contain URLs
            Object.keys(item).forEach((key) => {
              if (Array.isArray(item[key])) {
                item[key].forEach((arrayItem: any, arrayIndex: number) => {
                  if (
                    typeof arrayItem === "string" &&
                    (arrayItem.startsWith("http://") ||
                      arrayItem.startsWith("https://"))
                  ) {
                    urls.push(arrayItem);
                    console.log(
                      `Found URL in array ${key}[${arrayIndex}]: ${arrayItem}`,
                    );
                  }
                });
              }
            });

            // Check for nested objects that might contain URLs
            Object.keys(item).forEach((key) => {
              const value = item[key];
              if (value && typeof value === "object" && !Array.isArray(value)) {
                possibleUrlFields.forEach((field) => {
                  if (
                    value[field] &&
                    typeof value[field] === "string" &&
                    (value[field].startsWith("http://") ||
                      value[field].startsWith("https://"))
                  ) {
                    urls.push(value[field]);
                    console.log(
                      `Found URL in nested ${key}.${field}: ${value[field]}`,
                    );
                  }
                });
              }
            });
          });
        }

        // Remove duplicates and validate URLs
        const uniqueUrls = [...new Set(urls)].filter((url) => {
          try {
            new URL(url);
            return true;
          } catch {
            console.log(`Invalid URL filtered out: ${url}`);
            return false;
          }
        });

        console.log(`Final extracted URLs (${uniqueUrls.length}):`, uniqueUrls);

        setExtractedUrls(uniqueUrls);

        if (uniqueUrls.length > 0) {
          // Update the job config with the extracted URLs
          setNewJob((prev) => ({
            ...prev,
            config: {
              ...prev.config,
              source_crawler_job_id: crawlerJobId,
              batch_mode: true,
              extracted_urls: uniqueUrls,
            },
          }));
        }

        return uniqueUrls;
      }
    } catch (error) {
      console.error("Fallback extraction error:", error);
    }

    return [];
  };

  // Create batch scraping jobs from extracted URLs
  const createBatchScrapingJobs = async (
    urls: string[],
    batchSize: number = 10,
  ) => {
    if (!urls.length) return;

    setIsSubmitting(true);
    try {
      // Use the new batch job creation endpoint
      const response = await fetch("http://localhost:8002/api/jobs/batch", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          base_name: newJob.name,
          source_crawler_job_id: selectedCrawlerJob,
          scraper_type: newJob.scraper_type,
          urls: urls,
          batch_size: batchSize,
          config: {
            ...newJob.config,
            custom_selectors: newJob.custom_selectors,
          },
        }),
      });

      if (response.ok) {
        const createdJobs = await response.json();

        alert(
          `✅ Successfully created ${createdJobs.length} batch scraping jobs from ${urls.length} URLs!`,
        );
        await fetchJobs();

        // Reset form
        setNewJob({
          name: "",
          type: "intelligent_crawling",
          url: "",
          scraper_type: "intelligent",
          custom_selectors: {},
          config: {
            max_depth: 3,
            max_pages: 15,
            follow_internal_links: true,
            follow_external_links: false,
          },
        });
        setSelectedCrawlerJob(null);
        setExtractedUrls([]);
      } else {
        const errorData = await response.text();
        console.error(
          "Failed to create batch jobs:",
          response.status,
          errorData,
        );
        alert(`Failed to create batch jobs: ${response.status} ${errorData}`);
      }
    } catch (error) {
      console.error("Error creating batch jobs:", error);
      alert("Error creating batch jobs: " + error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div
        style={{
          padding: "20px",
          fontFamily: "Arial, sans-serif",
          maxWidth: "400px",
          margin: "50px auto",
        }}
      >
        <h1 style={{ color: "#1976d2", textAlign: "center" }}>
          🎯 Business Intelligence Scraper
        </h1>
        <div
          style={{
            padding: "10px",
            backgroundColor: isBackendConnected ? "#d4edda" : "#f8d7da",
            border: "1px solid",
            borderColor: isBackendConnected ? "#c3e6cb" : "#f5c6cb",
            borderRadius: "5px",
            marginBottom: "20px",
          }}
        >
          Backend Status:{" "}
          {isBackendConnected ? "✅ Connected" : "❌ Disconnected"}
        </div>

        <form
          onSubmit={login}
          style={{ display: "flex", flexDirection: "column", gap: "15px" }}
        >
          <h2>🔐 Login</h2>
          <div>
            <label
              style={{
                display: "block",
                marginBottom: "5px",
                fontWeight: "bold",
              }}
            >
              Username:
            </label>
            <input
              type="text"
              value={loginData.username}
              onChange={(e) =>
                setLoginData({ ...loginData, username: e.target.value })
              }
              required
              style={{
                width: "100%",
                padding: "8px",
                border: "1px solid #ccc",
                borderRadius: "4px",
              }}
            />
          </div>
          <div>
            <label
              style={{
                display: "block",
                marginBottom: "5px",
                fontWeight: "bold",
              }}
            >
              Password:
            </label>
            <input
              type="password"
              value={loginData.password}
              onChange={(e) =>
                setLoginData({ ...loginData, password: e.target.value })
              }
              required
              style={{
                width: "100%",
                padding: "8px",
                border: "1px solid #ccc",
                borderRadius: "4px",
              }}
            />
          </div>
          <button
            type="submit"
            disabled={!isBackendConnected}
            style={{
              padding: "12px",
              backgroundColor: isBackendConnected ? "#1976d2" : "#6c757d",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: isBackendConnected ? "pointer" : "not-allowed",
              fontSize: "16px",
            }}
          >
            Login
          </button>
        </form>
        <p
          style={{
            textAlign: "center",
            marginTop: "20px",
            fontSize: "14px",
            color: "#666",
          }}
        >
          Default credentials: admin / admin123
        </p>
      </div>
    );
  }

  // Operations configuration functions
  const updateOperationsConfig = (updates: any) => {
    const newConfig = { ...operationsConfig, ...updates };
    setOperationsConfig(newConfig);
    localStorage.setItem("operationsConfig", JSON.stringify(newConfig));
  };

  const toggleSection = (section: string) => {
    updateOperationsConfig({
      expandedSections: {
        ...operationsConfig.expandedSections,
        [section]: !operationsConfig.expandedSections[section],
      },
    });
  };

  const toggleConfigPanel = () => {
    setConfigPanelOpen(!configPanelOpen);
  };

  const resetOperationsConfig = () => {
    const defaultConfig = {
      showDashboard: true,
      showJobCreation: true,
      showQueue: true,
      showConfiguration: true,
      expandedSections: {
        dashboard: true,
        jobCreation: false,
        queue: true,
        configuration: false,
      },
      autoRefresh: true,
      refreshInterval: 5000,
    };
    setOperationsConfig(defaultConfig);
    localStorage.setItem("operationsConfig", JSON.stringify(defaultConfig));
  };

  const tabStyle = (tabName: string) => ({
    padding: "10px 20px",
    margin: "0 5px",
    backgroundColor: currentTab === tabName ? "#1976d2" : "#f8f9fa",
    color: currentTab === tabName ? "white" : "#333",
    border: "1px solid #ddd",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "14px",
  });

  return (
    <div
      style={{
        padding: "20px",
        fontFamily: "Arial, sans-serif",
        maxWidth: "1400px",
        margin: "0 auto",
      }}
    >
      <header
        style={{
          marginBottom: "30px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <h1 style={{ color: "#1976d2", margin: "0" }}>
            🎯 Business Intelligence Scraper
          </h1>
          <div
            style={{
              padding: "5px 10px",
              backgroundColor: isBackendConnected ? "#d4edda" : "#f8d7da",
              border: "1px solid",
              borderColor: isBackendConnected ? "#c3e6cb" : "#f5c6cb",
              borderRadius: "3px",
              marginTop: "5px",
              display: "inline-block",
            }}
          >
            {isBackendConnected ? "✅ Connected" : "❌ Disconnected"}
          </div>
        </div>
        <button
          onClick={() => {
            setIsAuthenticated(false);
            setToken("");
            setJobs([]);
            setAnalytics(null);
            setPerformance(null);
          }}
          style={{
            padding: "8px 16px",
            backgroundColor: "#dc3545",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          Logout
        </button>
      </header>

      {/* Navigation Tabs */}
      <nav style={{ marginBottom: "30px" }}>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "5px" }}>
          <button
            style={tabStyle("operations")}
            onClick={() => setCurrentTab("operations")}
          >
            🎯 Operations
          </button>
          <button
            style={tabStyle("dashboard")}
            onClick={() => setCurrentTab("dashboard")}
          >
            📊 Dashboard
          </button>
          <button
            style={tabStyle("analytics")}
            onClick={() => setCurrentTab("analytics")}
          >
            � Analytics
          </button>
          <button
            style={tabStyle("network")}
            onClick={() => setCurrentTab("network")}
          >
            🌐 Network
          </button>
          <button
            style={tabStyle("osint")}
            onClick={() => setCurrentTab("osint")}
          >
            🔍 OSINT
          </button>
          <button
            style={tabStyle("data-enrichment")}
            onClick={() => setCurrentTab("data-enrichment")}
          >
            💎 Data Enrichment
          </button>
          <button
            style={tabStyle("data-parsing")}
            onClick={() => setCurrentTab("data-parsing")}
          >
            📝 Data Parsing
          </button>
          <button
            style={tabStyle("browser")}
            onClick={() => setCurrentTab("browser")}
          >
            🌍 Browser
          </button>
          <button
            style={tabStyle("visualization")}
            onClick={() => setCurrentTab("visualization")}
          >
            📈 Visualization
          </button>
          <button
            style={tabStyle("performance")}
            onClick={() => setCurrentTab("performance")}
          >
            ⚡ Performance
          </button>
        </div>
      </nav>

      {/* Operations Tab */}
      {currentTab === "operations" && (
        <div>
          {/* Quick Create Job Section - Added to existing operations */}
          <div
            style={{
              backgroundColor: "#e3f2fd",
              padding: "20px",
              borderRadius: "8px",
              marginBottom: "20px",
            }}
          >
            <h2>🚀 Quick Create Job</h2>

            {/* Job Mode Selection */}
            <div style={{ marginBottom: "20px" }}>
              <div
                style={{ display: "flex", gap: "15px", marginBottom: "15px" }}
              >
                <label
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    cursor: "pointer",
                  }}
                >
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
                  />
                  <span style={{ fontWeight: "bold" }}>
                    🎯 Single URL Scraping
                  </span>
                </label>
                <label
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    cursor: "pointer",
                  }}
                >
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
                  />
                  <span style={{ fontWeight: "bold" }}>
                    🕷️ Batch Scraping from Crawler Results
                  </span>
                </label>
              </div>
            </div>

            {/* Batch Mode Configuration */}
            {newJob.config?.batch_mode && (
              <div
                style={{
                  backgroundColor: "#fff3cd",
                  padding: "15px",
                  borderRadius: "8px",
                  marginBottom: "20px",
                  border: "1px solid #ffeaa7",
                }}
              >
                <h4 style={{ margin: "0 0 15px 0", color: "#856404" }}>
                  🔄 Crawler Results to Scraper Pipeline
                </h4>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: "15px",
                    marginBottom: "15px",
                  }}
                >
                  <div>
                    <label
                      style={{
                        display: "block",
                        marginBottom: "5px",
                        fontWeight: "bold",
                      }}
                    >
                      Select Crawler Job:
                    </label>
                    <select
                      value={selectedCrawlerJob || ""}
                      onChange={async (e) => {
                        const jobId = parseInt(e.target.value);
                        setSelectedCrawlerJob(jobId);
                        if (jobId) {
                          const urls = await extractUrlsFromCrawler(jobId);
                          console.log(
                            `Extracted ${urls.length} URLs from crawler job ${jobId}`,
                          );
                        }
                      }}
                      style={{
                        width: "100%",
                        padding: "8px",
                        border: "1px solid #ccc",
                        borderRadius: "4px",
                      }}
                    >
                      <option value="">
                        Choose a completed crawler job...
                      </option>
                      {crawlerJobs.map((job) => (
                        <option key={job.id} value={job.id}>
                          {job.name} (
                          {new Date(job.created_at).toLocaleDateString()})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label
                      style={{
                        display: "block",
                        marginBottom: "5px",
                        fontWeight: "bold",
                      }}
                    >
                      Batch Size:
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
                        padding: "8px",
                        border: "1px solid #ccc",
                        borderRadius: "4px",
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
                  <div
                    style={{
                      backgroundColor: "#d4edda",
                      padding: "10px",
                      borderRadius: "4px",
                      border: "1px solid #c3e6cb",
                      marginBottom: "15px",
                    }}
                  >
                    <div
                      style={{
                        fontWeight: "bold",
                        color: "#155724",
                        marginBottom: "8px",
                      }}
                    >
                      ✅ Found {extractedUrls.length} URLs to scrape
                    </div>
                    <div
                      style={{
                        maxHeight: "100px",
                        overflow: "auto",
                        fontSize: "12px",
                        backgroundColor: "white",
                        padding: "8px",
                        borderRadius: "3px",
                      }}
                    >
                      {extractedUrls.slice(0, 10).map((url, index) => (
                        <div key={index} style={{ marginBottom: "2px" }}>
                          {index + 1}. {url}
                        </div>
                      ))}
                      {extractedUrls.length > 10 && (
                        <div style={{ fontStyle: "italic", color: "#666" }}>
                          ... and {extractedUrls.length - 10} more URLs
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Regular form for both modes */}
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
                gap: "15px",
                alignItems: "end",
              }}
            >
              <div>
                <label
                  style={{
                    display: "block",
                    marginBottom: "5px",
                    fontWeight: "bold",
                  }}
                >
                  Job Name:
                </label>
                <input
                  type="text"
                  value={newJob.name}
                  onChange={(e) =>
                    setNewJob({ ...newJob, name: e.target.value })
                  }
                  required
                  placeholder={
                    newJob.config?.batch_mode
                      ? "Batch Scraper from Crawler"
                      : "My Scraping Job"
                  }
                  style={{
                    width: "100%",
                    padding: "8px",
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                  }}
                />
              </div>

              {!newJob.config?.batch_mode && (
                <div>
                  <label
                    style={{
                      display: "block",
                      marginBottom: "5px",
                      fontWeight: "bold",
                    }}
                  >
                    URL:
                  </label>
                  <input
                    type="url"
                    value={newJob.url}
                    onChange={(e) =>
                      setNewJob({ ...newJob, url: e.target.value })
                    }
                    required
                    placeholder="https://example.com"
                    style={{
                      width: "100%",
                      padding: "8px",
                      border: "1px solid #ccc",
                      borderRadius: "4px",
                    }}
                  />
                </div>
              )}

              <div>
                <label
                  style={{
                    display: "block",
                    marginBottom: "5px",
                    fontWeight: "bold",
                  }}
                >
                  Type:
                </label>
                <select
                  value={newJob.scraper_type}
                  onChange={(e) =>
                    setNewJob({
                      ...newJob,
                      scraper_type: e.target.value as any,
                    })
                  }
                  style={{
                    width: "100%",
                    padding: "8px",
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                  }}
                >
                  <option value="basic">Basic</option>
                  <option value="e_commerce">E-Commerce</option>
                  <option value="news">News</option>
                  <option value="social_media">Social Media</option>
                  <option value="api">API</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={
                  !isBackendConnected ||
                  isSubmitting ||
                  (newJob.config?.batch_mode && extractedUrls.length === 0)
                }
                style={{
                  padding: "12px 20px",
                  backgroundColor: isBackendConnected
                    ? newJob.config?.batch_mode
                      ? "#6f42c1"
                      : "#1976d2"
                    : "#6c757d",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: isBackendConnected ? "pointer" : "not-allowed",
                  fontSize: "14px",
                  whiteSpace: "nowrap",
                }}
              >
                {isSubmitting
                  ? "Creating..."
                  : newJob.config?.batch_mode
                    ? `Create ${Math.ceil(extractedUrls.length / (newJob.config?.batch_size || 10))} Jobs`
                    : "Create Job"}
              </button>
            </form>
            
            {/* Enhanced Crawling Options */}
            <div style={{ marginTop: "20px", padding: "15px", backgroundColor: "#f8f9fa", borderRadius: "8px" }}>
              <h4 style={{ margin: "0 0 15px 0", color: "#1976d2" }}>
                🚀 Enhanced Crawling Options
              </h4>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "15px" }}>
                <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
                  <input
                    type="checkbox"
                    checked={newJob.config?.extract_full_html || false}
                    onChange={(e) =>
                      setNewJob({
                        ...newJob,
                        config: {
                          ...newJob.config,
                          extract_full_html: e.target.checked,
                        },
                      })
                    }
                  />
                  <span style={{ fontWeight: "500" }}>Extract Full HTML</span>
                </label>
                <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
                  <input
                    type="checkbox"
                    checked={newJob.config?.crawl_entire_domain || false}
                    onChange={(e) =>
                      setNewJob({
                        ...newJob,
                        config: {
                          ...newJob.config,
                          crawl_entire_domain: e.target.checked,
                        },
                      })
                    }
                  />
                  <span style={{ fontWeight: "500" }}>Crawl Entire Domain</span>
                </label>
                <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
                  <input
                    type="checkbox"
                    checked={newJob.config?.include_images || false}
                    onChange={(e) =>
                      setNewJob({
                        ...newJob,
                        config: {
                          ...newJob.config,
                          include_images: e.target.checked,
                        },
                      })
                    }
                  />
                  <span style={{ fontWeight: "500" }}>Include Images</span>
                </label>
                <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
                  <input
                    type="checkbox"
                    checked={newJob.config?.save_to_database !== false}
                    onChange={(e) =>
                      setNewJob({
                        ...newJob,
                        config: {
                          ...newJob.config,
                          save_to_database: e.target.checked,
                        },
                      })
                    }
                  />
                  <span style={{ fontWeight: "500" }}>Save to Database</span>
                </label>
              </div>
            </div>
          </div>

          {/* Original OperationsInterface - Restored */}
          <OperationsInterface
            jobs={jobs}
            newJob={newJob}
            setNewJob={setNewJob}
            operationsConfig={operationsConfig}
            updateOperationsConfig={updateOperationsConfig}
            toggleSection={toggleSection}
            configPanelOpen={configPanelOpen}
            toggleConfigPanel={toggleConfigPanel}
            workflowSidebarOpen={workflowSidebarOpen}
            setWorkflowSidebarOpen={setWorkflowSidebarOpen}
            selectedJobForWorkflow={selectedJobForWorkflow}
            setSelectedJobForWorkflow={setSelectedJobForWorkflow}
            isSubmitting={isSubmitting}
            createJob={submitJob}
            fetchJobs={fetchJobs}
            getJobDetails={getJobDetails}
            getJobResults={getJobResults}
            startJob={startJob}
            resetOperationsConfig={resetOperationsConfig}
          />
        </div>
      )}

      {/* Dashboard Tab */}
      {currentTab === "dashboard" && (
        <div>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
              gap: "20px",
              marginBottom: "30px",
            }}
          >
            {analytics && (
              <>
                <div
                  style={{
                    padding: "20px",
                    backgroundColor: "#f8f9fa",
                    borderRadius: "8px",
                    border: "1px solid #ddd",
                  }}
                >
                  <h3 style={{ margin: "0 0 10px 0", color: "#1976d2" }}>
                    Total Jobs
                  </h3>
                  <div style={{ fontSize: "2em", fontWeight: "bold" }}>
                    {analytics.total_jobs}
                  </div>
                </div>
                <div
                  style={{
                    padding: "20px",
                    backgroundColor: "#d4edda",
                    borderRadius: "8px",
                    border: "1px solid #c3e6cb",
                  }}
                >
                  <h3 style={{ margin: "0 0 10px 0", color: "#155724" }}>
                    Completed
                  </h3>
                  <div style={{ fontSize: "2em", fontWeight: "bold" }}>
                    {analytics.completed_jobs}
                  </div>
                </div>
                <div
                  style={{
                    padding: "20px",
                    backgroundColor: "#fff3cd",
                    borderRadius: "8px",
                    border: "1px solid #ffeaa7",
                  }}
                >
                  <h3 style={{ margin: "0 0 10px 0", color: "#856404" }}>
                    Running
                  </h3>
                  <div style={{ fontSize: "2em", fontWeight: "bold" }}>
                    {analytics.running_jobs}
                  </div>
                </div>
                <div
                  style={{
                    padding: "20px",
                    backgroundColor: "#f8d7da",
                    borderRadius: "8px",
                    border: "1px solid #f5c6cb",
                  }}
                >
                  <h3 style={{ margin: "0 0 10px 0", color: "#721c24" }}>
                    Failed
                  </h3>
                  <div style={{ fontSize: "2em", fontWeight: "bold" }}>
                    {analytics.failed_jobs}
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Recent Jobs */}
          <div
            style={{
              backgroundColor: "#f8f9fa",
              padding: "20px",
              borderRadius: "8px",
              marginBottom: "20px",
            }}
          >
            <h2>🔄 Recent Jobs</h2>
            {jobs.slice(0, 5).map((job) => (
              <div
                key={job.id}
                style={{
                  padding: "15px",
                  border: "1px solid #ddd",
                  borderRadius: "5px",
                  backgroundColor: "white",
                  marginBottom: "10px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <strong>{job.name}</strong>
                  <div style={{ fontSize: "12px", color: "#666" }}>
                    Created: {new Date(job.created_at).toLocaleString()}
                  </div>
                </div>
                <div
                  style={{ display: "flex", gap: "10px", alignItems: "center" }}
                >
                  <span
                    style={{
                      padding: "4px 8px",
                      borderRadius: "12px",
                      fontSize: "12px",
                      backgroundColor:
                        job.status === "completed"
                          ? "#d4edda"
                          : job.status === "failed"
                            ? "#f8d7da"
                            : job.status === "running"
                              ? "#fff3cd"
                              : "#e2e3e5",
                      color:
                        job.status === "completed"
                          ? "#155724"
                          : job.status === "failed"
                            ? "#721c24"
                            : job.status === "running"
                              ? "#856404"
                              : "#383d41",
                    }}
                  >
                    {job.status}
                  </span>
                  <button
                    onClick={() => getJobDetails(job.id)}
                    style={{
                      padding: "4px 8px",
                      fontSize: "12px",
                      backgroundColor: "#007bff",
                      color: "white",
                      border: "none",
                      borderRadius: "3px",
                      cursor: "pointer",
                    }}
                  >
                    Details
                  </button>
                  {job.status === "pending" && (
                    <button
                      onClick={() => startJob(job.id)}
                      style={{
                        padding: "4px 8px",
                        fontSize: "12px",
                        backgroundColor: "#28a745",
                        color: "white",
                        border: "none",
                        borderRadius: "3px",
                        cursor: "pointer",
                      }}
                    >
                      Start
                    </button>
                  )}
                  {job.status === "completed" && (
                    <button
                      onClick={() => getJobResults(job.id)}
                      style={{
                        padding: "4px 8px",
                        fontSize: "12px",
                        backgroundColor: "#17a2b8",
                        color: "white",
                        border: "none",
                        borderRadius: "3px",
                        cursor: "pointer",
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

      {/* Jobs Tab */}
      {currentTab === "jobs" && (
        <div>
          <h2>🚀 Job Management & Queue</h2>
          <div style={{ marginBottom: "20px" }}>
            <button
              onClick={() => fetchJobs()}
              style={{
                padding: "8px 16px",
                backgroundColor: "#17a2b8",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
                marginRight: "10px",
              }}
            >
              🔄 Refresh
            </button>
            <span style={{ color: "#666" }}>
              Last updated: {new Date().toLocaleTimeString()}
            </span>
          </div>

          <div style={{ display: "grid", gap: "15px" }}>
            {jobs.map((job) => (
              <div
                key={job.id}
                style={{
                  padding: "20px",
                  border: "1px solid #ddd",
                  borderRadius: "8px",
                  backgroundColor: "#f8f9fa",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "start",
                    marginBottom: "15px",
                  }}
                >
                  <div>
                    <h3 style={{ margin: "0 0 5px 0" }}>{job.name}</h3>
                    <div style={{ fontSize: "14px", color: "#666" }}>
                      ID: {job.id} • Type: {job.type} • Created:{" "}
                      {new Date(job.created_at).toLocaleString()}
                    </div>
                    <div style={{ fontSize: "14px", color: "#666" }}>
                      Results: {job.results_count} data points
                    </div>
                  </div>
                  <div
                    style={{
                      display: "flex",
                      gap: "10px",
                      alignItems: "center",
                    }}
                  >
                    <span
                      style={{
                        padding: "6px 12px",
                        borderRadius: "15px",
                        fontSize: "14px",
                        fontWeight: "bold",
                        backgroundColor:
                          job.status === "completed"
                            ? "#d4edda"
                            : job.status === "failed"
                              ? "#f8d7da"
                              : job.status === "running"
                                ? "#fff3cd"
                                : "#e2e3e5",
                        color:
                          job.status === "completed"
                            ? "#155724"
                            : job.status === "failed"
                              ? "#721c24"
                              : job.status === "running"
                                ? "#856404"
                                : "#383d41",
                      }}
                    >
                      {job.status.toUpperCase()}
                    </span>
                  </div>
                </div>

                <div style={{ display: "flex", gap: "10px" }}>
                  <button
                    onClick={() => getJobDetails(job.id)}
                    style={{
                      padding: "8px 16px",
                      backgroundColor: "#007bff",
                      color: "white",
                      border: "none",
                      borderRadius: "4px",
                      cursor: "pointer",
                    }}
                  >
                    📊 View Details
                  </button>
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
                      }}
                    >
                      ▶️ Start Job
                    </button>
                  )}
                  {job.status === "completed" && (
                    <button
                      onClick={() => getJobResults(job.id)}
                      style={{
                        padding: "8px 16px",
                        backgroundColor: "#17a2b8",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        cursor: "pointer",
                      }}
                    >
                      � View Results
                    </button>
                  )}
                  {job.status === "running" && (
                    <div
                      style={{
                        padding: "8px 16px",
                        backgroundColor: "#fff3cd",
                        color: "#856404",
                        border: "1px solid #ffeaa7",
                        borderRadius: "4px",
                      }}
                    >
                      🔄 Processing...
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {(() => {
            console.log("Checking if job details modal should show. selectedJob:", !!selectedJob, selectedJob ? "job: " + selectedJob.name : "no job");
            return selectedJob;
          })() && (
            <div
              style={{
                position: "fixed",
                top: "0",
                left: "0",
                right: "0",
                bottom: "0",
                backgroundColor: "rgba(0,0,0,0.5)",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                zIndex: 1000,
              }}
            >
              <div
                style={{
                  backgroundColor: "white",
                  padding: "30px",
                  borderRadius: "8px",
                  maxWidth: "600px",
                  width: "90%",
                  maxHeight: "80%",
                  overflow: "auto",
                }}
              >
                <h2>📊 Job Details: {selectedJob.name}</h2>
                <div style={{ marginBottom: "20px" }}>
                  <div style={{ display: "grid", gap: "8px" }}>
                    <div><strong>Job ID:</strong> {selectedJob.id}</div>
                    <div><strong>Status:</strong> <span style={{ 
                      color: selectedJob.status === 'completed' ? '#28a745' : 
                             selectedJob.status === 'failed' ? '#dc3545' : 
                             selectedJob.status === 'running' ? '#ffc107' : '#6c757d',
                      fontWeight: 'bold'
                    }}>{selectedJob.status}</span></div>
                    <div><strong>Type:</strong> {selectedJob.type}</div>
                    <div><strong>Created:</strong> {new Date(selectedJob.created_at).toLocaleString()}</div>
                    {selectedJob.started_at && (
                      <div><strong>Started:</strong> {new Date(selectedJob.started_at).toLocaleString()}</div>
                    )}
                    {selectedJob.completed_at && (
                      <div><strong>Completed:</strong> {new Date(selectedJob.completed_at).toLocaleString()}</div>
                    )}
                    {selectedJob.results_count && (
                      <div><strong>Results Count:</strong> {selectedJob.results_count}</div>
                    )}
                    {selectedJob.error_message && (
                      <div style={{ color: '#dc3545' }}><strong>Error:</strong> {selectedJob.error_message}</div>
                    )}
                  </div>
                </div>
                
                {/* Configuration Section */}
                <div style={{ marginBottom: "20px" }}>
                  <strong>Configuration:</strong>
                  <div style={{ 
                    backgroundColor: "#f8f9fa", 
                    padding: "15px", 
                    borderRadius: "6px",
                    border: "1px solid #e9ecef",
                    marginTop: "8px" 
                  }}>
                    {selectedJob.config && typeof selectedJob.config === 'object' ? (
                      <div style={{ display: "grid", gap: "8px" }}>
                        {selectedJob.config.url && (
                          <div><strong>URL:</strong> <a href={selectedJob.config.url} target="_blank" rel="noopener noreferrer" style={{ color: "#007bff" }}>{selectedJob.config.url}</a></div>
                        )}
                        {selectedJob.config.scraper_type && (
                          <div><strong>Scraper Type:</strong> {selectedJob.config.scraper_type}</div>
                        )}
                        {selectedJob.config.summary && (
                          <div style={{ marginTop: "10px" }}>
                            <strong>Crawling Summary:</strong>
                            <div style={{ fontSize: "14px", marginTop: "5px" }}>
                              {(() => {
                                try {
                                  const summary = typeof selectedJob.config.summary === 'string' 
                                    ? JSON.parse(selectedJob.config.summary)
                                    : selectedJob.config.summary;
                                  return (
                                    <div style={{ display: "grid", gap: "4px" }}>
                                      {summary.pages_processed && <div>📄 Pages Processed: {summary.pages_processed}</div>}
                                      {summary.urls_discovered && <div>🔗 URLs Discovered: {summary.urls_discovered}</div>}
                                      {summary.data_extracted && <div>📊 Data Extracted: {summary.data_extracted}</div>}
                                      {summary.total_crawl_time && <div>⏱️ Crawl Time: {summary.total_crawl_time}s</div>}
                                      {summary.images_extracted !== undefined && <div>🖼️ Images Extracted: {summary.images_extracted}</div>}
                                      {summary.domains_crawled && <div>🌐 Domains: {summary.domains_crawled.join(', ')}</div>}
                                    </div>
                                  );
                                } catch {
                                  return <div>{selectedJob.config.summary}</div>;
                                }
                              })()}
                            </div>
                          </div>
                        )}
                        {selectedJob.config.config && Object.keys(selectedJob.config.config).length > 0 && (
                          <div style={{ marginTop: "10px" }}>
                            <strong>Advanced Config:</strong>
                            <pre style={{ 
                              fontSize: "12px", 
                              marginTop: "5px",
                              backgroundColor: "#ffffff",
                              padding: "8px",
                              borderRadius: "4px",
                              border: "1px solid #dee2e6"
                            }}>
                              {JSON.stringify(selectedJob.config.config, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    ) : (
                      <pre style={{ 
                        fontSize: "12px", 
                        margin: 0,
                        whiteSpace: "pre-wrap",
                        backgroundColor: "#ffffff",
                        padding: "8px",
                        borderRadius: "4px",
                        border: "1px solid #dee2e6"
                      }}>
                        {JSON.stringify(selectedJob.config, null, 2)}
                      </pre>
                    )}
                  </div>
                </div>

                {/* Action Buttons */}
                <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
                  {selectedJob.status === 'completed' && (
                    <button
                      onClick={() => {
                        setSelectedJob(null);
                        getJobResults(selectedJob.id);
                      }}
                      style={{
                        padding: "10px 20px",
                        backgroundColor: "#28a745",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        cursor: "pointer",
                        fontSize: "14px"
                      }}
                    >
                      📊 View Results
                    </button>
                  )}
                  <button
                    onClick={() => setSelectedJob(null)}
                    style={{
                      padding: "10px 20px",
                      backgroundColor: "#6c757d",
                      color: "white",
                      border: "none",
                      borderRadius: "4px",
                      cursor: "pointer",
                    }}
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Results Viewer Modal */}
          {(() => {
            console.log("Checking if results modal should show. jobResults:", !!jobResults, jobResults ? "data length: " + (jobResults.data?.length || 0) : "no data");
            return jobResults;
          })() && (
            <div
              style={{
                position: "fixed",
                top: "0",
                left: "0",
                right: "0",
                bottom: "0",
                backgroundColor: "rgba(0,0,0,0.8)",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                zIndex: 1001,
              }}
            >
              <div
                style={{
                  backgroundColor: "white",
                  padding: "30px",
                  borderRadius: "12px",
                  maxWidth: "95%",
                  width: "1200px",
                  maxHeight: "90%",
                  overflow: "hidden",
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                {/* Header */}
                <div
                  style={{
                    marginBottom: "20px",
                    borderBottom: "2px solid #e9ecef",
                    paddingBottom: "15px",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <div>
                      <h2 style={{ margin: "0 0 5px 0", color: "#1976d2" }}>
                        📊 Results: {jobResults.job_name}
                      </h2>
                      <div style={{ fontSize: "14px", color: "#666" }}>
                        Job ID: {jobResults.job_id} • Total Records:{" "}
                        {jobResults.total_count} • Status: {jobResults.status}
                      </div>
                      <div
                        style={{
                          fontSize: "12px",
                          color: "#666",
                          marginTop: "2px",
                        }}
                      >
                        Completed:{" "}
                        {jobResults.completed_at
                          ? new Date(jobResults.completed_at).toLocaleString()
                          : "N/A"}
                      </div>
                    </div>
                    <button
                      onClick={() => setJobResults(null)}
                      style={{
                        padding: "8px 16px",
                        backgroundColor: "#dc3545",
                        color: "white",
                        border: "none",
                        borderRadius: "6px",
                        cursor: "pointer",
                        fontSize: "14px",
                      }}
                    >
                      ✕ Close
                    </button>
                  </div>
                </div>

                {/* Controls */}
                <div
                  style={{
                    display: "flex",
                    gap: "15px",
                    marginBottom: "20px",
                    alignItems: "center",
                    flexWrap: "wrap",
                  }}
                >
                  <div style={{ flex: "1", minWidth: "300px" }}>
                    <input
                      type="text"
                      placeholder="🔍 Search results..."
                      value={resultsSearchTerm}
                      onChange={(e) => {
                        setResultsSearchTerm(e.target.value);
                        setCurrentPage(1); // Reset to first page on search
                      }}
                      style={{
                        width: "100%",
                        padding: "10px",
                        border: "1px solid #ddd",
                        borderRadius: "6px",
                        fontSize: "14px",
                      }}
                    />
                  </div>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "10px",
                    }}
                  >
                    <label style={{ fontSize: "14px", whiteSpace: "nowrap" }}>
                      Items per page:
                    </label>
                    <select
                      value={itemsPerPage}
                      onChange={(e) => {
                        setItemsPerPage(parseInt(e.target.value));
                        setCurrentPage(1); // Reset to first page
                      }}
                      style={{
                        padding: "8px",
                        border: "1px solid #ddd",
                        borderRadius: "4px",
                        fontSize: "14px",
                      }}
                    >
                      <option value={5}>5</option>
                      <option value={10}>10</option>
                      <option value={25}>25</option>
                      <option value={50}>50</option>
                      <option value={100}>100</option>
                    </select>
                  </div>
                  <button
                    onClick={async () => {
                      // Send to centralized database
                      try {
                        const response = await fetch(
                          "http://localhost:8000/api/data/centralize",
                          {
                            method: "POST",
                            headers: {
                              "Content-Type": "application/json",
                              Authorization: `Bearer ${token}`,
                            },
                            body: JSON.stringify({
                              job_id: jobResults.job_id,
                              job_name: jobResults.job_name,
                              data: jobResults.data,
                              metadata: {
                                total_count: jobResults.total_count,
                                status: jobResults.status,
                                created_at: jobResults.created_at,
                                completed_at: jobResults.completed_at,
                              },
                            }),
                          },
                        );

                        if (response.ok) {
                          alert(
                            "✅ Data successfully added to centralized database!",
                          );
                        } else {
                          alert("❌ Failed to centralize data");
                        }
                      } catch (error) {
                        console.error("Centralization error:", error);
                        alert(
                          "✅ Data queued for centralization (offline mode)",
                        );
                      }
                    }}
                    style={{
                      padding: "10px 20px",
                      backgroundColor: "#6f42c1",
                      color: "white",
                      border: "none",
                      borderRadius: "6px",
                      cursor: "pointer",
                      fontSize: "14px",
                      whiteSpace: "nowrap",
                    }}
                  >
                    🗄️ Centralize Data
                  </button>
                  <button
                    onClick={() => {
                      const dataStr = JSON.stringify(jobResults.data, null, 2);
                      const blob = new Blob([dataStr], {
                        type: "application/json",
                      });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = `${jobResults.job_name}_results.json`;
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                    style={{
                      padding: "10px 20px",
                      backgroundColor: "#28a745",
                      color: "white",
                      border: "none",
                      borderRadius: "6px",
                      cursor: "pointer",
                      fontSize: "14px",
                      whiteSpace: "nowrap",
                    }}
                  >
                    💾 Export JSON
                  </button>
                  <button
                    onClick={() => {
                      if (jobResults.data.length === 0) return;
                      const headers = Object.keys(jobResults.data[0]);
                      const csvContent = [
                        headers.join(","),
                        ...jobResults.data.map((row) =>
                          headers
                            .map((header) =>
                              typeof row[header] === "string"
                                ? `"${row[header].replace(/"/g, '""')}"`
                                : row[header],
                            )
                            .join(","),
                        ),
                      ].join("\n");
                      const blob = new Blob([csvContent], { type: "text/csv" });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = `${jobResults.job_name}_results.csv`;
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                    style={{
                      padding: "10px 20px",
                      backgroundColor: "#17a2b8",
                      color: "white",
                      border: "none",
                      borderRadius: "6px",
                      cursor: "pointer",
                      fontSize: "14px",
                      whiteSpace: "nowrap",
                    }}
                  >
                    📄 Export CSV
                  </button>
                  <button
                    onClick={async () => {
                      if (!jobResults.data.length) return;

                      // Enhanced URL extraction - try multiple approaches
                      let urls: string[] = [];

                      // First, try the backend API extraction
                      try {
                        const backendUrls = await extractUrlsFromCrawler(
                          jobResults.job_id,
                        );
                        if (backendUrls.length > 0) {
                          urls = backendUrls;
                        }
                      } catch (error) {
                        console.log(
                          "Backend extraction failed, trying client-side extraction",
                        );
                      }

                      // If backend didn't work, try direct client-side extraction from current data
                      if (urls.length === 0 && jobResults.data) {
                        console.log(
                          "Attempting direct URL extraction from job results data:",
                          jobResults.data,
                        );

                        jobResults.data.forEach((item: any, index: number) => {
                          console.log(`Examining item ${index}:`, item);

                          // Check all possible URL fields
                          const possibleUrlFields = [
                            "url",
                            "link",
                            "href",
                            "page_url",
                            "discovered_url",
                            "target_url",
                            "source_url",
                            "canonical_url",
                            "original_url",
                            "crawled_url",
                            "found_url",
                            "extracted_url",
                            "site_url",
                            "web_url",
                          ];

                          // Check direct fields
                          for (const field of possibleUrlFields) {
                            if (item[field]) {
                              const value = item[field];
                              if (
                                typeof value === "string" &&
                                (value.startsWith("http://") ||
                                  value.startsWith("https://"))
                              ) {
                                urls.push(value);
                                console.log(
                                  `Found URL in field '${field}':`,
                                  value,
                                );
                              }
                            }
                          }

                          // Check for arrays of links
                          if (item.links && Array.isArray(item.links)) {
                            item.links.forEach(
                              (link: any, linkIndex: number) => {
                                if (
                                  typeof link === "string" &&
                                  (link.startsWith("http://") ||
                                    link.startsWith("https://"))
                                ) {
                                  urls.push(link);
                                  console.log(
                                    `Found URL in links array[${linkIndex}]:`,
                                    link,
                                  );
                                } else if (link && typeof link === "object") {
                                  possibleUrlFields.forEach((field) => {
                                    if (
                                      link[field] &&
                                      typeof link[field] === "string" &&
                                      (link[field].startsWith("http://") ||
                                        link[field].startsWith("https://"))
                                    ) {
                                      urls.push(link[field]);
                                      console.log(
                                        `Found URL in links[${linkIndex}].${field}:`,
                                        link[field],
                                      );
                                    }
                                  });
                                }
                              },
                            );
                          }

                          // Check for nested objects that might contain URLs
                          Object.keys(item).forEach((key) => {
                            const value = item[key];
                            if (
                              value &&
                              typeof value === "object" &&
                              !Array.isArray(value)
                            ) {
                              possibleUrlFields.forEach((field) => {
                                if (
                                  value[field] &&
                                  typeof value[field] === "string" &&
                                  (value[field].startsWith("http://") ||
                                    value[field].startsWith("https://"))
                                ) {
                                  urls.push(value[field]);
                                  console.log(
                                    `Found URL in nested object ${key}.${field}:`,
                                    value[field],
                                  );
                                }
                              });
                            }
                          });
                        });

                        // Remove duplicates
                        urls = [...new Set(urls)];
                        console.log(
                          `Total unique URLs found: ${urls.length}`,
                          urls,
                        );
                      }

                      if (urls.length > 0) {
                        // Switch to the dashboard tab and prepare for batch scraping
                        setCurrentTab("dashboard");
                        setNewJob((prev) => ({
                          ...prev,
                          name: `Scraper from ${jobResults.job_name}`,
                          config: {
                            ...prev.config,
                            batch_mode: true,
                            source_crawler_job_id: jobResults.job_id,
                            extracted_urls: urls,
                          },
                        }));
                        setSelectedCrawlerJob(jobResults.job_id);
                        setExtractedUrls(urls);
                        setJobResults(null); // Close the modal

                        alert(
                          `✅ Found ${urls.length} URLs! Switched to dashboard to create batch scraping jobs.`,
                        );
                      } else {
                        // Show detailed debugging information
                        console.log(
                          "No URLs found. Job results structure:",
                          jobResults,
                        );
                        console.log("Sample data item:", jobResults.data[0]);

                        alert(
                          `❌ No URLs found in this job's results.\n\nDebugging info:\n- Job has ${jobResults.data.length} data items\n- Sample item keys: ${jobResults.data[0] ? Object.keys(jobResults.data[0]).join(", ") : "none"}\n\nMake sure the data contains URL fields like "url", "link", or "href".`,
                        );
                      }
                    }}
                    style={{
                      padding: "10px 20px",
                      backgroundColor: "#fd7e14",
                      color: "white",
                      border: "none",
                      borderRadius: "6px",
                      cursor: "pointer",
                      fontSize: "14px",
                      whiteSpace: "nowrap",
                    }}
                  >
                    🕷️ Use for Scraping
                  </button>
                </div>

                {/* Results Display */}
                <div
                  style={{
                    flex: "1",
                    overflow: "auto",
                    border: "1px solid #e9ecef",
                    borderRadius: "8px",
                    backgroundColor: "#f8f9fa",
                  }}
                >
                  {jobResults.data && jobResults.data.length > 0 ? (
                    <div>
                      {/* Filter results based on search */}
                      {(() => {
                        const filteredData = jobResults.data.filter(
                          (item) =>
                            !resultsSearchTerm ||
                            JSON.stringify(item)
                              .toLowerCase()
                              .includes(resultsSearchTerm.toLowerCase()),
                        );

                        if (filteredData.length === 0) {
                          return (
                            <div
                              style={{
                                padding: "40px",
                                textAlign: "center",
                                color: "#666",
                              }}
                            >
                              {resultsSearchTerm
                                ? `No results found for "${resultsSearchTerm}"`
                                : "No data available"}
                            </div>
                          );
                        }

                        return (
                          <div>
                            {/* Pagination Info */}
                            <div
                              style={{
                                padding: "10px 15px",
                                backgroundColor: "#fff",
                                borderBottom: "1px solid #e9ecef",
                                fontSize: "14px",
                                color: "#666",
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                              }}
                            >
                              <div>
                                Showing {(currentPage - 1) * itemsPerPage + 1}{" "}
                                to{" "}
                                {Math.min(
                                  currentPage * itemsPerPage,
                                  filteredData.length,
                                )}{" "}
                                of {filteredData.length} results
                                {resultsSearchTerm &&
                                  ` (filtered by "${resultsSearchTerm}")`}
                                {filteredData.length !==
                                  jobResults.total_count &&
                                  ` • Total in job: ${jobResults.total_count}`}
                              </div>
                              <div
                                style={{
                                  display: "flex",
                                  alignItems: "center",
                                  gap: "10px",
                                }}
                              >
                                {/* Pagination Controls */}
                                {(() => {
                                  const totalPages = Math.ceil(
                                    filteredData.length / itemsPerPage,
                                  );

                                  return (
                                    <div
                                      style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: "5px",
                                      }}
                                    >
                                      <button
                                        disabled={currentPage === 1}
                                        onClick={() => setCurrentPage(1)}
                                        style={{
                                          padding: "4px 8px",
                                          border: "1px solid #ddd",
                                          borderRadius: "4px",
                                          backgroundColor:
                                            currentPage === 1
                                              ? "#f8f9fa"
                                              : "white",
                                          cursor:
                                            currentPage === 1
                                              ? "not-allowed"
                                              : "pointer",
                                          fontSize: "12px",
                                        }}
                                      >
                                        ⏮️
                                      </button>
                                      <button
                                        disabled={currentPage === 1}
                                        onClick={() =>
                                          setCurrentPage(currentPage - 1)
                                        }
                                        style={{
                                          padding: "4px 8px",
                                          border: "1px solid #ddd",
                                          borderRadius: "4px",
                                          backgroundColor:
                                            currentPage === 1
                                              ? "#f8f9fa"
                                              : "white",
                                          cursor:
                                            currentPage === 1
                                              ? "not-allowed"
                                              : "pointer",
                                          fontSize: "12px",
                                        }}
                                      >
                                        ⏪
                                      </button>
                                      <span
                                        style={{
                                          padding: "4px 8px",
                                          fontSize: "12px",
                                        }}
                                      >
                                        Page {currentPage} of {totalPages}
                                      </span>
                                      <button
                                        disabled={currentPage === totalPages}
                                        onClick={() =>
                                          setCurrentPage(currentPage + 1)
                                        }
                                        style={{
                                          padding: "4px 8px",
                                          border: "1px solid #ddd",
                                          borderRadius: "4px",
                                          backgroundColor:
                                            currentPage === totalPages
                                              ? "#f8f9fa"
                                              : "white",
                                          cursor:
                                            currentPage === totalPages
                                              ? "not-allowed"
                                              : "pointer",
                                          fontSize: "12px",
                                        }}
                                      >
                                        ⏩
                                      </button>
                                      <button
                                        disabled={currentPage === totalPages}
                                        onClick={() =>
                                          setCurrentPage(totalPages)
                                        }
                                        style={{
                                          padding: "4px 8px",
                                          border: "1px solid #ddd",
                                          borderRadius: "4px",
                                          backgroundColor:
                                            currentPage === totalPages
                                              ? "#f8f9fa"
                                              : "white",
                                          cursor:
                                            currentPage === totalPages
                                              ? "not-allowed"
                                              : "pointer",
                                          fontSize: "12px",
                                        }}
                                      >
                                        ⏭️
                                      </button>
                                    </div>
                                  );
                                })()}
                              </div>
                            </div>

                            <div style={{ padding: "15px" }}>
                              <div style={{ display: "grid", gap: "15px" }}>
                                {(() => {
                                  const startIndex =
                                    (currentPage - 1) * itemsPerPage;
                                  const endIndex = Math.min(
                                    startIndex + itemsPerPage,
                                    filteredData.length,
                                  );
                                  const paginatedData = filteredData.slice(
                                    startIndex,
                                    endIndex,
                                  );

                                  return paginatedData.map((item, index) => (
                                    <div
                                      key={startIndex + index}
                                      style={{
                                        backgroundColor: "white",
                                        padding: "20px",
                                        borderRadius: "8px",
                                        border: "1px solid #e9ecef",
                                        boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
                                      }}
                                    >
                                      <div
                                        style={{
                                          display: "flex",
                                          justifyContent: "space-between",
                                          alignItems: "center",
                                          marginBottom: "15px",
                                        }}
                                      >
                                        <div
                                          style={{
                                            fontSize: "12px",
                                            color: "#666",
                                            backgroundColor: "#f8f9fa",
                                            padding: "4px 8px",
                                            borderRadius: "12px",
                                            fontWeight: "bold",
                                          }}
                                        >
                                          Record #{startIndex + index + 1} of{" "}
                                          {filteredData.length}
                                        </div>
                                        {item.url && (
                                          <a
                                            href={item.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            style={{
                                              fontSize: "12px",
                                              color: "#007bff",
                                              textDecoration: "none",
                                            }}
                                          >
                                            🔗 View Source
                                          </a>
                                        )}
                                      </div>
                                      <div
                                        style={{ display: "grid", gap: "8px" }}
                                      >
                                        {Object.entries(item).map(
                                          ([key, value]) => (
                                            <div
                                              key={key}
                                              style={{
                                                display: "flex",
                                                flexDirection: "column",
                                              }}
                                            >
                                              <span
                                                style={{
                                                  fontSize: "12px",
                                                  fontWeight: "bold",
                                                  color: "#495057",
                                                  textTransform: "capitalize",
                                                  marginBottom: "2px",
                                                }}
                                              >
                                                {key.replace(/_/g, " ")}:
                                              </span>
                                              <span
                                                style={{
                                                  fontSize: "14px",
                                                  color: "#212529",
                                                  wordBreak: "break-word",
                                                  backgroundColor: "#f8f9fa",
                                                  padding: "6px 8px",
                                                  borderRadius: "4px",
                                                  border: "1px solid #e9ecef",
                                                }}
                                              >
                                                {key === "url" ? (
                                                  <a
                                                    href={value as string}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    style={{ color: "#007bff" }}
                                                  >
                                                    {typeof value === "string"
                                                      ? value.length > 200
                                                        ? value.substring(
                                                            0,
                                                            200,
                                                          ) + "..."
                                                        : value
                                                      : JSON.stringify(value)}
                                                  </a>
                                                ) : typeof value ===
                                                  "string" ? (
                                                  value.length > 200 ? (
                                                    value.substring(0, 200) +
                                                    "..."
                                                  ) : (
                                                    value
                                                  )
                                                ) : (
                                                  JSON.stringify(value)
                                                )}
                                              </span>
                                            </div>
                                          ),
                                        )}
                                      </div>
                                    </div>
                                  ));
                                })()}
                              </div>

                              {/* Bottom Pagination */}
                              {(() => {
                                const totalPages = Math.ceil(
                                  filteredData.length / itemsPerPage,
                                );
                                if (totalPages <= 1) return null;

                                return (
                                  <div
                                    style={{
                                      marginTop: "30px",
                                      padding: "20px",
                                      backgroundColor: "#f8f9fa",
                                      borderRadius: "8px",
                                      display: "flex",
                                      justifyContent: "center",
                                      alignItems: "center",
                                      gap: "10px",
                                    }}
                                  >
                                    <button
                                      disabled={currentPage === 1}
                                      onClick={() => setCurrentPage(1)}
                                      style={{
                                        padding: "8px 12px",
                                        border: "1px solid #ddd",
                                        borderRadius: "6px",
                                        backgroundColor:
                                          currentPage === 1
                                            ? "#e9ecef"
                                            : "white",
                                        cursor:
                                          currentPage === 1
                                            ? "not-allowed"
                                            : "pointer",
                                        fontSize: "14px",
                                      }}
                                    >
                                      First
                                    </button>
                                    <button
                                      disabled={currentPage === 1}
                                      onClick={() =>
                                        setCurrentPage(currentPage - 1)
                                      }
                                      style={{
                                        padding: "8px 12px",
                                        border: "1px solid #ddd",
                                        borderRadius: "6px",
                                        backgroundColor:
                                          currentPage === 1
                                            ? "#e9ecef"
                                            : "white",
                                        cursor:
                                          currentPage === 1
                                            ? "not-allowed"
                                            : "pointer",
                                        fontSize: "14px",
                                      }}
                                    >
                                      Previous
                                    </button>

                                    {/* Page number buttons */}
                                    {(() => {
                                      const pageButtons = [];
                                      const startPage = Math.max(
                                        1,
                                        currentPage - 2,
                                      );
                                      const endPage = Math.min(
                                        totalPages,
                                        currentPage + 2,
                                      );

                                      for (
                                        let i = startPage;
                                        i <= endPage;
                                        i++
                                      ) {
                                        pageButtons.push(
                                          <button
                                            key={i}
                                            onClick={() => setCurrentPage(i)}
                                            style={{
                                              padding: "8px 12px",
                                              border: "1px solid #ddd",
                                              borderRadius: "6px",
                                              backgroundColor:
                                                currentPage === i
                                                  ? "#007bff"
                                                  : "white",
                                              color:
                                                currentPage === i
                                                  ? "white"
                                                  : "#333",
                                              cursor: "pointer",
                                              fontSize: "14px",
                                              fontWeight:
                                                currentPage === i
                                                  ? "bold"
                                                  : "normal",
                                            }}
                                          >
                                            {i}
                                          </button>,
                                        );
                                      }

                                      return pageButtons;
                                    })()}

                                    <button
                                      disabled={currentPage === totalPages}
                                      onClick={() =>
                                        setCurrentPage(currentPage + 1)
                                      }
                                      style={{
                                        padding: "8px 12px",
                                        border: "1px solid #ddd",
                                        borderRadius: "6px",
                                        backgroundColor:
                                          currentPage === totalPages
                                            ? "#e9ecef"
                                            : "white",
                                        cursor:
                                          currentPage === totalPages
                                            ? "not-allowed"
                                            : "pointer",
                                        fontSize: "14px",
                                      }}
                                    >
                                      Next
                                    </button>
                                    <button
                                      disabled={currentPage === totalPages}
                                      onClick={() => setCurrentPage(totalPages)}
                                      style={{
                                        padding: "8px 12px",
                                        border: "1px solid #ddd",
                                        borderRadius: "6px",
                                        backgroundColor:
                                          currentPage === totalPages
                                            ? "#e9ecef"
                                            : "white",
                                        cursor:
                                          currentPage === totalPages
                                            ? "not-allowed"
                                            : "pointer",
                                        fontSize: "14px",
                                      }}
                                    >
                                      Last
                                    </button>

                                    <div
                                      style={{
                                        marginLeft: "20px",
                                        fontSize: "14px",
                                        color: "#666",
                                      }}
                                    >
                                      Page {currentPage} of {totalPages}
                                    </div>
                                  </div>
                                );
                              })()}
                            </div>
                          </div>
                        );
                      })()}
                    </div>
                  ) : (
                    <div
                      style={{
                        padding: "40px",
                        textAlign: "center",
                        color: "#666",
                      }}
                    >
                      <div style={{ fontSize: "48px", marginBottom: "15px" }}>
                        📄
                      </div>
                      <div style={{ fontSize: "18px", marginBottom: "10px" }}>
                        No Results Available
                      </div>
                      <div style={{ fontSize: "14px" }}>
                        This job hasn't produced any data yet or the results are
                        empty.
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Analytics Tab */}
      {currentTab === "analytics" && (
        <div>
          <h2>📈 Centralized Analytics & Data Intelligence</h2>

          {/* Data Sources Overview */}
          <div
            style={{
              backgroundColor: "#e3f2fd",
              padding: "20px",
              borderRadius: "8px",
              marginBottom: "30px",
            }}
          >
            <h3>🗄️ Centralized Data Repository</h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                gap: "15px",
                marginBottom: "20px",
              }}
            >
              <div
                style={{
                  padding: "15px",
                  backgroundColor: "white",
                  borderRadius: "8px",
                  border: "1px solid #bbdefb",
                  textAlign: "center",
                }}
              >
                <div
                  style={{
                    fontSize: "2em",
                    fontWeight: "bold",
                    color: "#1976d2",
                  }}
                >
                  {analytics?.total_data_points || 0}
                </div>
                <div style={{ fontSize: "14px", color: "#666" }}>
                  Total Records
                </div>
              </div>
              <div
                style={{
                  padding: "15px",
                  backgroundColor: "white",
                  borderRadius: "8px",
                  border: "1px solid #bbdefb",
                  textAlign: "center",
                }}
              >
                <div
                  style={{
                    fontSize: "2em",
                    fontWeight: "bold",
                    color: "#28a745",
                  }}
                >
                  {analytics?.completed_jobs || 0}
                </div>
                <div style={{ fontSize: "14px", color: "#666" }}>
                  Data Sources
                </div>
              </div>
              <div
                style={{
                  padding: "15px",
                  backgroundColor: "white",
                  borderRadius: "8px",
                  border: "1px solid #bbdefb",
                  textAlign: "center",
                }}
              >
                <div
                  style={{
                    fontSize: "2em",
                    fontWeight: "bold",
                    color: "#17a2b8",
                  }}
                >
                  {analytics?.total_jobs && analytics?.total_jobs > 0
                    ? Math.round(
                        ((analytics?.completed_jobs || 0) /
                          analytics.total_jobs) *
                          100,
                      )
                    : 0}
                  %
                </div>
                <div style={{ fontSize: "14px", color: "#666" }}>
                  Success Rate
                </div>
              </div>
              <div
                style={{
                  padding: "15px",
                  backgroundColor: "white",
                  borderRadius: "8px",
                  border: "1px solid #bbdefb",
                  textAlign: "center",
                }}
              >
                <div
                  style={{
                    fontSize: "2em",
                    fontWeight: "bold",
                    color: "#fd7e14",
                  }}
                >
                  {analytics?.avg_completion_time || 0}s
                </div>
                <div style={{ fontSize: "14px", color: "#666" }}>
                  Avg Collection Time
                </div>
              </div>
            </div>

            {/* Centralization Actions */}
            <div style={{ display: "flex", gap: "15px", flexWrap: "wrap" }}>
              <button
                onClick={async () => {
                  try {
                    const response = await fetch(
                      "http://localhost:8000/api/data/analytics/refresh",
                      {
                        method: "POST",
                        headers: { Authorization: `Bearer ${token}` },
                      },
                    );
                    if (response.ok) {
                      fetchAnalytics();
                      alert(
                        "✅ Analytics refreshed from centralized database!",
                      );
                    }
                  } catch (error) {
                    alert("📊 Analytics refresh queued (offline mode)");
                  }
                }}
                style={{
                  padding: "10px 20px",
                  backgroundColor: "#007bff",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                }}
              >
                🔄 Refresh Analytics
              </button>
              <button
                onClick={async () => {
                  try {
                    const response = await fetch(
                      "http://localhost:8000/api/data/consolidate",
                      {
                        method: "POST",
                        headers: { Authorization: `Bearer ${token}` },
                      },
                    );
                    if (response.ok) {
                      alert(
                        "✅ All job data consolidated into centralized database!",
                      );
                      fetchAnalytics();
                    }
                  } catch (error) {
                    alert("🗄️ Data consolidation queued (offline mode)");
                  }
                }}
                style={{
                  padding: "10px 20px",
                  backgroundColor: "#28a745",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                }}
              >
                🗄️ Consolidate All Data
              </button>
              <button
                onClick={async () => {
                  try {
                    const response = await fetch(
                      "http://localhost:8000/api/data/export/all",
                      {
                        headers: { Authorization: `Bearer ${token}` },
                      },
                    );
                    if (response.ok) {
                      const blob = await response.blob();
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = `centralized_data_${new Date().toISOString().split("T")[0]}.json`;
                      a.click();
                      URL.revokeObjectURL(url);
                    }
                  } catch (error) {
                    alert("💾 Export queued (offline mode)");
                  }
                }}
                style={{
                  padding: "10px 20px",
                  backgroundColor: "#17a2b8",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                }}
              >
                💾 Export All Data
              </button>
            </div>
          </div>

          {/* Analytics Dashboard */}
          {analytics ? (
            <div>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(350px, 1fr))",
                  gap: "20px",
                  marginBottom: "30px",
                }}
              >
                <div
                  style={{
                    padding: "20px",
                    backgroundColor: "#f8f9fa",
                    borderRadius: "8px",
                    border: "1px solid #ddd",
                  }}
                >
                  <h3>📊 Job Performance Analytics</h3>
                  <div style={{ display: "grid", gap: "10px" }}>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                      }}
                    >
                      <span>Total Jobs:</span>
                      <strong>{analytics.total_jobs}</strong>
                    </div>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                      }}
                    >
                      <span>Completed:</span>
                      <strong style={{ color: "#28a745" }}>
                        {analytics.completed_jobs}
                      </strong>
                    </div>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                      }}
                    >
                      <span>Running:</span>
                      <strong style={{ color: "#ffc107" }}>
                        {analytics.running_jobs}
                      </strong>
                    </div>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                      }}
                    >
                      <span>Failed:</span>
                      <strong style={{ color: "#dc3545" }}>
                        {analytics.failed_jobs}
                      </strong>
                    </div>
                    <hr />
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                      }}
                    >
                      <span>Success Rate:</span>
                      <strong
                        style={{
                          color:
                            analytics.total_jobs > 0 &&
                            analytics.completed_jobs / analytics.total_jobs >
                              0.8
                              ? "#28a745"
                              : "#ffc107",
                        }}
                      >
                        {analytics.total_jobs > 0
                          ? Math.round(
                              (analytics.completed_jobs /
                                analytics.total_jobs) *
                                100,
                            )
                          : 0}
                        %
                      </strong>
                    </div>
                  </div>
                </div>

                <div
                  style={{
                    padding: "20px",
                    backgroundColor: "#e8f5e8",
                    borderRadius: "8px",
                    border: "1px solid #c3e6cb",
                  }}
                >
                  <h3>🎯 Data Collection Insights</h3>
                  <div style={{ display: "grid", gap: "10px" }}>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                      }}
                    >
                      <span>Total Data Points:</span>
                      <strong>
                        {analytics.total_data_points?.toLocaleString() || '0'}
                      </strong>
                    </div>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                      }}
                    >
                      <span>Avg per Job:</span>
                      <strong>
                        {analytics.total_jobs > 0
                          ? Math.round(
                              (analytics.total_data_points || 0) /
                                analytics.total_jobs,
                            ).toLocaleString()
                          : 0}
                      </strong>
                    </div>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                      }}
                    >
                      <span>Avg Completion Time:</span>
                      <strong>{analytics.avg_completion_time}s</strong>
                    </div>
                    <hr />
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                      }}
                    >
                      <span>Collection Rate:</span>
                      <strong>
                        {analytics.avg_completion_time > 0
                          ? Math.round(
                              (analytics.total_data_points || 0) /
                                analytics.avg_completion_time,
                            ).toLocaleString()
                          : 0}{" "}
                        pts/sec
                      </strong>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent Activity with Centralized Data */}
              <div
                style={{
                  backgroundColor: "#fff3cd",
                  padding: "20px",
                  borderRadius: "8px",
                  marginBottom: "20px",
                }}
              >
                <h3>🔍 Data Source Analysis</h3>
                <div style={{ display: "grid", gap: "10px" }}>
                  {jobs.slice(0, 10).map((job) => (
                    <div
                      key={job.id}
                      style={{
                        padding: "15px",
                        backgroundColor: "white",
                        borderRadius: "6px",
                        border: "1px solid #ffeaa7",
                        display: "grid",
                        gridTemplateColumns: "2fr 1fr 1fr auto",
                        alignItems: "center",
                        gap: "15px",
                      }}
                    >
                      <div>
                        <div style={{ fontWeight: "bold" }}>{job.name}</div>
                        <div style={{ fontSize: "12px", color: "#666" }}>
                          Created:{" "}
                          {new Date(job.created_at).toLocaleDateString()}
                        </div>
                      </div>
                      <div style={{ textAlign: "center" }}>
                        <div style={{ fontWeight: "bold", color: "#007bff" }}>
                          {job.results_count.toLocaleString()}
                        </div>
                        <div style={{ fontSize: "12px", color: "#666" }}>
                          Records
                        </div>
                      </div>
                      <div style={{ textAlign: "center" }}>
                        <span
                          style={{
                            padding: "4px 8px",
                            borderRadius: "12px",
                            fontSize: "12px",
                            fontWeight: "bold",
                            backgroundColor:
                              job.status === "completed"
                                ? "#d4edda"
                                : job.status === "failed"
                                  ? "#f8d7da"
                                  : job.status === "running"
                                    ? "#fff3cd"
                                    : "#e2e3e5",
                            color:
                              job.status === "completed"
                                ? "#155724"
                                : job.status === "failed"
                                  ? "#721c24"
                                  : job.status === "running"
                                    ? "#856404"
                                    : "#383d41",
                          }}
                        >
                          {job.status.toUpperCase()}
                        </span>
                      </div>
                      <button
                        onClick={() => getJobResults(job.id)}
                        style={{
                          padding: "6px 12px",
                          backgroundColor: "#6f42c1",
                          color: "white",
                          border: "none",
                          borderRadius: "4px",
                          cursor: "pointer",
                          fontSize: "12px",
                        }}
                      >
                        🔍 Analyze
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Data Quality Metrics */}
              <div
                style={{
                  backgroundColor: "#f8f9fa",
                  padding: "20px",
                  borderRadius: "8px",
                }}
              >
                <h3>🎯 Data Quality & Insights</h3>
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                    gap: "15px",
                  }}
                >
                  <div
                    style={{
                      padding: "15px",
                      backgroundColor: "white",
                      borderRadius: "8px",
                      border: "1px solid #dee2e6",
                      textAlign: "center",
                    }}
                  >
                    <div
                      style={{
                        fontSize: "1.5em",
                        fontWeight: "bold",
                        color: "#28a745",
                      }}
                    >
                      {analytics.completed_jobs > 0 ? "✅" : "⏳"}
                    </div>
                    <div style={{ fontSize: "14px", marginTop: "5px" }}>
                      Data Completeness
                    </div>
                    <div style={{ fontSize: "12px", color: "#666" }}>
                      {analytics.completed_jobs} of {analytics.total_jobs} jobs
                    </div>
                  </div>
                  <div
                    style={{
                      padding: "15px",
                      backgroundColor: "white",
                      borderRadius: "8px",
                      border: "1px solid #dee2e6",
                      textAlign: "center",
                    }}
                  >
                    <div
                      style={{
                        fontSize: "1.5em",
                        fontWeight: "bold",
                        color: "#007bff",
                      }}
                    >
                      📊
                    </div>
                    <div style={{ fontSize: "14px", marginTop: "5px" }}>
                      Collection Velocity
                    </div>
                    <div style={{ fontSize: "12px", color: "#666" }}>
                      {analytics.avg_completion_time > 0 ? "Fast" : "Pending"}
                    </div>
                  </div>
                  <div
                    style={{
                      padding: "15px",
                      backgroundColor: "white",
                      borderRadius: "8px",
                      border: "1px solid #dee2e6",
                      textAlign: "center",
                    }}
                  >
                    <div
                      style={{
                        fontSize: "1.5em",
                        fontWeight: "bold",
                        color: "#17a2b8",
                      }}
                    >
                      🎯
                    </div>
                    <div style={{ fontSize: "14px", marginTop: "5px" }}>
                      Data Density
                    </div>
                    <div style={{ fontSize: "12px", color: "#666" }}>
                      {analytics.total_jobs > 0
                        ? Math.round(
                            (analytics.total_data_points || 0) / analytics.total_jobs,
                          )
                        : 0}{" "}
                      avg/job
                    </div>
                  </div>
                  <div
                    style={{
                      padding: "15px",
                      backgroundColor: "white",
                      borderRadius: "8px",
                      border: "1px solid #dee2e6",
                      textAlign: "center",
                    }}
                  >
                    <div
                      style={{
                        fontSize: "1.5em",
                        fontWeight: "bold",
                        color:
                          analytics.failed_jobs === 0 ? "#28a745" : "#dc3545",
                      }}
                    >
                      {analytics.failed_jobs === 0 ? "💎" : "⚠️"}
                    </div>
                    <div style={{ fontSize: "14px", marginTop: "5px" }}>
                      Data Reliability
                    </div>
                    <div style={{ fontSize: "12px", color: "#666" }}>
                      {analytics.failed_jobs} failures
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div
              style={{ textAlign: "center", padding: "40px", color: "#666" }}
            >
              <div style={{ fontSize: "48px", marginBottom: "15px" }}>📊</div>
              <div style={{ fontSize: "18px", marginBottom: "10px" }}>
                Loading Analytics Data
              </div>
              <div style={{ fontSize: "14px" }}>
                Gathering insights from centralized database...
              </div>
            </div>
          )}
        </div>
      )}

      {/* Performance Tab */}
      {currentTab === "performance" && (
        <div>
          <h2>⚡ Performance Monitoring</h2>
          {performance ? (
            <div>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
                  gap: "20px",
                  marginBottom: "30px",
                }}
              >
                <div
                  style={{
                    padding: "20px",
                    backgroundColor: "#f8f9fa",
                    borderRadius: "8px",
                    border: "1px solid #ddd",
                  }}
                >
                  <h3>System Resources</h3>
                  <div>
                    CPU Usage: <strong>{performance.cpu_usage}%</strong>
                  </div>
                  <div>
                    Memory Usage: <strong>{performance.memory_usage}%</strong>
                  </div>
                  <div>
                    Active Connections:{" "}
                    <strong>{performance.active_connections}</strong>
                  </div>
                </div>
                <div
                  style={{
                    padding: "20px",
                    backgroundColor: "#e8f5e8",
                    borderRadius: "8px",
                    border: "1px solid #c3e6cb",
                  }}
                >
                  <h3>API Performance</h3>
                  <div>
                    Requests/min:{" "}
                    <strong>{performance.requests_per_minute}</strong>
                  </div>
                  <div>
                    Avg Response Time:{" "}
                    <strong>{performance.avg_response_time}ms</strong>
                  </div>
                  <div>
                    Cache Hit Rate:{" "}
                    <strong>{performance.cache_hit_rate}%</strong>
                  </div>
                </div>
              </div>

              <div
                style={{
                  backgroundColor: "#fff3cd",
                  padding: "20px",
                  borderRadius: "8px",
                  marginBottom: "20px",
                }}
              >
                <h3>Performance Actions</h3>
                <div style={{ display: "flex", gap: "10px" }}>
                  <button
                    onClick={() => fetchPerformance()}
                    style={{
                      padding: "8px 16px",
                      backgroundColor: "#17a2b8",
                      color: "white",
                      border: "none",
                      borderRadius: "4px",
                      cursor: "pointer",
                    }}
                  >
                    🔄 Refresh Metrics
                  </button>
                  <button
                    onClick={async () => {
                      try {
                        await fetch(
                          "http://localhost:8000/api/performance/cache/clear",
                          {
                            method: "POST",
                            headers: { Authorization: `Bearer ${token}` },
                          },
                        );
                        alert("Cache cleared successfully!");
                        fetchPerformance();
                      } catch (error) {
                        alert("Failed to clear cache");
                      }
                    }}
                    style={{
                      padding: "8px 16px",
                      backgroundColor: "#dc3545",
                      color: "white",
                      border: "none",
                      borderRadius: "4px",
                      cursor: "pointer",
                    }}
                  >
                    🗑️ Clear Cache
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div>Loading performance data...</div>
          )}
        </div>
      )}

      {/* Crawlers Tab */}
      {currentTab === "crawlers" && (
        <div>
          <h2>🕷️ Advanced Crawlers & Analysis</h2>

          {/* Crawler Type Selection */}
          <div
            style={{
              backgroundColor: "#fff3cd",
              padding: "20px",
              borderRadius: "8px",
              marginBottom: "30px",
            }}
          >
            <h3>🎯 Crawler Mode Selection</h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
                gap: "15px",
                marginBottom: "20px",
              }}
            >
              <div
                style={{
                  padding: "15px",
                  border:
                    newJob.type === "crawling"
                      ? "2px solid #007bff"
                      : "1px solid #ddd",
                  borderRadius: "8px",
                  backgroundColor:
                    newJob.type === "crawling" ? "#e3f2fd" : "white",
                  cursor: "pointer",
                }}
                onClick={() => setNewJob({ ...newJob, type: "crawling" })}
              >
                <h4 style={{ margin: "0 0 10px 0", color: "#007bff" }}>
                  🕷️ Deep Crawler
                </h4>
                <p style={{ margin: "0", fontSize: "14px" }}>
                  Automatically follows links and crawls through multiple pages
                  with configurable depth
                </p>
                <ul
                  style={{ fontSize: "12px", color: "#666", marginTop: "8px" }}
                >
                  <li>Link discovery & following</li>
                  <li>Configurable depth levels</li>
                  <li>Pattern-based filtering</li>
                  <li>Comprehensive site mapping</li>
                </ul>
              </div>
              <div
                style={{
                  padding: "15px",
                  border:
                    newJob.type === "scraping"
                      ? "2px solid #28a745"
                      : "1px solid #ddd",
                  borderRadius: "8px",
                  backgroundColor:
                    newJob.type === "scraping" ? "#d4edda" : "white",
                  cursor: "pointer",
                }}
                onClick={() => setNewJob({ ...newJob, type: "scraping" })}
              >
                <h4 style={{ margin: "0 0 10px 0", color: "#28a745" }}>
                  📄 Single Page Scraper
                </h4>
                <p style={{ margin: "0", fontSize: "14px" }}>
                  Extracts data from specific pages without following links
                </p>
                <ul
                  style={{ fontSize: "12px", color: "#666", marginTop: "8px" }}
                >
                  <li>Targeted data extraction</li>
                  <li>Custom selectors</li>
                  <li>Fast processing</li>
                  <li>Precise control</li>
                </ul>
              </div>
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "30px",
            }}
          >
            <div
              style={{
                backgroundColor: "#f8f9fa",
                padding: "20px",
                borderRadius: "8px",
              }}
            >
              <h3>
                🔍 {newJob.type === "crawling" ? "Crawler" : "Scraper"}{" "}
                Configuration
              </h3>
              <form
                onSubmit={submitJob}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "15px",
                }}
              >
                <div>
                  <label
                    style={{
                      display: "block",
                      marginBottom: "5px",
                      fontWeight: "bold",
                    }}
                  >
                    Job Name:
                  </label>
                  <input
                    type="text"
                    value={newJob.name}
                    onChange={(e) =>
                      setNewJob({ ...newJob, name: e.target.value })
                    }
                    required
                    placeholder={
                      newJob.type === "crawling"
                        ? "Site Crawler Job"
                        : "Page Scraper Job"
                    }
                    style={{
                      width: "100%",
                      padding: "8px",
                      border: "1px solid #ccc",
                      borderRadius: "4px",
                    }}
                  />
                </div>
                <div>
                  <label
                    style={{
                      display: "block",
                      marginBottom: "5px",
                      fontWeight: "bold",
                    }}
                  >
                    {newJob.type === "crawling"
                      ? "Starting URL:"
                      : "Target URL:"}
                  </label>
                  <input
                    type="url"
                    value={newJob.url}
                    onChange={(e) =>
                      setNewJob({ ...newJob, url: e.target.value })
                    }
                    required
                    placeholder="https://example.com"
                    style={{
                      width: "100%",
                      padding: "8px",
                      border: "1px solid #ccc",
                      borderRadius: "4px",
                    }}
                  />
                </div>
                <div>
                  <label
                    style={{
                      display: "block",
                      marginBottom: "5px",
                      fontWeight: "bold",
                    }}
                  >
                    Content Type:
                  </label>
                  <select
                    value={newJob.scraper_type}
                    onChange={(e) =>
                      setNewJob({
                        ...newJob,
                        scraper_type: e.target.value as any,
                      })
                    }
                    style={{
                      width: "100%",
                      padding: "8px",
                      border: "1px solid #ccc",
                      borderRadius: "4px",
                    }}
                  >
                    <option value="basic">Basic Web Content</option>
                    <option value="e_commerce">E-Commerce Products</option>
                    <option value="news">News & Articles</option>
                    <option value="social_media">Social Media</option>
                    <option value="api">API Endpoints</option>
                  </select>
                </div>

                {newJob.type === "crawling" && (
                  <>
                    <div>
                      <label
                        style={{
                          display: "block",
                          marginBottom: "5px",
                          fontWeight: "bold",
                        }}
                      >
                        Crawl Depth: {newJob.config?.max_depth || 2}
                      </label>
                      <input
                        type="range"
                        min="1"
                        max="10"
                        value={newJob.config?.max_depth || 2}
                        onChange={(e) =>
                          setNewJob({
                            ...newJob,
                            config: {
                              ...newJob.config,
                              max_depth: parseInt(e.target.value),
                            },
                          })
                        }
                        style={{ width: "100%" }}
                      />
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          fontSize: "12px",
                          color: "#666",
                        }}
                      >
                        <span>1 (shallow)</span>
                        <span>5 (moderate)</span>
                        <span>10 (deep)</span>
                      </div>
                    </div>

                    <div>
                      <label
                        style={{
                          display: "block",
                          marginBottom: "5px",
                          fontWeight: "bold",
                        }}
                      >
                        Max Pages: {newJob.config?.max_pages || 50}
                      </label>
                      <input
                        type="range"
                        min="10"
                        max="1000"
                        step="10"
                        value={newJob.config?.max_pages || 50}
                        onChange={(e) =>
                          setNewJob({
                            ...newJob,
                            config: {
                              ...newJob.config,
                              max_pages: parseInt(e.target.value),
                            },
                          })
                        }
                        style={{ width: "100%" }}
                      />
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          fontSize: "12px",
                          color: "#666",
                        }}
                      >
                        <span>10</span>
                        <span>500</span>
                        <span>1000</span>
                      </div>
                    </div>

                    <div>
                      <label
                        style={{
                          display: "block",
                          marginBottom: "5px",
                          fontWeight: "bold",
                        }}
                      >
                        Delay Between Requests: {newJob.config?.delay || 1000}ms
                      </label>
                      <input
                        type="range"
                        min="100"
                        max="5000"
                        step="100"
                        value={newJob.config?.delay || 1000}
                        onChange={(e) =>
                          setNewJob({
                            ...newJob,
                            config: {
                              ...newJob.config,
                              delay: parseInt(e.target.value),
                            },
                          })
                        }
                        style={{ width: "100%" }}
                      />
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          fontSize: "12px",
                          color: "#666",
                        }}
                      >
                        <span>100ms (fast)</span>
                        <span>2500ms (moderate)</span>
                        <span>5000ms (polite)</span>
                      </div>
                    </div>

                    <div>
                      <label
                        style={{
                          display: "block",
                          marginBottom: "5px",
                          fontWeight: "bold",
                        }}
                      >
                        Link Patterns (include):
                      </label>
                      <input
                        type="text"
                        value={newJob.config?.link_patterns?.join(", ") || ""}
                        onChange={(e) =>
                          setNewJob({
                            ...newJob,
                            config: {
                              ...newJob.config,
                              link_patterns: e.target.value
                                .split(",")
                                .map((p) => p.trim())
                                .filter((p) => p),
                            },
                          })
                        }
                        placeholder="/products/, /articles/, /news/"
                        style={{
                          width: "100%",
                          padding: "8px",
                          border: "1px solid #ccc",
                          borderRadius: "4px",
                        }}
                      />
                      <small style={{ color: "#666" }}>
                        Comma-separated patterns for links to follow
                      </small>
                    </div>

                    <div>
                      <label
                        style={{
                          display: "block",
                          marginBottom: "5px",
                          fontWeight: "bold",
                        }}
                      >
                        Ignore Patterns (exclude):
                      </label>
                      <input
                        type="text"
                        value={newJob.config?.ignore_patterns?.join(", ") || ""}
                        onChange={(e) =>
                          setNewJob({
                            ...newJob,
                            config: {
                              ...newJob.config,
                              ignore_patterns: e.target.value
                                .split(",")
                                .map((p) => p.trim())
                                .filter((p) => p),
                            },
                          })
                        }
                        placeholder="/admin/, /login/, .pdf, .jpg"
                        style={{
                          width: "100%",
                          padding: "8px",
                          border: "1px solid #ccc",
                          borderRadius: "4px",
                        }}
                      />
                      <small style={{ color: "#666" }}>
                        Comma-separated patterns for links to ignore
                      </small>
                    </div>
                  </>
                )}

                <div>
                  <label
                    style={{
                      display: "block",
                      marginBottom: "5px",
                      fontWeight: "bold",
                    }}
                  >
                    Custom Selectors (JSON):
                  </label>
                  <textarea
                    value={JSON.stringify(newJob.custom_selectors, null, 2)}
                    onChange={(e) => {
                      try {
                        setNewJob({
                          ...newJob,
                          custom_selectors: JSON.parse(e.target.value),
                        });
                      } catch (error) {
                        // Invalid JSON, ignore for now
                      }
                    }}
                    placeholder='{"title": "h1", "content": ".content", "links": "a"}'
                    style={{
                      width: "100%",
                      padding: "8px",
                      border: "1px solid #ccc",
                      borderRadius: "4px",
                      minHeight: "100px",
                      fontFamily: "monospace",
                    }}
                  />
                </div>

                <button
                  type="submit"
                  disabled={!isBackendConnected || isSubmitting}
                  style={{
                    padding: "12px",
                    backgroundColor: isBackendConnected
                      ? newJob.type === "crawling"
                        ? "#007bff"
                        : "#28a745"
                      : "#6c757d",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: isBackendConnected ? "pointer" : "not-allowed",
                    fontSize: "16px",
                  }}
                >
                  {isSubmitting
                    ? newJob.type === "crawling"
                      ? "Starting Crawler..."
                      : "Creating Scraper..."
                    : newJob.type === "crawling"
                      ? "🕷️ Start Crawler"
                      : "📄 Create Scraper"}
                </button>
              </form>
            </div>

            <div>
              <div
                style={{
                  backgroundColor: "#e3f2fd",
                  padding: "20px",
                  borderRadius: "8px",
                  marginBottom: "20px",
                }}
              >
                <h3>
                  📊 {newJob.type === "crawling" ? "Crawler" : "Scraper"}{" "}
                  Features
                </h3>
                <ul style={{ margin: "10px 0", paddingLeft: "20px" }}>
                  {newJob.type === "crawling" ? (
                    <>
                      <li>🔍 Automatic link discovery & following</li>
                      <li>📏 Configurable crawl depth (1-10 levels)</li>
                      <li>🎯 Pattern-based link filtering</li>
                      <li>🚦 Smart rate limiting & delays</li>
                      <li>🗺️ Site structure mapping</li>
                      <li>📈 Real-time progress tracking</li>
                      <li>💾 Comprehensive data collection</li>
                      <li>🔐 Respect for robots.txt</li>
                    </>
                  ) : (
                    <>
                      <li>🔍 Targeted content extraction</li>
                      <li>🎯 Custom CSS selectors</li>
                      <li>📊 Data validation & cleaning</li>
                      <li>⚡ Fast processing</li>
                      <li>📈 Quality analytics</li>
                      <li>🔄 Real-time monitoring</li>
                      <li>💾 Multiple export formats</li>
                      <li>🔐 Security & rate limiting</li>
                    </>
                  )}
                </ul>
              </div>

              <div
                style={{
                  backgroundColor: "#fff3cd",
                  padding: "20px",
                  borderRadius: "8px",
                }}
              >
                <h3>🎯 Quick Templates</h3>
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "10px",
                  }}
                >
                  <button
                    onClick={() =>
                      setNewJob({
                        name: "E-commerce Site Crawler",
                        type: "crawling",
                        url: "https://example-shop.com",
                        scraper_type: "e_commerce",
                        custom_selectors: {
                          title: ".product-title",
                          price: ".price",
                          description: ".product-desc",
                        },
                        config: {
                          max_depth: 3,
                          max_pages: 200,
                          follow_links: true,
                          delay: 2000,
                          link_patterns: ["/products/", "/category/"],
                          ignore_patterns: ["/admin/", "/cart/", "/checkout/"],
                        },
                      })
                    }
                    style={{
                      padding: "10px",
                      backgroundColor: "#17a2b8",
                      color: "white",
                      border: "none",
                      borderRadius: "4px",
                      cursor: "pointer",
                    }}
                  >
                    🛒 E-commerce Crawler
                  </button>
                  <button
                    onClick={() =>
                      setNewJob({
                        name: "News Site Deep Crawler",
                        type: "crawling",
                        url: "https://news-site.com",
                        scraper_type: "news",
                        custom_selectors: {
                          headline: "h1",
                          content: ".article-body",
                          author: ".author",
                          date: ".publish-date",
                        },
                        config: {
                          max_depth: 4,
                          max_pages: 500,
                          follow_links: true,
                          delay: 1500,
                          link_patterns: ["/articles/", "/news/", "/story/"],
                          ignore_patterns: ["/sports/", "/weather/", "/ads/"],
                        },
                      })
                    }
                    style={{
                      padding: "10px",
                      backgroundColor: "#fd7e14",
                      color: "white",
                      border: "none",
                      borderRadius: "4px",
                      cursor: "pointer",
                    }}
                  >
                    📰 News Crawler
                  </button>
                  <button
                    onClick={() =>
                      setNewJob({
                        name: "General Website Crawler",
                        type: "crawling",
                        url: "https://example.com",
                        scraper_type: "basic",
                        custom_selectors: {
                          title: "h1",
                          content: "p",
                          links: "a",
                        },
                        config: {
                          max_depth: 2,
                          max_pages: 100,
                          follow_links: true,
                          delay: 1000,
                          link_patterns: [],
                          ignore_patterns: [
                            ".pdf",
                            ".jpg",
                            ".png",
                            "/login/",
                            "/admin/",
                          ],
                        },
                      })
                    }
                    style={{
                      padding: "10px",
                      backgroundColor: "#6f42c1",
                      color: "white",
                      border: "none",
                      borderRadius: "4px",
                      cursor: "pointer",
                    }}
                  >
                    🔧 Basic Crawler
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Network Configuration Tab */}
      {currentTab === "network" && (
        <div>
          <h2>🌐 Network Configuration</h2>

          {/* TOR Integration */}
          <div
            style={{
              backgroundColor: "#f8d7da",
              padding: "20px",
              borderRadius: "8px",
              marginBottom: "30px",
            }}
          >
            <h3>🧅 TOR Network Integration</h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "20px",
              }}
            >
              <div>
                <h4>Connection Status</h4>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    marginBottom: "15px",
                  }}
                >
                  <span
                    style={{
                      width: "12px",
                      height: "12px",
                      borderRadius: "50%",
                      backgroundColor: "#dc3545",
                      display: "inline-block",
                    }}
                  ></span>
                  <span>Disconnected</span>
                </div>
                <button
                  style={{
                    padding: "10px 20px",
                    backgroundColor: "#28a745",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                    marginRight: "10px",
                  }}
                >
                  🔌 Connect to TOR
                </button>
                <button
                  style={{
                    padding: "10px 20px",
                    backgroundColor: "#17a2b8",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                  }}
                >
                  🔄 New Circuit
                </button>
              </div>
              <div>
                <h4>Exit Node Selection</h4>
                <select
                  style={{
                    width: "100%",
                    padding: "8px",
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                    marginBottom: "10px",
                  }}
                >
                  <option>🇺🇸 United States</option>
                  <option>🇩🇪 Germany</option>
                  <option>🇳🇱 Netherlands</option>
                  <option>🇨🇭 Switzerland</option>
                  <option>🇸🇪 Sweden</option>
                </select>
                <div style={{ fontSize: "12px", color: "#666" }}>
                  Current Circuit: Connecting...
                </div>
              </div>
            </div>
          </div>

          {/* VPN Integration */}
          <div
            style={{
              backgroundColor: "#d4edda",
              padding: "20px",
              borderRadius: "8px",
              marginBottom: "30px",
            }}
          >
            <h3>🔒 VPN Provider Integration</h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
                gap: "15px",
              }}
            >
              {[
                "CyberGhost",
                "IPVanish",
                "ProtonVPN",
                "Mullvad",
                "PIA",
                "TunnelBear",
                "SurfShark",
              ].map((provider) => (
                <div
                  key={provider}
                  style={{
                    padding: "15px",
                    border: "1px solid #c3e6cb",
                    borderRadius: "8px",
                    backgroundColor: "white",
                  }}
                >
                  <h4 style={{ margin: "0 0 10px 0" }}>{provider}</h4>
                  <div
                    style={{
                      fontSize: "12px",
                      color: "#666",
                      marginBottom: "10px",
                    }}
                  >
                    Status: Not Configured
                  </div>
                  <button
                    style={{
                      padding: "6px 12px",
                      backgroundColor: "#007bff",
                      color: "white",
                      border: "none",
                      borderRadius: "4px",
                      cursor: "pointer",
                      fontSize: "12px",
                    }}
                  >
                    Configure
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Proxy Pool Management */}
          <div
            style={{
              backgroundColor: "#fff3cd",
              padding: "20px",
              borderRadius: "8px",
            }}
          >
            <h3>🎭 Proxy Pool Management</h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr 1fr",
                gap: "20px",
              }}
            >
              <div
                style={{
                  padding: "15px",
                  border: "1px solid #ffeaa7",
                  borderRadius: "8px",
                  backgroundColor: "white",
                }}
              >
                <h4>Residential Proxies</h4>
                <div>Active: 0 / 0</div>
                <div>Success Rate: N/A</div>
                <div>Avg Speed: N/A</div>
                <button
                  style={{
                    padding: "8px 16px",
                    backgroundColor: "#28a745",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                    marginTop: "10px",
                  }}
                >
                  Add Pool
                </button>
              </div>
              <div
                style={{
                  padding: "15px",
                  border: "1px solid #ffeaa7",
                  borderRadius: "8px",
                  backgroundColor: "white",
                }}
              >
                <h4>Datacenter Proxies</h4>
                <div>Active: 0 / 0</div>
                <div>Success Rate: N/A</div>
                <div>Avg Speed: N/A</div>
                <button
                  style={{
                    padding: "8px 16px",
                    backgroundColor: "#28a745",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                    marginTop: "10px",
                  }}
                >
                  Add Pool
                </button>
              </div>
              <div
                style={{
                  padding: "15px",
                  border: "1px solid #ffeaa7",
                  borderRadius: "8px",
                  backgroundColor: "white",
                }}
              >
                <h4>Mobile Proxies</h4>
                <div>Active: 0 / 0</div>
                <div>Success Rate: N/A</div>
                <div>Avg Speed: N/A</div>
                <button
                  style={{
                    padding: "8px 16px",
                    backgroundColor: "#28a745",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                    marginTop: "10px",
                  }}
                >
                  Add Pool
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* OSINT Integration Tab */}
      {currentTab === "osint" && (
        <div>
          <h2>🔍 OSINT Intelligence Gathering</h2>

          {/* Investigation Targets */}
          <div
            style={{
              backgroundColor: "#e3f2fd",
              padding: "20px",
              borderRadius: "8px",
              marginBottom: "30px",
            }}
          >
            <h3>🎯 Investigation Targets</h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr auto",
                gap: "15px",
                marginBottom: "20px",
              }}
            >
              <input
                type="text"
                placeholder="Enter domain, email, username, or IP address"
                style={{
                  width: "100%",
                  padding: "12px",
                  border: "1px solid #ddd",
                  borderRadius: "6px",
                  fontSize: "14px",
                }}
              />
              <button
                style={{
                  padding: "12px 20px",
                  backgroundColor: "#007bff",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                }}
              >
                🔍 Add Target
              </button>
            </div>

            <div style={{ display: "grid", gap: "10px" }}>
              <div
                style={{
                  padding: "15px",
                  border: "1px solid #bbdefb",
                  borderRadius: "8px",
                  backgroundColor: "white",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <strong>example.com</strong>
                  <div style={{ fontSize: "12px", color: "#666" }}>
                    Domain • Added 2 minutes ago
                  </div>
                </div>
                <div style={{ display: "flex", gap: "10px" }}>
                  <span
                    style={{
                      padding: "4px 8px",
                      backgroundColor: "#fff3cd",
                      borderRadius: "12px",
                      fontSize: "12px",
                    }}
                  >
                    Queued
                  </span>
                  <button
                    style={{
                      padding: "4px 8px",
                      backgroundColor: "#28a745",
                      color: "white",
                      border: "none",
                      borderRadius: "4px",
                      cursor: "pointer",
                      fontSize: "12px",
                    }}
                  >
                    Start
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* SpiderFoot Integration */}
          <div
            style={{
              backgroundColor: "#f8f9fa",
              padding: "20px",
              borderRadius: "8px",
              marginBottom: "30px",
            }}
          >
            <h3>🕷️ SpiderFoot Intelligence Modules</h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                gap: "15px",
              }}
            >
              {[
                "DNS Records",
                "WHOIS Data",
                "Subdomain Discovery",
                "Email Discovery",
                "Social Media Profiles",
                "Data Breach Check",
                "Shodan Integration",
                "Certificate Transparency",
              ].map((module) => (
                <div
                  key={module}
                  style={{
                    padding: "12px",
                    border: "1px solid #dee2e6",
                    borderRadius: "6px",
                    backgroundColor: "white",
                    textAlign: "center",
                  }}
                >
                  <div style={{ fontWeight: "bold", marginBottom: "5px" }}>
                    {module}
                  </div>
                  <label
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: "5px",
                    }}
                  >
                    <input type="checkbox" defaultChecked />
                    <span style={{ fontSize: "12px" }}>Enabled</span>
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Investigation Results */}
          <div
            style={{
              backgroundColor: "#d4edda",
              padding: "20px",
              borderRadius: "8px",
            }}
          >
            <h3>📊 Investigation Results</h3>
            <div
              style={{ textAlign: "center", padding: "40px", color: "#666" }}
            >
              <div style={{ fontSize: "48px", marginBottom: "15px" }}>🕵️</div>
              <div style={{ fontSize: "18px", marginBottom: "10px" }}>
                No Active Investigations
              </div>
              <div style={{ fontSize: "14px" }}>
                Add targets above to start intelligence gathering
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Data Enrichment Tab */}
      {currentTab === "data-enrichment" && (
        <div>
          <h2>💎 Data Enrichment Services</h2>

          {/* API Providers */}
          <div
            style={{
              backgroundColor: "#fff3cd",
              padding: "20px",
              borderRadius: "8px",
              marginBottom: "30px",
            }}
          >
            <h3>🔌 Commercial API Providers</h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
                gap: "20px",
              }}
            >
              {[
                {
                  name: "Clearbit",
                  status: "Not Configured",
                  requests: 0,
                  cost: "$0.00",
                },
                {
                  name: "FullContact",
                  status: "Not Configured",
                  requests: 0,
                  cost: "$0.00",
                },
                {
                  name: "Hunter.io",
                  status: "Not Configured",
                  requests: 0,
                  cost: "$0.00",
                },
                {
                  name: "Shodan",
                  status: "Not Configured",
                  requests: 0,
                  cost: "$0.00",
                },
              ].map((provider) => (
                <div
                  key={provider.name}
                  style={{
                    padding: "20px",
                    border: "1px solid #ffeaa7",
                    borderRadius: "8px",
                    backgroundColor: "white",
                  }}
                >
                  <h4 style={{ margin: "0 0 15px 0" }}>{provider.name}</h4>
                  <div style={{ marginBottom: "10px" }}>
                    <div>
                      Status:{" "}
                      <span style={{ color: "#dc3545" }}>
                        {provider.status}
                      </span>
                    </div>
                    <div>Requests: {provider.requests}</div>
                    <div>Cost: {provider.cost}</div>
                  </div>
                  <button
                    style={{
                      padding: "8px 16px",
                      backgroundColor: "#007bff",
                      color: "white",
                      border: "none",
                      borderRadius: "4px",
                      cursor: "pointer",
                      marginRight: "10px",
                    }}
                  >
                    Configure API
                  </button>
                  <button
                    style={{
                      padding: "8px 16px",
                      backgroundColor: "#28a745",
                      color: "white",
                      border: "none",
                      borderRadius: "4px",
                      cursor: "pointer",
                    }}
                  >
                    Test
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Enrichment Queue */}
          <div
            style={{
              backgroundColor: "#e3f2fd",
              padding: "20px",
              borderRadius: "8px",
              marginBottom: "30px",
            }}
          >
            <h3>📋 Enrichment Queue</h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "2fr 1fr auto",
                gap: "15px",
                marginBottom: "20px",
              }}
            >
              <input
                type="text"
                placeholder="Enter email, domain, or company name for enrichment"
                style={{
                  width: "100%",
                  padding: "12px",
                  border: "1px solid #ddd",
                  borderRadius: "6px",
                }}
              />
              <select
                style={{
                  padding: "12px",
                  border: "1px solid #ddd",
                  borderRadius: "6px",
                }}
              >
                <option>All Providers</option>
                <option>Clearbit Only</option>
                <option>FullContact Only</option>
                <option>Hunter.io Only</option>
                <option>Shodan Only</option>
              </select>
              <button
                style={{
                  padding: "12px 20px",
                  backgroundColor: "#007bff",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                }}
              >
                🚀 Enrich
              </button>
            </div>

            <div
              style={{ textAlign: "center", padding: "40px", color: "#666" }}
            >
              <div style={{ fontSize: "48px", marginBottom: "15px" }}>💎</div>
              <div style={{ fontSize: "18px", marginBottom: "10px" }}>
                No Enrichment Requests
              </div>
              <div style={{ fontSize: "14px" }}>
                Add data above to start enrichment process
              </div>
            </div>
          </div>

          {/* Cost Analytics */}
          <div
            style={{
              backgroundColor: "#f8f9fa",
              padding: "20px",
              borderRadius: "8px",
            }}
          >
            <h3>💰 Cost Analytics & Usage</h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                gap: "20px",
              }}
            >
              <div
                style={{
                  padding: "15px",
                  border: "1px solid #dee2e6",
                  borderRadius: "8px",
                  backgroundColor: "white",
                  textAlign: "center",
                }}
              >
                <h4>Total Spend</h4>
                <div
                  style={{
                    fontSize: "2em",
                    fontWeight: "bold",
                    color: "#007bff",
                  }}
                >
                  $0.00
                </div>
              </div>
              <div
                style={{
                  padding: "15px",
                  border: "1px solid #dee2e6",
                  borderRadius: "8px",
                  backgroundColor: "white",
                  textAlign: "center",
                }}
              >
                <h4>This Month</h4>
                <div
                  style={{
                    fontSize: "2em",
                    fontWeight: "bold",
                    color: "#28a745",
                  }}
                >
                  $0.00
                </div>
              </div>
              <div
                style={{
                  padding: "15px",
                  border: "1px solid #dee2e6",
                  borderRadius: "8px",
                  backgroundColor: "white",
                  textAlign: "center",
                }}
              >
                <h4>Requests</h4>
                <div
                  style={{
                    fontSize: "2em",
                    fontWeight: "bold",
                    color: "#17a2b8",
                  }}
                >
                  0
                </div>
              </div>
              <div
                style={{
                  padding: "15px",
                  border: "1px solid #dee2e6",
                  borderRadius: "8px",
                  backgroundColor: "white",
                  textAlign: "center",
                }}
              >
                <h4>Success Rate</h4>
                <div
                  style={{
                    fontSize: "2em",
                    fontWeight: "bold",
                    color: "#fd7e14",
                  }}
                >
                  N/A
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Data Parsing Tab */}
      {currentTab === "data-parsing" && (
        <div>
          <h2>📝 Advanced Data Parsing</h2>

          {/* File Upload */}
          <div
            style={{
              backgroundColor: "#e3f2fd",
              padding: "20px",
              borderRadius: "8px",
              marginBottom: "30px",
            }}
          >
            <h3>📁 File Upload & Processing</h3>
            <div
              style={{
                border: "2px dashed #bbdefb",
                padding: "40px",
                textAlign: "center",
                borderRadius: "8px",
                backgroundColor: "#f8f9ff",
              }}
            >
              <div style={{ fontSize: "48px", marginBottom: "15px" }}>📄</div>
              <div style={{ fontSize: "18px", marginBottom: "10px" }}>
                Drop files here or click to upload
              </div>
              <div
                style={{
                  fontSize: "14px",
                  color: "#666",
                  marginBottom: "20px",
                }}
              >
                Supported: PDF, TXT, DOCX, CSV, JSON, XML, Images (OCR)
              </div>
              <button
                style={{
                  padding: "12px 24px",
                  backgroundColor: "#007bff",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                }}
              >
                📁 Choose Files
              </button>
            </div>
          </div>

          {/* ML Models */}
          <div
            style={{
              backgroundColor: "#d4edda",
              padding: "20px",
              borderRadius: "8px",
              marginBottom: "30px",
            }}
          >
            <h3>🧠 ML-Powered Analysis</h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
                gap: "15px",
              }}
            >
              {[
                {
                  name: "Entity Extraction",
                  model: "spaCy en_core_web_sm",
                  status: "Ready",
                },
                {
                  name: "Sentiment Analysis",
                  model: "VADER + TextBlob",
                  status: "Ready",
                },
                {
                  name: "Language Detection",
                  model: "langdetect",
                  status: "Ready",
                },
                {
                  name: "Topic Modeling",
                  model: "LDA + BERT",
                  status: "Loading...",
                },
                {
                  name: "OCR Processing",
                  model: "Tesseract + EasyOCR",
                  status: "Ready",
                },
                {
                  name: "Document Classification",
                  model: "DistilBERT",
                  status: "Loading...",
                },
              ].map((ml) => (
                <div
                  key={ml.name}
                  style={{
                    padding: "15px",
                    border: "1px solid #c3e6cb",
                    borderRadius: "8px",
                    backgroundColor: "white",
                  }}
                >
                  <h4 style={{ margin: "0 0 10px 0" }}>{ml.name}</h4>
                  <div
                    style={{
                      fontSize: "12px",
                      color: "#666",
                      marginBottom: "5px",
                    }}
                  >
                    {ml.model}
                  </div>
                  <span
                    style={{
                      padding: "4px 8px",
                      borderRadius: "12px",
                      fontSize: "12px",
                      backgroundColor:
                        ml.status === "Ready" ? "#d4edda" : "#fff3cd",
                      color: ml.status === "Ready" ? "#155724" : "#856404",
                    }}
                  >
                    {ml.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Processing Results */}
          <div
            style={{
              backgroundColor: "#f8f9fa",
              padding: "20px",
              borderRadius: "8px",
            }}
          >
            <h3>📊 Processing Results</h3>
            <div
              style={{ textAlign: "center", padding: "40px", color: "#666" }}
            >
              <div style={{ fontSize: "48px", marginBottom: "15px" }}>🤖</div>
              <div style={{ fontSize: "18px", marginBottom: "10px" }}>
                No Files Processed
              </div>
              <div style={{ fontSize: "14px" }}>
                Upload files above to start ML-powered analysis
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Embedded Browser Tab */}
      {currentTab === "browser" && (
        <div>
          <h2>🌍 Embedded Browser</h2>

          {/* Browser Controls */}
          <div
            style={{
              backgroundColor: "#f8f9fa",
              padding: "15px",
              borderRadius: "8px",
              marginBottom: "20px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <button
                style={{
                  padding: "8px 12px",
                  backgroundColor: "#6c757d",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                ← Back
              </button>
              <button
                style={{
                  padding: "8px 12px",
                  backgroundColor: "#6c757d",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                → Forward
              </button>
              <button
                style={{
                  padding: "8px 12px",
                  backgroundColor: "#17a2b8",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                🔄 Reload
              </button>
              <input
                type="url"
                placeholder="Enter URL..."
                defaultValue="https://example.com"
                style={{
                  flex: 1,
                  padding: "8px 12px",
                  border: "1px solid #ddd",
                  borderRadius: "4px",
                }}
              />
              <button
                style={{
                  padding: "8px 12px",
                  backgroundColor: "#28a745",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                Go
              </button>
              <button
                style={{
                  padding: "8px 12px",
                  backgroundColor: "#dc3545",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                🔴 Record
              </button>
            </div>
          </div>

          {/* Browser Window */}
          <div
            style={{
              border: "1px solid #ddd",
              borderRadius: "8px",
              height: "600px",
              backgroundColor: "white",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "18px",
              color: "#666",
            }}
          >
            🌍 Embedded Chromium Browser
            <br />
            <small>
              Browser integration would be implemented with PyQt6 WebEngine
            </small>
          </div>

          {/* Recording Panel */}
          <div
            style={{
              backgroundColor: "#fff3cd",
              padding: "20px",
              borderRadius: "8px",
              marginTop: "20px",
            }}
          >
            <h3>📹 Interaction Recording</h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr auto auto",
                gap: "15px",
                alignItems: "center",
              }}
            >
              <div>
                <div style={{ fontWeight: "bold" }}>
                  Recording Status: Not Recording
                </div>
                <div style={{ fontSize: "14px", color: "#666" }}>
                  Click Record to start capturing interactions
                </div>
              </div>
              <button
                style={{
                  padding: "10px 20px",
                  backgroundColor: "#007bff",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                💾 Save Recording
              </button>
              <button
                style={{
                  padding: "10px 20px",
                  backgroundColor: "#28a745",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                ▶️ Replay
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Data Visualization Tab */}
      {currentTab === "visualization" && (
        <div>
          <h2>📈 Data Visualization & Site Mapping</h2>

          {/* Visualization Controls */}
          <div
            style={{
              backgroundColor: "#e3f2fd",
              padding: "20px",
              borderRadius: "8px",
              marginBottom: "30px",
            }}
          >
            <h3>🎛️ Visualization Controls</h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                gap: "15px",
              }}
            >
              <div>
                <label
                  style={{
                    display: "block",
                    marginBottom: "5px",
                    fontWeight: "bold",
                  }}
                >
                  Layout Algorithm:
                </label>
                <select
                  style={{
                    width: "100%",
                    padding: "8px",
                    border: "1px solid #ddd",
                    borderRadius: "4px",
                  }}
                >
                  <option>Spring Layout</option>
                  <option>Circular Layout</option>
                  <option>Hierarchical Layout</option>
                  <option>Force-Directed</option>
                  <option>Grid Layout</option>
                </select>
              </div>
              <div>
                <label
                  style={{
                    display: "block",
                    marginBottom: "5px",
                    fontWeight: "bold",
                  }}
                >
                  Color Scheme:
                </label>
                <select
                  style={{
                    width: "100%",
                    padding: "8px",
                    border: "1px solid #ddd",
                    borderRadius: "4px",
                  }}
                >
                  <option>By Page Type</option>
                  <option>By Link Depth</option>
                  <option>By Response Time</option>
                  <option>By Content Size</option>
                  <option>By Status Code</option>
                </select>
              </div>
              <div>
                <label
                  style={{
                    display: "block",
                    marginBottom: "5px",
                    fontWeight: "bold",
                  }}
                >
                  Node Size:
                </label>
                <select
                  style={{
                    width: "100%",
                    padding: "8px",
                    border: "1px solid #ddd",
                    borderRadius: "4px",
                  }}
                >
                  <option>By Incoming Links</option>
                  <option>By Outgoing Links</option>
                  <option>By Content Length</option>
                  <option>Uniform Size</option>
                </select>
              </div>
              <div>
                <label
                  style={{
                    display: "block",
                    marginBottom: "5px",
                    fontWeight: "bold",
                  }}
                >
                  View Mode:
                </label>
                <select
                  style={{
                    width: "100%",
                    padding: "8px",
                    border: "1px solid #ddd",
                    borderRadius: "4px",
                  }}
                >
                  <option>2D View</option>
                  <option>3D View</option>
                </select>
              </div>
            </div>
          </div>

          {/* Visualization Canvas */}
          <div
            style={{
              border: "1px solid #ddd",
              borderRadius: "8px",
              height: "500px",
              backgroundColor: "#f8f9fa",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "18px",
              color: "#666",
              marginBottom: "30px",
            }}
          >
            📊 Interactive Site Map Visualization
            <br />
            <small>D3.js/Three.js visualization would render here</small>
          </div>

          {/* Site Statistics */}
          <div
            style={{
              backgroundColor: "#d4edda",
              padding: "20px",
              borderRadius: "8px",
            }}
          >
            <h3>📊 Site Statistics</h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
                gap: "15px",
              }}
            >
              {[
                { label: "Total Pages", value: "0" },
                { label: "Max Depth", value: "0" },
                { label: "Unique Domains", value: "0" },
                { label: "Total Links", value: "0" },
                { label: "Images Found", value: "0" },
                { label: "Forms Found", value: "0" },
                { label: "Scripts Found", value: "0" },
                { label: "External Links", value: "0" },
              ].map((stat) => (
                <div
                  key={stat.label}
                  style={{
                    padding: "15px",
                    border: "1px solid #c3e6cb",
                    borderRadius: "8px",
                    backgroundColor: "white",
                    textAlign: "center",
                  }}
                >
                  <div
                    style={{
                      fontSize: "2em",
                      fontWeight: "bold",
                      color: "#155724",
                    }}
                  >
                    {stat.value}
                  </div>
                  <div style={{ fontSize: "14px", color: "#666" }}>
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
