// COMPREHENSIVE FRONTEND MODAL TESTING SCRIPT
// Copy and paste this entire script into the browser console

console.log('🧪 Starting Comprehensive Frontend Modal Testing...');

// Test configuration
const testConfig = {
    jobName: 'BBC Business Test Job',
    timeout: 5000,
    maxRetries: 3
};

// Test state
const testState = {
    results: {},
    logs: [],
    startTime: Date.now()
};

// Utility functions
const log = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = `[${timestamp}] ${message}`;
    console.log(logEntry);
    testState.logs.push({ timestamp, message, type });
};

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Test functions
const tests = {
    // Test 1: Check if page is loaded
    async checkPageLoaded() {
        log('🔍 Test 1: Checking if page is loaded...');
        try {
            const hasTitle = document.title && document.title.length > 0;
            const hasBody = document.body && document.body.children.length > 0;
            const result = hasTitle && hasBody;
            
            log(`Page title: "${document.title}"`);
            log(`Body elements: ${document.body ? document.body.children.length : 0}`);
            log(result ? '✅ Page loaded successfully' : '❌ Page not properly loaded');
            
            return result;
        } catch (error) {
            log(`❌ Page load check failed: ${error.message}`, 'error');
            return false;
        }
    },

    // Test 2: Check authentication state
    async checkAuthentication() {
        log('🔐 Test 2: Checking authentication state...');
        try {
            // Look for login form or dashboard elements
            const loginForm = document.querySelector('form[name="login"], input[name="username"], input[type="password"]');
            const dashboardElements = document.querySelectorAll('h1, h2, .dashboard, [class*="dashboard"]');
            
            const isLoggedIn = !loginForm && dashboardElements.length > 0;
            
            log(`Login form present: ${!!loginForm}`);
            log(`Dashboard elements: ${dashboardElements.length}`);
            log(isLoggedIn ? '✅ User appears to be logged in' : '⚠️ User may need to log in');
            
            return isLoggedIn;
        } catch (error) {
            log(`❌ Authentication check failed: ${error.message}`, 'error');
            return false;
        }
    },

    // Test 3: Find job elements
    async findJobElements() {
        log('🔍 Test 3: Looking for job elements...');
        try {
            // Look for job-related elements
            const jobSelectors = [
                '[class*="job"]',
                '[data-job-id]',
                '*[class*="Job"]',
                'div:contains("BBC")',
                'div:contains("Job")',
                'tr:contains("Job")'
            ];
            
            let totalElements = 0;
            let bbcElements = 0;
            
            for (const selector of jobSelectors) {
                try {
                    const elements = document.querySelectorAll(selector);
                    totalElements += elements.length;
                    
                    // Check for BBC-related content
                    elements.forEach(el => {
                        if (el.textContent && el.textContent.includes('BBC')) {
                            bbcElements++;
                        }
                    });
                } catch (e) {
                    // Selector might not be valid, skip
                }
            }
            
            // Also check text content for jobs
            const allText = document.body.textContent || '';
            const hasJobText = allText.includes('Job') || allText.includes('job');
            const hasBBCText = allText.includes('BBC');
            
            log(`Job-related elements found: ${totalElements}`);
            log(`BBC-related elements found: ${bbcElements}`);
            log(`Page contains job text: ${hasJobText}`);
            log(`Page contains BBC text: ${hasBBCText}`);
            
            const result = totalElements > 0 || hasJobText;
            log(result ? '✅ Job elements found' : '❌ No job elements found');
            
            return result;
        } catch (error) {
            log(`❌ Job element search failed: ${error.message}`, 'error');
            return false;
        }
    },

    // Test 4: Find and test Details buttons
    async testDetailsButtons() {
        log('📋 Test 4: Testing Details buttons...');
        try {
            // Find Details buttons
            const detailsButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
                btn.textContent && btn.textContent.includes('Details')
            );
            
            log(`Details buttons found: ${detailsButtons.length}`);
            
            if (detailsButtons.length === 0) {
                log('❌ No Details buttons found');
                return false;
            }
            
            // Test clicking the first Details button
            const button = detailsButtons[0];
            log(`Clicking Details button: "${button.textContent.trim()}"`);
            
            // Set up modal detection
            const originalModalCount = document.querySelectorAll('div[style*="position: fixed"]').length;
            log(`Modals before click: ${originalModalCount}`);
            
            // Click the button
            button.click();
            
            // Wait for modal to appear
            await sleep(1000);
            
            // Check for modal
            const modalsAfter = document.querySelectorAll('div[style*="position: fixed"]');
            const modalAppeared = modalsAfter.length > originalModalCount;
            
            log(`Modals after click: ${modalsAfter.length}`);
            log(modalAppeared ? '✅ Details modal appeared' : '❌ Details modal did not appear');
            
            // If modal appeared, try to close it
            if (modalAppeared) {
                const modal = modalsAfter[modalsAfter.length - 1];
                const closeButtons = modal.querySelectorAll('button');
                const closeButton = Array.from(closeButtons).find(btn => 
                    btn.textContent.includes('Close') || btn.textContent.includes('✕') || btn.textContent.includes('×')
                );
                
                if (closeButton) {
                    log('Closing modal...');
                    closeButton.click();
                    await sleep(500);
                }
            }
            
            return modalAppeared;
        } catch (error) {
            log(`❌ Details button test failed: ${error.message}`, 'error');
            return false;
        }
    },

    // Test 5: Find and test View Results buttons
    async testResultsButtons() {
        log('📊 Test 5: Testing View Results buttons...');
        try {
            // Find View Results buttons
            const resultsButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
                btn.textContent && (btn.textContent.includes('View Results') || btn.textContent.includes('Results'))
            );
            
            log(`View Results buttons found: ${resultsButtons.length}`);
            
            if (resultsButtons.length === 0) {
                log('❌ No View Results buttons found');
                return false;
            }
            
            // Test clicking the first View Results button
            const button = resultsButtons[0];
            log(`Clicking View Results button: "${button.textContent.trim()}"`);
            
            // Set up modal detection
            const originalModalCount = document.querySelectorAll('div[style*="position: fixed"]').length;
            log(`Modals before click: ${originalModalCount}`);
            
            // Click the button
            button.click();
            
            // Wait for modal to appear
            await sleep(1000);
            
            // Check for modal
            const modalsAfter = document.querySelectorAll('div[style*="position: fixed"]');
            const modalAppeared = modalsAfter.length > originalModalCount;
            
            log(`Modals after click: ${modalsAfter.length}`);
            log(modalAppeared ? '✅ View Results modal appeared' : '❌ View Results modal did not appear');
            
            // If modal appeared, try to close it
            if (modalAppeared) {
                const modal = modalsAfter[modalsAfter.length - 1];
                const closeButtons = modal.querySelectorAll('button');
                const closeButton = Array.from(closeButtons).find(btn => 
                    btn.textContent.includes('Close') || btn.textContent.includes('✕') || btn.textContent.includes('×')
                );
                
                if (closeButton) {
                    log('Closing modal...');
                    closeButton.click();
                    await sleep(500);
                }
            }
            
            return modalAppeared;
        } catch (error) {
            log(`❌ View Results button test failed: ${error.message}`, 'error');
            return false;
        }
    },

    // Test 6: Check for JavaScript errors
    async checkForErrors() {
        log('🚨 Test 6: Checking for JavaScript errors...');
        try {
            // This is a basic check - real errors would be caught by error handlers
            const hasErrors = testState.logs.some(log => log.type === 'error');
            
            log(hasErrors ? '⚠️ JavaScript errors detected in testing' : '✅ No JavaScript errors detected in testing');
            
            return !hasErrors;
        } catch (error) {
            log(`❌ Error check failed: ${error.message}`, 'error');
            return false;
        }
    },

    // Test 7: API call monitoring
    async monitorAPICalls() {
        log('🌐 Test 7: Setting up API call monitoring...');
        try {
            // Intercept fetch for monitoring
            const originalFetch = window.fetch;
            const apiCalls = [];
            
            window.fetch = function(...args) {
                const url = args[0];
                const startTime = Date.now();
                
                log(`🌐 API Call initiated: ${url}`);
                
                return originalFetch.apply(this, arguments)
                    .then(response => {
                        const duration = Date.now() - startTime;
                        apiCalls.push({
                            url,
                            status: response.status,
                            duration,
                            timestamp: new Date().toISOString()
                        });
                        
                        log(`📥 API Response: ${response.status} for ${url} (${duration}ms)`);
                        return response;
                    })
                    .catch(error => {
                        const duration = Date.now() - startTime;
                        apiCalls.push({
                            url,
                            error: error.message,
                            duration,
                            timestamp: new Date().toISOString()
                        });
                        
                        log(`❌ API Error: ${error.message} for ${url} (${duration}ms)`, 'error');
                        throw error;
                    });
            };
            
            // Store reference for later reporting
            window.testAPICalls = apiCalls;
            
            log('✅ API monitoring set up successfully');
            return true;
        } catch (error) {
            log(`❌ API monitoring setup failed: ${error.message}`, 'error');
            return false;
        }
    }
};

// Main test runner
async function runAllTests() {
    log('🚀 Starting comprehensive frontend modal testing...');
    
    const testResults = {};
    const testOrder = [
        'checkPageLoaded',
        'checkAuthentication', 
        'monitorAPICalls',
        'findJobElements',
        'testDetailsButtons',
        'testResultsButtons',
        'checkForErrors'
    ];
    
    for (const testName of testOrder) {
        log(`\n--- Running ${testName} ---`);
        try {
            testResults[testName] = await tests[testName]();
        } catch (error) {
            log(`❌ Test ${testName} threw an error: ${error.message}`, 'error');
            testResults[testName] = false;
        }
        
        // Small delay between tests
        await sleep(500);
    }
    
    // Generate final report
    generateReport(testResults);
    
    return testResults;
}

function generateReport(testResults) {
    const totalTests = Object.keys(testResults).length;
    const passedTests = Object.values(testResults).filter(Boolean).length;
    const passRate = (passedTests / totalTests * 100).toFixed(1);
    
    log('\n' + '='.repeat(60));
    log('📋 FINAL TEST REPORT');
    log('='.repeat(60));
    
    log(`🎯 OVERALL SCORE: ${passedTests}/${totalTests} tests passed (${passRate}%)`);
    log(`⏱️ Total testing time: ${((Date.now() - testState.startTime) / 1000).toFixed(1)}s`);
    
    log('\n📊 DETAILED RESULTS:');
    for (const [testName, result] of Object.entries(testResults)) {
        const status = result ? '✅ PASS' : '❌ FAIL';
        const formattedName = testName.replace(/([A-Z])/g, ' $1').toLowerCase();
        log(`  ${formattedName}: ${status}`);
    }
    
    // API Calls Summary
    if (window.testAPICalls && window.testAPICalls.length > 0) {
        log('\n🌐 API CALLS SUMMARY:');
        for (const call of window.testAPICalls) {
            const status = call.status || `Error: ${call.error}`;
            log(`  ${call.url} → ${status}`);
        }
    }
    
    // Recommendations
    log('\n💡 RECOMMENDATIONS:');
    if (passRate === 100) {
        log('  🎉 All tests passed! Modal functionality is working perfectly.');
    } else if (passRate >= 80) {
        log('  ⚠️ Most tests passed but some issues need attention.');
    } else if (passRate >= 50) {
        log('  🚨 Significant issues detected. Modal functionality needs fixes.');
    } else {
        log('  🆘 Critical issues detected. Major debugging required.');
    }
    
    if (!testResults.checkAuthentication) {
        log('  🔑 Ensure you are logged in before running tests');
    }
    if (!testResults.findJobElements) {
        log('  📝 Create test jobs or check job list rendering');
    }
    if (!testResults.testDetailsButtons) {
        log('  🔍 Debug Details button and modal functionality');
    }
    if (!testResults.testResultsButtons) {
        log('  📊 Debug View Results button and modal functionality');
    }
    
    log('\n✅ Testing complete! Check the logs above for detailed information.');
}

// Auto-run tests
log('🎯 Frontend Modal Testing Script Loaded');
log('💡 Run runAllTests() to start testing, or individual tests like tests.testDetailsButtons()');

// Auto-start testing after a short delay
setTimeout(() => {
    log('🚀 Auto-starting tests in 3 seconds...');
    setTimeout(runAllTests, 3000);
}, 1000);
