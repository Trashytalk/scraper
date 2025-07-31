# 🧪 Quick Manual Testing Checklist

## Essential Manual Tests for Business Intelligence Scraper

### 🚀 **System Startup**
```bash
cd /home/homebrew/scraper
./quick_start.sh
```

**Verify**: 
- Frontend: http://localhost:5173
- Backend: http://localhost:8000/api/health

---

## 🔐 **1. Authentication Test**

**Steps:**
1. Open http://localhost:5173
2. Login with: `admin` / `admin123`
3. Verify dashboard loads

**Expected**: ✅ Connected status, dashboard visible

---

## 📊 **2. Basic Dashboard Test**

**Steps:**
1. Click "📊 Dashboard" tab
2. Check analytics cards (Total Jobs, Completed, etc.)
3. Verify recent jobs list

**Expected**: Analytics data displays, recent jobs shown

---

## 🎯 **3. Enhanced Crawling Tests**

### Test A: Basic Crawling
**Steps:**
1. Click "🎯 Operations"
2. Create job:
   - Name: `Test Basic`
   - URL: `https://example.com`
   - Type: `intelligent`
   - Keep default settings
3. Click "Create" → "Start" → Wait → "View Results"

**Expected**: Job completes successfully, shows scraped data

### Test B: Full HTML Extraction
**Steps:**
1. Create new job:
   - Name: `Test HTML`
   - URL: `https://example.com`
   - **Enable**: `extract_full_html: true`
2. Start and view results

**Expected**: Large HTML content (500K+ characters) in results

### Test C: Domain Crawling
**Steps:**
1. Create job:
   - Name: `Test Domain`
   - URL: `https://httpbin.org`
   - **Enable**: `crawl_entire_domain: true`
   - Set `max_depth: 2`
2. Start and view results

**Expected**: Multiple pages crawled, different URLs in results

### Test D: Image Extraction  
**Steps:**
1. Create job:
   - Name: `Test Images`
   - URL: `https://en.wikipedia.org/wiki/Photography`
   - **Enable**: `include_images: true`
2. Start and view results

**Expected**: 50+ images extracted with metadata

### Test E: All Features Combined
**Steps:**
1. Create job with ALL enhanced features enabled:
   - `extract_full_html: true`
   - `crawl_entire_domain: true` 
   - `include_images: true`
   - `save_to_database: true`
   - URL: `https://en.wikipedia.org/wiki/Python_(programming_language)`
2. Start and view results

**Expected**: 
- Multiple pages crawled
- Large HTML content
- Many images
- Data in database

---

## 🔧 **4. API Tests**

### Test F: Direct API Testing
```bash
cd /home/homebrew/scraper

# Test enhanced crawling
python test_enhanced_crawling.py

# Test data centralization  
python test_centralize_data.py

# Test all features
python test_all_features_final.py
```

**Expected**: All tests show 100% success rate

---

## 💾 **5. Database Persistence Test**

**Steps:**
1. After running jobs with `save_to_database: true`
2. Check database:
```bash
sqlite3 /home/homebrew/scraper/data.db
SELECT COUNT(*) FROM crawl_cache;
SELECT url, title FROM crawl_cache LIMIT 3;
.quit
```

**Expected**: Shows cached pages (50+ entries)

---

## 🎨 **6. Frontend Interface Tests**

### Test G: Navigation
**Steps:**
1. Click each tab: Operations, Dashboard, Analytics, etc.
2. Verify each loads without errors

**Expected**: All tabs load properly

### Test H: Job Management
**Steps:**
1. Create multiple jobs
2. Test "Details" button
3. Test "Start" and "View Results" buttons
4. Test search in results modal

**Expected**: All buttons work, modals open/close properly

---

## ⚡ **7. Performance Test**

### Test I: Multiple Jobs
**Steps:**
1. Create 3-5 jobs simultaneously
2. Start them all
3. Monitor completion

**Expected**: All complete successfully without errors

---

## 🔍 **8. Error Handling Test**

### Test J: Invalid URL
**Steps:**
1. Create job with invalid URL: `https://invalid-url-does-not-exist.com`
2. Start job
3. Check result

**Expected**: Fails gracefully with error message

---

## ✅ **Quick Success Criteria**

After all tests, verify:

- [ ] ✅ Login works
- [ ] ✅ Dashboard shows analytics  
- [ ] ✅ Basic crawling extracts data
- [ ] ✅ HTML extraction works (500K+ chars)
- [ ] ✅ Domain crawling finds multiple pages
- [ ] ✅ Image extraction finds 50+ images
- [ ] ✅ Database shows cached pages
- [ ] ✅ All API tests pass (100% success)
- [ ] ✅ Frontend navigation works
- [ ] ✅ Job management functions properly

---

## 🎯 **Expected Performance Benchmarks**

- **Crawling Speed**: 0.5-1.0 pages/second
- **HTML Size**: 500K+ characters/page  
- **Images**: 50-200 per site
- **Database**: 50+ cached pages
- **Success Rate**: 95-100%
- **API Response**: <5 seconds

---

## 🚨 **If Tests Fail**

### Common Fixes:
```bash
# Restart system
./quick_start.sh --restart

# Check logs  
tail -f backend_enhanced.log

# Verify database
ls -la data.db

# Test API directly
curl http://localhost:8000/api/health
```

**🎉 All tests passing = System is fully operational!**
