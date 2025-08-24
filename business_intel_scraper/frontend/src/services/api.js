import axios from 'axios';

// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
apiClient.interceptors.request.use(
  (config) => {
  // Standardized token storage key
  const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Enhanced error handling
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          // Handle unauthorized access
          localStorage.removeItem('token');
          console.error('Authentication failed - redirecting to login');
          // Only redirect if not already on login page
          if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login';
          }
          break;
        case 403:
          console.error('Access forbidden:', data?.message || 'Insufficient permissions');
          break;
        case 404:
          console.error('Resource not found:', data?.message || 'Endpoint not found');
          break;
        case 422:
          console.error('Validation error:', data?.detail || 'Invalid request data');
          break;
        case 429:
          console.error('Rate limit exceeded:', data?.message || 'Too many requests');
          break;
        case 500:
          console.error('Server error:', data?.message || 'Internal server error');
          break;
        default:
          console.error(`HTTP Error ${status}:`, data?.message || 'Unknown error');
      }
    } else if (error.request) {
      // Network error - no response received
      console.error('Network error: Unable to connect to server');
      error.message = 'Network error: Unable to connect to server. Please check your connection.';
    } else {
      // Something else happened
      console.error('Request error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// Job API service
export const jobService = {
  // Get all jobs
  async getJobs() {
    try {
      const response = await apiClient.get('/jobs/');
      if (!Array.isArray(response.data)) {
        throw new Error('Invalid response format: expected array of jobs');
      }
      return response.data;
    } catch (error) {
      console.error('Failed to fetch jobs:', error.message);
      throw new Error('Failed to load jobs. Please try again.');
    }
  },

  // Get specific job by ID
  async getJob(jobId) {
    try {
      if (!jobId || typeof jobId !== 'number') {
        throw new Error('Invalid job ID provided');
      }
      const response = await apiClient.get(`/jobs/${jobId}`);
      if (!response.data || typeof response.data !== 'object') {
        throw new Error('Invalid job data received');
      }
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch job ${jobId}:`, error.message);
      throw new Error(`Failed to load job details. ${error.message}`);
    }
  },

  // Create new job
  async createJob(jobData) {
    try {
      if (!jobData || typeof jobData !== 'object') {
        throw new Error('Invalid job data provided');
      }
      
      // Validate required fields
      const requiredFields = ['name', 'url', 'scraper_type'];
      for (const field of requiredFields) {
        if (!jobData[field] || typeof jobData[field] !== 'string') {
          throw new Error(`Missing or invalid required field: ${field}`);
        }
      }
      
      const response = await apiClient.post('/jobs/', jobData);
      if (!response.data || !response.data.id) {
        throw new Error('Invalid response: job ID not returned');
      }
      return response.data;
    } catch (error) {
      console.error('Failed to create job:', error.message);
      throw new Error(`Failed to create job. ${error.message}`);
    }
  },

  // Start job
  async startJob(jobId) {
    try {
      if (!jobId || typeof jobId !== 'number') {
        throw new Error('Invalid job ID provided');
      }
      const response = await apiClient.post(`/jobs/${jobId}/start`);
      return response.data;
    } catch (error) {
      console.error(`Failed to start job ${jobId}:`, error.message);
      throw new Error(`Failed to start job. ${error.message}`);
    }
  },

  // Stop job
  async stopJob(jobId) {
    try {
      if (!jobId || typeof jobId !== 'number') {
        throw new Error('Invalid job ID provided');
      }
      const response = await apiClient.post(`/jobs/${jobId}/stop`);
      return response.data;
    } catch (error) {
      console.error(`Failed to stop job ${jobId}:`, error.message);
      throw new Error(`Failed to stop job. ${error.message}`);
    }
  },

  // Delete job
  async deleteJob(jobId) {
    try {
      if (!jobId || typeof jobId !== 'number') {
        throw new Error('Invalid job ID provided');
      }
      const response = await apiClient.delete(`/jobs/${jobId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to delete job ${jobId}:`, error.message);
      throw new Error(`Failed to delete job. ${error.message}`);
    }
  },

  // Get job logs
  async getJobLogs(jobId, limit = 100) {
    try {
      if (!jobId || typeof jobId !== 'number') {
        throw new Error('Invalid job ID provided');
      }
      if (limit && (typeof limit !== 'number' || limit < 1 || limit > 1000)) {
        throw new Error('Invalid limit: must be between 1 and 1000');
      }
      
      const response = await apiClient.get(`/jobs/${jobId}/logs?limit=${limit}`);
      if (!response.data || !Array.isArray(response.data.logs)) {
        throw new Error('Invalid logs format received');
      }
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch logs for job ${jobId}:`, error.message);
      throw new Error(`Failed to load job logs. ${error.message}`);
    }
  },

  // Get job data/results
  async getJobData(jobId, format = 'json') {
    try {
      if (!jobId || typeof jobId !== 'number') {
        throw new Error('Invalid job ID provided');
      }
      if (!['json', 'csv', 'xlsx'].includes(format)) {
        throw new Error('Invalid format: must be json, csv, or xlsx');
      }
      
      const response = await apiClient.get(`/jobs/${jobId}/data?format=${format}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch data for job ${jobId}:`, error.message);
      throw new Error(`Failed to load job data. ${error.message}`);
    }
  },

  // Get job statistics
  async getJobStats() {
    try {
      const response = await apiClient.get('/jobs/stats');
      if (!response.data || typeof response.data !== 'object') {
        throw new Error('Invalid statistics format received');
      }
      
      // Validate expected statistics fields
      const requiredFields = ['total_jobs', 'running_jobs', 'completed_jobs', 'failed_jobs'];
      for (const field of requiredFields) {
        if (typeof response.data[field] !== 'number') {
          console.warn(`Missing or invalid statistics field: ${field}`);
        }
      }
      
      return response.data;
    } catch (error) {
      console.error('Failed to fetch job statistics:', error.message);
      throw new Error(`Failed to load job statistics. ${error.message}`);
    }
  }
};

// Analytics API service
export const analyticsService = {
  // Get system metrics
  async getMetrics() {
    try {
      const response = await apiClient.get('/analytics/metrics');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch analytics metrics:', error);
      throw new Error('Failed to load analytics data');
    }
  },

  // Get dashboard analytics
  async getDashboardAnalytics() {
    try {
      const response = await apiClient.get('/analytics/dashboard');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch dashboard analytics:', error);
      throw new Error('Failed to load dashboard data');
    }
  },

  // Get performance data
  async getPerformance() {
    const response = await apiClient.get('/analytics/performance');
    return response.data;
  },

  // Get audit logs
  async getAuditLogs(limit = 100) {
    const response = await apiClient.get(`/analytics/audit?limit=${limit}`);
    return response.data;
  }
};

// OSINT API service
export const osintService = {
  // Run domain scan
  async scanDomain(domain, tools = ['spiderfoot', 'theharvester']) {
    const response = await apiClient.post('/osint/domain-scan', {
      domain,
      tools
    });
    return response.data;
  },

  // Get scan results
  async getScanResults(scanId) {
    const response = await apiClient.get(`/osint/results/${scanId}`);
    return response.data;
  }
};

// Scraping API service
export const scrapingService = {
  // Start web scraping task
  async startScraping(config) {
    const response = await apiClient.post('/scraping/start', config);
    return response.data;
  },

  // Get scraping results
  async getResults(taskId) {
    const response = await apiClient.get(`/scraping/results/${taskId}`);
    return response.data;
  },

  // Get available scrapers
  async getAvailableScrapers() {
    const response = await apiClient.get('/scraping/scrapers');
    return response.data;
  }
};

// Real-time WebSocket connection for job updates
export class JobUpdatesSocket {
  constructor(onMessage) {
    this.ws = null;
    this.onMessage = onMessage;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
  }

  connect() {
    const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws/jobs';
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected for job updates');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.onMessage(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.reconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect();
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }
}

// Authentication Service
export const authService = {
  // Login user
  async login(username, password) {
    try {
      const response = await apiClient.post('/auth/login', {
        username,
        password
      });
      
      if (response.data.access_token) {
    // Store under standardized key used across the app
    localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        return response.data;
      }
      
      throw new Error('Login failed: No access token received');
    } catch (error) {
      console.error('Login error:', error);
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  },

  // Logout user
  logout() {
  localStorage.removeItem('token');
    localStorage.removeItem('user');
    return Promise.resolve();
  },

  // Get current user
  async getCurrentUser() {
    try {
      const response = await apiClient.get('/auth/me');
      return response.data;
    } catch (error) {
      console.error('Get current user error:', error);
      throw new Error('Failed to get user information');
    }
  },

  // Check if user is authenticated
  isAuthenticated() {
  return !!localStorage.getItem('token');
  },

  // Get stored user data
  getUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }
};

// Health check service
export const healthService = {
  async checkHealth() {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      return { status: 'unhealthy', error: error.message };
    }
  }
};

export default apiClient;
