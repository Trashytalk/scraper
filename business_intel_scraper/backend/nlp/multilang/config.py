"""
Multi-Language NLP Configuration

Configuration settings for language detection, processing,
and normalization across different languages and scripts.
"""

from typing import Dict, Any
import os

# Environment-based configuration
MULTILANG_CONFIG = {
    # Language Detection Settings
    "language_detection": {
        "confidence_threshold": float(
            os.getenv("MULTILANG_CONFIDENCE_THRESHOLD", "0.7")
        ),
        "fallback_language": os.getenv("MULTILANG_FALLBACK_LANGUAGE", "en"),
        "enable_fasttext": os.getenv("MULTILANG_ENABLE_FASTTEXT", "false").lower()
        == "true",
        "enable_polyglot": os.getenv("MULTILANG_ENABLE_POLYGLOT", "false").lower()
        == "true",
    },
    # Script Detection Settings
    "script_detection": {
        "min_script_chars": int(os.getenv("MULTILANG_MIN_SCRIPT_CHARS", "3")),
        "mixed_script_threshold": float(
            os.getenv("MULTILANG_MIXED_SCRIPT_THRESHOLD", "0.3")
        ),
    },
    # Tokenization Settings
    "tokenization": {
        "max_token_length": int(os.getenv("MULTILANG_MAX_TOKEN_LENGTH", "100")),
        "preserve_whitespace": os.getenv(
            "MULTILANG_PRESERVE_WHITESPACE", "false"
        ).lower()
        == "true",
        "chinese_mode": os.getenv(
            "MULTILANG_CHINESE_MODE", "accurate"
        ),  # 'accurate' or 'fast'
        "japanese_mode": os.getenv(
            "MULTILANG_JAPANESE_MODE", "wakati"
        ),  # 'wakati' or 'detail'
    },
    # NER Settings
    "ner": {
        "confidence_threshold": float(os.getenv("MULTILANG_NER_CONFIDENCE", "0.6")),
        "enable_business_patterns": os.getenv(
            "MULTILANG_ENABLE_BUSINESS_PATTERNS", "true"
        ).lower()
        == "true",
        "max_entity_length": int(os.getenv("MULTILANG_MAX_ENTITY_LENGTH", "200")),
        "spacy_batch_size": int(os.getenv("MULTILANG_SPACY_BATCH_SIZE", "100")),
        "transformers_model": os.getenv(
            "MULTILANG_TRANSFORMERS_MODEL", "bert-base-multilingual-cased"
        ),
    },
    # Translation Settings
    "translation": {
        "target_language": os.getenv("MULTILANG_TARGET_LANGUAGE", "en"),
        "prefer_offline": os.getenv("MULTILANG_PREFER_OFFLINE", "false").lower()
        == "true",
        "google_translate_api_key": os.getenv("GOOGLE_TRANSLATE_API_KEY"),
        "deepl_api_key": os.getenv("DEEPL_API_KEY"),
        "max_text_length": int(os.getenv("MULTILANG_MAX_TRANSLATION_LENGTH", "5000")),
    },
    # Transliteration Settings
    "transliteration": {
        "prefer_icu": os.getenv("MULTILANG_PREFER_ICU", "true").lower() == "true",
        "fallback_to_unidecode": os.getenv(
            "MULTILANG_FALLBACK_UNIDECODE", "true"
        ).lower()
        == "true",
    },
    # Normalization Settings
    "normalization": {
        "phone_default_country": os.getenv("MULTILANG_PHONE_DEFAULT_COUNTRY", "US"),
        "address_default_country": os.getenv("MULTILANG_ADDRESS_DEFAULT_COUNTRY", "US"),
        "financial_default_currency": os.getenv(
            "MULTILANG_FINANCIAL_DEFAULT_CURRENCY", "USD"
        ),
        "date_ambiguous_format": os.getenv(
            "MULTILANG_DATE_AMBIGUOUS_FORMAT", "mdy"
        ),  # 'mdy' or 'dmy'
    },
    # Performance Settings
    "performance": {
        "cache_size": int(os.getenv("MULTILANG_CACHE_SIZE", "1000")),
        "batch_size": int(os.getenv("MULTILANG_BATCH_SIZE", "50")),
        "max_workers": int(os.getenv("MULTILANG_MAX_WORKERS", "4")),
        "timeout_seconds": int(os.getenv("MULTILANG_TIMEOUT_SECONDS", "30")),
    },
    # Logging Settings
    "logging": {
        "level": os.getenv("MULTILANG_LOG_LEVEL", "INFO"),
        "enable_debug": os.getenv("MULTILANG_ENABLE_DEBUG", "false").lower() == "true",
    },
}

# Priority languages for business intelligence
BUSINESS_PRIORITY_LANGUAGES = [
    "en",
    "zh",
    "es",
    "hi",
    "ar",
    "pt",
    "ru",
    "ja",
    "fr",
    "de",
    "ko",
    "it",
    "th",
    "tr",
    "pl",
    "nl",
    "sv",
    "da",
    "no",
    "fi",
]

# Commonly used business entity patterns
BUSINESS_ENTITY_PATTERNS = {
    "company_suffixes": {
        "en": ["Inc", "LLC", "Corp", "Ltd", "Limited", "Company", "Co"],
        "zh": ["公司", "企业", "集团", "有限公司", "股份有限公司"],
        "ja": ["株式会社", "有限会社", "合同会社", "企業"],
        "ru": ["ООО", "ЗАО", "ОАО", "ИП"],
        "de": ["GmbH", "AG", "KG", "OHG"],
        "fr": ["SARL", "SA", "SAS", "EURL"],
    },
    "registration_patterns": {
        "US": r"\d{2}-\d{7}",  # EIN format
        "CN": r"[0-9A-Z]{18}",  # USCC format
        "RU": r"\d{10,12}",  # INN format
        "IN": r"[UL]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}",  # CIN format
        "DE": r"HRB\s*\d+",  # German commercial register
        "GB": r"\d{8}",  # UK company number
    },
    "phone_patterns": {
        "international": r"\+\d{1,3}[\s\-]?\d{6,14}",
        "us": r"\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}",
        "cn": r"1[3-9]\d{9}",
        "jp": r"0\d{1,4}-\d{1,4}-\d{4}",
        "ru": r"\+?7\d{10}",
    },
}

# Default language models and their capabilities
DEFAULT_LANGUAGE_MODELS = {
    "spacy": {
        "en": "en_core_web_sm",
        "zh": "zh_core_web_sm",
        "de": "de_core_news_sm",
        "fr": "fr_core_news_sm",
        "es": "es_core_news_sm",
        "pt": "pt_core_news_sm",
        "it": "it_core_news_sm",
        "nl": "nl_core_news_sm",
        "ja": "ja_core_news_sm",
        "ru": "ru_core_news_sm",
    },
    "stanza": {
        # Stanza supports 70+ languages
        "multilingual": True,
        "auto_download": True,
    },
    "transformers": {
        "multilingual_bert": "bert-base-multilingual-cased",
        "xlm_roberta": "xlm-roberta-base",
        "mbert_ner": "dbmdz/bert-large-cased-finetuned-conll03-english",
    },
}

# Feature flags for optional components
FEATURE_FLAGS = {
    "enable_language_detection": True,
    "enable_tokenization": True,
    "enable_ner": True,
    "enable_transliteration": True,
    "enable_translation": False,  # May require API keys
    "enable_normalization": True,
    "enable_caching": True,
    "enable_batch_processing": True,
    "enable_async_processing": True,
}


def get_config() -> Dict[str, Any]:
    """Get complete multi-language configuration"""
    return {
        "settings": MULTILANG_CONFIG,
        "business_languages": BUSINESS_PRIORITY_LANGUAGES,
        "entity_patterns": BUSINESS_ENTITY_PATTERNS,
        "models": DEFAULT_LANGUAGE_MODELS,
        "features": FEATURE_FLAGS,
    }
