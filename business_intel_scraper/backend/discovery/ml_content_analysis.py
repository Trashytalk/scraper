#!/usr/bin/env python3
"""
Phase 3: ML-Powered Content Analysis and Intelligent Pattern Recognition

This module implements advanced machine learning capabilities for:
- Intelligent content classification and analysis
- Pattern recognition in scraped data
- Predictive source discovery
- Quality assessment and content validation
- Smart data extraction optimization
"""

import asyncio
import json
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from pathlib import Path
import hashlib

# ML and data processing imports
try:
    import numpy as np
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from textblob import TextBlob
    import nltk
    from collections import Counter, defaultdict
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    # Fallback implementations
    np = None
    pd = None

# NLP Processing
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from bs4 import BeautifulSoup
import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class ContentFeatures:
    """Structured representation of content features for ML analysis"""
    
    # Basic metadata
    url: str
    title: str = ""
    meta_description: str = ""
    language: str = "en"
    
    # Content characteristics
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    heading_count: int = 0
    
    # Structure features
    dom_depth: int = 0
    element_counts: Dict[str, int] = field(default_factory=dict)
    css_classes: Set[str] = field(default_factory=set)
    
    # Text features
    text_content: str = ""
    keywords: List[str] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    
    # Data quality indicators
    quality_score: float = 0.0
    completeness_score: float = 0.0
    uniqueness_score: float = 0.0
    
    # Pattern indicators
    data_patterns: List[str] = field(default_factory=list)
    content_type: str = "unknown"
    business_category: str = "unknown"
    
    # Extraction metadata
    extraction_confidence: float = 0.0
    recommended_selectors: List[str] = field(default_factory=list)
    extraction_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamps
    analyzed_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/serialization"""
        return {
            'url': self.url,
            'title': self.title,
            'meta_description': self.meta_description,
            'language': self.language,
            'word_count': self.word_count,
            'sentence_count': self.sentence_count,
            'paragraph_count': self.paragraph_count,
            'heading_count': self.heading_count,
            'dom_depth': self.dom_depth,
            'element_counts': self.element_counts,
            'css_classes': list(self.css_classes),
            'text_content': self.text_content[:1000],  # Truncate for storage
            'keywords': self.keywords[:20],  # Top 20 keywords
            'entities': self.entities[:10],  # Top 10 entities
            'topics': self.topics,
            'quality_score': self.quality_score,
            'completeness_score': self.completeness_score,
            'uniqueness_score': self.uniqueness_score,
            'data_patterns': self.data_patterns,
            'content_type': self.content_type,
            'business_category': self.business_category,
            'extraction_confidence': self.extraction_confidence,
            'recommended_selectors': self.recommended_selectors,
            'extraction_suggestions': self.extraction_suggestions,
            'analyzed_at': self.analyzed_at.isoformat()
        }


class MLContentAnalyzer:
    """Machine learning powered content analysis engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + '.MLContentAnalyzer')
        
        # ML Models (lazy loaded)
        self._tfidf_vectorizer = None
        self._content_classifier = None
        self._topic_model = None
        self._quality_predictor = None
        
        # Analysis caches
        self.content_cache: Dict[str, ContentFeatures] = {}
        self.pattern_cache: Dict[str, List[str]] = {}
        self.similarity_cache: Dict[str, Dict[str, float]] = {}
        
        # NLP processor
        self._nlp_processor = None
        
        # Initialize if ML available
        if ML_AVAILABLE:
            self._initialize_ml_components()
        else:
            self.logger.warning("ML libraries not available, using fallback implementations")
    
    def _initialize_ml_components(self):
        """Initialize ML models and components"""
        try:
            # TF-IDF Vectorizer for content similarity
            self._tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95
            )
            
            # Content classifier for business categories
            self._content_classifier = MultinomialNB()
            
            # Topic modeling for content themes
            self._topic_model = LatentDirichletAllocation(
                n_components=10,
                random_state=42,
                max_iter=100
            )
            
            # Quality predictor
            self._quality_predictor = LogisticRegression(random_state=42)
            
            # Initialize spaCy if available
            if SPACY_AVAILABLE:
                try:
                    import spacy.cli
                    try:
                        self._nlp_processor = spacy.load("en_core_web_sm")
                    except OSError:
                        self.logger.info("Downloading spaCy English model...")
                        spacy.cli.download("en_core_web_sm")
                        self._nlp_processor = spacy.load("en_core_web_sm")
                except Exception as e:
                    self.logger.warning(f"Could not load spaCy model: {e}")
                    self._nlp_processor = None
            
            self.logger.info("ML components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing ML components: {e}")
            self._tfidf_vectorizer = None
    
    async def analyze_content(self, url: str, html_content: str, 
                            existing_features: Optional[ContentFeatures] = None) -> ContentFeatures:
        """Comprehensive ML-powered content analysis"""
        
        # Check cache first
        cache_key = hashlib.md5(f"{url}{html_content[:1000]}".encode()).hexdigest()
        if cache_key in self.content_cache:
            return self.content_cache[cache_key]
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Initialize features
        features = existing_features or ContentFeatures(url=url)
        
        # Extract basic metadata
        await self._extract_basic_features(features, soup)
        
        # Extract structural features
        await self._extract_structural_features(features, soup)
        
        # Extract text features with NLP
        await self._extract_text_features(features, soup)
        
        # Classify content type and business category
        await self._classify_content(features)
        
        # Assess data quality
        await self._assess_data_quality(features, soup)
        
        # Identify data patterns
        await self._identify_data_patterns(features, soup)
        
        # Generate extraction suggestions
        await self._generate_extraction_suggestions(features, soup)
        
        # Cache results
        self.content_cache[cache_key] = features
        
        self.logger.info(f"Content analysis complete for {url}")
        return features
    
    async def _extract_basic_features(self, features: ContentFeatures, soup: BeautifulSoup):
        """Extract basic page metadata and characteristics"""
        
        # Title extraction
        title_tag = soup.find('title')
        features.title = title_tag.get_text().strip() if title_tag else ""
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            features.meta_description = meta_desc.get('content', '').strip()
        
        # Language detection
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            features.language = html_tag.get('lang').split('-')[0]
        
        # Text content extraction
        # Remove script and style content
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        features.text_content = soup.get_text(separator=' ', strip=True)
        
        # Basic text statistics
        if features.text_content:
            words = features.text_content.split()
            features.word_count = len(words)
            
            sentences = re.split(r'[.!?]+', features.text_content)
            features.sentence_count = len([s for s in sentences if s.strip()])
            
            paragraphs = soup.find_all(['p', 'div'])
            features.paragraph_count = len(paragraphs)
            
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            features.heading_count = len(headings)
    
    async def _extract_structural_features(self, features: ContentFeatures, soup: BeautifulSoup):
        """Extract DOM structural features"""
        
        # Calculate DOM depth
        max_depth = 0
        for element in soup.find_all():
            depth = len(list(element.parents))
            max_depth = max(max_depth, depth)
        features.dom_depth = max_depth
        
        # Element counts
        element_counts = Counter()
        for element in soup.find_all():
            element_counts[element.name] += 1
        features.element_counts = dict(element_counts.most_common(20))
        
        # CSS classes
        css_classes = set()
        for element in soup.find_all(class_=True):
            classes = element.get('class', [])
            if isinstance(classes, list):
                css_classes.update(classes)
            elif isinstance(classes, str):
                css_classes.update(classes.split())
        features.css_classes = css_classes
    
    async def _extract_text_features(self, features: ContentFeatures, soup: BeautifulSoup):
        """Extract text features using NLP"""
        
        if not features.text_content:
            return
        
        try:
            # Keyword extraction using TF-IDF (simple approach)
            if ML_AVAILABLE and self._tfidf_vectorizer:
                # Clean text for analysis
                clean_text = re.sub(r'[^a-zA-Z\s]', ' ', features.text_content.lower())
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                
                if len(clean_text.split()) > 10:  # Minimum words for meaningful analysis
                    try:
                        # Fit and extract keywords
                        tfidf_matrix = self._tfidf_vectorizer.fit_transform([clean_text])
                        feature_names = self._tfidf_vectorizer.get_feature_names_out()
                        
                        # Get top TF-IDF scores
                        tfidf_scores = tfidf_matrix.toarray()[0]
                        top_indices = tfidf_scores.argsort()[-20:][::-1]
                        features.keywords = [feature_names[i] for i in top_indices if tfidf_scores[i] > 0]
                        
                    except Exception as e:
                        self.logger.debug(f"TF-IDF extraction failed: {e}")
            
            # Named entity recognition with spaCy
            if self._nlp_processor and len(features.text_content) < 100000:  # Limit for performance
                try:
                    doc = self._nlp_processor(features.text_content[:10000])  # Limit text length
                    
                    entities = []
                    for ent in doc.ents:
                        entities.append({
                            'text': ent.text,
                            'label': ent.label_,
                            'confidence': float(getattr(ent, 'probability', 0.8))
                        })
                    features.entities = entities[:10]  # Top 10 entities
                    
                except Exception as e:
                    self.logger.debug(f"NER extraction failed: {e}")
            
            # Simple keyword extraction fallback
            if not features.keywords:
                # Use simple word frequency
                words = re.findall(r'\b[a-zA-Z]{4,}\b', features.text_content.lower())
                word_freq = Counter(words)
                # Filter out common words
                common_words = {'that', 'this', 'with', 'have', 'will', 'they', 'from', 'been', 
                               'said', 'each', 'which', 'their', 'time', 'about', 'would', 'there'}
                filtered_words = {word: count for word, count in word_freq.items() 
                                if word not in common_words and len(word) > 3}
                features.keywords = list(dict(Counter(filtered_words).most_common(20)).keys())
                
        except Exception as e:
            self.logger.error(f"Error extracting text features: {e}")
    
    async def _classify_content(self, features: ContentFeatures):
        """Classify content type and business category"""
        
        try:
            # Simple rule-based classification for now
            text_lower = features.text_content.lower()
            title_lower = features.title.lower()
            
            # Content type classification
            if any(word in text_lower for word in ['product', 'buy', 'price', 'cart', 'shop']):
                features.content_type = 'ecommerce'
            elif any(word in text_lower for word in ['article', 'blog', 'post', 'author']):
                features.content_type = 'article'
            elif any(word in text_lower for word in ['company', 'about', 'team', 'contact']):
                features.content_type = 'corporate'
            elif any(word in text_lower for word in ['news', 'breaking', 'report', 'story']):
                features.content_type = 'news'
            elif any(word in text_lower for word in ['listing', 'directory', 'search', 'filter']):
                features.content_type = 'listing'
            else:
                features.content_type = 'general'
            
            # Business category classification
            business_keywords = {
                'technology': ['software', 'tech', 'digital', 'app', 'platform', 'cloud', 'AI', 'data'],
                'retail': ['store', 'shop', 'buy', 'sale', 'product', 'retail', 'commerce'],
                'finance': ['bank', 'finance', 'loan', 'investment', 'money', 'credit', 'trading'],
                'healthcare': ['health', 'medical', 'doctor', 'hospital', 'treatment', 'medicine'],
                'education': ['school', 'education', 'learn', 'course', 'university', 'training'],
                'media': ['news', 'media', 'entertainment', 'video', 'content', 'publish'],
                'real_estate': ['property', 'real estate', 'home', 'rent', 'house', 'apartment'],
                'automotive': ['car', 'auto', 'vehicle', 'truck', 'dealer', 'automotive'],
                'travel': ['travel', 'hotel', 'flight', 'vacation', 'trip', 'tourism'],
                'food': ['restaurant', 'food', 'recipe', 'menu', 'dining', 'kitchen']
            }
            
            category_scores = {}
            for category, keywords in business_keywords.items():
                score = sum(1 for keyword in keywords 
                          if keyword in text_lower or keyword in title_lower)
                if score > 0:
                    category_scores[category] = score
            
            if category_scores:
                features.business_category = max(category_scores.items(), key=lambda x: x[1])[0]
            
        except Exception as e:
            self.logger.error(f"Error classifying content: {e}")
    
    async def _assess_data_quality(self, features: ContentFeatures, soup: BeautifulSoup):
        """Assess data quality and completeness"""
        
        try:
            quality_factors = []
            
            # Text content quality
            if features.word_count > 100:
                quality_factors.append(0.3)
            elif features.word_count > 50:
                quality_factors.append(0.2)
            else:
                quality_factors.append(0.1)
            
            # Structure quality
            if features.heading_count > 0:
                quality_factors.append(0.2)
            else:
                quality_factors.append(0.0)
            
            # Metadata quality
            if features.title and len(features.title) > 10:
                quality_factors.append(0.2)
            else:
                quality_factors.append(0.0)
            
            if features.meta_description:
                quality_factors.append(0.1)
            else:
                quality_factors.append(0.0)
            
            # Content richness
            if len(features.keywords) > 5:
                quality_factors.append(0.2)
            elif len(features.keywords) > 0:
                quality_factors.append(0.1)
            else:
                quality_factors.append(0.0)
            
            features.quality_score = sum(quality_factors)
            
            # Completeness assessment
            completeness_factors = []
            
            # Required elements present
            required_elements = ['title', 'h1', 'p']
            present_elements = sum(1 for elem in required_elements if soup.find(elem))
            completeness_factors.append(present_elements / len(required_elements) * 0.4)
            
            # Content depth
            if features.word_count > 500:
                completeness_factors.append(0.3)
            elif features.word_count > 200:
                completeness_factors.append(0.2)
            else:
                completeness_factors.append(0.1)
            
            # Structural completeness
            if features.dom_depth > 5:
                completeness_factors.append(0.3)
            elif features.dom_depth > 3:
                completeness_factors.append(0.2)
            else:
                completeness_factors.append(0.1)
            
            features.completeness_score = sum(completeness_factors)
            
            # Uniqueness (simplified - would need comparison with other content)
            features.uniqueness_score = min(1.0, len(set(features.keywords)) / 20.0)
            
        except Exception as e:
            self.logger.error(f"Error assessing data quality: {e}")
    
    async def _identify_data_patterns(self, features: ContentFeatures, soup: BeautifulSoup):
        """Identify common data patterns in content"""
        
        try:
            patterns = []
            
            # Common data patterns
            text = features.text_content
            
            # Price patterns
            price_pattern = r'\$[\d,]+\.?\d*'
            if re.search(price_pattern, text):
                patterns.append('pricing')
            
            # Date patterns
            date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
            if re.search(date_pattern, text):
                patterns.append('dates')
            
            # Contact patterns
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            if re.search(email_pattern, text) or re.search(phone_pattern, text):
                patterns.append('contact_info')
            
            # Address patterns
            address_pattern = r'\b\d+\s+\w+\s+(?:street|st|avenue|ave|road|rd|boulevard|blvd|lane|ln|drive|dr)'
            if re.search(address_pattern, text, re.IGNORECASE):
                patterns.append('addresses')
            
            # Product listings
            if soup.find_all(['ul', 'ol']) and any(word in text.lower() for word in ['product', 'item', 'model']):
                patterns.append('product_listings')
            
            # Tables (structured data)
            if soup.find_all('table'):
                patterns.append('tabular_data')
            
            # Forms (data collection)
            if soup.find_all('form'):
                patterns.append('forms')
            
            # Navigation/menu patterns
            if soup.find_all(['nav', 'menu']) or len(soup.find_all('a')) > 10:
                patterns.append('navigation')
            
            features.data_patterns = patterns
            
        except Exception as e:
            self.logger.error(f"Error identifying data patterns: {e}")
    
    async def _generate_extraction_suggestions(self, features: ContentFeatures, soup: BeautifulSoup):
        """Generate smart extraction suggestions based on analysis"""
        
        try:
            suggestions = []
            confidence_scores = []
            
            # Based on content type, suggest extraction strategies
            if features.content_type == 'ecommerce':
                # Product-specific suggestions
                product_selectors = []
                
                # Look for product names
                for selector in ['.product-name', '.product-title', 'h1', 'h2']:
                    if soup.select(selector):
                        product_selectors.append(selector)
                        break
                
                # Look for prices
                price_selectors = []
                for selector in ['.price', '.cost', '[class*="price"]', '[id*="price"]']:
                    if soup.select(selector):
                        price_selectors.append(selector)
                        break
                
                if product_selectors or price_selectors:
                    suggestions.append({
                        'type': 'product_extraction',
                        'selectors': {
                            'name': product_selectors[0] if product_selectors else 'h1',
                            'price': price_selectors[0] if price_selectors else '[class*="price"]'
                        },
                        'description': 'Extract product information including name and price'
                    })
                    confidence_scores.append(0.8 if product_selectors and price_selectors else 0.6)
            
            elif features.content_type == 'article':
                # Article-specific suggestions
                suggestions.append({
                    'type': 'article_extraction',
                    'selectors': {
                        'title': 'h1',
                        'content': 'article, .content, .post-content, main',
                        'author': '.author, .byline, [rel="author"]',
                        'date': '.date, .published, time'
                    },
                    'description': 'Extract article content with metadata'
                })
                confidence_scores.append(0.7)
            
            elif features.content_type == 'listing':
                # Listing-specific suggestions
                list_items = soup.find_all(['li', '.item', '.listing'])
                if list_items:
                    suggestions.append({
                        'type': 'listing_extraction',
                        'selectors': {
                            'items': 'li, .item, .listing',
                            'title': 'h2, h3, .title',
                            'description': 'p, .description'
                        },
                        'description': f'Extract {len(list_items)} listing items'
                    })
                    confidence_scores.append(0.8)
            
            # Pattern-based suggestions
            if 'tabular_data' in features.data_patterns:
                tables = soup.find_all('table')
                if tables:
                    suggestions.append({
                        'type': 'table_extraction',
                        'selectors': {
                            'table': 'table',
                            'headers': 'th',
                            'rows': 'tr',
                            'cells': 'td'
                        },
                        'description': f'Extract data from {len(tables)} table(s)'
                    })
                    confidence_scores.append(0.9)
            
            if 'contact_info' in features.data_patterns:
                suggestions.append({
                    'type': 'contact_extraction',
                    'patterns': {
                        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
                    },
                    'description': 'Extract contact information using regex patterns'
                })
                confidence_scores.append(0.8)
            
            # Set extraction confidence based on suggestions
            features.extraction_confidence = max(confidence_scores) if confidence_scores else 0.0
            features.extraction_suggestions = suggestions
            
            # Generate recommended selectors
            recommended_selectors = []
            for suggestion in suggestions:
                if 'selectors' in suggestion:
                    recommended_selectors.extend(suggestion['selectors'].values())
            features.recommended_selectors = list(set(recommended_selectors))
            
        except Exception as e:
            self.logger.error(f"Error generating extraction suggestions: {e}")
    
    async def find_similar_content(self, target_features: ContentFeatures, 
                                 candidate_features: List[ContentFeatures], 
                                 threshold: float = 0.5) -> List[Tuple[ContentFeatures, float]]:
        """Find content similar to target using ML similarity metrics"""
        
        if not ML_AVAILABLE or not self._tfidf_vectorizer:
            # Fallback to simple keyword matching
            return self._find_similar_content_fallback(target_features, candidate_features, threshold)
        
        try:
            # Prepare text data
            target_text = f"{target_features.title} {target_features.text_content[:1000]}"
            candidate_texts = [f"{f.title} {f.text_content[:1000]}" for f in candidate_features]
            
            all_texts = [target_text] + candidate_texts
            
            # Compute TF-IDF vectors
            tfidf_matrix = self._tfidf_vectorizer.fit_transform(all_texts)
            
            # Calculate cosine similarities
            target_vector = tfidf_matrix[0:1]
            candidate_vectors = tfidf_matrix[1:]
            
            similarities = cosine_similarity(target_vector, candidate_vectors)[0]
            
            # Filter by threshold and sort by similarity
            similar_content = []
            for i, similarity in enumerate(similarities):
                if similarity >= threshold:
                    similar_content.append((candidate_features[i], float(similarity)))
            
            similar_content.sort(key=lambda x: x[1], reverse=True)
            return similar_content
            
        except Exception as e:
            self.logger.error(f"Error finding similar content with ML: {e}")
            return self._find_similar_content_fallback(target_features, candidate_features, threshold)
    
    def _find_similar_content_fallback(self, target_features: ContentFeatures, 
                                     candidate_features: List[ContentFeatures], 
                                     threshold: float) -> List[Tuple[ContentFeatures, float]]:
        """Fallback similarity matching using keyword overlap"""
        
        target_keywords = set(target_features.keywords)
        similar_content = []
        
        for candidate in candidate_features:
            candidate_keywords = set(candidate.keywords)
            
            if target_keywords and candidate_keywords:
                # Jaccard similarity
                intersection = len(target_keywords & candidate_keywords)
                union = len(target_keywords | candidate_keywords)
                similarity = intersection / union if union > 0 else 0.0
                
                if similarity >= threshold:
                    similar_content.append((candidate, similarity))
        
        similar_content.sort(key=lambda x: x[1], reverse=True)
        return similar_content
    
    async def predict_content_quality(self, features: ContentFeatures) -> Dict[str, float]:
        """Predict content quality metrics using ML"""
        
        try:
            # Feature vector for quality prediction
            feature_vector = [
                features.word_count,
                features.sentence_count,
                features.paragraph_count,
                features.heading_count,
                features.dom_depth,
                len(features.keywords),
                len(features.entities),
                len(features.data_patterns),
                1 if features.title else 0,
                1 if features.meta_description else 0,
                len(features.css_classes)
            ]
            
            # Simple quality scoring (would be trained on labeled data in production)
            quality_score = min(1.0, (
                min(features.word_count / 1000, 1.0) * 0.3 +
                min(len(features.keywords) / 20, 1.0) * 0.2 +
                min(features.dom_depth / 10, 1.0) * 0.2 +
                (1 if features.title else 0) * 0.15 +
                (1 if features.meta_description else 0) * 0.15
            ))
            
            return {
                'overall_quality': quality_score,
                'content_richness': min(features.word_count / 500, 1.0),
                'structural_quality': min(features.dom_depth / 8, 1.0),
                'metadata_completeness': (
                    (1 if features.title else 0) + 
                    (1 if features.meta_description else 0)
                ) / 2,
                'extraction_potential': features.extraction_confidence
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting content quality: {e}")
            return {
                'overall_quality': 0.5,
                'content_richness': 0.5,
                'structural_quality': 0.5,
                'metadata_completeness': 0.5,
                'extraction_potential': 0.5
            }
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get statistics about analyzed content"""
        
        if not self.content_cache:
            return {'total_analyzed': 0}
        
        features_list = list(self.content_cache.values())
        
        # Content type distribution
        content_types = Counter(f.content_type for f in features_list)
        
        # Business category distribution
        business_categories = Counter(f.business_category for f in features_list)
        
        # Quality statistics
        quality_scores = [f.quality_score for f in features_list]
        
        # Pattern frequency
        all_patterns = []
        for f in features_list:
            all_patterns.extend(f.data_patterns)
        pattern_frequency = Counter(all_patterns)
        
        return {
            'total_analyzed': len(features_list),
            'content_types': dict(content_types),
            'business_categories': dict(business_categories),
            'quality_stats': {
                'average': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
                'max': max(quality_scores) if quality_scores else 0,
                'min': min(quality_scores) if quality_scores else 0
            },
            'common_patterns': dict(pattern_frequency.most_common(10)),
            'languages': Counter(f.language for f in features_list),
            'avg_word_count': sum(f.word_count for f in features_list) / len(features_list)
        }


class PredictiveSourceDiscovery:
    """ML-powered predictive source discovery system"""
    
    def __init__(self, content_analyzer: MLContentAnalyzer):
        self.content_analyzer = content_analyzer
        self.logger = logging.getLogger(__name__ + '.PredictiveSourceDiscovery')
        
        # Source discovery models
        self.source_predictor = None
        self.pattern_matcher = None
        
        # Discovery cache and history
        self.discovered_sources: Dict[str, List[str]] = {}
        self.discovery_patterns: Dict[str, List[str]] = {}
        self.source_reliability: Dict[str, float] = {}
    
    async def discover_related_sources(self, seed_url: str, 
                                     content_features: ContentFeatures,
                                     max_sources: int = 10) -> List[Dict[str, Any]]:
        """Discover related sources using ML pattern recognition"""
        
        try:
            discovered = []
            
            # Pattern-based discovery
            pattern_sources = await self._discover_by_patterns(content_features)
            discovered.extend(pattern_sources)
            
            # Category-based discovery
            category_sources = await self._discover_by_category(content_features)
            discovered.extend(category_sources)
            
            # Structural similarity discovery
            structure_sources = await self._discover_by_structure(content_features)
            discovered.extend(structure_sources)
            
            # Remove duplicates and rank by confidence
            unique_sources = {}
            for source in discovered:
                url = source['url']
                if url not in unique_sources or source['confidence'] > unique_sources[url]['confidence']:
                    unique_sources[url] = source
            
            # Sort by confidence and return top results
            ranked_sources = sorted(unique_sources.values(), 
                                  key=lambda x: x['confidence'], reverse=True)
            
            return ranked_sources[:max_sources]
            
        except Exception as e:
            self.logger.error(f"Error discovering related sources: {e}")
            return []
    
    async def _discover_by_patterns(self, features: ContentFeatures) -> List[Dict[str, Any]]:
        """Discover sources with similar data patterns"""
        
        sources = []
        
        # Define pattern-based source suggestions
        pattern_sources = {
            'ecommerce': [
                'shopify.com/directory',
                'amazon.com/s',
                'etsy.com/search',
                'ebay.com/sch',
                'alibaba.com/trade'
            ],
            'news': [
                'news.google.com',
                'allsides.com/news',
                'reuters.com',
                'ap.org',
                'bbc.com/news'
            ],
            'real_estate': [
                'zillow.com',
                'realtor.com',
                'trulia.com',
                'redfin.com',
                'homes.com'
            ],
            'job_listings': [
                'indeed.com',
                'glassdoor.com',
                'linkedin.com/jobs',
                'monster.com',
                'ziprecruiter.com'
            ],
            'reviews': [
                'yelp.com',
                'tripadvisor.com',
                'trustpilot.com',
                'consumerreports.org',
                'google.com/maps'
            ]
        }
        
        # Match based on content type and business category
        relevant_patterns = []
        if features.content_type in pattern_sources:
            relevant_patterns.extend(pattern_sources[features.content_type])
        
        if features.business_category in pattern_sources:
            relevant_patterns.extend(pattern_sources[features.business_category])
        
        # Generate source suggestions
        for pattern in relevant_patterns:
            sources.append({
                'url': pattern,
                'confidence': 0.7,
                'reason': f'Pattern match: {features.content_type}/{features.business_category}',
                'discovery_method': 'pattern_based'
            })
        
        return sources
    
    async def _discover_by_category(self, features: ContentFeatures) -> List[Dict[str, Any]]:
        """Discover sources in the same business category"""
        
        sources = []
        
        # Industry-specific source directories
        category_directories = {
            'technology': [
                'crunchbase.com/search/organizations',
                'producthunt.com',
                'github.com/search',
                'stackshare.io/stacks'
            ],
            'finance': [
                'fintech.global/directory',
                'sec.gov/edgar/search',
                'bloomberg.com/markets',
                'yahoo.com/finance'
            ],
            'healthcare': [
                'healthgrades.com',
                'webmd.com/directories',
                'medicare.gov/care-compare'
            ],
            'education': [
                'usnews.com/best-colleges',
                'collegeboard.org',
                'coursera.org',
                'edx.org'
            ]
        }
        
        if features.business_category in category_directories:
            for directory in category_directories[features.business_category]:
                sources.append({
                    'url': directory,
                    'confidence': 0.8,
                    'reason': f'Industry directory: {features.business_category}',
                    'discovery_method': 'category_based'
                })
        
        return sources
    
    async def _discover_by_structure(self, features: ContentFeatures) -> List[Dict[str, Any]]:
        """Discover sources with similar structural patterns"""
        
        sources = []
        
        # Analyze structural features for discovery
        if 'tabular_data' in features.data_patterns:
            # Suggest data-rich sources
            data_sources = [
                'data.gov',
                'kaggle.com/datasets',
                'dataworld.com',
                'census.gov'
            ]
            
            for source in data_sources:
                sources.append({
                    'url': source,
                    'confidence': 0.6,
                    'reason': 'Similar tabular data structure',
                    'discovery_method': 'structure_based'
                })
        
        if 'product_listings' in features.data_patterns:
            # Suggest listing-style sources
            listing_sources = [
                'yellowpages.com',
                'foursquare.com',
                'opentable.com',
                'booking.com'
            ]
            
            for source in listing_sources:
                sources.append({
                    'url': source,
                    'confidence': 0.6,
                    'reason': 'Similar listing structure',
                    'discovery_method': 'structure_based'
                })
        
        return sources
    
    async def evaluate_source_potential(self, url: str, 
                                      features: ContentFeatures) -> Dict[str, Any]:
        """Evaluate the potential value of a source for data extraction"""
        
        try:
            evaluation = {
                'url': url,
                'overall_score': 0.0,
                'data_richness': 0.0,
                'extraction_feasibility': 0.0,
                'update_frequency_estimate': 'unknown',
                'recommended_extraction_method': 'unknown',
                'potential_data_volume': 'low',
                'business_value': 'medium'
            }
            
            # Data richness assessment
            richness_factors = []
            
            if features.word_count > 1000:
                richness_factors.append(0.3)
            elif features.word_count > 500:
                richness_factors.append(0.2)
            else:
                richness_factors.append(0.1)
            
            if len(features.data_patterns) > 3:
                richness_factors.append(0.3)
            elif len(features.data_patterns) > 1:
                richness_factors.append(0.2)
            else:
                richness_factors.append(0.0)
            
            if len(features.keywords) > 10:
                richness_factors.append(0.2)
            else:
                richness_factors.append(0.1)
            
            if features.extraction_confidence > 0.7:
                richness_factors.append(0.2)
            else:
                richness_factors.append(0.1)
            
            evaluation['data_richness'] = sum(richness_factors)
            
            # Extraction feasibility
            feasibility_score = features.extraction_confidence
            if 'tabular_data' in features.data_patterns:
                feasibility_score += 0.2
            if features.content_type in ['ecommerce', 'listing', 'article']:
                feasibility_score += 0.1
                
            evaluation['extraction_feasibility'] = min(1.0, feasibility_score)
            
            # Overall score
            evaluation['overall_score'] = (
                evaluation['data_richness'] * 0.4 +
                evaluation['extraction_feasibility'] * 0.4 +
                features.quality_score * 0.2
            )
            
            # Recommendations based on analysis
            if evaluation['overall_score'] > 0.8:
                evaluation['business_value'] = 'high'
                evaluation['potential_data_volume'] = 'high'
            elif evaluation['overall_score'] > 0.6:
                evaluation['business_value'] = 'medium'
                evaluation['potential_data_volume'] = 'medium'
            else:
                evaluation['business_value'] = 'low'
                evaluation['potential_data_volume'] = 'low'
            
            # Suggest extraction method
            if 'tabular_data' in features.data_patterns:
                evaluation['recommended_extraction_method'] = 'structured_scraping'
            elif features.content_type == 'ecommerce':
                evaluation['recommended_extraction_method'] = 'product_scraping'
            elif features.content_type == 'article':
                evaluation['recommended_extraction_method'] = 'content_scraping'
            else:
                evaluation['recommended_extraction_method'] = 'general_scraping'
            
            return evaluation
            
        except Exception as e:
            self.logger.error(f"Error evaluating source potential: {e}")
            return {
                'url': url,
                'overall_score': 0.0,
                'error': str(e)
            }


# Initialize global instances
if ML_AVAILABLE:
    content_analyzer = MLContentAnalyzer()
    predictive_discovery = PredictiveSourceDiscovery(content_analyzer)
else:
    content_analyzer = None
    predictive_discovery = None
