#!/usr/bin/env python3
"""
AI Integration Test Script
Demonstrates AI capabilities without API dependencies
"""

import asyncio
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from business_intel_scraper.backend.ai import AIProcessor


async def main():
    print("🤖 Business Intelligence Scraper - AI Integration Test")
    print("=" * 60)

    # Initialize AI processor
    print("Initializing AI processor...")
    processor = AIProcessor()

    # Check AI status
    status = processor.get_model_status()
    print("\nAI System Status:")
    print(f"  Enabled: {status['ai_enabled']}")
    print(f"  Models loaded: {sum(status['models'].values())}/{len(status['models'])}")
    print(
        f"  Capabilities: {sum(status['capabilities'].values())}/{len(status['capabilities'])}"
    )

    # Test data samples
    sample_texts = [
        {
            "title": "Apple earnings news",
            "content": "Apple Inc. announced record quarterly earnings today, with CEO Tim Cook highlighting strong performance in California and international markets. The company's stock price rose 5% following the announcement.",
            "url": "https://example.com/apple-earnings",
        },
        {
            "title": "Job posting",
            "content": "Software Engineer position available at Google Inc. in Mountain View, California. Looking for candidates with Python and Machine Learning experience. Competitive salary and benefits package.",
            "url": "https://careers.google.com/job123",
        },
        {
            "title": "Product review",
            "content": "I absolutely love this new smartphone! The camera quality is incredible and the battery life is amazing. Highly recommend to anyone looking for a premium device.",
            "url": "https://reviews.example.com/phone",
        },
    ]

    print(f"\n📊 Processing {len(sample_texts)} sample items...")
    print("-" * 60)

    # Process data with AI
    enhanced_data = await processor.enhance_scraped_data(sample_texts)

    # Display results
    for i, item in enumerate(enhanced_data, 1):
        print(f"\n🔍 Item {i}: {sample_texts[i-1]['title']}")
        print(f"  Quality Score: {item.quality_score:.3f}")

        # Entities
        if item.entities:
            print(f"  Entities ({len(item.entities)}):")
            for entity in item.entities[:5]:  # Show first 5
                print(f"    • {entity.text} ({entity.label}) - {entity.confidence:.3f}")

        # Classification
        if item.classification:
            print(
                f"  Category: {item.classification.category} ({item.classification.confidence:.3f})"
            )

        # Sentiment
        if item.sentiment:
            primary_sentiment = max(item.sentiment, key=item.sentiment.get)
            score = item.sentiment[primary_sentiment]
            print(f"  Sentiment: {primary_sentiment} ({score:.3f})")

        # Summary
        if item.summary and len(item.summary) < len(sample_texts[i - 1]["content"]):
            print(f"  Summary: {item.summary[:100]}...")

        print()

    # Test duplicate detection
    print("🔍 Testing Duplicate Detection...")
    test_texts = [
        "Apple Inc. released new iPhone model",
        "Apple announced the release of a new iPhone",
        "Microsoft launched Windows update",
        "Google updates its search algorithm",
    ]

    duplicates = processor.detect_duplicates(test_texts, threshold=0.8)
    print(f"  Found {len([g for g in duplicates if len(g) > 1])} duplicate groups")

    for i, group in enumerate(duplicates):
        if len(group) > 1:
            print(f"    Group {i+1}: {group}")

    print("\n✅ AI Integration Test Complete!")
    print("\nKey Features Demonstrated:")
    print("  ✓ Named Entity Recognition (People, Organizations, Locations)")
    print("  ✓ Text Classification (Business, Technology, etc.)")
    print("  ✓ Sentiment Analysis (Positive, Negative, Neutral)")
    print("  ✓ Text Summarization")
    print("  ✓ Duplicate Detection")
    print("  ✓ Data Quality Scoring")

    print("\n🚀 Next Steps:")
    print(
        "  • AI dependencies are included in main requirements: pip install -r requirements.txt"
    )
    print("  • Configure AI settings: python bis.py ai setup")
    print("  • Use in Scrapy pipelines for automatic enhancement")
    print("  • Access via REST API: /ai/process-text")
    print("  • View documentation: docs/ai_integration.md")


if __name__ == "__main__":
    asyncio.run(main())
