"""
Multi-Language Transliteration and Translation Module

Provides transliteration, translation, and normalization capabilities
for cross-language entity matching and search.
"""

from __future__ import annotations

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
import json

from .core import LanguageInfo, ScriptType, DetectedText, language_detector

# Transliteration libraries
try:
    from unidecode import unidecode
    HAS_UNIDECODE = True
except ImportError:
    HAS_UNIDECODE = False

try:
    import transliterate
    HAS_TRANSLITERATE = True
except ImportError:
    HAS_TRANSLITERATE = False

try:
    from icu import Transliterator
    HAS_ICU = True
except ImportError:
    HAS_ICU = False

# Translation libraries
try:
    from deep_translator import GoogleTranslator, BingTranslator
    HAS_DEEP_TRANSLATOR = True
except ImportError:
    HAS_DEEP_TRANSLATOR = False

try:
    from transformers import MarianMTModel, MarianTokenizer, pipeline
    HAS_MARIAN = True
except ImportError:
    HAS_MARIAN = False

# Phonetic matching
try:
    import phonetics
    HAS_PHONETICS = True
except ImportError:
    HAS_PHONETICS = False

try:
    from fuzzywuzzy import fuzz
    HAS_FUZZYWUZZY = True
except ImportError:
    HAS_FUZZYWUZZY = False

logger = logging.getLogger(__name__)


@dataclass
class TransliterationResult:
    """Result of transliteration operation"""
    original: str
    transliterated: str
    script_from: ScriptType
    script_to: ScriptType
    method: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TranslationResult:
    """Result of translation operation"""
    original: str
    translated: str
    language_from: LanguageInfo
    language_to: LanguageInfo
    method: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class ScriptTransliterator:
    """Base class for script transliteration"""
    
    def __init__(self):
        self.transliteration_rules = self._load_transliteration_rules()
        self.icu_transliterators = {}
        self._initialize_icu()
    
    def _initialize_icu(self):
        """Initialize ICU transliterators if available"""
        if not HAS_ICU:
            return
        
        try:
            # Common transliteration pairs
            transliterator_ids = [
                'Cyrillic-Latin',
                'Arabic-Latin', 
                'Greek-Latin',
                'Hebrew-Latin',
                'Devanagari-Latin',
                'Han-Latin',  # Chinese
                'Hiragana-Latin',
                'Katakana-Latin',
                'Georgian-Latin',
                'Armenian-Latin',
                'Thai-Latin'
            ]
            
            for trans_id in transliterator_ids:
                try:
                    self.icu_transliterators[trans_id] = Transliterator.createInstance(trans_id)
                    logger.debug(f"Loaded ICU transliterator: {trans_id}")
                except Exception as e:
                    logger.debug(f"Could not load ICU transliterator {trans_id}: {e}")
        
        except Exception as e:
            logger.warning(f"ICU initialization failed: {e}")
    
    def _load_transliteration_rules(self) -> Dict[str, Dict[str, str]]:
        """Load custom transliteration rules"""
        # This would typically load from configuration files
        # For now, defining key mappings inline
        return {
            'cyrillic_to_latin': {
                'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e',
                'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k',
                'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
                'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
                'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
                'э': 'e', 'ю': 'yu', 'я': 'ya'
            },
            'arabic_to_latin': {
                'ا': 'a', 'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j', 'ح': 'h',
                'خ': 'kh', 'د': 'd', 'ذ': 'dh', 'ر': 'r', 'ز': 'z', 'س': 's',
                'ش': 'sh', 'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'z', 'ع': '',
                'غ': 'gh', 'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm',
                'ن': 'n', 'ه': 'h', 'و': 'w', 'ي': 'y'
            },
            'greek_to_latin': {
                'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e', 'ζ': 'z',
                'η': 'e', 'θ': 'th', 'ι': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm',
                'ν': 'n', 'ξ': 'x', 'ο': 'o', 'π': 'p', 'ρ': 'r', 'σ': 's',
                'τ': 't', 'υ': 'u', 'φ': 'f', 'χ': 'ch', 'ψ': 'ps', 'ω': 'o'
            }
        }
    
    def transliterate_cyrillic(self, text: str) -> TransliterationResult:
        """Transliterate Cyrillic text to Latin"""
        if not text:
            return TransliterationResult('', '', ScriptType.CYRILLIC, ScriptType.LATIN, 'none', 0.0)
        
        # Method 1: ICU transliterator
        if 'Cyrillic-Latin' in self.icu_transliterators:
            try:
                transliterated = self.icu_transliterators['Cyrillic-Latin'].transliterate(text)
                return TransliterationResult(
                    text, transliterated, ScriptType.CYRILLIC, ScriptType.LATIN,
                    'icu', 0.9, {'icu_id': 'Cyrillic-Latin'}
                )
            except Exception as e:
                logger.debug(f"ICU Cyrillic transliteration failed: {e}")
        
        # Method 2: transliterate library
        if HAS_TRANSLITERATE:
            try:
                transliterated = transliterate.translit(text, 'ru', reversed=True)
                return TransliterationResult(
                    text, transliterated, ScriptType.CYRILLIC, ScriptType.LATIN,
                    'transliterate', 0.8
                )
            except Exception as e:
                logger.debug(f"transliterate library failed: {e}")
        
        # Method 3: Custom rules
        rules = self.transliteration_rules.get('cyrillic_to_latin', {})
        transliterated = text.lower()
        for cyrillic, latin in rules.items():
            transliterated = transliterated.replace(cyrillic, latin)
        
        return TransliterationResult(
            text, transliterated, ScriptType.CYRILLIC, ScriptType.LATIN,
            'custom_rules', 0.7
        )
    
    def transliterate_arabic(self, text: str) -> TransliterationResult:
        """Transliterate Arabic text to Latin"""
        if not text:
            return TransliterationResult('', '', ScriptType.ARABIC, ScriptType.LATIN, 'none', 0.0)
        
        # Method 1: ICU transliterator
        if 'Arabic-Latin' in self.icu_transliterators:
            try:
                transliterated = self.icu_transliterators['Arabic-Latin'].transliterate(text)
                return TransliterationResult(
                    text, transliterated, ScriptType.ARABIC, ScriptType.LATIN,
                    'icu', 0.9, {'icu_id': 'Arabic-Latin'}
                )
            except Exception as e:
                logger.debug(f"ICU Arabic transliteration failed: {e}")
        
        # Method 2: Custom rules
        rules = self.transliteration_rules.get('arabic_to_latin', {})
        transliterated = text
        for arabic, latin in rules.items():
            transliterated = transliterated.replace(arabic, latin)
        
        # Remove Arabic diacritics
        transliterated = re.sub(r'[\u064B-\u065F\u0670\u06D6-\u06ED]', '', transliterated)
        
        return TransliterationResult(
            text, transliterated, ScriptType.ARABIC, ScriptType.LATIN,
            'custom_rules', 0.7
        )
    
    def transliterate_cjk(self, text: str) -> TransliterationResult:
        """Transliterate CJK text to Latin"""
        if not text:
            return TransliterationResult('', '', ScriptType.CJK, ScriptType.LATIN, 'none', 0.0)
        
        # Method 1: ICU transliterator for Chinese
        if 'Han-Latin' in self.icu_transliterators:
            try:
                transliterated = self.icu_transliterators['Han-Latin'].transliterate(text)
                return TransliterationResult(
                    text, transliterated, ScriptType.CJK, ScriptType.LATIN,
                    'icu', 0.8, {'icu_id': 'Han-Latin'}
                )
            except Exception as e:
                logger.debug(f"ICU CJK transliteration failed: {e}")
        
        # Method 2: Unidecode (fallback)
        if HAS_UNIDECODE:
            transliterated = unidecode(text)
            return TransliterationResult(
                text, transliterated, ScriptType.CJK, ScriptType.LATIN,
                'unidecode', 0.6
            )
        
        return TransliterationResult(
            text, text, ScriptType.CJK, ScriptType.LATIN, 'none', 0.0
        )
    
    def transliterate_universal(self, text: str, script: ScriptType) -> TransliterationResult:
        """Universal transliteration using unidecode"""
        if not text or not HAS_UNIDECODE:
            return TransliterationResult(text, text, script, ScriptType.LATIN, 'none', 0.0)
        
        try:
            transliterated = unidecode(text)
            return TransliterationResult(
                text, transliterated, script, ScriptType.LATIN,
                'unidecode', 0.5
            )
        except Exception as e:
            logger.error(f"Unidecode transliteration failed: {e}")
            return TransliterationResult(text, text, script, ScriptType.LATIN, 'failed', 0.0)
    
    def transliterate(self, text: str, script: Optional[ScriptType] = None) -> TransliterationResult:
        """Main transliteration method with automatic script detection"""
        if not text:
            return TransliterationResult('', '', ScriptType.UNKNOWN, ScriptType.LATIN, 'none', 0.0)
        
        if script is None:
            script, _ = language_detector.detect_script(text)
        
        # Route to appropriate transliterator
        if script == ScriptType.CYRILLIC:
            return self.transliterate_cyrillic(text)
        elif script == ScriptType.ARABIC:
            return self.transliterate_arabic(text)
        elif script == ScriptType.CJK:
            return self.transliterate_cjk(text)
        elif script == ScriptType.GREEK:
            if 'Greek-Latin' in self.icu_transliterators:
                try:
                    transliterated = self.icu_transliterators['Greek-Latin'].transliterate(text)
                    return TransliterationResult(
                        text, transliterated, ScriptType.GREEK, ScriptType.LATIN,
                        'icu', 0.9
                    )
                except Exception:
                    pass
            return self.transliterate_universal(text, script)
        elif script in [ScriptType.HEBREW, ScriptType.DEVANAGARI, ScriptType.THAI, 
                       ScriptType.GEORGIAN, ScriptType.ARMENIAN]:
            return self.transliterate_universal(text, script)
        else:
            # Already Latin or unknown
            return TransliterationResult(text, text, script, ScriptType.LATIN, 'none', 1.0)


class MultiLanguageTranslator:
    """Multi-language translation system"""
    
    def __init__(self):
        self.translators = {}
        self.marian_models = {}
        self._initialize_translators()
    
    def _initialize_translators(self):
        """Initialize available translation services"""
        # Google Translator
        if HAS_DEEP_TRANSLATOR:
            try:
                self.translators['google'] = GoogleTranslator
                logger.info("Google Translator initialized")
            except Exception as e:
                logger.warning(f"Google Translator initialization failed: {e}")
        
        # Marian MT models
        if HAS_MARIAN:
            self._initialize_marian_models()
    
    def _initialize_marian_models(self):
        """Initialize offline Marian translation models"""
        # Common language pairs for business intelligence
        model_pairs = [
            ('zh', 'en'),  # Chinese to English
            ('ru', 'en'),  # Russian to English
            ('ar', 'en'),  # Arabic to English
            ('es', 'en'),  # Spanish to English
            ('fr', 'en'),  # French to English
            ('de', 'en'),  # German to English
        ]
        
        for src, tgt in model_pairs:
            model_name = f'Helsinki-NLP/opus-mt-{src}-{tgt}'
            try:
                # Only initialize if model is available locally
                # Don't auto-download to avoid large downloads
                tokenizer = MarianTokenizer.from_pretrained(model_name, local_files_only=True)
                model = MarianMTModel.from_pretrained(model_name, local_files_only=True)
                self.marian_models[f'{src}-{tgt}'] = (tokenizer, model)
                logger.info(f"Loaded Marian model: {src} -> {tgt}")
            except Exception:
                # Model not available locally
                logger.debug(f"Marian model not available locally: {src} -> {tgt}")
    
    def translate_google(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Translate using Google Translator"""
        if not HAS_DEEP_TRANSLATOR or 'google' not in self.translators:
            raise ValueError("Google Translator not available")
        
        try:
            translator = self.translators['google'](source=source_lang, target=target_lang)
            translated = translator.translate(text)
            
            return TranslationResult(
                text, translated,
                language_detector.language_data.get(source_lang, language_detector.language_data['en']),
                language_detector.language_data.get(target_lang, language_detector.language_data['en']),
                'google', 0.9
            )
        
        except Exception as e:
            logger.error(f"Google translation failed: {e}")
            raise
    
    def translate_marian(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Translate using Marian MT model"""
        model_key = f'{source_lang}-{target_lang}'
        
        if model_key not in self.marian_models:
            raise ValueError(f"Marian model not available for {source_lang} -> {target_lang}")
        
        try:
            tokenizer, model = self.marian_models[model_key]
            
            # Tokenize and translate
            inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
            translated_tokens = model.generate(**inputs, max_length=512, num_beams=4, early_stopping=True)
            translated = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
            
            return TranslationResult(
                text, translated,
                language_detector.language_data.get(source_lang, language_detector.language_data['en']),
                language_detector.language_data.get(target_lang, language_detector.language_data['en']),
                'marian', 0.8, {'model': model_key}
            )
        
        except Exception as e:
            logger.error(f"Marian translation failed: {e}")
            raise
    
    def translate(self, text: str, source_lang: str, target_lang: str = 'en', 
                 prefer_offline: bool = False) -> TranslationResult:
        """Main translation method with fallback options"""
        if not text or source_lang == target_lang:
            return TranslationResult(
                text, text,
                language_detector.language_data.get(source_lang, language_detector.language_data['en']),
                language_detector.language_data.get(target_lang, language_detector.language_data['en']),
                'none', 1.0
            )
        
        errors = []
        
        # Try offline models first if preferred
        if prefer_offline:
            try:
                return self.translate_marian(text, source_lang, target_lang)
            except Exception as e:
                errors.append(f"Marian: {e}")
        
        # Try Google Translator
        try:
            return self.translate_google(text, source_lang, target_lang)
        except Exception as e:
            errors.append(f"Google: {e}")
        
        # Try Marian as fallback if not already tried
        if not prefer_offline:
            try:
                return self.translate_marian(text, source_lang, target_lang)
            except Exception as e:
                errors.append(f"Marian: {e}")
        
        # All translation methods failed
        logger.error(f"All translation methods failed for {source_lang} -> {target_lang}: {errors}")
        return TranslationResult(
            text, text,
            language_detector.language_data.get(source_lang, language_detector.language_data['en']),
            language_detector.language_data.get(target_lang, language_detector.language_data['en']),
            'failed', 0.0, {'errors': errors}
        )


class EntityNormalizer:
    """Normalizes entities for cross-language matching"""
    
    def __init__(self):
        self.transliterator = ScriptTransliterator()
        self.translator = MultiLanguageTranslator()
        self.phonetic_algorithms = ['soundex', 'metaphone', 'nysiis'] if HAS_PHONETICS else []
    
    def normalize_company_name(self, name: str, language: LanguageInfo) -> Dict[str, str]:
        """Normalize company name for matching"""
        normalized = {}
        
        # Original
        normalized['original'] = name
        
        # Cleaned (remove common suffixes, punctuation)
        cleaned = self._clean_company_name(name, language)
        normalized['cleaned'] = cleaned
        
        # Transliterated
        if language.script != ScriptType.LATIN:
            transliteration_result = self.transliterator.transliterate(name, language.script)
            normalized['transliterated'] = transliteration_result.transliterated
            normalized['transliterated_cleaned'] = self._clean_company_name(
                transliteration_result.transliterated, language_detector.language_data['en']
            )
        
        # Translated to English
        if language.code != 'en':
            try:
                translation_result = self.translator.translate(name, language.code, 'en')
                normalized['translated'] = translation_result.translated
                normalized['translated_cleaned'] = self._clean_company_name(
                    translation_result.translated, language_detector.language_data['en']
                )
            except Exception as e:
                logger.debug(f"Translation failed for company name: {e}")
        
        # Phonetic representations
        if HAS_PHONETICS:
            for algorithm in self.phonetic_algorithms:
                try:
                    if algorithm == 'soundex':
                        phonetic = phonetics.soundex(cleaned)
                    elif algorithm == 'metaphone':
                        phonetic = phonetics.metaphone(cleaned)
                    elif algorithm == 'nysiis':
                        phonetic = phonetics.nysiis(cleaned)
                    else:
                        continue
                    
                    if phonetic:
                        normalized[f'phonetic_{algorithm}'] = phonetic
                except Exception as e:
                    logger.debug(f"Phonetic encoding failed with {algorithm}: {e}")
        
        return normalized
    
    def _clean_company_name(self, name: str, language: LanguageInfo) -> str:
        """Clean company name by removing suffixes and noise"""
        if not name:
            return name
        
        cleaned = name.strip()
        
        # Language-specific cleaning patterns
        if language.code == 'en':
            # Remove English company suffixes
            suffixes = r'\b(?:Inc\.?|Corp\.?|LLC|Ltd\.?|Limited|Company|Co\.?|Group|Holdings|International|Intl\.?|Industries|Solutions|Services|Technologies|Systems|Enterprises|Associates)\b'
            cleaned = re.sub(suffixes, '', cleaned, flags=re.IGNORECASE)
        elif language.code == 'zh':
            # Remove Chinese company suffixes
            suffixes = r'(?:公司|企业|集团|有限公司|股份有限公司|责任有限公司)'
            cleaned = re.sub(suffixes, '', cleaned)
        elif language.code == 'ja':
            # Remove Japanese company suffixes
            suffixes = r'(?:株式会社|有限会社|合同会社|合名会社|合資会社|企業|会社)'
            cleaned = re.sub(suffixes, '', cleaned)
        elif language.code == 'ru':
            # Remove Russian company suffixes
            suffixes = r'\b(?:ООО|ЗАО|ОАО|ИП|Общество|Компания|Корпорация|Группа|Холдинг)\b'
            cleaned = re.sub(suffixes, '', cleaned, flags=re.IGNORECASE)
        
        # General cleaning
        cleaned = re.sub(r'[^\w\s]', ' ', cleaned)  # Remove punctuation
        cleaned = re.sub(r'\s+', ' ', cleaned)      # Normalize whitespace
        cleaned = cleaned.strip().lower()
        
        return cleaned
    
    def normalize_person_name(self, name: str, language: LanguageInfo) -> Dict[str, str]:
        """Normalize person name for matching"""
        normalized = {}
        
        # Original
        normalized['original'] = name
        
        # Cleaned
        cleaned = self._clean_person_name(name, language)
        normalized['cleaned'] = cleaned
        
        # Transliterated
        if language.script != ScriptType.LATIN:
            transliteration_result = self.transliterator.transliterate(name, language.script)
            normalized['transliterated'] = transliteration_result.transliterated
        
        # Phonetic representations for Latin scripts
        if language.script == ScriptType.LATIN and HAS_PHONETICS:
            for algorithm in self.phonetic_algorithms:
                try:
                    if algorithm == 'soundex':
                        phonetic = phonetics.soundex(cleaned)
                    elif algorithm == 'metaphone':
                        phonetic = phonetics.metaphone(cleaned)
                    elif algorithm == 'nysiis':
                        phonetic = phonetics.nysiis(cleaned)
                    else:
                        continue
                    
                    if phonetic:
                        normalized[f'phonetic_{algorithm}'] = phonetic
                except Exception as e:
                    logger.debug(f"Phonetic encoding failed: {e}")
        
        return normalized
    
    def _clean_person_name(self, name: str, language: LanguageInfo) -> str:
        """Clean person name"""
        if not name:
            return name
        
        cleaned = name.strip()
        
        # Remove common titles
        if language.code == 'en':
            titles = r'\b(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Prof\.?|CEO|CFO|CTO|President|Director)\b'
            cleaned = re.sub(titles, '', cleaned, flags=re.IGNORECASE)
        
        # General cleaning
        cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip().lower()
        
        return cleaned
    
    def calculate_similarity(self, normalized1: Dict[str, str], 
                           normalized2: Dict[str, str]) -> float:
        """Calculate similarity between normalized entities"""
        if not HAS_FUZZYWUZZY:
            return 0.0
        
        max_similarity = 0.0
        
        # Compare all normalized forms
        for key1, value1 in normalized1.items():
            if not value1 or key1.startswith('phonetic_'):
                continue
            
            for key2, value2 in normalized2.items():
                if not value2 or key2.startswith('phonetic_'):
                    continue
                
                similarity = fuzz.ratio(value1, value2) / 100.0
                max_similarity = max(max_similarity, similarity)
        
        # Compare phonetic encodings
        for algorithm in self.phonetic_algorithms:
            key = f'phonetic_{algorithm}'
            if key in normalized1 and key in normalized2:
                if normalized1[key] == normalized2[key]:
                    max_similarity = max(max_similarity, 0.8)  # High similarity for phonetic match
        
        return max_similarity


# Global instances
script_transliterator = ScriptTransliterator()
multilang_translator = MultiLanguageTranslator()
entity_normalizer = EntityNormalizer()
