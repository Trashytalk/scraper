"""
Crawl Orchestrator and Enhanced Link Classifier

High-level orchestrator for crawling operations and enhanced classification
with business intelligence patterns.
"""

import asyncio
import logging
from typing import Dict, List, Tuple, Optional
import re
from datetime import datetime

from .advanced_crawler import AdvancedCrawlManager, DiscoveredPage
from ..discovery.classifier import AdaptiveLinkClassifier, LinkCategory

logger = logging.getLogger(__name__)


class CrawlOrchestrator:
    """High-level orchestrator for crawling operations"""
    
    def __init__(self, crawl_manager: AdvancedCrawlManager):
        self.crawl_manager = crawl_manager
        
    async def run_intelligence_gathering(self, operation_name: str = "business_intel") -> Dict:
        """Run a complete intelligence gathering operation"""
        logger.info(f"Starting intelligence gathering operation: {operation_name}")
        
        discovered_pages = []
        start_time = datetime.utcnow()
        
        try:
            async for page in self.crawl_manager.start_discovery_operation(operation_name):
                discovered_pages.append(page)
                
                # Log progress every 100 pages
                if len(discovered_pages) % 100 == 0:
                    metrics = await self.crawl_manager.get_discovery_metrics()
                    logger.info(f"Discovery progress: {len(discovered_pages)} pages - {metrics}")
                
                # Safety limit to prevent runaway crawling
                if len(discovered_pages) >= 10000:
                    logger.warning("Reached maximum pages limit (10,000), stopping operation")
                    break
        
        except Exception as e:
            logger.error(f"Intelligence gathering operation failed: {e}")
        
        # Final report
        final_metrics = await self.crawl_manager.get_discovery_metrics()
        operation_duration = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"Discovery operation completed in {operation_duration:.2f}s: {final_metrics}")
        
        return {
            'operation_name': operation_name,
            'discovered_pages': len(discovered_pages),
            'duration_seconds': operation_duration,
            'metrics': final_metrics,
            'high_value_pages': [p for p in discovered_pages if p.classification_score > 0.8],
            'summary': self._generate_operation_summary(discovered_pages, final_metrics)
        }
    
    def _generate_operation_summary(self, pages: List[DiscoveredPage], metrics: Dict) -> Dict:
        """Generate comprehensive operation summary"""
        if not pages:
            return {'status': 'no_pages_discovered'}
        
        # Analyze page types
        source_types = {}
        classification_types = {}
        depth_distribution = {}
        
        for page in pages:
            source_types[page.source_type] = source_types.get(page.source_type, 0) + 1
            classification_types[page.classification_type] = classification_types.get(page.classification_type, 0) + 1
            depth_distribution[page.depth] = depth_distribution.get(page.depth, 0) + 1
        
        # Calculate quality metrics
        avg_score = sum(p.classification_score for p in pages) / len(pages)
        success_rate = len([p for p in pages if p.crawl_status == 'crawled']) / len(pages)
        
        return {
            'total_pages': len(pages),
            'average_quality_score': round(avg_score, 3),
            'success_rate': round(success_rate, 3),
            'source_type_distribution': source_types,
            'classification_distribution': classification_types,
            'depth_distribution': depth_distribution,
            'crawl_rate_pages_per_minute': round(metrics.get('crawl_rate_per_minute', 0), 2),
            'top_domains': self._extract_top_domains(pages),
            'quality_breakdown': {
                'high_quality': len([p for p in pages if p.classification_score > 0.8]),
                'medium_quality': len([p for p in pages if 0.5 < p.classification_score <= 0.8]),
                'low_quality': len([p for p in pages if p.classification_score <= 0.5])
            }
        }
    
    def _extract_top_domains(self, pages: List[DiscoveredPage], limit: int = 10) -> List[Dict]:
        """Extract top domains by page count"""
        from urllib.parse import urlparse
        from collections import Counter
        
        domain_counts = Counter()
        domain_scores = {}
        
        for page in pages:
            domain = urlparse(page.url).netloc
            domain_counts[domain] += 1
            
            if domain not in domain_scores:
                domain_scores[domain] = []
            domain_scores[domain].append(page.classification_score)
        
        top_domains = []
        for domain, count in domain_counts.most_common(limit):
            avg_score = sum(domain_scores[domain]) / len(domain_scores[domain])
            top_domains.append({
                'domain': domain,
                'page_count': count,
                'average_score': round(avg_score, 3)
            })
        
        return top_domains


class EnhancedAdaptiveLinkClassifier(AdaptiveLinkClassifier):
    """Extended version with additional business intelligence patterns"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.business_patterns = self._compile_business_patterns()
        logger.info("Enhanced AdaptiveLinkClassifier initialized with business patterns")
    
    def _compile_business_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile comprehensive business intelligence patterns"""
        patterns = {
            'high_value_patterns': [
                re.compile(r'company[-_]profile', re.IGNORECASE),
                re.compile(r'business[-_]profile', re.IGNORECASE),
                re.compile(r'executive[-_]team', re.IGNORECASE),
                re.compile(r'management[-_]team', re.IGNORECASE),
                re.compile(r'financial[-_]statements', re.IGNORECASE),
                re.compile(r'annual[-_]report', re.IGNORECASE),
                re.compile(r'sec[-_]filing', re.IGNORECASE),
                re.compile(r'investor[-_]relations', re.IGNORECASE),
                re.compile(r'about[-_]company', re.IGNORECASE),
                re.compile(r'corporate[-_]info', re.IGNORECASE)
            ],
            'medium_value_patterns': [
                re.compile(r'contact[-_]us', re.IGNORECASE),
                re.compile(r'company[-_]info', re.IGNORECASE),
                re.compile(r'business[-_]directory', re.IGNORECASE),
                re.compile(r'company[-_]listing', re.IGNORECASE),
                re.compile(r'organization[-_]chart', re.IGNORECASE),
                re.compile(r'leadership', re.IGNORECASE),
                re.compile(r'executives', re.IGNORECASE),
                re.compile(r'board[-_]directors', re.IGNORECASE),
                re.compile(r'press[-_]release', re.IGNORECASE),
                re.compile(r'news[-_]room', re.IGNORECASE)
            ],
            'navigation_patterns': [
                re.compile(r'next[-_]page', re.IGNORECASE),
                re.compile(r'more[-_]results', re.IGNORECASE),
                re.compile(r'view[-_]all', re.IGNORECASE),
                re.compile(r'see[-_]more', re.IGNORECASE),
                re.compile(r'continue', re.IGNORECASE),
                re.compile(r'page[-_]\d+', re.IGNORECASE),
                re.compile(r'>>', re.IGNORECASE),
                re.compile(r'next', re.IGNORECASE)
            ],
            'exclude_patterns': [
                re.compile(r'login', re.IGNORECASE),
                re.compile(r'signup', re.IGNORECASE),
                re.compile(r'register', re.IGNORECASE),
                re.compile(r'privacy[-_]policy', re.IGNORECASE),
                re.compile(r'terms[-_]of[-_]service', re.IGNORECASE),
                re.compile(r'cookie[-_]policy', re.IGNORECASE),
                re.compile(r'careers', re.IGNORECASE),
                re.compile(r'jobs', re.IGNORECASE),
                re.compile(r'cart', re.IGNORECASE),
                re.compile(r'checkout', re.IGNORECASE)
            ],
            'financial_patterns': [
                re.compile(r'financial[-_]data', re.IGNORECASE),
                re.compile(r'stock[-_]price', re.IGNORECASE),
                re.compile(r'market[-_]cap', re.IGNORECASE),
                re.compile(r'earnings', re.IGNORECASE),
                re.compile(r'revenue', re.IGNORECASE),
                re.compile(r'quarterly[-_]report', re.IGNORECASE),
                re.compile(r'balance[-_]sheet', re.IGNORECASE)
            ],
            'industry_patterns': [
                re.compile(r'industry[-_]analysis', re.IGNORECASE),
                re.compile(r'market[-_]research', re.IGNORECASE),
                re.compile(r'competitor[-_]analysis', re.IGNORECASE),
                re.compile(r'sector[-_]overview', re.IGNORECASE)
            ]
        }
        return patterns
    
    def enhanced_rule_based_classification(self, url: str, anchor_text: str, context: str) -> Tuple[float, str]:
        """Enhanced rule-based classification with more sophisticated scoring"""
        score = 0.0
        classification = 'unknown'
        
        # Combine all text for pattern matching
        all_text = f"{url} {anchor_text} {context}".lower()
        
        # Check high-value patterns (business profiles, financial data, etc.)
        high_value_matches = sum(1 for pattern in self.business_patterns['high_value_patterns'] 
                               if pattern.search(all_text))
        if high_value_matches > 0:
            score += 0.8 * min(high_value_matches, 3) / 3  # Cap at 3 matches
            classification = 'high_value_business'
        
        # Check financial patterns
        financial_matches = sum(1 for pattern in self.business_patterns['financial_patterns']
                              if pattern.search(all_text))
        if financial_matches > 0:
            score += 0.7 * min(financial_matches, 2) / 2
            classification = 'financial_data'
        
        # Check medium-value patterns
        medium_value_matches = sum(1 for pattern in self.business_patterns['medium_value_patterns']
                                 if pattern.search(all_text))
        if medium_value_matches > 0:
            score += 0.5 * min(medium_value_matches, 3) / 3
            if classification == 'unknown':
                classification = 'medium_value_business'
        
        # Check industry patterns
        industry_matches = sum(1 for pattern in self.business_patterns['industry_patterns']
                             if pattern.search(all_text))
        if industry_matches > 0:
            score += 0.6 * min(industry_matches, 2) / 2
            if classification == 'unknown':
                classification = 'industry_info'
        
        # Check navigation patterns
        navigation_matches = sum(1 for pattern in self.business_patterns['navigation_patterns']
                               if pattern.search(anchor_text))
        if navigation_matches > 0:
            score += 0.4 * min(navigation_matches, 2) / 2
            if classification == 'unknown':
                classification = 'navigation'
        
        # Check exclude patterns (negative scoring)
        exclude_matches = sum(1 for pattern in self.business_patterns['exclude_patterns']
                            if pattern.search(all_text))
        if exclude_matches > 0:
            score -= 0.8 * min(exclude_matches, 2) / 2
            classification = 'exclude'
        
        # Context-based scoring enhancements
        business_keywords = [
            'company', 'business', 'corporate', 'organization', 'enterprise',
            'corporation', 'inc', 'ltd', 'llc', 'group', 'industries',
            'solutions', 'services', 'technology', 'systems'
        ]
        
        context_score = sum(0.05 for keyword in business_keywords 
                          if keyword in context.lower())
        score += min(context_score, 0.2)  # Cap context contribution at 0.2
        
        # URL structure scoring
        url_parts = url.lower().split('/')
        business_url_indicators = ['company', 'business', 'corp', 'about', 'profile']
        url_score = sum(0.1 for indicator in business_url_indicators
                       if any(indicator in part for part in url_parts))
        score += min(url_score, 0.3)  # Cap URL contribution at 0.3
        
        # Normalize score to 0-1 range
        final_score = max(0.0, min(1.0, score))
        
        return final_score, classification
    
    def classify_link(self, url: str, anchor_text: str, parent_url: str = "", context: str = ""):
        """Override parent method to use enhanced classification"""
        # Get base classification from parent class
        base_result = super().classify_link(url, anchor_text, parent_url, context)
        
        # Apply enhanced classification
        enhanced_score, enhanced_type = self.enhanced_rule_based_classification(
            url, anchor_text, context
        )
        
        # Use the higher confidence result
        if enhanced_score > base_result.confidence:
            base_result.confidence = enhanced_score
            # Map enhanced types to existing categories
            if enhanced_type == 'high_value_business':
                base_result.category = LinkCategory.BUSINESS_PROFILE
            elif enhanced_type == 'financial_data':
                base_result.category = LinkCategory.FINANCIAL_DATA
            elif enhanced_type == 'medium_value_business':
                base_result.category = LinkCategory.CONTACT_INFO
            elif enhanced_type == 'industry_info':
                base_result.category = LinkCategory.COMPANY_NEWS
            elif enhanced_type == 'navigation':
                base_result.category = LinkCategory.UNKNOWN
            elif enhanced_type == 'exclude':
                base_result.category = LinkCategory.IRRELEVANT
        
        # Recalculate priority based on new confidence and category
        base_result.priority = self._assign_priority(base_result.category, base_result.confidence)
        
        return base_result
    
    def get_pattern_stats(self) -> Dict:
        """Get statistics about pattern matching capabilities"""
        return {
            'pattern_categories': len(self.business_patterns),
            'total_patterns': sum(len(patterns) for patterns in self.business_patterns.values()),
            'pattern_breakdown': {
                category: len(patterns) for category, patterns in self.business_patterns.items()
            },
            'enhanced_features': [
                'Business intelligence focused patterns',
                'Financial data detection',
                'Industry analysis recognition',
                'Navigation pattern identification',
                'Exclusion pattern filtering',
                'Context-aware scoring',
                'URL structure analysis'
            ]
        }
