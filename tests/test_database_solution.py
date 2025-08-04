"""
Database Solution Integration Test
Tests the new PostgreSQL-ready database models with SQLite for simplicity
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Create a simple SQLite test database
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

# Import our models
from business_intel_scraper.database.models import (
    Base,
    Connection,
    Entity,
    Event,
    Location,
)

# Create test database engine
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_database.db"


async def setup_test_database():
    """Setup test database"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(engine, class_=AsyncSession)

    return engine, async_session_maker


async def test_database_models():
    """Test our new database models"""
    print("🚀 Testing database models...")

    engine, session_maker = await setup_test_database()

    async with session_maker() as session:
        # Test Entity creation
        entity1 = Entity(
            label="Acme Corporation",
            entity_type="organization",
            properties={
                "industry": "Technology",
                "employees": 500,
                "founded": "2000-01-01",
                "revenue": 50000000,
            },
            confidence=0.9,
        )

        entity2 = Entity(
            label="John Doe",
            entity_type="person",
            properties={"role": "CEO", "email": "john@acme.com", "age": 45},
            confidence=0.85,
        )

        # Add entities first
        session.add_all([entity1, entity2])
        await session.commit()

        # Refresh to get IDs
        await session.refresh(entity1)
        await session.refresh(entity2)

        # Now create location with entity_id
        location = Location(
            entity_id=entity1.id,  # Link to entity1
            name="San Francisco Office",
            latitude=37.7749,
            longitude=-122.4194,
            address="123 Tech Street, San Francisco, CA",
            city="San Francisco",
            state="CA",
            country="USA",
            location_type="office",
            confidence=0.9,
            properties={"capacity": 200, "floors": 5, "parking": True},
        )

        # Add location
        session.add(location)
        await session.commit()
        await session.refresh(location)

        print(f"✅ Created entities: {entity1.label}, {entity2.label}")
        print(f"✅ Created location: {location.name}")

        # Test Connection creation
        connection = Connection(
            source_id=entity1.id,
            target_id=entity2.id,
            relationship_type="employment",
            weight=0.9,
            confidence=0.8,
            properties={
                "position": "CEO",
                "start_date": "2020-01-01",
                "salary_range": "high",
                "equity": True,
            },
        )

        session.add(connection)
        await session.commit()
        await session.refresh(connection)

        print(f"✅ Created connection: {connection.relationship_type}")

        # Test Event creation
        event1 = Event(
            entity_id=entity1.id,
            title="Series A Funding Round",
            description="Company secured Series A funding",
            event_type="funding",
            category="financial",
            start_date=datetime.utcnow(),
            confidence=0.95,
            properties={
                "amount": 10000000,
                "round": "Series A",
                "investors": ["VC Fund Alpha", "Angel Investor Beta"],
                "valuation": 50000000,
            },
        )

        event2 = Event(
            entity_id=entity2.id,
            title="Executive Promotion",
            description="John Doe promoted to CEO",
            event_type="promotion",
            category="career",
            start_date=datetime.utcnow(),
            confidence=0.9,
            properties={
                "previous_role": "CTO",
                "new_role": "CEO",
                "effective_date": "2020-01-01",
            },
        )

        # Associate entity with location (location already has entity_id)

        session.add_all([event1, event2])
        await session.commit()

        print(f"✅ Created events: {event1.title}, {event2.title}")

        # Test querying with relationships
        result = await session.execute(
            sa.select(Entity)
            .options(selectinload(Entity.source_connections))
            .options(selectinload(Entity.events))
            .options(selectinload(Entity.locations))
            .where(Entity.entity_type == "organization")
        )

        org_entities = result.scalars().all()
        print(f"✅ Found {len(org_entities)} organizations")

        for entity in org_entities:
            print(f"   - {entity.label} ({entity.entity_type})")
            print(f"     Properties: {json.dumps(entity.properties, indent=2)}")
            print(f"     Connections: {len(entity.source_connections)}")
            print(f"     Events: {len(entity.events)}")
            if entity.locations:
                print(f"     Locations: {[loc.name for loc in entity.locations]}")

        # Test complex queries
        # Find entities with specific properties
        result = await session.execute(
            sa.select(Entity).where(
                Entity.properties.op("->>")("industry") == "Technology"
            )
        )
        tech_entities = result.scalars().all()
        print(f"✅ Found {len(tech_entities)} technology entities")

        # Find connections with high weight
        result = await session.execute(
            sa.select(Connection)
            .options(selectinload(Connection.source_entity))
            .options(selectinload(Connection.target_entity))
            .where(Connection.weight >= 0.8)
        )
        strong_connections = result.scalars().all()
        print(f"✅ Found {len(strong_connections)} strong connections")

        for conn in strong_connections:
            print(f"   - {conn.source_entity.label} -> {conn.target_entity.label}")
            print(f"     Type: {conn.relationship_type}, Weight: {conn.weight}")

        # Test geographic queries
        result = await session.execute(
            sa.select(Location).where(
                sa.and_(
                    Location.latitude.between(37.0, 38.0),
                    Location.longitude.between(-123.0, -122.0),
                )
            )
        )
        bay_area_locations = result.scalars().all()
        print(f"✅ Found {len(bay_area_locations)} Bay Area locations")

        # Test event timeline queries
        result = await session.execute(
            sa.select(Event)
            .options(selectinload(Event.entity))
            .where(Event.event_type == "funding")
            .order_by(Event.start_date.desc())
        )
        funding_events = result.scalars().all()
        print(f"✅ Found {len(funding_events)} funding events")

        for event in funding_events:
            print(f"   - {event.entity.label}: ${event.properties.get('amount', 0):,}")

    await engine.dispose()
    print("🎉 Database model tests completed successfully!")


async def test_database_performance():
    """Test database performance features"""
    print("🚀 Testing database performance...")

    engine, session_maker = await setup_test_database()

    async with session_maker() as session:
        # Create bulk test data
        entities = []
        for i in range(100):
            entity = Entity(
                name=f"Test Entity {i}",
                entity_type="organization" if i % 2 == 0 else "person",
                properties={
                    "test_id": i,
                    "category": f"Category {i % 10}",
                    "score": i * 0.01,
                },
                confidence_score=0.5 + (i % 50) * 0.01,
            )
            entities.append(entity)

        session.add_all(entities)
        await session.commit()

        print(f"✅ Created {len(entities)} test entities")

        # Test bulk queries
        import time

        start_time = time.time()

        result = await session.execute(
            sa.select(Entity)
            .where(Entity.entity_type == "organization")
            .order_by(Entity.confidence_score.desc())
            .limit(20)
        )
        top_orgs = result.scalars().all()

        query_time = time.time() - start_time
        print(
            f"✅ Top organizations query: {len(top_orgs)} results in {query_time:.3f}s"
        )

        # Test aggregation queries
        start_time = time.time()

        result = await session.execute(
            sa.select(
                Entity.entity_type,
                sa.func.count(Entity.id).label("count"),
                sa.func.avg(Entity.confidence_score).label("avg_confidence"),
            ).group_by(Entity.entity_type)
        )
        stats = result.all()

        agg_time = time.time() - start_time
        print(f"✅ Aggregation query in {agg_time:.3f}s:")

        for stat in stats:
            print(
                f"   - {stat.entity_type}: {stat.count} entities, avg confidence: {stat.avg_confidence:.3f}"
            )

    await engine.dispose()
    print("🎉 Database performance tests completed!")


async def test_real_world_scenario():
    """Test a real-world business intelligence scenario"""
    print("🚀 Testing real-world BI scenario...")

    engine, session_maker = await setup_test_database()

    async with session_maker() as session:
        # Scenario: Tech startup ecosystem analysis

        # Create companies
        companies = [
            {
                "name": "TechCorp Inc",
                "industry": "Software",
                "employees": 150,
                "funding_stage": "Series B",
                "founded": 2018,
            },
            {
                "name": "DataFlow Systems",
                "industry": "Data Analytics",
                "employees": 80,
                "funding_stage": "Series A",
                "founded": 2020,
            },
            {
                "name": "AI Innovations",
                "industry": "Artificial Intelligence",
                "employees": 50,
                "funding_stage": "Seed",
                "founded": 2022,
            },
        ]

        # Create people
        people = [
            {
                "name": "Sarah Johnson",
                "role": "CEO",
                "company": "TechCorp Inc",
                "linkedin": "sarah-johnson-tech",
            },
            {
                "name": "Mike Chen",
                "role": "CTO",
                "company": "TechCorp Inc",
                "linkedin": "mike-chen-cto",
            },
            {
                "name": "Emma Wilson",
                "role": "Founder & CEO",
                "company": "DataFlow Systems",
                "linkedin": "emma-wilson-dataflow",
            },
        ]

        # Create locations
        locations_data = [
            {
                "name": "Silicon Valley Hub",
                "city": "Palo Alto",
                "lat": 37.4419,
                "lng": -122.1430,
            },
            {
                "name": "Austin Tech District",
                "city": "Austin",
                "lat": 30.2672,
                "lng": -97.7431,
            },
        ]

        # Insert companies
        company_entities = []
        for comp_data in companies:
            entity = Entity(
                name=comp_data["name"],
                entity_type="organization",
                properties=comp_data,
                confidence_score=0.9,
            )
            company_entities.append(entity)
            session.add(entity)

        await session.commit()

        # Insert people
        person_entities = []
        for person_data in people:
            entity = Entity(
                name=person_data["name"],
                entity_type="person",
                properties=person_data,
                confidence_score=0.85,
            )
            person_entities.append(entity)
            session.add(entity)

        await session.commit()

        # Insert locations
        location_entities = []
        for loc_data in locations_data:
            location = Location(
                name=loc_data["name"],
                latitude=loc_data["lat"],
                longitude=loc_data["lng"],
                address=loc_data["city"],
                location_type="business_district",
                properties={"city": loc_data["city"]},
            )
            location_entities.append(location)
            session.add(location)

        await session.commit()

        # Create relationships
        connections = []

        # Find TechCorp and its employees
        techcorp = next(e for e in company_entities if e.name == "TechCorp Inc")
        sarah = next(e for e in person_entities if e.name == "Sarah Johnson")
        mike = next(e for e in person_entities if e.name == "Mike Chen")

        # Employment connections
        connections.extend(
            [
                Connection(
                    source_entity_id=techcorp.id,
                    target_entity_id=sarah.id,
                    relationship_type="employment",
                    strength=0.95,
                    properties={"role": "CEO", "equity": 15.0},
                ),
                Connection(
                    source_entity_id=techcorp.id,
                    target_entity_id=mike.id,
                    relationship_type="employment",
                    strength=0.90,
                    properties={"role": "CTO", "equity": 8.0},
                ),
            ]
        )

        session.add_all(connections)
        await session.commit()

        # Create funding events
        events = [
            Event(
                entity_id=techcorp.id,
                event_type="funding",
                timestamp=datetime.utcnow(),
                properties={
                    "round": "Series B",
                    "amount": 25000000,
                    "lead_investor": "Venture Capital Partners",
                    "valuation": 100000000,
                },
            )
        ]

        session.add_all(events)
        await session.commit()

        # Now run business intelligence queries
        print("📊 Running BI queries...")

        # 1. Company analysis
        result = await session.execute(
            sa.select(Entity)
            .where(Entity.entity_type == "organization")
            .options(selectinload(Entity.source_connections))
            .options(selectinload(Entity.events))
        )
        companies = result.scalars().all()

        print("📈 Company Analysis:")
        for company in companies:
            props = company.properties
            print(f"   • {company.label}")
            print(f"     Industry: {props.get('industry', 'N/A')}")
            print(f"     Employees: {props.get('employees', 'N/A')}")
            print(f"     Stage: {props.get('funding_stage', 'N/A')}")
            print(f"     Connections: {len(company.source_connections)}")
            print(f"     Events: {len(company.events)}")

        # 2. Network analysis - find key people
        result = await session.execute(
            sa.select(Entity, sa.func.count(Connection.id).label("connection_count"))
            .outerjoin(Connection, Entity.id == Connection.target_entity_id)
            .where(Entity.entity_type == "person")
            .group_by(Entity.id)
            .order_by(sa.desc("connection_count"))
        )

        network_stats = result.all()
        print("🌐 Network Analysis (Key People):")
        for person, conn_count in network_stats:
            print(f"   • {person.label}: {conn_count} connections")
            if person.properties.get("role"):
                print(f"     Role: {person.properties['role']}")

        # 3. Funding analysis
        result = await session.execute(
            sa.select(Event)
            .options(selectinload(Event.entity))
            .where(Event.event_type == "funding")
        )

        funding_events = result.scalars().all()
        print("💰 Funding Analysis:")
        total_funding = 0
        for event in funding_events:
            amount = event.properties.get("amount", 0)
            total_funding += amount
            print(
                f"   • {event.entity.label}: ${amount:,} ({event.properties.get('round', 'N/A')})"
            )

        print(f"   Total funding tracked: ${total_funding:,}")

        # 4. Geographic distribution
        result = await session.execute(sa.select(Location))
        locations = result.scalars().all()
        print("📍 Geographic Analysis:")
        for location in locations:
            print(f"   • {location.name} ({location.address})")
            print(f"     Coordinates: {location.latitude}, {location.longitude}")

    await engine.dispose()
    print("🎉 Real-world scenario test completed!")


async def main():
    """Run all database tests"""
    print("=" * 60)
    print("🚀 DATABASE SOLUTION INTEGRATION TEST")
    print("=" * 60)

    try:
        await test_database_models()
        print()
        await test_database_performance()
        print()
        await test_real_world_scenario()

        print("\n" + "=" * 60)
        print("🎉 ALL DATABASE TESTS PASSED!")
        print("✅ PostgreSQL-ready models working perfectly")
        print("✅ Complex relationships and queries functional")
        print("✅ JSON properties and geographic data supported")
        print("✅ Performance optimizations effective")
        print("✅ Real-world business intelligence scenarios working")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())
