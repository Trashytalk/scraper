"""
Enhanced API Documentation with OpenAPI/Swagger Integration
Provides comprehensive API documentation with examples and versioning
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
import os
from typing import Dict, Any

def create_enhanced_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """
    Create enhanced OpenAPI schema with comprehensive documentation
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Visual Analytics Platform API",
        version="3.0.0",
        description="""
# Visual Analytics Platform API

A comprehensive business intelligence and data visualization platform providing real-time analytics, 
network analysis, timeline visualization, and geospatial insights.

## Features

- **Real-time Data Processing**: WebSocket-based live data updates
- **Advanced Filtering**: Multi-dimensional data filtering with confidence thresholds
- **Data Export**: Multiple format support (JSON, CSV, Excel)
- **Network Analysis**: Entity relationship mapping and visualization
- **Timeline Analytics**: Temporal event analysis and visualization
- **Geospatial Intelligence**: Location-based data analysis and mapping
- **Performance Monitoring**: Built-in metrics and health monitoring

## Authentication

This API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Rate Limiting

API requests are limited to prevent abuse:
- **Standard Users**: 100 requests per minute
- **Premium Users**: 1000 requests per minute
- **Enterprise Users**: Unlimited

## Data Formats

All timestamps are in ISO 8601 format (UTC):
```
2025-01-21T10:30:00Z
```

Confidence scores are float values between 0.0 and 1.0:
```
0.0 = No confidence
0.5 = Medium confidence  
1.0 = High confidence
```

## Error Handling

Standard HTTP status codes are used:
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

Error responses include detailed information:
```json
{
    "error": "ValidationError",
    "message": "Invalid confidence threshold",
    "details": {
        "field": "confidence_threshold",
        "provided": 1.5,
        "expected": "float between 0.0 and 1.0"
    },
    "request_id": "req-123-456-789"
}
```
        """,
        routes=app.routes,
    )
    
    # Add custom sections
    openapi_schema["info"]["contact"] = {
        "name": "Visual Analytics Team",
        "email": "support@visualanalytics.com",
        "url": "https://visualanalytics.com/contact"
    }
    
    openapi_schema["info"]["license"] = {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    # Add servers
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.visualanalytics.com",
            "description": "Production server"
        },
        {
            "url": "https://staging-api.visualanalytics.com", 
            "description": "Staging server"
        }
    ]
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token obtained from authentication endpoint"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for service-to-service authentication"
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [
        {"BearerAuth": []},
        {"ApiKeyAuth": []}
    ]
    
    # Add custom tags with descriptions
    openapi_schema["tags"] = [
        {
            "name": "Health",
            "description": "System health and status monitoring endpoints"
        },
        {
            "name": "Authentication",
            "description": "User authentication and authorization endpoints"
        },
        {
            "name": "Network Analysis",
            "description": "Entity relationship and network analysis endpoints"
        },
        {
            "name": "Timeline Analytics",
            "description": "Temporal event analysis and timeline visualization endpoints"
        },
        {
            "name": "Geospatial Intelligence",
            "description": "Location-based data analysis and mapping endpoints"
        },
        {
            "name": "Data Export",
            "description": "Data export and download endpoints supporting multiple formats"
        },
        {
            "name": "Real-time Updates",
            "description": "WebSocket endpoints for real-time data streaming"
        },
        {
            "name": "Analytics & Metrics",
            "description": "Usage analytics and performance metrics endpoints"
        }
    ]
    
    # Enhanced examples for common request/response patterns
    openapi_schema["components"]["examples"] = {
        "FilterRequestExample": {
            "summary": "Advanced filtering example",
            "description": "Example of advanced filtering with multiple criteria",
            "value": {
                "entity_type": "person",
                "search_term": "analyst",
                "confidence_threshold": 0.8,
                "date_range": {
                    "start": "2024-01-01",
                    "end": "2024-12-31"
                }
            }
        },
        "NetworkDataResponse": {
            "summary": "Network data response example", 
            "description": "Example response from network data endpoint",
            "value": {
                "nodes": [
                    {
                        "id": "entity_1",
                        "label": "John Doe",
                        "type": "person",
                        "confidence": 0.95,
                        "properties": {
                            "role": "analyst",
                            "department": "finance"
                        }
                    }
                ],
                "edges": [
                    {
                        "id": "connection_1",
                        "source": "entity_1",
                        "target": "entity_2", 
                        "type": "works_with",
                        "weight": 0.8
                    }
                ],
                "metadata": {
                    "total_nodes": 50,
                    "total_edges": 125,
                    "applied_filters": {
                        "entity_type": "person",
                        "confidence_threshold": 0.8
                    },
                    "generated_at": "2025-01-21T10:30:00Z"
                }
            }
        },
        "ErrorResponse": {
            "summary": "Error response example",
            "description": "Standard error response format",
            "value": {
                "error": "ValidationError",
                "message": "Invalid confidence threshold",
                "details": {
                    "field": "confidence_threshold", 
                    "provided": 1.5,
                    "expected": "float between 0.0 and 1.0"
                },
                "request_id": "req-123-456-789",
                "timestamp": "2025-01-21T10:30:00Z"
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

def setup_api_documentation(app: FastAPI):
    """
    Set up enhanced API documentation with custom styling
    """
    
    # Custom OpenAPI schema
    app.openapi = lambda: create_enhanced_openapi_schema(app)
    
    # Custom docs endpoint with enhanced styling
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title="Visual Analytics API Documentation",
            swagger_js_url="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css",
            swagger_ui_parameters={
                "deepLinking": True,
                "displayRequestDuration": True,
                "docExpansion": "none",
                "operationsSorter": "method",
                "filter": True,
                "showExtensions": True,
                "showCommonExtensions": True,
                "defaultModelsExpandDepth": 2,
                "defaultModelExpandDepth": 2,
                "displayOperationId": True,
                "tryItOutEnabled": True
            }
        )
    
    # API versioning endpoint
    @app.get("/api/version", tags=["Health"])
    async def get_api_version():
        """
        Get API version information and compatibility details
        """
        return {
            "version": "3.0.0",
            "api_version": "v3",
            "release_date": "2025-01-21",
            "compatibility": {
                "minimum_client_version": "2.0.0",
                "supported_versions": ["v2", "v3"],
                "deprecated_versions": ["v1"],
                "sunset_dates": {
                    "v1": "2025-06-01",
                    "v2": "2026-01-01"
                }
            },
            "features": {
                "websocket_support": True,
                "real_time_updates": True,
                "advanced_filtering": True,
                "data_export": True,
                "authentication": "JWT",
                "rate_limiting": True
            },
            "endpoints": {
                "total": len([route for route in app.routes if hasattr(route, 'methods')]),
                "documentation": "/docs",
                "health_check": "/health",
                "openapi_schema": "/openapi.json"
            }
        }
    
    # API capabilities endpoint
    @app.get("/api/capabilities", tags=["Health"])
    async def get_api_capabilities():
        """
        Get detailed API capabilities and feature matrix
        """
        return {
            "data_types": {
                "entities": {
                    "supported_types": ["person", "organization", "location", "event", "document"],
                    "max_results": 1000,
                    "filtering": True,
                    "search": True
                },
                "connections": {
                    "relationship_types": ["connected_to", "works_with", "located_at", "owns"],
                    "directional": True,
                    "weighted": True
                },
                "events": {
                    "time_range_filtering": True,
                    "category_filtering": True,
                    "max_results": 10000
                },
                "locations": {
                    "coordinate_precision": "6 decimal places",
                    "address_geocoding": True,
                    "proximity_search": True
                }
            },
            "export_formats": {
                "supported": ["json", "csv", "excel", "pdf"],
                "compression": ["gzip", "zip"],
                "max_file_size": "100MB"
            },
            "real_time": {
                "websocket_support": True,
                "max_connections": 500,
                "message_types": ["data_update", "notification", "system_alert"],
                "heartbeat_interval": "30s"
            },
            "performance": {
                "rate_limits": {
                    "requests_per_minute": 100,
                    "burst_allowance": 20
                },
                "response_times": {
                    "target_p95": "200ms",
                    "target_p99": "500ms"
                },
                "availability_sla": "99.9%"
            }
        }

# API versioning utilities
class APIVersion:
    """API versioning utilities"""
    
    @staticmethod
    def get_version_from_header(request: Request) -> str:
        """Extract API version from Accept header"""
        accept_header = request.headers.get("Accept", "")
        
        # Look for version in Accept header: application/vnd.visualanalytics.v3+json
        if "vnd.visualanalytics.v" in accept_header:
            try:
                version_part = accept_header.split("vnd.visualanalytics.v")[1]
                version = version_part.split("+")[0]
                return f"v{version}"
            except IndexError:
                pass
        
        # Look for version in custom header
        version_header = request.headers.get("API-Version", "")
        if version_header:
            return version_header if version_header.startswith("v") else f"v{version_header}"
        
        # Default to latest version
        return "v3"
    
    @staticmethod
    def validate_version(version: str) -> bool:
        """Validate if API version is supported"""
        supported_versions = ["v2", "v3"]
        return version in supported_versions
    
    @staticmethod
    def get_deprecation_warning(version: str) -> str:
        """Get deprecation warning for version"""
        deprecation_dates = {
            "v1": "2025-06-01",
            "v2": "2026-01-01"
        }
        
        if version in deprecation_dates:
            return f"API version {version} is deprecated and will be sunset on {deprecation_dates[version]}"
        
        return ""

# Middleware for API versioning
async def api_versioning_middleware(request: Request, call_next):
    """Middleware to handle API versioning"""
    
    # Extract and validate API version
    version = APIVersion.get_version_from_header(request)
    
    if not APIVersion.validate_version(version):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "UnsupportedAPIVersion",
                "message": f"API version {version} is not supported",
                "supported_versions": ["v2", "v3"],
                "current_version": "v3"
            }
        )
    
    # Add version to request state
    request.state.api_version = version
    
    # Process request
    response = await call_next(request)
    
    # Add version headers to response
    response.headers["API-Version"] = version
    response.headers["API-Supported-Versions"] = "v2,v3"
    
    # Add deprecation warning if needed
    deprecation_warning = APIVersion.get_deprecation_warning(version)
    if deprecation_warning:
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = deprecation_warning.split("on ")[1]
        response.headers["Warning"] = f"299 - \"{deprecation_warning}\""
    
    return response
