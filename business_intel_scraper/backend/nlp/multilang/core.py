"""
Multi-Language NLP Core Module

Provides language detection, script identification, and multi-language processing capabilities
for business intelligence data extraction from diverse global sources.
"""

from __future__ import annotations

import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from dataclasses import dataclass, field
from pathlib import Path
import json
from enum import Enum

# Language and script detection
try:
    import langdetect
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False

try:
    import polyglot
    from polyglot.detect import Detector
    HAS_POLYGLOT = True
except ImportError:
    HAS_POLYGLOT = False

try:
    import fasttext
    HAS_FASTTEXT = True
except ImportError:
    HAS_FASTTEXT = False

# Script detection
try:
    import unicodedata
    HAS_UNICODEDATA = True
except ImportError:
    HAS_UNICODEDATA = False

# Multi-language tokenization
try:
    import jieba  # Chinese
    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False

try:
    import MeCab  # Japanese
    HAS_MECAB = True
except ImportError:
    HAS_MECAB = False

try:
    import stanza
    HAS_STANZA = True
except ImportError:
    HAS_STANZA = False

# Transliteration
try:
    from unidecode import unidecode
    HAS_UNIDECODE = True
except ImportError:
    HAS_UNIDECODE = False

try:
    from icu import Transliterator
    HAS_ICU = True
except ImportError:
    HAS_ICU = False

logger = logging.getLogger(__name__)


class ScriptType(Enum):
    """Unicode script types for text classification"""
    LATIN = "Latin"
    CYRILLIC = "Cyrillic"
    ARABIC = "Arabic"
    CJK = "CJK"  # Chinese, Japanese, Korean
    DEVANAGARI = "Devanagari"
    GREEK = "Greek"
    HEBREW = "Hebrew"
    THAI = "Thai"
    GEORGIAN = "Georgian"
    ARMENIAN = "Armenian"
    MIXED = "Mixed"
    UNKNOWN = "Unknown"


class LanguageFamily(Enum):
    """Language family classifications"""
    INDO_EUROPEAN = "Indo-European"
    SINO_TIBETAN = "Sino-Tibetan"
    AFRO_ASIATIC = "Afro-Asiatic"
    ALTAIC = "Altaic"
    AUSTROASIATIC = "Austroasiatic"
    AUSTRONESIAN = "Austronesian"
    NIGER_CONGO = "Niger-Congo"
    DRAVIDIAN = "Dravidian"
    OTHER = "Other"


@dataclass
class LanguageInfo:
    """Comprehensive language information"""
    code: str  # ISO 639-1/639-2 code
    name: str
    native_name: str
    script: ScriptType
    family: LanguageFamily
    confidence: float
    rtl: bool = False  # Right-to-left writing
    tokenizer: Optional[str] = None
    spacy_model: Optional[str] = None
    stanza_model: Optional[str] = None


@dataclass
class DetectedText:
    """Text with detected language and script information"""
    text: str
    language: LanguageInfo
    script: ScriptType
    confidence: float
    segments: List[Tuple[str, LanguageInfo]] = field(default_factory=list)  # For mixed-language text


class MultiLanguageDetector:
    """Multi-language and script detection system"""
    
    def __init__(self):
        self.language_models = {}
        self.script_patterns = self._initialize_script_patterns()
        self.language_data = self._load_language_data()
        self._initialize_detectors()
    
    def _initialize_detectors(self):
        """Initialize available language detection libraries"""
        if HAS_FASTTEXT:
            try:
                # Download language identification model if not present
                model_path = Path.home() / '.cache' / 'fasttext' / 'lid.176.bin'
                if model_path.exists():
                    self.language_models['fasttext'] = fasttext.load_model(str(model_path))
                    logger.info("FastText language detector initialized")
            except Exception as e:
                logger.warning(f"FastText initialization failed: {e}")
        
        if HAS_LANGDETECT:
            logger.info("Langdetect initialized")
            
        if HAS_POLYGLOT:
            logger.info("Polyglot detector initialized")
    
    def _initialize_script_patterns(self) -> Dict[ScriptType, Dict[str, Any]]:
        """Initialize Unicode script detection patterns"""
        return {
            ScriptType.LATIN: {
                'ranges': [(0x0041, 0x007A), (0x00C0, 0x024F), (0x1E00, 0x1EFF)],
                'pattern': re.compile(r'[A-Za-z\u00C0-\u024F\u1E00-\u1EFF]+')
            },
            ScriptType.CYRILLIC: {
                'ranges': [(0x0400, 0x04FF), (0x0500, 0x052F), (0x2DE0, 0x2DFF)],
                'pattern': re.compile(r'[\u0400-\u04FF\u0500-\u052F\u2DE0-\u2DFF]+')
            },
            ScriptType.ARABIC: {
                'ranges': [(0x0600, 0x06FF), (0x0750, 0x077F), (0xFB50, 0xFDFF)],
                'pattern': re.compile(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF]+')
            },
            ScriptType.CJK: {
                'ranges': [
                    (0x4E00, 0x9FFF),  # CJK Unified Ideographs
                    (0x3400, 0x4DBF),  # CJK Extension A
                    (0x20000, 0x2A6DF),  # CJK Extension B
                    (0x3040, 0x309F),  # Hiragana
                    (0x30A0, 0x30FF),  # Katakana
                    (0xAC00, 0xD7AF),  # Hangul
                ],
                'pattern': re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF\u3040-\u309F\u30A0-\u30FF\uAC00-\uD7AF]+')
            },
            ScriptType.DEVANAGARI: {
                'ranges': [(0x0900, 0x097F)],
                'pattern': re.compile(r'[\u0900-\u097F]+')
            },
            ScriptType.GREEK: {
                'ranges': [(0x0370, 0x03FF), (0x1F00, 0x1FFF)],
                'pattern': re.compile(r'[\u0370-\u03FF\u1F00-\u1FFF]+')
            },
            ScriptType.HEBREW: {
                'ranges': [(0x0590, 0x05FF), (0xFB1D, 0xFB4F)],
                'pattern': re.compile(r'[\u0590-\u05FF\uFB1D-\uFB4F]+')
            },
            ScriptType.THAI: {
                'ranges': [(0x0E00, 0x0E7F)],
                'pattern': re.compile(r'[\u0E00-\u0E7F]+')
            },
            ScriptType.GEORGIAN: {
                'ranges': [(0x10A0, 0x10FF), (0x2D00, 0x2D2F)],
                'pattern': re.compile(r'[\u10A0-\u10FF\u2D00-\u2D2F]+')
            },
            ScriptType.ARMENIAN: {
                'ranges': [(0x0530, 0x058F), (0xFB13, 0xFB17)],
                'pattern': re.compile(r'[\u0530-\u058F\uFB13-\uFB17]+')
            }
        }
    
    def _load_language_data(self) -> Dict[str, LanguageInfo]:
        """Load comprehensive language metadata"""
        # This would typically load from a configuration file
        # For now, defining major business languages inline
        return {
            # Major European Languages
            'en': LanguageInfo('en', 'English', 'English', ScriptType.LATIN, 
                             LanguageFamily.INDO_EUROPEAN, 0.0, spacy_model='en_core_web_sm'),
            'es': LanguageInfo('es', 'Spanish', 'Español', ScriptType.LATIN, 
                             LanguageFamily.INDO_EUROPEAN, 0.0, spacy_model='es_core_news_sm'),
            'fr': LanguageInfo('fr', 'French', 'Français', ScriptType.LATIN, 
                             LanguageFamily.INDO_EUROPEAN, 0.0, spacy_model='fr_core_news_sm'),
            'de': LanguageInfo('de', 'German', 'Deutsch', ScriptType.LATIN, 
                             LanguageFamily.INDO_EUROPEAN, 0.0, spacy_model='de_core_news_sm'),
            'it': LanguageInfo('it', 'Italian', 'Italiano', ScriptType.LATIN, 
                             LanguageFamily.INDO_EUROPEAN, 0.0, spacy_model='it_core_news_sm'),
            'pt': LanguageInfo('pt', 'Portuguese', 'Português', ScriptType.LATIN, 
                             LanguageFamily.INDO_EUROPEAN, 0.0, spacy_model='pt_core_news_sm'),
            'nl': LanguageInfo('nl', 'Dutch', 'Nederlands', ScriptType.LATIN, 
                             LanguageFamily.INDO_EUROPEAN, 0.0, spacy_model='nl_core_news_sm'),
            
            # Cyrillic Scripts
            'ru': LanguageInfo('ru', 'Russian', 'Русский', ScriptType.CYRILLIC, 
                             LanguageFamily.INDO_EUROPEAN, 0.0, spacy_model='ru_core_news_sm'),
            'uk': LanguageInfo('uk', 'Ukrainian', 'Українська', ScriptType.CYRILLIC, 
                             LanguageFamily.INDO_EUROPEAN, 0.0),
            'bg': LanguageInfo('bg', 'Bulgarian', 'Български', ScriptType.CYRILLIC, 
                             LanguageFamily.INDO_EUROPEAN, 0.0),
            'sr': LanguageInfo('sr', 'Serbian', 'Српски', ScriptType.CYRILLIC, 
                             LanguageFamily.INDO_EUROPEAN, 0.0),
            
            # CJK Languages
            'zh': LanguageInfo('zh', 'Chinese', '中文', ScriptType.CJK, 
                             LanguageFamily.SINO_TIBETAN, 0.0, tokenizer='jieba', 
                             spacy_model='zh_core_web_sm', stanza_model='zh'),
            'ja': LanguageInfo('ja', 'Japanese', '日本語', ScriptType.CJK, 
                             LanguageFamily.OTHER, 0.0, tokenizer='mecab',
                             spacy_model='ja_core_news_sm', stanza_model='ja'),
            'ko': LanguageInfo('ko', 'Korean', '한국어', ScriptType.CJK, 
                             LanguageFamily.OTHER, 0.0, stanza_model='ko'),
            
            # Arabic Script
            'ar': LanguageInfo('ar', 'Arabic', 'العربية', ScriptType.ARABIC, 
                             LanguageFamily.AFRO_ASIATIC, 0.0, rtl=True, stanza_model='ar'),
            'fa': LanguageInfo('fa', 'Persian', 'فارسی', ScriptType.ARABIC, 
                             LanguageFamily.INDO_EUROPEAN, 0.0, rtl=True, stanza_model='fa'),
            'ur': LanguageInfo('ur', 'Urdu', 'اردو', ScriptType.ARABIC, 
                             LanguageFamily.INDO_EUROPEAN, 0.0, rtl=True),
            
            # South Asian Languages
            'hi': LanguageInfo('hi', 'Hindi', 'हिन्दी', ScriptType.DEVANAGARI, 
                             LanguageFamily.INDO_EUROPEAN, 0.0, stanza_model='hi'),
            'bn': LanguageInfo('bn', 'Bengali', 'বাংলা', ScriptType.DEVANAGARI, 
                             LanguageFamily.INDO_EUROPEAN, 0.0),
            
            # Southeast Asian Languages
            'th': LanguageInfo('th', 'Thai', 'ไทย', ScriptType.THAI, 
                             LanguageFamily.OTHER, 0.0, stanza_model='th'),
            'vi': LanguageInfo('vi', 'Vietnamese', 'Tiếng Việt', ScriptType.LATIN, 
                             LanguageFamily.AUSTROASIATIC, 0.0, stanza_model='vi'),
            'id': LanguageInfo('id', 'Indonesian', 'Bahasa Indonesia', ScriptType.LATIN, 
                             LanguageFamily.AUSTRONESIAN, 0.0),
            'ms': LanguageInfo('ms', 'Malay', 'Bahasa Melayu', ScriptType.LATIN, 
                             LanguageFamily.AUSTRONESIAN, 0.0),
            
            # Other Important Languages
            'tr': LanguageInfo('tr', 'Turkish', 'Türkçe', ScriptType.LATIN, 
                             LanguageFamily.ALTAIC, 0.0, stanza_model='tr'),
            'he': LanguageInfo('he', 'Hebrew', 'עברית', ScriptType.HEBREW, 
                             LanguageFamily.AFRO_ASIATIC, 0.0, rtl=True),
            'el': LanguageInfo('el', 'Greek', 'Ελληνικά', ScriptType.GREEK, 
                             LanguageFamily.INDO_EUROPEAN, 0.0),
        }
    
    def detect_script(self, text: str) -> Tuple[ScriptType, float]:
        """Detect the primary script used in text"""
        if not text:
            return ScriptType.UNKNOWN, 0.0
        
        # Count characters by script
        script_counts = {script: 0 for script in ScriptType}
        total_chars = 0
        
        for char in text:
            if char.isalnum():
                total_chars += 1
                script_found = False
                
                for script_type, script_info in self.script_patterns.items():
                    if any(start <= ord(char) <= end for start, end in script_info['ranges']):
                        script_counts[script_type] += 1
                        script_found = True
                        break
                
                if not script_found:
                    script_counts[ScriptType.UNKNOWN] += 1
        
        if total_chars == 0:
            return ScriptType.UNKNOWN, 0.0
        
        # Find dominant script
        max_count = max(script_counts.values())
        if max_count == 0:
            return ScriptType.UNKNOWN, 0.0
        
        dominant_script = next(script for script, count in script_counts.items() 
                             if count == max_count)
        confidence = max_count / total_chars
        
        # Check for mixed scripts
        significant_scripts = [script for script, count in script_counts.items() 
                             if count > total_chars * 0.1 and count > 0]
        
        if len(significant_scripts) > 1:
            return ScriptType.MIXED, confidence
        
        return dominant_script, confidence
    
    def detect_language(self, text: str) -> List[LanguageInfo]:
        """Detect language(s) in text using multiple methods"""
        if not text or len(text.strip()) < 3:
            return []
        
        detected_languages = []
        
        # Method 1: langdetect (Google's language detection)
        if HAS_LANGDETECT:
            try:
                lang_probs = langdetect.detect_langs(text)
                for lang_prob in lang_probs[:3]:  # Top 3 candidates
                    lang_code = lang_prob.lang
                    if lang_code in self.language_data:
                        lang_info = self.language_data[lang_code]
                        lang_info.confidence = lang_prob.prob
                        detected_languages.append(lang_info)
            except Exception as e:
                logger.debug(f"Langdetect failed: {e}")
        
        # Method 2: FastText
        if HAS_FASTTEXT and 'fasttext' in self.language_models:
            try:
                predictions = self.language_models['fasttext'].predict(text.replace('\n', ' '), k=3)
                for i, (label, confidence) in enumerate(zip(predictions[0], predictions[1])):
                    lang_code = label.replace('__label__', '')
                    if lang_code in self.language_data and confidence > 0.1:
                        lang_info = self.language_data[lang_code]
                        # Adjust confidence if we already have this language
                        existing = next((l for l in detected_languages if l.code == lang_code), None)
                        if existing:
                            existing.confidence = max(existing.confidence, float(confidence))
                        else:
                            lang_info.confidence = float(confidence)
                            detected_languages.append(lang_info)
            except Exception as e:
                logger.debug(f"FastText detection failed: {e}")
        
        # Method 3: Polyglot
        if HAS_POLYGLOT:
            try:
                detector = Detector(text)
                for language in detector.languages:
                    lang_code = language.code
                    if lang_code in self.language_data:
                        lang_info = self.language_data[lang_code]
                        existing = next((l for l in detected_languages if l.code == lang_code), None)
                        if existing:
                            existing.confidence = max(existing.confidence, language.confidence)
                        else:
                            lang_info.confidence = language.confidence
                            detected_languages.append(lang_info)
            except Exception as e:
                logger.debug(f"Polyglot detection failed: {e}")
        
        # Sort by confidence and return top candidates
        detected_languages.sort(key=lambda x: x.confidence, reverse=True)
        return detected_languages[:3]
    
    def detect_mixed_language_segments(self, text: str) -> List[Tuple[str, LanguageInfo]]:
        """Detect and segment mixed-language text"""
        if not text:
            return []
        
        # Simple sentence-based segmentation
        # More sophisticated approaches would use sentence boundary detection
        sentences = re.split(r'[.!?]+', text)
        segments = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 3:
                continue
                
            detected_langs = self.detect_language(sentence)
            if detected_langs:
                segments.append((sentence, detected_langs[0]))
        
        return segments
    
    def create_detected_text(self, text: str) -> DetectedText:
        """Create a DetectedText object with full language analysis"""
        if not text:
            return DetectedText(text, self.language_data['en'], ScriptType.UNKNOWN, 0.0)
        
        # Detect script
        script, script_confidence = self.detect_script(text)
        
        # Detect language
        detected_languages = self.detect_language(text)
        primary_language = detected_languages[0] if detected_languages else self.language_data['en']
        
        # Detect mixed segments if confidence is low or script is mixed
        segments = []
        if script == ScriptType.MIXED or (detected_languages and detected_languages[0].confidence < 0.7):
            segments = self.detect_mixed_language_segments(text)
        
        return DetectedText(
            text=text,
            language=primary_language,
            script=script,
            confidence=primary_language.confidence if detected_languages else 0.0,
            segments=segments
        )


# Global detector instance
language_detector = MultiLanguageDetector()
