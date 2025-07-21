"""
Multi-Language Tokenization Module

Provides language-specific tokenization for various scripts and languages
used in global business intelligence data sources.
"""

from __future__ import annotations

import re
import logging
from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod

from .core import LanguageInfo, ScriptType, DetectedText, language_detector

# Language-specific tokenizers
try:
    import jieba
    jieba.setLogLevel(logging.WARNING)  # Reduce jieba logging
    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False

try:
    import MeCab
    HAS_MECAB = True
except ImportError:
    HAS_MECAB = False

try:
    from pythainlp.tokenize import word_tokenize as thai_word_tokenize
    HAS_PYTHAINLP = True
except ImportError:
    HAS_PYTHAINLP = False

try:
    import stanza
    HAS_STANZA = True
except ImportError:
    HAS_STANZA = False

try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

logger = logging.getLogger(__name__)


class BaseTokenizer(ABC):
    """Abstract base class for language-specific tokenizers"""
    
    def __init__(self, language: LanguageInfo):
        self.language = language
    
    @abstractmethod
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words/tokens"""
        pass
    
    @abstractmethod
    def tokenize_sentences(self, text: str) -> List[str]:
        """Tokenize text into sentences"""
        pass


class LatinScriptTokenizer(BaseTokenizer):
    """Tokenizer for Latin script languages (English, Spanish, French, etc.)"""
    
    def __init__(self, language: LanguageInfo):
        super().__init__(language)
        self.nlp_model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize spaCy model if available"""
        if HAS_SPACY and self.language.spacy_model:
            try:
                self.nlp_model = spacy.load(self.language.spacy_model)
            except Exception:
                # Fallback to blank model
                try:
                    self.nlp_model = spacy.blank(self.language.code)
                except Exception:
                    logger.warning(f"Could not initialize spaCy model for {self.language.name}")
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize Latin script text"""
        if not text:
            return []
        
        if self.nlp_model:
            doc = self.nlp_model(text)
            return [token.text for token in doc if not token.is_space]
        else:
            # Simple regex-based tokenization
            # Handle contractions, punctuation, etc.
            pattern = r"\b\w+(?:'\w+)?\b|\S"
            return re.findall(pattern, text, re.UNICODE)
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """Tokenize into sentences"""
        if not text:
            return []
        
        if self.nlp_model and self.nlp_model.has_pipe("sentencizer"):
            doc = self.nlp_model(text)
            return [sent.text.strip() for sent in doc.sents]
        else:
            # Simple sentence splitting
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]


class ChineseTokenizer(BaseTokenizer):
    """Chinese text tokenizer using jieba"""
    
    def __init__(self, language: LanguageInfo):
        super().__init__(language)
        self.initialized = False
        self._initialize_jieba()
    
    def _initialize_jieba(self):
        """Initialize jieba tokenizer"""
        if HAS_JIEBA:
            try:
                # Enable HMM for better unknown word recognition
                jieba.enable_parallel(4)  # Use parallel processing
                self.initialized = True
                logger.info("Chinese tokenizer (jieba) initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize jieba: {e}")
        else:
            logger.warning("jieba not available for Chinese tokenization")
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize Chinese text"""
        if not text:
            return []
        
        if not self.initialized:
            # Fallback to character-level splitting
            return list(text.replace(' ', ''))
        
        try:
            # Use jieba for word segmentation
            tokens = list(jieba.cut(text, cut_all=False, HMM=True))
            # Filter out whitespace-only tokens
            return [token for token in tokens if token.strip()]
        except Exception as e:
            logger.error(f"Chinese tokenization failed: {e}")
            return list(text.replace(' ', ''))
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """Tokenize Chinese text into sentences"""
        if not text:
            return []
        
        # Chinese sentence boundaries
        sentence_endings = r'[。！？；]+|[.!?;]+'
        sentences = re.split(sentence_endings, text)
        return [s.strip() for s in sentences if s.strip()]


class JapaneseTokenizer(BaseTokenizer):
    """Japanese text tokenizer using MeCab"""
    
    def __init__(self, language: LanguageInfo):
        super().__init__(language)
        self.mecab = None
        self._initialize_mecab()
    
    def _initialize_mecab(self):
        """Initialize MeCab tokenizer"""
        if HAS_MECAB:
            try:
                self.mecab = MeCab.Tagger('-Owakati')  # Wakati-gaki (word boundary) mode
                logger.info("Japanese tokenizer (MeCab) initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize MeCab: {e}")
        else:
            logger.warning("MeCab not available for Japanese tokenization")
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize Japanese text"""
        if not text:
            return []
        
        if not self.mecab:
            # Fallback: mix of character-level and basic splitting
            tokens = []
            for char in text:
                if char.isalnum() or ord(char) >= 0x3040:  # Japanese characters
                    tokens.append(char)
                elif char.isspace():
                    continue
                else:
                    tokens.append(char)
            return tokens
        
        try:
            result = self.mecab.parse(text).strip()
            return result.split()
        except Exception as e:
            logger.error(f"Japanese tokenization failed: {e}")
            return list(text.replace(' ', ''))
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """Tokenize Japanese text into sentences"""
        if not text:
            return []
        
        # Japanese sentence boundaries
        sentence_endings = r'[。！？]+|[.!?]+'
        sentences = re.split(sentence_endings, text)
        return [s.strip() for s in sentences if s.strip()]


class ArabicTokenizer(BaseTokenizer):
    """Arabic script tokenizer"""
    
    def __init__(self, language: LanguageInfo):
        super().__init__(language)
        self.stanza_pipeline = None
        self._initialize_stanza()
    
    def _initialize_stanza(self):
        """Initialize Stanza pipeline for Arabic"""
        if HAS_STANZA and self.language.stanza_model:
            try:
                self.stanza_pipeline = stanza.Pipeline(
                    self.language.stanza_model,
                    processors='tokenize',
                    verbose=False,
                    download_method=None  # Don't auto-download
                )
                logger.info(f"Arabic tokenizer (Stanza) initialized for {self.language.name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Stanza for {self.language.name}: {e}")
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize Arabic script text"""
        if not text:
            return []
        
        if self.stanza_pipeline:
            try:
                doc = self.stanza_pipeline(text)
                tokens = []
                for sentence in doc.sentences:
                    tokens.extend([token.text for token in sentence.tokens])
                return tokens
            except Exception as e:
                logger.error(f"Arabic tokenization failed: {e}")
        
        # Fallback: simple whitespace and punctuation splitting
        # Arabic text is generally space-separated at word level
        pattern = r'[\w\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF]+'
        return re.findall(pattern, text, re.UNICODE)
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """Tokenize Arabic text into sentences"""
        if not text:
            return []
        
        if self.stanza_pipeline:
            try:
                doc = self.stanza_pipeline(text)
                return [sentence.text for sentence in doc.sentences]
            except Exception:
                pass
        
        # Arabic sentence boundaries
        sentence_endings = r'[.!?؟]+|[.!?]+'
        sentences = re.split(sentence_endings, text)
        return [s.strip() for s in sentences if s.strip()]


class ThaiTokenizer(BaseTokenizer):
    """Thai text tokenizer"""
    
    def __init__(self, language: LanguageInfo):
        super().__init__(language)
        self.has_pythainlp = HAS_PYTHAINLP
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize Thai text"""
        if not text:
            return []
        
        if self.has_pythainlp:
            try:
                return thai_word_tokenize(text, engine='newmm')
            except Exception as e:
                logger.error(f"Thai tokenization failed: {e}")
        
        # Fallback: character-level splitting
        # Thai doesn't use spaces between words
        return list(text.replace(' ', ''))
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """Tokenize Thai text into sentences"""
        if not text:
            return []
        
        # Thai sentence boundaries
        sentence_endings = r'[.!?]+|[.!?]+'
        sentences = re.split(sentence_endings, text)
        return [s.strip() for s in sentences if s.strip()]


class CyrillicTokenizer(BaseTokenizer):
    """Cyrillic script tokenizer (Russian, Bulgarian, Serbian, etc.)"""
    
    def __init__(self, language: LanguageInfo):
        super().__init__(language)
        self.nlp_model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize spaCy model if available"""
        if HAS_SPACY and self.language.spacy_model:
            try:
                self.nlp_model = spacy.load(self.language.spacy_model)
            except Exception:
                logger.warning(f"Could not initialize spaCy model for {self.language.name}")
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize Cyrillic text"""
        if not text:
            return []
        
        if self.nlp_model:
            doc = self.nlp_model(text)
            return [token.text for token in doc if not token.is_space]
        else:
            # Simple regex-based tokenization for Cyrillic
            pattern = r'[\w\u0400-\u04FF\u0500-\u052F]+|[^\w\s]'
            return re.findall(pattern, text, re.UNICODE)
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """Tokenize Cyrillic text into sentences"""
        if not text:
            return []
        
        if self.nlp_model and self.nlp_model.has_pipe("sentencizer"):
            doc = self.nlp_model(text)
            return [sent.text.strip() for sent in doc.sents]
        else:
            # Simple sentence splitting
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]


class UniversalTokenizer(BaseTokenizer):
    """Universal tokenizer using Stanza for any supported language"""
    
    def __init__(self, language: LanguageInfo):
        super().__init__(language)
        self.stanza_pipeline = None
        self._initialize_stanza()
    
    def _initialize_stanza(self):
        """Initialize Stanza pipeline"""
        if HAS_STANZA and self.language.stanza_model:
            try:
                self.stanza_pipeline = stanza.Pipeline(
                    self.language.stanza_model,
                    processors='tokenize',
                    verbose=False,
                    download_method=None
                )
                logger.info(f"Universal tokenizer (Stanza) initialized for {self.language.name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Stanza for {self.language.name}: {e}")
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text using Stanza"""
        if not text:
            return []
        
        if self.stanza_pipeline:
            try:
                doc = self.stanza_pipeline(text)
                tokens = []
                for sentence in doc.sentences:
                    tokens.extend([token.text for token in sentence.tokens])
                return tokens
            except Exception as e:
                logger.error(f"Universal tokenization failed: {e}")
        
        # Fallback: simple regex-based tokenization
        pattern = r'\w+|[^\w\s]'
        return re.findall(pattern, text, re.UNICODE)
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """Tokenize text into sentences using Stanza"""
        if not text:
            return []
        
        if self.stanza_pipeline:
            try:
                doc = self.stanza_pipeline(text)
                return [sentence.text for sentence in doc.sentences]
            except Exception:
                pass
        
        # Fallback sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]


class MultiLanguageTokenizer:
    """Main tokenizer that automatically selects appropriate tokenizer"""
    
    def __init__(self):
        self.tokenizer_cache: Dict[str, BaseTokenizer] = {}
        self.tokenizer_classes = {
            ScriptType.LATIN: LatinScriptTokenizer,
            ScriptType.CJK: self._get_cjk_tokenizer,
            ScriptType.CYRILLIC: CyrillicTokenizer,
            ScriptType.ARABIC: ArabicTokenizer,
            ScriptType.THAI: ThaiTokenizer,
            ScriptType.DEVANAGARI: UniversalTokenizer,
            ScriptType.GREEK: LatinScriptTokenizer,
            ScriptType.HEBREW: ArabicTokenizer,  # Similar RTL handling
            ScriptType.GEORGIAN: UniversalTokenizer,
            ScriptType.ARMENIAN: UniversalTokenizer,
        }
    
    def _get_cjk_tokenizer(self, language: LanguageInfo) -> BaseTokenizer:
        """Get appropriate CJK tokenizer based on language"""
        if language.code == 'zh':
            return ChineseTokenizer(language)
        elif language.code == 'ja':
            return JapaneseTokenizer(language)
        else:
            return UniversalTokenizer(language)
    
    def get_tokenizer(self, language: LanguageInfo) -> BaseTokenizer:
        """Get appropriate tokenizer for language"""
        cache_key = f"{language.code}_{language.script.value}"
        
        if cache_key not in self.tokenizer_cache:
            tokenizer_class = self.tokenizer_classes.get(
                language.script, 
                UniversalTokenizer
            )
            
            if callable(tokenizer_class):
                if tokenizer_class == self._get_cjk_tokenizer:
                    tokenizer = tokenizer_class(language)
                else:
                    tokenizer = tokenizer_class(language)
            else:
                tokenizer = UniversalTokenizer(language)
            
            self.tokenizer_cache[cache_key] = tokenizer
        
        return self.tokenizer_cache[cache_key]
    
    def tokenize(self, text: str, language: Optional[LanguageInfo] = None) -> List[str]:
        """Tokenize text with automatic language detection"""
        if not text:
            return []
        
        if language is None:
            detected_text = language_detector.create_detected_text(text)
            language = detected_text.language
        
        tokenizer = self.get_tokenizer(language)
        return tokenizer.tokenize(text)
    
    def tokenize_sentences(self, text: str, language: Optional[LanguageInfo] = None) -> List[str]:
        """Tokenize text into sentences with automatic language detection"""
        if not text:
            return []
        
        if language is None:
            detected_text = language_detector.create_detected_text(text)
            language = detected_text.language
        
        tokenizer = self.get_tokenizer(language)
        return tokenizer.tokenize_sentences(text)
    
    def tokenize_mixed_language(self, detected_text: DetectedText) -> Dict[str, List[str]]:
        """Tokenize mixed-language text with per-segment tokenization"""
        results = {}
        
        if detected_text.segments:
            # Process each segment with its detected language
            for segment_text, segment_language in detected_text.segments:
                tokenizer = self.get_tokenizer(segment_language)
                segment_tokens = tokenizer.tokenize(segment_text)
                results[segment_language.code] = results.get(segment_language.code, [])
                results[segment_language.code].extend(segment_tokens)
        else:
            # Process as single language
            tokenizer = self.get_tokenizer(detected_text.language)
            tokens = tokenizer.tokenize(detected_text.text)
            results[detected_text.language.code] = tokens
        
        return results


# Global tokenizer instance
multilang_tokenizer = MultiLanguageTokenizer()
