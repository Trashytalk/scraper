# AI Integration Documentation

## Overview

The Business Intelligence Scraper now includes comprehensive AI integration capabilities that enhance your scraped data with intelligent analysis. This documentation covers setup, configuration, and usage of AI features.

## Features

### 🧠 Core AI Capabilities

- **Named Entity Recognition (NER)**: Extract people, organizations, locations, emails, URLs, and more
- **Text Classification**: Automatically categorize content (business, technology, news, etc.)
- **Sentiment Analysis**: Analyze emotional tone and opinion polarity
- **Text Summarization**: Generate concise summaries of long content
- **Duplicate Detection**: Identify similar or duplicate content
- **Quality Scoring**: Assess data quality and completeness

### 🔧 Integration Methods

1. **API Endpoints**: REST API for real-time AI processing
2. **Scrapy Pipeline**: Automatic AI enhancement during scraping
3. **CLI Tools**: Command-line utilities for testing and batch processing
4. **Background Processing**: Async processing for large datasets

## Quick Start

### 1. Setup AI Features

```bash
# Interactive AI setup
python bis.py ai setup

# Check AI system status
python bis.py ai status

# Generate AI requirements
python bis.py ai requirements
```

### 2. Install AI Dependencies

```bash
# AI packages are now included in main requirements
pip install -r requirements.txt

# For development
python bis.py install --include-ai
```

### 3. Test AI Capabilities

```bash
# Test entity extraction
python bis.py ai test-entities "Apple Inc. released new iPhone in California"

# Test text classification
python bis.py ai test-classification "This is a job posting for a software engineer position"

# Test sentiment analysis
python bis.py ai test-sentiment "I love this new product! It's amazing."

# Test summarization
python bis.py ai test-summary "Long text content here..."
```

## Configuration

### AI Configuration File

The AI system uses `config/ai_config.yaml` for configuration:

```yaml
# Enable/disable AI features
enabled: true

# Model configurations
models:
  spacy_en:
    name: "en_core_web_sm"
    type: "spacy"
    enabled: true
  
  sentiment_classifier:
    name: "cardiffnlp/twitter-roberta-base-sentiment-latest"
    type: "transformers"
    enabled: true
  
  # ... more models
```

### Environment Variables

Set these environment variables for optimal AI performance:

```bash
export OPENAI_API_KEY="your-openai-api-key"  # For OpenAI models
export TRANSFORMERS_CACHE="./data/ai_cache/transformers"
export SENTENCE_TRANSFORMERS_HOME="./data/ai_cache/sentence_transformers"
export TOKENIZERS_PARALLELISM=false
```

## API Usage

### Process Text with AI

```python
import httpx

# Process text with all AI features
response = httpx.post("http://localhost:8000/ai/process-text", json={
    "text": "Apple Inc. announced record quarterly earnings today.",
    "include_entities": True,
    "include_classification": True,
    "include_sentiment": True,
    "include_summary": True
})

result = response.json()
print(f"Entities: {result['entities']}")
print(f"Category: {result['classification']['category']}")
print(f"Sentiment: {result['sentiment']}")
```

### Batch Processing

```python
# Process multiple items
response = httpx.post("http://localhost:8000/ai/process-data", json={
    "data": [
        {"title": "News Article 1", "content": "..."},
        {"title": "News Article 2", "content": "..."}
    ],
    "detect_duplicates": True,
    "calculate_quality": True
})

processed_data = response.json()
```

## Scrapy Integration

### Enable AI Pipeline

Add AI pipelines to your Scrapy settings:

```python
# settings.py
ITEM_PIPELINES = {
    'business_intel_scraper.backend.utils.ai_pipeline.AIEnhancementPipeline': 300,
    'business_intel_scraper.backend.utils.ai_pipeline.AIFilterPipeline': 400,
}

# AI Configuration
AI_ENABLED = True
AI_BATCH_SIZE = 10
AI_PROCESS_ENTITIES = True
AI_PROCESS_CLASSIFICATION = True
AI_PROCESS_SENTIMENT = True
AI_MIN_QUALITY_SCORE = 0.6
```

### Spider Implementation

```python
import scrapy
from business_intel_scraper.backend.utils.ai_settings import *

class NewsSpider(scrapy.Spider):
    name = 'news'
    
    custom_settings = NEWS_SCRAPER_AI_SETTINGS  # Pre-configured AI settings
    
    def parse(self, response):
        # Extract data as usual
        yield {
            'title': response.css('h1::text').get(),
            'content': response.css('.article-content::text').getall(),
            'url': response.url,
        }
        # AI pipeline will automatically enhance this data
```

### AI-Enhanced Output

The AI pipeline adds these fields to your scraped items:

```json
{
    "title": "Original title",
    "content": "Original content",
    "url": "Original URL",
    
    // AI enhancements
    "ai_processed": true,
    "ai_quality_score": 0.85,
    "ai_entities": [
        {"text": "Apple Inc.", "label": "ORG", "confidence": 0.99}
    ],
    "ai_people": ["Tim Cook"],
    "ai_organizations": ["Apple Inc."],
    "ai_locations": ["California"],
    "ai_emails": ["contact@example.com"],
    "ai_urls": ["https://example.com"],
    "ai_category": "technology",
    "ai_category_confidence": 0.92,
    "ai_sentiment": {"positive": 0.8, "negative": 0.1, "neutral": 0.1},
    "ai_sentiment_primary": "positive",
    "ai_summary": "Brief summary of the content",
    "ai_is_duplicate": false
}
```

## Model Configuration

### Available Models

| Model | Type | Purpose | Performance |
|-------|------|---------|-------------|
| `en_core_web_sm` | SpaCy | Entity extraction | Fast |
| `twitter-roberta-base-sentiment` | Transformers | Sentiment analysis | Medium |
| `bart-large-mnli` | Transformers | Text classification | Medium |
| `bart-large-cnn` | Transformers | Summarization | Slow |
| `all-MiniLM-L6-v2` | Sentence Transformers | Embeddings | Fast |
| `gpt-3.5-turbo` | OpenAI | Advanced processing | API-based |

### Model Management

```bash
# Enable/disable specific models
python bis.py ai setup  # Interactive configuration

# Check model status
python bis.py ai status

# Run performance benchmarks
python bis.py ai benchmark
```

## Performance Optimization

### Batch Processing

Process items in batches for better performance:

```python
# Scrapy settings
AI_BATCH_SIZE = 20  # Process 20 items at once

# API batch processing
response = httpx.post("/ai/batch-process", json={
    "data": large_dataset,
    "callback_url": "https://your-app.com/ai-callback"
})
```

### Caching

AI results are automatically cached to improve performance:

```yaml
# config/ai_config.yaml
cache_dir: "./data/ai_cache"
models:
  spacy_en:
    cache_size: 1000  # Cache 1000 processed texts
```

### Resource Management

```yaml
# Limit resource usage
parallel_processing: true
max_workers: 4
max_text_length: 10000  # Skip very long texts
```

## Use Cases

### 1. News Monitoring

```python
# Monitor news sentiment about your company
AI_REQUIRED_ENTITIES = ['ORG']  # Must mention organizations
AI_PROCESS_SENTIMENT = True
AI_MIN_QUALITY_SCORE = 0.7
```

### 2. Job Market Analysis

```python
# Analyze job postings
AI_REQUIRED_ENTITIES = ['ORG', 'MONEY']  # Company and salary
AI_BLOCKED_CATEGORIES = ['spam']
AI_PROCESS_CLASSIFICATION = True
```

### 3. Social Media Monitoring

```python
# Track social media mentions
AI_PROCESS_SENTIMENT = True
AI_MIN_SENTIMENT_CONFIDENCE = 0.5
AI_FILTER_DUPLICATES = True
```

### 4. E-commerce Intelligence

```python
# Product and pricing analysis
AI_REQUIRED_ENTITIES = ['MONEY', 'PRODUCT']
AI_PROCESS_CLASSIFICATION = True
AI_MIN_QUALITY_SCORE = 0.8
```

## Troubleshooting

### Common Issues

1. **Model Loading Errors**
   ```bash
   # Check model status
   python bis.py ai status
   
   # Reinstall AI dependencies (now in main requirements.txt)
   pip install -r requirements.txt
   ```

2. **Performance Issues**
   ```yaml
   # Reduce batch size
   AI_BATCH_SIZE: 5
   
   # Disable heavy models
   models:
     summarizer:
       enabled: false
   ```

3. **Memory Issues**
   ```yaml
   # Limit text length
   max_text_length: 5000
   
   # Reduce cache size
   models:
     spacy_en:
       cache_size: 100
   ```

### Debug Mode

Enable debug logging for troubleshooting:

```yaml
# config/ai_config.yaml
log_level: "DEBUG"
```

```bash
# Check logs
tail -f data/logs/ai.log
```

## API Reference

### Endpoints

- `GET /ai/status` - Get AI system status
- `POST /ai/process-text` - Process single text
- `POST /ai/extract-entities` - Extract entities only
- `POST /ai/classify-text` - Classify text only
- `POST /ai/analyze-sentiment` - Analyze sentiment only
- `POST /ai/summarize-text` - Summarize text only
- `POST /ai/detect-duplicates` - Detect duplicates
- `POST /ai/process-data` - Process structured data
- `POST /ai/batch-process` - Batch processing
- `GET /ai/health` - Health check
- `GET /ai/models` - List available models

### CLI Commands

```bash
# AI system management
python bis.py ai setup          # Interactive setup
python bis.py ai status         # Show status
python bis.py ai requirements   # Generate requirements

# Testing commands
python bis.py ai test-entities "text"
python bis.py ai test-classification "text"
python bis.py ai test-sentiment "text"
python bis.py ai test-summary "text"
python bis.py ai test-duplicates "text1" "text2"

# Configuration management
python bis.py ai export-config
python bis.py ai import-config config.json

# Utilities
python bis.py ai benchmark      # Performance testing
python bis.py ai process-file data.json  # Process file
```

## Best Practices

1. **Start Simple**: Begin with basic entity extraction and sentiment analysis
2. **Batch Processing**: Use batching for better performance
3. **Quality Filtering**: Set appropriate quality thresholds
4. **Model Selection**: Choose models based on your accuracy vs. speed requirements
5. **Caching**: Enable caching for repeated processing
6. **Monitoring**: Monitor AI performance and adjust settings as needed

## Support

- 📖 [Full Documentation](../README.md)
- 🐛 [Report Issues](https://github.com/your-repo/issues)
- 💬 [Community Support](https://github.com/your-repo/discussions)
- 📧 [Email Support](mailto:support@example.com)

---

*This AI integration transforms your scraper from a simple data collection tool into an intelligent business intelligence platform.*
