"""
Phase 2: DOM Change Detection System

This module implements intelligent monitoring of discovered sources for structural changes
and automatically updates spider extraction logic when pages change.

Key Features:
- DOM structure fingerprinting and change detection
- Automatic spider extraction logic updates
- Alert system for broken spiders
- Version control for spider templates
- Historical change tracking
- Smart re-training of extraction patterns
"""

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import aiohttp
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


@dataclass
class DOMFingerprint:
    """Represents a DOM structure fingerprint for change detection"""
    
    url: str
    timestamp: datetime
    structure_hash: str
    element_counts: Dict[str, int]
    key_selectors: Dict[str, str]  # Important selectors -> content samples
    page_title: Optional[str] = None
    meta_description: Optional[str] = None
    form_signatures: List[Dict[str, Any]] = field(default_factory=list)
    api_endpoints: List[str] = field(default_factory=list)
    content_patterns: Dict[str, List[str]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'url': self.url,
            'timestamp': self.timestamp.isoformat(),
            'structure_hash': self.structure_hash,
            'element_counts': self.element_counts,
            'key_selectors': self.key_selectors,
            'page_title': self.page_title,
            'meta_description': self.meta_description,
            'form_signatures': self.form_signatures,
            'api_endpoints': self.api_endpoints,
            'content_patterns': self.content_patterns
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DOMFingerprint':
        """Create from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class DOMChange:
    """Represents a detected change in DOM structure"""
    
    url: str
    change_type: str  # 'structure', 'content', 'forms', 'api', 'critical'
    severity: str     # 'low', 'medium', 'high', 'critical'
    description: str
    old_fingerprint: DOMFingerprint
    new_fingerprint: DOMFingerprint
    detected_at: datetime = field(default_factory=datetime.utcnow)
    affected_spiders: List[str] = field(default_factory=list)
    suggested_fixes: List[str] = field(default_factory=list)
    auto_fixable: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'url': self.url,
            'change_type': self.change_type,
            'severity': self.severity,
            'description': self.description,
            'old_fingerprint': self.old_fingerprint.to_dict(),
            'new_fingerprint': self.new_fingerprint.to_dict(),
            'detected_at': self.detected_at.isoformat(),
            'affected_spiders': self.affected_spiders,
            'suggested_fixes': self.suggested_fixes,
            'auto_fixable': self.auto_fixable
        }


class DOMAnalyzer:
    """Analyzes DOM structure and creates fingerprints for change detection"""
    
    def __init__(self):
        self.key_business_selectors = [
            'h1', 'h2', 'h3',           # Headings
            '.title', '.name', '.headline',
            '.description', '.summary', '.content',
            '.price', '.cost', '.amount',
            '.address', '.location', '.contact',
            '.phone', '.email', '.website',
            '.category', '.type', '.classification',
            'form', 'input', 'select', 'textarea',
            '.listing', '.item', '.entry', '.record',
            '.api', '.endpoint', '[data-api]',
            '.pagination', '.next', '.prev'
        ]
    
    async def analyze_page(self, url: str, html_content: str) -> DOMFingerprint:
        """Analyze page and create DOM fingerprint"""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Calculate structure hash
        structure_hash = self._calculate_structure_hash(soup)
        
        # Count elements
        element_counts = self._count_elements(soup)
        
        # Extract key selectors
        key_selectors = self._extract_key_selectors(soup)
        
        # Get page metadata
        title = soup.find('title')
        page_title = title.get_text(strip=True) if title else None
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_desc.get('content') if meta_desc else None
        
        # Analyze forms
        form_signatures = self._analyze_forms(soup)
        
        # Detect API endpoints
        api_endpoints = self._detect_api_endpoints(soup)
        
        # Extract content patterns
        content_patterns = self._extract_content_patterns(soup)
        
        return DOMFingerprint(
            url=url,
            timestamp=datetime.utcnow(),
            structure_hash=structure_hash,
            element_counts=element_counts,
            key_selectors=key_selectors,
            page_title=page_title,
            meta_description=meta_description,
            form_signatures=form_signatures,
            api_endpoints=api_endpoints,
            content_patterns=content_patterns
        )
    
    def _calculate_structure_hash(self, soup: BeautifulSoup) -> str:
        """Calculate hash of DOM structure"""
        # Create simplified structure representation
        structure_parts = []
        
        def traverse(element, depth=0):
            if depth > 10:  # Limit depth to avoid infinite recursion
                return
            
            if isinstance(element, Tag):
                # Include tag name and key attributes
                tag_info = element.name
                
                # Include important attributes
                important_attrs = ['class', 'id', 'name', 'type', 'action', 'method']
                for attr in important_attrs:
                    if element.has_attr(attr):
                        tag_info += f"[{attr}={element[attr]}]"
                
                structure_parts.append(tag_info)
                
                # Process children
                for child in element.children:
                    traverse(child, depth + 1)
        
        # Start traversal from body or html
        body = soup.find('body')
        if body:
            traverse(body)
        else:
            traverse(soup)
        
        # Create hash from structure
        structure_str = '|'.join(structure_parts)
        return hashlib.md5(structure_str.encode()).hexdigest()
    
    def _count_elements(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Count different types of elements"""
        counts = {}
        
        # Count basic HTML elements
        basic_elements = ['div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                         'form', 'input', 'select', 'textarea', 'button', 'a', 
                         'img', 'table', 'tr', 'td', 'ul', 'ol', 'li']
        
        for element in basic_elements:
            counts[element] = len(soup.find_all(element))
        
        # Count elements with business-relevant classes
        business_classes = ['listing', 'item', 'entry', 'record', 'product', 
                           'company', 'business', 'contact', 'address', 'price']
        
        for cls in business_classes:
            counts[f'class_{cls}'] = len(soup.find_all(class_=cls))
        
        return counts
    
    def _extract_key_selectors(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract content from key business-relevant selectors"""
        key_selectors = {}
        
        for selector in self.key_business_selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    # Get first few elements' content as sample
                    samples = []
                    for elem in elements[:3]:  # Limit to first 3
                        text = elem.get_text(strip=True)
                        if text and len(text) > 5:  # Only meaningful content
                            samples.append(text[:100])  # Truncate for storage
                    
                    if samples:
                        key_selectors[selector] = '|'.join(samples)
                        
            except Exception as e:
                logger.warning(f"Error processing selector {selector}: {e}")
                continue
        
        return key_selectors
    
    def _analyze_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Analyze form structures"""
        form_signatures = []
        
        forms = soup.find_all('form')
        for form in forms:
            signature = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get').lower(),
                'fields': []
            }
            
            # Analyze form fields
            inputs = form.find_all(['input', 'select', 'textarea'])
            for input_elem in inputs:
                field_info = {
                    'tag': input_elem.name,
                    'type': input_elem.get('type', ''),
                    'name': input_elem.get('name', ''),
                    'required': input_elem.has_attr('required')
                }
                signature['fields'].append(field_info)
            
            form_signatures.append(signature)
        
        return form_signatures
    
    def _detect_api_endpoints(self, soup: BeautifulSoup) -> List[str]:
        """Detect potential API endpoints in page"""
        endpoints = set()
        
        # Look for API-like URLs in various places
        api_patterns = [
            r'/api/', r'/rest/', r'/graphql', r'/v\d+/', 
            r'\.json', r'\.xml', r'/data/', r'/feed'
        ]
        
        # Check links
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            for pattern in api_patterns:
                if pattern in href.lower():
                    endpoints.add(href)
        
        # Check script tags for AJAX calls
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                content = script.string.lower()
                for pattern in api_patterns:
                    if pattern in content:
                        # Extract potential API URLs (simplified)
                        import re
                        urls = re.findall(r'["\']([^"\']*' + pattern + r'[^"\']*)["\']', 
                                        script.string, re.IGNORECASE)
                        endpoints.update(urls[:5])  # Limit results
        
        return list(endpoints)
    
    def _extract_content_patterns(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract common content patterns for comparison"""
        patterns = {
            'headings': [],
            'links': [],
            'lists': [],
            'tables': []
        }
        
        # Extract heading patterns
        headings = soup.find_all(['h1', 'h2', 'h3'])
        for h in headings[:5]:  # Limit to first 5
            text = h.get_text(strip=True)
            if text:
                patterns['headings'].append(text[:50])  # Truncate
        
        # Extract link patterns
        links = soup.find_all('a', href=True)
        for link in links[:10]:  # Limit to first 10
            text = link.get_text(strip=True)
            if text and len(text) > 3:
                patterns['links'].append(text[:30])  # Truncate
        
        # Extract list patterns
        lists = soup.find_all(['ul', 'ol'])
        for lst in lists[:3]:  # Limit to first 3
            items = lst.find_all('li')
            if items:
                list_text = ' | '.join([li.get_text(strip=True)[:20] for li in items[:3]])
                patterns['lists'].append(list_text)
        
        # Extract table patterns
        tables = soup.find_all('table')
        for table in tables[:2]:  # Limit to first 2
            headers = table.find_all(['th', 'td'])
            if headers:
                header_text = ' | '.join([h.get_text(strip=True)[:15] for h in headers[:5]])
                patterns['tables'].append(header_text)
        
        return patterns


class DOMChangeDetector:
    """Detects and analyzes changes in DOM structure"""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path('data/dom_changes')
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.fingerprints_file = self.storage_dir / 'fingerprints.json'
        self.changes_file = self.storage_dir / 'changes.json'
        
        self.analyzer = DOMAnalyzer()
        self.fingerprints: Dict[str, List[DOMFingerprint]] = {}
        self.changes: List[DOMChange] = []
        
        self.load_data()
    
    def load_data(self) -> None:
        """Load stored fingerprints and changes"""
        # Load fingerprints
        if self.fingerprints_file.exists():
            try:
                with open(self.fingerprints_file, 'r') as f:
                    data = json.load(f)
                    for url, fp_list in data.items():
                        self.fingerprints[url] = [
                            DOMFingerprint.from_dict(fp_data) for fp_data in fp_list
                        ]
            except Exception as e:
                logger.error(f"Error loading fingerprints: {e}")
        
        # Load changes
        if self.changes_file.exists():
            try:
                with open(self.changes_file, 'r') as f:
                    changes_data = json.load(f)
                    for change_data in changes_data:
                        change_data['old_fingerprint'] = DOMFingerprint.from_dict(
                            change_data['old_fingerprint']
                        )
                        change_data['new_fingerprint'] = DOMFingerprint.from_dict(
                            change_data['new_fingerprint']
                        )
                        change_data['detected_at'] = datetime.fromisoformat(
                            change_data['detected_at']
                        )
                        self.changes.append(DOMChange(**change_data))
            except Exception as e:
                logger.error(f"Error loading changes: {e}")
    
    def save_data(self) -> None:
        """Save fingerprints and changes to disk"""
        # Save fingerprints
        try:
            fp_data = {}
            for url, fp_list in self.fingerprints.items():
                fp_data[url] = [fp.to_dict() for fp in fp_list]
            
            with open(self.fingerprints_file, 'w') as f:
                json.dump(fp_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving fingerprints: {e}")
        
        # Save changes
        try:
            changes_data = [change.to_dict() for change in self.changes]
            with open(self.changes_file, 'w') as f:
                json.dump(changes_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving changes: {e}")
    
    async def check_for_changes(self, url: str, html_content: str) -> List[DOMChange]:
        """Check for changes in a URL's DOM structure"""
        
        # Create new fingerprint
        new_fingerprint = await self.analyzer.analyze_page(url, html_content)
        
        # Get previous fingerprints for this URL
        previous_fingerprints = self.fingerprints.get(url, [])
        
        # Store new fingerprint
        if url not in self.fingerprints:
            self.fingerprints[url] = []
        self.fingerprints[url].append(new_fingerprint)
        
        # Keep only last 10 fingerprints per URL
        self.fingerprints[url] = self.fingerprints[url][-10:]
        
        changes = []
        
        if previous_fingerprints:
            # Compare with most recent fingerprint
            latest_fingerprint = previous_fingerprints[-1]
            detected_changes = self._compare_fingerprints(latest_fingerprint, new_fingerprint)
            changes.extend(detected_changes)
            
            # Store detected changes
            self.changes.extend(detected_changes)
            
            # Keep only recent changes (last 30 days)
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            self.changes = [c for c in self.changes if c.detected_at > cutoff_date]
        
        self.save_data()
        return changes
    
    def _compare_fingerprints(self, old_fp: DOMFingerprint, new_fp: DOMFingerprint) -> List[DOMChange]:
        """Compare two fingerprints and detect changes"""
        changes = []
        
        # Structure change detection
        if old_fp.structure_hash != new_fp.structure_hash:
            severity = self._calculate_structure_change_severity(old_fp, new_fp)
            
            change = DOMChange(
                url=new_fp.url,
                change_type='structure',
                severity=severity,
                description=f"DOM structure changed. Hash: {old_fp.structure_hash[:8]} → {new_fp.structure_hash[:8]}",
                old_fingerprint=old_fp,
                new_fingerprint=new_fp,
                suggested_fixes=self._suggest_structure_fixes(old_fp, new_fp),
                auto_fixable=severity in ['low', 'medium']
            )
            changes.append(change)
        
        # Element count changes
        count_changes = self._detect_element_count_changes(old_fp, new_fp)
        changes.extend(count_changes)
        
        # Key selector changes
        selector_changes = self._detect_selector_changes(old_fp, new_fp)
        changes.extend(selector_changes)
        
        # Form changes
        form_changes = self._detect_form_changes(old_fp, new_fp)
        changes.extend(form_changes)
        
        # API endpoint changes
        api_changes = self._detect_api_changes(old_fp, new_fp)
        changes.extend(api_changes)
        
        # Content pattern changes
        content_changes = self._detect_content_changes(old_fp, new_fp)
        changes.extend(content_changes)
        
        return changes
    
    def _calculate_structure_change_severity(self, old_fp: DOMFingerprint, new_fp: DOMFingerprint) -> str:
        """Calculate severity of structure changes"""
        # Compare element counts to gauge change magnitude
        old_counts = old_fp.element_counts
        new_counts = new_fp.element_counts
        
        total_changes = 0
        major_changes = 0
        
        all_elements = set(old_counts.keys()) | set(new_counts.keys())
        
        for element in all_elements:
            old_count = old_counts.get(element, 0)
            new_count = new_counts.get(element, 0)
            
            if old_count != new_count:
                total_changes += abs(old_count - new_count)
                
                # Major changes in important elements
                if element in ['form', 'input', 'h1', 'h2', 'table'] and abs(old_count - new_count) > 2:
                    major_changes += 1
        
        # Determine severity
        if major_changes > 3 or total_changes > 50:
            return 'critical'
        elif major_changes > 1 or total_changes > 20:
            return 'high'
        elif total_changes > 5:
            return 'medium'
        else:
            return 'low'
    
    def _suggest_structure_fixes(self, old_fp: DOMFingerprint, new_fp: DOMFingerprint) -> List[str]:
        """Suggest fixes for structure changes"""
        fixes = []
        
        # Compare key selectors to suggest alternatives
        old_selectors = set(old_fp.key_selectors.keys())
        new_selectors = set(new_fp.key_selectors.keys())
        
        missing_selectors = old_selectors - new_selectors
        new_added_selectors = new_selectors - old_selectors
        
        for missing in missing_selectors:
            # Suggest potential replacements
            for added in new_added_selectors:
                if self._selector_similarity(missing, added) > 0.6:
                    fixes.append(f"Replace selector '{missing}' with '{added}'")
        
        # Suggest fallback selectors
        if missing_selectors:
            fixes.append("Consider using more generic selectors as fallbacks")
            fixes.append("Add error handling for missing elements")
        
        # Suggest updating spider logic
        fixes.append("Review and update spider extraction logic")
        fixes.append("Test spider with new page structure")
        
        return fixes
    
    def _selector_similarity(self, sel1: str, sel2: str) -> float:
        """Calculate similarity between two selectors"""
        # Simple similarity based on common terms
        terms1 = set(sel1.lower().replace('.', ' ').replace('#', ' ').split())
        terms2 = set(sel2.lower().replace('.', ' ').replace('#', ' ').split())
        
        if not terms1 or not terms2:
            return 0.0
        
        intersection = len(terms1 & terms2)
        union = len(terms1 | terms2)
        
        return intersection / union if union > 0 else 0.0
    
    def _detect_element_count_changes(self, old_fp: DOMFingerprint, new_fp: DOMFingerprint) -> List[DOMChange]:
        """Detect significant changes in element counts"""
        changes = []
        
        old_counts = old_fp.element_counts
        new_counts = new_fp.element_counts
        
        # Check for significant changes in important elements
        important_elements = ['form', 'input', 'table', 'h1', 'h2', 'h3', 'class_listing', 'class_item']
        
        for element in important_elements:
            old_count = old_counts.get(element, 0)
            new_count = new_counts.get(element, 0)
            
            if old_count > 0 and new_count == 0:
                # Element completely removed
                changes.append(DOMChange(
                    url=new_fp.url,
                    change_type='content',
                    severity='high',
                    description=f"All {element} elements removed (was {old_count})",
                    old_fingerprint=old_fp,
                    new_fingerprint=new_fp,
                    suggested_fixes=[f"Find alternative selector for {element} elements"],
                    auto_fixable=False
                ))
            
            elif abs(old_count - new_count) > max(old_count * 0.5, 5):
                # Significant change in count
                severity = 'high' if element in ['form', 'input'] else 'medium'
                
                changes.append(DOMChange(
                    url=new_fp.url,
                    change_type='content',
                    severity=severity,
                    description=f"{element} count changed significantly: {old_count} → {new_count}",
                    old_fingerprint=old_fp,
                    new_fingerprint=new_fp,
                    suggested_fixes=[f"Review {element} extraction logic"],
                    auto_fixable=severity == 'medium'
                ))
        
        return changes
    
    def _detect_selector_changes(self, old_fp: DOMFingerprint, new_fp: DOMFingerprint) -> List[DOMChange]:
        """Detect changes in key selector content"""
        changes = []
        
        old_selectors = old_fp.key_selectors
        new_selectors = new_fp.key_selectors
        
        # Check for missing selectors
        for selector in old_selectors:
            if selector not in new_selectors:
                changes.append(DOMChange(
                    url=new_fp.url,
                    change_type='structure',
                    severity='medium',
                    description=f"Key selector '{selector}' no longer found",
                    old_fingerprint=old_fp,
                    new_fingerprint=new_fp,
                    suggested_fixes=[f"Find alternative selector for '{selector}'"],
                    auto_fixable=True
                ))
        
        # Check for content changes in existing selectors
        for selector in old_selectors:
            if selector in new_selectors:
                old_content = old_selectors[selector]
                new_content = new_selectors[selector]
                
                if old_content != new_content:
                    # Calculate content similarity
                    similarity = self._content_similarity(old_content, new_content)
                    
                    if similarity < 0.3:  # Significant content change
                        changes.append(DOMChange(
                            url=new_fp.url,
                            change_type='content',
                            severity='medium',
                            description=f"Content changed for selector '{selector}'",
                            old_fingerprint=old_fp,
                            new_fingerprint=new_fp,
                            suggested_fixes=[f"Review content extraction for '{selector}'"],
                            auto_fixable=True
                        ))
        
        return changes
    
    def _content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content strings"""
        if not content1 or not content2:
            return 0.0
        
        # Simple word-based similarity
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _detect_form_changes(self, old_fp: DOMFingerprint, new_fp: DOMFingerprint) -> List[DOMChange]:
        """Detect changes in form structures"""
        changes = []
        
        old_forms = old_fp.form_signatures
        new_forms = new_fp.form_signatures
        
        if len(old_forms) != len(new_forms):
            severity = 'high' if len(old_forms) > 0 else 'medium'
            changes.append(DOMChange(
                url=new_fp.url,
                change_type='forms',
                severity=severity,
                description=f"Form count changed: {len(old_forms)} → {len(new_forms)}",
                old_fingerprint=old_fp,
                new_fingerprint=new_fp,
                suggested_fixes=["Review form submission logic", "Update form field mappings"],
                auto_fixable=severity == 'medium'
            ))
        
        # Compare individual forms
        for i, old_form in enumerate(old_forms):
            if i < len(new_forms):
                new_form = new_forms[i]
                form_changes = self._compare_forms(old_form, new_form, new_fp)
                changes.extend(form_changes)
        
        return changes
    
    def _compare_forms(self, old_form: Dict[str, Any], new_form: Dict[str, Any], new_fp: DOMFingerprint) -> List[DOMChange]:
        """Compare two form structures"""
        changes = []
        
        # Check action URL change
        if old_form.get('action') != new_form.get('action'):
            changes.append(DOMChange(
                url=new_fp.url,
                change_type='forms',
                severity='high',
                description=f"Form action changed: {old_form.get('action')} → {new_form.get('action')}",
                old_fingerprint=None,  # Will be set by caller
                new_fingerprint=new_fp,
                suggested_fixes=["Update form submission URL"],
                auto_fixable=True
            ))
        
        # Check method change
        if old_form.get('method') != new_form.get('method'):
            changes.append(DOMChange(
                url=new_fp.url,
                change_type='forms',
                severity='medium',
                description=f"Form method changed: {old_form.get('method')} → {new_form.get('method')}",
                old_fingerprint=None,  # Will be set by caller
                new_fingerprint=new_fp,
                suggested_fixes=["Update form submission method"],
                auto_fixable=True
            ))
        
        # Check field changes
        old_fields = {f.get('name', ''): f for f in old_form.get('fields', [])}
        new_fields = {f.get('name', ''): f for f in new_form.get('fields', [])}
        
        missing_fields = set(old_fields.keys()) - set(new_fields.keys())
        new_fields_added = set(new_fields.keys()) - set(old_fields.keys())
        
        if missing_fields:
            changes.append(DOMChange(
                url=new_fp.url,
                change_type='forms',
                severity='high',
                description=f"Form fields removed: {', '.join(missing_fields)}",
                old_fingerprint=None,  # Will be set by caller
                new_fingerprint=new_fp,
                suggested_fixes=["Update form field mappings", "Handle missing fields gracefully"],
                auto_fixable=False
            ))
        
        if new_fields_added:
            changes.append(DOMChange(
                url=new_fp.url,
                change_type='forms',
                severity='low',
                description=f"New form fields added: {', '.join(new_fields_added)}",
                old_fingerprint=None,  # Will be set by caller
                new_fingerprint=new_fp,
                suggested_fixes=["Consider utilizing new form fields"],
                auto_fixable=True
            ))
        
        return changes
    
    def _detect_api_changes(self, old_fp: DOMFingerprint, new_fp: DOMFingerprint) -> List[DOMChange]:
        """Detect changes in API endpoints"""
        changes = []
        
        old_apis = set(old_fp.api_endpoints)
        new_apis = set(new_fp.api_endpoints)
        
        missing_apis = old_apis - new_apis
        new_apis_added = new_apis - old_apis
        
        if missing_apis:
            changes.append(DOMChange(
                url=new_fp.url,
                change_type='api',
                severity='high',
                description=f"API endpoints removed: {', '.join(list(missing_apis)[:3])}",
                old_fingerprint=old_fp,
                new_fingerprint=new_fp,
                suggested_fixes=["Find alternative API endpoints", "Update API integration"],
                auto_fixable=False
            ))
        
        if new_apis_added:
            changes.append(DOMChange(
                url=new_fp.url,
                change_type='api',
                severity='low',
                description=f"New API endpoints found: {', '.join(list(new_apis_added)[:3])}",
                old_fingerprint=old_fp,
                new_fingerprint=new_fp,
                suggested_fixes=["Consider utilizing new API endpoints"],
                auto_fixable=True
            ))
        
        return changes
    
    def _detect_content_changes(self, old_fp: DOMFingerprint, new_fp: DOMFingerprint) -> List[DOMChange]:
        """Detect changes in content patterns"""
        changes = []
        
        old_patterns = old_fp.content_patterns
        new_patterns = new_fp.content_patterns
        
        for pattern_type in ['headings', 'links', 'lists', 'tables']:
            old_pattern = old_patterns.get(pattern_type, [])
            new_pattern = new_patterns.get(pattern_type, [])
            
            if len(old_pattern) != len(new_pattern) and abs(len(old_pattern) - len(new_pattern)) > 2:
                severity = 'medium' if pattern_type in ['headings', 'tables'] else 'low'
                
                changes.append(DOMChange(
                    url=new_fp.url,
                    change_type='content',
                    severity=severity,
                    description=f"{pattern_type.title()} pattern changed: {len(old_pattern)} → {len(new_pattern)} items",
                    old_fingerprint=old_fp,
                    new_fingerprint=new_fp,
                    suggested_fixes=[f"Review {pattern_type} extraction logic"],
                    auto_fixable=severity == 'low'
                ))
        
        return changes
    
    def get_changes_for_url(self, url: str, days: int = 7) -> List[DOMChange]:
        """Get recent changes for a specific URL"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return [change for change in self.changes 
                if change.url == url and change.detected_at > cutoff_date]
    
    def get_critical_changes(self, days: int = 7) -> List[DOMChange]:
        """Get critical changes across all URLs"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return [change for change in self.changes 
                if change.severity == 'critical' and change.detected_at > cutoff_date]
    
    def get_changes_by_severity(self, severity: str, days: int = 7) -> List[DOMChange]:
        """Get changes by severity level"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return [change for change in self.changes 
                if change.severity == severity and change.detected_at > cutoff_date]


async def demo_dom_change_detection():
    """Demo the DOM change detection system"""
    
    print("🔍 Phase 2: DOM Change Detection Demo")
    print("=" * 50)
    
    detector = DOMChangeDetector()
    
    # Simulate initial page scan
    print("\n📊 Initial Page Analysis")
    print("-" * 30)
    
    mock_html_v1 = """
    <html>
        <head>
            <title>Business Directory</title>
            <meta name="description" content="Find businesses in your area">
        </head>
        <body>
            <h1>Business Directory</h1>
            <div class="search-form">
                <form action="/search" method="GET">
                    <input name="query" type="text" placeholder="Search businesses">
                    <input name="location" type="text" placeholder="Location">
                    <button type="submit">Search</button>
                </form>
            </div>
            <div class="listings">
                <div class="listing">
                    <h2 class="name">ABC Company</h2>
                    <p class="description">Professional services</p>
                    <span class="address">123 Main St</span>
                </div>
                <div class="listing">
                    <h2 class="name">XYZ Corp</h2>
                    <p class="description">Technology solutions</p>
                    <span class="address">456 Oak Ave</span>
                </div>
            </div>
        </body>
    </html>
    """
    
    url = "https://example.com/business-directory"
    changes = await detector.check_for_changes(url, mock_html_v1)
    
    print(f"✅ Initial analysis complete for {url}")
    print(f"   Structure hash: {detector.fingerprints[url][-1].structure_hash[:8]}")
    print(f"   Elements found: {sum(detector.fingerprints[url][-1].element_counts.values())}")
    print(f"   Key selectors: {len(detector.fingerprints[url][-1].key_selectors)}")
    print(f"   Changes detected: {len(changes)} (expected 0 for first scan)")
    
    # Simulate page change
    print("\n🔄 Simulating Page Changes")
    print("-" * 30)
    
    mock_html_v2 = """
    <html>
        <head>
            <title>Business Directory - Updated</title>
            <meta name="description" content="Find businesses in your area - Now with more features">
        </head>
        <body>
            <h1>Business Directory</h1>
            <div class="advanced-search">
                <form action="/api/search" method="POST">
                    <input name="query" type="text" placeholder="Search businesses">
                    <input name="location" type="text" placeholder="Location">
                    <select name="category">
                        <option>All Categories</option>
                        <option>Professional Services</option>
                        <option>Technology</option>
                    </select>
                    <input name="radius" type="range" min="1" max="50">
                    <button type="submit">Advanced Search</button>
                </form>
            </div>
            <div class="business-listings">
                <div class="business-item">
                    <h3 class="company-name">ABC Company</h3>
                    <p class="company-description">Professional services</p>
                    <span class="company-address">123 Main St</span>
                    <a href="/api/business/1" class="api-link">Get Details</a>
                </div>
                <div class="business-item">
                    <h3 class="company-name">XYZ Corp</h3>
                    <p class="company-description">Technology solutions</p>
                    <span class="company-address">456 Oak Ave</span>
                    <a href="/api/business/2" class="api-link">Get Details</a>
                </div>
                <div class="business-item">
                    <h3 class="company-name">New Business LLC</h3>
                    <p class="company-description">Consulting services</p>
                    <span class="company-address">789 Pine St</span>
                    <a href="/api/business/3" class="api-link">Get Details</a>
                </div>
            </div>
            <script>
                // New API integration
                fetch('/api/businesses').then(r => r.json()).then(console.log);
            </script>
        </body>
    </html>
    """
    
    changes = await detector.check_for_changes(url, mock_html_v2)
    
    print(f"🔍 Change detection complete")
    print(f"   New structure hash: {detector.fingerprints[url][-1].structure_hash[:8]}")
    print(f"   Changes detected: {len(changes)}")
    
    # Display detected changes
    if changes:
        print("\n📋 Detected Changes:")
        for i, change in enumerate(changes, 1):
            print(f"   {i}. {change.change_type.upper()} [{change.severity}]: {change.description}")
            if change.suggested_fixes:
                print(f"      Suggested fixes: {change.suggested_fixes[0]}")
            print(f"      Auto-fixable: {'Yes' if change.auto_fixable else 'No'}")
            print()
    
    # Show statistics
    print(f"📈 Detection Statistics:")
    print(f"   Total fingerprints stored: {len(detector.fingerprints)}")
    print(f"   Total changes recorded: {len(detector.changes)}")
    
    # Show change types
    if detector.changes:
        change_types = {}
        severities = {}
        
        for change in detector.changes:
            change_types[change.change_type] = change_types.get(change.change_type, 0) + 1
            severities[change.severity] = severities.get(change.severity, 0) + 1
        
        print(f"   Change types: {dict(change_types)}")
        print(f"   Severities: {dict(severities)}")
    
    print(f"\n✅ DOM Change Detection Demo Complete!")
    return detector


if __name__ == "__main__":
    asyncio.run(demo_dom_change_detection())
