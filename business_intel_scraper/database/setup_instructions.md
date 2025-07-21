# Database Setup and Configuration

## PostgreSQL Installation and Setup

### Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Database Configuration
```sql
-- Connect to PostgreSQL as superuser
sudo -u postgres psql

-- Create database and user
CREATE DATABASE visual_analytics;
CREATE USER va_user WITH PASSWORD 'secure_password_123';
GRANT ALL PRIVILEGES ON DATABASE visual_analytics TO va_user;

-- Exit PostgreSQL
\q
```

### Python Dependencies
```bash
pip install psycopg2-binary SQLAlchemy alembic asyncpg
```
