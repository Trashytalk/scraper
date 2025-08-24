"""
CFPL Integration Layer
Integrates CFPL capture with the existing scraping engine
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from storage.capture_engine import CFPLCaptureEngine
from storage.config import get_config
from storage.processors import ProcessingPipeline

logger = logging.getLogger(__name__)


class CFPLScrapingEngine:
    """
    Enhanced scraping engine that implements CFPL principles
    Drop-in replacement for the original ScrapingEngine
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.cfpl_config = get_config()
        if config_path:
            from storage.config import CFPLConfigManager
            config_manager = CFPLConfigManager(config_path)
            self.cfpl_config = config_manager.load_config()
        
        self.capture_engine: Optional[CFPLCaptureEngine] = None
        self.processing_pipeline = ProcessingPipeline(self.cfpl_config)
        self._current_run_id: Optional[str] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.capture_engine = CFPLCaptureEngine(self.cfpl_config)
        await self.capture_engine.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.capture_engine:
            await self.capture_engine.__aexit__(exc_type, exc_val, exc_tb)

    def start_session(self, session_id: Optional[str] = None) -> str:
        """Start a new capture session"""
        if not session_id:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            session_id = f"session_{timestamp}_{uuid.uuid4().hex[:8]}"
        
        if self.capture_engine:
            self._current_run_id = self.capture_engine.start_run(session_id)
        else:
            self._current_run_id = session_id
            
        logger.info(f"Started CFPL session: {self._current_run_id}")
        return self._current_run_id

    async def scrape_url(
        self, 
        url: str, 
        scraper_type: str = "basic", 
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        CFPL-compatible scrape_url method
        Maintains backward compatibility while implementing capture-first principles
        """
        if not self.capture_engine:
            self.capture_engine = CFPLCaptureEngine(self.cfpl_config)
            await self.capture_engine.__aenter__()

        if not self._current_run_id:
            self.start_session()

        config = config or {}
        logger.info(f"CFPL scraping URL: {url} (type: {scraper_type})")

        try:
            # Step 1: Capture with CFPL engine
            capture_result = await self.capture_engine.capture_url(url, self._current_run_id)
            
            if capture_result['status'] != 'success':
                return {
                    "url": url,
                    "status": "error",
                    "error": capture_result.get('error', 'Capture failed'),
                    "timestamp": datetime.now().isoformat(),
                    "cfpl_enabled": True
                }

            # Step 2: Process immediately if requested (for backward compatibility)
            processed_data = {}
            if config.get('immediate_processing', True):
                manifest_path = capture_result['manifest_path']
                processing_result = await self.processing_pipeline.process_manifest(
                    manifest_path, self._current_run_id
                )
                
                # Extract relevant data for backward compatibility
                processors = processing_result.get('processors', {})
                
                if 'html_parser' in processors:
                    html_data = processors['html_parser']
                    processed_data.update({
                        "title": html_data.get('title', ''),
                        "links": [link['href'] for link in html_data.get('links', [])],
                        "images": [img['src'] for img in html_data.get('images', [])],
                        "forms": html_data.get('forms', []),
                        "meta_description": html_data.get('meta_description', ''),
                        "headings": html_data.get('headings', [])
                    })
                
                if 'text_extractor' in processors:
                    text_data = processors['text_extractor']
                    processed_data.update({
                        "content": text_data.get('main_text', ''),
                        "word_count": text_data.get('word_count', 0),
                        "reading_time": text_data.get('reading_time', 0)
                    })
                
                if 'media_metadata' in processors:
                    media_data = processors['media_metadata']
                    processed_data.update({
                        "media": media_data.get('media_items', []),
                        "media_count": media_data.get('media_count', 0)
                    })

            # Build backward-compatible response
            return {
                "url": url,
                "final_url": capture_result['capture_result']['final_url'],
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "response_code": capture_result['capture_result']['status'],
                
                # CFPL-specific metadata
                "cfpl_enabled": True,
                "run_id": self._current_run_id,
                "manifest_path": capture_result['manifest_path'],
                "content_hash": capture_result['content_hash'],
                "assets_captured": capture_result['assets_captured'],
                "media_captured": capture_result['media_captured'],
                
                # Processed data (for backward compatibility)
                **processed_data,
                
                # Raw capture metadata (for advanced users)
                "capture_metadata": {
                    "fetch_start": capture_result['capture_result']['fetch_start'],
                    "fetch_end": capture_result['capture_result']['fetch_end'],
                    "content_size": capture_result['capture_result']['content']['size'],
                    "content_type": capture_result['capture_result']['content']['content_type'],
                    "redirects": capture_result['capture_result']['redirects'],
                    "tools": capture_result['capture_result']['tools']
                }
            }

        except Exception as e:
            logger.error(f"CFPL scraping failed for {url}: {str(e)}")
            return {
                "url": url,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "cfpl_enabled": True
            }

    async def intelligent_crawl(
        self, 
        seed_url: str, 
        scraper_type: str = "basic", 
        config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        CFPL-enhanced intelligent crawling
        Maintains backward compatibility while implementing capture-first principles
        """
        config = config or {}
        
        if not self.capture_engine:
            self.capture_engine = CFPLCaptureEngine(self.cfpl_config)
            await self.capture_engine.__aenter__()

        if not self._current_run_id:
            self.start_session()

        logger.info(f"Starting CFPL intelligent crawl from: {seed_url}")

        # Enhanced crawling configuration
        max_pages = config.get("max_pages", 50)
        max_depth = config.get("max_depth", 3)
        follow_internal_links = config.get("follow_internal_links", True)
        follow_external_links = config.get("follow_external_links", False)
        
        # CFPL crawling state
        crawl_results = {
            "seed_url": seed_url,
            "job_type": "cfpl_intelligent_crawling",
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "run_id": self._current_run_id,
            "cfpl_enabled": True,
            
            "config": {
                "max_pages": max_pages,
                "max_depth": max_depth,
                "follow_internal_links": follow_internal_links,
                "follow_external_links": follow_external_links,
            },
            
            "summary": {
                "pages_processed": 0,
                "urls_discovered": 0,
                "data_extracted": 0,
                "total_crawl_time": 0,
                "errors_encountered": 0,
                "content_stored": 0,
                "manifests_created": 0
            },
            
            "crawled_data": [],
            "discovered_urls": [],
            "errors": [],
            "manifests": []
        }

        try:
            # Initialize crawling queue
            from urllib.parse import urljoin, urlparse
            import re
            
            url_queue = [{"url": seed_url, "depth": 0}]
            visited_urls = set()
            discovered_urls = set()
            
            seed_domain = urlparse(seed_url).netloc

            while url_queue and len(visited_urls) < max_pages:
                current_item = url_queue.pop(0)
                current_url = current_item["url"]
                current_depth = current_item["depth"]

                # Skip if already visited or max depth reached
                if current_url in visited_urls or current_depth > max_depth:
                    continue

                visited_urls.add(current_url)

                try:
                    # Capture with CFPL
                    capture_result = await self.capture_engine.capture_url(current_url, self._current_run_id)
                    
                    if capture_result['status'] == 'success':
                        # Process the captured data
                        manifest_path = capture_result['manifest_path']
                        processing_result = await self.processing_pipeline.process_manifest(
                            manifest_path, self._current_run_id
                        )

                        # Build page data for backward compatibility
                        page_data = {
                            "url": current_url,
                            "final_url": capture_result['capture_result']['final_url'],
                            "status": "success",
                            "timestamp": datetime.now().isoformat(),
                            "depth": current_depth,
                            
                            # CFPL metadata
                            "manifest_path": manifest_path,
                            "content_hash": capture_result['content_hash'],
                            "assets_captured": capture_result['assets_captured'],
                            "media_captured": capture_result['media_captured'],
                        }

                        # Add processed data
                        processors = processing_result.get('processors', {})
                        if 'html_parser' in processors and 'error' not in processors['html_parser']:
                            html_data = processors['html_parser']
                            page_data.update({
                                "title": html_data.get('title', ''),
                                "links": html_data.get('links', []),
                                "images": html_data.get('images', []),
                                "meta_description": html_data.get('meta_description', '')
                            })
                            
                            # Extract links for further crawling
                            if current_depth < max_depth:
                                for link in html_data.get('links', []):
                                    link_url = link.get('href', '') if isinstance(link, dict) else str(link)
                                    
                                    if not link_url or link_url in visited_urls:
                                        continue
                                    
                                    # Parse and filter URLs
                                    try:
                                        parsed_url = urlparse(link_url)
                                        is_internal = parsed_url.netloc == seed_domain
                                        
                                        should_follow = (
                                            (is_internal and follow_internal_links) or
                                            (not is_internal and follow_external_links)
                                        )
                                        
                                        if should_follow and link_url not in discovered_urls:
                                            discovered_urls.add(link_url)
                                            url_queue.append({
                                                "url": link_url,
                                                "depth": current_depth + 1
                                            })
                                            crawl_results["discovered_urls"].append(link_url)
                                            crawl_results["summary"]["urls_discovered"] += 1
                                    except Exception as e:
                                        logger.warning(f"Failed to parse URL {link_url}: {str(e)}")

                        if 'text_extractor' in processors and 'error' not in processors['text_extractor']:
                            text_data = processors['text_extractor']
                            page_data.update({
                                "content": text_data.get('main_text', ''),
                                "word_count": text_data.get('word_count', 0)
                            })

                        crawl_results["crawled_data"].append(page_data)
                        crawl_results["manifests"].append(manifest_path)
                        crawl_results["summary"]["pages_processed"] += 1
                        crawl_results["summary"]["data_extracted"] += 1
                        crawl_results["summary"]["content_stored"] += 1
                        crawl_results["summary"]["manifests_created"] += 1

                        logger.info(f"Successfully crawled and processed: {current_url}")

                    else:
                        error_msg = capture_result.get('error', 'Capture failed')
                        crawl_results["errors"].append({
                            "url": current_url,
                            "error": error_msg,
                            "depth": current_depth,
                            "timestamp": datetime.now().isoformat()
                        })
                        crawl_results["summary"]["errors_encountered"] += 1
                        logger.error(f"Failed to capture {current_url}: {error_msg}")

                except Exception as e:
                    error_msg = str(e)
                    crawl_results["errors"].append({
                        "url": current_url,
                        "error": error_msg,
                        "depth": current_depth,
                        "timestamp": datetime.now().isoformat()
                    })
                    crawl_results["summary"]["errors_encountered"] += 1
                    logger.error(f"Exception during crawl of {current_url}: {error_msg}")

            # Finalize results
            crawl_results["status"] = "completed"
            crawl_results["summary"]["total_crawl_time"] = "calculated_separately"  # Would calculate actual time
            
            logger.info(f"CFPL intelligent crawl completed: {crawl_results['summary']['pages_processed']} pages processed")
            return crawl_results

        except Exception as e:
            logger.error(f"CFPL intelligent crawl failed: {str(e)}")
            crawl_results["status"] = "error"
            crawl_results["error"] = str(e)
            return crawl_results

    async def process_stored_data(self, run_id: Optional[str] = None) -> Dict[str, Any]:
        """Process all stored data for a specific run"""
        target_run_id = run_id or self._current_run_id
        if not target_run_id:
            raise ValueError("No run ID specified and no current session")
        
        logger.info(f"Processing stored data for run: {target_run_id}")
        result = await self.processing_pipeline.process_run(target_run_id)
        return result

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        return self.capture_engine.cas_store.get_storage_stats() if self.capture_engine else {}

    def get_current_run_id(self) -> Optional[str]:
        """Get the current run ID"""
        return self._current_run_id


# Factory function for backward compatibility
def create_scraping_engine(use_cfpl: bool = True, config_path: Optional[str] = None):
    """
    Factory function to create either CFPL or legacy scraping engine
    """
    if use_cfpl:
        return CFPLScrapingEngine(config_path)
    else:
        # Import the original scraping engine
        from scraping_engine import ScrapingEngine
        return ScrapingEngine()


# Async context manager for backward compatibility
async def get_cfpl_scraping_engine(config_path: Optional[str] = None) -> CFPLScrapingEngine:
    """Get a ready-to-use CFPL scraping engine"""
    engine = CFPLScrapingEngine(config_path)
    await engine.__aenter__()
    return engine
