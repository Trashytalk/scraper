"""
AI Integration Settings for Scrapy
Configuration for AI-enhanced scraping pipelines
"""

# Add these settings to your Scrapy project's settings.py

# AI Enhancement Pipeline Settings
AI_ENABLED = True  # Enable/disable AI processing
AI_BATCH_SIZE = 10  # Process items in batches for efficiency
AI_PROCESS_ENTITIES = True  # Extract named entities
AI_PROCESS_CLASSIFICATION = True  # Classify text content
AI_PROCESS_SENTIMENT = True  # Analyze sentiment
AI_PROCESS_DUPLICATES = True  # Detect duplicates

# AI Filter Pipeline Settings
AI_MIN_QUALITY_SCORE = 0.5  # Minimum quality score to keep items
AI_FILTER_DUPLICATES = True  # Drop duplicate items
AI_REQUIRED_ENTITIES: list[str] = (
    []
)  # List of required entity types (e.g., ['PERSON', 'ORG'])
AI_BLOCKED_CATEGORIES: list[str] = (
    []
)  # List of categories to block (e.g., ['spam', 'irrelevant'])
AI_MIN_SENTIMENT_CONFIDENCE = 0.0  # Minimum sentiment confidence

# Pipeline Configuration
# Add these pipelines to your ITEM_PIPELINES setting:
ITEM_PIPELINES = {
    "business_intel_scraper.backend.utils.ai_pipeline.AIEnhancementPipeline": 300,
    "business_intel_scraper.backend.utils.ai_pipeline.AIFilterPipeline": 400,
    # ... your other pipelines
}

# Example AI-enhanced spider settings for specific use cases:

# Job Posting Scraper Settings
JOB_SCRAPER_AI_SETTINGS = {
    "AI_REQUIRED_ENTITIES": ["ORG"],  # Must have company names
    "AI_BLOCKED_CATEGORIES": ["spam", "irrelevant"],
    "AI_MIN_QUALITY_SCORE": 0.7,  # Higher quality threshold
}

# News Article Scraper Settings
NEWS_SCRAPER_AI_SETTINGS = {
    "AI_PROCESS_SENTIMENT": True,
    "AI_MIN_QUALITY_SCORE": 0.6,
    "AI_BLOCKED_CATEGORIES": ["advertisement"],
}

# E-commerce Product Scraper Settings
ECOMMERCE_SCRAPER_AI_SETTINGS = {
    "AI_REQUIRED_ENTITIES": ["MONEY"],  # Must have price information
    "AI_MIN_QUALITY_SCORE": 0.8,
    "AI_FILTER_DUPLICATES": True,
}

# Social Media Scraper Settings
SOCIAL_SCRAPER_AI_SETTINGS = {
    "AI_PROCESS_SENTIMENT": True,
    "AI_MIN_SENTIMENT_CONFIDENCE": 0.3,
    "AI_BLOCKED_CATEGORIES": ["spam", "bot"],
}
