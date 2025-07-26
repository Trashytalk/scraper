"""
Comprehensive Testing Strategy Implementation
Advanced testing infrastructure with unit tests, integration tests, end-to-end tests,
performance testing, and automated CI/CD validation
"""

import pytest
import asyncio
import unittest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import tempfile
import shutil
import os
import json
import time
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import concurrent.futures
import psutil
import threading
from contextlib import contextmanager

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Test execution result"""
    test_name: str
    status: str  # PASS, FAIL, SKIP
    duration: float
    error_message: Optional[str] = None
    details: Dict[str, Any] = None


@dataclass
class TestSuite:
    """Test suite configuration"""
    name: str
    test_files: List[str]
    test_type: str  # unit, integration, e2e, performance
    parallel: bool = False
    timeout: int = 300  # seconds
    required_services: List[str] = None


class TestEnvironmentManager:
    """Manage test environments and dependencies"""
    
    def __init__(self):
        self.temp_dirs = []
        self.running_processes = []
        self.test_databases = {}
        self.mock_services = {}
    
    @contextmanager
    def test_environment(self, config: Dict[str, Any]):
        """Create isolated test environment"""
        try:
            # Setup test environment
            self._setup_test_database(config.get('database'))
            self._setup_test_files(config.get('files', {}))
            self._setup_mock_services(config.get('services', []))
            
            yield self
            
        finally:
            # Cleanup test environment
            self._cleanup_environment()
    
    def _setup_test_database(self, db_config: Optional[Dict]):
        """Setup test database"""
        if not db_config:
            return
        
        db_name = f"test_{int(time.time())}_{os.getpid()}.db"
        db_path = os.path.join(tempfile.gettempdir(), db_name)
        
        # Create test database
        conn = sqlite3.connect(db_path)
        
        # Load schema if provided
        if 'schema_file' in db_config:
            with open(db_config['schema_file'], 'r') as f:
                schema = f.read()
                conn.executescript(schema)
        
        # Load test data if provided
        if 'test_data' in db_config:
            for table, data in db_config['test_data'].items():
                self._insert_test_data(conn, table, data)
        
        conn.commit()
        conn.close()
        
        self.test_databases['main'] = db_path
        
        # Set environment variable for tests
        os.environ['TEST_DATABASE_PATH'] = db_path
    
    def _setup_test_files(self, files_config: Dict[str, str]):
        """Setup test files and directories"""
        test_dir = tempfile.mkdtemp(prefix="test_")
        self.temp_dirs.append(test_dir)
        
        for filename, content in files_config.items():
            file_path = os.path.join(test_dir, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(content)
        
        os.environ['TEST_FILES_DIR'] = test_dir
    
    def _setup_mock_services(self, services: List[str]):
        """Setup mock external services"""
        for service in services:
            if service == 'api_server':
                mock_server = self._create_mock_api_server()
                self.mock_services[service] = mock_server
            elif service == 'database':
                # Database already setup above
                pass
            # Add more services as needed
    
    def _create_mock_api_server(self) -> Mock:
        """Create mock API server"""
        from unittest.mock import Mock
        
        mock_server = Mock()
        mock_server.get.return_value.json.return_value = {"status": "ok"}
        mock_server.post.return_value.json.return_value = {"id": "test_id"}
        
        return mock_server
    
    def _insert_test_data(self, conn: sqlite3.Connection, table: str, data: List[Dict]):
        """Insert test data into database table"""
        if not data:
            return
        
        # Get column names from first row
        columns = list(data[0].keys())
        placeholders = ', '.join(['?' for _ in columns])
        
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        
        for row in data:
            values = [row[col] for col in columns]
            conn.execute(query, values)
    
    def _cleanup_environment(self):
        """Cleanup test environment"""
        # Remove temporary directories
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        
        # Remove test databases
        for db_path in self.test_databases.values():
            if os.path.exists(db_path):
                os.remove(db_path)
        
        # Stop mock services
        for service in self.mock_services.values():
            if hasattr(service, 'stop'):
                service.stop()
        
        # Clean environment variables
        test_env_vars = [key for key in os.environ.keys() if key.startswith('TEST_')]
        for var in test_env_vars:
            del os.environ[var]


class UnitTestFramework:
    """Advanced unit testing framework"""
    
    def __init__(self):
        self.test_env = TestEnvironmentManager()
        self.results = []
    
    def run_unit_tests(self, test_directory: str, pattern: str = "test_*.py") -> List[TestResult]:
        """Run unit tests with comprehensive reporting"""
        logger.info(f"Running unit tests from {test_directory}")
        
        # Discover test files
        test_files = self._discover_tests(test_directory, pattern)
        
        results = []
        for test_file in test_files:
            result = self._run_test_file(test_file)
            results.extend(result)
        
        return results
    
    def _discover_tests(self, directory: str, pattern: str) -> List[str]:
        """Discover test files matching pattern"""
        test_files = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    test_files.append(os.path.join(root, file))
        
        return test_files
    
    def _run_test_file(self, test_file: str) -> List[TestResult]:
        """Run individual test file"""
        results = []
        
        try:
            # Import test module
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_module", test_file)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            # Find test classes and methods
            test_cases = self._find_test_cases(test_module)
            
            for test_case in test_cases:
                result = self._run_test_case(test_case)
                results.append(result)
                
        except Exception as e:
            results.append(TestResult(
                test_name=test_file,
                status="FAIL",
                duration=0.0,
                error_message=str(e)
            ))
        
        return results
    
    def _find_test_cases(self, module) -> List[Tuple[str, callable]]:
        """Find test cases in module"""
        test_cases = []
        
        for name in dir(module):
            obj = getattr(module, name)
            
            # Check for test classes
            if (isinstance(obj, type) and 
                issubclass(obj, unittest.TestCase) and 
                name.startswith('Test')):
                
                # Get test methods
                for method_name in dir(obj):
                    if method_name.startswith('test_'):
                        test_cases.append((f"{name}.{method_name}", getattr(obj, method_name)))
            
            # Check for standalone test functions
            elif callable(obj) and name.startswith('test_'):
                test_cases.append((name, obj))
        
        return test_cases
    
    def _run_test_case(self, test_case: Tuple[str, callable]) -> TestResult:
        """Run individual test case"""
        test_name, test_func = test_case
        
        start_time = time.time()
        try:
            # Setup test environment if needed
            if hasattr(test_func, '_test_config'):
                config = test_func._test_config
                with self.test_env.test_environment(config):
                    test_func()
            else:
                test_func()
            
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status="PASS",
                duration=duration
            )
            
        except unittest.SkipTest as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status="SKIP",
                duration=duration,
                error_message=str(e)
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status="FAIL",
                duration=duration,
                error_message=str(e)
            )


class IntegrationTestFramework:
    """Integration testing framework"""
    
    def __init__(self):
        self.services = {}
        self.test_env = TestEnvironmentManager()
    
    async def run_integration_tests(self, test_suites: List[TestSuite]) -> Dict[str, List[TestResult]]:
        """Run integration test suites"""
        logger.info("Starting integration tests")
        
        results = {}
        
        for suite in test_suites:
            logger.info(f"Running integration suite: {suite.name}")
            
            # Start required services
            await self._start_services(suite.required_services or [])
            
            try:
                suite_results = await self._run_test_suite(suite)
                results[suite.name] = suite_results
            finally:
                # Stop services
                await self._stop_services()
        
        return results
    
    async def _start_services(self, services: List[str]):
        """Start required services for testing"""
        for service in services:
            if service == 'backend_server':
                await self._start_backend_server()
            elif service == 'database':
                await self._start_test_database()
            elif service == 'redis':
                await self._start_redis()
            # Add more services as needed
    
    async def _start_backend_server(self):
        """Start backend server for testing"""
        import subprocess
        
        # Start server in background
        process = subprocess.Popen(
            ['python', 'backend_server.py', '--test-mode'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.services['backend'] = process
        
        # Wait for server to start
        await asyncio.sleep(2)
        
        # Verify server is running
        try:
            response = requests.get('http://localhost:8000/health', timeout=5)
            if response.status_code != 200:
                raise Exception("Backend server failed to start")
        except requests.exceptions.RequestException:
            raise Exception("Backend server not responding")
    
    async def _start_test_database(self):
        """Start test database"""
        # This would typically start a containerized database
        # For now, we'll use SQLite
        db_path = tempfile.mktemp(suffix='.db')
        
        conn = sqlite3.connect(db_path)
        # Load schema
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.close()
        
        os.environ['TEST_DATABASE_URL'] = f'sqlite:///{db_path}'
        self.services['database'] = db_path
    
    async def _start_redis(self):
        """Start Redis for testing"""
        # This would typically start a Redis container
        # For testing, we can use a mock Redis
        from unittest.mock import Mock
        
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True
        
        self.services['redis'] = mock_redis
    
    async def _run_test_suite(self, suite: TestSuite) -> List[TestResult]:
        """Run a test suite"""
        results = []
        
        if suite.parallel:
            # Run tests in parallel
            tasks = []
            for test_file in suite.test_files:
                task = asyncio.create_task(self._run_integration_test(test_file))
                tasks.append(task)
            
            suite_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in suite_results:
                if isinstance(result, Exception):
                    results.append(TestResult(
                        test_name="parallel_test",
                        status="FAIL",
                        duration=0.0,
                        error_message=str(result)
                    ))
                else:
                    results.extend(result)
        else:
            # Run tests sequentially
            for test_file in suite.test_files:
                test_results = await self._run_integration_test(test_file)
                results.extend(test_results)
        
        return results
    
    async def _run_integration_test(self, test_file: str) -> List[TestResult]:
        """Run individual integration test"""
        # This would run pytest or similar on the test file
        import subprocess
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', test_file, '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                return [TestResult(
                    test_name=test_file,
                    status="PASS",
                    duration=duration,
                    details={"output": result.stdout}
                )]
            else:
                return [TestResult(
                    test_name=test_file,
                    status="FAIL",
                    duration=duration,
                    error_message=result.stderr,
                    details={"output": result.stdout}
                )]
                
        except subprocess.TimeoutExpired:
            return [TestResult(
                test_name=test_file,
                status="FAIL",
                duration=time.time() - start_time,
                error_message="Test timeout"
            )]
        except Exception as e:
            return [TestResult(
                test_name=test_file,
                status="FAIL",
                duration=time.time() - start_time,
                error_message=str(e)
            )]
    
    async def _stop_services(self):
        """Stop all test services"""
        for service_name, service in self.services.items():
            try:
                if hasattr(service, 'terminate'):
                    service.terminate()
                    service.wait(timeout=10)
                elif isinstance(service, str) and service_name == 'database':
                    # Remove test database file
                    if os.path.exists(service):
                        os.remove(service)
            except Exception as e:
                logger.warning(f"Error stopping service {service_name}: {e}")
        
        self.services.clear()


class EndToEndTestFramework:
    """End-to-end testing with browser automation"""
    
    def __init__(self):
        self.driver = None
        self.services = IntegrationTestFramework()
    
    async def run_e2e_tests(self, test_scenarios: List[Dict]) -> List[TestResult]:
        """Run end-to-end test scenarios"""
        logger.info("Starting end-to-end tests")
        
        # Start all required services
        await self.services._start_services(['backend_server', 'database'])
        
        # Setup browser
        self._setup_browser()
        
        results = []
        
        try:
            for scenario in test_scenarios:
                result = await self._run_e2e_scenario(scenario)
                results.append(result)
        finally:
            # Cleanup
            if self.driver:
                self.driver.quit()
            await self.services._stop_services()
        
        return results
    
    def _setup_browser(self):
        """Setup browser for testing"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            logger.warning(f"Chrome driver not available: {e}")
            # Fallback to Firefox or skip browser tests
            self.driver = None
    
    async def _run_e2e_scenario(self, scenario: Dict) -> TestResult:
        """Run individual E2E scenario"""
        start_time = time.time()
        
        if not self.driver:
            return TestResult(
                test_name=scenario['name'],
                status="SKIP",
                duration=0.0,
                error_message="Browser driver not available"
            )
        
        try:
            # Execute test steps
            for step in scenario['steps']:
                await self._execute_step(step)
            
            duration = time.time() - start_time
            return TestResult(
                test_name=scenario['name'],
                status="PASS",
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=scenario['name'],
                status="FAIL",
                duration=duration,
                error_message=str(e)
            )
    
    async def _execute_step(self, step: Dict):
        """Execute individual test step"""
        action = step['action']
        
        if action == 'navigate':
            self.driver.get(step['url'])
            
        elif action == 'click':
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, step['selector']))
            )
            element.click()
            
        elif action == 'type':
            element = self.driver.find_element(By.CSS_SELECTOR, step['selector'])
            element.clear()
            element.send_keys(step['text'])
            
        elif action == 'wait':
            await asyncio.sleep(step['seconds'])
            
        elif action == 'assert_text':
            element = self.driver.find_element(By.CSS_SELECTOR, step['selector'])
            assert step['expected'] in element.text
            
        elif action == 'assert_visible':
            element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, step['selector']))
            )
            
        elif action == 'screenshot':
            filename = step.get('filename', f"screenshot_{int(time.time())}.png")
            self.driver.save_screenshot(filename)


class PerformanceTestFramework:
    """Performance and load testing framework"""
    
    def __init__(self):
        self.metrics = {}
        self.services = IntegrationTestFramework()
    
    async def run_performance_tests(self, test_configs: List[Dict]) -> Dict[str, Any]:
        """Run performance test suite"""
        logger.info("Starting performance tests")
        
        # Start services
        await self.services._start_services(['backend_server', 'database'])
        
        results = {}
        
        try:
            for config in test_configs:
                test_name = config['name']
                logger.info(f"Running performance test: {test_name}")
                
                result = await self._run_performance_test(config)
                results[test_name] = result
                
        finally:
            await self.services._stop_services()
        
        return results
    
    async def _run_performance_test(self, config: Dict) -> Dict[str, Any]:
        """Run individual performance test"""
        test_type = config['type']
        
        if test_type == 'load':
            return await self._run_load_test(config)
        elif test_type == 'stress':
            return await self._run_stress_test(config)
        elif test_type == 'endurance':
            return await self._run_endurance_test(config)
        elif test_type == 'spike':
            return await self._run_spike_test(config)
        else:
            raise ValueError(f"Unknown performance test type: {test_type}")
    
    async def _run_load_test(self, config: Dict) -> Dict[str, Any]:
        """Run load test with specified concurrent users"""
        users = config['concurrent_users']
        duration = config['duration_seconds']
        endpoint = config['endpoint']
        
        logger.info(f"Load test: {users} users for {duration}s on {endpoint}")
        
        start_time = time.time()
        response_times = []
        error_count = 0
        success_count = 0
        
        # Track system metrics
        cpu_usage = []
        memory_usage = []
        
        async def make_request():
            nonlocal error_count, success_count
            
            request_start = time.time()
            try:
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=30)
                response_time = time.time() - request_start
                
                if response.status_code == 200:
                    success_count += 1
                    response_times.append(response_time)
                else:
                    error_count += 1
                    
            except Exception:
                error_count += 1
        
        # Monitor system resources
        def monitor_system():
            while time.time() - start_time < duration:
                cpu_usage.append(psutil.cpu_percent())
                memory_usage.append(psutil.virtual_memory().percent)
                time.sleep(1)
        
        # Start system monitoring
        monitor_thread = threading.Thread(target=monitor_system)
        monitor_thread.start()
        
        # Run load test
        tasks = []
        end_time = start_time + duration
        
        while time.time() < end_time:
            # Create batch of concurrent requests
            batch_tasks = []
            for _ in range(min(users, 50)):  # Limit batch size
                task = asyncio.create_task(make_request())
                batch_tasks.append(task)
            
            await asyncio.gather(*batch_tasks, return_exceptions=True)
            await asyncio.sleep(0.1)  # Small delay between batches
        
        # Wait for monitoring to complete
        monitor_thread.join()
        
        # Calculate metrics
        total_requests = success_count + error_count
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        requests_per_second = total_requests / duration
        error_rate = (error_count / total_requests) * 100 if total_requests > 0 else 0
        
        # Response time percentiles
        if response_times:
            response_times.sort()
            p50 = response_times[int(len(response_times) * 0.5)]
            p95 = response_times[int(len(response_times) * 0.95)]
            p99 = response_times[int(len(response_times) * 0.99)]
        else:
            p50 = p95 = p99 = 0
        
        return {
            'total_requests': total_requests,
            'successful_requests': success_count,
            'failed_requests': error_count,
            'requests_per_second': requests_per_second,
            'error_rate_percent': error_rate,
            'avg_response_time': avg_response_time,
            'response_time_p50': p50,
            'response_time_p95': p95,
            'response_time_p99': p99,
            'avg_cpu_usage': sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0,
            'max_cpu_usage': max(cpu_usage) if cpu_usage else 0,
            'avg_memory_usage': sum(memory_usage) / len(memory_usage) if memory_usage else 0,
            'max_memory_usage': max(memory_usage) if memory_usage else 0,
            'duration': duration
        }
    
    async def _run_stress_test(self, config: Dict) -> Dict[str, Any]:
        """Run stress test with increasing load"""
        max_users = config['max_users']
        ramp_up_time = config['ramp_up_seconds']
        endpoint = config['endpoint']
        
        logger.info(f"Stress test: ramping up to {max_users} users over {ramp_up_time}s")
        
        results = []
        
        # Gradually increase load
        for users in range(1, max_users + 1, max(1, max_users // 10)):
            test_config = {
                'concurrent_users': users,
                'duration_seconds': 30,
                'endpoint': endpoint
            }
            
            result = await self._run_load_test(test_config)
            result['concurrent_users'] = users
            results.append(result)
            
            # Check if system is failing
            if result['error_rate_percent'] > 50:
                logger.warning(f"High error rate at {users} users, stopping stress test")
                break
        
        return {
            'test_type': 'stress',
            'max_users_tested': max(r['concurrent_users'] for r in results),
            'breaking_point': next(
                (r['concurrent_users'] for r in results if r['error_rate_percent'] > 20),
                None
            ),
            'detailed_results': results
        }
    
    async def _run_endurance_test(self, config: Dict) -> Dict[str, Any]:
        """Run endurance test over extended period"""
        users = config['concurrent_users']
        duration = config['duration_seconds']  # Should be much longer, e.g., 3600s
        endpoint = config['endpoint']
        
        logger.info(f"Endurance test: {users} users for {duration}s")
        
        # Run test in smaller intervals to track degradation
        interval = 300  # 5 minutes
        results = []
        
        start_time = time.time()
        while time.time() - start_time < duration:
            remaining_time = min(interval, duration - (time.time() - start_time))
            
            test_config = {
                'concurrent_users': users,
                'duration_seconds': int(remaining_time),
                'endpoint': endpoint
            }
            
            result = await self._run_load_test(test_config)
            result['elapsed_time'] = time.time() - start_time
            results.append(result)
        
        return {
            'test_type': 'endurance',
            'total_duration': duration,
            'performance_degradation': self._calculate_degradation(results),
            'detailed_results': results
        }
    
    async def _run_spike_test(self, config: Dict) -> Dict[str, Any]:
        """Run spike test with sudden load increase"""
        normal_users = config['normal_users']
        spike_users = config['spike_users']
        spike_duration = config['spike_duration_seconds']
        endpoint = config['endpoint']
        
        logger.info(f"Spike test: {normal_users} → {spike_users} users for {spike_duration}s")
        
        results = []
        
        # Normal load
        normal_config = {
            'concurrent_users': normal_users,
            'duration_seconds': 60,
            'endpoint': endpoint
        }
        normal_result = await self._run_load_test(normal_config)
        normal_result['phase'] = 'normal'
        results.append(normal_result)
        
        # Spike load
        spike_config = {
            'concurrent_users': spike_users,
            'duration_seconds': spike_duration,
            'endpoint': endpoint
        }
        spike_result = await self._run_load_test(spike_config)
        spike_result['phase'] = 'spike'
        results.append(spike_result)
        
        # Recovery
        recovery_config = {
            'concurrent_users': normal_users,
            'duration_seconds': 60,
            'endpoint': endpoint
        }
        recovery_result = await self._run_load_test(recovery_config)
        recovery_result['phase'] = 'recovery'
        results.append(recovery_result)
        
        return {
            'test_type': 'spike',
            'recovery_time': self._calculate_recovery_time(results),
            'spike_impact': spike_result['error_rate_percent'],
            'detailed_results': results
        }
    
    def _calculate_degradation(self, results: List[Dict]) -> float:
        """Calculate performance degradation over time"""
        if len(results) < 2:
            return 0.0
        
        first_result = results[0]
        last_result = results[-1]
        
        # Compare response times
        degradation = (
            (last_result['avg_response_time'] - first_result['avg_response_time']) /
            first_result['avg_response_time']
        ) * 100
        
        return max(0.0, degradation)
    
    def _calculate_recovery_time(self, results: List[Dict]) -> float:
        """Calculate recovery time after spike"""
        normal_phase = next(r for r in results if r['phase'] == 'normal')
        recovery_phase = next(r for r in results if r['phase'] == 'recovery')
        
        # Compare error rates
        normal_error_rate = normal_phase['error_rate_percent']
        recovery_error_rate = recovery_phase['error_rate_percent']
        
        if recovery_error_rate <= normal_error_rate * 1.1:  # Within 10% of normal
            return 0.0  # Immediate recovery
        else:
            return 60.0  # Assume 1 minute if not recovered


class TestReportGenerator:
    """Generate comprehensive test reports"""
    
    def __init__(self):
        self.report_data = {}
    
    def generate_report(self, test_results: Dict[str, Any]) -> str:
        """Generate comprehensive test report"""
        report = []
        
        # Header
        report.append("# Comprehensive Test Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        
        # Summary
        total_tests = sum(len(results) for results in test_results.values() if isinstance(results, list))
        passed_tests = sum(
            sum(1 for r in results if r.status == "PASS")
            for results in test_results.values()
            if isinstance(results, list)
        )
        failed_tests = total_tests - passed_tests
        
        report.append("## Test Summary")
        report.append(f"- Total Tests: {total_tests}")
        report.append(f"- Passed: {passed_tests}")
        report.append(f"- Failed: {failed_tests}")
        report.append(f"- Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "- Success Rate: N/A")
        report.append("")
        
        # Detailed results by category
        for category, results in test_results.items():
            report.append(f"## {category.title()} Tests")
            
            if isinstance(results, list):
                # Standard test results
                for result in results:
                    status_icon = "✅" if result.status == "PASS" else "❌" if result.status == "FAIL" else "⏭️"
                    report.append(f"- {status_icon} {result.test_name} ({result.duration:.2f}s)")
                    if result.error_message:
                        report.append(f"  Error: {result.error_message}")
            
            elif isinstance(results, dict):
                # Performance test results
                if category == "performance":
                    for test_name, result in results.items():
                        report.append(f"### {test_name}")
                        if 'requests_per_second' in result:
                            report.append(f"- Requests/sec: {result['requests_per_second']:.2f}")
                            report.append(f"- Error rate: {result['error_rate_percent']:.2f}%")
                            report.append(f"- Avg response time: {result['avg_response_time']:.3f}s")
                            report.append(f"- 95th percentile: {result['response_time_p95']:.3f}s")
            
            report.append("")
        
        return "\n".join(report)
    
    def generate_html_report(self, test_results: Dict[str, Any]) -> str:
        """Generate HTML test report"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .pass { color: green; }
                .fail { color: red; }
                .skip { color: orange; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
        """
        
        html += f"<h1>Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h1>"
        
        # Add test results tables
        for category, results in test_results.items():
            html += f"<h2>{category.title()} Tests</h2>"
            
            if isinstance(results, list):
                html += "<table><tr><th>Test Name</th><th>Status</th><th>Duration</th><th>Error</th></tr>"
                
                for result in results:
                    status_class = result.status.lower()
                    error_msg = result.error_message or ""
                    
                    html += f"""
                    <tr>
                        <td>{result.test_name}</td>
                        <td class="{status_class}">{result.status}</td>
                        <td>{result.duration:.2f}s</td>
                        <td>{error_msg}</td>
                    </tr>
                    """
                
                html += "</table>"
        
        html += "</body></html>"
        return html


# Usage example and main test runner
class TestRunner:
    """Main test runner orchestrating all test types"""
    
    def __init__(self):
        self.unit_framework = UnitTestFramework()
        self.integration_framework = IntegrationTestFramework()
        self.e2e_framework = EndToEndTestFramework()
        self.performance_framework = PerformanceTestFramework()
        self.report_generator = TestReportGenerator()
    
    async def run_all_tests(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        logger.info("Starting comprehensive test suite")
        
        results = {}
        
        # Unit tests
        if config.get('run_unit_tests', True):
            unit_results = self.unit_framework.run_unit_tests(
                config.get('unit_test_dir', 'tests/unit')
            )
            results['unit'] = unit_results
        
        # Integration tests
        if config.get('run_integration_tests', True):
            integration_suites = config.get('integration_suites', [])
            integration_results = await self.integration_framework.run_integration_tests(integration_suites)
            results['integration'] = integration_results
        
        # End-to-end tests
        if config.get('run_e2e_tests', True):
            e2e_scenarios = config.get('e2e_scenarios', [])
            e2e_results = await self.e2e_framework.run_e2e_tests(e2e_scenarios)
            results['e2e'] = e2e_results
        
        # Performance tests
        if config.get('run_performance_tests', True):
            performance_configs = config.get('performance_configs', [])
            performance_results = await self.performance_framework.run_performance_tests(performance_configs)
            results['performance'] = performance_results
        
        return results
    
    def generate_reports(self, results: Dict[str, Any], output_dir: str = "test_reports"):
        """Generate test reports"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Text report
        text_report = self.report_generator.generate_report(results)
        with open(os.path.join(output_dir, "test_report.txt"), 'w') as f:
            f.write(text_report)
        
        # HTML report
        html_report = self.report_generator.generate_html_report(results)
        with open(os.path.join(output_dir, "test_report.html"), 'w') as f:
            f.write(html_report)
        
        # JSON report for CI/CD
        with open(os.path.join(output_dir, "test_results.json"), 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Test reports generated in {output_dir}")


# Example configuration and usage
if __name__ == "__main__":
    # Test configuration
    test_config = {
        'run_unit_tests': True,
        'run_integration_tests': True,
        'run_e2e_tests': True,
        'run_performance_tests': True,
        
        'unit_test_dir': 'tests/unit',
        
        'integration_suites': [
            TestSuite(
                name="API Tests",
                test_files=["tests/integration/test_api.py"],
                test_type="integration",
                required_services=["backend_server", "database"]
            ),
            TestSuite(
                name="Database Tests", 
                test_files=["tests/integration/test_database.py"],
                test_type="integration",
                required_services=["database"]
            )
        ],
        
        'e2e_scenarios': [
            {
                'name': 'User Login Flow',
                'steps': [
                    {'action': 'navigate', 'url': 'http://localhost:3000/login'},
                    {'action': 'type', 'selector': '#username', 'text': 'testuser'},
                    {'action': 'type', 'selector': '#password', 'text': 'testpass'},
                    {'action': 'click', 'selector': '#login-button'},
                    {'action': 'assert_visible', 'selector': '#dashboard'}
                ]
            }
        ],
        
        'performance_configs': [
            {
                'name': 'API Load Test',
                'type': 'load',
                'concurrent_users': 50,
                'duration_seconds': 120,
                'endpoint': '/api/data'
            },
            {
                'name': 'Search Stress Test',
                'type': 'stress', 
                'max_users': 200,
                'ramp_up_seconds': 300,
                'endpoint': '/api/search'
            }
        ]
    }
    
    # Run tests
    async def main():
        runner = TestRunner()
        results = await runner.run_all_tests(test_config)
        runner.generate_reports(results)
        
        # Print summary
        print("\n" + "="*50)
        print("TEST EXECUTION COMPLETE")
        print("="*50)
        
        for category, category_results in results.items():
            if isinstance(category_results, list):
                total = len(category_results)
                passed = sum(1 for r in category_results if r.status == "PASS")
                print(f"{category.upper()}: {passed}/{total} passed")
        
        print("="*50)
    
    # Run the test suite
    asyncio.run(main())
