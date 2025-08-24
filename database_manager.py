#!/usr/bin/env python3
"""
Database Management and Job Cleanup Tool
Fixes stuck jobs and provides database management capabilities
"""

import sqlite3
import json
from datetime import datetime, timedelta


def fix_stuck_jobs():
    """Fix jobs that are stuck in running state"""
    print("🔧 Fixing Stuck Jobs")
    print("=" * 50)
    
    conn = sqlite3.connect('/home/homebrew/scraper/data/scraper.db')
    cursor = conn.cursor()
    
    # Find jobs that have been running for more than 1 hour
    cutoff_time = datetime.now() - timedelta(hours=1)
    cutoff_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("""
        SELECT id, name, type, started_at 
        FROM jobs 
        WHERE status = 'running' 
        AND started_at < ? 
        ORDER BY started_at
    """, (cutoff_str,))
    
    stuck_jobs = cursor.fetchall()
    
    if not stuck_jobs:
        print("✅ No stuck jobs found")
        conn.close()
        return
    
    print(f"Found {len(stuck_jobs)} stuck jobs:")
    for job_id, name, job_type, started_at in stuck_jobs:
        print(f"  📋 Job {job_id}: {name} ({job_type}) - Started: {started_at}")
    
    # Update stuck jobs to failed status
    job_ids = [str(job[0]) for job in stuck_jobs]
    placeholders = ','.join(['?' for _ in job_ids])
    
    cursor.execute(f"""
        UPDATE jobs 
        SET status = 'failed', 
            completed_at = ?, 
            error_message = 'Job terminated - exceeded maximum runtime'
        WHERE id IN ({placeholders})
    """, [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] + job_ids)
    
    print(f"✅ Updated {cursor.rowcount} stuck jobs to 'failed' status")
    
    conn.commit()
    conn.close()


def get_database_stats():
    """Get comprehensive database statistics"""
    print("\n📊 Database Statistics")
    print("=" * 50)
    
    conn = sqlite3.connect('/home/homebrew/scraper/data/scraper.db')
    cursor = conn.cursor()
    
    # Jobs statistics
    cursor.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
    job_stats = cursor.fetchall()
    print("Jobs by status:")
    for status, count in job_stats:
        print(f"  📋 {status}: {count}")
    
    # Total results
    cursor.execute("SELECT COUNT(*) FROM job_results")
    total_results = cursor.fetchone()[0]
    print(f"\n📊 Total job results: {total_results}")
    
    # Users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    print(f"👥 Total users: {total_users}")
    
    # Database size
    cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
    db_size = cursor.fetchone()[0]
    print(f"💾 Database size: {db_size / (1024*1024):.2f} MB")
    
    # Recent activity
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE created_at > datetime('now', '-24 hours')")
    recent_jobs = cursor.fetchone()[0]
    print(f"📅 Jobs created in last 24h: {recent_jobs}")
    
    # Centralized data
    cursor.execute("SELECT COUNT(*) FROM centralized_data")
    centralized_count = cursor.fetchone()[0]
    print(f"🗄️ Centralized data entries: {centralized_count}")
    
    conn.close()


def cleanup_old_data():
    """Clean up old failed jobs and orphaned data"""
    print("\n🧹 Cleaning Up Old Data")
    print("=" * 50)
    
    conn = sqlite3.connect('/home/homebrew/scraper/data/scraper.db')
    cursor = conn.cursor()
    
    # Remove failed jobs older than 7 days
    cutoff_date = datetime.now() - timedelta(days=7)
    cutoff_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
    
    # Get failed jobs to delete
    cursor.execute("""
        SELECT id FROM jobs 
        WHERE status = 'failed' 
        AND completed_at < ?
    """, (cutoff_str,))
    
    old_failed_jobs = [row[0] for row in cursor.fetchall()]
    
    if old_failed_jobs:
        print(f"🗑️ Removing {len(old_failed_jobs)} old failed jobs...")
        
        # Delete job results first
        placeholders = ','.join(['?' for _ in old_failed_jobs])
        cursor.execute(f"DELETE FROM job_results WHERE job_id IN ({placeholders})", old_failed_jobs)
        results_deleted = cursor.rowcount
        
        # Delete jobs
        cursor.execute(f"DELETE FROM jobs WHERE id IN ({placeholders})", old_failed_jobs)
        jobs_deleted = cursor.rowcount
        
        print(f"✅ Deleted {jobs_deleted} old failed jobs and {results_deleted} results")
    else:
        print("✅ No old failed jobs to clean up")
    
    # Clean up orphaned job results
    cursor.execute("""
        DELETE FROM job_results 
        WHERE job_id NOT IN (SELECT id FROM jobs)
    """)
    orphaned_results = cursor.rowcount
    
    if orphaned_results > 0:
        print(f"🗑️ Removed {orphaned_results} orphaned job results")
    
    conn.commit()
    conn.close()


def show_recent_errors():
    """Show recent job errors"""
    print("\n❌ Recent Job Errors")
    print("=" * 50)
    
    conn = sqlite3.connect('/home/homebrew/scraper/data/scraper.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, type, error_message, completed_at 
        FROM jobs 
        WHERE status = 'failed' 
        AND completed_at > datetime('now', '-24 hours')
        ORDER BY completed_at DESC
        LIMIT 10
    """)
    
    recent_errors = cursor.fetchall()
    
    if not recent_errors:
        print("✅ No recent errors found")
    else:
        for job_id, name, job_type, error_msg, completed_at in recent_errors:
            print(f"📋 Job {job_id}: {name} ({job_type})")
            print(f"   ⏰ Failed at: {completed_at}")
            print(f"   ❌ Error: {error_msg}")
            print()
    
    conn.close()


if __name__ == "__main__":
    print("🔧 Database Management and Job Cleanup Tool")
    print("=" * 60)
    
    # Fix stuck jobs first
    fix_stuck_jobs()
    
    # Show database statistics
    get_database_stats()
    
    # Show recent errors
    show_recent_errors()
    
    # Offer cleanup
    print("\n🧹 Cleanup Options")
    print("=" * 50)
    response = input("Do you want to clean up old failed jobs? (y/N): ")
    if response.lower() == 'y':
        cleanup_old_data()
    
    print("\n✅ Database management complete!")
