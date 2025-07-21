"""
Multi-Language NLP Integration Module

Main interface for multi-language business intelligence processing.
Integrates language detection, tokenization, NER, transliteration, 
translation, and normalization capabilities.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

from .core import (
    LanguageInfo, ScriptType, DetectedText, MultiLanguageDetector,
    language_detector
)
from .tokenization import (
    TokenizationResult, MultiLanguageTokenizer, multilang_tokenizer
)
from .ner import (
    EntityResult, EntityType, MultiLanguageNER, multilang_ner
)
from .transliteration import (
    TransliterationResult, TranslationResult, ScriptTransliterator,
    MultiLanguageTranslator, EntityNormalizer,
    script_transliterator, multilang_translator, entity_normalizer
)
from .normalization import (
    NormalizedField, AddressComponents, phone_normalizer,
    address_normalizer, company_id_normalizer, financial_normalizer,
    date_normalizer
)

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Complete multi-language processing result"""
    original_text: str
    detected_language: DetectedText
    tokenization: Optional[TokenizationResult] = None
    entities: List[EntityResult] = field(default_factory=list)
    transliteration: Optional[TransliterationResult] = None
    translation: Optional[TranslationResult] = None
    normalized_entities: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BusinessEntity:
    """Structured business entity with multi-language support"""
    entity_id: str
    entity_type: str
    original_forms: Dict[str, str]  # language -> original text
    normalized_forms: Dict[str, str]  # normalization_type -> normalized text
    transliterations: Dict[str, str]  # script -> transliterated text
    translations: Dict[str, str]  # language -> translated text
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class MultiLanguageProcessor:
    """Main multi-language processing pipeline"""
    
    def __init__(self):
        self.detector = language_detector
        self.tokenizer = multilang_tokenizer
        self.ner = multilang_ner
        self.transliterator = script_transliterator
        self.translator = multilang_translator
        self.entity_normalizer = entity_normalizer
        
        # Field normalizers
        self.phone_normalizer = phone_normalizer
        self.address_normalizer = address_normalizer
        self.company_id_normalizer = company_id_normalizer
        self.financial_normalizer = financial_normalizer
        self.date_normalizer = date_normalizer
    
    def process_text(self, text: str, target_language: str = 'en', 
                    include_transliteration: bool = True,
                    include_translation: bool = True,
                    include_normalization: bool = True) -> ProcessingResult:
        """Complete multi-language text processing"""
        
        if not text:
            return ProcessingResult('', DetectedText('', self.detector.language_data['en'], ScriptType.UNKNOWN, 0.0))
        
        # Step 1: Language and script detection
        detected_language = self.detector.create_detected_text(text)
        logger.debug(f"Detected language: {detected_language.language.name} ({detected_language.confidence:.2f})")
        
        result = ProcessingResult(text, detected_language)
        
        # Step 2: Tokenization
        try:
            tokenization = self.tokenizer.tokenize(text, detected_language.language)
            result.tokenization = tokenization
            logger.debug(f"Tokenized into {len(tokenization.tokens)} tokens")
        except Exception as e:
            logger.error(f"Tokenization failed: {e}")
            result.metadata['tokenization_error'] = str(e)
        
        # Step 3: Named Entity Recognition
        try:
            entities = self.ner.extract_entities(text, detected_language.language)
            result.entities = entities
            logger.debug(f"Extracted {len(entities)} entities")
        except Exception as e:
            logger.error(f"NER failed: {e}")
            result.metadata['ner_error'] = str(e)
        
        # Step 4: Transliteration (if not Latin script)
        if include_transliteration and detected_language.script != ScriptType.LATIN:
            try:
                transliteration = self.transliterator.transliterate(text, detected_language.script)
                result.transliteration = transliteration
                logger.debug(f"Transliterated using method: {transliteration.method}")
            except Exception as e:
                logger.error(f"Transliteration failed: {e}")
                result.metadata['transliteration_error'] = str(e)
        
        # Step 5: Translation (if not target language)
        if include_translation and detected_language.language.code != target_language:
            try:
                translation = self.translator.translate(
                    text, detected_language.language.code, target_language
                )
                result.translation = translation
                logger.debug(f"Translated using method: {translation.method}")
            except Exception as e:
                logger.error(f"Translation failed: {e}")
                result.metadata['translation_error'] = str(e)
        
        # Step 6: Entity normalization
        if include_normalization and result.entities:
            try:
                result.normalized_entities = self._normalize_entities(
                    result.entities, detected_language.language
                )
                logger.debug(f"Normalized {len(result.normalized_entities)} entity types")
            except Exception as e:
                logger.error(f"Entity normalization failed: {e}")
                result.metadata['normalization_error'] = str(e)
        
        return result
    
    def _normalize_entities(self, entities: List[EntityResult], 
                          language: LanguageInfo) -> Dict[str, List[NormalizedField]]:
        """Normalize extracted entities"""
        normalized = {}
        
        for entity in entities:
            entity_text = entity.text
            entity_type = entity.entity_type.value if hasattr(entity.entity_type, 'value') else str(entity.entity_type)
            
            if entity_type not in normalized:
                normalized[entity_type] = []
            
            try:
                # Route to appropriate normalizer
                if entity_type in ['phone', 'telephone', 'mobile']:
                    norm_field = self.phone_normalizer.normalize_phone(entity_text)
                
                elif entity_type in ['address', 'location']:
                    norm_field = self.address_normalizer.normalize_address(entity_text, language)
                
                elif entity_type in ['company_id', 'registration_number', 'tax_id']:
                    norm_field = self.company_id_normalizer.normalize_company_id(entity_text)
                
                elif entity_type in ['money', 'amount', 'financial']:
                    norm_field = self.financial_normalizer.normalize_amount(entity_text)
                
                elif entity_type in ['date', 'time']:
                    norm_field = self.date_normalizer.normalize_date(entity_text, language)
                
                else:
                    # Generic normalization (no specific handler)
                    norm_field = NormalizedField(
                        entity_text, entity_text.strip(), entity_type, 
                        entity.confidence, language
                    )
                
                normalized[entity_type].append(norm_field)
                
            except Exception as e:
                logger.error(f"Failed to normalize {entity_type} entity '{entity_text}': {e}")
        
        return normalized
    
    def create_business_entity(self, entity_text: str, entity_type: str,
                             language: LanguageInfo, entity_id: Optional[str] = None) -> BusinessEntity:
        """Create a structured business entity with multi-language processing"""
        
        if not entity_id:
            entity_id = f"{entity_type}_{hash(entity_text)}_{language.code}"
        
        original_forms = {language.code: entity_text}
        normalized_forms = {}
        transliterations = {}
        translations = {}
        
        # Process with entity normalizer for cross-language matching
        if entity_type in ['company', 'organization']:
            normalized_dict = self.entity_normalizer.normalize_company_name(entity_text, language)
        elif entity_type in ['person', 'name']:
            normalized_dict = self.entity_normalizer.normalize_person_name(entity_text, language)
        else:
            normalized_dict = {'original': entity_text, 'cleaned': entity_text.strip().lower()}
        
        normalized_forms.update(normalized_dict)
        
        # Add transliterations if available
        if 'transliterated' in normalized_dict:
            transliterations[ScriptType.LATIN.value] = normalized_dict['transliterated']
        
        # Add translations if available
        if 'translated' in normalized_dict:
            translations['en'] = normalized_dict['translated']
        
        # Calculate overall confidence
        confidence = 0.8  # Base confidence for structured entities
        
        return BusinessEntity(
            entity_id=entity_id,
            entity_type=entity_type,
            original_forms=original_forms,
            normalized_forms=normalized_forms,
            transliterations=transliterations,
            translations=translations,
            confidence=confidence,
            metadata={
                'language': language.code,
                'script': language.script.value,
                'processing_timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def batch_process(self, texts: List[str], **kwargs) -> List[ProcessingResult]:
        """Process multiple texts in batch"""
        results = []
        
        for text in texts:
            try:
                result = self.process_text(text, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch processing failed for text: {text[:100]}... Error: {e}")
                # Create minimal result for failed processing
                detected = DetectedText(text, self.detector.language_data['en'], ScriptType.UNKNOWN, 0.0)
                failed_result = ProcessingResult(text, detected)
                failed_result.metadata['processing_error'] = str(e)
                results.append(failed_result)
        
        return results
    
    async def async_process_text(self, text: str, **kwargs) -> ProcessingResult:
        """Asynchronous text processing"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process_text, text, **kwargs)
    
    async def async_batch_process(self, texts: List[str], **kwargs) -> List[ProcessingResult]:
        """Asynchronous batch processing"""
        tasks = [self.async_process_text(text, **kwargs) for text in texts]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def extract_business_intelligence(self, text: str) -> Dict[str, Any]:
        """Extract structured business intelligence from text"""
        
        # Process the text
        result = self.process_text(text, include_normalization=True)
        
        intelligence = {
            'language_info': {
                'detected_language': result.detected_language.language.name,
                'language_code': result.detected_language.language.code,
                'script': result.detected_language.script.value,
                'confidence': result.detected_language.confidence
            },
            'entities': {},
            'structured_data': {},
            'cross_language_matching': {}
        }
        
        # Organize entities by type
        for entity in result.entities:
            entity_type = entity.entity_type.value if hasattr(entity.entity_type, 'value') else str(entity.entity_type)
            
            if entity_type not in intelligence['entities']:
                intelligence['entities'][entity_type] = []
            
            intelligence['entities'][entity_type].append({
                'text': entity.text,
                'confidence': entity.confidence,
                'span': entity.span,
                'metadata': entity.metadata
            })
        
        # Add normalized data
        if result.normalized_entities:
            for entity_type, normalized_list in result.normalized_entities.items():
                intelligence['structured_data'][entity_type] = []
                for norm_field in normalized_list:
                    intelligence['structured_data'][entity_type].append({
                        'original': norm_field.original,
                        'normalized': norm_field.normalized,
                        'confidence': norm_field.confidence,
                        'metadata': norm_field.metadata
                    })
        
        # Add cross-language data if available
        if result.transliteration:
            intelligence['cross_language_matching']['transliterated'] = result.transliteration.transliterated
        
        if result.translation:
            intelligence['cross_language_matching']['translated'] = result.translation.translated
            intelligence['cross_language_matching']['translation_language'] = result.translation.language_to.code
        
        return intelligence
    
    def get_supported_languages(self) -> Dict[str, LanguageInfo]:
        """Get all supported languages"""
        return self.detector.language_data
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get processor capabilities"""
        return {
            'languages': list(self.detector.language_data.keys()),
            'scripts': [script.value for script in ScriptType],
            'tokenization_support': self.tokenizer.get_supported_languages(),
            'ner_support': {
                'spacy': self.ner.spacy_extractor.get_supported_languages() if self.ner.spacy_extractor else [],
                'stanza': self.ner.stanza_extractor.get_supported_languages() if self.ner.stanza_extractor else [],
                'transformers': ['multilingual']
            },
            'transliteration_support': {
                'icu_available': bool(self.transliterator.icu_transliterators),
                'supported_scripts': ['cyrillic', 'arabic', 'cjk', 'greek', 'hebrew']
            },
            'translation_support': {
                'google_available': 'google' in self.translator.translators,
                'marian_models': list(self.translator.marian_models.keys())
            },
            'normalization_support': {
                'phone': True,
                'address': True,
                'company_id': True,
                'financial': True,
                'date': True
            }
        }


# Global instance
multilang_processor = MultiLanguageProcessor()
