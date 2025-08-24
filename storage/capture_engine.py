"""
CFPL Capture Engine
Implements single-touch URL fetching with comprehensive content capture
"""

import asyncio
import hashlib
import json
import logging
import mimetypes
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse
import uuid

import aiohttp
import aiofiles
from bs4 import BeautifulSoup

from .cas_store import CASStore
from .config import get_config, CFPLConfig

logger = logging.getLogger(__name__)


class CFPLCaptureEngine:
    """Capture engine implementing CFPL single-touch fetching"""
    
    def __init__(self, config: Optional[CFPLConfig] = None):
        self.config = config or get_config()
        self.cas_store = CASStore(self.config.storage.root)
        self.session: Optional[aiohttp.ClientSession] = None
        self._current_run_id: Optional[str] = None
        
        # Content discovery patterns
        self.asset_selectors = [
            'link[rel="stylesheet"]',  # CSS
            'script[src]',             # JavaScript
            'img[src]',                # Images
            'link[rel="icon"]',        # Favicons
            'link[rel="apple-touch-icon"]',  # Apple touch icons
        ]
        
        self.media_patterns = [
            r'\.mp4$', r'\.webm$', r'\.avi$', r'\.mov$',  # Video
            r'\.mp3$', r'\.wav$', r'\.ogg$', r'\.m4a$',   # Audio
            r'\.m3u8$', r'\.mpd$',                        # Streaming playlists
        ]
        
        # DRM detection patterns
        self.drm_indicators = [
            'widevine', 'playready', 'fairplay', 'clearkey',
            'encrypted-media', 'eme-', 'drm'
        ]

    async def __aenter__(self):
        """Async context manager entry"""
        await self._init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._close_session()

    async def _init_session(self):
        """Initialize HTTP session with proper configuration"""
        timeout = aiohttp.ClientTimeout(total=self.config.limits.timeout_sec)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        connector = aiohttp.TCPConnector(
            limit=self.config.limits.concurrent_fetches,
            limit_per_host=self.config.limits.concurrent_per_domain,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers=headers,
            connector=connector,
            max_redirects=self.config.limits.max_redirects if self.config.capture.follow_redirects else 0
        )

    async def _close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None

    def start_run(self, run_id: Optional[str] = None) -> str:
        """Start a new capture run"""
        if not run_id:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            run_id = f"{self.config.run_id_prefix}_{timestamp}_{uuid.uuid4().hex[:8]}"
        
        self._current_run_id = run_id
        logger.info(f"Started capture run: {run_id}")
        return run_id

    async def capture_url(self, url: str, run_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Capture a single URL with all associated assets
        Implements single-touch principle: no refetching for analysis
        """
        if not self.session:
            await self._init_session()
            
        run_id = run_id or self._current_run_id
        if not run_id:
            run_id = self.start_run()

        capture_start = datetime.utcnow()
        
        # Initialize capture result
        capture_result = {
            'url': url,
            'final_url': url,
            'status': None,
            'fetch_start': capture_start.isoformat() + 'Z',
            'fetch_end': None,
            'redirects': [],
            'request_headers': {},
            'response_headers': {},
            'redacted_headers': self.config.privacy.redact_headers,
            'content': {},
            'dom_snapshot': None,
            'har_capture': None,
            'assets': [],
            'media': [],
            'tools': {
                'capture_engine_version': '1.0.0',
                'aiohttp_version': aiohttp.__version__
            },
            'capture_decisions': {},
            'errors': []
        }

        try:
            # Step 1: Fetch main content
            logger.info(f"Fetching main content: {url}")
            main_response = await self._fetch_with_metadata(url)
            
            if not main_response:
                capture_result['errors'].append("Failed to fetch main content")
                return capture_result
                
            # Store main content in CAS
            content_bytes = main_response['content']
            content_hash = self.cas_store.store_content(
                content_bytes, 
                main_response.get('content_type')
            )
            
            # Update capture result with main content info
            capture_result.update({
                'final_url': main_response['final_url'],
                'status': main_response['status'],
                'redirects': main_response['redirects'],
                'request_headers': self._redact_headers(main_response['request_headers']),
                'response_headers': self._redact_headers(main_response['response_headers']),
                'content': {
                    'sha256': content_hash,
                    'size': len(content_bytes),
                    'content_type': main_response.get('content_type', ''),
                    'encoding': main_response.get('encoding', '')
                }
            })
            
            # Step 2: Asset discovery and capture (if enabled)
            if self.config.capture.assets and self._is_html_content(main_response.get('content_type', '')):
                logger.info(f"Discovering assets for: {url}")
                assets = await self._discover_and_capture_assets(
                    content_bytes.decode(main_response.get('encoding', 'utf-8'), errors='ignore'),
                    main_response['final_url']
                )
                capture_result['assets'] = assets
                
                # Step 3: Media discovery and capture
                media_items = await self._discover_and_capture_media(
                    content_bytes.decode(main_response.get('encoding', 'utf-8'), errors='ignore'),
                    main_response['final_url']
                )
                capture_result['media'] = media_items

            # Step 4: DOM snapshot (if enabled and HTML content)
            if (self.config.capture.render_dom and 
                self._is_html_content(main_response.get('content_type', ''))):
                logger.info(f"Capturing DOM snapshot for: {url}")
                dom_snapshot = await self._capture_dom_snapshot(url)
                if dom_snapshot:
                    capture_result['dom_snapshot'] = dom_snapshot

            # Step 5: HAR capture (if enabled)
            if self.config.capture.har:
                logger.info(f"Capturing HAR data for: {url}")
                har_data = await self._capture_har_data(url)
                if har_data:
                    capture_result['har_capture'] = har_data

            capture_result['fetch_end'] = datetime.utcnow().isoformat() + 'Z'
            
            # Step 6: Create manifest (RAW write barrier)
            logger.info(f"Creating manifest for: {url}")
            manifest_path = self.cas_store.create_manifest(run_id, url, capture_result)
            
            logger.info(f"Successfully captured: {url} -> {manifest_path}")
            return {
                'status': 'success',
                'manifest_path': manifest_path,
                'content_hash': content_hash,
                'assets_captured': len(capture_result['assets']),
                'media_captured': len(capture_result['media']),
                'capture_result': capture_result
            }

        except Exception as e:
            logger.error(f"Capture failed for {url}: {str(e)}")
            capture_result['errors'].append(str(e))
            capture_result['fetch_end'] = datetime.utcnow().isoformat() + 'Z'
            
            return {
                'status': 'error',
                'error': str(e),
                'capture_result': capture_result
            }

    async def _fetch_with_metadata(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch URL with comprehensive metadata capture"""
        redirects = []
        
        try:
            async with self.session.get(url, allow_redirects=True) as response:
                # Track redirects
                if response.history:
                    for redirect in response.history:
                        redirects.append({
                            'from': str(redirect.url),
                            'to': str(redirect.url),  # This will be updated in chain
                            'status': redirect.status
                        })
                
                # Check content size limits
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > self.config.limits.max_content_bytes:
                    logger.warning(f"Content too large: {content_length} bytes for {url}")
                    return None
                
                # Read content with size limit
                content_bytes = b''
                bytes_read = 0
                
                async for chunk in response.content.iter_chunked(8192):
                    bytes_read += len(chunk)
                    if bytes_read > self.config.limits.max_content_bytes:
                        logger.warning(f"Content size limit exceeded for {url}")
                        break
                    content_bytes += chunk
                
                # Determine encoding
                encoding = 'utf-8'
                content_type = response.headers.get('content-type', '')
                if 'charset=' in content_type:
                    try:
                        encoding = content_type.split('charset=')[1].split(';')[0].strip()
                    except:
                        encoding = 'utf-8'
                
                return {
                    'content': content_bytes,
                    'status': response.status,
                    'final_url': str(response.url),
                    'redirects': redirects,
                    'request_headers': dict(response.request_info.headers),
                    'response_headers': dict(response.headers),
                    'content_type': content_type,
                    'encoding': encoding
                }
                
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return None

    async def _discover_and_capture_assets(self, html_content: str, base_url: str) -> List[Dict[str, Any]]:
        """Discover and capture all assets from HTML content"""
        assets = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract different types of assets
            asset_urls = set()
            
            # CSS files
            for link in soup.find_all('link', rel='stylesheet'):
                href = link.get('href')
                if href:
                    asset_urls.add(urljoin(base_url, href))
            
            # JavaScript files
            for script in soup.find_all('script', src=True):
                src = script.get('src')
                if src:
                    asset_urls.add(urljoin(base_url, src))
            
            # Images
            for img in soup.find_all('img', src=True):
                src = img.get('src')
                if src:
                    asset_urls.add(urljoin(base_url, src))
                    
            # Favicons and icons
            for link in soup.find_all('link', rel=['icon', 'apple-touch-icon', 'shortcut icon']):
                href = link.get('href')
                if href:
                    asset_urls.add(urljoin(base_url, href))
            
            # Capture assets concurrently with semaphore for rate limiting
            semaphore = asyncio.Semaphore(self.config.limits.concurrent_fetches)
            
            async def capture_single_asset(asset_url: str) -> Optional[Dict[str, Any]]:
                async with semaphore:
                    try:
                        # Rate limiting
                        await asyncio.sleep(1.0 / self.config.limits.rate_limit_rps)
                        
                        response = await self._fetch_with_metadata(asset_url)
                        if not response:
                            return None
                        
                        # Store in CAS
                        content_hash = self.cas_store.store_content(
                            response['content'],
                            response.get('content_type')
                        )
                        
                        return {
                            'url': asset_url,
                            'sha256': content_hash,
                            'size': len(response['content']),
                            'content_type': response.get('content_type', ''),
                            'discovered_via': 'html_parsing',
                            'status': response['status']
                        }
                        
                    except Exception as e:
                        logger.warning(f"Failed to capture asset {asset_url}: {str(e)}")
                        return None
            
            # Execute asset capture concurrently
            asset_tasks = [capture_single_asset(url) for url in asset_urls]
            asset_results = await asyncio.gather(*asset_tasks, return_exceptions=True)
            
            # Filter successful captures
            for result in asset_results:
                if isinstance(result, dict) and result:
                    assets.append(result)
                    
        except Exception as e:
            logger.error(f"Asset discovery failed: {str(e)}")
        
        logger.info(f"Captured {len(assets)} assets")
        return assets

    async def _discover_and_capture_media(self, html_content: str, base_url: str) -> List[Dict[str, Any]]:
        """Discover and capture media content"""
        media_items = []
        
        if self.config.capture.media == "off":
            return media_items
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            media_urls = set()
            
            # Video elements
            for video in soup.find_all('video'):
                # Direct video sources
                src = video.get('src')
                if src:
                    media_urls.add(urljoin(base_url, src))
                
                # Source elements within video
                for source in video.find_all('source'):
                    src = source.get('src')
                    if src:
                        media_urls.add(urljoin(base_url, src))
            
            # Audio elements  
            for audio in soup.find_all('audio'):
                src = audio.get('src')
                if src:
                    media_urls.add(urljoin(base_url, src))
                    
                for source in audio.find_all('source'):
                    src = source.get('src')
                    if src:
                        media_urls.add(urljoin(base_url, src))
            
            # Detect streaming playlists in script content
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # Look for HLS playlist URLs
                    hls_matches = re.findall(r'["\']([^"\']*\.m3u8[^"\']*)["\']', script.string)
                    for match in hls_matches:
                        media_urls.add(urljoin(base_url, match))
            
            # Capture media files
            for media_url in media_urls:
                try:
                    # Check for DRM before attempting capture
                    if self._detect_drm(media_url):
                        logger.info(f"DRM detected, skipping: {media_url}")
                        media_items.append({
                            'url': media_url,
                            'status': 'skipped',
                            'reason': 'drm_detected',
                            'capture_method': 'none'
                        })
                        continue
                    
                    # Attempt direct network capture
                    if self._is_playlist_url(media_url):
                        media_item = await self._capture_hls_playlist(media_url)
                    else:
                        media_item = await self._capture_direct_media(media_url)
                    
                    if media_item:
                        media_items.append(media_item)
                        
                except Exception as e:
                    logger.warning(f"Failed to capture media {media_url}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Media discovery failed: {str(e)}")
        
        logger.info(f"Captured {len(media_items)} media items")
        return media_items

    async def _capture_direct_media(self, media_url: str) -> Optional[Dict[str, Any]]:
        """Capture direct media file"""
        try:
            response = await self._fetch_with_metadata(media_url)
            if not response:
                return None
            
            # Check if content is too large
            if len(response['content']) > self.config.limits.max_asset_bytes:
                logger.warning(f"Media file too large: {len(response['content'])} bytes for {media_url}")
                return None
            
            # Store in CAS
            content_hash = self.cas_store.store_content(
                response['content'],
                response.get('content_type')
            )
            
            return {
                'url': media_url,
                'sha256': content_hash,
                'size': len(response['content']),
                'content_type': response.get('content_type', ''),
                'capture_method': 'direct_download'
            }
            
        except Exception as e:
            logger.error(f"Direct media capture failed for {media_url}: {str(e)}")
            return None

    async def _capture_hls_playlist(self, playlist_url: str) -> Optional[Dict[str, Any]]:
        """Capture HLS playlist and all segments"""
        try:
            # Fetch playlist
            response = await self._fetch_with_metadata(playlist_url)
            if not response:
                return None
            
            playlist_content = response['content'].decode('utf-8', errors='ignore')
            
            # Store playlist in CAS
            playlist_hash = self.cas_store.store_content(
                response['content'],
                'application/vnd.apple.mpegurl'
            )
            
            # Parse playlist for segment URLs
            segments = []
            base_url = '/'.join(playlist_url.split('/')[:-1]) + '/'
            
            for line in playlist_content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    segment_url = urljoin(base_url, line)
                    
                    # Capture segment
                    try:
                        segment_response = await self._fetch_with_metadata(segment_url)
                        if segment_response:
                            segment_hash = self.cas_store.store_content(
                                segment_response['content'],
                                segment_response.get('content_type', 'video/mp2t')
                            )
                            
                            segments.append({
                                'url': segment_url,
                                'sha256': segment_hash,
                                'size': len(segment_response['content'])
                            })
                    except Exception as e:
                        logger.warning(f"Failed to capture segment {segment_url}: {str(e)}")
            
            return {
                'url': playlist_url,
                'sha256': playlist_hash,
                'size': len(response['content']),
                'content_type': 'application/vnd.apple.mpegurl',
                'capture_method': 'hls_playlist',
                'segments': segments,
                'segment_count': len(segments)
            }
            
        except Exception as e:
            logger.error(f"HLS playlist capture failed for {playlist_url}: {str(e)}")
            return None

    async def _capture_dom_snapshot(self, url: str) -> Optional[Dict[str, Any]]:
        """Capture rendered DOM snapshot (placeholder - would integrate with Playwright)"""
        # This is a placeholder for DOM snapshot functionality
        # In a full implementation, this would use Playwright or similar
        logger.info(f"DOM snapshot capture not yet implemented for: {url}")
        return None

    async def _capture_har_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Capture HAR (HTTP Archive) data (placeholder - would integrate with browser automation)"""
        # This is a placeholder for HAR capture functionality
        # In a full implementation, this would use Playwright or similar
        logger.info(f"HAR capture not yet implemented for: {url}")
        return None

    def _redact_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Redact sensitive headers based on privacy configuration"""
        redacted = {}
        redact_list = [h.lower() for h in self.config.privacy.redact_headers]
        
        for key, value in headers.items():
            if key.lower() in redact_list:
                redacted[key] = '[REDACTED]'
            else:
                redacted[key] = value
                
        return redacted

    def _is_html_content(self, content_type: str) -> bool:
        """Check if content type is HTML"""
        return 'text/html' in content_type.lower()

    def _is_playlist_url(self, url: str) -> bool:
        """Check if URL is a streaming playlist"""
        return url.lower().endswith(('.m3u8', '.mpd'))

    def _detect_drm(self, url: str) -> bool:
        """Detect if content likely has DRM protection"""
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in self.drm_indicators)


# Convenience function for single URL capture
async def capture_single_url(url: str, config: Optional[CFPLConfig] = None) -> Dict[str, Any]:
    """Capture a single URL with CFPL engine"""
    async with CFPLCaptureEngine(config) as engine:
        return await engine.capture_url(url)
