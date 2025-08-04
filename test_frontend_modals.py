#!/usr/bin/env python3
"""
Frontend Modal Testing Script
Conducts comprehensive frontend testing using browser automation
"""

import json
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class FrontendModalTester:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.base_url = "http://localhost:5173"
        self.test_results = {}

    def setup_browser(self):
        """Set up Chrome browser with debugging options"""
        print("🌐 Setting up browser...")
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        # chrome_options.add_argument('--headless')  # Uncomment for headless mode

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            print("✅ Browser setup complete")
            return True
        except Exception as e:
            print(f"❌ Browser setup failed: {e}")
            return False

    def inject_debug_script(self):
        """Inject our debugging JavaScript into the page"""
        print("🔧 Injecting debug script...")
        debug_script = """
        // Modal Debug Tracker
        window.modalDebugger = {
            clickCount: 0,
            apiCalls: [],
            modalsDetected: [],
            errors: []
        };
        
        // Track button clicks
        document.addEventListener('click', (event) => {
            if (event.target.tagName === 'BUTTON') {
                const buttonText = event.target.textContent.trim();
                console.log(`🖱️ Button clicked: "${buttonText}"`);
                window.modalDebugger.clickCount++;
                
                if (buttonText.includes('Details') || buttonText.includes('View Results')) {
                    console.log('🎯 MODAL TRIGGER BUTTON CLICKED!');
                    
                    // Check for modal after delay
                    setTimeout(() => {
                        const modals = document.querySelectorAll('div[style*="position: fixed"]');
                        console.log(`📊 Modals found: ${modals.length}`);
                        window.modalDebugger.modalsDetected.push({
                            button: buttonText,
                            timestamp: Date.now(),
                            modalCount: modals.length,
                            modals: Array.from(modals).map(m => m.outerHTML.substring(0, 200))
                        });
                        
                        if (modals.length === 0) {
                            console.log('❌ NO MODAL APPEARED!');
                        } else {
                            console.log('✅ Modal appeared successfully!');
                        }
                    }, 500);
                }
            }
        });
        
        // Track API calls
        const origFetch = window.fetch;
        window.fetch = function(...args) {
            const url = args[0];
            console.log(`🌐 API Call: ${url}`);
            
            const callInfo = {
                url: url,
                timestamp: Date.now(),
                status: null,
                error: null
            };
            
            return origFetch.apply(this, arguments)
                .then(response => {
                    callInfo.status = response.status;
                    window.modalDebugger.apiCalls.push(callInfo);
                    console.log(`📥 API Response: ${response.status} for ${url}`);
                    return response;
                })
                .catch(error => {
                    callInfo.error = error.toString();
                    window.modalDebugger.apiCalls.push(callInfo);
                    console.log(`❌ API Error: ${error}`);
                    throw error;
                });
        };
        
        // Track JavaScript errors
        window.addEventListener('error', (event) => {
            console.log('🚨 JavaScript Error:', event.error);
            window.modalDebugger.errors.push({
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                timestamp: Date.now()
            });
        });
        
        console.log('🔧 Debug script injected successfully');
        """

        try:
            self.driver.execute_script(debug_script)
            print("✅ Debug script injected")
            return True
        except Exception as e:
            print(f"❌ Debug script injection failed: {e}")
            return False

    def login(self):
        """Login to the application"""
        print("🔐 Logging in...")
        try:
            # Navigate to login page
            self.driver.get(self.base_url)
            time.sleep(2)

            # Find and fill login form
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            login_button = self.driver.find_element(By.TYPE, "submit")

            username_field.send_keys("admin")
            password_field.send_keys("admin123")
            login_button.click()

            # Wait for dashboard to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            print("✅ Login successful")
            return True

        except TimeoutException:
            print("❌ Login timeout - elements not found")
            return False
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False

    def find_test_job(self):
        """Find the test job (BBC Business Test Job)"""
        print("🔍 Looking for test job...")
        try:
            # Look for job with "BBC" in the name
            job_elements = self.driver.find_elements(
                By.XPATH, "//*[contains(text(), 'BBC')]"
            )

            if job_elements:
                print(f"✅ Found {len(job_elements)} BBC-related elements")
                return True
            else:
                # Look for any job elements
                job_rows = self.driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class, 'job') or contains(text(), 'Job')]",
                )
                print(f"ℹ️ Found {len(job_rows)} general job elements")
                return len(job_rows) > 0

        except Exception as e:
            print(f"❌ Error finding test job: {e}")
            return False

    def test_details_button(self):
        """Test the Details button functionality"""
        print("🔍 Testing Details button...")
        try:
            # Find Details buttons
            details_buttons = self.driver.find_elements(
                By.XPATH, "//button[contains(text(), 'Details')]"
            )

            if not details_buttons:
                print("❌ No Details buttons found")
                return False

            print(f"✅ Found {len(details_buttons)} Details buttons")

            # Click the first Details button
            details_buttons[0].click()
            print("🖱️ Details button clicked")

            # Wait for modal to appear
            time.sleep(1)

            # Check for modal
            modals = self.driver.find_elements(
                By.XPATH, "//div[contains(@style, 'position: fixed')]"
            )

            if modals:
                print(f"✅ Details modal appeared! Found {len(modals)} modals")

                # Check modal content
                modal_text = modals[0].text
                if "Job Details" in modal_text or "Details" in modal_text:
                    print("✅ Modal contains expected content")
                else:
                    print("⚠️ Modal content may be unexpected")

                # Test close button
                close_buttons = modals[0].find_elements(
                    By.XPATH, ".//button[contains(text(), 'Close')]"
                )
                if close_buttons:
                    close_buttons[0].click()
                    print("✅ Close button clicked")
                    time.sleep(0.5)

                return True
            else:
                print("❌ No modal appeared after clicking Details button")
                return False

        except Exception as e:
            print(f"❌ Details button test failed: {e}")
            return False

    def test_results_button(self):
        """Test the View Results button functionality"""
        print("📊 Testing View Results button...")
        try:
            # Find View Results buttons
            results_buttons = self.driver.find_elements(
                By.XPATH,
                "//button[contains(text(), 'View Results') or contains(text(), 'Results')]",
            )

            if not results_buttons:
                print("❌ No View Results buttons found")
                return False

            print(f"✅ Found {len(results_buttons)} View Results buttons")

            # Click the first View Results button
            results_buttons[0].click()
            print("🖱️ View Results button clicked")

            # Wait for modal to appear
            time.sleep(1)

            # Check for modal
            modals = self.driver.find_elements(
                By.XPATH, "//div[contains(@style, 'position: fixed')]"
            )

            if modals:
                print(f"✅ Results modal appeared! Found {len(modals)} modals")

                # Check modal content
                modal_text = modals[0].text
                if "Results" in modal_text or "data" in modal_text.lower():
                    print("✅ Modal contains expected content")
                else:
                    print("⚠️ Modal content may be unexpected")

                # Test close button
                close_buttons = modals[0].find_elements(
                    By.XPATH,
                    ".//button[contains(text(), 'Close') or contains(text(), '✕')]",
                )
                if close_buttons:
                    close_buttons[0].click()
                    print("✅ Close button clicked")
                    time.sleep(0.5)

                return True
            else:
                print("❌ No modal appeared after clicking View Results button")
                return False

        except Exception as e:
            print(f"❌ View Results button test failed: {e}")
            return False

    def get_debug_info(self):
        """Get debugging information from the injected script"""
        print("📊 Collecting debug information...")
        try:
            debug_info = self.driver.execute_script("return window.modalDebugger;")
            return debug_info
        except Exception as e:
            print(f"❌ Failed to get debug info: {e}")
            return None

    def get_console_logs(self):
        """Get browser console logs"""
        print("📝 Collecting console logs...")
        try:
            logs = self.driver.get_log("browser")
            return logs
        except Exception as e:
            print(f"❌ Failed to get console logs: {e}")
            return []

    def run_comprehensive_test(self):
        """Run the complete test suite"""
        print("🧪 Starting Comprehensive Frontend Modal Testing")
        print("=" * 60)

        # Setup
        if not self.setup_browser():
            return False

        try:
            # Test 1: Login
            self.test_results["login"] = self.login()
            if not self.test_results["login"]:
                print("❌ Cannot proceed without login")
                return False

            # Test 2: Inject debugging
            self.test_results["debug_injection"] = self.inject_debug_script()

            # Test 3: Find test job
            self.test_results["job_found"] = self.find_test_job()

            # Test 4: Test Details button
            self.test_results["details_modal"] = self.test_details_button()

            # Test 5: Test Results button
            self.test_results["results_modal"] = self.test_results_button()

            # Test 6: Get debug information
            debug_info = self.get_debug_info()
            console_logs = self.get_console_logs()

            # Generate report
            self.generate_report(debug_info, console_logs)

            return True

        finally:
            # Cleanup
            if self.driver:
                self.driver.quit()

    def generate_report(self, debug_info, console_logs):
        """Generate comprehensive test report"""
        print("\n📋 COMPREHENSIVE TEST REPORT")
        print("=" * 60)

        # Test Results Summary
        print("🎯 TEST RESULTS SUMMARY:")
        for test, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test.replace('_', ' ').title()}: {status}")

        # Debug Information
        if debug_info:
            print(f"\n🔧 DEBUG INFORMATION:")
            print(f"  Button Clicks: {debug_info.get('clickCount', 0)}")
            print(f"  API Calls: {len(debug_info.get('apiCalls', []))}")
            print(f"  Modals Detected: {len(debug_info.get('modalsDetected', []))}")
            print(f"  JavaScript Errors: {len(debug_info.get('errors', []))}")

            # API Calls Detail
            if debug_info.get("apiCalls"):
                print(f"\n🌐 API CALLS:")
                for call in debug_info["apiCalls"]:
                    status = call.get("status", "Error")
                    print(f"  {call['url']} → {status}")

            # Modal Detection Detail
            if debug_info.get("modalsDetected"):
                print(f"\n📊 MODAL DETECTIONS:")
                for modal in debug_info["modalsDetected"]:
                    print(f"  {modal['button']} → {modal['modalCount']} modals")

            # Errors Detail
            if debug_info.get("errors"):
                print(f"\n🚨 JAVASCRIPT ERRORS:")
                for error in debug_info["errors"]:
                    print(
                        f"  {error['message']} at {error['filename']}:{error['lineno']}"
                    )

        # Console Logs
        if console_logs:
            print(f"\n📝 CONSOLE LOGS ({len(console_logs)} entries):")
            for log in console_logs[-10:]:  # Show last 10 logs
                print(f"  [{log['level']}] {log['message']}")

        # Overall Assessment
        print(f"\n🏆 OVERALL ASSESSMENT:")
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())

        if passed_tests == total_tests:
            print("  🎉 ALL TESTS PASSED! Modal functionality is working correctly.")
        elif passed_tests >= total_tests * 0.7:
            print("  ⚠️ Most tests passed but some issues detected.")
        else:
            print(
                "  🚨 Multiple test failures - modal functionality has serious issues."
            )

        print(
            f"  Test Score: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)"
        )


def main():
    """Run the frontend testing"""
    tester = FrontendModalTester()
    success = tester.run_comprehensive_test()

    if success:
        print("\n✅ Frontend testing completed successfully!")
    else:
        print("\n❌ Frontend testing encountered errors!")


if __name__ == "__main__":
    main()
