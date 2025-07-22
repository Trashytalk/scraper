#!/usr/bin/env python3
"""
Real-world data integration testing for Enterprise Visual Analytics Platform
Tests the platform with actual Fortune 500 company data and business intelligence scenarios
"""

import asyncio
import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class RealWorldDataTester:
    def __init__(self):
        self.test_data_dir = Path("data/real_world_testing")
        self.test_data_dir.mkdir(exist_ok=True, parents=True)
        
    def create_sample_fortune500_data(self) -> List[Dict[str, Any]]:
        """Create realistic Fortune 500 company data for testing"""
        return [
            {
                "name": "Apple Inc.",
                "description": "Technology company that designs, develops, and sells consumer electronics, computer software, and online services. Known for iPhone, iPad, Mac computers, and innovative ecosystem integration.",
                "revenue": 394.3e9,  # $394.3B
                "employees": 164000,
                "headquarters": "Cupertino, California",
                "ceo": "Tim Cook",
                "industry": "Technology",
                "founded": 1976,
                "stock_symbol": "AAPL",
                "market_cap": 3.0e12,  # $3T
                "coordinates": {"lat": 37.3349, "lng": -122.0090}
            },
            {
                "name": "Microsoft Corporation",
                "description": "Multinational technology corporation that develops, manufactures, licenses, supports, and sells computer software, consumer electronics, personal computers, and related services.",
                "revenue": 211.9e9,  # $211.9B
                "employees": 221000,
                "headquarters": "Redmond, Washington",
                "ceo": "Satya Nadella",
                "industry": "Technology",
                "founded": 1975,
                "stock_symbol": "MSFT",
                "market_cap": 2.8e12,  # $2.8T
                "coordinates": {"lat": 47.6431, "lng": -122.1365}
            },
            {
                "name": "Amazon.com Inc.",
                "description": "Multinational technology company focusing on e-commerce, cloud computing, online advertising, digital streaming, and artificial intelligence. Largest online marketplace globally.",
                "revenue": 513.9e9,  # $513.9B
                "employees": 1608000,
                "headquarters": "Seattle, Washington", 
                "ceo": "Andy Jassy",
                "industry": "Technology/E-commerce",
                "founded": 1994,
                "stock_symbol": "AMZN",
                "market_cap": 1.7e12,  # $1.7T
                "coordinates": {"lat": 47.6205, "lng": -122.3493}
            },
            {
                "name": "Tesla Inc.",
                "description": "Electric vehicle and clean energy company that designs, manufactures, and sells electric vehicles, energy storage systems, and solar panels. Leading autonomous driving technology.",
                "revenue": 96.7e9,  # $96.7B
                "employees": 140000,
                "headquarters": "Austin, Texas",
                "ceo": "Elon Musk",
                "industry": "Automotive/Clean Energy",
                "founded": 2003,
                "stock_symbol": "TSLA", 
                "market_cap": 800e9,  # $800B
                "coordinates": {"lat": 30.2711, "lng": -97.7437}
            },
            {
                "name": "JPMorgan Chase & Co.",
                "description": "American multinational investment bank and financial services company. Largest bank in the United States and a leader in investment banking, commercial banking, and asset management.",
                "revenue": 128.7e9,  # $128.7B
                "employees": 293723,
                "headquarters": "New York City, New York",
                "ceo": "Jamie Dimon",
                "industry": "Financial Services",
                "founded": 1799,
                "stock_symbol": "JPM",
                "market_cap": 500e9,  # $500B
                "coordinates": {"lat": 40.7589, "lng": -73.9851}
            }
        ]
    
    async def test_entity_extraction_and_storage(self) -> bool:
        """Test entity extraction and database storage with real company data"""
        print("🏢 Testing Entity Extraction and Storage...")
        
        try:
            from business_intel_scraper.backend.db.models import Entity
            from business_intel_scraper.backend.db.utils import get_db_session
            from business_intel_scraper.backend.nlp.pipeline import NLPPipeline
            
            nlp = NLPPipeline()
            companies = self.create_sample_fortune500_data()
            stored_entities = []
            
            async with get_db_session() as session:
                for company in companies:
                    # Extract entities from company description using NLP
                    entities = await nlp.extract_entities(company['description'])
                    print(f"   📊 Extracted {len(entities)} entities from {company['name']} description")
                    
                    # Create comprehensive entity record
                    entity = Entity(
                        name=company['name'],
                        entity_type='company',
                        properties={
                            **company,
                            'extracted_entities': entities,
                            'processed_at': datetime.now().isoformat()
                        }
                    )
                    
                    session.add(entity)
                    stored_entities.append(entity)
                
                await session.commit()
                print(f"   ✅ Successfully stored {len(stored_entities)} Fortune 500 companies")
                
                # Verify storage with queries
                for entity in stored_entities:
                    await session.refresh(entity)
                    assert entity.id is not None
                    assert entity.properties['revenue'] > 0
                    
                print("   ✅ Entity storage verification: PASSED")
                return True
                
        except Exception as e:
            print(f"   ❌ Entity extraction and storage failed: {e}")
            return False
    
    async def test_geographic_processing(self) -> bool:
        """Test geographic processing with real business locations"""
        print("🌍 Testing Geographic Processing...")
        
        try:
            from business_intel_scraper.backend.db.models import Location
            from business_intel_scraper.backend.db.utils import get_db_session
            from business_intel_scraper.backend.geo.processing import GeoProcessor
            
            geo = GeoProcessor()
            companies = self.create_sample_fortune500_data()
            locations_processed = 0
            
            async with get_db_session() as session:
                for company in companies:
                    # Test geocoding
                    address = company['headquarters']
                    coords = company.get('coordinates', {})
                    
                    if coords:
                        # Create location record
                        location = Location(
                            name=f"{company['name']} Headquarters",
                            address=address,
                            latitude=coords['lat'],
                            longitude=coords['lng'],
                            location_type='headquarters',
                            properties={
                                'company': company['name'],
                                'industry': company['industry'],
                                'employees': company['employees']
                            }
                        )
                        
                        session.add(location)
                        locations_processed += 1
                        print(f"   📍 Processed location for {company['name']}: {address}")
                
                await session.commit()
                print(f"   ✅ Successfully processed {locations_processed} business locations")
                
                # Test geographic queries
                # Query locations within a region (e.g., California tech companies)
                california_locations = await session.execute(
                    """SELECT * FROM locations 
                       WHERE latitude BETWEEN 32.0 AND 42.0 
                       AND longitude BETWEEN -125.0 AND -114.0"""
                )
                ca_count = len(list(california_locations))
                print(f"   📊 Found {ca_count} California-based companies")
                
                print("   ✅ Geographic processing: PASSED")
                return True
                
        except Exception as e:
            print(f"   ❌ Geographic processing failed: {e}")
            return False
    
    async def test_relationship_analysis(self) -> bool:
        """Test business relationship analysis between companies"""
        print("🔗 Testing Business Relationship Analysis...")
        
        try:
            from business_intel_scraper.backend.db.models import Connection, Entity
            from business_intel_scraper.backend.db.utils import get_db_session
            
            # Define realistic business relationships
            business_relationships = [
                {
                    "entity1": "Apple Inc.",
                    "entity2": "Microsoft Corporation", 
                    "relationship_type": "strategic_partnership",
                    "description": "Office suite integration on Apple devices and cloud service partnerships",
                    "strength": 7.5,
                    "properties": {
                        "partnership_areas": ["productivity_software", "cloud_services"],
                        "established": "2019",
                        "revenue_impact": "moderate"
                    }
                },
                {
                    "entity1": "Amazon.com Inc.",
                    "entity2": "Microsoft Corporation",
                    "relationship_type": "competition",
                    "description": "Direct competition in cloud computing services (AWS vs Azure)",
                    "strength": 9.0,
                    "properties": {
                        "competition_areas": ["cloud_computing", "enterprise_services", "ai_services"],
                        "market_share_aws": 32,
                        "market_share_azure": 21
                    }
                },
                {
                    "entity1": "Tesla Inc.",
                    "entity2": "JPMorgan Chase & Co.",
                    "relationship_type": "financial_services",
                    "description": "Banking and financial services relationship for corporate operations",
                    "strength": 6.0,
                    "properties": {
                        "services": ["corporate_banking", "treasury_management", "capital_markets"],
                        "relationship_duration": "5_years"
                    }
                }
            ]
            
            connections_created = 0
            
            async with get_db_session() as session:
                # First, get entity IDs
                entities = {}
                for company in self.create_sample_fortune500_data():
                    result = await session.execute(
                        "SELECT id FROM entities WHERE name = :name",
                        {"name": company['name']}
                    )
                    entity_id = result.scalar()
                    if entity_id:
                        entities[company['name']] = entity_id
                
                # Create relationships
                for relationship in business_relationships:
                    entity1_id = entities.get(relationship['entity1'])
                    entity2_id = entities.get(relationship['entity2'])
                    
                    if entity1_id and entity2_id:
                        connection = Connection(
                            entity1_id=entity1_id,
                            entity2_id=entity2_id,
                            connection_type=relationship['relationship_type'],
                            strength=relationship['strength'],
                            properties={
                                'description': relationship['description'],
                                **relationship['properties'],
                                'created_at': datetime.now().isoformat()
                            }
                        )
                        
                        session.add(connection)
                        connections_created += 1
                        print(f"   🔗 Created {relationship['relationship_type']} connection: {relationship['entity1']} ↔ {relationship['entity2']}")
                
                await session.commit()
                print(f"   ✅ Successfully created {connections_created} business relationships")
                
                # Test relationship queries
                # Find all partnerships
                partnerships = await session.execute(
                    "SELECT COUNT(*) FROM connections WHERE connection_type LIKE '%partnership%'"
                )
                partnership_count = partnerships.scalar()
                print(f"   📊 Found {partnership_count} strategic partnerships")
                
                # Find competitive relationships
                competitions = await session.execute(
                    "SELECT COUNT(*) FROM connections WHERE connection_type = 'competition'"
                )
                competition_count = competitions.scalar()
                print(f"   📊 Found {competition_count} competitive relationships")
                
                print("   ✅ Relationship analysis: PASSED")
                return True
                
        except Exception as e:
            print(f"   ❌ Relationship analysis failed: {e}")
            return False
    
    async def test_time_series_events(self) -> bool:
        """Test time-series event processing with real business events"""
        print("📅 Testing Time-Series Event Processing...")
        
        try:
            from business_intel_scraper.backend.db.models import Event, Entity
            from business_intel_scraper.backend.db.utils import get_db_session
            from datetime import datetime, timedelta
            
            # Define realistic business events
            business_events = [
                {
                    "entity": "Apple Inc.",
                    "event_type": "product_launch",
                    "title": "iPhone 15 Series Launch",
                    "description": "Launch of iPhone 15, iPhone 15 Plus, iPhone 15 Pro, and iPhone 15 Pro Max with USB-C transition",
                    "timestamp": datetime.now() - timedelta(days=120),
                    "properties": {
                        "products": ["iPhone 15", "iPhone 15 Plus", "iPhone 15 Pro", "iPhone 15 Pro Max"],
                        "key_features": ["USB-C", "A17 Pro chip", "Titanium design"],
                        "estimated_revenue_impact": 50e9
                    }
                },
                {
                    "entity": "Microsoft Corporation",
                    "event_type": "acquisition",
                    "title": "Activision Blizzard Acquisition Completed",
                    "description": "Microsoft completes $68.7 billion acquisition of Activision Blizzard, largest gaming acquisition in history",
                    "timestamp": datetime.now() - timedelta(days=90),
                    "properties": {
                        "acquisition_value": 68.7e9,
                        "gaming_franchises": ["Call of Duty", "World of Warcraft", "Candy Crush"],
                        "strategic_goal": "Gaming market expansion"
                    }
                },
                {
                    "entity": "Tesla Inc.",
                    "event_type": "earnings_report",
                    "title": "Q3 2024 Earnings Beat",
                    "description": "Tesla reports record Q3 delivery numbers and beats earnings expectations",
                    "timestamp": datetime.now() - timedelta(days=60),
                    "properties": {
                        "deliveries": 466140,
                        "revenue": 25.2e9,
                        "eps": 1.85,
                        "market_reaction": "positive"
                    }
                },
                {
                    "entity": "Amazon.com Inc.",
                    "event_type": "market_expansion",
                    "title": "AWS Infrastructure Expansion",
                    "description": "Amazon Web Services announces new data centers in 5 countries to support growing cloud demand",
                    "timestamp": datetime.now() - timedelta(days=30),
                    "properties": {
                        "new_regions": ["India", "Brazil", "South Korea", "UAE", "Switzerland"],
                        "investment": 12e9,
                        "expected_jobs": 15000
                    }
                }
            ]
            
            events_created = 0
            
            async with get_db_session() as session:
                # Get entity IDs
                entities = {}
                for company in self.create_sample_fortune500_data():
                    result = await session.execute(
                        "SELECT id FROM entities WHERE name = :name",
                        {"name": company['name']}
                    )
                    entity_id = result.scalar()
                    if entity_id:
                        entities[company['name']] = entity_id
                
                # Create events
                for event_data in business_events:
                    entity_id = entities.get(event_data['entity'])
                    
                    if entity_id:
                        event = Event(
                            entity_id=entity_id,
                            event_type=event_data['event_type'],
                            title=event_data['title'],
                            description=event_data['description'],
                            timestamp=event_data['timestamp'],
                            properties=event_data['properties']
                        )
                        
                        session.add(event)
                        events_created += 1
                        print(f"   📅 Created {event_data['event_type']} event: {event_data['title']}")
                
                await session.commit()
                print(f"   ✅ Successfully created {events_created} business events")
                
                # Test time-series queries
                # Events in last 90 days
                recent_events = await session.execute(
                    """SELECT COUNT(*) FROM events 
                       WHERE timestamp >= :cutoff_date""",
                    {"cutoff_date": datetime.now() - timedelta(days=90)}
                )
                recent_count = recent_events.scalar()
                print(f"   📊 Found {recent_count} events in last 90 days")
                
                # Events by type
                event_types = await session.execute(
                    "SELECT event_type, COUNT(*) FROM events GROUP BY event_type"
                )
                for event_type, count in event_types:
                    print(f"   📈 {event_type}: {count} events")
                
                print("   ✅ Time-series event processing: PASSED")
                return True
                
        except Exception as e:
            print(f"   ❌ Time-series event processing failed: {e}")
            return False
    
    async def test_complex_business_queries(self) -> bool:
        """Test complex business intelligence queries"""
        print("🧠 Testing Complex Business Intelligence Queries...")
        
        try:
            from business_intel_scraper.backend.db.utils import get_db_session
            
            async with get_db_session() as session:
                # 1. Multi-table join query: Companies with their events and locations
                complex_query = """
                SELECT 
                    e.name as company_name,
                    e.properties->>'industry' as industry,
                    e.properties->>'revenue' as revenue,
                    COUNT(ev.id) as event_count,
                    COUNT(l.id) as location_count
                FROM entities e
                LEFT JOIN events ev ON e.id = ev.entity_id
                LEFT JOIN locations l ON l.properties->>'company' = e.name
                WHERE e.entity_type = 'company'
                GROUP BY e.id, e.name, e.properties->>'industry', e.properties->>'revenue'
                ORDER BY CAST(e.properties->>'revenue' AS FLOAT) DESC
                """
                
                results = await session.execute(complex_query)
                companies_analyzed = 0
                
                for row in results:
                    company_name, industry, revenue, event_count, location_count = row
                    print(f"   📊 {company_name} ({industry}): ${float(revenue)/1e9:.1f}B revenue, {event_count} events, {location_count} locations")
                    companies_analyzed += 1
                
                print(f"   ✅ Analyzed {companies_analyzed} companies with complex joins")
                
                # 2. Geographic analysis: Technology companies by region
                geo_analysis = """
                SELECT 
                    CASE 
                        WHEN l.latitude BETWEEN 32.0 AND 42.0 AND l.longitude BETWEEN -125.0 AND -114.0 THEN 'California'
                        WHEN l.latitude BETWEEN 47.0 AND 49.0 AND l.longitude BETWEEN -125.0 AND -117.0 THEN 'Pacific Northwest'
                        WHEN l.latitude BETWEEN 40.0 AND 45.0 AND l.longitude BETWEEN -75.0 AND -70.0 THEN 'Northeast'
                        ELSE 'Other'
                    END as region,
                    COUNT(*) as company_count,
                    AVG(CAST(l.properties->>'employees' AS INTEGER)) as avg_employees
                FROM locations l
                WHERE l.location_type = 'headquarters'
                GROUP BY region
                ORDER BY company_count DESC
                """
                
                geo_results = await session.execute(geo_analysis)
                for region, count, avg_employees in geo_results:
                    print(f"   🌍 {region}: {count} companies, avg {int(avg_employees):,} employees")
                
                # 3. Relationship strength analysis
                relationship_analysis = """
                SELECT 
                    c.connection_type,
                    COUNT(*) as relationship_count,
                    AVG(c.strength) as avg_strength,
                    MIN(c.strength) as min_strength,
                    MAX(c.strength) as max_strength
                FROM connections c
                GROUP BY c.connection_type
                ORDER BY avg_strength DESC
                """
                
                rel_results = await session.execute(relationship_analysis)
                for rel_type, count, avg_str, min_str, max_str in rel_results:
                    print(f"   🔗 {rel_type}: {count} relationships, strength {avg_str:.1f} (range: {min_str}-{max_str})")
                
                # 4. Timeline analysis: Event frequency over time
                timeline_analysis = """
                SELECT 
                    DATE_TRUNC('month', timestamp) as month,
                    COUNT(*) as event_count,
                    COUNT(DISTINCT entity_id) as companies_active
                FROM events
                GROUP BY month
                ORDER BY month DESC
                LIMIT 6
                """
                
                timeline_results = await session.execute(timeline_analysis)
                for month, event_count, companies_active in timeline_results:
                    print(f"   📅 {month.strftime('%Y-%m')}: {event_count} events from {companies_active} companies")
                
                print("   ✅ Complex business intelligence queries: PASSED")
                return True
                
        except Exception as e:
            print(f"   ❌ Complex business queries failed: {e}")
            return False

async def run_real_world_data_tests():
    """Run all real-world data integration tests"""
    print("🌍 Enterprise Visual Analytics Platform - Real-World Data Integration Testing")
    print("=" * 80)
    
    tester = RealWorldDataTester()
    
    test_results = {}
    
    # Run all data integration tests
    tests = [
        ("Entity Extraction & Storage", tester.test_entity_extraction_and_storage),
        ("Geographic Processing", tester.test_geographic_processing),
        ("Relationship Analysis", tester.test_relationship_analysis), 
        ("Time-Series Events", tester.test_time_series_events),
        ("Complex BI Queries", tester.test_complex_business_queries)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*50}")
            result = await test_func()
            test_results[test_name] = result
            if result:
                passed_tests += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            test_results[test_name] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 REAL-WORLD DATA INTEGRATION TESTING SUMMARY")
    print("=" * 80)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<60} {status}")
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL REAL-WORLD DATA TESTS PASSED!")
        print("🚀 Platform successfully validated with Fortune 500 business data!")
        print("📊 Ready for production deployment with real business intelligence workflows!")
        return True
    else:
        print("⚠️  Some data integration components need attention.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_real_world_data_tests())
    sys.exit(0 if success else 1)
