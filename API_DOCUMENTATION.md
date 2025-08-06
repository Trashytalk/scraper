# 📚 API DOCUMENTATION
## Business Intelligence Scraper Platform v2.0.0

---

## 🌐 **API OVERVIEW**

**Base URL**: `http://localhost:8000` (Development) | `https://your-domain.com` (Production)  
**Authentication**: JWT Bearer Token  
**Content-Type**: `application/json`  
**API Version**: v2.0.0  

---

## 🔐 **AUTHENTICATION**

### **Login**
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### **Using the Token**
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## 📊 **CORE ENDPOINTS**

### **System Health**
```http
GET /health
```
**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-12-22T10:00:00Z",
  "version": "2.0.0",
  "uptime": 3600
}
```

### **API Documentation** 
```http
GET /docs
```
Interactive Swagger UI with all endpoint documentation.

---

## 🤖 **AI & ML SERVICES**

### **AI Status**
```http
GET /api/ai/status
Authorization: Bearer <token>
```

**Response:**
```json
{
  "status": "operational",
  "services": {
    "content_analysis": true,
    "sentiment_analysis": true,
    "entity_extraction": true
  },
  "models_loaded": 5,
  "processing_queue": 12
}
```

### **Content Analysis**
```http
POST /api/ai/process-text
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "Your content to analyze",
  "analysis_types": ["sentiment", "entities", "classification"]
}
```

**Response:**
```json
{
  "sentiment": {
    "score": 0.75,
    "label": "positive"
  },
  "entities": [
    {
      "text": "OpenAI",
      "label": "ORG",
      "confidence": 0.95
    }
  ],
  "classification": {
    "category": "technology",
    "confidence": 0.88
  }
}
```

### **Real-Time Dashboard**
```http
GET /api/ai/realtime-dashboard
Authorization: Bearer <token>
```

**Response:**
```json
{
  "active_jobs": 15,
  "completed_today": 234,
  "processing_rate": "12.5/min",
  "system_health": "excellent",
  "recent_insights": [...]
}
```

---

## 🕷️ **CRAWLING & DATA COLLECTION**

### **Create Crawl Job**
```http
POST /api/crawl/jobs
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Example Crawl",
  "url": "https://example.com",
  "type": "intelligent_crawling",
  "config": {
    "max_pages": 100,
    "max_depth": 3,
    "rate_limit": {
      "requests_per_second": 1.0
    }
  }
}
```

### **Job Status**
```http
GET /api/crawl/jobs/{job_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Example Crawl",
  "status": "running",
  "progress": 45,
  "pages_crawled": 45,
  "data_collected": 1250,
  "started_at": "2024-12-22T10:00:00Z",
  "estimated_completion": "2024-12-22T11:30:00Z"
}
```

### **List All Jobs**
```http
GET /api/crawl/jobs
Authorization: Bearer <token>
```

### **Stop Job**
```http
POST /api/crawl/jobs/{job_id}/stop
Authorization: Bearer <token>
```

---

## 📊 **DASHBOARD & ANALYTICS**

### **Dashboard Stats**
```http
GET /api/dashboard/stats
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_jobs": 1547,
  "active_jobs": 12,
  "completed_jobs": 1520,
  "failed_jobs": 15,
  "total_pages_crawled": 125000,
  "data_quality_score": 94.5,
  "success_rate": 98.1,
  "avg_processing_time": "2.3s"
}
```

### **User Profile**
```http
GET /api/users/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "user123",
  "username": "admin",
  "email": "admin@company.com",
  "role": "administrator",
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-12-22T09:00:00Z"
}
```

---

## 🔧 **SYSTEM ADMINISTRATION**

### **System Metrics**
```http
GET /api/admin/metrics
Authorization: Bearer <token>
```

**Response:**
```json
{
  "cpu_usage": 45.2,
  "memory_usage": 67.8,
  "disk_usage": 23.1,
  "network_io": {
    "bytes_sent": 1048576,
    "bytes_received": 2097152
  },
  "database": {
    "connections": 15,
    "query_time_avg": "12ms"
  },
  "cache_hit_rate": 89.5
}
```

### **Background Tasks**
```http
GET /api/admin/tasks
Authorization: Bearer <token>
```

**Response:**
```json
{
  "active_tasks": 8,
  "pending_tasks": 23,
  "failed_tasks": 2,
  "tasks": [
    {
      "id": "task123",
      "type": "content_analysis",
      "status": "running",
      "progress": 75,
      "started_at": "2024-12-22T10:15:00Z"
    }
  ]
}
```

---

## 📈 **DATA EXPORT & REPORTS**

### **Export Data**
```http
POST /api/data/export
Authorization: Bearer <token>
Content-Type: application/json

{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "format": "json",
  "filters": {
    "date_range": {
      "start": "2024-12-01",
      "end": "2024-12-22"
    }
  }
}
```

### **Generate Report**
```http
POST /api/reports/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "report_type": "performance_summary",
  "period": "last_30_days",
  "include_visualizations": true
}
```

---

## 🚨 **ERROR HANDLING**

### **Standard Error Response**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "url",
      "reason": "Invalid URL format"
    },
    "timestamp": "2024-12-22T10:00:00Z"
  }
}
```

### **HTTP Status Codes**
| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

---

## 🔄 **WEBHOOKS & REAL-TIME**

### **WebSocket Connection**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  // Handle real-time updates
};
```

### **Event Types**
- `job_started`: Crawl job initiated
- `job_completed`: Crawl job finished
- `job_failed`: Crawl job encountered error
- `data_processed`: New data available
- `system_alert`: System notification

---

## 📊 **RATE LIMITS**

| Endpoint Category | Rate Limit | Window |
|------------------|------------|---------|
| Authentication | 10 requests | 1 minute |
| Data Operations | 100 requests | 1 minute |
| AI Processing | 50 requests | 1 minute |
| Admin Operations | 30 requests | 1 minute |

---

## 🛠️ **SDK & EXAMPLES**

### **Python SDK Example**
```python
import requests

class ScraperAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {token}'}
    
    def create_job(self, name, url, config=None):
        data = {
            'name': name,
            'url': url,
            'type': 'intelligent_crawling',
            'config': config or {}
        }
        response = requests.post(
            f'{self.base_url}/api/crawl/jobs',
            json=data,
            headers=self.headers
        )
        return response.json()

# Usage
api = ScraperAPI('http://localhost:8000', 'your_token')
job = api.create_job('My Crawl', 'https://example.com')
```

### **JavaScript/Node.js Example**
```javascript
class ScraperAPI {
  constructor(baseUrl, token) {
    this.baseUrl = baseUrl;
    this.headers = { 'Authorization': `Bearer ${token}` };
  }

  async getJobStatus(jobId) {
    const response = await fetch(
      `${this.baseUrl}/api/crawl/jobs/${jobId}`,
      { headers: this.headers }
    );
    return response.json();
  }
}
```

---

## 📞 **SUPPORT & RESOURCES**

- **Interactive API Docs**: `/docs` (Swagger UI)
- **Health Check**: `/health`
- **Status Page**: `/status`
- **GitHub Issues**: [Repository Issues](link-to-issues)
- **Technical Support**: See CONTRIBUTING.md

---

*API Documentation for Business Intelligence Scraper Platform v2.0.0 - Last updated: December 2024*
