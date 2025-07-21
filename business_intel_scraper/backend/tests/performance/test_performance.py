"""
Performance and load testing for Phase 1 and Phase 2 systems.

Tests system performance under various load conditions.
"""
from __future__ import annotations

import pytest
import asyncio
import time
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch, AsyncMock

from business_intel_scraper.backend.discovery.automated_discovery import AutomatedDiscoveryManager
from business_intel_scraper.backend.discovery.dom_change_detection import DOMChangeDetector


class TestPhase1Performance:
    """Performance tests for Phase 1 spider discovery."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_discovery_speed_benchmark(self):
        """Benchmark discovery speed for multiple sources."""
        discovery_manager = AutomatedDiscoveryManager()
        
        urls = [f"https://example{i}.com" for i in range(50)]
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="""
                <html>
                    <body>
                        <a href="/companies">Company Registry</a>
                        <a href="/news">Business News</a>
                    </body>
                </html>
            """)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            start_time = time.time()
            
            # Test concurrent discovery
            tasks = [discovery_manager.discover_seed_sources(url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            # Performance assertions
            assert elapsed < 30.0  # Should complete within 30 seconds
            assert len([r for r in results if not isinstance(r, Exception)]) >= 40  # At least 80% success rate
            
            # Calculate throughput
            successful_discoveries = len([r for r in results if isinstance(r, list)])
            throughput = successful_discoveries / elapsed
            
            print(f"Discovery throughput: {throughput:.2f} sources/second")
            assert throughput > 1.0  # At least 1 source per second
    
    @pytest.mark.performance
    def test_memory_usage_during_discovery(self):
        """Test memory usage remains reasonable during discovery."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        discovery_manager = AutomatedDiscoveryManager()
        
        # Simulate large discovery operation
        for i in range(1000):
            # Add mock discovered sources
            discovery_manager.discovered_sources.append({
                'url': f'https://example{i}.com',
                'confidence_score': 0.8,
                'source_type': 'business_registry'
            })
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory usage increased by: {memory_increase:.2f} MB")
        assert memory_increase < 100  # Should not use more than 100MB additional memory
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_spider_execution(self):
        """Test performance of concurrent spider execution."""
        num_concurrent = 10
        
        async def mock_spider_run():
            # Simulate spider work
            await asyncio.sleep(0.1)
            return {'scraped_items': 100}
        
        start_time = time.time()
        
        # Run concurrent spiders
        tasks = [mock_spider_run() for _ in range(num_concurrent)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        assert elapsed < 2.0  # Should complete concurrently, not sequentially
        assert len(results) == num_concurrent
        assert all('scraped_items' in result for result in results)


class TestPhase2Performance:
    """Performance tests for Phase 2 DOM change detection."""
    
    @pytest.fixture
    def large_html_document(self):
        """Generate a large HTML document for testing."""
        companies = []
        for i in range(1000):
            companies.append(f"""
                <div class="company" id="comp-{i}">
                    <h2>Company {i}</h2>
                    <span class="reg-num">{i:06d}</span>
                    <div class="details">
                        <p>Address: {i} Business Street</p>
                        <p>Phone: +1-555-{i:04d}</p>
                        <p>Industry: Technology</p>
                    </div>
                </div>
            """)
        
        return f"""
        <html>
            <body>
                <div class="company-list">
                    {''.join(companies)}
                </div>
            </body>
        </html>
        """
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_dom_change_detection_speed(self, large_html_document):
        """Test DOM change detection speed with large documents."""
        dom_detector = DOMChangeDetector()
        url = "https://example.com/large-registry"
        
        # Store initial snapshot
        start_time = time.time()
        await dom_detector.store_dom_snapshot(url, large_html_document)
        snapshot_time = time.time() - start_time
        
        assert snapshot_time < 5.0  # Snapshot should complete within 5 seconds
        
        # Create modified version (add one new company)
        modified_html = large_html_document.replace(
            '</div>\n                </div>',
            '''</div>
                <div class="company" id="comp-1000">
                    <h2>New Company</h2>
                    <span class="reg-num">001000</span>
                </div>
                </div>'''
        )
        
        # Test change detection speed
        start_time = time.time()
        changes = await dom_detector.check_for_changes(url, modified_html)
        detection_time = time.time() - start_time
        
        assert detection_time < 10.0  # Detection should complete within 10 seconds
        assert len(changes) > 0  # Should detect the new company
        
        print(f"Snapshot time: {snapshot_time:.2f}s, Detection time: {detection_time:.2f}s")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_change_detection(self):
        """Test concurrent change detection across multiple sources."""
        dom_detector = DOMChangeDetector()
        
        urls = [f"https://example{i}.com" for i in range(20)]
        html_content = "<html><body><div class='content'>Test content</div></body></html>"
        
        # Store snapshots for all URLs
        for url in urls:
            await dom_detector.store_dom_snapshot(url, html_content)
        
        # Modified content
        modified_html = "<html><body><div class='new-content'>Modified content</div></body></html>"
        
        start_time = time.time()
        
        # Test concurrent change detection
        tasks = [dom_detector.check_for_changes(url, modified_html) for url in urls]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        assert elapsed < 15.0  # Should complete concurrently within reasonable time
        assert len(results) == len(urls)
        assert all(isinstance(result, list) for result in results)
        
        # Calculate throughput
        throughput = len(urls) / elapsed
        print(f"Change detection throughput: {throughput:.2f} sources/second")
        assert throughput > 1.0  # At least 1 source per second
    
    @pytest.mark.performance
    def test_memory_usage_with_many_snapshots(self):
        """Test memory usage with many stored DOM snapshots."""
        dom_detector = DOMChangeDetector()
        process = psutil.Process()
        
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Store many snapshots
        large_html = "<html><body>" + "x" * 10000 + "</body></html>"  # 10KB per snapshot
        
        for i in range(500):  # 500 snapshots = ~5MB of HTML
            asyncio.run(dom_detector.store_dom_snapshot(
                f"https://example{i}.com", 
                large_html
            ))
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory increase with 500 snapshots: {memory_increase:.2f} MB")
        assert memory_increase < 50  # Should not use excessive memory


class TestSystemLoadTesting:
    """Load testing for combined Phase 1 and Phase 2 systems."""
    
    @pytest.mark.load_test
    @pytest.mark.asyncio
    async def test_high_load_discovery_and_monitoring(self):
        """Test system under high load with both discovery and monitoring."""
        discovery_manager = AutomatedDiscoveryManager()
        dom_detector = DOMChangeDetector()
        
        # Simulate high load scenario
        num_discovery_tasks = 50
        num_monitoring_sources = 100
        
        # Set up monitoring sources
        for i in range(num_monitoring_sources):
            await dom_detector.add_monitoring_source(f"https://monitor{i}.com")
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="<html><body>Test</body></html>")
            mock_get.return_value.__aenter__.return_value = mock_response
            
            start_time = time.time()
            
            # Run concurrent discovery and monitoring
            discovery_tasks = [
                discovery_manager.discover_seed_sources(f"https://discover{i}.com") 
                for i in range(num_discovery_tasks)
            ]
            
            monitoring_task = dom_detector.check_monitoring_sources_batch(batch_size=10)
            
            # Execute all tasks concurrently
            discovery_results = await asyncio.gather(*discovery_tasks, return_exceptions=True)
            await monitoring_task
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            # Performance assertions
            assert elapsed < 60.0  # Should complete within 1 minute
            
            success_rate = len([r for r in discovery_results if not isinstance(r, Exception)]) / len(discovery_results)
            assert success_rate > 0.8  # At least 80% success rate under load
            
            print(f"High load test completed in {elapsed:.2f}s with {success_rate:.2%} success rate")
    
    @pytest.mark.load_test
    def test_cpu_usage_under_load(self):
        """Test CPU usage remains reasonable under load."""
        def cpu_intensive_task():
            # Simulate CPU-intensive spider processing
            total = 0
            for i in range(1000000):
                total += i ** 0.5
            return total
        
        # Monitor CPU usage
        process = psutil.Process()
        initial_cpu = process.cpu_percent()
        
        # Run multiple CPU-intensive tasks
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(cpu_intensive_task) for _ in range(8)]
            results = [future.result() for future in futures]
        
        final_cpu = process.cpu_percent()
        
        assert len(results) == 8  # All tasks completed
        print(f"CPU usage: {initial_cpu}% -> {final_cpu}%")
        
        # CPU usage should be reasonable (this is system-dependent)
        # Just ensure we're not hitting 100% constantly
        assert final_cpu < 95.0
    
    @pytest.mark.load_test
    def test_system_stability_under_stress(self):
        """Test system stability under stress conditions."""
        # This would implement stress testing
        # - High memory usage
        # - High CPU usage  
        # - High I/O usage
        # - Resource exhaustion scenarios
        pass


class TestPerformanceRegression:
    """Regression tests to ensure performance doesn't degrade."""
    
    @pytest.mark.performance
    def test_discovery_performance_baseline(self):
        """Establish baseline performance metrics for discovery."""
        # This would establish and check against performance baselines
        # Should be run regularly to catch performance regressions
        pass
    
    @pytest.mark.performance
    def test_change_detection_performance_baseline(self):
        """Establish baseline performance metrics for change detection."""
        # This would establish and check against performance baselines
        pass


if __name__ == "__main__":
    # Run with: pytest test_performance.py -m performance
    pytest.main([__file__, "-m", "performance", "-v"])
