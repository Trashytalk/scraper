# Crawler-to-Scraper Pipeline Documentation

## Overview
This feature enables a powerful two-stage data collection workflow: use crawler results as input for targeted scraping operations. This allows you to first discover URLs through crawling, then systematically scrape those discovered URLs for detailed data extraction.

## Workflow: From Discovery to Extraction

### Stage 1: Discovery (Crawling)
1. **Create a Crawler Job**: Set up a crawling job to discover URLs and map site structure
2. **Run Discovery**: Let the crawler explore the target website and collect URLs
3. **Review Results**: Examine the discovered URLs, links, and site structure

### Stage 2: Extraction (Batch Scraping)
1. **Select Crawler Results**: Choose a completed crawler job as your data source
2. **Configure Scraping**: Set up scraping parameters for the discovered URLs
3. **Execute Batch Jobs**: Automatically create multiple scraping jobs for efficient processing

## User Interface Features

### 🚀 Quick Create Job - Enhanced Modes

#### 🎯 Single URL Scraping (Standard Mode)
- Traditional single-page scraping
- Direct URL input
- Immediate execution

#### 🕷️ Batch Scraping from Crawler Results (New Mode)
- **Crawler Job Selection**: Dropdown of completed crawler jobs
- **URL Preview**: Shows discovered URLs before job creation
- **Batch Configuration**: Configurable batch sizes (5, 10, 25, 50 URLs per job)
- **Smart Job Naming**: Automatic naming with batch numbers
- **Progress Tracking**: Visual feedback on extraction and job creation

### 📊 Results Viewer - New "Use for Scraping" Feature
- **🕷️ Use for Scraping Button**: Extract URLs from any completed job
- **Automatic Pipeline Setup**: Switches to dashboard and prepares batch configuration
- **URL Field Detection**: Intelligently finds URL fields in job results
- **Seamless Integration**: Maintains context between crawler and scraper jobs

## Technical Implementation

### Frontend Enhancements
- **State Management**: New state variables for crawler jobs, extracted URLs, and batch configuration
- **URL Extraction Logic**: Client-side URL discovery from various data fields
- **Batch Job Interface**: Enhanced form with conditional rendering for batch mode
- **Pipeline Integration**: Seamless transition from results viewer to job creator

### Backend API Endpoints

#### New Endpoints
```
POST /api/jobs/batch
- Create multiple scraping jobs from URL list
- Automatic batch splitting and job generation
- Configurable batch sizes and naming

GET /api/jobs/{job_id}/extract-urls
- Extract URLs from completed crawler job results
- Intelligent URL field detection
- Sample URL generation for testing
```

#### Enhanced Data Models
```typescript
interface ScrapingJob {
  // Existing fields...
  config: {
    // Existing config...
    source_crawler_job_id?: number;
    batch_mode?: boolean;
    batch_urls?: string[];
    batch_index?: number;
    total_batches?: number;
  }
}

interface BatchJobCreate {
  base_name: string;
  source_crawler_job_id: number;
  scraper_type: string;
  urls: string[];
  batch_size: number;
  config: object;
}
```

## Usage Guide

### Step 1: Create a Crawler Job
1. Go to the **Dashboard** tab
2. Select **🕷️ Batch Scraping from Crawler Results** mode
3. **BUT FIRST**: Create a regular crawler job to discover URLs
   - Switch back to **🎯 Single URL Scraping** mode
   - Set type to "crawling" in the crawlers tab
   - Configure depth and page limits
   - Run the crawler job and wait for completion

### Step 2: Use Crawler Results for Scraping
1. Once crawler job is completed, return to **Dashboard**
2. Select **🕷️ Batch Scraping from Crawler Results** mode
3. Choose your completed crawler job from the dropdown
4. Review the extracted URLs in the preview panel
5. Configure batch size and scraping parameters
6. Click **Create X Jobs** to generate batch scraping jobs

### Step 3: Alternative - Use Results Viewer
1. Go to **Jobs & Queue** tab
2. Click **📊 View Results** on any completed crawler job
3. Click **🕷️ Use for Scraping** button in the results viewer
4. System automatically switches to dashboard with URLs pre-loaded
5. Configure and create batch jobs

## URL Extraction Logic

### Supported URL Fields
The system automatically detects URLs in these common fields:
- `url` - Primary URL field
- `link` - Generic link field
- `href` - HTML href attribute
- `page_url` - Page-specific URL
- `discovered_url` - Crawler-discovered URL
- `target_url` - Target URL for scraping

### Array Detection
- `links[]` - Arrays of link objects or strings
- `links[].href` - Nested href attributes in link arrays

### Validation
- URL format validation using JavaScript URL constructor
- Duplicate removal using Set deduplication
- Protocol filtering (http/https only)

## Batch Job Management

### Job Naming Convention
```
Base Name - Batch X/Y
Example: "E-commerce Products - Batch 1/5"
```

### Configuration Inheritance
- **Scraper Type**: Inherited from base configuration
- **Custom Selectors**: Applied to all batch jobs
- **Source Tracking**: Links back to original crawler job
- **Batch Metadata**: Index and total batch information

### Job Distribution
- **Batch Size**: Configurable (5, 10, 25, 50 URLs per job)
- **Load Balancing**: Even distribution of URLs across jobs
- **Sequential Processing**: Jobs can be processed in parallel or sequence

## Advanced Features

### 🔄 Pipeline Automation
- **One-Click Setup**: From results to batch jobs in seconds
- **Context Preservation**: Maintains configuration across pipeline stages
- **Smart Defaults**: Intelligent parameter selection based on source data

### 📊 Progress Tracking
- **Extraction Feedback**: Real-time URL discovery updates
- **Batch Creation Progress**: Visual feedback during job generation
- **Job Relationship Tracking**: Links between crawler and scraper jobs

### 🎯 Quality Assurance
- **URL Validation**: Automatic filtering of invalid URLs
- **Duplicate Prevention**: Deduplication across all extracted URLs
- **Error Handling**: Graceful fallbacks and error reporting

## Use Cases

### 1. E-commerce Product Scraping
- **Crawler**: Discover all product category and listing pages
- **Scraper**: Extract detailed product information from each discovered page

### 2. News Article Collection
- **Crawler**: Find all article URLs from news website sections
- **Scraper**: Extract full article content, metadata, and comments

### 3. Directory Harvesting
- **Crawler**: Map directory structure and find all listing pages
- **Scraper**: Extract contact information and business details

### 4. Social Media Content
- **Crawler**: Discover user profiles and post URLs
- **Scraper**: Extract detailed profile information and post content

### 5. Research Data Collection
- **Crawler**: Find research paper and publication URLs
- **Scraper**: Extract abstracts, authors, and citation information

## Performance Considerations

### Batch Size Selection
- **Small Batches (5-10)**: Better for real-time monitoring, higher overhead
- **Medium Batches (25)**: Balanced performance and monitoring
- **Large Batches (50)**: Better throughput, less granular control

### Memory Management
- **URL Extraction**: Processes URLs in chunks to prevent memory overflow
- **Job Creation**: Sequential batch creation to avoid API overload
- **Result Storage**: Efficient storage of extracted URLs during processing

### Error Recovery
- **Individual Job Failures**: Other batch jobs continue processing
- **Partial Success Handling**: Reports successful and failed job creation
- **Retry Mechanisms**: Manual retry of failed batch job creation

## Best Practices

### 1. Crawler Configuration
- **Appropriate Depth**: Balance discovery scope with processing time
- **Page Limits**: Set reasonable limits to prevent infinite crawling
- **Pattern Filtering**: Use URL patterns to focus on relevant pages

### 2. Batch Job Planning
- **Batch Size**: Consider target site's rate limiting and server capacity
- **Job Scheduling**: Space out batch job execution to avoid overwhelming targets
- **Resource Planning**: Monitor system resources during large batch operations

### 3. Data Quality
- **URL Validation**: Review extracted URLs before creating batch jobs
- **Selector Testing**: Test custom selectors on sample pages first
- **Result Monitoring**: Monitor initial batch jobs before launching full pipeline

### 4. Workflow Organization
- **Naming Conventions**: Use descriptive names for easy job tracking
- **Documentation**: Document crawler configurations for reproducibility
- **Result Archiving**: Export and archive results for future reference

## Troubleshooting

### Common Issues

#### No URLs Extracted
- **Check Data Fields**: Verify crawler results contain URL fields
- **Field Naming**: Ensure URL fields use common naming conventions
- **Data Structure**: Check if URLs are nested in arrays or objects

#### Batch Jobs Not Created
- **Authentication**: Verify API token is valid
- **URL Validation**: Check if extracted URLs pass validation
- **Batch Size**: Ensure batch size doesn't exceed system limits

#### Performance Issues
- **Batch Size**: Reduce batch size for better performance
- **Concurrent Jobs**: Limit number of simultaneous batch jobs
- **System Resources**: Monitor CPU and memory usage

### Error Messages
- **"No URLs found"**: Crawler results don't contain extractable URLs
- **"Job not completed"**: Source crawler job must be in completed status
- **"Batch creation failed"**: API error during batch job generation

## Future Enhancements

### Planned Features
- **Custom URL Extraction Rules**: User-defined field mapping
- **Pipeline Templates**: Saved crawler-to-scraper configurations
- **Automatic Scheduling**: Time-based pipeline execution
- **Result Merging**: Automatic consolidation of batch job results
- **Performance Analytics**: Pipeline efficiency metrics and optimization
