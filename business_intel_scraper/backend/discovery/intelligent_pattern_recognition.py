#!/usr/bin/env python3
"""
Phase 3: Intelligent Pattern Recognition and Learning System

This module implements advanced pattern recognition for:
- Automatic spider optimization based on learned patterns
- Content structure pattern detection
- Behavioral pattern analysis
- Predictive extraction strategy selection
- Self-improving scraping algorithms
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import hashlib
import pickle
from pathlib import Path

# ML imports for pattern recognition
try:
    import numpy as np
    import pandas as pd
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    np = None
    pd = None

from .ml_content_analysis import ContentFeatures, MLContentAnalyzer
from .data_quality_assessment import DataQualityMetrics

logger = logging.getLogger(__name__)


@dataclass
class ExtractionPattern:
    """Represents a learned extraction pattern"""
    
    pattern_id: str
    pattern_type: str  # 'structural', 'semantic', 'behavioral'
    confidence: float = 0.0
    
    # Pattern characteristics
    selectors: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    success_rate: float = 0.0
    usage_count: int = 0
    
    # Context information
    applicable_domains: Set[str] = field(default_factory=set)
    content_types: Set[str] = field(default_factory=set)
    business_categories: Set[str] = field(default_factory=set)
    
    # Performance metrics
    avg_extraction_time: float = 0.0
    avg_data_quality: float = 0.0
    error_rate: float = 0.0
    
    # Learning metadata
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    adaptation_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'pattern_id': self.pattern_id,
            'pattern_type': self.pattern_type,
            'confidence': self.confidence,
            'selectors': self.selectors,
            'attributes': self.attributes,
            'success_rate': self.success_rate,
            'usage_count': self.usage_count,
            'applicable_domains': list(self.applicable_domains),
            'content_types': list(self.content_types),
            'business_categories': list(self.business_categories),
            'avg_extraction_time': self.avg_extraction_time,
            'avg_data_quality': self.avg_data_quality,
            'error_rate': self.error_rate,
            'discovered_at': self.discovered_at.isoformat(),
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'adaptation_count': self.adaptation_count
        }


@dataclass
class LearningSession:
    """Represents a learning session from spider execution"""
    
    session_id: str
    spider_name: str
    target_url: str
    
    # Execution metrics
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0
    records_extracted: int = 0
    errors_encountered: int = 0
    
    # Quality metrics
    data_quality_score: float = 0.0
    content_features: Optional[ContentFeatures] = None
    extraction_patterns_used: List[str] = field(default_factory=list)
    
    # Learning data
    successful_selectors: Dict[str, float] = field(default_factory=dict)  # selector -> success_rate
    failed_selectors: List[str] = field(default_factory=list)
    adaptations_made: List[Dict[str, Any]] = field(default_factory=list)
    
    # Context
    page_structure_hash: str = ""
    response_characteristics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'session_id': self.session_id,
            'spider_name': self.spider_name,
            'target_url': self.target_url,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'records_extracted': self.records_extracted,
            'errors_encountered': self.errors_encountered,
            'data_quality_score': self.data_quality_score,
            'content_features': self.content_features.to_dict() if self.content_features else None,
            'extraction_patterns_used': self.extraction_patterns_used,
            'successful_selectors': self.successful_selectors,
            'failed_selectors': self.failed_selectors,
            'adaptations_made': self.adaptations_made,
            'page_structure_hash': self.page_structure_hash,
            'response_characteristics': self.response_characteristics
        }


class IntelligentPatternRecognizer:
    """ML-powered pattern recognition for spider optimization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + '.IntelligentPatternRecognizer')
        
        # Pattern storage
        self.patterns: Dict[str, ExtractionPattern] = {}
        self.learning_sessions: List[LearningSession] = []
        
        # ML models for pattern recognition
        self.pattern_classifier = None
        self.selector_optimizer = None
        self.quality_predictor = None
        
        # Pattern analysis components
        self.scaler = None
        self.pca = None
        
        # Caching
        self.pattern_cache: Dict[str, List[ExtractionPattern]] = {}
        self.model_cache: Dict[str, Any] = {}
        
        # Configuration
        self.min_pattern_confidence = 0.7
        self.max_patterns_per_type = 100
        self.learning_rate = 0.1
        
        # Initialize ML components
        if ML_AVAILABLE:
            self._initialize_ml_components()
        
        # Load existing patterns
        self._load_patterns()
    
    def _initialize_ml_components(self):
        """Initialize ML models for pattern recognition"""
        
        try:
            # Pattern classifier to categorize extraction strategies
            self.pattern_classifier = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )
            
            # Selector optimizer for choosing best selectors
            self.selector_optimizer = DecisionTreeClassifier(
                random_state=42,
                max_depth=8
            )
            
            # Quality predictor to estimate extraction success
            self.quality_predictor = RandomForestClassifier(
                n_estimators=50,
                random_state=42
            )
            
            # Dimensionality reduction for pattern clustering
            self.pca = PCA(n_components=10)
            self.scaler = StandardScaler()
            
            self.logger.info("ML pattern recognition components initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing ML components: {e}")
    
    def _load_patterns(self):
        """Load existing patterns from storage"""
        
        try:
            patterns_file = Path("data/patterns/extraction_patterns.json")
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    patterns_data = json.load(f)
                
                for pattern_data in patterns_data:
                    pattern = ExtractionPattern(
                        pattern_id=pattern_data['pattern_id'],
                        pattern_type=pattern_data['pattern_type'],
                        confidence=pattern_data['confidence'],
                        selectors=pattern_data['selectors'],
                        attributes=pattern_data['attributes'],
                        success_rate=pattern_data['success_rate'],
                        usage_count=pattern_data['usage_count'],
                        applicable_domains=set(pattern_data['applicable_domains']),
                        content_types=set(pattern_data['content_types']),
                        business_categories=set(pattern_data['business_categories']),
                        avg_extraction_time=pattern_data['avg_extraction_time'],
                        avg_data_quality=pattern_data['avg_data_quality'],
                        error_rate=pattern_data['error_rate'],
                        discovered_at=datetime.fromisoformat(pattern_data['discovered_at']),
                        last_used=datetime.fromisoformat(pattern_data['last_used']) if pattern_data['last_used'] else None,
                        adaptation_count=pattern_data['adaptation_count']
                    )
                    self.patterns[pattern.pattern_id] = pattern
                
                self.logger.info(f"Loaded {len(self.patterns)} extraction patterns")
                
        except Exception as e:
            self.logger.info(f"No existing patterns found or error loading: {e}")
    
    def _save_patterns(self):
        """Save patterns to storage"""
        
        try:
            patterns_file = Path("data/patterns/extraction_patterns.json")
            patterns_file.parent.mkdir(parents=True, exist_ok=True)
            
            patterns_data = [pattern.to_dict() for pattern in self.patterns.values()]
            
            with open(patterns_file, 'w') as f:
                json.dump(patterns_data, f, indent=2)
            
            self.logger.debug(f"Saved {len(self.patterns)} patterns to storage")
            
        except Exception as e:
            self.logger.error(f"Error saving patterns: {e}")
    
    async def learn_from_session(self, session: LearningSession) -> List[ExtractionPattern]:
        """Learn extraction patterns from a spider execution session"""
        
        try:
            self.learning_sessions.append(session)
            discovered_patterns = []
            
            # Extract patterns from successful selectors
            if session.successful_selectors:
                structural_patterns = await self._discover_structural_patterns(session)
                discovered_patterns.extend(structural_patterns)
            
            # Learn semantic patterns from content
            if session.content_features:
                semantic_patterns = await self._discover_semantic_patterns(session)
                discovered_patterns.extend(semantic_patterns)
            
            # Learn behavioral patterns from execution characteristics
            behavioral_patterns = await self._discover_behavioral_patterns(session)
            discovered_patterns.extend(behavioral_patterns)
            
            # Update existing patterns with new data
            await self._update_existing_patterns(session)
            
            # Train ML models if enough data
            if len(self.learning_sessions) % 10 == 0:  # Every 10 sessions
                await self._train_pattern_models()
            
            # Save patterns
            self._save_patterns()
            
            self.logger.info(f"Learned {len(discovered_patterns)} new patterns from session {session.session_id}")
            return discovered_patterns
            
        except Exception as e:
            self.logger.error(f"Error learning from session: {e}")
            return []
    
    async def _discover_structural_patterns(self, session: LearningSession) -> List[ExtractionPattern]:
        """Discover structural extraction patterns"""
        
        patterns = []
        
        try:
            # Group successful selectors by similarity
            selector_groups = self._group_similar_selectors(session.successful_selectors)
            
            for group_selectors in selector_groups:
                if len(group_selectors) >= 2:  # Need multiple similar selectors
                    # Create structural pattern
                    pattern_id = f"struct_{hashlib.md5(str(sorted(group_selectors)).encode()).hexdigest()[:8]}"
                    
                    # Calculate pattern confidence from selector success rates
                    success_rates = [session.successful_selectors[sel] for sel in group_selectors]
                    avg_success_rate = sum(success_rates) / len(success_rates)
                    
                    if avg_success_rate > 0.7:  # Only patterns with good success rate
                        pattern = ExtractionPattern(
                            pattern_id=pattern_id,
                            pattern_type='structural',
                            confidence=avg_success_rate,
                            selectors=list(group_selectors),
                            success_rate=avg_success_rate,
                            usage_count=1
                        )
                        
                        # Add context from session
                        if session.content_features:
                            pattern.content_types.add(session.content_features.content_type)
                            pattern.business_categories.add(session.content_features.business_category)
                        
                        # Extract domain from URL
                        try:
                            from urllib.parse import urlparse
                            domain = urlparse(session.target_url).netloc
                            pattern.applicable_domains.add(domain)
                        except Exception:
                            pass
                        
                        # Performance metrics
                        pattern.avg_extraction_time = session.duration
                        pattern.avg_data_quality = session.data_quality_score
                        pattern.error_rate = session.errors_encountered / max(session.records_extracted, 1)
                        
                        patterns.append(pattern)
                        self.patterns[pattern_id] = pattern
            
        except Exception as e:
            self.logger.error(f"Error discovering structural patterns: {e}")
        
        return patterns
    
    async def _discover_semantic_patterns(self, session: LearningSession) -> List[ExtractionPattern]:
        """Discover semantic content patterns"""
        
        patterns = []
        
        try:
            if not session.content_features:
                return patterns
            
            features = session.content_features
            
            # Pattern based on content type and business category
            pattern_id = f"sem_{features.content_type}_{features.business_category}_{hashlib.md5(session.target_url.encode()).hexdigest()[:8]}"
            
            # Check if this semantic pattern already exists
            existing_pattern = None
            for pattern in self.patterns.values():
                if (pattern.pattern_type == 'semantic' and 
                    features.content_type in pattern.content_types and
                    features.business_category in pattern.business_categories):
                    existing_pattern = pattern
                    break
            
            if existing_pattern:
                # Update existing pattern
                existing_pattern.usage_count += 1
                existing_pattern.last_used = datetime.utcnow()
                
                # Update performance metrics (moving average)
                alpha = self.learning_rate
                existing_pattern.avg_extraction_time = (
                    (1 - alpha) * existing_pattern.avg_extraction_time + 
                    alpha * session.duration
                )
                existing_pattern.avg_data_quality = (
                    (1 - alpha) * existing_pattern.avg_data_quality + 
                    alpha * session.data_quality_score
                )
                
                # Add successful selectors if they're not already there
                for selector in session.successful_selectors:
                    if selector not in existing_pattern.selectors:
                        existing_pattern.selectors.append(selector)
                
            else:
                # Create new semantic pattern
                pattern = ExtractionPattern(
                    pattern_id=pattern_id,
                    pattern_type='semantic',
                    confidence=0.8,  # Start with good confidence for semantic patterns
                    selectors=list(session.successful_selectors.keys()),
                    success_rate=sum(session.successful_selectors.values()) / len(session.successful_selectors),
                    usage_count=1
                )
                
                pattern.content_types.add(features.content_type)
                pattern.business_categories.add(features.business_category)
                
                # Add semantic attributes
                pattern.attributes = {
                    'keywords': features.keywords[:10],
                    'data_patterns': features.data_patterns,
                    'extraction_suggestions': features.extraction_suggestions,
                    'recommended_selectors': features.recommended_selectors
                }
                
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(session.target_url).netloc
                    pattern.applicable_domains.add(domain)
                except Exception:
                    pass
                
                pattern.avg_extraction_time = session.duration
                pattern.avg_data_quality = session.data_quality_score
                pattern.error_rate = session.errors_encountered / max(session.records_extracted, 1)
                
                patterns.append(pattern)
                self.patterns[pattern_id] = pattern
        
        except Exception as e:
            self.logger.error(f"Error discovering semantic patterns: {e}")
        
        return patterns
    
    async def _discover_behavioral_patterns(self, session: LearningSession) -> List[ExtractionPattern]:
        """Discover behavioral patterns from spider execution"""
        
        patterns = []
        
        try:
            # Pattern based on response characteristics and adaptations
            if session.adaptations_made:
                pattern_id = f"behav_{hashlib.md5(json.dumps(session.adaptations_made, sort_keys=True).encode()).hexdigest()[:8]}"
                
                pattern = ExtractionPattern(
                    pattern_id=pattern_id,
                    pattern_type='behavioral',
                    confidence=0.7,
                    selectors=[],
                    success_rate=1 - (session.errors_encountered / max(session.records_extracted, 1)),
                    usage_count=1
                )
                
                # Store behavioral attributes
                pattern.attributes = {
                    'adaptations': session.adaptations_made,
                    'response_characteristics': session.response_characteristics,
                    'page_structure_hash': session.page_structure_hash,
                    'error_patterns': session.failed_selectors
                }
                
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(session.target_url).netloc
                    pattern.applicable_domains.add(domain)
                except Exception:
                    pass
                
                if session.content_features:
                    pattern.content_types.add(session.content_features.content_type)
                    pattern.business_categories.add(session.content_features.business_category)
                
                pattern.avg_extraction_time = session.duration
                pattern.avg_data_quality = session.data_quality_score
                pattern.error_rate = session.errors_encountered / max(session.records_extracted, 1)
                
                patterns.append(pattern)
                self.patterns[pattern_id] = pattern
        
        except Exception as e:
            self.logger.error(f"Error discovering behavioral patterns: {e}")
        
        return patterns
    
    async def _update_existing_patterns(self, session: LearningSession):
        """Update existing patterns with new session data"""
        
        try:
            for pattern in self.patterns.values():
                # Check if pattern is applicable to this session
                applicable = False
                
                # Check domain applicability
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(session.target_url).netloc
                    if domain in pattern.applicable_domains:
                        applicable = True
                except Exception:
                    pass
                
                # Check content type applicability
                if session.content_features:
                    if (session.content_features.content_type in pattern.content_types or
                        session.content_features.business_category in pattern.business_categories):
                        applicable = True
                
                # Check selector overlap
                session_selectors = set(session.successful_selectors.keys())
                pattern_selectors = set(pattern.selectors)
                if len(session_selectors & pattern_selectors) > 0:
                    applicable = True
                
                if applicable:
                    # Update pattern with new data
                    pattern.usage_count += 1
                    pattern.last_used = datetime.utcnow()
                    
                    # Update performance metrics (moving average)
                    alpha = self.learning_rate
                    pattern.avg_extraction_time = (
                        (1 - alpha) * pattern.avg_extraction_time + 
                        alpha * session.duration
                    )
                    pattern.avg_data_quality = (
                        (1 - alpha) * pattern.avg_data_quality + 
                        alpha * session.data_quality_score
                    )
                    
                    session_error_rate = session.errors_encountered / max(session.records_extracted, 1)
                    pattern.error_rate = (
                        (1 - alpha) * pattern.error_rate + 
                        alpha * session_error_rate
                    )
                    
                    # Update success rate based on session performance
                    session_success_rate = 1 - session_error_rate
                    pattern.success_rate = (
                        (1 - alpha) * pattern.success_rate + 
                        alpha * session_success_rate
                    )
                    
                    # Update confidence based on success rate and usage
                    usage_factor = min(1.0, pattern.usage_count / 10)  # More usage = more confidence
                    pattern.confidence = pattern.success_rate * usage_factor
        
        except Exception as e:
            self.logger.error(f"Error updating existing patterns: {e}")
    
    async def _train_pattern_models(self):
        """Train ML models on accumulated learning data"""
        
        try:
            if not ML_AVAILABLE or len(self.learning_sessions) < 10:
                return
            
            self.logger.info("Training pattern recognition models...")
            
            # Prepare training data
            features = []
            labels = []
            
            for session in self.learning_sessions:
                if session.content_features:
                    # Feature vector from session
                    feature_vector = [
                        session.duration,
                        session.records_extracted,
                        session.errors_encountered,
                        session.data_quality_score,
                        len(session.successful_selectors),
                        len(session.failed_selectors),
                        len(session.content_features.keywords),
                        session.content_features.word_count,
                        session.content_features.quality_score,
                        session.content_features.extraction_confidence
                    ]
                    
                    features.append(feature_vector)
                    
                    # Label based on session success
                    success_score = (
                        session.data_quality_score * 0.4 +
                        (1 - session.errors_encountered / max(session.records_extracted, 1)) * 0.6
                    )
                    labels.append('successful' if success_score > 0.7 else 'needs_improvement')
            
            if len(features) >= 10:
                # Train pattern classifier
                X = np.array(features)
                y = np.array(labels)
                
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                # Scale features
                X_train_scaled = self.scaler.fit_transform(X_train)
                X_test_scaled = self.scaler.transform(X_test)
                
                # Train classifier
                self.pattern_classifier.fit(X_train_scaled, y_train)
                
                # Evaluate
                y_pred = self.pattern_classifier.predict(X_test_scaled)
                accuracy = accuracy_score(y_test, y_pred)
                
                self.logger.info(f"Pattern classifier trained with accuracy: {accuracy:.3f}")
        
        except Exception as e:
            self.logger.error(f"Error training pattern models: {e}")
    
    def _group_similar_selectors(self, selectors: Dict[str, float]) -> List[List[str]]:
        """Group similar selectors together"""
        
        groups = []
        selector_list = list(selectors.keys())
        used = set()
        
        for i, selector1 in enumerate(selector_list):
            if selector1 in used:
                continue
            
            group = [selector1]
            used.add(selector1)
            
            for j, selector2 in enumerate(selector_list[i+1:], i+1):
                if selector2 in used:
                    continue
                
                # Check similarity
                if self._selectors_similar(selector1, selector2):
                    group.append(selector2)
                    used.add(selector2)
            
            groups.append(group)
        
        return groups
    
    def _selectors_similar(self, sel1: str, sel2: str) -> bool:
        """Check if two selectors are similar"""
        
        # Simple similarity based on common elements
        sel1_parts = set(sel1.replace('.', ' ').replace('#', ' ').replace('>', ' ').split())
        sel2_parts = set(sel2.replace('.', ' ').replace('#', ' ').replace('>', ' ').split())
        
        intersection = len(sel1_parts & sel2_parts)
        union = len(sel1_parts | sel2_parts)
        
        similarity = intersection / union if union > 0 else 0
        return similarity > 0.3  # 30% similarity threshold
    
    async def recommend_extraction_strategy(self, url: str, 
                                          content_features: ContentFeatures) -> Dict[str, Any]:
        """Recommend optimal extraction strategy based on learned patterns"""
        
        try:
            recommendations = {
                'recommended_patterns': [],
                'suggested_selectors': [],
                'confidence': 0.0,
                'extraction_approach': 'default',
                'expected_performance': {}
            }
            
            # Find applicable patterns
            applicable_patterns = await self._find_applicable_patterns(url, content_features)
            
            if applicable_patterns:
                # Sort by confidence and success rate
                applicable_patterns.sort(
                    key=lambda p: (p.confidence * p.success_rate), 
                    reverse=True
                )
                
                # Take top patterns
                top_patterns = applicable_patterns[:3]
                recommendations['recommended_patterns'] = [p.pattern_id for p in top_patterns]
                
                # Aggregate selector recommendations
                selector_scores = defaultdict(float)
                for pattern in top_patterns:
                    for selector in pattern.selectors:
                        weight = pattern.confidence * pattern.success_rate
                        selector_scores[selector] += weight
                
                # Sort selectors by score
                sorted_selectors = sorted(selector_scores.items(), key=lambda x: x[1], reverse=True)
                recommendations['suggested_selectors'] = [sel for sel, score in sorted_selectors[:10]]
                
                # Overall confidence
                recommendations['confidence'] = sum(p.confidence for p in top_patterns) / len(top_patterns)
                
                # Determine extraction approach
                pattern_types = [p.pattern_type for p in top_patterns]
                if 'structural' in pattern_types and len([p for p in top_patterns if p.pattern_type == 'structural']) >= 2:
                    recommendations['extraction_approach'] = 'structural_focused'
                elif 'semantic' in pattern_types:
                    recommendations['extraction_approach'] = 'semantic_guided'
                elif 'behavioral' in pattern_types:
                    recommendations['extraction_approach'] = 'adaptive'
                else:
                    recommendations['extraction_approach'] = 'hybrid'
                
                # Expected performance
                avg_quality = sum(p.avg_data_quality for p in top_patterns) / len(top_patterns)
                avg_time = sum(p.avg_extraction_time for p in top_patterns) / len(top_patterns)
                avg_error_rate = sum(p.error_rate for p in top_patterns) / len(top_patterns)
                
                recommendations['expected_performance'] = {
                    'data_quality': avg_quality,
                    'extraction_time': avg_time,
                    'error_rate': avg_error_rate,
                    'success_probability': 1 - avg_error_rate
                }
            
            # Use ML model if available and trained
            if ML_AVAILABLE and self.pattern_classifier:
                ml_recommendation = await self._get_ml_recommendation(content_features)
                if ml_recommendation:
                    recommendations['ml_recommendation'] = ml_recommendation
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error recommending extraction strategy: {e}")
            return {'error': str(e)}
    
    async def _find_applicable_patterns(self, url: str, 
                                      content_features: ContentFeatures) -> List[ExtractionPattern]:
        """Find patterns applicable to the given URL and content"""
        
        applicable = []
        
        try:
            # Extract domain
            domain = ""
            try:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
            except Exception:
                pass
            
            for pattern in self.patterns.values():
                is_applicable = False
                
                # Check domain match
                if domain and domain in pattern.applicable_domains:
                    is_applicable = True
                
                # Check content type match
                if content_features.content_type in pattern.content_types:
                    is_applicable = True
                
                # Check business category match
                if content_features.business_category in pattern.business_categories:
                    is_applicable = True
                
                # Check keyword overlap for semantic patterns
                if pattern.pattern_type == 'semantic':
                    pattern_keywords = set(pattern.attributes.get('keywords', []))
                    content_keywords = set(content_features.keywords)
                    keyword_overlap = len(pattern_keywords & content_keywords)
                    
                    if keyword_overlap >= 2:  # At least 2 keyword matches
                        is_applicable = True
                
                # Filter by minimum confidence
                if is_applicable and pattern.confidence >= self.min_pattern_confidence:
                    applicable.append(pattern)
        
        except Exception as e:
            self.logger.error(f"Error finding applicable patterns: {e}")
        
        return applicable
    
    async def _get_ml_recommendation(self, content_features: ContentFeatures) -> Optional[Dict[str, Any]]:
        """Get ML-based extraction recommendation"""
        
        try:
            if not self.pattern_classifier or not self.scaler:
                return None
            
            # Prepare feature vector
            feature_vector = [
                0,  # duration (unknown for recommendation)
                0,  # records_extracted (unknown)
                0,  # errors_encountered (unknown)
                content_features.quality_score,
                len(content_features.recommended_selectors),
                0,  # failed_selectors (unknown)
                len(content_features.keywords),
                content_features.word_count,
                content_features.quality_score,
                content_features.extraction_confidence
            ]
            
            # Scale features
            feature_vector_scaled = self.scaler.transform([feature_vector])
            
            # Predict
            prediction = self.pattern_classifier.predict(feature_vector_scaled)[0]
            probability = self.pattern_classifier.predict_proba(feature_vector_scaled)[0]
            
            return {
                'prediction': prediction,
                'confidence': float(max(probability)),
                'recommendation': 'Use high-confidence selectors' if prediction == 'successful' else 'Apply cautious extraction with validation'
            }
        
        except Exception as e:
            self.logger.debug(f"Error getting ML recommendation: {e}")
            return None
    
    async def optimize_selectors(self, selectors: List[str], 
                               url: str, 
                               content_features: ContentFeatures) -> List[Tuple[str, float]]:
        """Optimize selector list based on learned patterns"""
        
        try:
            optimized = []
            
            # Find patterns that might help optimize these selectors
            applicable_patterns = await self._find_applicable_patterns(url, content_features)
            
            # Score each selector
            for selector in selectors:
                score = 0.0
                
                # Base score from content features
                if selector in content_features.recommended_selectors:
                    score += 0.3
                
                # Pattern-based scoring
                pattern_matches = 0
                pattern_score_sum = 0.0
                
                for pattern in applicable_patterns:
                    if selector in pattern.selectors:
                        pattern_matches += 1
                        pattern_score_sum += pattern.success_rate * pattern.confidence
                
                if pattern_matches > 0:
                    score += pattern_score_sum / pattern_matches
                
                # Penalize overly complex selectors
                complexity_penalty = len(selector.split()) / 10  # Penalty for complex selectors
                score = max(0, score - complexity_penalty)
                
                optimized.append((selector, score))
            
            # Sort by score
            optimized.sort(key=lambda x: x[1], reverse=True)
            
            return optimized
            
        except Exception as e:
            self.logger.error(f"Error optimizing selectors: {e}")
            return [(sel, 0.5) for sel in selectors]  # Return with neutral scores
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get statistics about learned patterns"""
        
        try:
            stats = {
                'total_patterns': len(self.patterns),
                'pattern_types': Counter(p.pattern_type for p in self.patterns.values()),
                'avg_confidence': sum(p.confidence for p in self.patterns.values()) / len(self.patterns) if self.patterns else 0,
                'avg_success_rate': sum(p.success_rate for p in self.patterns.values()) / len(self.patterns) if self.patterns else 0,
                'total_usage': sum(p.usage_count for p in self.patterns.values()),
                'learning_sessions': len(self.learning_sessions),
                'domains_covered': len(set().union(*(p.applicable_domains for p in self.patterns.values()))),
                'content_types_covered': len(set().union(*(p.content_types for p in self.patterns.values()))),
                'business_categories_covered': len(set().union(*(p.business_categories for p in self.patterns.values())))
            }
            
            # Pattern performance distribution
            high_perf_patterns = sum(1 for p in self.patterns.values() if p.success_rate > 0.8)
            medium_perf_patterns = sum(1 for p in self.patterns.values() if 0.5 <= p.success_rate <= 0.8)
            low_perf_patterns = sum(1 for p in self.patterns.values() if p.success_rate < 0.5)
            
            stats['performance_distribution'] = {
                'high_performance': high_perf_patterns,
                'medium_performance': medium_perf_patterns,
                'low_performance': low_perf_patterns
            }
            
            # Recent learning activity
            recent_sessions = [s for s in self.learning_sessions 
                             if s.start_time > datetime.utcnow() - timedelta(days=7)]
            stats['recent_activity'] = {
                'sessions_last_week': len(recent_sessions),
                'avg_daily_sessions': len(recent_sessions) / 7,
                'total_records_extracted': sum(s.records_extracted for s in recent_sessions),
                'avg_session_quality': sum(s.data_quality_score for s in recent_sessions) / len(recent_sessions) if recent_sessions else 0
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting pattern statistics: {e}")
            return {'error': str(e)}
    
    async def adaptive_learning_cycle(self):
        """Run adaptive learning cycle to improve patterns"""
        
        try:
            self.logger.info("Starting adaptive learning cycle...")
            
            # Prune low-performing patterns
            removed_count = 0
            for pattern_id in list(self.patterns.keys()):
                pattern = self.patterns[pattern_id]
                
                # Remove patterns with low success rate and low usage
                if (pattern.success_rate < 0.3 and 
                    pattern.usage_count < 3 and
                    datetime.utcnow() - pattern.discovered_at > timedelta(days=30)):
                    
                    del self.patterns[pattern_id]
                    removed_count += 1
            
            # Consolidate similar patterns
            consolidated_count = await self._consolidate_similar_patterns()
            
            # Retrain models if enough new data
            if len(self.learning_sessions) % 50 == 0:  # Every 50 sessions
                await self._train_pattern_models()
            
            self.logger.info(f"Adaptive learning cycle complete: removed {removed_count} patterns, consolidated {consolidated_count}")
            
            # Save updated patterns
            self._save_patterns()
            
        except Exception as e:
            self.logger.error(f"Error in adaptive learning cycle: {e}")
    
    async def _consolidate_similar_patterns(self) -> int:
        """Consolidate similar patterns to avoid redundancy"""
        
        consolidated_count = 0
        
        try:
            if not ML_AVAILABLE:
                return 0
            
            # Group patterns by type
            pattern_groups = defaultdict(list)
            for pattern in self.patterns.values():
                pattern_groups[pattern.pattern_type].append(pattern)
            
            for pattern_type, patterns in pattern_groups.items():
                if len(patterns) < 2:
                    continue
                
                # Create feature vectors for patterns
                features = []
                pattern_objects = []
                
                for pattern in patterns:
                    # Feature vector based on pattern characteristics
                    feature_vector = [
                        pattern.confidence,
                        pattern.success_rate,
                        pattern.usage_count / 100,  # Normalize
                        len(pattern.selectors),
                        len(pattern.applicable_domains),
                        len(pattern.content_types),
                        pattern.avg_data_quality,
                        pattern.error_rate
                    ]
                    
                    features.append(feature_vector)
                    pattern_objects.append(pattern)
                
                if len(features) >= 2:
                    # Cluster similar patterns
                    features_array = np.array(features)
                    
                    # Use DBSCAN for clustering
                    clustering = DBSCAN(eps=0.3, min_samples=2)
                    cluster_labels = clustering.fit_predict(features_array)
                    
                    # Consolidate patterns in the same cluster
                    clusters = defaultdict(list)
                    for i, label in enumerate(cluster_labels):
                        if label != -1:  # Not noise
                            clusters[label].append(pattern_objects[i])
                    
                    for cluster_patterns in clusters.values():
                        if len(cluster_patterns) > 1:
                            # Merge patterns in this cluster
                            await self._merge_patterns(cluster_patterns)
                            consolidated_count += len(cluster_patterns) - 1
        
        except Exception as e:
            self.logger.error(f"Error consolidating patterns: {e}")
        
        return consolidated_count
    
    async def _merge_patterns(self, patterns: List[ExtractionPattern]):
        """Merge similar patterns into one"""
        
        try:
            if len(patterns) < 2:
                return
            
            # Choose the best pattern as the base
            best_pattern = max(patterns, key=lambda p: p.confidence * p.success_rate * p.usage_count)
            
            # Merge attributes from other patterns
            for pattern in patterns:
                if pattern.pattern_id == best_pattern.pattern_id:
                    continue
                
                # Merge selectors
                for selector in pattern.selectors:
                    if selector not in best_pattern.selectors:
                        best_pattern.selectors.append(selector)
                
                # Merge domains, content types, business categories
                best_pattern.applicable_domains.update(pattern.applicable_domains)
                best_pattern.content_types.update(pattern.content_types)
                best_pattern.business_categories.update(pattern.business_categories)
                
                # Update aggregated metrics
                total_usage = best_pattern.usage_count + pattern.usage_count
                
                # Weighted averages
                best_pattern.success_rate = (
                    (best_pattern.success_rate * best_pattern.usage_count + 
                     pattern.success_rate * pattern.usage_count) / total_usage
                )
                
                best_pattern.avg_data_quality = (
                    (best_pattern.avg_data_quality * best_pattern.usage_count + 
                     pattern.avg_data_quality * pattern.usage_count) / total_usage
                )
                
                best_pattern.usage_count = total_usage
                best_pattern.adaptation_count += pattern.adaptation_count
                
                # Remove the merged pattern
                if pattern.pattern_id in self.patterns:
                    del self.patterns[pattern.pattern_id]
        
        except Exception as e:
            self.logger.error(f"Error merging patterns: {e}")


# Global instance
pattern_recognizer = IntelligentPatternRecognizer()
