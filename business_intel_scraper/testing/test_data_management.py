"""
Test Data Management and Fixtures
Comprehensive test data generation, fixtures, and data lifecycle management
"""

import os
import json
import yaml
import random
import string
import uuid
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Union, Generator
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import logging
from pathlib import Path
import sqlite3
import asyncio
from contextlib import contextmanager, asynccontextmanager
import pytest
import faker
import factory
from factory import fuzzy
import psycopg2
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


@dataclass
class TestDataConfig:
    """Test data configuration"""
    database_type: str = 'sqlite'  # sqlite, postgresql
    data_volume: str = 'small'  # small, medium, large
    include_historical_data: bool = True
    anonymize_data: bool = True
    seed_value: Optional[int] = None
    custom_generators: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataFixture:
    """Test data fixture definition"""
    name: str
    description: str
    data: Any
    dependencies: List[str] = field(default_factory=list)
    cleanup_required: bool = True
    scope: str = 'function'  # function, class, module, session


class TestDataGenerator:
    """Generate realistic test data"""
    
    def __init__(self, config: TestDataConfig):
        self.config = config
        self.fake = faker.Faker()
        if config.seed_value:
            faker.Faker.seed(config.seed_value)
            random.seed(config.seed_value)
    
    def generate_user_data(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate user test data"""
        users = []
        
        for _ in range(count):
            user = {
                'id': str(uuid.uuid4()),
                'email': self.fake.email(),
                'username': self.fake.user_name(),
                'first_name': self.fake.first_name(),
                'last_name': self.fake.last_name(),
                'date_joined': self.fake.date_time_between(start_date='-2y', end_date='now'),
                'is_active': random.choice([True, True, True, False]),  # 75% active
                'role': random.choice(['user', 'admin', 'moderator']),
                'preferences': {
                    'notifications': random.choice([True, False]),
                    'theme': random.choice(['light', 'dark']),
                    'language': random.choice(['en', 'es', 'fr', 'de'])
                },
                'profile': {
                    'bio': self.fake.text(max_nb_chars=200),
                    'avatar_url': self.fake.image_url(),
                    'website': self.fake.url() if random.random() > 0.7 else None,
                    'location': self.fake.city()
                }
            }
            
            if self.config.anonymize_data:
                user = self._anonymize_user_data(user)
            
            users.append(user)
        
        return users
    
    def generate_scraping_job_data(self, count: int = 20) -> List[Dict[str, Any]]:
        """Generate scraping job test data"""
        jobs = []
        
        statuses = ['pending', 'running', 'completed', 'failed', 'cancelled']
        priorities = ['low', 'normal', 'high', 'urgent']
        
        for _ in range(count):
            created_at = self.fake.date_time_between(start_date='-30d', end_date='now')
            status = random.choice(statuses)
            
            # Determine end time based on status
            if status in ['completed', 'failed', 'cancelled']:
                started_at = created_at + timedelta(minutes=random.randint(1, 60))
                ended_at = started_at + timedelta(minutes=random.randint(1, 180))
            elif status == 'running':
                started_at = created_at + timedelta(minutes=random.randint(1, 60))
                ended_at = None
            else:  # pending
                started_at = None
                ended_at = None
            
            job = {
                'id': str(uuid.uuid4()),
                'name': f"Scrape {self.fake.company()} Data",
                'description': self.fake.text(max_nb_chars=300),
                'target_url': self.fake.url(),
                'selector_config': {
                    'title': '.title, h1, h2',
                    'content': '.content, .description, p',
                    'price': '.price, .cost, .amount',
                    'metadata': '.meta, .info, .details'
                },
                'schedule': {
                    'type': random.choice(['once', 'daily', 'weekly', 'monthly']),
                    'interval': random.randint(1, 24) if random.random() > 0.5 else None,
                    'cron_expression': '0 */6 * * *' if random.random() > 0.8 else None
                },
                'status': status,
                'priority': random.choice(priorities),
                'created_at': created_at,
                'started_at': started_at,
                'ended_at': ended_at,
                'created_by': str(uuid.uuid4()),
                'configuration': {
                    'max_pages': random.randint(1, 100),
                    'delay_seconds': random.randint(1, 10),
                    'user_agent': self.fake.user_agent(),
                    'headers': {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5'
                    },
                    'timeout': random.randint(30, 300),
                    'retry_attempts': random.randint(1, 5)
                },
                'results_summary': {
                    'pages_scraped': random.randint(0, 50) if status == 'completed' else 0,
                    'items_extracted': random.randint(0, 1000) if status == 'completed' else 0,
                    'errors_count': random.randint(0, 5) if status in ['completed', 'failed'] else 0
                }
            }
            
            jobs.append(job)
        
        return jobs
    
    def generate_scraped_data(self, job_count: int = 5, items_per_job: int = 50) -> List[Dict[str, Any]]:
        """Generate scraped data records"""
        scraped_items = []
        
        categories = ['product', 'article', 'listing', 'profile', 'event', 'review']
        
        for job_id in range(job_count):
            job_uuid = str(uuid.uuid4())
            
            for item_id in range(items_per_job):
                item = {
                    'id': str(uuid.uuid4()),
                    'job_id': job_uuid,
                    'url': self.fake.url(),
                    'category': random.choice(categories),
                    'title': self.fake.catch_phrase(),
                    'content': self.fake.text(max_nb_chars=1000),
                    'extracted_data': self._generate_extracted_data(),
                    'metadata': {
                        'scraped_at': self.fake.date_time_between(start_date='-7d', end_date='now'),
                        'content_length': random.randint(100, 5000),
                        'response_time_ms': random.randint(200, 3000),
                        'http_status': random.choice([200, 200, 200, 404, 503]),  # Mostly 200
                        'encoding': 'utf-8',
                        'content_type': 'text/html'
                    },
                    'quality_score': round(random.uniform(0.5, 1.0), 2),
                    'processing_status': random.choice(['raw', 'processed', 'validated', 'archived']),
                    'tags': random.sample(['important', 'trending', 'featured', 'new', 'popular', 'verified'], 
                                        k=random.randint(0, 3))
                }
                
                scraped_items.append(item)
        
        return scraped_items
    
    def _generate_extracted_data(self) -> Dict[str, Any]:
        """Generate realistic extracted data"""
        data_type = random.choice(['product', 'article', 'listing', 'profile'])
        
        if data_type == 'product':
            return {
                'name': self.fake.catch_phrase(),
                'price': round(random.uniform(9.99, 999.99), 2),
                'currency': random.choice(['USD', 'EUR', 'GBP']),
                'description': self.fake.text(max_nb_chars=500),
                'brand': self.fake.company(),
                'category': random.choice(['Electronics', 'Clothing', 'Books', 'Home']),
                'in_stock': random.choice([True, False]),
                'rating': round(random.uniform(1.0, 5.0), 1),
                'reviews_count': random.randint(0, 1000),
                'images': [self.fake.image_url() for _ in range(random.randint(1, 5))]
            }
        
        elif data_type == 'article':
            return {
                'title': self.fake.catch_phrase(),
                'author': self.fake.name(),
                'published_date': self.fake.date_between(start_date='-1y', end_date='today'),
                'content': self.fake.text(max_nb_chars=2000),
                'summary': self.fake.text(max_nb_chars=200),
                'tags': random.sample(['tech', 'business', 'science', 'politics', 'sports'], 
                                    k=random.randint(1, 3)),
                'reading_time': random.randint(2, 15),
                'word_count': random.randint(500, 3000)
            }
        
        elif data_type == 'listing':
            return {
                'title': self.fake.catch_phrase(),
                'location': self.fake.address(),
                'price': round(random.uniform(50, 5000), 2),
                'condition': random.choice(['new', 'like_new', 'good', 'fair', 'poor']),
                'seller': self.fake.name(),
                'contact': self.fake.phone_number(),
                'posted_date': self.fake.date_between(start_date='-30d', end_date='today'),
                'views': random.randint(1, 500),
                'images': [self.fake.image_url() for _ in range(random.randint(1, 8))]
            }
        
        else:  # profile
            return {
                'name': self.fake.name(),
                'title': self.fake.job(),
                'company': self.fake.company(),
                'location': self.fake.city(),
                'bio': self.fake.text(max_nb_chars=300),
                'experience_years': random.randint(0, 20),
                'skills': random.sample(['Python', 'JavaScript', 'SQL', 'React', 'AWS', 'Docker'], 
                                     k=random.randint(2, 6)),
                'connections': random.randint(50, 2000),
                'profile_url': self.fake.url()
            }
    
    def _anonymize_user_data(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize sensitive user data"""
        # Replace with dummy data while maintaining structure
        user['email'] = f"test_user_{user['id'][:8]}@example.com"
        user['first_name'] = f"TestUser{random.randint(1000, 9999)}"
        user['last_name'] = f"TestLast{random.randint(1000, 9999)}"
        
        if 'profile' in user and 'bio' in user['profile']:
            user['profile']['bio'] = "Test user bio for automated testing"
        
        return user
    
    def generate_analytics_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """Generate analytics/metrics test data"""
        analytics = []
        
        base_date = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            current_date = base_date + timedelta(days=day)
            
            # Daily metrics
            daily_metrics = {
                'date': current_date.date(),
                'total_jobs': random.randint(10, 100),
                'successful_jobs': random.randint(8, 95),
                'failed_jobs': random.randint(0, 10),
                'avg_processing_time': round(random.uniform(30, 300), 2),
                'total_items_scraped': random.randint(100, 10000),
                'unique_domains': random.randint(5, 50),
                'data_quality_score': round(random.uniform(0.7, 1.0), 3),
                'storage_used_mb': round(random.uniform(100, 1000), 2),
                'api_requests': random.randint(500, 5000),
                'error_rate': round(random.uniform(0, 0.1), 4)
            }
            
            # Hourly breakdown for recent data
            if day >= days - 7:  # Last 7 days
                hourly_data = []
                for hour in range(24):
                    hour_metrics = {
                        'hour': hour,
                        'jobs_count': random.randint(0, 10),
                        'success_rate': round(random.uniform(0.8, 1.0), 3),
                        'avg_response_time': round(random.uniform(100, 2000), 2),
                        'items_per_hour': random.randint(10, 500)
                    }
                    hourly_data.append(hour_metrics)
                
                daily_metrics['hourly_breakdown'] = hourly_data
            
            analytics.append(daily_metrics)
        
        return analytics


class FactoryBoyGenerators:
    """Factory Boy factories for complex object generation"""
    
    class UserFactory(factory.Factory):
        class Meta:
            model = dict
        
        id = factory.LazyFunction(lambda: str(uuid.uuid4()))
        email = factory.Faker('email')
        username = factory.Faker('user_name')
        first_name = factory.Faker('first_name')
        last_name = factory.Faker('last_name')
        date_joined = factory.Faker('date_time_between', start_date='-2y', end_date='now')
        is_active = fuzzy.FuzzyChoice([True, False], [True, True, True, False])
        role = fuzzy.FuzzyChoice(['user', 'admin', 'moderator'])
    
    class ScrapingJobFactory(factory.Factory):
        class Meta:
            model = dict
        
        id = factory.LazyFunction(lambda: str(uuid.uuid4()))
        name = factory.Faker('catch_phrase')
        target_url = factory.Faker('url')
        status = fuzzy.FuzzyChoice(['pending', 'running', 'completed', 'failed'])
        priority = fuzzy.FuzzyChoice(['low', 'normal', 'high', 'urgent'])
        created_at = factory.Faker('date_time_between', start_date='-30d', end_date='now')
        created_by = factory.LazyFunction(lambda: str(uuid.uuid4()))
    
    class ScrapedItemFactory(factory.Factory):
        class Meta:
            model = dict
        
        id = factory.LazyFunction(lambda: str(uuid.uuid4()))
        job_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
        url = factory.Faker('url')
        title = factory.Faker('catch_phrase')
        content = factory.Faker('text', max_nb_chars=1000)
        quality_score = fuzzy.FuzzyFloat(0.5, 1.0)


class DatabaseFixtureManager:
    """Manage database fixtures and test data lifecycle"""
    
    def __init__(self, config: TestDataConfig):
        self.config = config
        self.generator = TestDataGenerator(config)
        self.temp_files = []
        self.temp_databases = []
    
    @contextmanager
    def temporary_database(self, db_type: str = 'sqlite'):
        """Create temporary database for testing"""
        if db_type == 'sqlite':
            db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
            db_path = db_file.name
            db_file.close()
            
            self.temp_files.append(db_path)
            
            try:
                # Create database and tables
                conn = sqlite3.connect(db_path)
                self._create_sqlite_schema(conn)
                conn.close()
                
                yield f"sqlite:///{db_path}"
            finally:
                if os.path.exists(db_path):
                    os.unlink(db_path)
                if db_path in self.temp_files:
                    self.temp_files.remove(db_path)
        
        elif db_type == 'postgresql':
            # For PostgreSQL, assume test database exists
            test_db_url = os.getenv('TEST_DATABASE_URL', 'postgresql://testuser:testpass@localhost:5433/testdb')
            yield test_db_url
    
    def _create_sqlite_schema(self, conn: sqlite3.Connection):
        """Create test database schema"""
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                first_name TEXT,
                last_name TEXT,
                date_joined TIMESTAMP,
                is_active BOOLEAN,
                role TEXT,
                preferences TEXT,
                profile TEXT
            )
        ''')
        
        # Scraping jobs table
        cursor.execute('''
            CREATE TABLE scraping_jobs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                target_url TEXT NOT NULL,
                selector_config TEXT,
                schedule TEXT,
                status TEXT,
                priority TEXT,
                created_at TIMESTAMP,
                started_at TIMESTAMP,
                ended_at TIMESTAMP,
                created_by TEXT,
                configuration TEXT,
                results_summary TEXT
            )
        ''')
        
        # Scraped items table
        cursor.execute('''
            CREATE TABLE scraped_items (
                id TEXT PRIMARY KEY,
                job_id TEXT,
                url TEXT,
                category TEXT,
                title TEXT,
                content TEXT,
                extracted_data TEXT,
                metadata TEXT,
                quality_score REAL,
                processing_status TEXT,
                tags TEXT
            )
        ''')
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                total_jobs INTEGER,
                successful_jobs INTEGER,
                failed_jobs INTEGER,
                avg_processing_time REAL,
                total_items_scraped INTEGER,
                unique_domains INTEGER,
                data_quality_score REAL,
                storage_used_mb REAL,
                api_requests INTEGER,
                error_rate REAL,
                hourly_breakdown TEXT
            )
        ''')
        
        conn.commit()
    
    def populate_test_database(self, db_url: str, volume: str = 'small'):
        """Populate database with test data"""
        
        volume_configs = {
            'small': {'users': 10, 'jobs': 20, 'items': 100, 'analytics_days': 7},
            'medium': {'users': 100, 'jobs': 200, 'items': 1000, 'analytics_days': 30},
            'large': {'users': 1000, 'jobs': 2000, 'items': 10000, 'analytics_days': 90}
        }
        
        config = volume_configs.get(volume, volume_configs['small'])
        
        if db_url.startswith('sqlite'):
            self._populate_sqlite(db_url, config)
        elif db_url.startswith('postgresql'):
            self._populate_postgresql(db_url, config)
    
    def _populate_sqlite(self, db_url: str, config: Dict[str, int]):
        """Populate SQLite database"""
        db_path = db_url.replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Insert users
            users = self.generator.generate_user_data(config['users'])
            for user in users:
                cursor.execute('''
                    INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user['id'], user['email'], user['username'],
                    user['first_name'], user['last_name'], user['date_joined'],
                    user['is_active'], user['role'],
                    json.dumps(user['preferences']), json.dumps(user['profile'])
                ))
            
            # Insert scraping jobs
            jobs = self.generator.generate_scraping_job_data(config['jobs'])
            for job in jobs:
                cursor.execute('''
                    INSERT INTO scraping_jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job['id'], job['name'], job['description'],
                    job['target_url'], json.dumps(job['selector_config']),
                    json.dumps(job['schedule']), job['status'], job['priority'],
                    job['created_at'], job['started_at'], job['ended_at'],
                    job['created_by'], json.dumps(job['configuration']),
                    json.dumps(job['results_summary'])
                ))
            
            # Insert scraped items
            items = self.generator.generate_scraped_data(
                job_count=min(config['jobs'], 20),
                items_per_job=config['items'] // min(config['jobs'], 20)
            )
            for item in items:
                cursor.execute('''
                    INSERT INTO scraped_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item['id'], item['job_id'], item['url'], item['category'],
                    item['title'], item['content'],
                    json.dumps(item['extracted_data']),
                    json.dumps(item['metadata']), item['quality_score'],
                    item['processing_status'], json.dumps(item['tags'])
                ))
            
            # Insert analytics data
            analytics = self.generator.generate_analytics_data(config['analytics_days'])
            for record in analytics:
                hourly_data = record.pop('hourly_breakdown', None)
                cursor.execute('''
                    INSERT INTO analytics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    None, record['date'], record['total_jobs'],
                    record['successful_jobs'], record['failed_jobs'],
                    record['avg_processing_time'], record['total_items_scraped'],
                    record['unique_domains'], record['data_quality_score'],
                    record['storage_used_mb'], record['api_requests'],
                    record['error_rate'], json.dumps(hourly_data) if hourly_data else None
                ))
            
            conn.commit()
            logger.info(f"Populated SQLite database with {len(users)} users, {len(jobs)} jobs, {len(items)} items")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to populate SQLite database: {e}")
            raise
        finally:
            conn.close()
    
    def cleanup(self):
        """Clean up temporary files and databases"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_file}: {e}")
        
        self.temp_files.clear()


class PytestFixtures:
    """Pytest fixtures for test data management"""
    
    @pytest.fixture(scope='session')
    def test_data_config():
        """Test data configuration fixture"""
        return TestDataConfig(
            database_type='sqlite',
            data_volume='small',
            include_historical_data=True,
            anonymize_data=True,
            seed_value=12345
        )
    
    @pytest.fixture(scope='session')
    def test_database(test_data_config):
        """Test database fixture"""
        manager = DatabaseFixtureManager(test_data_config)
        
        with manager.temporary_database('sqlite') as db_url:
            manager.populate_test_database(db_url, test_data_config.data_volume)
            yield db_url
    
    @pytest.fixture(scope='function')
    def test_users(test_data_config):
        """Generate test users"""
        generator = TestDataGenerator(test_data_config)
        return generator.generate_user_data(5)
    
    @pytest.fixture(scope='function')
    def test_scraping_jobs(test_data_config):
        """Generate test scraping jobs"""
        generator = TestDataGenerator(test_data_config)
        return generator.generate_scraping_job_data(10)
    
    @pytest.fixture(scope='function')
    def test_scraped_items(test_data_config):
        """Generate test scraped items"""
        generator = TestDataGenerator(test_data_config)
        return generator.generate_scraped_data(job_count=3, items_per_job=20)
    
    @pytest.fixture(scope='function')
    def mock_web_responses():
        """Mock web responses for testing"""
        return {
            'success_response': {
                'status_code': 200,
                'content': '''
                <html>
                    <head><title>Test Page</title></head>
                    <body>
                        <h1 class="title">Test Article Title</h1>
                        <div class="content">This is test content for scraping.</div>
                        <span class="price">$99.99</span>
                        <div class="meta">Published: 2024-01-01</div>
                    </body>
                </html>
                ''',
                'headers': {'content-type': 'text/html; charset=utf-8'}
            },
            'error_response': {
                'status_code': 404,
                'content': '<html><body>Page not found</body></html>',
                'headers': {'content-type': 'text/html'}
            },
            'timeout_response': {
                'status_code': 408,
                'content': '',
                'headers': {}
            }
        }


# Example usage in tests
class ExampleTestUsage:
    """Example of how to use test data fixtures"""
    
    def test_user_creation(self, test_users):
        """Example test using user fixtures"""
        assert len(test_users) == 5
        assert all('id' in user for user in test_users)
        assert all('@' in user['email'] for user in test_users)
    
    def test_scraping_job_processing(self, test_scraping_jobs):
        """Example test using scraping job fixtures"""
        pending_jobs = [job for job in test_scraping_jobs if job['status'] == 'pending']
        assert len(pending_jobs) >= 0
        
        for job in test_scraping_jobs:
            assert 'target_url' in job
            assert job['status'] in ['pending', 'running', 'completed', 'failed', 'cancelled']
    
    def test_data_quality_metrics(self, test_scraped_items):
        """Example test using scraped item fixtures"""
        quality_scores = [item['quality_score'] for item in test_scraped_items]
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        assert 0.5 <= avg_quality <= 1.0
        assert all(0 <= score <= 1 for score in quality_scores)
    
    def test_database_operations(self, test_database):
        """Example test using database fixture"""
        # Database operations using the test database URL
        assert test_database.startswith('sqlite:///')
        
        # Example: Query users from test database
        import sqlite3
        db_path = test_database.replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        assert user_count > 0
        
        conn.close()


if __name__ == "__main__":
    # Generate sample test data
    config = TestDataConfig(
        database_type='sqlite',
        data_volume='medium',
        include_historical_data=True,
        anonymize_data=True,
        seed_value=42
    )
    
    generator = TestDataGenerator(config)
    
    # Generate and save sample data
    users = generator.generate_user_data(20)
    jobs = generator.generate_scraping_job_data(50)
    items = generator.generate_scraped_data(job_count=10, items_per_job=100)
    analytics = generator.generate_analytics_data(30)
    
    # Save to files for inspection
    with open('sample_test_users.json', 'w') as f:
        json.dump(users, f, indent=2, default=str)
    
    with open('sample_test_jobs.json', 'w') as f:
        json.dump(jobs, f, indent=2, default=str)
    
    logger.info("Sample test data generated and saved to files")
    logger.info(f"Generated: {len(users)} users, {len(jobs)} jobs, {len(items)} items, {len(analytics)} analytics records")
