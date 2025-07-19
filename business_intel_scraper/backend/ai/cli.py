"""
AI Integration CLI Commands
Provides command-line tools for AI configuration and testing
"""

import click
import asyncio
import json
from typing import List, Dict, Any
from pathlib import Path

from .config import get_config_manager, setup_ai_config
from . import AIProcessor


@click.group()
def ai():
    """AI integration commands"""
    pass


@ai.command()
def setup():
    """Interactive AI configuration setup"""
    setup_ai_config()


@ai.command()
def status():
    """Show AI system status"""
    try:
        processor = AIProcessor()
        status = processor.get_model_status()
        
        click.echo("AI System Status")
        click.echo("================")
        click.echo(f"AI Enabled: {status['ai_enabled']}")
        click.echo()
        
        click.echo("Models:")
        for model_name, loaded in status['models'].items():
            status_icon = "✓" if loaded else "✗"
            click.echo(f"  {status_icon} {model_name}")
        
        click.echo()
        click.echo("Capabilities:")
        for capability, available in status['capabilities'].items():
            status_icon = "✓" if available else "✗"
            click.echo(f"  {status_icon} {capability}")
        
    except Exception as e:
        click.echo(f"Error checking AI status: {e}", err=True)


@ai.command()
@click.argument('text')
def test_entities(text: str):
    """Test entity extraction on sample text"""
    try:
        processor = AIProcessor()
        entities = processor.extract_entities(text)
        
        click.echo(f"Text: {text}")
        click.echo("Entities:")
        for entity in entities:
            click.echo(f"  {entity.text} ({entity.label}) - {entity.confidence:.3f}")
        
    except Exception as e:
        click.echo(f"Error extracting entities: {e}", err=True)


@ai.command()
@click.argument('text')
def test_classification(text: str):
    """Test text classification on sample text"""
    try:
        processor = AIProcessor()
        classification = processor.classify_text(text)
        
        click.echo(f"Text: {text}")
        click.echo(f"Category: {classification.category}")
        click.echo(f"Confidence: {classification.confidence:.3f}")
        
    except Exception as e:
        click.echo(f"Error classifying text: {e}", err=True)


@ai.command()
@click.argument('text')
def test_sentiment(text: str):
    """Test sentiment analysis on sample text"""
    try:
        processor = AIProcessor()
        sentiment = processor.analyze_sentiment(text)
        
        click.echo(f"Text: {text}")
        click.echo("Sentiment:")
        for label, score in sentiment.items():
            click.echo(f"  {label}: {score:.3f}")
        
    except Exception as e:
        click.echo(f"Error analyzing sentiment: {e}", err=True)


@ai.command()
@click.argument('text')
@click.option('--max-length', default=150, help='Maximum summary length')
def test_summary(text: str, max_length: int):
    """Test text summarization on sample text"""
    try:
        processor = AIProcessor()
        summary = processor.summarize_text(text, max_length)
        
        click.echo(f"Original ({len(text)} chars): {text}")
        click.echo(f"Summary ({len(summary)} chars): {summary}")
        
    except Exception as e:
        click.echo(f"Error summarizing text: {e}", err=True)


@ai.command()
@click.argument('texts', nargs=-1)
@click.option('--threshold', default=0.85, help='Similarity threshold')
def test_duplicates(texts: List[str], threshold: float):
    """Test duplicate detection on multiple texts"""
    try:
        processor = AIProcessor()
        duplicates = processor.detect_duplicates(list(texts), threshold)
        
        click.echo(f"Texts ({len(texts)}):")
        for i, text in enumerate(texts):
            click.echo(f"  {i}: {text}")
        
        click.echo(f"\nDuplicate groups (threshold: {threshold}):")
        for i, group in enumerate(duplicates):
            if len(group) > 1:
                click.echo(f"  Group {i}: {group}")
        
        if not any(len(group) > 1 for group in duplicates):
            click.echo("  No duplicates found")
        
    except Exception as e:
        click.echo(f"Error detecting duplicates: {e}", err=True)


@ai.command()
@click.argument('file_path', type=click.Path(exists=True))
def process_file(file_path: str):
    """Process a JSON file with scraped data"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            data = [data]
        
        processor = AIProcessor()
        
        async def process_data():
            return await processor.enhance_scraped_data(data)
        
        results = asyncio.run(process_data())
        
        click.echo(f"Processed {len(results)} items:")
        for i, result in enumerate(results):
            click.echo(f"\nItem {i}:")
            click.echo(f"  Quality Score: {result.quality_score:.3f}")
            click.echo(f"  Entities: {len(result.entities)}")
            click.echo(f"  Category: {result.classification.category}")
            if result.sentiment:
                sentiment_summary = max(result.sentiment, key=result.sentiment.get)
                click.echo(f"  Sentiment: {sentiment_summary}")
            if result.duplicates:
                click.echo(f"  Duplicates: {len(result.duplicates)}")
        
    except Exception as e:
        click.echo(f"Error processing file: {e}", err=True)


@ai.command()
@click.option('--output', '-o', help='Output file path')
def export_config(output: str):
    """Export current AI configuration"""
    try:
        config_manager = get_config_manager()
        config = config_manager.get_config()
        
        config_dict = config_manager._config_to_dict(config)
        
        if output:
            with open(output, 'w') as f:
                json.dump(config_dict, f, indent=2)
            click.echo(f"Configuration exported to {output}")
        else:
            click.echo(json.dumps(config_dict, indent=2))
        
    except Exception as e:
        click.echo(f"Error exporting config: {e}", err=True)


@ai.command()
@click.argument('config_file', type=click.Path(exists=True))
def import_config(config_file: str):
    """Import AI configuration from file"""
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        config_manager = get_config_manager()
        config_manager.update_config(config_data)
        
        click.echo(f"Configuration imported from {config_file}")
        
        # Validate the imported config
        issues = config_manager.validate_config()
        if issues:
            click.echo("Configuration issues:")
            for issue in issues:
                click.echo(f"  - {issue}")
        else:
            click.echo("Configuration imported successfully!")
        
    except Exception as e:
        click.echo(f"Error importing config: {e}", err=True)


@ai.command()
def requirements():
    """Show Python requirements for AI features"""
    try:
        config_manager = get_config_manager()
        reqs = config_manager.generate_requirements()
        
        click.echo("Python Requirements for AI Features:")
        click.echo("===================================")
        for req in reqs:
            click.echo(req)
        
        # Save to requirements-ai.txt
        req_file = Path("requirements-ai.txt")
        with open(req_file, 'w') as f:
            for req in reqs:
                f.write(f"{req}\n")
        
        click.echo(f"\nRequirements saved to {req_file}")
        click.echo(f"Install with: pip install -r {req_file}")
        
    except Exception as e:
        click.echo(f"Error generating requirements: {e}", err=True)


@ai.command()
def benchmark():
    """Run AI performance benchmarks"""
    try:
        processor = AIProcessor()
        
        # Sample texts for benchmarking
        sample_texts = [
            "Apple Inc. is planning to release a new iPhone model next year with advanced AI capabilities.",
            "The stock market experienced significant volatility today with tech stocks leading the decline.",
            "Machine learning engineers at Google are developing new neural network architectures.",
            "Remote work opportunities in software development have increased by 300% this year.",
            "Bitcoin price surged to new heights as institutional investors showed renewed interest."
        ]
        
        click.echo("AI Performance Benchmark")
        click.echo("=======================")
        
        import time
        
        # Entity extraction benchmark
        start_time = time.time()
        for text in sample_texts:
            entities = processor.extract_entities(text)
        entity_time = time.time() - start_time
        click.echo(f"Entity Extraction: {entity_time:.3f}s for {len(sample_texts)} texts")
        
        # Classification benchmark
        start_time = time.time()
        for text in sample_texts:
            classification = processor.classify_text(text)
        classification_time = time.time() - start_time
        click.echo(f"Text Classification: {classification_time:.3f}s for {len(sample_texts)} texts")
        
        # Sentiment analysis benchmark
        start_time = time.time()
        for text in sample_texts:
            sentiment = processor.analyze_sentiment(text)
        sentiment_time = time.time() - start_time
        click.echo(f"Sentiment Analysis: {sentiment_time:.3f}s for {len(sample_texts)} texts")
        
        # Duplicate detection benchmark
        start_time = time.time()
        duplicates = processor.detect_duplicates(sample_texts)
        duplicate_time = time.time() - start_time
        click.echo(f"Duplicate Detection: {duplicate_time:.3f}s for {len(sample_texts)} texts")
        
        total_time = entity_time + classification_time + sentiment_time + duplicate_time
        click.echo(f"\nTotal Time: {total_time:.3f}s")
        click.echo(f"Average per text: {total_time/len(sample_texts):.3f}s")
        
    except Exception as e:
        click.echo(f"Error running benchmark: {e}", err=True)


if __name__ == "__main__":
    ai()
