# Phase 2: DOM Change Detection & Spider Updates

## Overview

Phase 2 implements intelligent DOM change detection and automatic spider maintenance, building on the foundation of Phase 1's automated source discovery. This phase ensures your scraping infrastructure remains resilient to website changes through proactive monitoring and automatic adaptation.

## Key Features

### 🔍 DOM Structure Analysis
- **Fingerprinting**: Creates unique structural signatures for web pages
- **Element Analysis**: Tracks HTML structure, CSS selectors, and form elements  
- **API Detection**: Automatically identifies JavaScript API endpoints
- **Content Monitoring**: Monitors key data extraction points

### 🔄 Change Detection
- **Structural Changes**: Detects layout and DOM structure modifications
- **Selector Changes**: Identifies when CSS selectors become invalid
- **Form Changes**: Monitors form field modifications and new requirements
- **API Changes**: Tracks endpoint modifications and parameter updates

### 🔧 Automatic Spider Updates
- **Code Analysis**: Understands spider code patterns and dependencies
- **Automatic Fixes**: Applies fixes for common selector and structure changes
- **Backup & Rollback**: Creates backups before modifications with rollback capability
- **Update Tracking**: Maintains history of all modifications and their success rates

### ⏰ Scheduled Monitoring
- **Proactive Monitoring**: Regular checks for changes before spiders break
- **Intelligent Scheduling**: Configurable intervals based on site change frequency
- **Priority Processing**: High-impact changes processed first
- **Comprehensive Reporting**: Detailed reports on changes and update status

## Architecture

```
Phase 2 Components:
├── DOM Change Detection
│   ├── DOMAnalyzer - Page structure analysis
│   ├── DOMFingerprint - Structural signatures
│   └── DOMChangeDetector - Change identification
├── Spider Update System  
│   ├── SpiderTemplate - Code pattern analysis
│   ├── SpiderUpdater - Automatic code fixes
│   └── SpiderUpdateScheduler - Update orchestration
└── Celery Integration
    ├── Scheduled Tasks - Automated monitoring
    ├── Change Processing - Batch change handling
    └── Report Generation - Status reporting
```

## Installation & Setup

### Prerequisites
Phase 2 builds on Phase 1 infrastructure. Ensure Phase 1 is installed and configured.

### Configuration
Add Phase 2 settings to your configuration:

```yaml
# config/config.yaml
phase2:
  dom_monitoring:
    enabled: true
    check_interval: 14400  # 4 hours
    max_concurrent_checks: 10
    change_threshold: 0.1
    
  spider_updates:
    enabled: true
    auto_fix_enabled: true
    backup_enabled: true
    rollback_on_failure: true
    update_interval: 28800  # 8 hours
    
  reporting:
    enabled: true
    daily_reports: true
    email_notifications: true
    report_retention_days: 30
```

### Database Migration
Phase 2 adds new tables for change tracking:

```bash
cd business_intel_scraper/backend/db
alembic upgrade head
```

## Usage

### Command Line Interface

#### DOM Change Detection

```bash
# Check specific URLs for changes
python -m business_intel_scraper dom-changes check \
    --urls https://example.com https://test-site.com \
    --output changes.json

# Analyze page structure
python -m business_intel_scraper dom-changes analyze https://example.com

# List recent changes
python -m business_intel_scraper dom-changes list --days 7 --severity high

# Generate change report
python -m business_intel_scraper dom-changes report --days 30 --output report.json
```

#### Spider Updates

```bash
# Check and update spiders automatically
python -m business_intel_scraper spider-updates check --auto-fix

# Check spiders for specific URL
python -m business_intel_scraper spider-updates check --url https://example.com

# Show update status
python -m business_intel_scraper spider-updates status --days 30

# View update history
python -m business_intel_scraper spider-updates history --limit 20
```

#### Demo Mode

```bash
# Run full Phase 2 demonstration
python -m business_intel_scraper demo

# Run specific demo components
python -m business_intel_scraper demo --component dom
python -m business_intel_scraper demo --component changes
python -m business_intel_scraper demo --component updates
```

### Python API

#### DOM Analysis Example

```python
import asyncio
from business_intel_scraper.backend.discovery.dom_change_detection import DOMAnalyzer

async def analyze_site():
    analyzer = DOMAnalyzer()
    
    # Analyze page structure
    fingerprint = await analyzer.analyze_page(
        "https://example.com", 
        html_content
    )
    
    print(f"Structure hash: {fingerprint.structure_hash}")
    print(f"Key selectors: {len(fingerprint.key_selectors)}")
    print(f"Forms found: {len(fingerprint.form_signatures)}")

asyncio.run(analyze_site())
```

#### Change Detection Example

```python
from business_intel_scraper.backend.discovery.dom_change_detection import DOMChangeDetector

async def monitor_changes():
    detector = DOMChangeDetector()
    
    # Check for changes
    changes = await detector.check_for_changes(url, new_html_content)
    
    for change in changes:
        print(f"Change detected: {change.description}")
        print(f"Severity: {change.severity}")
        if change.auto_fixable:
            print(f"Auto-fix: {change.suggested_fixes[0]}")

asyncio.run(monitor_changes())
```

#### Spider Update Example

```python
from business_intel_scraper.backend.discovery.spider_update_system import SpiderUpdater

async def update_spiders():
    updater = SpiderUpdater()
    
    # Get recent changes
    changes = detector.get_critical_changes(days=1)
    
    # Apply updates
    results = await updater.update_spiders_for_changes(changes)
    
    print(f"Updated {results['spiders_updated']} spiders")
    print(f"Applied {results['automatic_fixes']} automatic fixes")
```

## Celery Integration

Phase 2 adds several scheduled tasks to your Celery worker system:

### Scheduled Tasks

- **`check-dom-changes`**: Every 4 hours - Monitor sites for DOM changes
- **`update-spider-logic`**: Every 8 hours - Apply automatic spider updates  
- **`generate-dom-change-report`**: Daily - Generate comprehensive change reports
- **`spider-health-check`**: Every 6 hours - Verify spider functionality

### Manual Task Execution

```python
# Trigger immediate DOM check
from business_intel_scraper.backend.workers.tasks import check_dom_changes
result = check_dom_changes.delay(['https://example.com'])

# Trigger spider updates
from business_intel_scraper.backend.workers.tasks import update_spider_logic
result = update_spider_logic.delay()
```

## Change Detection Types

### Structural Changes
- **Element Addition/Removal**: New or removed HTML elements
- **Hierarchy Changes**: Modified DOM structure or nesting
- **Class/ID Changes**: Updated CSS classes or element IDs

### Selector Changes
- **CSS Selector Updates**: Changed selectors for data extraction
- **Attribute Changes**: Modified or new HTML attributes
- **XPath Changes**: Updated XPath expressions

### Form Changes
- **Field Modifications**: New, removed, or renamed form fields
- **Validation Changes**: Updated form validation requirements
- **Submission Changes**: Modified form action URLs or methods

### API Changes
- **Endpoint Changes**: New or modified API endpoints
- **Parameter Changes**: Updated API parameters or formats
- **Authentication Changes**: Modified authentication requirements

## Automatic Fix Types

### Simple Fixes (Auto-Applied)
- CSS selector updates
- Attribute name changes
- Class/ID modifications
- Simple form field updates

### Complex Fixes (Manual Review)
- Structural reorganization
- New authentication requirements
- Significant API changes
- Logic flow modifications

## Monitoring & Reporting

### Change Severity Levels

- **🟢 Low**: Minor cosmetic changes with no scraping impact
- **🟡 Medium**: Changes that may affect data extraction quality
- **🟠 High**: Changes likely to break existing spiders
- **🔴 Critical**: Changes that will immediately break spiders

### Reports Include

- Change frequency and patterns
- Spider update success rates
- Site reliability metrics
- Maintenance recommendations
- Performance impact analysis

### Alerting

- **Email Notifications**: Critical changes and update failures
- **Slack Integration**: Real-time alerts for high-priority changes
- **Dashboard Alerts**: Visual indicators in monitoring interface
- **API Webhooks**: Custom integration endpoints

## Best Practices

### Monitoring Configuration

1. **Set Appropriate Intervals**: Balance detection speed with resource usage
2. **Configure Thresholds**: Avoid false positives from minor changes
3. **Prioritize Sources**: Monitor high-value sources more frequently
4. **Test Rollback**: Ensure rollback procedures work correctly

### Spider Maintenance

1. **Regular Backups**: Maintain versioned spider backups
2. **Update Testing**: Validate updates in staging environments
3. **Manual Review**: Review complex changes before applying
4. **Performance Monitoring**: Track spider performance post-update

### Change Management

1. **Change Documentation**: Document all detected and applied changes
2. **Review Cycles**: Regular review of change patterns and update success
3. **Threshold Tuning**: Adjust detection sensitivity based on experience
4. **Team Coordination**: Coordinate manual reviews with development team

## Integration with Phase 1

Phase 2 seamlessly integrates with Phase 1 capabilities:

### Enhanced Discovery
- **Source Monitoring**: Continuously monitors discovered sources
- **Quality Assessment**: Tracks source reliability over time
- **Dynamic Adaptation**: Updates spider behavior based on changes

### Improved Generation
- **Template Updates**: Updates spider templates based on change patterns
- **Best Practices**: Incorporates learned patterns into new spider generation
- **Resilient Code**: Generates more change-resistant spider code

## Troubleshooting

### Common Issues

**High False Positive Rate**
- Adjust change threshold in configuration
- Exclude dynamic content areas from monitoring
- Fine-tune CSS selector matching

**Update Failures**
- Check backup and rollback procedures
- Review manual intervention requirements
- Validate spider dependencies

**Performance Impact**
- Adjust monitoring intervals
- Optimize concurrent check limits
- Review resource allocation

### Debug Mode

```bash
# Enable debug logging
export BI_SCRAPER_DEBUG=true

# Run with verbose output
python -m business_intel_scraper dom-changes check --urls https://example.com --verbose

# Check Celery task status
celery -A business_intel_scraper.backend.workers.celery_config inspect active
```

## API Reference

### DOMAnalyzer Class

#### `analyze_page(url: str, html_content: str) -> DOMFingerprint`
Analyzes HTML content and generates structural fingerprint.

#### `extract_key_selectors(soup: BeautifulSoup) -> Dict[str, str]`
Extracts important CSS selectors and their content.

### DOMChangeDetector Class  

#### `check_for_changes(url: str, html_content: str) -> List[DOMChange]`
Compares current HTML with stored fingerprint and returns detected changes.

#### `compare_fingerprints(url: str, old_fp: DOMFingerprint, new_fp: DOMFingerprint) -> List[DOMChange]`
Compares two fingerprints and identifies differences.

### SpiderUpdater Class

#### `update_spiders_for_changes(changes: List[DOMChange]) -> Dict`
Applies automatic updates to affected spiders based on detected changes.

#### `get_update_statistics(days: int) -> Dict`
Returns update statistics and success rates.

## Performance Considerations

### Resource Usage
- **Memory**: ~100MB per 1000 monitored URLs
- **CPU**: Moderate during analysis, low during monitoring
- **Storage**: ~1MB per site per month for change history
- **Network**: Bandwidth scales with monitoring frequency

### Scalability
- **Concurrent Monitoring**: Up to 50 URLs simultaneously
- **Change Processing**: Batch processing for efficiency
- **Update Application**: Parallel spider updates with locking
- **Report Generation**: Optimized queries and caching

### Optimization Tips
1. Use CDN/proxy for geographically distributed monitoring
2. Implement intelligent caching for frequently unchanged sites
3. Optimize CSS selector matching algorithms
4. Use database indexing for change history queries

## Contributing

Phase 2 welcomes contributions in several areas:

### Enhancement Opportunities
- Additional change detection algorithms
- New automatic fix patterns
- Integration with popular CMS systems
- Advanced reporting and visualization

### Testing
- Unit tests for change detection accuracy
- Integration tests with various website types
- Performance testing under load
- Rollback procedure validation

## License

Phase 2 is part of the Business Intelligence Scraper project and follows the same licensing terms.

## Support

For Phase 2 specific issues:
- 📧 Email: phase2-support@example.com
- 💬 Discord: #phase2-support
- 🐛 Issues: GitHub repository issues
- 📖 Wiki: Comprehensive documentation and examples

---

**Phase 2 Status**: ✅ **IMPLEMENTATION COMPLETE**

Ready for production deployment and Phase 3 development!
