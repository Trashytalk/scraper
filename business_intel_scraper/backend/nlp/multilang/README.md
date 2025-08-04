# Multi-Language NLP Setup Guide

This guide covers the installation and setup of the comprehensive Multi-Language NLP system for business intelligence data processing.

## Overview

The Multi-Language NLP system provides:
- Language detection for 25+ languages
- Script identification (Latin, Cyrillic, Arabic, CJK, etc.)
- Language-specific tokenization
- Multi-language Named Entity Recognition (NER)
- Script transliteration
- Translation services
- Field normalization and standardization
- Cross-language entity matching

## Installation

### 1. Core Dependencies

Install the core multi-language dependencies:

```bash

# Navigate to the multilang directory

cd business_intel_scraper/backend/nlp/multilang

# Install Python dependencies

pip install -r requirements.txt

```

### 2. Language Models

#### spaCy Models

Install spaCy language models for better NER performance:

```bash

# English (required)

python -m spacy download en_core_web_sm

# Other languages (optional but recommended)

python -m spacy download zh_core_web_sm    # Chinese
python -m spacy download de_core_news_sm   # German
python -m spacy download fr_core_news_sm   # French
python -m spacy download es_core_news_sm   # Spanish
python -m spacy download ru_core_news_sm   # Russian
python -m spacy download ja_core_news_sm   # Japanese

```

#### Stanza Models

Stanza models are downloaded automatically on first use for each language.

#### Transformers Models

The default multilingual BERT model will be downloaded automatically when first used.

### 3. Optional Components

#### ICU Library (Recommended)

For advanced transliteration capabilities:

```bash

# Ubuntu/Debian

sudo apt-get install libicu-dev

# macOS

brew install icu4c

# Then reinstall PyICU

pip install --force-reinstall PyICU

```

#### FastText Language Detection

For improved language detection:

```bash

# Download FastText language identification model

wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
mkdir -p ~/.fasttext
mv lid.176.bin ~/.fasttext/

```

#### Translation APIs

For translation services, set up API keys:

```bash

# Google Translate API

export GOOGLE_TRANSLATE_API_KEY="your-api-key"

# DeepL API

export DEEPL_API_KEY="your-api-key"

```

### 4. Tokenization Libraries

#### Chinese (jieba)

```bash

pip install jieba

```

#### Japanese (MeCab)

```bash

# Ubuntu/Debian

sudo apt-get install mecab mecab-ipadic-utf8 libmecab-dev

# macOS

brew install mecab mecab-ipadic

# Python package

pip install mecab-python3

```

#### Thai (PyThaiNLP)

```bash

pip install pythainlp

```

## Configuration

### Environment Variables

Set up environment variables for customization:

```bash

# Language detection

export MULTILANG_CONFIDENCE_THRESHOLD=0.7
export MULTILANG_FALLBACK_LANGUAGE=en

# Processing preferences

export MULTILANG_TARGET_LANGUAGE=en
export MULTILANG_PREFER_OFFLINE=true

# Performance settings

export MULTILANG_BATCH_SIZE=50
export MULTILANG_MAX_WORKERS=4

# Normalization defaults

export MULTILANG_PHONE_DEFAULT_COUNTRY=US
export MULTILANG_FINANCIAL_DEFAULT_CURRENCY=USD

```

### Configuration File

Edit `config.py` to customize settings for your use case:

```python

# Example configuration changes

MULTILANG_CONFIG['language_detection']['confidence_threshold'] = 0.8
MULTILANG_CONFIG['translation']['target_language'] = 'en'
MULTILANG_CONFIG['performance']['batch_size'] = 100

```

## Usage Examples

### Basic Usage

```python

from business_intel_scraper.backend.nlp.multilang import multilang_processor

# Process text in any language

text = "苹果公司位于美国加利福尼亚州库比蒂诺"
result = multilang_processor.process_text(text)

print(f"Detected language: {result.detected_language.language.name}")
print(f"Entities found: {len(result.entities)}")
if result.translation:
    print(f"Translation: {result.translation.translated}")

```

### Business Intelligence Extraction

```python

# Extract structured business data

text = "Apple Inc. revenue was $365.8 billion. Contact: +1-408-996-1010"
intelligence = multilang_processor.extract_business_intelligence(text)

print("Language:", intelligence['language_info']['detected_language'])
print("Entities:", intelligence['entities'])
print("Structured data:", intelligence['structured_data'])

```

### Entity Normalization

```python

from business_intel_scraper.backend.nlp.multilang.normalization import phone_normalizer

# Normalize phone numbers

phone = "(555) 123-4567"
result = phone_normalizer.normalize_phone(phone)
print(f"Normalized: {result.normalized}")  # Output: +1555123456

```

### Cross-Language Matching

```python

from business_intel_scraper.backend.nlp.multilang.transliteration import entity_normalizer

# Normalize company names for matching

company1 = entity_normalizer.normalize_company_name("Apple Inc.", lang_en)
company2 = entity_normalizer.normalize_company_name("苹果公司", lang_zh)

similarity = entity_normalizer.calculate_similarity(company1, company2)
print(f"Similarity: {similarity}")

```

### Batch Processing

```python

# Process multiple texts

texts = [
    "English text here",
    "中文文本在这里",
    "Русский текст здесь"
]

results = multilang_processor.batch_process(texts)
for i, result in enumerate(results):
    print(f"Text {i+1}: {result.detected_language.language.name}")

```

## Testing

Run the comprehensive test suite:

```bash

# Run all tests

python -m pytest test_multilang.py -v

# Run specific test categories

python -m pytest test_multilang.py::TestLanguageDetection -v
python -m pytest test_multilang.py::TestNormalization -v

# Run with coverage

python -m pytest test_multilang.py --cov=multilang --cov-report=html

```

## Performance Optimization

### 1. Model Loading

- Models are loaded lazily on first use
- Use batch processing for multiple texts
- Enable caching for repeated processing

### 2. Memory Management

```python

# For large-scale processing

multilang_processor.process_text(
    text,
    include_translation=False,  # Skip if not needed
    include_transliteration=False  # Skip if not needed
)

```

### 3. Async Processing

```python

import asyncio

async def process_many_texts(texts):
    results = await multilang_processor.async_batch_process(texts)
    return results

# Run async processing

results = asyncio.run(process_many_texts(text_list))

```

## Troubleshooting

### Common Issues

1. **Missing Language Models**
   ```
   Error: Can't find model 'en_core_web_sm'
   Solution: python -m spacy download en_core_web_sm
   ```

2. **ICU Library Issues**
   ```
   Error: ICU transliterators not available
   Solution: Install libicu-dev and reinstall PyICU
   ```

3. **Memory Issues with Large Texts**
   ```
   Solution: Use batch processing or reduce batch_size in config
   ```

4. **Slow Translation**
   ```
   Solution: Set MULTILANG_PREFER_OFFLINE=true to use local models
   ```

### Debug Mode

Enable debug logging to troubleshoot issues:

```python

import logging
logging.basicConfig(level=logging.DEBUG)

# Or set environment variable

export MULTILANG_LOG_LEVEL=DEBUG

```

## Integration with Existing Pipeline

### Update Existing Code

Replace basic NLP calls with multi-language equivalents:

```python

# Old way

from business_intel_scraper.backend.nlp.pipeline import extract_entities
entities = extract_entities([text])

# New way

from business_intel_scraper.backend.nlp.pipeline import extract_multilang_entities
entities = extract_multilang_entities(text)

```

### Backward Compatibility

The enhanced pipeline maintains backward compatibility:

```python

# Still works - will use multi-language processor if available

from business_intel_scraper.backend.nlp.pipeline import extract_entities_structured
entities = extract_entities_structured(text)

```

## Production Deployment

### Docker Setup

Add to Dockerfile:

```dockerfile

# Install system dependencies

RUN apt-get update && apt-get install -y \
    libicu-dev \
    mecab \
    mecab-ipadic-utf8 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies

COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Download language models

RUN python -m spacy download en_core_web_sm
RUN python -m spacy download zh_core_web_sm

```

### Environment Configuration

```yaml

# docker-compose.yml or kubernetes config

environment:
  - MULTILANG_CONFIDENCE_THRESHOLD=0.8
  - MULTILANG_PREFER_OFFLINE=true
  - MULTILANG_BATCH_SIZE=100
  - MULTILANG_MAX_WORKERS=4

```

### Monitoring

Monitor performance and accuracy:

```python

# Add to your monitoring system

capabilities = multilang_processor.get_capabilities()
print("Supported languages:", len(capabilities['languages']))
print("Translation available:", capabilities['translation_support'])

```

## Next Steps

1. **Fine-tuning**: Train custom models for domain-specific entities
2. **Custom Patterns**: Add business-specific entity patterns
3. **Language Expansion**: Add support for additional languages
4. **Performance Optimization**: Profile and optimize for your specific workload
5. **Integration**: Connect with your existing data processing pipeline

For more details, see the API documentation and example implementations.
