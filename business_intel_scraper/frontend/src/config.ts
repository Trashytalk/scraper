// API Configuration
export const API_BASE_URL = 'http://localhost:8000';

// API Endpoints
export const API_ENDPOINTS = {
  health: `${API_BASE_URL}/api/health`,
  auth: {
    login: `${API_BASE_URL}/api/auth/login`,
  },
  jobs: {
    base: `${API_BASE_URL}/api/jobs`,
    batch: `${API_BASE_URL}/api/jobs/batch`,
    byId: (id: number) => `${API_BASE_URL}/api/jobs/${id}`,
    start: (id: number) => `${API_BASE_URL}/api/jobs/${id}/start`,
    results: (id: number) => `${API_BASE_URL}/api/jobs/${id}/results`,
    extractUrls: (id: number) => `${API_BASE_URL}/api/jobs/${id}/extract-urls`,
  },
  analytics: {
    dashboard: `${API_BASE_URL}/api/analytics/dashboard`,
  },
  performance: {
    summary: `${API_BASE_URL}/api/performance/summary`,
    clearCache: `${API_BASE_URL}/api/performance/cache/clear`,
  },
  data: {
    centralize: `${API_BASE_URL}/api/data/centralize`,
    consolidate: `${API_BASE_URL}/api/data/consolidate`,
    export: `${API_BASE_URL}/api/data/export/all`,
    analyticsRefresh: `${API_BASE_URL}/api/data/analytics/refresh`,
  },
};
