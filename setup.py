#!/usr/bin/env python3
"""
Business Intelligence Scraper Setup
Consolidated setup with optional dependency groups
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Business Intelligence Scraper Platform"

# Define version
VERSION = "1.0.0"

# Core dependencies (always installed)
CORE_REQUIREMENTS = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy>=2.0.23",
    "alembic>=1.12.1",
    "aiosqlite>=0.19.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
]

# Web and API dependencies
WEB_REQUIREMENTS = [
    "strawberry-graphql[fastapi]>=0.213.0",
    "sse-starlette>=1.6.5",
    "python-multipart>=0.0.6",
    "aiofiles>=23.2.0",
    "requests>=2.31.0",
    "httpx>=0.25.2",
]

# Database dependencies
DATABASE_REQUIREMENTS = [
    "psycopg2-binary>=2.9.9",
    "redis>=5.0.1",
    "celery>=5.3.4",
]

# Scraping dependencies
SCRAPING_REQUIREMENTS = [
    "scrapy>=2.11.0",
    "beautifulsoup4>=4.12.2",
    "aiohttp>=3.9.0",
    "requests-cache>=1.1.1",
    "playwright>=1.40.0",
    "selenium>=4.15.2",
]

# Security dependencies
SECURITY_REQUIREMENTS = [
    "pyjwt[crypto]>=2.8.0",
    "passlib[bcrypt]>=1.7.4",
    "cryptography>=41.0.7",
    "bcrypt>=4.1.2",
    "python-socks>=2.4.3",
    "urllib3>=2.0.7",
    "stem>=1.8.2",
    "pysocks>=1.7.1",
]

# Data processing dependencies
DATA_REQUIREMENTS = [
    "pandas>=2.1.4",
    "numpy>=1.24.3",
    "plotly>=5.17.0",
    "matplotlib>=3.8.0",
    "networkx>=3.2.1",
]

# NLP dependencies
NLP_REQUIREMENTS = [
    "spacy>=3.7.2",
    "nltk>=3.8.1",
    "textblob>=0.17.1",
    "langdetect>=1.0.9",
    "transformers>=4.36.0",
    "torch>=2.1.0",
    "scikit-learn>=1.3.0",
    "sentence-transformers>=2.2.0",
    "tokenizers>=0.14.1",
    "unidecode>=1.3.4",
    "fuzzywuzzy>=0.18.0",
    "python-Levenshtein>=0.12.2",
]

# Advanced NLP (with system dependencies)
NLP_ADVANCED_REQUIREMENTS = [
    "jieba>=0.42.1",
    "fasttext>=0.9.2",
    "polyglot>=16.7.4",
    "mecab-python3>=1.0.5",
    "pythainlp>=4.0.0",
    "stanza>=1.5.0",
    "PyICU>=2.10.2",
    "transliterate>=1.10.2",
    "deep-translator>=1.9.2",
    "phonetics>=1.0.5",
]

# Computer Vision dependencies
VISION_REQUIREMENTS = [
    "opencv-python>=4.8.1.78",
    "pytesseract>=0.3.10",
    "Pillow>=10.1.0",
]

# Monitoring dependencies
MONITORING_REQUIREMENTS = [
    "prometheus-client>=0.19.0",
    "structlog>=23.2.0",
]

# Development dependencies
DEV_REQUIREMENTS = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-mock>=3.12.0",
    "pytest-cov>=4.1.0",
    "black>=23.11.0",
    "ruff>=0.1.6",
    "mypy>=1.7.0",
    "pre-commit>=3.5.0",
    "factory-boy>=3.3.0",
]

# Notebook dependencies
NOTEBOOK_REQUIREMENTS = [
    "jupyter>=1.0.0",
    "notebook>=7.0.0",
    "ipykernel>=6.26.0",
]

# Performance profiling
PROFILING_REQUIREMENTS = [
    "memory-profiler>=0.61.0",
    "py-spy>=0.3.14",
]

# Utility dependencies
UTILS_REQUIREMENTS = [
    "python-dateutil>=2.8.2",
    "gevent>=23.9.0",
    "asyncio-mqtt>=0.11.1",
    "openpyxl>=3.1.2",
    "python-docx>=1.1.0",
    "email-validator>=2.1.0",
]

# Combine all requirements for 'all' extra
ALL_REQUIREMENTS = (
    WEB_REQUIREMENTS +
    DATABASE_REQUIREMENTS +
    SCRAPING_REQUIREMENTS +
    SECURITY_REQUIREMENTS +
    DATA_REQUIREMENTS +
    NLP_REQUIREMENTS +
    VISION_REQUIREMENTS +
    MONITORING_REQUIREMENTS +
    UTILS_REQUIREMENTS
)

if __name__ == "__main__":
    setup(
        name="business-intel-scraper",
        version=VERSION,
        description="Enterprise Visual Analytics Platform for Business Intelligence",
        long_description=read_readme(),
        long_description_content_type="text/markdown",
        author="Business Intelligence Team",
        author_email="dev@businessintel.local",
        url="https://github.com/Trashytalk/scraper",
        packages=find_packages(),
        include_package_data=True,
        python_requires=">=3.11",
        install_requires=CORE_REQUIREMENTS,
        extras_require={
            # Individual feature groups
            "web": WEB_REQUIREMENTS,
            "database": DATABASE_REQUIREMENTS,
            "scraping": SCRAPING_REQUIREMENTS,
            "security": SECURITY_REQUIREMENTS,
            "data": DATA_REQUIREMENTS,
            "nlp": NLP_REQUIREMENTS,
            "nlp-advanced": NLP_REQUIREMENTS + NLP_ADVANCED_REQUIREMENTS,
            "vision": VISION_REQUIREMENTS,
            "monitoring": MONITORING_REQUIREMENTS,
            "utils": UTILS_REQUIREMENTS,
            
            # Development groups
            "dev": DEV_REQUIREMENTS,
            "notebook": NOTEBOOK_REQUIREMENTS,
            "profiling": PROFILING_REQUIREMENTS,
            
            # Combined groups
            "production": (
                WEB_REQUIREMENTS +
                DATABASE_REQUIREMENTS +
                SCRAPING_REQUIREMENTS +
                SECURITY_REQUIREMENTS +
                MONITORING_REQUIREMENTS
            ),
            "analytics": (
                DATA_REQUIREMENTS +
                NLP_REQUIREMENTS +
                VISION_REQUIREMENTS +
                NOTEBOOK_REQUIREMENTS
            ),
            "all": ALL_REQUIREMENTS,
            "full": ALL_REQUIREMENTS + DEV_REQUIREMENTS + NOTEBOOK_REQUIREMENTS + PROFILING_REQUIREMENTS,
        },
        entry_points={
            "console_scripts": [
                "business-intel=business_intel_scraper.cli:main",
                "bi-scraper=business_intel_scraper.cli:main",
            ],
        },
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
            "Topic :: Office/Business :: Financial :: Investment",
        ],
        keywords="business intelligence scraping analytics osint data-mining",
        project_urls={
            "Bug Reports": "https://github.com/Trashytalk/scraper/issues",
            "Source": "https://github.com/Trashytalk/scraper",
            "Documentation": "https://github.com/Trashytalk/scraper/docs",
        },
    )
