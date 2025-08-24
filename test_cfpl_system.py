#!/usr/bin/env python3
"""
CFPL System Test & Validation
Comprehensive test of the Capture-First, Process-Later implementation
"""

import asyncio
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from storage.cas_store import CASStore
from storage.capture_engine import CFPLCaptureEngine
from storage.config import CFPLConfig, CFPLConfigManager
from storage.processors import ProcessingPipeline
from storage.cfpl_integration import CFPLScrapingEngine


class CFPLSystemTest:
    """Comprehensive CFPL system test"""
    
    def __init__(self):
        self.temp_storage = None
        self.config = None
        self.test_results = {
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_skipped": 0,
            "errors": []
        }
    
    def setup_test_environment(self):
        """Setup temporary test environment"""
        print("🔧 Setting up test environment...")
        
        # Create temporary storage directory
        self.temp_storage = tempfile.mkdtemp(prefix="cfpl_test_")
        print(f"   Test storage: {self.temp_storage}")
        
        # Create test configuration
        self.config = CFPLConfig()
        self.config.storage.root = self.temp_storage
        self.config.limits.concurrent_fetches = 2
        self.config.limits.timeout_sec = 10
        self.config.limits.max_content_bytes = 10 * 1024 * 1024  # 10MB
        
        print("✅ Test environment ready")
    
    def cleanup_test_environment(self):
        """Cleanup test environment"""
        if self.temp_storage and os.path.exists(self.temp_storage):
            try:
                shutil.rmtree(self.temp_storage)
                print(f"🧹 Cleaned up test storage: {self.temp_storage}")
            except Exception as e:
                print(f"⚠️  Warning: Failed to cleanup {self.temp_storage}: {e}")
    
    def assert_test(self, condition: bool, test_name: str, error_msg: str = ""):
        """Assert test condition and track results"""
        if condition:
            print(f"✅ {test_name}")
            self.test_results["tests_passed"] += 1
            return True
        else:
            print(f"❌ {test_name}: {error_msg}")
            self.test_results["tests_failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {error_msg}")
            return False
    
    async def test_cas_store_basic(self):
        """Test basic CAS store functionality"""
        print("\n📦 Testing CAS Store Basic Operations...")
        
        cas_store = CASStore(self.temp_storage)
        
        # Test content storage
        test_content = b"Hello, CFPL World!"
        content_hash = cas_store.store_content(test_content, "text/plain")
        
        self.assert_test(
            len(content_hash) == 64,
            "CAS content storage returns valid SHA256 hash",
            f"Expected 64 chars, got {len(content_hash)}"
        )
        
        # Test content retrieval
        retrieved_content = cas_store.retrieve_content(content_hash)
        
        self.assert_test(
            retrieved_content == test_content,
            "CAS content retrieval matches original",
            f"Retrieved content doesn't match original"
        )
        
        # Test deduplication
        duplicate_hash = cas_store.store_content(test_content, "text/plain")
        
        self.assert_test(
            content_hash == duplicate_hash,
            "CAS deduplication works correctly",
            f"Duplicate content got different hash: {duplicate_hash}"
        )
        
        # Test stats
        stats = cas_store.get_storage_stats()
        
        self.assert_test(
            stats["storage"]["total_objects"] >= 1,
            "CAS storage statistics work",
            f"Expected >= 1 object, got {stats['storage']['total_objects']}"
        )
    
    async def test_capture_engine_single_url(self):
        """Test capture engine with single URL"""
        print("\n🎯 Testing Capture Engine Single URL...")
        
        test_url = "https://httpbin.org/html"  # Simple test endpoint
        
        async with CFPLCaptureEngine(self.config) as engine:
            run_id = engine.start_run("test_single_url")
            
            self.assert_test(
                run_id.startswith("cfpl_"),
                "Capture engine generates valid run ID",
                f"Invalid run ID: {run_id}"
            )
            
            # Capture URL
            result = await engine.capture_url(test_url, run_id)
            
            self.assert_test(
                result["status"] == "success",
                "Single URL capture succeeds",
                f"Capture failed: {result.get('error', 'Unknown error')}"
            )
            
            if result["status"] == "success":
                self.assert_test(
                    len(result["content_hash"]) == 64,
                    "Capture returns valid content hash",
                    f"Invalid content hash: {result['content_hash']}"
                )
                
                self.assert_test(
                    os.path.exists(result["manifest_path"]),
                    "Manifest file is created",
                    f"Manifest not found: {result['manifest_path']}"
                )
    
    async def test_processing_pipeline(self):
        """Test processing pipeline"""
        print("\n⚙️ Testing Processing Pipeline...")
        
        # First capture some content
        test_url = "https://httpbin.org/html"
        
        async with CFPLCaptureEngine(self.config) as engine:
            run_id = engine.start_run("test_processing")
            capture_result = await engine.capture_url(test_url, run_id)
            
            if capture_result["status"] != "success":
                self.test_results["tests_skipped"] += 1
                print("⏭️  Skipped processing test (capture failed)")
                return
            
            # Test processing pipeline
            pipeline = ProcessingPipeline(self.config)
            
            # Process single manifest
            processing_result = await pipeline.process_manifest(
                capture_result["manifest_path"], 
                run_id
            )
            
            self.assert_test(
                "processors" in processing_result,
                "Processing pipeline returns processor results",
                "No processors key in result"
            )
            
            # Check individual processors
            processors = processing_result.get("processors", {})
            
            if "html_parser" in processors:
                html_result = processors["html_parser"]
                self.assert_test(
                    "error" not in html_result,
                    "HTML processor runs without error",
                    f"HTML processor error: {html_result.get('error', 'Unknown')}"
                )
                
                if "error" not in html_result:
                    self.assert_test(
                        "title" in html_result,
                        "HTML processor extracts title",
                        "No title in HTML processor result"
                    )
            
            if "text_extractor" in processors:
                text_result = processors["text_extractor"]
                self.assert_test(
                    "error" not in text_result,
                    "Text extractor runs without error", 
                    f"Text extractor error: {text_result.get('error', 'Unknown')}"
                )
                
                if "error" not in text_result:
                    self.assert_test(
                        text_result.get("word_count", 0) > 0,
                        "Text extractor counts words",
                        f"Word count is {text_result.get('word_count', 0)}"
                    )
    
    async def test_integration_layer(self):
        """Test CFPL integration with existing interface"""
        print("\n🔗 Testing Integration Layer...")
        
        test_url = "https://httpbin.org/html"
        
        async with CFPLScrapingEngine() as engine:
            # Override config
            engine.cfpl_config = self.config
            engine.capture_engine = CFPLCaptureEngine(self.config)
            await engine.capture_engine.__aenter__()
            
            session_id = engine.start_session("test_integration")
            
            self.assert_test(
                session_id.startswith("session_"),
                "Integration layer creates session",
                f"Invalid session ID: {session_id}"
            )
            
            # Test backward-compatible scrape_url
            result = await engine.scrape_url(test_url, "basic")
            
            self.assert_test(
                result["status"] == "success",
                "Integration layer scrape_url works",
                f"Scrape failed: {result.get('error', 'Unknown error')}"
            )
            
            if result["status"] == "success":
                self.assert_test(
                    result["cfpl_enabled"] == True,
                    "Integration layer enables CFPL flag",
                    "CFPL flag not set"
                )
                
                self.assert_test(
                    "content_hash" in result,
                    "Integration layer includes CFPL metadata",
                    "Missing CFPL metadata"
                )
                
                self.assert_test(
                    "title" in result or "content" in result,
                    "Integration layer includes processed data",
                    "Missing processed data for backward compatibility"
                )
    
    async def test_intelligent_crawl_cfpl(self):
        """Test CFPL intelligent crawling"""
        print("\n🕷️ Testing CFPL Intelligent Crawl...")
        
        # Use a simple test page with internal links
        test_url = "https://httpbin.org/"
        
        async with CFPLScrapingEngine() as engine:
            engine.cfpl_config = self.config
            engine.capture_engine = CFPLCaptureEngine(self.config)
            await engine.capture_engine.__aenter__()
            
            crawl_config = {
                "max_pages": 3,
                "max_depth": 2,
                "follow_internal_links": True,
                "follow_external_links": False
            }
            
            result = await engine.intelligent_crawl(test_url, "basic", crawl_config)
            
            self.assert_test(
                result["status"] in ["success", "completed"],
                "CFPL intelligent crawl completes",
                f"Crawl failed with status: {result.get('status', 'unknown')}"
            )
            
            if result["status"] in ["success", "completed"]:
                self.assert_test(
                    result["cfpl_enabled"] == True,
                    "Intelligent crawl enables CFPL",
                    "CFPL not enabled in crawl"
                )
                
                self.assert_test(
                    len(result["crawled_data"]) > 0,
                    "Intelligent crawl captures data",
                    f"No data captured: {len(result['crawled_data'])} pages"
                )
                
                self.assert_test(
                    len(result["manifests"]) > 0,
                    "Intelligent crawl creates manifests",
                    f"No manifests created: {len(result['manifests'])}"
                )
    
    async def test_replayability_principle(self):
        """Test that processing is replayable from stored data"""
        print("\n🔄 Testing Replayability Principle...")
        
        test_url = "https://httpbin.org/html"
        
        # Step 1: Capture and process
        async with CFPLCaptureEngine(self.config) as engine:
            run_id = engine.start_run("test_replay")
            capture_result = await engine.capture_url(test_url, run_id)
            
            if capture_result["status"] != "success":
                self.test_results["tests_skipped"] += 1
                print("⏭️  Skipped replayability test (capture failed)")
                return
            
            manifest_path = capture_result["manifest_path"]
            
            # First processing run
            pipeline = ProcessingPipeline(self.config)
            result1 = await pipeline.process_manifest(manifest_path, run_id)
            
            # Second processing run (should be identical)
            result2 = await pipeline.process_manifest(manifest_path, run_id)
            
            # Compare results (ignoring timestamps)
            def normalize_result(result):
                """Remove non-deterministic fields for comparison"""
                normalized = {}
                for key, value in result.items():
                    if key in ["processing_start", "processing_end"]:
                        continue  # Skip timestamps
                    if isinstance(value, dict):
                        if "processed_at" in value:
                            value = {k: v for k, v in value.items() if k != "processed_at"}
                        normalized[key] = value
                    else:
                        normalized[key] = value
                return normalized
            
            norm1 = normalize_result(result1)
            norm2 = normalize_result(result2)
            
            # Compare processor results
            processors1 = norm1.get("processors", {})
            processors2 = norm2.get("processors", {})
            
            identical = True
            for processor_name in processors1:
                if processor_name in processors2:
                    # Compare core extracted data
                    proc1 = processors1[processor_name]
                    proc2 = processors2[processor_name]
                    
                    if "error" not in proc1 and "error" not in proc2:
                        # Compare key fields that should be identical
                        for key in ["title", "word_count", "content_sha256"]:
                            if key in proc1 and key in proc2:
                                if proc1[key] != proc2[key]:
                                    identical = False
                                    break
            
            self.assert_test(
                identical,
                "Processing is replayable (deterministic results)",
                "Processing results differ between runs"
            )
    
    async def test_raw_derived_separation(self):
        """Test RAW/DERIVED zone separation"""
        print("\n🏛️ Testing RAW/DERIVED Separation...")
        
        cas_store = CASStore(self.temp_storage)
        
        # Check directory structure
        raw_dir = Path(self.temp_storage) / "raw"
        derived_dir = Path(self.temp_storage) / "derived"
        
        self.assert_test(
            raw_dir.exists(),
            "RAW directory exists",
            f"RAW directory not found: {raw_dir}"
        )
        
        self.assert_test(
            derived_dir.exists(),
            "DERIVED directory exists", 
            f"DERIVED directory not found: {derived_dir}"
        )
        
        # Test content storage (should go to RAW)
        test_content = b"Test content for RAW zone"
        content_hash = cas_store.store_content(test_content)
        
        cas_path = cas_store._get_cas_path(content_hash)
        
        self.assert_test(
            str(cas_path).startswith(str(raw_dir)),
            "Content stored in RAW zone",
            f"Content not in RAW: {cas_path}"
        )
        
        # Test that CAS content is read-only
        if cas_path.exists():
            stat_info = cas_path.stat()
            is_readonly = (stat_info.st_mode & 0o200) == 0  # Check if write bit is off
            
            self.assert_test(
                is_readonly,
                "CAS content is read-only",
                f"CAS file is writable: {oct(stat_info.st_mode)}"
            )
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*60)
        print("🎯 CFPL SYSTEM TEST SUMMARY")
        print("="*60)
        
        total_tests = (self.test_results["tests_passed"] + 
                      self.test_results["tests_failed"] + 
                      self.test_results["tests_skipped"])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed:   {self.test_results['tests_passed']}")
        print(f"❌ Failed:   {self.test_results['tests_failed']}")
        print(f"⏭️ Skipped:  {self.test_results['tests_skipped']}")
        
        success_rate = (self.test_results["tests_passed"] / max(total_tests, 1)) * 100
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.test_results["errors"]:
            print("\n❌ FAILED TESTS:")
            for error in self.test_results["errors"]:
                print(f"   • {error}")
        
        if self.test_results["tests_failed"] == 0:
            print("\n🎉 ALL TESTS PASSED! CFPL implementation is working correctly.")
        else:
            print(f"\n⚠️  {self.test_results['tests_failed']} TESTS FAILED. Please review the implementation.")
        
        print("="*60)


async def main():
    """Main test execution"""
    print("🧪 CFPL SYSTEM TEST SUITE")
    print("Testing Capture-First, Process-Later Implementation")
    print("="*60)
    
    test_suite = CFPLSystemTest()
    
    try:
        # Setup
        test_suite.setup_test_environment()
        
        # Run tests
        await test_suite.test_cas_store_basic()
        await test_suite.test_capture_engine_single_url()
        await test_suite.test_processing_pipeline()
        await test_suite.test_integration_layer()
        await test_suite.test_intelligent_crawl_cfpl()
        await test_suite.test_replayability_principle()
        await test_suite.test_raw_derived_separation()
        
        # Summary
        test_suite.print_test_summary()
        
        # Return appropriate exit code
        return 0 if test_suite.test_results["tests_failed"] == 0 else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n💥 Test suite crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Cleanup
        test_suite.cleanup_test_environment()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
