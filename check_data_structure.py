#!/usr/bin/env python3
import asyncio
import json
from scraping_engine import ScrapingEngine

async def check_data_structure():
    engine = ScrapingEngine()
    result = await engine.scrape_url('https://en.wikipedia.org/wiki/Python_(programming_language)', 'basic', {'include_images': True, 'include_forms': True, 'max_pages': 1})
    
    print('=== STANDARD SCRAPING RESULT STRUCTURE ===')
    print('Top-level keys:', list(result.keys()))
    
    if 'images' in result:
        print(f'\nImages array length: {len(result["images"])}')
        if result['images']:
            print('First image structure:')
            print(json.dumps(result['images'][0], indent=2))
    
    if 'links' in result:
        print(f'\nLinks array length: {len(result["links"])}')
        if result['links']:
            print('First 3 links with image extensions:')
            image_links = [link for link in result['links'] if link.get('url') and any(ext in link['url'].lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg'])]
            for i, link in enumerate(image_links[:3]):
                print(f'  {i+1}. {json.dumps(link, indent=4)}')

if __name__ == "__main__":
    asyncio.run(check_data_structure())
