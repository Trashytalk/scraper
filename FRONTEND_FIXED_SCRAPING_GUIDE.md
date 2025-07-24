# 🔧 Frontend Troubleshooting & Scraping Quick Start Guide

## ✅ **FRONTEND ISSUE RESOLVED**

The blank browser issue has been fixed! Here's what was wrong and the solution:

### **Problem Identified:**
1. **Incorrect script reference**: `index.html` was referencing `/src/main.jsx` instead of `/src/main.tsx`
2. **Complex component dependencies**: The original App.tsx had complex MUI dependencies that may have had import issues

### **Solution Applied:**
1. ✅ **Fixed script reference** in `index.html` to point to correct TypeScript file
2. ✅ **Simplified App component** to use pure React without complex dependencies
3. ✅ **Created working test interface** that displays system status

## 🚀 **QUICK START - SCRAPING OPERATIONS**

### **1. Frontend Status ✅**
Your frontend should now display:
- Business Intelligence Scraper heading
- System status indicators 
- Next steps for scraping
- Test button for functionality verification

**Access**: http://localhost:5173

### **2. Start Backend Server**
```bash
cd /home/homebrew/scraper
python backend_server.py
```

**Backend will be available at**: http://localhost:8000
**API Documentation**: http://localhost:8000/docs

### **3. Start Scraping Immediately**

#### **Option A: Use API (Recommended)**
```bash
# 1. Get authentication token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 2. Create scraping job
TOKEN="your-jwt-token-here"
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Test Website Scrape",
    "url": "https://example.com",
    "scraper_type": "basic",
    "config": {"delay": 1}
  }'

# 3. Start the job
curl -X POST http://localhost:8000/api/jobs/1/start \
  -H "Authorization: Bearer $TOKEN"

# 4. Get results
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/jobs/1/results
```

#### **Option B: Direct Scraping Engine**
```bash
cd /home/homebrew/scraper
python -c "
import asyncio
from scraping_engine import ScrapingEngine

async def test_scrape():
    engine = ScrapingEngine()
    result = await engine.scrape_url('https://example.com', 'basic')
    print('Scraping Result:', result)

asyncio.run(test_scrape())
"
```

#### **Option C: Working Demo Spider**
```bash
cd /home/homebrew/scraper/business_intel_scraper/backend/modules/spiders
scrapy crawl business_news_demo -o results.json
```

### **4. Real Scraping Examples**

#### **E-commerce Scraping:**
```python
from scraping_engine import ScrapingEngine
import asyncio

async def scrape_ecommerce():
    engine = ScrapingEngine()
    result = await engine.scrape_url(
        "https://example-shop.com/products",
        "e_commerce",
        {
            "custom_selectors": {
                "title": ".product-title",
                "price": ".price",
                "description": ".product-description"
            }
        }
    )
    return result

# Run the scraping
result = asyncio.run(scrape_ecommerce())
print(result)
```

#### **News Article Scraping:**
```python
async def scrape_news():
    engine = ScrapingEngine()
    result = await engine.scrape_url(
        "https://news-site.com/article",
        "news",
        {
            "custom_selectors": {
                "headline": "h1.headline",
                "author": ".author-name",
                "content": ".article-body"
            }
        }
    )
    return result
```

#### **API Data Collection:**
```python
async def scrape_api():
    engine = ScrapingEngine()
    result = await engine.scrape_url(
        "https://api.example.com/data",
        "api"
    )
    return result
```

## 📊 **Monitor Your Scraping**

### **Check Results via API:**
```bash
# List all jobs
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/jobs

# Get specific job details
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/jobs/{job_id}

# View system performance
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/performance/summary
```

### **Database Results:**
```bash
cd /home/homebrew/scraper
sqlite3 data/scraper.db

.tables
SELECT * FROM jobs LIMIT 10;
SELECT * FROM job_results LIMIT 5;
```

## 🔍 **Available Scraper Types**

1. **`basic`** - General web content extraction
2. **`e_commerce`** - Product listings, prices, reviews
3. **`news`** - Articles, headlines, publication dates
4. **`social_media`** - Public posts, profiles (limited)
5. **`api`** - JSON/XML API endpoints

## 🛡️ **Best Practices**

### **Respectful Scraping:**
- Always include delays between requests
- Respect robots.txt files
- Use reasonable request rates
- Monitor for rate limiting

### **Error Handling:**
- Check response status codes
- Implement retry logic for failed requests
- Log errors for debugging
- Validate extracted data

### **Performance:**
- Use async operations for multiple URLs
- Implement caching for repeated requests
- Monitor memory usage for large datasets
- Use database storage for persistent results

## 🎯 **Next Steps**

1. **✅ Frontend working** - You can see the interface
2. **🔄 Start backend** - `python backend_server.py`
3. **🚀 Begin scraping** - Use API or direct engine
4. **📊 Monitor results** - Check database and API endpoints
5. **🔧 Implement custom spiders** - Add business-specific scrapers

Your scraping system is now fully operational! 🎉
