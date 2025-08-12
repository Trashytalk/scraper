# API Documentation

This folder contains all API-related documentation for the Business Intelligence Scraper Platform.

## Files in this directory

- **API_DOCUMENTATION.md** - Complete API reference and usage guide
- **api-documentation.md** - Detailed API endpoint documentation
- **api_usage.md** - API usage examples and best practices

## API Status

**Current Status:** ✅ **PRODUCTION READY**
- Security-hardened API endpoints
- JWT authentication with enhanced security
- Rate limiting and input validation active
- Comprehensive endpoint documentation

## API Features

- **Authentication**: JWT-based with enhanced security
- **Rate Limiting**: Configurable per endpoint and user
- **Input Validation**: Comprehensive request validation
- **Security Headers**: CORS, CSP, and security middleware
- **Real-time**: WebSocket support for live updates

## Quick Links

- [Complete API Reference](API_DOCUMENTATION.md) - Full API documentation
- [API Endpoints](api-documentation.md) - Detailed endpoint reference
- [Usage Examples](api_usage.md) - API usage and examples

## API Endpoints

### Authentication
- `POST /api/auth/login` - User authentication
- `GET /api/auth/me` - Current user information

### Core Features
- `GET /api/jobs` - Job management
- `POST /api/jobs` - Create new jobs
- `GET /api/performance/metrics` - Performance monitoring

### Real-time
- `WebSocket /ws` - Real-time updates and notifications

## Related Files

- **API Server**: `/backend_server.py`
- **Security Config**: `/secure_config.py`
- **API Explorer**: `/docs/api_explorer.html`

---

**Last Updated:** August 9, 2025  
**Version:** v2.0.1-security
