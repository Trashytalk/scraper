#!/usr/bin/env python3
"""
Complete Data Cleanup Script
Clears all previous scrape data to start fresh
"""

import os
import sqlite3
import shutil
import sys
from pathlib import Path

def clear_database_tables(db_path, tables_to_clear):
    """Clear specified tables in a database"""
    if not os.path.exists(db_path):
        print(f"⚠️ Database not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for table in tables_to_clear:
            try:
                cursor.execute(f"DELETE FROM {table}")
                rows_deleted = cursor.rowcount
                print(f"✅ Cleared {rows_deleted} rows from {table}")
            except sqlite3.Error as e:
                print(f"⚠️ Error clearing {table}: {e}")
        
        conn.commit()
        conn.close()
        print(f"✅ Database cleanup complete: {db_path}")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")

def clear_directory_contents(dir_path):
    """Clear all contents of a directory but keep the directory"""
    if not os.path.exists(dir_path):
        print(f"⚠️ Directory not found: {dir_path}")
        return
    
    try:
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
                print(f"🗑️ Deleted file: {item}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"🗑️ Deleted directory: {item}")
        print(f"✅ Directory cleared: {dir_path}")
    except Exception as e:
        print(f"❌ Error clearing directory {dir_path}: {e}")

def main():
    """Main cleanup execution"""
    print("🧹 COMPLETE DATA CLEANUP")
    print("=" * 50)
    print("This will clear ALL previous scrape data")
    print("=" * 50)
    
    # Get confirmation
    confirm = input("Are you sure you want to clear all data? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Cleanup cancelled")
        sys.exit(1)
    
    print("\n🚀 Starting cleanup...")
    
    # 1. Clear main databases
    print("\n📊 Clearing databases...")
    
    # Clear analytics.db
    clear_database_tables("analytics.db", [
        "analytics_metrics",
        "performance_snapshots", 
        "quality_snapshots"
    ])
    
    # Clear data.db
    clear_database_tables("data.db", [
        "articles",
        "entities", 
        "osint_results",
        "companies",
        "events",
        "scrape_tasks",
        "connections",
        "job_events",
        "search_queries",
        "crawl_cache",
        "locations",
        "users",
        "data_sources",
        "marketplace_spiders"
    ])
    
    # Clear scraper.db
    clear_database_tables("data/scraper.db", [
        "analytics",
        "job_results",
        "users",
        "centralized_data",
        "jobs"
    ])
    
    # 2. Clear data directories
    print("\n📁 Clearing data directories...")
    
    data_subdirs = [
        "data/jobs",
        "data/logs", 
        "data/marketplace_cache",
        "data/output",
        "data/temp"
    ]
    
    for subdir in data_subdirs:
        clear_directory_contents(subdir)
    
    # 3. Clear cache
    print("\n🗂️ Clearing cache...")
    clear_directory_contents("cache")
    
    # 4. Clear any CFPL storage if it exists
    cfpl_dirs = [
        "storage/raw",
        "storage/derived", 
        "storage/index"
    ]
    
    for cfpl_dir in cfpl_dirs:
        if os.path.exists(cfpl_dir):
            print(f"\n💾 Clearing CFPL storage: {cfpl_dir}")
            clear_directory_contents(cfpl_dir)
    
    # 5. Clear logs
    print("\n📋 Clearing log files...")
    log_files = [
        "backend.log",
        "server.log", 
        "quick_start.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                open(log_file, 'w').close()  # Truncate log file
                print(f"✅ Cleared log: {log_file}")
            except Exception as e:
                print(f"⚠️ Error clearing {log_file}: {e}")
    
    # 6. Verify cleanup
    print("\n🔍 Verifying cleanup...")
    
    # Check database counts
    databases_to_check = [
        ("analytics.db", "analytics_metrics"),
        ("data.db", "scrape_tasks"), 
        ("data/scraper.db", "jobs"),
        ("data/scraper.db", "job_results")
    ]
    
    all_clear = True
    for db_path, table in databases_to_check:
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                conn.close()
                
                if count == 0:
                    print(f"✅ {db_path}:{table} - {count} rows")
                else:
                    print(f"⚠️ {db_path}:{table} - {count} rows remaining")
                    all_clear = False
            except Exception as e:
                print(f"❌ Error checking {db_path}:{table} - {e}")
                all_clear = False
    
    print("\n" + "=" * 50)
    if all_clear:
        print("🎉 CLEANUP COMPLETE!")
        print("✅ All previous scrape data cleared")
        print("✅ Ready for fresh job execution")
        print("🚀 You can now run job 196 as the only data")
    else:
        print("⚠️ Cleanup completed with some issues")
        print("Please check the warnings above")
    
    print("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}")
        sys.exit(1)
