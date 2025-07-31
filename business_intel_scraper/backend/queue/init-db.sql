-- Database initialization for Queue System
-- Creates necessary tables and indexes for crawl tracking and queue management

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create crawl_urls table for tracking crawled URLs
CREATE TABLE IF NOT EXISTS crawl_urls (
    id SERIAL PRIMARY KEY,
    url VARCHAR(2048) NOT NULL,
    url_hash VARCHAR(64) NOT NULL UNIQUE,
    job_id VARCHAR(100) NOT NULL,
    domain VARCHAR(255),
    crawl_status VARCHAR(20) DEFAULT 'pending',
    response_status INTEGER,
    content_type VARCHAR(100),
    content_length BIGINT,
    crawl_time TIMESTAMP,
    parse_time TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,
    priority INTEGER DEFAULT 5,
    depth INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_crawl_urls_url_hash ON crawl_urls(url_hash);
CREATE INDEX IF NOT EXISTS idx_crawl_urls_job_id ON crawl_urls(job_id);
CREATE INDEX IF NOT EXISTS idx_crawl_urls_domain ON crawl_urls(domain);
CREATE INDEX IF NOT EXISTS idx_crawl_urls_status ON crawl_urls(crawl_status);
CREATE INDEX IF NOT EXISTS idx_crawl_urls_crawl_time ON crawl_urls(crawl_time);
CREATE INDEX IF NOT EXISTS idx_crawl_urls_priority ON crawl_urls(priority);

-- Create queue_jobs table for job tracking
CREATE TABLE IF NOT EXISTS queue_jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) NOT NULL UNIQUE,
    job_name VARCHAR(255),
    description TEXT,
    created_by VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    total_urls INTEGER DEFAULT 0,
    crawled_urls INTEGER DEFAULT 0,
    failed_urls INTEGER DEFAULT 0,
    max_depth INTEGER DEFAULT 3,
    max_pages INTEGER,
    crawl_delay FLOAT DEFAULT 1.0,
    timeout FLOAT DEFAULT 30.0,
    retry_count INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Create index on job_id
CREATE INDEX IF NOT EXISTS idx_queue_jobs_job_id ON queue_jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_queue_jobs_status ON queue_jobs(status);

-- Create queue_metrics table for monitoring
CREATE TABLE IF NOT EXISTS queue_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC,
    metric_type VARCHAR(20), -- 'counter', 'gauge', 'histogram'
    labels JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for metrics querying
CREATE INDEX IF NOT EXISTS idx_queue_metrics_name_time ON queue_metrics(metric_name, timestamp);
CREATE INDEX IF NOT EXISTS idx_queue_metrics_timestamp ON queue_metrics(timestamp);

-- Create parsed_content table for storing parsed data
CREATE TABLE IF NOT EXISTS parsed_content (
    id SERIAL PRIMARY KEY,
    url_id INTEGER REFERENCES crawl_urls(id),
    content_type VARCHAR(50), -- 'html', 'pdf', 'image', 'text'
    title TEXT,
    extracted_text TEXT,
    extracted_urls TEXT[], -- Array of discovered URLs
    metadata JSONB,
    ocr_text TEXT,
    business_data JSONB, -- Structured business information
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for parsed content
CREATE INDEX IF NOT EXISTS idx_parsed_content_url_id ON parsed_content(url_id);
CREATE INDEX IF NOT EXISTS idx_parsed_content_type ON parsed_content(content_type);
CREATE INDEX IF NOT EXISTS idx_parsed_content_created_at ON parsed_content(created_at);

-- Create queue_worker_status table for worker monitoring
CREATE TABLE IF NOT EXISTS queue_worker_status (
    id SERIAL PRIMARY KEY,
    worker_id VARCHAR(100) NOT NULL,
    worker_type VARCHAR(20) NOT NULL, -- 'crawl', 'parse'
    status VARCHAR(20) NOT NULL, -- 'active', 'idle', 'stopped', 'error'
    current_task VARCHAR(255),
    tasks_processed INTEGER DEFAULT 0,
    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT
);

-- Create unique index on worker_id
CREATE UNIQUE INDEX IF NOT EXISTS idx_queue_worker_status_worker_id ON queue_worker_status(worker_id);
CREATE INDEX IF NOT EXISTS idx_queue_worker_status_type ON queue_worker_status(worker_type);
CREATE INDEX IF NOT EXISTS idx_queue_worker_status_status ON queue_worker_status(status);
CREATE INDEX IF NOT EXISTS idx_queue_worker_status_heartbeat ON queue_worker_status(last_heartbeat);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_crawl_urls_updated_at 
    BEFORE UPDATE ON crawl_urls 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_queue_jobs_updated_at 
    BEFORE UPDATE ON queue_jobs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to generate URL hash
CREATE OR REPLACE FUNCTION generate_url_hash(input_url TEXT)
RETURNS VARCHAR(64) AS $$
BEGIN
    RETURN encode(digest(input_url, 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql;

-- Create view for queue statistics
CREATE OR REPLACE VIEW queue_statistics AS
SELECT 
    j.job_id,
    j.job_name,
    j.status as job_status,
    j.total_urls,
    j.crawled_urls,
    j.failed_urls,
    COALESCE(ROUND((j.crawled_urls::float / NULLIF(j.total_urls, 0)) * 100, 2), 0) as completion_percentage,
    COUNT(cu.id) FILTER (WHERE cu.crawl_status = 'pending') as pending_urls,
    COUNT(cu.id) FILTER (WHERE cu.crawl_status = 'crawling') as crawling_urls,
    COUNT(cu.id) FILTER (WHERE cu.crawl_status = 'completed') as completed_urls,
    COUNT(cu.id) FILTER (WHERE cu.crawl_status = 'failed') as failed_urls_detailed,
    COUNT(cu.id) FILTER (WHERE cu.crawl_status = 'retry') as retry_urls,
    j.created_at,
    j.updated_at
FROM queue_jobs j
LEFT JOIN crawl_urls cu ON j.job_id = cu.job_id
GROUP BY j.id, j.job_id, j.job_name, j.status, j.total_urls, j.crawled_urls, j.failed_urls, j.created_at, j.updated_at;

-- Create view for worker statistics
CREATE OR REPLACE VIEW worker_statistics AS
SELECT 
    worker_type,
    COUNT(*) as total_workers,
    COUNT(*) FILTER (WHERE status = 'active') as active_workers,
    COUNT(*) FILTER (WHERE status = 'idle') as idle_workers,
    COUNT(*) FILTER (WHERE status = 'stopped') as stopped_workers,
    COUNT(*) FILTER (WHERE status = 'error') as error_workers,
    SUM(tasks_processed) as total_tasks_processed,
    AVG(tasks_processed) as avg_tasks_per_worker,
    MIN(last_heartbeat) as oldest_heartbeat,
    MAX(last_heartbeat) as newest_heartbeat
FROM queue_worker_status
GROUP BY worker_type;

-- Insert sample data for testing (only if tables are empty)
INSERT INTO queue_jobs (job_id, job_name, description, created_by, status, max_depth, max_pages, crawl_delay, timeout, retry_count)
SELECT 'sample-job-001', 'Sample Crawl Job', 'A sample job for testing the queue system', 'system', 'active', 3, 1000, 1.0, 30.0, 3
WHERE NOT EXISTS (SELECT 1 FROM queue_jobs WHERE job_id = 'sample-job-001');

-- Create materialized view for performance metrics (refreshed periodically)
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_crawl_stats AS
SELECT 
    DATE(crawl_time) as crawl_date,
    COUNT(*) as total_crawls,
    COUNT(*) FILTER (WHERE crawl_status = 'completed') as successful_crawls,
    COUNT(*) FILTER (WHERE crawl_status = 'failed') as failed_crawls,
    AVG(content_length) as avg_content_length,
    AVG(EXTRACT(EPOCH FROM (parse_time - crawl_time))) as avg_parse_time_seconds
FROM crawl_urls 
WHERE crawl_time IS NOT NULL
GROUP BY DATE(crawl_time)
ORDER BY crawl_date DESC;

-- Create index on materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_daily_crawl_stats_date ON daily_crawl_stats(crawl_date);

-- Create function to refresh materialized view
CREATE OR REPLACE FUNCTION refresh_daily_stats()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY daily_crawl_stats;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed for your security requirements)
-- These are basic permissions for the application user
-- In production, create specific users with limited permissions

-- GRANT USAGE ON SCHEMA public TO app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Success message
SELECT 'Queue system database initialized successfully!' as message;
