# 🧪 Manual Testing Guide - Business Intelligence Scraper Platform

## 📋 Complete Manual Testing Instructions

This guide provides step-by-step instructions to manually test all functions of the Business Intelligence Scraper Platform, including the new enhanced crawling features.

---

## 🚀 **Pre-Testing Setup**

### 1. System Startup
```bash
# Start the platform
cd /home/homebrew/scraper
./quick_start.sh

# Verify services are running
curl http://localhost:8000/api/health  # Backend health check
curl http://localhost:5173            # Frontend access
```

### 2. Access Points
- **Frontend Dashboard**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
- **Backend API**: http://localhost:8000/api/*

---

## 🔐 **Authentication Testing**

### Test 1: Login Functionality
1. **Open Frontend**: Navigate to http://localhost:5173
2. **Verify Login Screen**: Should see Business Intelligence Scraper login
3. **Test Invalid Credentials**:
   - Username: `wrong`
   - Password: `wrong`
   - Click "Login" → Should show "Login failed"
4. **Test Valid Credentials**:
   - Username: `admin`
   - Password: `admin123`
   - Click "Login" → Should redirect to main dashboard

### Test 2: Backend Connection Status
1. **Verify Connection Status**: Green "✅ Connected" indicator in header
2. **Test Disconnection**: Stop backend server → Should show "❌ Disconnected"
3. **Test Reconnection**: Restart backend → Should show "✅ Connected" again

---

## 📊 **Dashboard Testing**

### Test 3: Dashboard Overview
1. **Navigate to Dashboard Tab**: Click "📊 Dashboard"
2. **Verify Analytics Cards**: Should show Total Jobs, Completed, Running, Failed counts
   - **Fixed**: Job counts now display correctly (Total: 169, Completed: 59, Running: 6, Failed: 0)
3. **Check Recent Jobs**: Should display list of recent jobs with status indicators
4. **Note**: Job creation has been moved to Operations tab for better organization

### Test 4: Analytics Data
1. **Check Job Counts**: Verify numbers match actual job data
2. **Test Status Colors**: 
   - Completed = Green background
   - Failed = Red background
   - Running = Yellow background
3. **Verify Timestamps**: Recent jobs should show correct creation dates

---

## 🎯 **Enhanced Crawling System Testing**

### Test 5: Job Creation via Operations Tab

1. **Navigate to Operations Tab**: Click "🎯 Operations"
2. **Quick Create Job Section (New)**:
   - Use the "🚀 Quick Create Job" section at the top
   - Job Name: `Test Quick Job`
   - URL: `https://example.com`
   - Type: `basic` (default scraper type)
   - **Enhanced Options Available**: 
     - ✅ Extract Full HTML
     - ✅ Crawl Entire Domain  
     - ✅ Include Images
     - ✅ Save to Database (enabled by default)
   - Click "Create Job"

3. **Original Operations Panel (Preserved)**:
   - All existing operations functionality remains below the quick create section
   - Advanced configuration options
   - Workflow management
   - Job monitoring and control

4. **Verify Job Creation**: Should appear in Jobs tab
5. **Start Job**: Navigate to Jobs tab and click the "Start" (play arrow) button
6. **Monitor Progress**: Watch status change from "pending" → "running" → "completed"

### Test 6: Enhanced Crawling Features

**Note**: Enhanced crawling options are now fully integrated in the Operations tab GUI:

1. **Test Enhanced Features via Quick Create Section**:
   - Navigate to Operations Tab
   - Use the "🚀 Quick Create Job" section at the top
   - In the "Enhanced Crawling Options" section:
     - Check "Extract Full HTML" for complete page content
     - Check "Crawl Entire Domain" to crawl all pages
     - Check "Include Images" to download images
     - Verify "Save to Database" is checked by default
   - Create and run the job

2. **Test Batch Mode**:
   - Select "🕷️ Batch Scraping from Crawler Results" radio button
   - Choose a completed crawler job from dropdown
   - Set batch size (5, 10, 25, or 50 URLs per job)
   - Create batch jobs

3. **Use Original Operations Panel**:
   - Access advanced configuration options in the original operations interface below
   - Expand "⚙️ Advanced Configuration" section
   - In "Universal Settings", find "🚀 Enhanced Crawling Options":
     - ✅ Extract Full HTML
     - ✅ Crawl Entire Domain
     - ✅ Include Images
     - ✅ Save to Database
   - Configure complex workflows and automation
   - Monitor job execution and results

### Test 7: Operations Panel Functionality

1. **Quick Create Section (New Addition)**:
   - Use the enhanced job creation form at the top of Operations tab
   - Test single URL and batch mode options
   - Configure enhanced crawling options
   - Immediate job creation workflow

2. **Original Operations Interface (Preserved)**:
   - Access comprehensive configuration panels
   - Expand "⚙️ Advanced Configuration" section
   - In "Universal Settings", test "🚀 Enhanced Crawling Options":
     - Extract Full HTML (checkbox)
     - Crawl Entire Domain (checkbox)
     - Include Images (checkbox)  
     - Save to Database (checkbox)
   - Use advanced workflow management
   - Configure automation and scheduling
   - Access detailed job monitoring and control

3. **Integration Testing**:
   - Verify both interfaces work together seamlessly
   - Test job creation from both quick create and original interface
   - Confirm all jobs appear in the unified job management system

### Test 8: API-Based Enhanced Features Testing

**Note**: Enhanced crawling features are available via API but not exposed in current GUI

1. **Test Full HTML Extraction via API**:
   ```bash
   # Test enhanced crawling with API
   python3 test_enhanced_crawling.py
   ```

2. **Test Data Centralization**:
   ```bash
   # Test data centralization
   python3 test_centralize_data.py
   ```

3. **Monitor Results**: Check database and job results via GUI

---

## 🔧 **Backend API Testing**

### Test 12: Health Check
```bash
curl http://localhost:8000/api/health
# Expected: {"status": "healthy"}
```

### Test 13: Authentication API
```bash
# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
# Expected: {"access_token": "...", "token_type": "bearer"}
```

### Test 14: Jobs API
```bash
# Get jobs list (replace TOKEN with actual token)
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/jobs
# Expected: List of jobs with status, timestamps, etc.
```

### Test 15: Performance API
```bash
# Get performance metrics
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/performance/summary
# Expected: System performance data
```

---

## 🎨 **Frontend Interface Testing**

### Test 16: Navigation Testing

1. **Test All Tabs**: Click each tab and verify content loads
   - **Current Available Tabs**: Jobs, Dashboard, Analytics
   - **Note**: Some tabs mentioned in documentation may not be implemented yet
   - Verify each accessible tab loads without errors

### Test 17: Job Management Interface

1. **Job Creation Form**:
   - Click "Create Job" button 
   - Test required field validation (Job Name, URL)
   - Test URL format validation
   - Test different scraper types (beautiful_soup, etc.)
   - **Note**: Advanced crawling toggles not available in current GUI

2. **Job List Management**:
   - Verify job status indicators (pending, running, completed, failed)
   - Test "View Details" button functionality  
   - Test Start/Stop buttons (play/stop icons)
   - **Note**: If job counts show 0, this indicates a stats calculation issue

### Test 18: Results Viewer

1. **Open Job Results**: Click "View Details" on completed job
2. **Enhanced Job Details Modal**: 
   - Verify comprehensive job information is displayed (not console message)
   - Check job ID, status with color coding, type, timestamps
   - Verify configuration shows URL as clickable link
   - Check crawling summary with pages processed, URLs discovered, data extracted
   - Test "View Results" button for completed jobs
3. **Test Modal Operations**: Verify modal opens and closes properly
4. **Show Collected Data**: Click the "Show Collected Data" button
   - **Fixed**: Should now display actual scraped content (50+ items with full data)
   - **No longer shows**: "Item 1" placeholder text
   - **Displays**: Complete URLs, titles, descriptions, links, text content, images, metadata
   - **Pagination**: Navigate through multiple pages of results
   - **Search**: Filter results using the search box
   - **Export**: Test JSON/CSV export functionality

### Test 19: Configuration Panel
1. **Open Operations Tab**: Click "🎯 Operations"
2. **Test Configuration Options**: Toggle various settings
3. **Test Save/Reset**: Verify configuration persistence

---

## 🧪 **Automated Test Execution**

### Test 20: Run Test Suites
```bash
cd /home/homebrew/scraper

# Test enhanced crawling features
python test_enhanced_crawling.py
# Expected: 100% success rate on all 5 features

# Test data centralization
python test_centralize_data.py
# Expected: Successful centralization with quality assessment

# Test complete workflow
python test_all_features_final.py
# Expected: All 6 features working with performance metrics
```

---

## 📊 **Performance Testing**

### Test 21: Load Testing
1. **Create Multiple Jobs**: Create 5-10 jobs simultaneously
2. **Monitor System Resources**: Check CPU, memory usage
3. **Verify Completion**: Ensure all jobs complete successfully

### Test 22: Large Dataset Testing
1. **Test Large Site**: Use a site with many pages (Wikipedia main page)
2. **Monitor Performance**: Check crawling speed and memory usage
3. **Verify Quality**: Ensure data quality remains high

---

## 🔍 **Error Handling Testing**

### Test 23: Invalid URL Testing
1. **Create Job with Invalid URL**: `https://invalid-url-that-does-not-exist.com`
2. **Verify Error Handling**: Should fail gracefully with error message
3. **Check Logs**: Verify appropriate error logging

### Test 24: Network Timeout Testing
1. **Create Job with Slow Response**: Use a URL known to be slow
2. **Monitor Timeout Behavior**: Verify proper timeout handling
3. **Check Status**: Should show appropriate status/error

### Test 25: Database Error Testing
1. **Stop Database**: Temporarily stop database service
2. **Create Job**: Attempt to create job requiring database
3. **Verify Fallback**: Should handle database unavailability gracefully

---

## 📋 **Manual Testing Checklist**

### ✅ **Authentication & Access**
- [ ] Login with valid credentials
- [ ] Login rejection with invalid credentials
- [ ] Backend connection status display
- [ ] Automatic session management

### ✅ **Enhanced Crawling Features**

- [ ] Quick job creation via Operations tab (new enhanced interface at top)
- [ ] Enhanced crawling options in GUI (Extract Full HTML, Crawl Entire Domain, Include Images, Save to Database)
- [ ] Enhanced options in Advanced Configuration (Universal Settings section)
- [ ] Batch mode processing (crawler results to scraper pipeline)
- [ ] Original operations panel functionality (preserved below quick create section)
- [ ] Advanced configuration and workflow management
- [ ] Database persistence (57+ cached entries)
- [ ] Data centralization (quality assessment)
- [ ] Backend processing capabilities
- [ ] **Updated**: Enhanced crawling options available in both quick create AND advanced configuration

### ✅ **User Interface**

- [ ] Dashboard analytics display (job counts now show correctly: Total: 169, Completed: 59, Running: 6, Failed: 0)
- [ ] Quick job creation at top of Operations tab
- [ ] Enhanced crawling options visible in GUI
- [ ] Original operations panel preserved with full functionality
- [ ] Job list management (Start/Stop buttons)
- [ ] Job details viewer functionality
- [ ] Modal operations
- [ ] Navigation between available tabs
- [ ] **Enhanced**: Operations tab combines quick creation with comprehensive operations management

### ✅ **API Functionality**
- [ ] Health check endpoint
- [ ] Authentication API
- [ ] Jobs CRUD operations
- [ ] Performance metrics API
- [ ] Data centralization endpoint

### ✅ **Performance & Reliability**
- [ ] Multiple concurrent jobs
- [ ] Large dataset handling
- [ ] Error recovery
- [ ] Resource usage monitoring

### ✅ **Data Quality**
- [ ] Complete data extraction
- [ ] Accurate metadata
- [ ] Proper data formatting
- [ ] Quality scoring

---

## 🎯 **Expected Results Summary**

### **Performance Benchmarks**
- **Crawling Speed**: 0.5-1.0 pages per second
- **HTML Extraction**: 500K+ characters per page
- **Image Extraction**: 50-200 images per site
- **Database Storage**: 50+ cached pages
- **Success Rate**: 95-100% for valid URLs

### **Quality Metrics**
- **Data Completeness**: 90%+ fields populated
- **Error Rate**: <5% for valid requests
- **Response Time**: <30 seconds for typical sites
- **Memory Usage**: <1GB for standard operations

---

## 🔧 **Troubleshooting Common Issues**

### Issue: Backend Not Starting
```bash
# Check logs
tail -f backend_enhanced.log

# Restart services
./quick_start.sh --restart
```

### Issue: Database Connection Errors
```bash
# Verify database file
ls -la data.db

# Check permissions
chmod 644 data.db
```

### Issue: Frontend Not Loading
```bash
# Check frontend process
ps aux | grep npm

# Restart frontend
cd business_intel_scraper/frontend
npm run dev
```

---

## 📞 **Testing Completion**

After completing all tests, you should have verified:

1. ✅ **Basic scraping functionality working**
2. ✅ **API endpoints responding correctly** 
3. ✅ **Database persistence operational** (57+ cached entries)
4. ✅ **Authentication system working**
5. ✅ **Job creation and management via GUI**
6. ✅ **Enhanced features working via API** (test scripts)

**📋 Current System Status:**
- ✅ Job count statistics now display correctly (Total: 169, Completed: 59, Running: 6, Failed: 0)
- ✅ Operations tab enhanced with quick job creation at the top
- ✅ All original operations panel functionality preserved below quick create section
- ✅ Enhanced crawling options fully exposed in GUI in TWO locations:
  - Quick Create section (Extract Full HTML, Crawl Entire Domain, Include Images, Save to Database)
  - Advanced Configuration → Universal Settings → Enhanced Crawling Options
- ✅ Both quick creation and comprehensive operations management available in unified interface
- ✅ **NEW**: "View Details" modal enhanced with comprehensive job information, crawling summary, and direct action buttons
- ✅ **FIXED**: "Show Collected Data" now displays actual scraped content (50+ items) instead of "Item 1" placeholder

**🎉 The Business Intelligence Scraper Platform now provides maximum flexibility: quick job creation for immediate needs, plus comprehensive advanced configuration for power users - with enhanced crawling options accessible in both interfaces! Both View Details and Show Collected Data functionality now work properly with rich, comprehensive data display.**
