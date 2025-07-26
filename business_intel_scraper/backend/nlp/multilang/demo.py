#!/usr/bin/env python3
"""
Multi-Language NLP Integration Demo

Demonstrates the complete multi-language NLP system for business intelligence.
Run this script to test all components with sample data.
"""

import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print("=" * 60)


def print_subsection(title: str):
    """Print formatted subsection header"""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print("-" * 40)


def main():
    """Main demonstration function"""
    print_section("Multi-Language NLP System Demo")

    # Sample texts in different languages
    sample_texts = {
        "English": "Apple Inc. is located at 1 Apple Park Way, Cupertino, CA 95014, USA. Revenue: $365.8B. Contact: +1-408-996-1010.",
        "Chinese": "苹果公司位于美国加利福尼亚州库比蒂诺苹果公园大道1号，邮编95014。营收3658亿美元。电话：+1-408-996-1010。",
        "Russian": "Яндекс является российской компанией. Адрес: Москва, ул. Льва Толстого, д. 16. Доход: 280 млрд руб. Телефон: +7-495-739-70-00.",
        "Arabic": "أرامكو السعودية شركة نفط سعودية. العنوان: الظهران، المملكة العربية السعودية. الدخل: 400 مليار دولار. الهاتف: +966-13-872-7000.",
        "Japanese": "トヨタ自動車株式会社は日本の自動車メーカーです。住所：愛知県豊田市トヨタ町1番地。売上：30兆円。電話：+81-565-28-2121。",
        "Spanish": "Banco Santander tiene sede en Madrid, España. Dirección: Paseo de la Castellana 24. Ingresos: €50.2B. Teléfono: +34-91-289-0000.",
        "German": "SAP SE hat ihren Sitz in Weinheim, Deutschland. Adresse: Dietmar-Hopp-Allee 16. Umsatz: €27.8B. Telefon: +49-6227-7-47474.",
        "French": "Total SE est une compagnie française. Adresse: 2 Place Jean Millier, La Défense. Chiffre d'affaires: €140B. Téléphone: +33-1-47-44-45-46.",
    }

    try:
        # Import the multi-language processor
        try:
            from business_intel_scraper.backend.nlp.multilang import multilang_processor

            HAS_MULTILANG = True
        except ImportError as e:
            logger.warning(f"Multi-language processor not available: {e}")
            HAS_MULTILANG = False

        if not HAS_MULTILANG:
            print("❌ Multi-language processor not available")
            print("Please install dependencies: pip install -r requirements.txt")
            return

        # Test 1: Language Detection
        print_section("1. Language Detection Test")

        for lang_name, text in sample_texts.items():
            try:
                detected = multilang_processor.detector.create_detected_text(text)
                print(
                    f"🔍 {lang_name:10} → {detected.language.name:15} "
                    f"({detected.language.code}) "
                    f"Script: {detected.script.value:10} "
                    f"Confidence: {detected.confidence:.2f}"
                )
            except Exception as e:
                print(f"❌ {lang_name:10} → Error: {e}")

        # Test 2: Complete Processing
        print_section("2. Complete Multi-Language Processing")

        test_text = sample_texts["English"]  # Start with English
        print(f"Processing: {test_text[:80]}...")

        try:
            result = multilang_processor.process_text(
                test_text,
                include_transliteration=True,
                include_translation=False,  # Skip translation for demo
                include_normalization=True,
            )

            print(
                f"✅ Language: {result.detected_language.language.name} ({result.detected_language.confidence:.2f})"
            )
            print(f"✅ Script: {result.detected_language.script.value}")

            if result.tokenization:
                print(f"✅ Tokens: {len(result.tokenization.tokens)} tokens")
                print(f"   Sample: {result.tokenization.tokens[:5]}...")

            if result.entities:
                print(f"✅ Entities: {len(result.entities)} found")
                for entity in result.entities[:3]:  # Show first 3
                    entity_type = (
                        entity.entity_type.value
                        if hasattr(entity.entity_type, "value")
                        else str(entity.entity_type)
                    )
                    print(
                        f"   - {entity_type}: '{entity.text}' (conf: {entity.confidence:.2f})"
                    )

            if result.normalized_entities:
                print(
                    f"✅ Normalized entities: {len(result.normalized_entities)} types"
                )
                for entity_type, norm_list in result.normalized_entities.items():
                    print(f"   - {entity_type}: {len(norm_list)} items")

        except Exception as e:
            print(f"❌ Processing failed: {e}")

        # Test 3: Business Intelligence Extraction
        print_section("3. Business Intelligence Extraction")

        try:
            intelligence = multilang_processor.extract_business_intelligence(test_text)

            print("📊 Language Information:")
            lang_info = intelligence["language_info"]
            print(
                f"   Language: {lang_info['detected_language']} ({lang_info['language_code']})"
            )
            print(f"   Script: {lang_info['script']}")
            print(f"   Confidence: {lang_info['confidence']:.2f}")

            print("📊 Extracted Entities:")
            entities = intelligence["entities"]
            for entity_type, entity_list in entities.items():
                print(f"   {entity_type}: {len(entity_list)} items")
                for entity in entity_list[:2]:  # Show first 2 of each type
                    print(
                        f"     - '{entity['text']}' (conf: {entity['confidence']:.2f})"
                    )

            print("📊 Structured Data:")
            structured = intelligence["structured_data"]
            for data_type, data_list in structured.items():
                print(f"   {data_type}: {len(data_list)} items")
                for item in data_list[:1]:  # Show first item of each type
                    print(f"     - Original: '{item['original']}'")
                    print(f"     - Normalized: '{item['normalized']}'")

        except Exception as e:
            print(f"❌ Business intelligence extraction failed: {e}")

        # Test 4: Normalization Demo
        print_section("4. Field Normalization Demo")

        normalization_tests = [
            ("Phone", "+1-408-996-1010", "phone"),
            ("Phone", "(555) 123-4567", "phone"),
            ("Amount", "$365.8 billion", "financial"),
            ("Amount", "€1,234.56", "financial"),
            ("Address", "1 Apple Park Way, Cupertino, CA 95014", "address"),
            ("Company ID", "12-3456789", "company_id"),
            ("Date", "2023-12-25", "date"),
        ]

        for test_name, test_value, field_type in normalization_tests:
            try:
                if field_type == "phone":
                    from business_intel_scraper.backend.nlp.multilang.normalization import (
                        phone_normalizer,
                    )

                    result = phone_normalizer.normalize_phone(test_value)
                elif field_type == "financial":
                    from business_intel_scraper.backend.nlp.multilang.normalization import (
                        financial_normalizer,
                    )

                    result = financial_normalizer.normalize_amount(test_value)
                elif field_type == "address":
                    from business_intel_scraper.backend.nlp.multilang.normalization import (
                        address_normalizer,
                    )

                    lang = multilang_processor.detector.language_data["en"]
                    result = address_normalizer.normalize_address(test_value, lang)
                elif field_type == "company_id":
                    from business_intel_scraper.backend.nlp.multilang.normalization import (
                        company_id_normalizer,
                    )

                    result = company_id_normalizer.normalize_company_id(test_value)
                elif field_type == "date":
                    from business_intel_scraper.backend.nlp.multilang.normalization import (
                        date_normalizer,
                    )

                    lang = multilang_processor.detector.language_data["en"]
                    result = date_normalizer.normalize_date(test_value, lang)
                else:
                    continue

                print(
                    f"🔧 {test_name:12} '{test_value}' → '{result.normalized}' "
                    f"(conf: {result.confidence:.2f})"
                )

            except Exception as e:
                print(f"❌ {test_name:12} normalization failed: {e}")

        # Test 5: Cross-Language Entity Matching
        print_section("5. Cross-Language Entity Matching")

        try:
            from business_intel_scraper.backend.nlp.multilang.transliteration import (
                entity_normalizer,
            )

            # Test company name matching across languages
            companies = [
                ("Apple Inc.", multilang_processor.detector.language_data["en"]),
                ("苹果公司", multilang_processor.detector.language_data["zh"]),
                (
                    "Samsung Electronics",
                    multilang_processor.detector.language_data["en"],
                ),
                (
                    "삼성전자",
                    multilang_processor.detector.language_data.get(
                        "ko", multilang_processor.detector.language_data["en"]
                    ),
                ),
            ]

            normalized_companies = []
            for company_name, language in companies:
                try:
                    normalized = entity_normalizer.normalize_company_name(
                        company_name, language
                    )
                    normalized_companies.append((company_name, normalized))

                    print(f"🏢 {company_name:20} ({language.code}):")
                    print(f"   Original: {normalized.get('original', 'N/A')}")
                    print(f"   Cleaned: {normalized.get('cleaned', 'N/A')}")
                    if "transliterated" in normalized:
                        print(f"   Transliterated: {normalized['transliterated']}")
                    if "translated" in normalized:
                        print(f"   Translated: {normalized['translated']}")

                except Exception as e:
                    print(f"❌ Failed to normalize {company_name}: {e}")

            # Calculate similarities
            if len(normalized_companies) >= 2:
                print("\n🔗 Similarity Scores:")
                for i in range(len(normalized_companies)):
                    for j in range(i + 1, len(normalized_companies)):
                        try:
                            name1, norm1 = normalized_companies[i]
                            name2, norm2 = normalized_companies[j]
                            similarity = entity_normalizer.calculate_similarity(
                                norm1, norm2
                            )
                            print(f"   {name1} ↔ {name2}: {similarity:.3f}")
                        except Exception as e:
                            print(f"❌ Similarity calculation failed: {e}")

        except Exception as e:
            print(f"❌ Cross-language matching failed: {e}")

        # Test 6: Batch Processing
        print_section("6. Batch Processing Demo")

        try:
            # Process multiple texts
            batch_texts = list(sample_texts.values())[:3]  # First 3 texts
            print(f"Processing {len(batch_texts)} texts in batch...")

            results = multilang_processor.batch_process(
                batch_texts,
                include_translation=False,
                include_normalization=False,  # Skip for faster demo
            )

            for i, result in enumerate(results):
                if hasattr(result, "detected_language"):
                    print(
                        f"📝 Text {i+1}: {result.detected_language.language.name} "
                        f"({len(result.entities)} entities)"
                    )
                else:
                    print(f"❌ Text {i+1}: Processing failed")

        except Exception as e:
            print(f"❌ Batch processing failed: {e}")

        # Test 7: Capabilities Report
        print_section("7. System Capabilities")

        try:
            capabilities = multilang_processor.get_capabilities()

            print(f"🌍 Supported Languages: {len(capabilities['languages'])}")
            print(f"   Languages: {', '.join(capabilities['languages'][:10])}...")

            print(f"📝 Scripts: {', '.join(capabilities['scripts'])}")

            tokenization = capabilities.get("tokenization_support", {})
            print(f"🔤 Tokenization: {len(tokenization)} language-specific tokenizers")

            ner = capabilities.get("ner_support", {})
            print("🏷️  NER Support:")
            if "spacy" in ner:
                print(f"   spaCy: {len(ner['spacy'])} languages")
            if "transformers" in ner:
                print(f"   Transformers: {', '.join(ner['transformers'])}")

            transliteration = capabilities.get("transliteration_support", {})
            if transliteration.get("icu_available"):
                print("🔤 Transliteration: ICU available")
            print(
                f"   Supported scripts: {', '.join(transliteration.get('supported_scripts', []))}"
            )

            translation = capabilities.get("translation_support", {})
            if translation.get("google_available"):
                print("🌐 Translation: Google Translate available")
            marian_models = translation.get("marian_models", [])
            if marian_models:
                print(f"   Offline models: {len(marian_models)} language pairs")

            normalization = capabilities.get("normalization_support", {})
            supported_fields = [
                field for field, available in normalization.items() if available
            ]
            print(f"🔧 Normalization: {', '.join(supported_fields)}")

        except Exception as e:
            print(f"❌ Capabilities report failed: {e}")

        # Summary
        print_section("Demo Complete")
        print("✅ Multi-Language NLP system demonstration completed!")
        print("\n📋 Summary:")
        print("   - Language detection across multiple scripts")
        print("   - Tokenization with language-specific algorithms")
        print("   - Multi-language Named Entity Recognition")
        print("   - Script transliteration and translation")
        print("   - Field normalization and standardization")
        print("   - Cross-language entity matching")
        print("   - Batch and asynchronous processing")
        print("\n🚀 The system is ready for business intelligence processing!")

    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        logger.exception("Demo execution failed")


async def async_demo():
    """Demonstrate async processing capabilities"""
    print_section("Async Processing Demo")

    try:
        from business_intel_scraper.backend.nlp.multilang import multilang_processor

        # Sample texts for async processing
        texts = [
            "Apple Inc. financial report",
            "Google revenue statistics",
            "Microsoft quarterly earnings",
        ]

        print("🔄 Processing texts asynchronously...")

        # Process texts asynchronously
        results = await multilang_processor.async_batch_process(texts)

        for i, result in enumerate(results):
            if hasattr(result, "detected_language"):
                print(
                    f"⚡ Async result {i+1}: {result.detected_language.language.name}"
                )
            else:
                print(f"❌ Async result {i+1}: Failed")

        print("✅ Async processing completed!")

    except Exception as e:
        print(f"❌ Async demo failed: {e}")


if __name__ == "__main__":
    # Run main demo
    main()

    # Run async demo
    print("\n" + "=" * 60)
    asyncio.run(async_demo())
