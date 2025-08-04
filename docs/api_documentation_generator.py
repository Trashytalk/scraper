#!/usr/bin/env python3
"""
API Documentation Generator
Automatically generates comprehensive API documentation from FastAPI application
"""

import json
import yaml
import inspect
from typing import Dict, Any, List, Optional
from pathlib import Path
import markdown
from datetime import datetime

class APIDocumentationGenerator:
    """Generates comprehensive API documentation"""
    
    def __init__(self, app, output_dir: str = "docs/api"):
        self.app = app
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # API metadata
        self.api_info = {
            "title": "Business Intelligence Scraper API",
            "version": "2.0.0",
            "description": "Comprehensive API for automated data collection and business intelligence",
            "contact": {
                "name": "API Support",
                "email": "api-support@business-intel-scraper.com",
                "url": "https://business-intel-scraper.com/support"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        }
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification"""
        
        # Get OpenAPI schema from FastAPI
        openapi_schema = self.app.openapi()
        
        # Enhance with additional metadata
        openapi_schema.update({
            "info": self.api_info,
            "servers": [
                {
                    "url": "https://api.business-intel-scraper.com",
                    "description": "Production server"
                },
                {
                    "url": "https://staging-api.business-intel-scraper.com", 
                    "description": "Staging server"
                },
                {
                    "url": "http://localhost:8000",
                    "description": "Development server"
                }
            ],
            "security": [
                {"bearerAuth": []},
                {"apiKeyAuth": []}
            ],
            "components": {
                **openapi_schema.get("components", {}),
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": "JWT token obtained from /api/auth/login"
                    },
                    "apiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key",
                        "description": "API key for service-to-service authentication"
                    }
                },
                "responses": {
                    "UnauthorizedError": {
                        "description": "Authentication information is missing or invalid",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                        "message": {"type": "string"},
                                        "timestamp": {"type": "string", "format": "date-time"}
                                    }
                                }
                            }
                        }
                    },
                    "ValidationError": {
                        "description": "Request validation failed",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                        "details": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "field": {"type": "string"},
                                                    "message": {"type": "string"},
                                                    "code": {"type": "string"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "RateLimitError": {
                        "description": "Rate limit exceeded",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                        "retry_after": {"type": "integer"},
                                        "limit": {"type": "integer"},
                                        "window": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "tags": [
                {
                    "name": "Authentication",
                    "description": "User authentication and session management"
                },
                {
                    "name": "Jobs",
                    "description": "Scraping job management and execution"
                },
                {
                    "name": "Data",
                    "description": "Data retrieval and management"
                },
                {
                    "name": "Analytics",
                    "description": "Analytics and reporting"
                },
                {
                    "name": "System",
                    "description": "System health and monitoring"
                },
                {
                    "name": "Database",
                    "description": "Database management and operations"
                }
            ]
        })
        
        return openapi_schema
    
    def generate_markdown_docs(self) -> str:
        """Generate comprehensive Markdown documentation"""
        
        openapi_spec = self.generate_openapi_spec()
        
        doc_content = f"""# {self.api_info['title']} Documentation

## Overview

{self.api_info['description']}

**Version:** {self.api_info['version']}  
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Base URLs

- **Production:** `https://api.business-intel-scraper.com`
- **Staging:** `https://staging-api.business-intel-scraper.com`
- **Development:** `http://localhost:8000`

## Authentication

The API supports two authentication methods:

### 1. JWT Bearer Token (Recommended)

```http
Authorization: Bearer <jwt_token>
```

Obtain a JWT token by authenticating with the `/api/auth/login` endpoint:

```bash
curl -X POST "https://api.business-intel-scraper.com/api/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{{"username": "your_username", "password": "your_password"}}'
```

### 2. API Key

```http
X-API-Key: <your_api_key>
```

API keys can be generated in the dashboard under Settings > API Keys.

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Free tier:** 100 requests per hour
- **Pro tier:** 1,000 requests per hour  
- **Enterprise tier:** 10,000 requests per hour

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in window
- `X-RateLimit-Reset`: Window reset time (Unix timestamp)

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{{
  "success": true,
  "data": {{
    // Response data
  }},
  "metadata": {{
    "timestamp": "2025-01-31T12:00:00Z",
    "request_id": "req_12345",
    "version": "2.0.0"
  }}
}}
```

### Error Response
```json
{{
  "success": false,
  "error": {{
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {{
        "field": "email",
        "message": "Invalid email format",
        "code": "INVALID_FORMAT"
      }}
    ]
  }},
  "metadata": {{
    "timestamp": "2025-01-31T12:00:00Z",
    "request_id": "req_12345"
  }}
}}
```

## Endpoints

"""
        
        # Group endpoints by tags
        paths = openapi_spec.get("paths", {})
        tags = {tag["name"]: tag["description"] for tag in openapi_spec.get("tags", [])}
        
        endpoints_by_tag = {}
        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    tag = details.get("tags", ["Other"])[0]
                    if tag not in endpoints_by_tag:
                        endpoints_by_tag[tag] = []
                    endpoints_by_tag[tag].append({
                        "path": path,
                        "method": method.upper(),
                        "details": details
                    })
        
        # Generate documentation for each tag
        for tag, description in tags.items():
            if tag in endpoints_by_tag:
                doc_content += f"\n### {tag}\n\n{description}\n\n"
                
                for endpoint in endpoints_by_tag[tag]:
                    doc_content += self._generate_endpoint_docs(endpoint)
        
        # Add examples section
        doc_content += self._generate_examples_section()
        
        # Add SDK section
        doc_content += self._generate_sdk_section()
        
        # Add changelog section
        doc_content += self._generate_changelog_section()
        
        return doc_content
    
    def _generate_endpoint_docs(self, endpoint: Dict[str, Any]) -> str:
        """Generate documentation for a single endpoint"""
        path = endpoint["path"]
        method = endpoint["method"]
        details = endpoint["details"]
        
        summary = details.get("summary", "")
        description = details.get("description", "")
        
        doc = f"#### {method} {path}\n\n"
        
        if summary:
            doc += f"**{summary}**\n\n"
        
        if description:
            doc += f"{description}\n\n"
        
        # Parameters
        parameters = details.get("parameters", [])
        if parameters:
            doc += "**Parameters:**\n\n"
            for param in parameters:
                required = " (required)" if param.get("required") else " (optional)"
                param_type = param.get("schema", {}).get("type", "string")
                doc += f"- `{param['name']}` ({param['in']}, {param_type}){required}: {param.get('description', '')}\n"
            doc += "\n"
        
        # Request body
        request_body = details.get("requestBody")
        if request_body:
            doc += "**Request Body:**\n\n"
            content = request_body.get("content", {})
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                doc += "```json\n"
                doc += json.dumps(self._generate_example_from_schema(schema), indent=2)
                doc += "\n```\n\n"
        
        # Responses
        responses = details.get("responses", {})
        if responses:
            doc += "**Responses:**\n\n"
            for status_code, response in responses.items():
                desc = response.get("description", "")
                doc += f"- `{status_code}`: {desc}\n"
            
            # Example success response
            if "200" in responses:
                content = responses["200"].get("content", {})
                if "application/json" in content:
                    schema = content["application/json"].get("schema", {})
                    doc += "\n**Example Response:**\n\n"
                    doc += "```json\n"
                    doc += json.dumps(self._generate_example_from_schema(schema), indent=2)
                    doc += "\n```\n\n"
        
        # cURL example
        doc += "**Example Request:**\n\n"
        doc += f"```bash\ncurl -X {method} \"https://api.business-intel-scraper.com{path}\" \\\\\n"
        doc += "  -H \"Authorization: Bearer <jwt_token>\" \\\\\n"
        doc += "  -H \"Content-Type: application/json\"\n```\n\n"
        
        doc += "---\n\n"
        
        return doc
    
    def _generate_example_from_schema(self, schema: Dict[str, Any]) -> Any:
        """Generate example data from JSON schema"""
        schema_type = schema.get("type")
        
        if schema_type == "object":
            example = {}
            properties = schema.get("properties", {})
            for prop_name, prop_schema in properties.items():
                example[prop_name] = self._generate_example_from_schema(prop_schema)
            return example
        
        elif schema_type == "array":
            items_schema = schema.get("items", {})
            return [self._generate_example_from_schema(items_schema)]
        
        elif schema_type == "string":
            format_type = schema.get("format")
            if format_type == "email":
                return "user@example.com"
            elif format_type == "date-time":
                return "2025-01-31T12:00:00Z"
            elif format_type == "date":
                return "2025-01-31"
            elif format_type == "uri":
                return "https://example.com"
            else:
                return schema.get("example", "string_value")
        
        elif schema_type == "integer":
            return schema.get("example", 123)
        
        elif schema_type == "number":
            return schema.get("example", 123.45)
        
        elif schema_type == "boolean":
            return schema.get("example", True)
        
        else:
            return schema.get("example", "example_value")
    
    def _generate_examples_section(self) -> str:
        """Generate comprehensive examples section"""
        return """
## Examples

### Complete Workflow Example

Here's a complete example of creating and running a scraping job:

```python
import requests
import time

# 1. Authenticate
auth_response = requests.post(
    "https://api.business-intel-scraper.com/api/auth/login",
    json={"username": "your_username", "password": "your_password"}
)
token = auth_response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# 2. Create a scraping job
job_data = {
    "name": "Wikipedia Python Article",
    "type": "web_scraping",
    "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "scraper_type": "basic",
    "config": {
        "crawl_links": True,
        "max_pages": 10,
        "include_images": True
    }
}

job_response = requests.post(
    "https://api.business-intel-scraper.com/api/jobs",
    json=job_data,
    headers=headers
)
job_id = job_response.json()["data"]["job_id"]

# 3. Start the job
requests.post(
    f"https://api.business-intel-scraper.com/api/jobs/{job_id}/start",
    headers=headers
)

# 4. Monitor job progress
while True:
    status_response = requests.get(
        f"https://api.business-intel-scraper.com/api/jobs/{job_id}/status",
        headers=headers
    )
    status = status_response.json()["data"]["status"]
    
    if status in ["completed", "failed"]:
        break
    
    time.sleep(5)

# 5. Get results
results_response = requests.get(
    f"https://api.business-intel-scraper.com/api/jobs/{job_id}/results",
    headers=headers
)
results = results_response.json()["data"]

print(f"Collected {len(results)} records")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

class BusinessIntelAPI {
    constructor(baseURL = 'https://api.business-intel-scraper.com') {
        this.baseURL = baseURL;
        this.token = null;
    }

    async authenticate(username, password) {
        const response = await axios.post(`${this.baseURL}/api/auth/login`, {
            username,
            password
        });
        this.token = response.data.access_token;
        return this.token;
    }

    async createJob(jobConfig) {
        const response = await axios.post(
            `${this.baseURL}/api/jobs`,
            jobConfig,
            { headers: { Authorization: `Bearer ${this.token}` } }
        );
        return response.data.data.job_id;
    }

    async getJobResults(jobId) {
        const response = await axios.get(
            `${this.baseURL}/api/jobs/${jobId}/results`,
            { headers: { Authorization: `Bearer ${this.token}` } }
        );
        return response.data.data;
    }
}

// Usage
const api = new BusinessIntelAPI();
await api.authenticate('username', 'password');
const jobId = await api.createJob({
    name: 'Test Job',
    type: 'web_scraping',
    url: 'https://example.com'
});
const results = await api.getJobResults(jobId);
```

"""
    
    def _generate_sdk_section(self) -> str:
        """Generate SDK and tools section"""
        return """
## SDKs and Tools

### Official SDKs

- **Python SDK:** `pip install business-intel-scraper-sdk`
- **JavaScript SDK:** `npm install business-intel-scraper-sdk`
- **Go SDK:** Available on GitHub
- **PHP SDK:** Available via Composer

### Third-Party Tools

- **Postman Collection:** [Download here](https://business-intel-scraper.com/postman)
- **OpenAPI Spec:** [Download here](https://api.business-intel-scraper.com/openapi.json)
- **Insomnia Workspace:** [Download here](https://business-intel-scraper.com/insomnia)

### Code Generators

Generate client code in your preferred language using OpenAPI generators:

```bash
# Generate Python client
openapi-generator-cli generate \\
  -i https://api.business-intel-scraper.com/openapi.json \\
  -g python \\
  -o ./python-client

# Generate Java client  
openapi-generator-cli generate \\
  -i https://api.business-intel-scraper.com/openapi.json \\
  -g java \\
  -o ./java-client
```

"""
    
    def _generate_changelog_section(self) -> str:
        """Generate API changelog section"""
        return """
## Changelog

### Version 2.0.0 (2025-01-31)

**🎉 Major Release**

**Added:**
- Database management endpoints (`/api/database/*`)
- Enhanced authentication with JWT refresh tokens
- Rate limiting with tier-based limits
- WebSocket support for real-time updates
- Bulk operations for jobs and data
- Advanced filtering and pagination
- Export functionality (CSV, JSON, Excel)

**Changed:**
- Improved error response format with detailed validation errors
- Enhanced security with request signing
- Updated response metadata structure
- Standardized timestamp format (ISO 8601)

**Deprecated:**
- Legacy authentication endpoints (will be removed in v3.0.0)
- Old job status format (use new structured format)

**Security:**
- Added request signature verification
- Enhanced rate limiting algorithms
- Improved input validation and sanitization
- Added security headers to all responses

### Version 1.5.0 (2024-12-15)

**Added:**
- Analytics endpoints
- Performance monitoring
- Health check improvements

**Fixed:**
- Job status update reliability
- Memory optimization for large datasets
- Error handling improvements

### Version 1.0.0 (2024-10-01)

**🚀 Initial Release**

- Core scraping functionality
- Basic authentication
- Job management
- Data retrieval
- System monitoring

"""
    
    def generate_all_docs(self):
        """Generate all documentation formats"""
        print("🚀 Generating API Documentation...")
        
        # Generate OpenAPI specification
        openapi_spec = self.generate_openapi_spec()
        
        # Save OpenAPI JSON
        openapi_json_path = self.output_dir / "openapi.json"
        with open(openapi_json_path, 'w') as f:
            json.dump(openapi_spec, f, indent=2)
        print(f"✅ OpenAPI JSON saved to {openapi_json_path}")
        
        # Save OpenAPI YAML
        openapi_yaml_path = self.output_dir / "openapi.yaml"
        with open(openapi_yaml_path, 'w') as f:
            yaml.dump(openapi_spec, f, default_flow_style=False)
        print(f"✅ OpenAPI YAML saved to {openapi_yaml_path}")
        
        # Generate Markdown documentation
        markdown_content = self.generate_markdown_docs()
        markdown_path = self.output_dir / "README.md"
        with open(markdown_path, 'w') as f:
            f.write(markdown_content)
        print(f"✅ Markdown documentation saved to {markdown_path}")
        
        # Generate HTML documentation
        html_content = markdown.markdown(markdown_content, extensions=['toc', 'codehilite'])
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.api_info['title']} Documentation</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 20px; max-width: 1200px; margin: 0 auto; }}
        h1, h2, h3, h4 {{ color: #333; }}
        code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        .toc {{ background: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .endpoint {{ border-left: 4px solid #007bff; padding-left: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
        """
        
        html_path = self.output_dir / "index.html"
        with open(html_path, 'w') as f:
            f.write(html_template)
        print(f"✅ HTML documentation saved to {html_path}")
        
        print(f"\n🎉 Documentation generation complete!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"🌐 View HTML docs: file://{html_path.absolute()}")

if __name__ == "__main__":
    # This would normally import your FastAPI app
    # from backend_server import app
    
    # For demo purposes, create a mock app
    class MockApp:
        def openapi(self):
            return {
                "openapi": "3.0.0",
                "info": {"title": "API", "version": "1.0.0"},
                "paths": {
                    "/api/health": {
                        "get": {
                            "summary": "Health Check",
                            "description": "Check API health status",
                            "tags": ["System"],
                            "responses": {
                                "200": {
                                    "description": "API is healthy",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "type": "object",
                                                "properties": {
                                                    "status": {"type": "string"},
                                                    "timestamp": {"type": "string"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
    
    app = MockApp()
    generator = APIDocumentationGenerator(app)
    generator.generate_all_docs()
