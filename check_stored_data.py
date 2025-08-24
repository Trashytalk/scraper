#!/usr/bin/env python3
import sqlite3
import json

conn = sqlite3.connect('/home/homebrew/scraper/data/scraper.db')
cursor = conn.cursor()

cursor.execute("SELECT data FROM job_results ORDER BY created_at DESC LIMIT 1")
row = cursor.fetchone()

if row:
    data = json.loads(row[0])
    print("Keys in data:", list(data.keys()))
    
    if 'crawled_data' in data and data['crawled_data']:
        page = data['crawled_data'][0]
        print('Keys in first page:', list(page.keys()))
        if 'images' in page:
            print(f'Images found: {len(page["images"])}')
            if page['images']:
                print('First image:', page['images'][0])
        else:
            print('No images key found in page data')
    else:
        print('No crawled_data found')
else:
    print('No data found')

conn.close()
