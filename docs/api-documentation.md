# API Documentation

## 🔌 Business Intelligence Scraper API v2.0

**Complete REST API documentation for the Business Intelligence Scraper Platform**


---


## 📋 Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL & Versioning](#base-url--versioning)
- [Request/Response Format](#requestresponse-format)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Authentication](#authentication-endpoints)
  - [Data Management](#data-management-endpoints)
  - [Analytics](#analytics-endpoints)
  - [Job Management](#job-management-endpoints)
  - [User Management](#user-management-endpoints)
  - [System Monitoring](#system-monitoring-endpoints)
- [WebSocket API](#websocket-api)
- [SDK & Examples](#sdk--examples)


---


## 🎯 Overview

The Business Intelligence Scraper API provides comprehensive access to all platform features including data collection, analytics, user management, and system monitoring. The API is built with FastAPI and follows REST principles with full OpenAPI/Swagger documentation.

### Key Features

- **🔐 Secure Authentication**: JWT-based auth with MFA support
- **📊 Real-time Data**: WebSocket connections for live updates
- **⚡ High Performance**: Optimized endpoints with intelligent caching
- **🛡️ Enterprise Security**: Input validation, rate limiting, threat detection
- **📚 Auto-Documentation**: Interactive Swagger UI at `/docs`
- **🔧 Developer Friendly**: SDKs, examples, and comprehensive error handling


---


## 🔐 Authentication

### JWT Token Authentication

All API endpoints require authentication using JWT Bearer tokens. Obtain tokens through the login endpoint and include them in the Authorization header.

#### Login Flow

```bash

# 1. Login to get access token

curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{

    "username": "your_username",
    "password": "your_password",
    "mfa_token": "123456"  # Optional, if MFA enabled
  }'

# Response

{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": "user_123",
      "username": "your_username",
      "role": "analyst",
      "permissions": ["read_data", "create_reports"]
    }
  }
}

```

#### Using Access Tokens

```bash

# Include token in Authorization header

curl -X GET "http://localhost:8000/api/data" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

```

#### Token Refresh

```bash

# Refresh expired access token

curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{

    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'

```

### Multi-Factor Authentication (MFA)

#### Setup MFA

```bash

# Enable MFA for user account

curl -X POST "http://localhost:8000/auth/mfa/setup" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

# Response includes QR code and backup codes

{
  "success": true,
  "data": {
    "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSU...",
    "secret": "JBSWY3DPEHPK3PXP",
    "backup_codes": ["12345678", "87654321", ...],
    "setup_url": "otpauth://totp/BusinessIntelScraper:user@example.com?secret=..."
  }
}

```

#### Verify MFA Setup

```bash

# Verify MFA with TOTP token

curl -X POST "http://localhost:8000/auth/mfa/verify" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{

    "totp_token": "123456"
  }'

```


---


## 🌐 Base URL & Versioning

### Base URLs

|     Environment | Base URL     |
|    ------------|----------    |
|     Production | `https://your-domain.com/api/v2`     |
|     Staging | `https://staging.your-domain.com/api/v2`     |
|     Development | `http://localhost:8000/api/v2`     |

### API Versioning

The API uses URL path versioning:

- **Current Version**: `v2` (Latest)
- **Previous Version**: `v1` (Deprecated, will be removed in Q4 2025)
- **Version Header**: Optional `API-Version: v2` header support

### Content Type

All requests should use `Content-Type: application/json` unless specified otherwise.


---


## 📨 Request/Response Format

### Standard Request Format

```json

{
  "data": {
    // Request payload
  },
  "metadata": {
    "request_id": "req_123456789",
    "timestamp": "2025-07-24T10:30:00Z",
    "version": "v2"
  }
}

```

### Standard Response Format

#### Success Response

```json

{
  "success": true,
  "data": {
    // Response data
  },
  "metadata": {
    "request_id": "req_123456789",
    "timestamp": "2025-07-24T10:30:00Z",
    "execution_time_ms": 145,
    "version": "v2"
  },
  "pagination": {  // For paginated responses
    "page": 1,
    "per_page": 50,
    "total": 1250,
    "total_pages": 25,
    "has_next": true,
    "has_previous": false
  }
}

```

#### Error Response

```json

{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    },
    "documentation_url": "https://docs.business-intel-scraper.com/errors#validation-error"
  },
  "metadata": {
    "request_id": "req_123456789",
    "timestamp": "2025-07-24T10:30:00Z",
    "version": "v2"
  }
}

```


---


## 🚦 Rate Limiting

### Rate Limit Rules

|     Endpoint Category | Rate Limit | Burst | Block Duration     |
|    ------------------|------------|-------|----------------    |
|     Authentication | 10 req/min | 2 | 15 minutes     |
|     Data Retrieval | 100 req/min | 10 | 5 minutes     |
|     Data Search | 50 req/min | 5 | 5 minutes     |
|     Data Upload | 5 req/min | 1 | 10 minutes     |
|     Analytics | 30 req/min | 5 | 5 minutes     |
|     System Admin | 20 req/min | 3 | 10 minutes     |

### Rate Limit Headers

Every API response includes rate limiting information:

```http

X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1642781400
X-RateLimit-Burst: 10
X-RateLimit-Burst-Remaining: 8

```

### Rate Limit Exceeded Response

```json

{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 100,
      "window": 60,
      "retry_after": 45
    }
  }
}

```


---


## ❌ Error Handling

### HTTP Status Codes

|     Status Code | Description | Example     |
|    -------------|-------------|---------    |
|     `200` | Success | Request completed successfully     |
|     `201` | Created | Resource created successfully     |
|     `400` | Bad Request | Invalid request parameters     |
|     `401` | Unauthorized | Authentication required     |
|     `403` | Forbidden | Insufficient permissions     |
|     `404` | Not Found | Resource not found     |
|     `422` | Validation Error | Request validation failed     |
|     `429` | Rate Limited | Rate limit exceeded     |
|     `500` | Server Error | Internal server error     |
|     `503` | Service Unavailable | Service temporarily unavailable     |

### Error Codes

|     Code | Description | HTTP Status     |
|    ------|-------------|-------------    |
|     `VALIDATION_ERROR` | Request validation failed | 422     |
|     `AUTHENTICATION_REQUIRED` | Authentication token required | 401     |
|     `INVALID_CREDENTIALS` | Invalid username/password | 401     |
|     `TOKEN_EXPIRED` | Access token has expired | 401     |
|     `INSUFFICIENT_PERMISSIONS` | User lacks required permissions | 403     |
|     `RESOURCE_NOT_FOUND` | Requested resource not found | 404     |
|     `RATE_LIMIT_EXCEEDED` | Rate limit exceeded | 429     |
|     `SERVER_ERROR` | Internal server error | 500     |
|     `SERVICE_UNAVAILABLE` | Service temporarily unavailable | 503     |

### Error Response Examples

#### Validation Error

```json

{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "errors": [
        {
          "field": "email",
          "message": "Invalid email format",
          "code": "INVALID_FORMAT"
        },
        {
          "field": "password",
          "message": "Password must be at least 12 characters",
          "code": "MIN_LENGTH"
        }
      ]
    }
  }
}

```

#### Permission Error

```json

{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "User does not have required permissions",
    "details": {
      "required_permissions": ["admin", "user_management"],
      "user_permissions": ["analyst", "read_data"]
    }
  }
}

```


---


## 🔐 Authentication Endpoints

### POST /auth/login

Authenticate user and obtain access tokens.

**Request:**

```json

{
  "username": "user@example.com",
  "password": "secure_password",
  "mfa_token": "123456",  // Optional
  "remember_me": true     // Optional
}

```

**Response:**

```json

{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": "user_123",
      "username": "user@example.com",
      "role": "analyst",
      "permissions": ["read_data", "create_reports"],
      "mfa_enabled": true,
      "last_login": "2025-07-24T10:30:00Z"
    }
  }
}

```

### POST /auth/logout

Logout user and invalidate tokens.

**Request:**

```json

{
  "all_devices": false  // Optional: logout from all devices
}

```

**Response:**

```json

{
  "success": true,
  "data": {
    "message": "Successfully logged out"
  }
}

```

### POST /auth/refresh

Refresh expired access token.

**Request:**

```json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

```

**Response:**

```json

{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 1800
  }
}

```

### POST /auth/register

Register new user account (if registration is enabled).

**Request:**

```json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "secure_password123!",
  "first_name": "John",
  "last_name": "Doe",
  "role": "analyst"  // Optional, defaults to viewer
}

```

### GET /auth/me

Get current authenticated user information.

**Response:**

```json

{
  "success": true,
  "data": {
    "id": "user_123",
    "username": "user@example.com",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "analyst",
    "permissions": ["read_data", "create_reports"],
    "mfa_enabled": true,
    "created_at": "2025-01-15T09:00:00Z",
    "last_login": "2025-07-24T10:30:00Z",
    "active_sessions": 2
  }
}

```


---


## 📊 Data Management Endpoints

### GET /data

Retrieve collected data with filtering and pagination.

**Query Parameters:**

|     Parameter | Type | Description | Default     |
|    -----------|------|-------------|---------    |
|     `page` | integer | Page number | 1     |
|     `per_page` | integer | Items per page (max 1000) | 50     |
|     `data_type` | string | Filter by data type | all     |
|     `source_domain` | string | Filter by source domain | all     |
|     `date_from` | string | Start date (ISO format) | 24h ago     |
|     `date_to` | string | End date (ISO format) | now     |
|     `quality_min` | float | Minimum quality score | 0.0     |
|     `search` | string | Text search query | -     |
|     `sort_by` | string | Sort field | scraped_at     |
|     `sort_order` | string | Sort order (asc/desc) | desc     |

**Example Request:**

```bash

curl -X GET "http://localhost:8000/api/data?page=1&per_page=20&data_type=news&quality_min=70" \
  -H "Authorization: Bearer $TOKEN"

```

**Response:**

```json

{
  "success": true,
  "data": [
    {
      "id": "rec_123",
      "record_uuid": "550e8400-e29b-41d4-a716-446655440000",
      "title": "AI Technology Breakthrough",
      "summary": "Recent developments in artificial intelligence...",
      "source_url": "https://example.com/ai-news",
      "source_domain": "example.com",
      "data_type": "news",
      "content_category": "technology",
      "language": "en",
      "quality_score": 85.5,
      "completeness_score": 92.0,
      "word_count": 1250,
      "scraped_at": "2025-07-24T10:15:00Z",
      "published_at": "2025-07-24T08:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 15420,
    "total_pages": 771,
    "has_next": true,
    "has_previous": false
  }
}

```

### GET /data/{id}

Get specific data record by ID.

**Response:**

```json

{
  "success": true,
  "data": {
    "id": "rec_123",
    "record_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "title": "AI Technology Breakthrough",
    "extracted_text": "Full extracted text content...",
    "raw_data": {
      "original": "Original scraped data..."
    },
    "processed_data": {
      "cleaned": "Processed data..."
    },
    "metadata": {
      "extraction_method": "content_parser",
      "processing_time_ms": 450,
      "validation_checks": ["format", "quality", "completeness"]
    }
  }
}

```

### POST /data/search

Advanced data search with complex filters.

**Request:**

```json

{
  "query": "artificial intelligence machine learning",
  "filters": {
    "data_types": ["news", "research"],
    "source_domains": ["techcrunch.com", "arxiv.org"],
    "date_range": {
      "from": "2025-07-01T00:00:00Z",
      "to": "2025-07-24T23:59:59Z"
    },
    "quality_range": {
      "min": 70.0,
      "max": 100.0
    },
    "language": "en",
    "content_categories": ["technology", "science"]
  },
  "sort": {
    "field": "relevance",
    "order": "desc"
  },
  "pagination": {
    "page": 1,
    "per_page": 25
  },
  "highlight": true,
  "facets": ["data_type", "source_domain", "content_category"]
}

```

**Response:**

```json

{
  "success": true,
  "data": {
    "results": [
      {
        "id": "rec_123",
        "title": "AI Technology Breakthrough",
        "summary": "Recent developments in <mark>artificial intelligence</mark>...",
        "relevance_score": 0.95,
        "highlights": {
          "title": ["<mark>AI</mark> Technology Breakthrough"],
          "content": ["<mark>artificial intelligence</mark> and <mark>machine learning</mark>"]
        }
      }
    ],
    "facets": {
      "data_type": {
        "news": 150,
        "research": 45
      },
      "source_domain": {
        "techcrunch.com": 89,
        "arxiv.org": 67
      }
    },
    "query_info": {
      "query": "artificial intelligence machine learning",
      "search_time_ms": 45,
      "total_hits": 195
    }
  },
  "pagination": {
    "page": 1,
    "per_page": 25,
    "total": 195,
    "total_pages": 8
  }
}

```

### POST /data/export

Export data in various formats.

**Request:**

```json

{
  "format": "csv",  // csv, json, excel, pdf
  "filters": {
    "data_type": "news",
    "date_range": {
      "from": "2025-07-01T00:00:00Z",
      "to": "2025-07-24T23:59:59Z"
    }
  },
  "fields": ["title", "summary", "source_url", "scraped_at", "quality_score"],
  "options": {
    "include_metadata": true,
    "compress": true
  }
}

```

**Response:**

```json

{
  "success": true,
  "data": {
    "export_id": "exp_789",
    "download_url": "https://api.example.com/exports/exp_789/download",
    "expires_at": "2025-07-25T10:30:00Z",
    "file_size": 2048576,
    "record_count": 1250,
    "format": "csv"
  }
}

```

### DELETE /data/{id}

Delete specific data record.

**Response:**

```json

{
  "success": true,
  "data": {
    "message": "Data record deleted successfully",
    "deleted_id": "rec_123"
  }
}

```


---


## 📈 Analytics Endpoints

### GET /analytics/dashboard

Get dashboard analytics data.

**Query Parameters:**

|     Parameter | Type | Description | Default     |
|    -----------|------|-------------|---------    |
|     `time_range` | string | Time range (1h, 24h, 7d, 30d, 90d) | 24h     |
|     `data_types` | string | Comma-separated data types | all     |
|     `refresh` | boolean | Force refresh cached data | false     |

**Response:**

```json

{
  "success": true,
  "data": {
    "overview": {
      "total_records": 125680,
      "records_today": 3420,
      "growth_rate": 12.5,
      "avg_quality_score": 78.5,
      "active_jobs": 15,
      "data_sources": 45
    },
    "trends": {
      "collection_rate": [
        {"timestamp": "2025-07-24T00:00:00Z", "value": 145},
        {"timestamp": "2025-07-24T01:00:00Z", "value": 167}
      ],
      "quality_trends": [
        {"timestamp": "2025-07-24T00:00:00Z", "value": 76.2},
        {"timestamp": "2025-07-24T01:00:00Z", "value": 78.1}
      ]
    },
    "breakdown": {
      "by_data_type": {
        "news": 45680,
        "social_media": 32140,
        "ecommerce": 28560,
        "research": 19300
      },
      "by_source": {
        "techcrunch.com": 8520,
        "twitter.com": 7340,
        "amazon.com": 6890
      }
    },
    "performance": {
      "avg_processing_time_ms": 234,
      "success_rate": 94.5,
      "error_rate": 2.1,
      "cache_hit_rate": 87.3
    }
  }
}

```

### GET /analytics/metrics

Get specific analytics metrics.

**Query Parameters:**

|     Parameter | Type | Description     |
|    -----------|------|-------------    |
|     `metrics` | string | Comma-separated metric names     |
|     `time_range` | string | Time range for metrics     |
|     `aggregation` | string | Aggregation method (avg, sum, count)     |
|     `group_by` | string | Group results by field     |

**Available Metrics:**
- `collection_rate` - Data collection rate per hour
- `quality_score` - Average data quality score
- `processing_time` - Average processing time
- `success_rate` - Job success rate percentage
- `error_rate` - Error rate percentage
- `user_activity` - User activity metrics
- `system_performance` - System performance metrics

**Response:**

```json

{
  "success": true,
  "data": {
    "metrics": {
      "collection_rate": {
        "current": 156.5,
        "previous": 143.2,
        "change": 9.3,
        "unit": "records/hour"
      },
      "quality_score": {
        "current": 78.5,
        "previous": 76.8,
        "change": 2.2,
        "unit": "score"
      }
    },
    "time_series": [
      {
        "timestamp": "2025-07-24T10:00:00Z",
        "collection_rate": 156.5,
        "quality_score": 78.5
      }
    ]
  }
}

```

### POST /analytics/reports

Generate custom analytics reports.

**Request:**

```json

{
  "report_type": "weekly_summary",
  "parameters": {
    "date_range": {
      "from": "2025-07-17T00:00:00Z",
      "to": "2025-07-24T23:59:59Z"
    },
    "data_types": ["news", "social_media"],
    "include_charts": true,
    "include_tables": true
  },
  "format": "pdf",
  "delivery": {
    "method": "email",
    "recipients": ["analyst@company.com", "manager@company.com"],
    "schedule": "weekly"  // Optional: for recurring reports
  }
}

```

**Response:**

```json

{
  "success": true,
  "data": {
    "report_id": "rpt_456",
    "status": "generating",
    "estimated_completion": "2025-07-24T10:35:00Z",
    "download_url": null,  // Available when completed
    "preview_url": "https://api.example.com/reports/rpt_456/preview"
  }
}

```

### GET /analytics/insights

Get AI-generated insights and recommendations.

**Response:**

```json

{
  "success": true,
  "data": {
    "insights": [
      {
        "type": "trend",
        "category": "data_quality",
        "title": "Data Quality Improvement",
        "description": "Data quality scores have improved by 15% over the past week",
        "confidence": 0.92,
        "impact": "high",
        "action_items": [
          "Continue current data validation processes",
          "Consider expanding to similar data sources"
        ]
      },
      {
        "type": "anomaly",
        "category": "collection_rate",
        "title": "Collection Rate Spike",
        "description": "Unusual spike in data collection detected at 2 AM",
        "confidence": 0.87,
        "impact": "medium",
        "investigation_required": true
      }
    ],
    "recommendations": [
      {
        "type": "optimization",
        "title": "Optimize Collection Schedule",
        "description": "Adjust collection schedule to avoid peak server hours",
        "potential_improvement": "20% reduction in processing time",
        "implementation_effort": "low"
      }
    ]
  }
}

```


---


## 🔧 Job Management Endpoints

### GET /jobs

List all scraping jobs with filtering and pagination.

**Query Parameters:**

|     Parameter | Type | Description | Default     |
|    -----------|------|-------------|---------    |
|     `status` | string | Filter by job status | all     |
|     `type` | string | Filter by job type | all     |
|     `page` | integer | Page number | 1     |
|     `per_page` | integer | Items per page | 20     |
|     `sort_by` | string | Sort field | created_at     |

**Response:**

```json

{
  "success": true,
  "data": [
    {
      "id": "job_123",
      "name": "Tech News Scraper",
      "type": "web_scraping",
      "status": "running",
      "schedule": "0 */6 * * *",
      "next_run": "2025-07-24T16:00:00Z",
      "last_run": "2025-07-24T10:00:00Z",
      "success_rate": 94.5,
      "total_runs": 145,
      "failed_runs": 8,
      "created_at": "2025-07-01T09:00:00Z",
      "updated_at": "2025-07-24T10:30:00Z",
      "config": {
        "urls": ["https://techcrunch.com/feed"],
        "max_pages": 10,
        "respect_robots": true,
        "delay": 2
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 67,
    "total_pages": 4
  }
}

```

### POST /jobs

Create a new scraping job.

**Request:**

```json

{
  "name": "E-commerce Product Scraper",
  "type": "web_scraping",
  "description": "Scrape product data from e-commerce sites",
  "config": {
    "urls": [
      "https://example-shop.com/products",
      "https://another-shop.com/catalog"
    ],
    "max_pages": 50,
    "respect_robots": true,
    "delay": 3,
    "user_agent": "BusinessIntelScraper/2.0",
    "headers": {
      "Accept": "text/html,application/xhtml+xml"
    },
    "selectors": {
      "title": ".product-title",
      "price": ".price",
      "description": ".product-description"
    },
    "filters": {
      "min_price": 10,
      "categories": ["electronics", "clothing"]
    }
  },
  "schedule": "0 2 * * *",  // Daily at 2 AM
  "enabled": true,
  "notifications": {
    "on_success": ["admin@company.com"],
    "on_failure": ["admin@company.com", "ops@company.com"]
  },
  "retry_config": {
    "max_retries": 3,
    "retry_delay": 300
  }
}

```

**Response:**

```json

{
  "success": true,
  "data": {
    "id": "job_456",
    "name": "E-commerce Product Scraper",
    "status": "created",
    "next_run": "2025-07-25T02:00:00Z",
    "created_at": "2025-07-24T10:30:00Z"
  }
}

```

### GET /jobs/{id}

Get detailed information about a specific job.

**Response:**

```json

{
  "success": true,
  "data": {
    "id": "job_123",
    "name": "Tech News Scraper",
    "type": "web_scraping",
    "status": "running",
    "description": "Scrape technology news from major publications",
    "config": {
      "urls": ["https://techcrunch.com/feed"],
      "max_pages": 10,
      "respect_robots": true,
      "delay": 2
    },
    "schedule": "0 */6 * * *",
    "enabled": true,
    "created_at": "2025-07-01T09:00:00Z",
    "updated_at": "2025-07-24T10:30:00Z",
    "statistics": {
      "total_runs": 145,
      "successful_runs": 137,
      "failed_runs": 8,
      "success_rate": 94.5,
      "avg_runtime_seconds": 234,
      "total_records_collected": 5680,
      "last_successful_run": "2025-07-24T10:00:00Z"
    },
    "recent_runs": [
      {
        "run_id": "run_789",
        "started_at": "2025-07-24T10:00:00Z",
        "completed_at": "2025-07-24T10:04:15Z",
        "status": "completed",
        "records_collected": 42,
        "errors": 0
      }
    ]
  }
}

```

### PUT /jobs/{id}

Update job configuration.

**Request:**

```json

{
  "name": "Updated Tech News Scraper",
  "config": {
    "urls": [
      "https://techcrunch.com/feed",
      "https://venturebeat.com/feed"
    ],
    "max_pages": 15,
    "delay": 3
  },
  "schedule": "0 */4 * * *",  // Every 4 hours instead of 6
  "enabled": true
}

```

### DELETE /jobs/{id}

Delete a scraping job.

**Response:**

```json

{
  "success": true,
  "data": {
    "message": "Job deleted successfully",
    "deleted_id": "job_123"
  }
}

```

### POST /jobs/{id}/start

Start job execution immediately.

**Request:**

```json

{
  "force": false,  // Force start even if job is already running
  "priority": "normal"  // normal, high, low
}

```

**Response:**

```json

{
  "success": true,
  "data": {
    "run_id": "run_890",
    "job_id": "job_123",
    "status": "starting",
    "estimated_completion": "2025-07-24T10:45:00Z"
  }
}

```

### POST /jobs/{id}/stop

Stop running job.

**Response:**

```json

{
  "success": true,
  "data": {
    "message": "Job stopped successfully",
    "job_id": "job_123",
    "stopped_at": "2025-07-24T10:32:00Z"
  }
}

```

### GET /jobs/{id}/runs

Get job execution history.

**Query Parameters:**

|     Parameter | Type | Description | Default     |
|    -----------|------|-------------|---------    |
|     `status` | string | Filter by run status | all     |
|     `limit` | integer | Number of runs to return | 50     |
|     `offset` | integer | Offset for pagination | 0     |

**Response:**

```json

{
  "success": true,
  "data": [
    {
      "run_id": "run_789",
      "job_id": "job_123",
      "started_at": "2025-07-24T10:00:00Z",
      "completed_at": "2025-07-24T10:04:15Z",
      "status": "completed",
      "duration_seconds": 255,
      "records_collected": 42,
      "records_processed": 42,
      "errors": 0,
      "warnings": 1,
      "performance_metrics": {
        "avg_response_time_ms": 456,
        "total_requests": 15,
        "cache_hits": 3,
        "data_size_mb": 2.4
      },
      "error_details": null
    }
  ]
}

```


---


## 👥 User Management Endpoints

### GET /users

List all users (Admin only).

**Query Parameters:**

|     Parameter | Type | Description | Default     |
|    -----------|------|-------------|---------    |
|     `role` | string | Filter by user role | all     |
|     `status` | string | Filter by user status | all     |
|     `page` | integer | Page number | 1     |
|     `per_page` | integer | Items per page | 20     |

**Response:**

```json

{
  "success": true,
  "data": [
    {
      "id": "user_123",
      "username": "analyst1",
      "email": "analyst1@company.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "analyst",
      "status": "active",
      "mfa_enabled": true,
      "created_at": "2025-06-15T09:00:00Z",
      "last_login": "2025-07-24T08:30:00Z",
      "permissions": ["read_data", "create_reports", "manage_jobs"]
    }
  ]
}

```

### POST /users

Create new user (Admin only).

**Request:**

```json

{
  "username": "newanalyst",
  "email": "newanalyst@company.com",
  "password": "SecurePassword123!",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "analyst",
  "permissions": ["read_data", "create_reports"],
  "send_welcome_email": true
}

```

### GET /users/{id}

Get user details.

**Response:**

```json

{
  "success": true,
  "data": {
    "id": "user_123",
    "username": "analyst1",
    "email": "analyst1@company.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "analyst",
    "status": "active",
    "mfa_enabled": true,
    "created_at": "2025-06-15T09:00:00Z",
    "last_login": "2025-07-24T08:30:00Z",
    "permissions": ["read_data", "create_reports", "manage_jobs"],
    "activity_summary": {
      "total_logins": 156,
      "reports_created": 23,
      "jobs_managed": 8,
      "last_active": "2025-07-24T10:15:00Z"
    }
  }
}

```

### PUT /users/{id}

Update user information.

**Request:**

```json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@company.com",
  "role": "senior_analyst",
  "permissions": ["read_data", "create_reports", "manage_jobs", "export_data"]
}

```

### DELETE /users/{id}

Delete user account (Admin only).

### PUT /users/{id}/password

Change user password.

**Request:**

```json

{
  "current_password": "current_password",
  "new_password": "NewSecurePassword123!",
  "confirm_password": "NewSecurePassword123!"
}

```

### POST /users/{id}/reset-password

Reset user password (Admin only).

**Request:**

```json

{
  "send_email": true,
  "temporary_password": "TempPass123!"  // Optional
}

```


---


## 📊 System Monitoring Endpoints

### GET /system/health

Get overall system health status.

**Response:**

```json

{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-07-24T10:30:00Z",
    "uptime_seconds": 86400,
    "version": "2.0.0",
    "environment": "production",
    "components": {
      "api": {
        "status": "healthy",
        "response_time_ms": 15,
        "last_check": "2025-07-24T10:30:00Z"
      },
      "database": {
        "status": "healthy",
        "connection_pool": "8/20",
        "query_time_ms": 25,
        "last_check": "2025-07-24T10:30:00Z"
      },
      "cache": {
        "status": "healthy",
        "memory_usage": "245MB",
        "hit_rate": 87.3,
        "last_check": "2025-07-24T10:30:00Z"
      },
      "workers": {
        "status": "healthy",
        "active_workers": 4,
        "queue_size": 12,
        "last_check": "2025-07-24T10:30:00Z"
      }
    }
  }
}

```

### GET /system/metrics

Get detailed system performance metrics.

**Query Parameters:**

|     Parameter | Type | Description | Default     |
|    -----------|------|-------------|---------    |
|     `time_range` | string | Time range for metrics | 1h     |
|     `metrics` | string | Specific metrics to include | all     |
|     `aggregation` | string | Aggregation method | avg     |

**Response:**

```json

{
  "success": true,
  "data": {
    "system": {
      "cpu_percent": 45.2,
      "memory_percent": 62.1,
      "disk_usage_percent": 34.7,
      "network_io_mbps": 12.4
    },
    "application": {
      "active_connections": 156,
      "requests_per_minute": 234,
      "avg_response_time_ms": 85,
      "error_rate_percent": 0.8
    },
    "database": {
      "active_connections": 8,
      "queries_per_second": 45,
      "avg_query_time_ms": 25,
      "cache_hit_rate": 89.2
    },
    "jobs": {
      "active_jobs": 3,
      "completed_today": 45,
      "failed_today": 2,
      "avg_processing_time_ms": 2340
    }
  }
}

```

### GET /system/alerts

Get active system alerts.

**Response:**

```json

{
  "success": true,
  "data": [
    {
      "alert_id": "alert_456",
      "type": "performance",
      "severity": "warning",
      "title": "High CPU Usage",
      "message": "CPU usage has been above 80% for 5 minutes",
      "triggered_at": "2025-07-24T10:25:00Z",
      "status": "active",
      "component": "system",
      "metrics": {
        "current_cpu": 85.4,
        "threshold": 80.0
      }
    }
  ]
}

```

### GET /system/logs

Get system logs with filtering.

**Query Parameters:**

|     Parameter | Type | Description | Default     |
|    -----------|------|-------------|---------    |
|     `level` | string | Log level (debug, info, warning, error) | info     |
|     `component` | string | Filter by component | all     |
|     `since` | string | Logs since timestamp | 1h ago     |
|     `limit` | integer | Number of logs to return | 100     |

**Response:**

```json

{
  "success": true,
  "data": [
    {
      "timestamp": "2025-07-24T10:30:15Z",
      "level": "info",
      "component": "scraper",
      "message": "Job job_123 completed successfully",
      "metadata": {
        "job_id": "job_123",
        "duration_ms": 2340,
        "records_collected": 42
      }
    }
  ]
}

```


---


## 🔌 WebSocket API

### Connection

Connect to WebSocket for real-time updates:

```javascript

const ws = new WebSocket('ws://localhost:8000/ws');

```

### Authentication

Authenticate WebSocket connection:

```javascript

ws.send(JSON.stringify({
  type: 'auth',
  token: 'your_access_token'
}));

```

### Subscription

Subscribe to real-time channels:

```javascript

ws.send(JSON.stringify({
  type: 'subscribe',
  channels: ['job_updates', 'system_metrics', 'alerts', 'data_updates']
}));

```

### Message Types

#### Job Updates

```json

{
  "type": "job_update",
  "data": {
    "job_id": "job_123",
    "status": "running",
    "progress": 65,
    "records_collected": 28,
    "estimated_completion": "2025-07-24T10:35:00Z"
  }
}

```

#### System Metrics

```json

{
  "type": "system_metrics",
  "data": {
    "timestamp": "2025-07-24T10:30:00Z",
    "cpu_percent": 45.2,
    "memory_percent": 62.1,
    "active_connections": 156,
    "requests_per_minute": 234
  }
}

```

#### Alerts

```json

{
  "type": "alert",
  "data": {
    "alert_id": "alert_789",
    "severity": "warning",
    "title": "High Memory Usage",
    "message": "Memory usage has exceeded 85%",
    "triggered_at": "2025-07-24T10:30:00Z"
  }
}

```


---


## 🛠️ SDK & Examples

### Python SDK

```python

from business_intel_scraper_sdk import BusinessIntelClient

# Initialize client

client = BusinessIntelClient(
    base_url="http://localhost:8000",
    api_key="your_api_key"
)

# Authenticate

client.login(username="your_username", password="your_password")

# Get data

data = client.data.list(
    data_type="news",
    limit=50,
    quality_min=70
)

# Search data

results = client.data.search(
    query="artificial intelligence",
    filters={"data_type": "news", "language": "en"}
)

# Create job

job = client.jobs.create(
    name="Tech News Scraper",
    urls=["https://techcrunch.com/feed"],
    schedule="0 */6 * * *"
)

# Get analytics

metrics = client.analytics.get_dashboard_metrics(time_range="24h")

```

### JavaScript SDK

```javascript

import { BusinessIntelClient } from 'business-intel-scraper-sdk';

// Initialize client
const client = new BusinessIntelClient({
  baseURL: 'http://localhost:8000',
  apiKey: 'your_api_key'
});

// Authenticate
await client.auth.login({
  username: 'your_username',
  password: 'your_password'
});

// Get data
const data = await client.data.list({
  dataType: 'news',
  limit: 50,
  qualityMin: 70
});

// Real-time updates
client.ws.connect();
client.ws.subscribe(['job_updates', 'system_metrics']);
client.ws.on('job_update', (data) => {
  console.log('Job update:', data);
});

```

### cURL Examples

#### Authentication

```bash

# Login

curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Use token

export TOKEN="your_access_token"

```

#### Data Operations

```bash

# Get data

curl -X GET "http://localhost:8000/api/data?limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Search data

curl -X POST "http://localhost:8000/api/data/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI", "filters": {"data_type": "news"}}'

# Export data

curl -X POST "http://localhost:8000/api/data/export" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"format": "csv", "filters": {"data_type": "news"}}'

```

#### Job Management

```bash

# List jobs

curl -X GET "http://localhost:8000/api/jobs" \
  -H "Authorization: Bearer $TOKEN"

# Create job

curl -X POST "http://localhost:8000/api/jobs" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "News Scraper", "urls": ["https://example.com"]}'

# Start job

curl -X POST "http://localhost:8000/api/jobs/123/start" \
  -H "Authorization: Bearer $TOKEN"

```


---


## 📚 Additional Resources

- **Interactive API Docs**: Available at `/docs` endpoint
- **OpenAPI Spec**: Available at `/openapi.json`
- **Postman Collection**: [Download Collection](./postman/business-intel-scraper.json)
- **GitHub Repository**: [Source Code](https://github.com/Trashytalk/scraper)
- **Support**: support@business-intel-scraper.com


---


**Built with ❤️ by the Business Intelligence Scraper Team**
