"""
CFPL Processing Pipeline
Post-capture processors that work exclusively with stored RAW data
"""

import asyncio
import json
import logging
import mimetypes
import re
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

import pandas as pd
from bs4 import BeautifulSoup

from .cas_store import CASStore
from .config import get_config, CFPLConfig

logger = logging.getLogger(__name__)


class BaseProcessor(ABC):
    """Base class for all CFPL processors"""
    
    def __init__(self, config: CFPLConfig):
        self.config = config
        self.cas_store = CASStore(config.storage.root)
        
    @abstractmethod
    async def process(self, manifest: Dict[str, Any], run_id: str) -> Dict[str, Any]:
        """Process a capture manifest and return derived data"""
        pass
    
    @property
    @abstractmethod
    def processor_name(self) -> str:
        """Name of this processor"""
        pass
    
    @property
    @abstractmethod
    def output_schema(self) -> Dict[str, Any]:
        """Schema for this processor's output"""
        pass


class HTMLProcessor(BaseProcessor):
    """Extract structured data from HTML content"""
    
    @property
    def processor_name(self) -> str:
        return "html_parser"
    
    @property 
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "meta_description": {"type": "string"},
                "headings": {"type": "array", "items": {"type": "object"}},
                "links": {"type": "array", "items": {"type": "object"}},
                "images": {"type": "array", "items": {"type": "object"}},
                "forms": {"type": "array", "items": {"type": "object"}},
                "tables": {"type": "array", "items": {"type": "object"}},
                "lang": {"type": "string"},
                "canonical_url": {"type": "string"},
                "social_meta": {"type": "object"}
            }
        }
    
    async def process(self, manifest: Dict[str, Any], run_id: str) -> Dict[str, Any]:
        """Extract structured data from HTML content"""
        try:
            # Get main content from CAS
            content_info = manifest.get('content', {})
            content_sha256 = content_info.get('sha256')
            
            if not content_sha256:
                return {"error": "No content hash in manifest"}
            
            # Check if content is HTML
            content_type = content_info.get('content_type', '')
            if 'text/html' not in content_type.lower():
                return {"error": f"Not HTML content: {content_type}"}
            
            # Retrieve content from CAS
            raw_content = self.cas_store.retrieve_content(content_sha256)
            encoding = content_info.get('encoding', 'utf-8')
            html_content = raw_content.decode(encoding, errors='ignore')
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract structured data
            result = {
                "source_manifest": manifest.get('url'),
                "content_sha256": content_sha256,
                "processed_at": datetime.utcnow().isoformat() + 'Z',
                "processor_version": "1.0.0",
                
                # Basic page metadata
                "title": self._extract_title(soup),
                "meta_description": self._extract_meta_description(soup),
                "lang": self._extract_language(soup),
                "canonical_url": self._extract_canonical_url(soup),
                
                # Content structure
                "headings": self._extract_headings(soup),
                "links": self._extract_links(soup, manifest.get('final_url', manifest.get('url'))),
                "images": self._extract_images(soup, manifest.get('final_url', manifest.get('url'))),
                "forms": self._extract_forms(soup),
                "tables": self._extract_tables(soup),
                
                # Social/SEO metadata
                "social_meta": self._extract_social_meta(soup),
                
                # Content statistics
                "stats": {
                    "text_length": len(soup.get_text()),
                    "word_count": len(soup.get_text().split()),
                    "link_count": len(soup.find_all('a')),
                    "image_count": len(soup.find_all('img')),
                    "heading_count": len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"HTML processing failed: {str(e)}")
            return {"error": str(e)}
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ""
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else ""
    
    def _extract_language(self, soup: BeautifulSoup) -> str:
        """Extract page language"""
        html_tag = soup.find('html')
        return html_tag.get('lang', '') if html_tag else ""
    
    def _extract_canonical_url(self, soup: BeautifulSoup) -> str:
        """Extract canonical URL"""
        canonical = soup.find('link', rel='canonical')
        return canonical.get('href', '') if canonical else ""
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all headings with hierarchy"""
        headings = []
        for i, heading in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
            headings.append({
                "level": int(heading.name[1]),
                "text": heading.get_text().strip(),
                "order": i + 1,
                "id": heading.get('id', ''),
                "classes": heading.get('class', [])
            })
        return headings
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract all links with metadata"""
        links = []
        for i, link in enumerate(soup.find_all('a', href=True)):
            href = link.get('href', '').strip()
            if not href:
                continue
                
            # Convert relative URLs to absolute
            from urllib.parse import urljoin
            absolute_url = urljoin(base_url, href)
            
            links.append({
                "href": absolute_url,
                "text": link.get_text().strip(),
                "title": link.get('title', ''),
                "rel": link.get('rel', []),
                "target": link.get('target', ''),
                "order": i + 1,
                "is_external": urlparse(absolute_url).netloc != urlparse(base_url).netloc
            })
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract all images with metadata"""
        images = []
        for i, img in enumerate(soup.find_all('img')):
            src = img.get('src', '').strip()
            if not src:
                continue
                
            from urllib.parse import urljoin
            absolute_url = urljoin(base_url, src)
            
            images.append({
                "src": absolute_url,
                "alt": img.get('alt', ''),
                "title": img.get('title', ''),
                "width": img.get('width', ''),
                "height": img.get('height', ''),
                "loading": img.get('loading', ''),
                "order": i + 1
            })
        return images
    
    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract form metadata"""
        forms = []
        for i, form in enumerate(soup.find_all('form')):
            form_data = {
                "action": form.get('action', ''),
                "method": form.get('method', 'get').lower(),
                "enctype": form.get('enctype', ''),
                "order": i + 1,
                "fields": []
            }
            
            # Extract form fields
            for field in form.find_all(['input', 'select', 'textarea']):
                field_data = {
                    "type": field.get('type', field.name),
                    "name": field.get('name', ''),
                    "id": field.get('id', ''),
                    "required": field.has_attr('required'),
                    "placeholder": field.get('placeholder', '')
                }
                form_data["fields"].append(field_data)
            
            forms.append(form_data)
        return forms
    
    def _extract_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract table structure"""
        tables = []
        for i, table in enumerate(soup.find_all('table')):
            table_data = {
                "order": i + 1,
                "caption": "",
                "headers": [],
                "row_count": 0,
                "column_count": 0
            }
            
            # Extract caption
            caption = table.find('caption')
            if caption:
                table_data["caption"] = caption.get_text().strip()
            
            # Extract headers
            header_row = table.find('tr')
            if header_row:
                headers = header_row.find_all(['th', 'td'])
                table_data["headers"] = [h.get_text().strip() for h in headers]
                table_data["column_count"] = len(headers)
            
            # Count rows
            rows = table.find_all('tr')
            table_data["row_count"] = len(rows)
            
            tables.append(table_data)
        return tables
    
    def _extract_social_meta(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract social media and SEO metadata"""
        social_meta = {
            "og": {},
            "twitter": {},
            "schema_org": []
        }
        
        # Open Graph metadata
        for meta in soup.find_all('meta', property=re.compile(r'^og:')):
            prop = meta.get('property')
            content = meta.get('content', '')
            social_meta["og"][prop] = content
        
        # Twitter Card metadata
        for meta in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
            name = meta.get('name')
            content = meta.get('content', '')
            social_meta["twitter"][name] = content
        
        # Schema.org structured data
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                schema_data = json.loads(script.get_text())
                social_meta["schema_org"].append(schema_data)
            except json.JSONDecodeError:
                pass
        
        return social_meta


class TextExtractor(BaseProcessor):
    """Extract clean text content from HTML"""
    
    @property
    def processor_name(self) -> str:
        return "text_extractor"
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "main_text": {"type": "string"},
                "text_blocks": {"type": "array"},
                "word_count": {"type": "integer"},
                "reading_time": {"type": "integer"},
                "language_detected": {"type": "string"}
            }
        }
    
    async def process(self, manifest: Dict[str, Any], run_id: str) -> Dict[str, Any]:
        """Extract clean text content"""
        try:
            content_info = manifest.get('content', {})
            content_sha256 = content_info.get('sha256')
            
            if not content_sha256:
                return {"error": "No content hash in manifest"}
            
            content_type = content_info.get('content_type', '')
            if 'text/html' not in content_type.lower():
                return {"error": f"Not HTML content: {content_type}"}
            
            # Retrieve and parse content
            raw_content = self.cas_store.retrieve_content(content_sha256)
            encoding = content_info.get('encoding', 'utf-8')
            html_content = raw_content.decode(encoding, errors='ignore')
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "aside"]):
                script.decompose()
            
            # Extract main text
            main_text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in main_text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            main_text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Calculate statistics
            words = main_text.split()
            word_count = len(words)
            reading_time = max(1, word_count // 200)  # Assume 200 WPM reading speed
            
            # Extract text blocks (paragraphs)
            text_blocks = []
            for i, p in enumerate(soup.find_all(['p', 'div', 'article', 'section'])):
                text = p.get_text().strip()
                if len(text) > 50:  # Only substantial text blocks
                    text_blocks.append({
                        "order": i + 1,
                        "text": text,
                        "word_count": len(text.split()),
                        "tag": p.name
                    })
            
            return {
                "source_manifest": manifest.get('url'),
                "content_sha256": content_sha256,
                "processed_at": datetime.utcnow().isoformat() + 'Z',
                "processor_version": "1.0.0",
                
                "main_text": main_text,
                "text_blocks": text_blocks,
                "word_count": word_count,
                "reading_time": reading_time,
                "character_count": len(main_text),
                "language_detected": "en"  # Placeholder - would use actual detection
            }
            
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            return {"error": str(e)}


class MediaMetadataProcessor(BaseProcessor):
    """Extract metadata from media files"""
    
    @property
    def processor_name(self) -> str:
        return "media_metadata"
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "media_items": {"type": "array"},
                "total_size": {"type": "integer"},
                "total_duration": {"type": "number"}
            }
        }
    
    async def process(self, manifest: Dict[str, Any], run_id: str) -> Dict[str, Any]:
        """Extract metadata from captured media"""
        try:
            media_items = manifest.get('media', [])
            processed_media = []
            total_size = 0
            
            for media_item in media_items:
                sha256 = media_item.get('sha256')
                if not sha256:
                    continue
                
                # Get media content for analysis
                try:
                    content = self.cas_store.retrieve_content(sha256)
                    content_type = media_item.get('content_type', '')
                    
                    # Basic metadata
                    metadata = {
                        "url": media_item.get('url'),
                        "sha256": sha256,
                        "size": len(content),
                        "content_type": content_type,
                        "capture_method": media_item.get('capture_method'),
                        "format": self._detect_format(content_type),
                        "is_streaming": media_item.get('capture_method') == 'hls_playlist'
                    }
                    
                    # Add streaming-specific metadata
                    if metadata["is_streaming"]:
                        metadata["segment_count"] = media_item.get('segment_count', 0)
                        metadata["segments"] = media_item.get('segments', [])
                    
                    processed_media.append(metadata)
                    total_size += len(content)
                    
                except Exception as e:
                    logger.warning(f"Failed to process media {sha256}: {str(e)}")
            
            return {
                "source_manifest": manifest.get('url'),
                "processed_at": datetime.utcnow().isoformat() + 'Z',
                "processor_version": "1.0.0",
                
                "media_items": processed_media,
                "media_count": len(processed_media),
                "total_size": total_size,
                "formats": list(set(item.get('format', 'unknown') for item in processed_media))
            }
            
        except Exception as e:
            logger.error(f"Media metadata extraction failed: {str(e)}")
            return {"error": str(e)}
    
    def _detect_format(self, content_type: str) -> str:
        """Detect media format from content type"""
        format_map = {
            'video/mp4': 'mp4',
            'video/webm': 'webm',
            'video/avi': 'avi',
            'audio/mp3': 'mp3',
            'audio/mpeg': 'mp3',
            'audio/wav': 'wav',
            'audio/ogg': 'ogg',
            'application/vnd.apple.mpegurl': 'hls',
            'application/dash+xml': 'dash'
        }
        return format_map.get(content_type.lower(), 'unknown')


class ProcessingPipeline:
    """Orchestrates post-capture processing"""
    
    def __init__(self, config: Optional[CFPLConfig] = None):
        self.config = config or get_config()
        self.cas_store = CASStore(self.config.storage.root)
        
        # Initialize processors
        self.processors = {
            'html_parser': HTMLProcessor(self.config),
            'text_extractor': TextExtractor(self.config),
            'media_metadata': MediaMetadataProcessor(self.config)
        }
    
    async def process_manifest(self, manifest_path: str, run_id: str) -> Dict[str, Any]:
        """Process a single capture manifest"""
        try:
            # Load manifest
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            url = manifest.get('url', 'unknown')
            logger.info(f"Processing manifest for: {url}")
            
            # Run enabled processors
            results = {
                "manifest_path": manifest_path,
                "url": url,
                "run_id": run_id,
                "processing_start": datetime.utcnow().isoformat() + 'Z',
                "processors": {}
            }
            
            enabled_processors = self.config.processing.enabled_processors
            
            for processor_name in enabled_processors:
                if processor_name in self.processors:
                    try:
                        processor = self.processors[processor_name]
                        result = await processor.process(manifest, run_id)
                        results["processors"][processor_name] = result
                        logger.info(f"Completed {processor_name} for {url}")
                    except Exception as e:
                        logger.error(f"Processor {processor_name} failed for {url}: {str(e)}")
                        results["processors"][processor_name] = {"error": str(e)}
            
            results["processing_end"] = datetime.utcnow().isoformat() + 'Z'
            
            # Save results to DERIVED zone
            await self._save_derived_results(results, run_id)
            
            return results
            
        except Exception as e:
            logger.error(f"Processing failed for {manifest_path}: {str(e)}")
            return {"error": str(e)}
    
    async def _save_derived_results(self, results: Dict[str, Any], run_id: str):
        """Save processing results to DERIVED zone"""
        try:
            derived_dir = Path(self.config.storage.root) / "derived" / run_id
            derived_dir.mkdir(parents=True, exist_ok=True)
            
            # Save individual processor results
            for processor_name, processor_result in results.get("processors", {}).items():
                if "error" not in processor_result:
                    output_file = derived_dir / f"{processor_name}.jsonl"
                    
                    # Append to JSONL file
                    async with aiofiles.open(output_file, 'a') as f:
                        await f.write(json.dumps(processor_result, ensure_ascii=False) + '\n')
            
            # Save combined results
            combined_file = derived_dir / "processing_results.jsonl"
            async with aiofiles.open(combined_file, 'a') as f:
                await f.write(json.dumps(results, ensure_ascii=False) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to save derived results: {str(e)}")
    
    async def process_run(self, run_id: str) -> Dict[str, Any]:
        """Process all manifests in a run"""
        logger.info(f"Processing run: {run_id}")
        
        # Find all manifests for this run
        manifests = self.cas_store.query_captures(run_id=run_id)
        
        if not manifests:
            return {"error": f"No manifests found for run {run_id}"}
        
        # Process manifests concurrently with semaphore
        semaphore = asyncio.Semaphore(self.config.processing.max_processing_workers)
        
        async def process_single_manifest(manifest_record: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                manifest_path = manifest_record['manifest_path']
                return await self.process_manifest(manifest_path, run_id)
        
        # Execute processing
        processing_tasks = [process_single_manifest(m) for m in manifests]
        processing_results = await asyncio.gather(*processing_tasks, return_exceptions=True)
        
        # Summarize results
        successful = sum(1 for r in processing_results if isinstance(r, dict) and "error" not in r)
        failed = len(processing_results) - successful
        
        summary = {
            "run_id": run_id,
            "total_manifests": len(manifests),
            "successful_processing": successful,
            "failed_processing": failed,
            "processing_completed": datetime.utcnow().isoformat() + 'Z'
        }
        
        logger.info(f"Processing complete for run {run_id}: {successful}/{len(manifests)} successful")
        return summary


# Convenience function
async def process_single_url_capture(manifest_path: str, run_id: str, config: Optional[CFPLConfig] = None) -> Dict[str, Any]:
    """Process a single capture manifest"""
    pipeline = ProcessingPipeline(config)
    return await pipeline.process_manifest(manifest_path, run_id)
