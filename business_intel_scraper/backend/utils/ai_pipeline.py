"""
AI Integration for Scrapy Pipeline
Integrates AI processing directly into the Scrapy data pipeline
"""

from typing import Dict, Any, List, Optional
from scrapy import Spider
from scrapy.http import Response
from itemadapter import ItemAdapter
import asyncio
import logging

from ..ai import AIProcessor, ProcessedData


class AIEnhancementPipeline:
    """Scrapy pipeline that enhances items with AI processing"""
    
    def __init__(self, settings: Optional[Any] = None) -> None:
        self.ai_processor: Optional[Any] = None
        self.enabled = True
        self.batch_size = 10
        self.batch_items: List[Any] = []
        self.process_entities = True
        self.process_classification = True
        self.process_sentiment = True
        self.process_duplicates = True
        self.logger = logging.getLogger(__name__)
        
        if settings:
            self.enabled = settings.getbool('AI_ENABLED', True)
            self.batch_size = settings.getint('AI_BATCH_SIZE', 10)
            self.process_entities = settings.getbool('AI_PROCESS_ENTITIES', True)
            self.process_classification = settings.getbool('AI_PROCESS_CLASSIFICATION', True)
            self.process_sentiment = settings.getbool('AI_PROCESS_SENTIMENT', True)
            self.process_duplicates = settings.getbool('AI_PROCESS_DUPLICATES', True)
    
    @classmethod
    def from_crawler(cls, crawler: Any) -> 'AIEnhancementPipeline':
        return cls(crawler.settings)
    
    def open_spider(self, spider: Spider) -> None:
        """Initialize AI processor when spider opens"""
        if self.enabled:
            try:
                self.ai_processor = AIProcessor()
                status = self.ai_processor.get_model_status()
                if status['ai_enabled']:
                    self.logger.info("AI enhancement pipeline enabled")
                    self.logger.info(f"Available capabilities: {list(status['capabilities'].keys())}")
                else:
                    self.logger.warning("AI models not available, disabling AI pipeline")
                    self.enabled = False
            except Exception as e:
                self.logger.error(f"Failed to initialize AI processor: {e}")
                self.enabled = False
    
    def close_spider(self, spider: Spider) -> None:
        """Process any remaining batch items when spider closes"""
        if self.enabled and self.batch_items:
            try:
                self._process_batch(spider)
            except Exception as e:
                self.logger.error(f"Error processing final batch: {e}")
    
    def process_item(self, item: Any, spider: Spider) -> Any:
        """Process individual items, batching for efficiency"""
        if not self.enabled or not self.ai_processor:
            return item
        
        # Add item to batch
        self.batch_items.append(item)
        
        # Process batch when it reaches the desired size
        if len(self.batch_items) >= self.batch_size:
            try:
                processed_items = self._process_batch(spider)
                # Return the first item, others will be yielded by spider
                if processed_items:
                    return processed_items[0]
            except Exception as e:
                self.logger.error(f"Error processing AI batch: {e}")
                # Return original item on error
                return self.batch_items.pop(0)
        
        return item
    
    def _process_batch(self, spider: Spider) -> List[Dict[str, Any]]:
        """Process a batch of items with AI enhancement"""
        if not self.batch_items or self.ai_processor is None:
            return []
        
        try:
            # Convert items to dictionaries
            batch_data = []
            for item in self.batch_items:
                adapter = ItemAdapter(item)
                batch_data.append(dict(adapter))
            
            # Process with AI
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                enhanced_data = loop.run_until_complete(
                    self.ai_processor.enhance_scraped_data(batch_data)
                )
            finally:
                loop.close()
            
            # Update original items with AI enhancements
            processed_items = []
            for original_item, enhanced in zip(self.batch_items, enhanced_data):
                enhanced_item = self._merge_ai_data(original_item, enhanced)
                processed_items.append(enhanced_item)
            
            # Clear batch
            self.batch_items.clear()
            
            self.logger.info(f"AI processed batch of {len(processed_items)} items")
            return processed_items
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            # Return original items on error
            items = list(self.batch_items)
            self.batch_items.clear()
            return items
    
    def _merge_ai_data(self, original_item: Any, enhanced_data: ProcessedData) -> Dict[str, Any]:
        """Merge AI enhancement data into original item"""
        adapter = ItemAdapter(original_item)
        enhanced_item = dict(adapter)
        
        # Add AI metadata
        enhanced_item['ai_processed'] = True
        enhanced_item['ai_quality_score'] = enhanced_data.quality_score
        
        # Add entities
        if self.process_entities and enhanced_data.entities:
            enhanced_item['ai_entities'] = [
                {
                    'text': entity.text,
                    'label': entity.label,
                    'confidence': entity.confidence,
                    'start': entity.start,
                    'end': entity.end
                } for entity in enhanced_data.entities
            ]
            
            # Extract specific entity types
            enhanced_item['ai_people'] = [e.text for e in enhanced_data.entities if e.label == 'PERSON']
            enhanced_item['ai_organizations'] = [e.text for e in enhanced_data.entities if e.label == 'ORG']
            enhanced_item['ai_locations'] = [e.text for e in enhanced_data.entities if e.label in ['GPE', 'LOC']]
            enhanced_item['ai_emails'] = [e.text for e in enhanced_data.entities if e.label == 'EMAIL']
            enhanced_item['ai_urls'] = [e.text for e in enhanced_data.entities if e.label == 'URL']
        
        # Add classification
        if self.process_classification and enhanced_data.classification:
            enhanced_item['ai_category'] = enhanced_data.classification.category
            enhanced_item['ai_category_confidence'] = enhanced_data.classification.confidence
        
        # Add sentiment
        if self.process_sentiment and enhanced_data.sentiment:
            enhanced_item['ai_sentiment'] = enhanced_data.sentiment
            # Extract dominant sentiment
            sentiment_dict = enhanced_data.sentiment
            if sentiment_dict:
                dominant_sentiment = max(sentiment_dict, key=lambda k: sentiment_dict[k])
                enhanced_item['ai_sentiment_primary'] = dominant_sentiment
                enhanced_item['ai_sentiment_score'] = sentiment_dict[dominant_sentiment]
        
        # Add summary
        if enhanced_data.summary:
            enhanced_item['ai_summary'] = enhanced_data.summary
        
        # Add duplicate information
        if self.process_duplicates and enhanced_data.duplicates:
            enhanced_item['ai_duplicates'] = enhanced_data.duplicates
            enhanced_item['ai_is_duplicate'] = len(enhanced_data.duplicates) > 0
        
        return enhanced_item


class AIFilterPipeline:
    """Pipeline that filters items based on AI analysis"""
    
    def __init__(self, settings: Optional[Any] = None) -> None:
        self.min_quality_score = 0.5
        self.filter_duplicates = True
        self.required_entities = []
        self.blocked_categories = []
        self.min_sentiment_confidence = 0.0
        self.logger = logging.getLogger(__name__)
        
        if settings:
            self.min_quality_score = settings.getfloat('AI_MIN_QUALITY_SCORE', 0.5)
            self.filter_duplicates = settings.getbool('AI_FILTER_DUPLICATES', True)
            self.required_entities = settings.getlist('AI_REQUIRED_ENTITIES', [])
            self.blocked_categories = settings.getlist('AI_BLOCKED_CATEGORIES', [])
            self.min_sentiment_confidence = settings.getfloat('AI_MIN_SENTIMENT_CONFIDENCE', 0.0)
    
    @classmethod
    def from_crawler(cls, crawler: Any) -> 'AIFilterPipeline':
        return cls(crawler.settings)
    
    def process_item(self, item: Any, spider: Spider) -> Any:
        """Filter items based on AI analysis"""
        adapter = ItemAdapter(item)
        
        # Skip items not processed by AI
        if not adapter.get('ai_processed'):
            return item
        
        # Quality score filter
        quality_score = adapter.get('ai_quality_score', 0.0)
        if quality_score < self.min_quality_score:
            self.logger.info(f"Dropping item with low quality score: {quality_score}")
            raise DropItem(f"Quality score {quality_score} below threshold {self.min_quality_score}")
        
        # Duplicate filter
        if self.filter_duplicates and adapter.get('ai_is_duplicate'):
            self.logger.info("Dropping duplicate item")
            raise DropItem("Item identified as duplicate")
        
        # Required entities filter
        if self.required_entities:
            item_entities = [e['label'] for e in adapter.get('ai_entities', [])]
            missing_entities = set(self.required_entities) - set(item_entities)
            if missing_entities:
                self.logger.info(f"Dropping item missing required entities: {missing_entities}")
                raise DropItem(f"Missing required entities: {missing_entities}")
        
        # Category filter
        category = adapter.get('ai_category')
        if category and category in self.blocked_categories:
            self.logger.info(f"Dropping item in blocked category: {category}")
            raise DropItem(f"Category {category} is blocked")
        
        # Sentiment filter
        sentiment_score = adapter.get('ai_sentiment_score', 1.0)
        if sentiment_score < self.min_sentiment_confidence:
            self.logger.info(f"Dropping item with low sentiment confidence: {sentiment_score}")
            raise DropItem(f"Sentiment confidence {sentiment_score} below threshold")
        
        return item


# Custom exception for dropping items
class DropItem(Exception):
    """Exception to signal that an item should be dropped"""
    pass
