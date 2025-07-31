# 🎨 Frontend Manual Testing Checklist

## React Interface Testing Guide

### 🚀 **Prerequisites**
- Backend running on http://localhost:8000
- Frontend running on http://localhost:5173
- Valid login credentials: admin/admin123

---

## 🔐 **Authentication Interface**

### ✅ Login Screen Tests
1. **Access Login**: Open http://localhost:5173
2. **Visual Check**: 
   - See "🎯 Business Intelligence Scraper" title
   - Backend status indicator (green = connected)
   - Username/password fields
   - Login button

3. **Invalid Login Test**:
   - Enter: `wrong` / `wrong`
   - Click "Login"
   - **Expected**: "Login failed" alert

4. **Valid Login Test**:
   - Enter: `admin` / `admin123`
   - Click "Login"
   - **Expected**: Redirect to main interface

---

## 📊 **Dashboard Tab Testing**

### ✅ Dashboard Overview
1. **Navigate**: Click "📊 Dashboard" tab
2. **Analytics Cards**: Verify 4 cards show:
   - Total Jobs (gray background)
   - Completed (green background)
   - Running (yellow background)  
   - Failed (red background)

3. **Recent Jobs**: Check jobs list shows:
   - Job names and creation dates
   - Status badges with correct colors
   - Action buttons (Details, Start, View Results)

4. **Quick Create Job Form**: Verify form has:
   - Job name field
   - URL field (when not in batch mode)
   - Type dropdown
   - Create button

---

## 🎯 **Operations Tab Testing**

### ✅ Enhanced Crawling Configuration
1. **Navigate**: Click "🎯 Operations" tab
2. **Job Creation Form**: Check enhanced options:
   - `extract_full_html` checkbox
   - `crawl_entire_domain` checkbox
   - `include_images` checkbox
   - `save_to_database` checkbox (should be checked by default)

3. **Test Job Creation**:
   - Name: `Frontend Test Job`
   - URL: `https://example.com`
   - Enable all enhanced features
   - Click "Create Job"
   - **Expected**: Job appears in operations interface

---

## 🎛️ **Job Management Interface**

### ✅ Job List Operations
1. **Job Status Indicators**: Verify colors:
   - Pending: Gray
   - Running: Yellow
   - Completed: Green
   - Failed: Red

2. **Action Buttons Test**:
   - **Details Button**: Click on any job
     - **Expected**: Modal opens with job details
     - **Close Test**: Click outside or X to close
   
   - **Start Button**: Click on pending job
     - **Expected**: Status changes to "running"
   
   - **View Results Button**: Click on completed job
     - **Expected**: Results modal opens

### ✅ Results Viewer Modal
1. **Open Results**: Click "View Results" on completed job
2. **Modal Content**: Should show:
   - Job name and metadata
   - Search bar for filtering
   - Pagination controls
   - Data table/cards
   - Close button (X)

3. **Search Function**:
   - Type in search bar
   - **Expected**: Results filter in real-time

4. **Pagination**:
   - Click next/previous page
   - **Expected**: Navigation works smoothly

5. **Modal Close**:
   - Click X button
   - Click outside modal
   - **Expected**: Modal closes properly

---

## 📱 **Navigation & Tabs**

### ✅ Tab Navigation
Test each tab clicks and loads:
1. **🎯 Operations** - Job creation and management
2. **📊 Dashboard** - Analytics overview
3. **📈 Analytics** - Advanced analytics (may be placeholder)
4. **🌐 Network** - Network tools (may be placeholder)
5. **🔍 OSINT** - OSINT tools (may be placeholder)
6. **💎 Data Enrichment** - Enrichment tools (may be placeholder)
7. **📝 Data Parsing** - Parsing tools (may be placeholder)
8. **🌍 Browser** - Browser tools (may be placeholder)
9. **📈 Visualization** - Visualization tools (may be placeholder)
10. **⚡ Performance** - Performance metrics

**Expected**: All tabs should be clickable without errors

---

## 🔧 **Interactive Features**

### ✅ Enhanced Crawling Toggles
1. **Configuration Toggles**: Test each checkbox:
   - Click to enable/disable
   - **Expected**: State changes visually
   - **Expected**: Form data updates

2. **Form Validation**:
   - Submit empty form
   - **Expected**: Required field validation
   - Submit invalid URL
   - **Expected**: URL format validation

### ✅ Real-time Updates
1. **Auto-refresh**: Leave interface open
2. **Expected**: Job statuses update automatically
3. **Backend Connection**: Stop/start backend
4. **Expected**: Connection status updates

---

## 🎨 **Visual & UX Testing**

### ✅ Responsive Design
1. **Resize Browser**: Make window smaller/larger
2. **Expected**: Interface adapts responsively
3. **Mobile View**: Very narrow width
4. **Expected**: Elements stack properly

### ✅ Loading States
1. **Submit Job**: Create new job
2. **Expected**: Button shows "Creating..." during submission
3. **API Calls**: Watch for loading indicators
4. **Expected**: No hanging loading states

### ✅ Error Handling
1. **Invalid Operations**: Try invalid actions
2. **Network Errors**: Disconnect backend temporarily
3. **Expected**: Graceful error messages, no crashes

---

## 📋 **Frontend Testing Checklist**

### ✅ **Basic Interface**
- [ ] Login screen displays correctly
- [ ] Authentication works (valid/invalid)
- [ ] Main interface loads after login
- [ ] Header shows connection status
- [ ] Logout button works

### ✅ **Dashboard Tab**
- [ ] Analytics cards display with correct colors
- [ ] Recent jobs list shows properly
- [ ] Quick create form is functional
- [ ] All buttons respond correctly

### ✅ **Operations Tab**
- [ ] Enhanced crawling options visible
- [ ] All checkboxes work
- [ ] Job creation form validates
- [ ] Jobs appear after creation

### ✅ **Job Management**
- [ ] Job status colors correct
- [ ] Details modal opens/closes
- [ ] Results modal opens/closes
- [ ] Start button changes job status
- [ ] Search function works in results

### ✅ **Navigation**
- [ ] All tabs clickable
- [ ] Tab switching smooth
- [ ] No console errors
- [ ] URL updates appropriately

### ✅ **Enhanced Features**
- [ ] Full HTML extraction option
- [ ] Domain crawling option
- [ ] Image extraction option
- [ ] Database persistence option
- [ ] All toggles save state

### ✅ **User Experience**
- [ ] Interface responsive
- [ ] Loading states visible
- [ ] Error messages clear
- [ ] No UI freezing
- [ ] Smooth interactions

---

## 🚨 **Common Issues to Watch**

### ❌ **Red Flags**
- Modal not opening/closing
- Buttons not responding
- Console errors in browser
- Forms not submitting
- Data not updating
- UI elements overlapping
- Missing enhanced crawling options

### ✅ **Success Indicators**
- All modals work smoothly
- Enhanced crawling options available
- Job creation and management flows
- Real-time status updates
- Clean, responsive interface
- No JavaScript errors

---

## 🎯 **Frontend Success Criteria**

**100% Working Frontend Should Have:**
- ✅ Smooth login/logout flow
- ✅ All tabs navigable
- ✅ Enhanced crawling configuration visible
- ✅ Job creation with all 6 enhanced features
- ✅ Real-time job status updates
- ✅ Working modals (details, results)
- ✅ Responsive design
- ✅ Error handling
- ✅ No console errors

**🎉 If all tests pass: React frontend is fully functional!**
