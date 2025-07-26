# Contributing to Business Intelligence Scraper

Thank you for your interest in contributing to the Business Intelligence Scraper! This document provides guidelines for contributing to the project.

## 🚀 **Quick Start for Contributors**

### **Step 1: Get the Platform Running (2 minutes)**

Before contributing, get the platform running instantly with our automated setup:

```bash
# Clone and navigate
git clone https://github.com/Trashytalk/scraper.git
cd scraper

# Make script executable (first time only)
chmod +x quick_start.sh

# Start everything automatically
./quick_start.sh --dev
```

**✨ The `--dev` flag enables:**
- 🔄 Hot reload for code changes
- 🐛 Enhanced debugging output
- 📝 Development configuration
- 🧪 Test database setup
- 📊 Development monitoring

### **Step 2: Verify Your Setup**

After the quick start completes, verify everything is working:

```bash
# Check system status
./quick_start.sh --status

# Run a quick test
curl http://localhost:8000/health

# Access development interfaces
open http://localhost:8000        # Main dashboard
open http://localhost:8000/docs   # API documentation
```

### **Step 3: Development Workflow**

```bash
# Stop services when needed
./quick_start.sh --stop

# Clean install for troubleshooting
./quick_start.sh --clean

# Restart in development mode
./quick_start.sh --dev

# Get help and options
./quick_start.sh --help
```

## 📋 Development Guidelines

### Code Style
- **Python**: We use `black` for formatting and `ruff` for linting
- **Type Hints**: All new code should include type hints
- **Docstrings**: Use Google-style docstrings for all public functions/classes

```python
def extract_companies(html: str, country: str = "US") -> List[Dict[str, Any]]:
    """Extract company information from HTML content.
    
    Args:
        html: The HTML content to parse
        country: The country code for the registry
        
    Returns:
        List of dictionaries containing company data
        
    Raises:
        ParseError: If HTML content is malformed
    """
```

### Testing
- **Comprehensive Testing**: All new features must include comprehensive tests using our 9-category testing framework
- **Unit Tests**: Core functionality tests with business logic validation
- **Integration Tests**: End-to-end workflow testing with cross-component validation
- **Performance Tests**: Load testing and optimization validation for performance-critical features
- **Security Tests**: Authentication, authorization, and vulnerability assessment
- **GUI Tests**: Component testing and user interface validation for frontend features
- **Test Coverage**: Aim for >90% test coverage on new code (use `python3 tests/run_full_coverage.py --coverage`)
- **Test Naming**: Use descriptive test names that explain the scenario

```python
def test_company_registry_spider_handles_invalid_country_gracefully():
    """Test that spider logs warning and continues when given invalid country."""
```

### Git Workflow
1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make changes** and add tests
4. **Run the test suite**: `pytest`
5. **Commit changes**: Use conventional commit messages
6. **Push** to your fork
7. **Create a Pull Request**

### Commit Messages
Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
feat: add company registry spider for German companies
fix: handle timeout errors in proxy rotation
docs: update API documentation for new endpoints
test: add integration tests for OSINT workflows
```

## 🕷️ Adding New Spiders

### 1. Create Spider File
```python
# business_intel_scraper/backend/modules/spiders/my_spider.py
import scrapy
from typing import Generator, Dict, Any

class MySpider(scrapy.Spider):
    name = "my_spider"
    start_urls = ["https://example.com"]
    
    def parse(self, response: scrapy.http.Response) -> Generator[Dict[str, Any], None, None]:
        # Implementation here
        yield {"name": "Example Company"}
```

### 2. Add Tests
```python
# business_intel_scraper/backend/tests/test_my_spider.py
def test_my_spider_extracts_companies():
    # Test implementation
    pass
```

### 3. Update Spider Registry
Add your spider to the appropriate module's `__all__` list.

## 🔌 Adding Integrations

### 1. Create Integration Wrapper
```python
# business_intel_scraper/backend/integrations/my_tool_wrapper.py
def run_my_tool(*args: str) -> CompletedProcess[str]:
    """Run my_tool CLI with args."""
    if shutil.which("my_tool") is None:
        raise NotImplementedError("my_tool is not installed")
    return subprocess.run(["my_tool", *args], ...)
```

### 2. Add Celery Task
```python
# business_intel_scraper/backend/workers/tasks.py
@celery_app.task
def my_tool_scan(target: str) -> Dict[str, str]:
    """Run my_tool scan on target."""
    return run_my_tool(target)
```

### 3. Add API Endpoint (if needed)
```python
# business_intel_scraper/backend/api/main.py  
@app.post("/scan/my-tool")
async def start_my_tool_scan(target: str = Body(...)):
    task = my_tool_scan.delay(target)
    return {"task_id": task.id}
```

## 📊 Adding Data Exporters

```python
# business_intel_scraper/backend/utils/exporters.py
def export_to_my_format(data: List[Dict], **kwargs) -> str:
    """Export data to my custom format."""
    # Implementation
    return formatted_data
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment**: OS, Python version, package versions
2. **Steps to reproduce** the issue
3. **Expected behavior** vs **actual behavior**  
4. **Error messages** and stack traces
5. **Configuration** (redacted sensitive info)

Use our bug report template:

```markdown
**Environment:**
- OS: Ubuntu 20.04
- Python: 3.11.2
- Package version: 0.1.0

**Steps to reproduce:**
1. Run `./demo.sh`
2. Start company registry spider
3. Error occurs after 30 seconds

**Expected:** Spider should complete successfully
**Actual:** Spider crashes with timeout error

**Error:**
```
[paste error here]
```

**Configuration:**
```yaml
# .env (redacted)
DATABASE_URL=sqlite:///data.db
PROXY_URL=
```
```

## 💡 Feature Requests

For new features, please:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** and problem being solved
3. **Provide examples** of how it would be used
4. **Consider implementation** complexity and alternatives

## 📝 Documentation

- **API docs**: Update OpenAPI schemas for new endpoints
- **User guides**: Add to `docs/` directory using Markdown
- **Code examples**: Include working examples in docstrings
- **Architecture docs**: Update `docs/architecture.md` for major changes

## 🧪 Testing Guidelines

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest business_intel_scraper/backend/tests/test_my_feature.py

# With coverage
pytest --cov=business_intel_scraper

# Integration tests (requires Docker)
pytest -m integration
```

### Test Categories
- **Unit tests**: Fast, isolated, no external dependencies
- **Integration tests**: Test component interactions
- **End-to-end tests**: Full workflow tests with Docker

### Mocking External Services
```python
def test_api_call(monkeypatch):
    def mock_get(url, **kwargs):
        return MockResponse({"status": "ok"})
    
    monkeypatch.setattr("requests.get", mock_get)
    # Test implementation
```

## 🏷️ Release Process

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with new features/fixes
3. **Create release PR** with version bump
4. **Tag release** after merge: `git tag v0.2.0`
5. **Automated deployment** will handle the rest

## 💬 Getting Help

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Use GitHub Issues for bugs and feature requests
- **Documentation**: Check `docs/` directory first
- **Examples**: See `examples/` directory for usage patterns

## 🎯 Good First Issues

Look for issues tagged with `good-first-issue`:
- Documentation improvements
- Test additions
- Simple spider implementations
- Bug fixes with clear reproduction steps

## 📜 Code of Conduct

Please note that this project follows a Code of Conduct. By participating, you agree to abide by its terms:

- **Be respectful** and inclusive
- **Focus on constructive feedback**
- **Help others learn** and grow
- **Respect different perspectives** and experiences

## 🙏 Recognition

Contributors will be recognized in:
- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions  
- **Documentation** for major features

Thank you for helping make Business Intelligence Scraper better! 🚀
