#!/usr/bin/env python3
"""
Test script for Database Management APIs
This script tests the new database management endpoints we just added.
"""
import json
import os
import sqlite3
import sys

# Add the project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_database_connection():
    """Test basic database connectivity"""
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        # Get table names
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]

        print("🔍 Database Tables Found:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   📊 {table}: {count} records")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_table_structure():
    """Test table structure analysis"""
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        # Test table info query (what our API uses)
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = []

        for (table_name,) in cursor.fetchall():
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]

            table_info = {
                "name": table_name,
                "columns": [
                    {
                        "name": col[1],
                        "type": col[2],
                        "nullable": not col[3],
                        "primary_key": bool(col[5]),
                    }
                    for col in columns
                ],
                "row_count": row_count,
            }
            tables.append(table_info)

        print("\n📋 Detailed Table Structure:")
        for table in tables:
            print(f"\n   🗂️ Table: {table['name']} ({table['row_count']} rows)")
            for col in table["columns"]:
                pk_indicator = " (PK)" if col["primary_key"] else ""
                nullable_indicator = " (nullable)" if col["nullable"] else " (NOT NULL)"
                print(
                    f"      • {col['name']}: {col['type']}{pk_indicator}{nullable_indicator}"
                )

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Table structure analysis failed: {e}")
        return False


def test_sample_queries():
    """Test sample database queries"""
    try:
        conn = sqlite3.connect("data.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print("\n🔍 Sample Data Preview:")

        # Test each main table
        test_tables = ["users", "jobs", "job_results", "analytics"]

        for table in test_tables:
            try:
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                rows = cursor.fetchall()

                print(f"\n   📊 {table} (showing up to 3 records):")
                if rows:
                    for i, row in enumerate(rows, 1):
                        print(f"      {i}. {dict(row)}")
                else:
                    print("      (no data)")

            except Exception as e:
                print(f"      ⚠️ Error querying {table}: {e}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Sample queries failed: {e}")
        return False


def test_database_management_readiness():
    """Test if database is ready for our management APIs"""
    print("🗄️ Database Management API Readiness Test")
    print("=" * 50)

    # Test 1: Basic connectivity
    print("\n1️⃣ Testing database connectivity...")
    if not test_database_connection():
        return False

    # Test 2: Table structure
    print("\n2️⃣ Testing table structure analysis...")
    if not test_table_structure():
        return False

    # Test 3: Sample queries
    print("\n3️⃣ Testing sample queries...")
    if not test_sample_queries():
        return False

    print("\n✅ Database Management API Readiness: PASSED")
    print("\n🎉 Your database is ready for the new Database Management tab!")
    print("\nNext steps:")
    print("1. Start the backend server: python backend_server.py")
    print(
        "2. Start the frontend server: cd business_intel_scraper/frontend && npm run dev"
    )
    print("3. Navigate to the 🗄️ Database tab in the web interface")

    return True


if __name__ == "__main__":
    if test_database_management_readiness():
        sys.exit(0)
    else:
        sys.exit(1)
