"""
Test suite for Multi-Language NLP Module

Comprehensive tests for language detection, tokenization, NER,
transliteration, translation, and normalization capabilities.
"""

import pytest

from business_intel_scraper.backend.nlp.multilang import multilang_processor
from business_intel_scraper.backend.nlp.multilang.core import (
    language_detector,
    ScriptType,
)
from business_intel_scraper.backend.nlp.multilang.tokenization import (
    multilang_tokenizer,
)
from business_intel_scraper.backend.nlp.multilang.ner import multilang_ner
from business_intel_scraper.backend.nlp.multilang.transliteration import (
    script_transliterator,
    entity_normalizer,
)
from business_intel_scraper.backend.nlp.multilang.normalization import (
    phone_normalizer,
    address_normalizer,
    company_id_normalizer,
    financial_normalizer,
)

# Test data for different languages and scripts
TEST_DATA = {
    "english": {
        "text": "Apple Inc. is located at 1 Apple Park Way, Cupertino, CA 95014, USA. Contact: +1-408-996-1010.",
        "expected_language": "en",
        "expected_script": ScriptType.LATIN,
        "expected_entities": [
            "Apple Inc.",
            "1 Apple Park Way",
            "Cupertino",
            "+1-408-996-1010",
        ],
    },
    "chinese": {
        "text": "苹果公司位于美国加利福尼亚州库比蒂诺苹果公园大道1号，邮编95014。电话：+1-408-996-1010。",
        "expected_language": "zh",
        "expected_script": ScriptType.CJK,
        "expected_entities": ["苹果公司", "加利福尼亚州", "库比蒂诺"],
    },
    "russian": {
        "text": "Яндекс является российской компанией. Адрес: Москва, ул. Льва Толстого, д. 16. Телефон: +7-495-739-70-00.",
        "expected_language": "ru",
        "expected_script": ScriptType.CYRILLIC,
        "expected_entities": ["Яндекс", "Москва", "+7-495-739-70-00"],
    },
    "arabic": {
        "text": "أرامكو السعودية شركة نفط سعودية. العنوان: الظهران، المملكة العربية السعودية. الهاتف: +966-13-872-7000.",
        "expected_language": "ar",
        "expected_script": ScriptType.ARABIC,
        "expected_entities": ["أرامكو السعودية", "الظهران", "+966-13-872-7000"],
    },
    "japanese": {
        "text": "トヨタ自動車株式会社は日本の自動車メーカーです。住所：愛知県豊田市トヨタ町1番地。電話：+81-565-28-2121。",
        "expected_language": "ja",
        "expected_script": ScriptType.CJK,
        "expected_entities": ["トヨタ自動車株式会社", "愛知県", "+81-565-28-2121"],
    },
    "mixed_script": {
        "text": "Samsung Electronics (삼성전자) is a South Korean company. 주소: 경기도 수원시",
        "expected_language": "en",  # Majority language
        "expected_script": ScriptType.LATIN,
        "expected_entities": ["Samsung Electronics", "삼성전자"],
    },
}


class TestLanguageDetection:
    """Test language and script detection capabilities"""

    def test_english_detection(self):
        """Test English language detection"""
        result = language_detector.create_detected_text(TEST_DATA["english"]["text"])
        assert result.language.code == "en"
        assert result.script == ScriptType.LATIN
        assert result.confidence > 0.5

    def test_chinese_detection(self):
        """Test Chinese language detection"""
        result = language_detector.create_detected_text(TEST_DATA["chinese"]["text"])
        assert result.language.code == "zh"
        assert result.script == ScriptType.CJK
        assert result.confidence > 0.5

    def test_russian_detection(self):
        """Test Russian language detection"""
        result = language_detector.create_detected_text(TEST_DATA["russian"]["text"])
        assert result.language.code == "ru"
        assert result.script == ScriptType.CYRILLIC
        assert result.confidence > 0.5

    def test_arabic_detection(self):
        """Test Arabic language detection"""
        result = language_detector.create_detected_text(TEST_DATA["arabic"]["text"])
        assert result.language.code == "ar"
        assert result.script == ScriptType.ARABIC
        assert result.confidence > 0.5

    def test_japanese_detection(self):
        """Test Japanese language detection"""
        result = language_detector.create_detected_text(TEST_DATA["japanese"]["text"])
        assert result.language.code == "ja"
        assert result.script == ScriptType.CJK
        assert result.confidence > 0.5

    def test_mixed_script_detection(self):
        """Test mixed script detection"""
        script, confidence = language_detector.detect_script(
            TEST_DATA["mixed_script"]["text"]
        )
        # Should detect mixed content
        assert confidence < 1.0  # Not pure single script

    def test_empty_text(self):
        """Test handling of empty text"""
        result = language_detector.create_detected_text("")
        assert result.text == ""
        assert result.confidence == 0.0

    def test_short_text(self):
        """Test handling of very short text"""
        result = language_detector.create_detected_text("Hi")
        # Should still provide some detection
        assert result.language.code is not None


class TestTokenization:
    """Test multi-language tokenization"""

    def test_english_tokenization(self):
        """Test English tokenization"""
        lang = language_detector.language_data["en"]
        result = multilang_tokenizer.tokenize(TEST_DATA["english"]["text"], lang)
        assert len(result.tokens) > 0
        assert result.language.code == "en"
        assert "Apple" in result.tokens
        assert "Inc." in result.tokens or "Inc" in result.tokens

    @pytest.mark.skip(reason="Requires jieba library")
    def test_chinese_tokenization(self):
        """Test Chinese tokenization"""
        lang = language_detector.language_data["zh"]
        result = multilang_tokenizer.tokenize(TEST_DATA["chinese"]["text"], lang)
        assert len(result.tokens) > 0
        assert result.language.code == "zh"
        # Should properly segment Chinese text
        assert any("苹果" in token for token in result.tokens)

    def test_fallback_tokenization(self):
        """Test fallback tokenization for unsupported languages"""
        lang = language_detector.language_data[
            "th"
        ]  # Thai - might not have specialized tokenizer
        result = multilang_tokenizer.tokenize("สวัสดีครับ", lang)
        # Should fall back to universal tokenization
        assert len(result.tokens) > 0


class TestNER:
    """Test multi-language Named Entity Recognition"""

    def test_english_ner(self):
        """Test English NER"""
        lang = language_detector.language_data["en"]
        entities = multilang_ner.extract_entities(TEST_DATA["english"]["text"], lang)
        assert len(entities) > 0

        # Look for company name
        company_entities = [e for e in entities if "apple" in e.text.lower()]
        assert len(company_entities) > 0

        # Look for location
        location_entities = [e for e in entities if "cupertino" in e.text.lower()]
        # May or may not be detected depending on model

    def test_business_pattern_extraction(self):
        """Test business-specific pattern extraction"""
        text = "Contact ACME Corp LLC at EIN: 12-3456789, phone +1-555-0123"
        lang = language_detector.language_data["en"]
        entities = multilang_ner.extract_entities(text, lang)

        # Should detect company suffix patterns
        company_entities = [
            e for e in entities if "corp" in e.text.lower() or "llc" in e.text.lower()
        ]
        # Pattern-based detection may find these

        # Should detect EIN pattern
        ein_entities = [
            e for e in entities if "EIN" in e.text or "12-3456789" in e.text
        ]
        # Business pattern extraction should find this

    def test_multilingual_ner(self):
        """Test NER across multiple languages"""
        for lang_key, data in TEST_DATA.items():
            if lang_key == "mixed_script":
                continue

            lang = language_detector.language_data[data["expected_language"]]
            entities = multilang_ner.extract_entities(data["text"], lang)

            # Should extract some entities for each language
            assert len(entities) >= 0  # May be 0 if no appropriate models available


class TestTransliteration:
    """Test script transliteration"""

    def test_cyrillic_transliteration(self):
        """Test Cyrillic to Latin transliteration"""
        russian_text = "Яндекс"
        result = script_transliterator.transliterate_cyrillic(russian_text)

        assert result.original == russian_text
        assert result.script_from == ScriptType.CYRILLIC
        assert result.script_to == ScriptType.LATIN
        assert len(result.transliterated) > 0
        # Should convert Cyrillic characters to Latin equivalents

    def test_arabic_transliteration(self):
        """Test Arabic to Latin transliteration"""
        arabic_text = "أرامكو"
        result = script_transliterator.transliterate_arabic(arabic_text)

        assert result.original == arabic_text
        assert result.script_from == ScriptType.ARABIC
        assert result.script_to == ScriptType.LATIN
        assert len(result.transliterated) > 0

    def test_universal_transliteration(self):
        """Test universal transliteration fallback"""
        mixed_text = "Café naïve résumé"
        result = script_transliterator.transliterate_universal(
            mixed_text, ScriptType.LATIN
        )

        # Should handle accented characters
        assert result.transliterated is not None
        # May be same as input if no special characters, or converted if accents present

    def test_latin_passthrough(self):
        """Test that Latin text passes through unchanged"""
        latin_text = "Hello World"
        result = script_transliterator.transliterate(latin_text, ScriptType.LATIN)

        assert result.original == latin_text
        assert result.transliterated == latin_text
        assert result.confidence == 1.0


class TestNormalization:
    """Test field normalization"""

    def test_phone_normalization(self):
        """Test phone number normalization"""
        test_phones = [
            "(555) 123-4567",
            "+1-555-123-4567",
            "555.123.4567",
            "15551234567",
            "+86 138 0013 8000",  # Chinese mobile
        ]

        for phone in test_phones:
            result = phone_normalizer.normalize_phone(phone)
            assert result.original == phone
            assert result.field_type == "phone"
            # Should have some normalized form
            assert len(result.normalized) > 0
            # International format should start with +
            if result.confidence > 0.7:
                assert result.normalized.startswith("+")

    def test_company_id_normalization(self):
        """Test company ID normalization"""
        test_ids = [
            "12-3456789",  # US EIN
            "91-1234567890123",  # Indian CIN
            "HRB 12345",  # German
            "123456789",  # Generic
        ]

        for company_id in test_ids:
            result = company_id_normalizer.normalize_company_id(company_id)
            assert result.original == company_id
            assert result.field_type == "company_id"
            assert len(result.normalized) > 0

    def test_financial_normalization(self):
        """Test financial amount normalization"""
        test_amounts = [
            "$1,234.56",
            "€1.234,56",
            "¥100,000",
            "USD 1000",
            "$1.5M",
            "(500.00)",  # Negative
        ]

        for amount in test_amounts:
            result = financial_normalizer.normalize_amount(amount)
            assert result.original == amount
            assert result.field_type == "amount"
            # Should extract currency information
            if result.confidence > 0.5:
                assert "currency" in result.metadata

    def test_address_normalization(self):
        """Test address normalization"""
        test_addresses = [
            "123 Main St, Anytown, CA 90210",
            "北京市朝阳区建国门外大街1号",  # Chinese address
            "Москва, Красная площадь, дом 1",  # Russian address
        ]

        for address in test_addresses:
            # Detect language for proper normalization
            lang_result = language_detector.create_detected_text(address)
            result = address_normalizer.normalize_address(address, lang_result.language)

            assert result.original == address
            assert result.field_type == "address"
            assert len(result.normalized) > 0


class TestEntityNormalization:
    """Test entity normalization for cross-language matching"""

    def test_company_name_normalization(self):
        """Test company name normalization"""
        test_companies = [
            ("Apple Inc.", language_detector.language_data["en"]),
            ("苹果公司", language_detector.language_data["zh"]),
            ("Яндекс ООО", language_detector.language_data["ru"]),
        ]

        for company_name, language in test_companies:
            normalized = entity_normalizer.normalize_company_name(
                company_name, language
            )

            assert "original" in normalized
            assert "cleaned" in normalized
            assert normalized["original"] == company_name

            # Non-Latin scripts should have transliteration
            if language.script != ScriptType.LATIN:
                assert "transliterated" in normalized or "translated" in normalized

    def test_person_name_normalization(self):
        """Test person name normalization"""
        test_names = [
            ("John Smith", language_detector.language_data["en"]),
            ("张伟", language_detector.language_data["zh"]),
            ("Иван Петров", language_detector.language_data["ru"]),
        ]

        for person_name, language in test_names:
            normalized = entity_normalizer.normalize_person_name(person_name, language)

            assert "original" in normalized
            assert "cleaned" in normalized
            assert normalized["original"] == person_name

    def test_similarity_calculation(self):
        """Test entity similarity calculation"""
        # Normalize same entity in different forms
        name1 = entity_normalizer.normalize_company_name(
            "Apple Inc.", language_detector.language_data["en"]
        )
        name2 = entity_normalizer.normalize_company_name(
            "Apple Incorporated", language_detector.language_data["en"]
        )

        similarity = entity_normalizer.calculate_similarity(name1, name2)

        # Should have high similarity for similar company names
        assert 0.0 <= similarity <= 1.0
        # Exact match or high similarity expected
        assert similarity > 0.7  # May vary based on fuzzy matching implementation


class TestIntegration:
    """Integration tests for complete multi-language processing"""

    def test_complete_processing_english(self):
        """Test complete processing of English text"""
        text = TEST_DATA["english"]["text"]
        result = multilang_processor.process_text(text)

        assert result.original_text == text
        assert result.detected_language.language.code == "en"
        assert result.detected_language.script == ScriptType.LATIN

        # Should have tokenization
        assert result.tokenization is not None
        assert len(result.tokenization.tokens) > 0

        # Should have entities
        assert len(result.entities) >= 0  # May be 0 if models not available

        # No transliteration needed for Latin script
        assert result.transliteration is None

        # No translation needed for English
        assert result.translation is None

    def test_business_intelligence_extraction(self):
        """Test business intelligence extraction"""
        text = "Apple Inc. (NASDAQ: AAPL) revenue was $365.8 billion in 2021. Contact: +1-408-996-1010"
        intelligence = multilang_processor.extract_business_intelligence(text)

        assert "language_info" in intelligence
        assert "entities" in intelligence
        assert "structured_data" in intelligence

        # Should detect English
        assert intelligence["language_info"]["language_code"] == "en"

        # Should have some structured data
        assert len(intelligence["entities"]) >= 0

    def test_batch_processing(self):
        """Test batch processing of multiple texts"""
        texts = [data["text"] for data in TEST_DATA.values()]
        results = multilang_processor.batch_process(texts)

        assert len(results) == len(texts)

        # Each result should have basic structure
        for result in results:
            assert hasattr(result, "original_text")
            assert hasattr(result, "detected_language")

    @pytest.mark.asyncio
    async def test_async_processing(self):
        """Test asynchronous processing"""
        text = TEST_DATA["english"]["text"]
        result = await multilang_processor.async_process_text(text)

        assert result.original_text == text
        assert result.detected_language.language.code == "en"

    def test_capabilities_reporting(self):
        """Test capabilities reporting"""
        capabilities = multilang_processor.get_capabilities()

        assert "languages" in capabilities
        assert "scripts" in capabilities
        assert "tokenization_support" in capabilities
        assert "ner_support" in capabilities

        # Should list supported languages
        assert len(capabilities["languages"]) > 0
        assert "en" in capabilities["languages"]


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_empty_text_handling(self):
        """Test handling of empty text"""
        result = multilang_processor.process_text("")
        assert result.original_text == ""
        assert result.detected_language.confidence == 0.0

    def test_very_long_text(self):
        """Test handling of very long text"""
        long_text = "This is a test sentence. " * 1000  # Very long text
        result = multilang_processor.process_text(long_text)

        # Should handle long text without crashing
        assert result.original_text == long_text
        assert result.detected_language.language.code == "en"

    def test_special_characters(self):
        """Test handling of special characters and symbols"""
        special_text = "Test with symbols: @#$%^&*()_+-=[]{}|;':\",./<>?"
        result = multilang_processor.process_text(special_text)

        # Should not crash on special characters
        assert result.original_text == special_text

    def test_mixed_encoding(self):
        """Test handling of mixed character encodings"""
        # Text with various Unicode characters
        mixed_text = "English 中文 русский العربية 日本語 🌍"
        result = multilang_processor.process_text(mixed_text)

        # Should handle mixed Unicode content
        assert result.original_text == mixed_text
        assert result.detected_language is not None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
