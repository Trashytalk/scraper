#!/usr/bin/env python3
"""
Enhanced Database Manager with GUI capabilities
Provides comprehensive database management and job control
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any


class DatabaseManager:
    def __init__(self, db_path='/home/homebrew/scraper/data/scraper.db'):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def get_all_jobs(self, limit=50, status_filter=None):
        """Get all jobs with optional status filter"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT j.id, j.name, j.type, j.status, j.created_at, j.started_at, 
                   j.completed_at, j.error_message, j.results_count,
                   u.username as created_by_name
            FROM jobs j
            LEFT JOIN users u ON j.created_by = u.id
        """
        
        params = []
        if status_filter:
            query += " WHERE j.status = ?"
            params.append(status_filter)
        
        query += " ORDER BY j.created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        jobs = []
        for row in cursor.fetchall():
            jobs.append({
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'status': row[3],
                'created_at': row[4],
                'started_at': row[5],
                'completed_at': row[6],
                'error_message': row[7],
                'results_count': row[8],
                'created_by': row[9]
            })
        
        conn.close()
        return jobs
    
    def get_job_details(self, job_id):
        """Get detailed information about a specific job"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get job info
        cursor.execute("""
            SELECT j.*, u.username as created_by_name
            FROM jobs j
            LEFT JOIN users u ON j.created_by = u.id
            WHERE j.id = ?
        """, (job_id,))
        
        job_row = cursor.fetchone()
        if not job_row:
            conn.close()
            return None
        
        job_info = dict(zip([d[0] for d in cursor.description], job_row))
        
        # Get job results
        cursor.execute("""
            SELECT COUNT(*) as total_results,
                   MIN(created_at) as first_result,
                   MAX(created_at) as last_result
            FROM job_results
            WHERE job_id = ?
        """, (job_id,))
        
        results_info = dict(zip([d[0] for d in cursor.description], cursor.fetchone()))
        
        # Get sample results
        cursor.execute("""
            SELECT data, created_at
            FROM job_results
            WHERE job_id = ?
            ORDER BY created_at DESC
            LIMIT 3
        """, (job_id,))
        
        sample_results = []
        for row in cursor.fetchall():
            try:
                data = json.loads(row[0])
                sample_results.append({
                    'data_preview': {k: str(v)[:100] + '...' if len(str(v)) > 100 else v 
                                   for k, v in list(data.items())[:5]},
                    'created_at': row[1]
                })
            except:
                sample_results.append({
                    'data_preview': {'raw': str(row[0])[:200] + '...'},
                    'created_at': row[1]
                })
        
        conn.close()
        
        return {
            'job_info': job_info,
            'results_info': results_info,
            'sample_results': sample_results
        }
    
    def terminate_job(self, job_id, reason="Manual termination"):
        """Terminate a running job"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE jobs 
            SET status = 'failed', 
                completed_at = ?, 
                error_message = ?
            WHERE id = ? AND status = 'running'
        """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), reason, job_id))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def delete_job(self, job_id):
        """Delete a job and all its results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Delete job results first
        cursor.execute("DELETE FROM job_results WHERE job_id = ?", (job_id,))
        results_deleted = cursor.rowcount
        
        # Delete job
        cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        job_deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return job_deleted > 0, results_deleted
    
    def get_database_stats(self):
        """Get comprehensive database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Job statistics
        cursor.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
        stats['jobs_by_status'] = dict(cursor.fetchall())
        
        # Total counts
        cursor.execute("SELECT COUNT(*) FROM jobs")
        stats['total_jobs'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM job_results")
        stats['total_results'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM centralized_data")
        stats['centralized_data'] = cursor.fetchone()[0]
        
        # Database size
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        stats['database_size_bytes'] = cursor.fetchone()[0]
        
        # Recent activity
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE created_at > datetime('now', '-24 hours')")
        stats['jobs_last_24h'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = 'running'")
        stats['currently_running'] = cursor.fetchone()[0]
        
        # Find stuck jobs
        cutoff_time = datetime.now() - timedelta(hours=2)
        cursor.execute("""
            SELECT COUNT(*) FROM jobs 
            WHERE status = 'running' 
            AND started_at < ?
        """, (cutoff_time.strftime('%Y-%m-%d %H:%M:%S'),))
        stats['stuck_jobs'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def cleanup_old_data(self, days_old=7, dry_run=True):
        """Clean up old failed jobs and orphaned data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
        
        # Find old failed jobs
        cursor.execute("""
            SELECT id, name FROM jobs 
            WHERE status = 'failed' 
            AND completed_at < ?
        """, (cutoff_str,))
        
        old_failed_jobs = cursor.fetchall()
        
        cleanup_report = {
            'old_failed_jobs': len(old_failed_jobs),
            'jobs_to_delete': [{'id': job[0], 'name': job[1]} for job in old_failed_jobs],
            'results_deleted': 0,
            'orphaned_results': 0
        }
        
        if not dry_run and old_failed_jobs:
            job_ids = [job[0] for job in old_failed_jobs]
            
            # Delete job results
            placeholders = ','.join(['?' for _ in job_ids])
            cursor.execute(f"DELETE FROM job_results WHERE job_id IN ({placeholders})", job_ids)
            cleanup_report['results_deleted'] = cursor.rowcount
            
            # Delete jobs
            cursor.execute(f"DELETE FROM jobs WHERE id IN ({placeholders})", job_ids)
        
        # Find orphaned job results
        cursor.execute("""
            SELECT COUNT(*) FROM job_results 
            WHERE job_id NOT IN (SELECT id FROM jobs)
        """)
        orphaned_count = cursor.fetchone()[0]
        cleanup_report['orphaned_results'] = orphaned_count
        
        if not dry_run and orphaned_count > 0:
            cursor.execute("""
                DELETE FROM job_results 
                WHERE job_id NOT IN (SELECT id FROM jobs)
            """)
        
        if not dry_run:
            conn.commit()
        
        conn.close()
        return cleanup_report


def interactive_database_manager():
    """Interactive command-line database manager"""
    db_manager = DatabaseManager()
    
    while True:
        print("\n" + "=" * 60)
        print("🗄️ DATABASE MANAGER")
        print("=" * 60)
        
        # Show quick stats
        stats = db_manager.get_database_stats()
        print(f"📊 Total Jobs: {stats['total_jobs']} | Running: {stats['currently_running']} | Stuck: {stats['stuck_jobs']}")
        print(f"📊 Total Results: {stats['total_results']} | Size: {stats['database_size_bytes']/(1024*1024):.1f}MB")
        
        print("\n📋 OPTIONS:")
        print("1. List all jobs")
        print("2. List running jobs")
        print("3. List failed jobs")
        print("4. View job details")
        print("5. Terminate running job")
        print("6. Delete job")
        print("7. Show database statistics")
        print("8. Clean up old data")
        print("9. Fix stuck jobs")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-9): ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            jobs = db_manager.get_all_jobs(50)
            print("\n📋 ALL JOBS (Last 50):")
            print("-" * 80)
            for job in jobs:
                status_emoji = {"completed": "✅", "running": "🔄", "failed": "❌", "pending": "⏳"}.get(job['status'], "❓")
                print(f"{status_emoji} {job['id']:3d} | {job['name'][:30]:30s} | {job['type']:12s} | {job['status']:10s} | {job['created_at']}")
        
        elif choice == '2':
            jobs = db_manager.get_all_jobs(50, 'running')
            print("\n🔄 RUNNING JOBS:")
            print("-" * 80)
            for job in jobs:
                print(f"🔄 {job['id']:3d} | {job['name'][:30]:30s} | Started: {job['started_at']} | Results: {job['results_count']}")
        
        elif choice == '3':
            jobs = db_manager.get_all_jobs(50, 'failed')
            print("\n❌ FAILED JOBS:")
            print("-" * 80)
            for job in jobs:
                error = job['error_message'][:50] + '...' if job['error_message'] and len(job['error_message']) > 50 else job['error_message']
                print(f"❌ {job['id']:3d} | {job['name'][:30]:30s} | Error: {error}")
        
        elif choice == '4':
            job_id = input("Enter job ID: ").strip()
            if job_id.isdigit():
                details = db_manager.get_job_details(int(job_id))
                if details:
                    job = details['job_info']
                    results = details['results_info']
                    
                    print(f"\n📋 JOB {job['id']} DETAILS:")
                    print("-" * 50)
                    print(f"Name: {job['name']}")
                    print(f"Type: {job['type']}")
                    print(f"Status: {job['status']}")
                    print(f"Created: {job['created_at']} by {job['created_by_name']}")
                    print(f"Started: {job['started_at']}")
                    print(f"Completed: {job['completed_at']}")
                    if job['error_message']:
                        print(f"Error: {job['error_message']}")
                    
                    print(f"\n📊 RESULTS:")
                    print(f"Total results: {results['total_results']}")
                    print(f"First result: {results['first_result']}")
                    print(f"Last result: {results['last_result']}")
                    
                    if details['sample_results']:
                        print(f"\n📄 SAMPLE DATA:")
                        for i, sample in enumerate(details['sample_results'][:2]):
                            print(f"  Result {i+1}: {sample['data_preview']}")
                else:
                    print("❌ Job not found")
        
        elif choice == '5':
            job_id = input("Enter job ID to terminate: ").strip()
            if job_id.isdigit():
                reason = input("Enter termination reason (or press Enter for default): ").strip()
                if not reason:
                    reason = "Manual termination via database manager"
                
                if db_manager.terminate_job(int(job_id), reason):
                    print(f"✅ Job {job_id} terminated successfully")
                else:
                    print(f"❌ Job {job_id} not found or not running")
        
        elif choice == '6':
            job_id = input("Enter job ID to DELETE (this cannot be undone): ").strip()
            if job_id.isdigit():
                confirm = input(f"Are you sure you want to DELETE job {job_id}? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    job_deleted, results_deleted = db_manager.delete_job(int(job_id))
                    if job_deleted:
                        print(f"✅ Job {job_id} and {results_deleted} results deleted successfully")
                    else:
                        print(f"❌ Job {job_id} not found")
        
        elif choice == '7':
            stats = db_manager.get_database_stats()
            print("\n📊 DATABASE STATISTICS:")
            print("-" * 50)
            print(f"Total Jobs: {stats['total_jobs']}")
            print(f"Jobs by Status: {stats['jobs_by_status']}")
            print(f"Total Results: {stats['total_results']}")
            print(f"Total Users: {stats['total_users']}")
            print(f"Centralized Data: {stats['centralized_data']}")
            print(f"Database Size: {stats['database_size_bytes']/(1024*1024):.2f} MB")
            print(f"Jobs Last 24h: {stats['jobs_last_24h']}")
            print(f"Currently Running: {stats['currently_running']}")
            print(f"Stuck Jobs: {stats['stuck_jobs']}")
        
        elif choice == '8':
            days = input("Clean up failed jobs older than how many days? (default 7): ").strip()
            days = int(days) if days.isdigit() else 7
            
            print("🔍 Analyzing cleanup (dry run)...")
            cleanup_report = db_manager.cleanup_old_data(days, dry_run=True)
            
            print(f"\nCleanup Preview:")
            print(f"Old failed jobs to delete: {cleanup_report['old_failed_jobs']}")
            print(f"Orphaned results to delete: {cleanup_report['orphaned_results']}")
            
            if cleanup_report['old_failed_jobs'] > 0 or cleanup_report['orphaned_results'] > 0:
                confirm = input("Proceed with cleanup? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    final_report = db_manager.cleanup_old_data(days, dry_run=False)
                    print(f"✅ Cleanup complete!")
                    print(f"Deleted {final_report['old_failed_jobs']} jobs and {final_report['results_deleted']} results")
            else:
                print("✅ No cleanup needed")
        
        elif choice == '9':
            cutoff_time = datetime.now() - timedelta(hours=1)
            cutoff_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')
            
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, started_at 
                FROM jobs 
                WHERE status = 'running' 
                AND started_at < ?
            """, (cutoff_str,))
            
            stuck_jobs = cursor.fetchall()
            
            if stuck_jobs:
                print(f"\n🔧 Found {len(stuck_jobs)} stuck jobs:")
                for job_id, name, started_at in stuck_jobs:
                    print(f"  📋 Job {job_id}: {name} (started {started_at})")
                
                confirm = input("Fix these stuck jobs? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    for job_id, _, _ in stuck_jobs:
                        db_manager.terminate_job(job_id, "Auto-terminated - exceeded maximum runtime")
                    print(f"✅ Fixed {len(stuck_jobs)} stuck jobs")
            else:
                print("✅ No stuck jobs found")
            
            conn.close()


if __name__ == "__main__":
    interactive_database_manager()
