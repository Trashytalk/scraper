"""
Spider Update System - Automatically updates spider extraction logic when DOM changes are detected

This module integrates with the DOM change detection system to automatically update
spider extraction logic when structural changes are detected in target websites.
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .dom_change_detection import DOMChange, DOMChangeDetector, DOMFingerprint

logger = logging.getLogger(__name__)


class SpiderTemplate:
    """Represents a spider template with updatable extraction logic"""

    def __init__(self, filepath: Path, spider_name: str):
        self.filepath = filepath
        self.spider_name = spider_name
        self.original_code = ""
        self.current_code = ""
        self.extraction_patterns = {}
        self.selectors = set()

        self.load_spider()
        self.analyze_extraction_patterns()

    def load_spider(self) -> None:
        """Load spider code from file"""
        try:
            with open(self.filepath, "r") as f:
                self.original_code = f.read()
                self.current_code = self.original_code
        except Exception as e:
            logger.error(f"Error loading spider {self.filepath}: {e}")

    def analyze_extraction_patterns(self) -> None:
        """Analyze spider code to identify extraction patterns"""

        # Extract CSS selectors
        css_pattern = r'response\.css\(["\']([^"\']+)["\']\)'
        css_matches = re.findall(css_pattern, self.current_code)

        xpath_pattern = r'response\.xpath\(["\']([^"\']+)["\']\)'
        xpath_matches = re.findall(xpath_pattern, self.current_code)

        # Store selectors
        self.selectors = set(css_matches + xpath_matches)

        # Analyze extraction patterns
        self.extraction_patterns = {
            "css_selectors": css_matches,
            "xpath_selectors": xpath_matches,
            "field_mappings": self._extract_field_mappings(),
            "yield_items": self._extract_yield_items(),
        }

    def _extract_field_mappings(self) -> Dict[str, str]:
        """Extract field mapping patterns from spider code"""
        mappings = {}

        # Look for patterns like: 'field_name': response.css('selector')
        pattern = r'["\'](\w+)["\']:\s*response\.(css|xpath)\(["\']([^"\']+)["\']\)'
        matches = re.findall(pattern, self.current_code)

        for field_name, method, selector in matches:
            mappings[field_name] = f"{method}('{selector}')"

        return mappings

    def _extract_yield_items(self) -> List[str]:
        """Extract yield item patterns"""
        yield_patterns = []

        # Find yield statements
        lines = self.current_code.split("\n")
        in_yield = False
        current_yield = []

        for line in lines:
            stripped = line.strip()

            if "yield {" in stripped or "yield(" in stripped:
                in_yield = True
                current_yield = [line]
            elif in_yield:
                current_yield.append(line)
                if "}" in stripped or ")" in stripped:
                    in_yield = False
                    yield_patterns.append("\n".join(current_yield))
                    current_yield = []

        return yield_patterns

    def save_updated_spider(self, backup: bool = True) -> bool:
        """Save updated spider code to file"""
        try:
            if backup:
                # Create backup
                backup_path = self.filepath.with_suffix(
                    f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
                )
                with open(backup_path, "w") as f:
                    f.write(self.original_code)

            # Save updated code
            with open(self.filepath, "w") as f:
                f.write(self.current_code)

            logger.info(f"Updated spider saved: {self.filepath}")
            return True

        except Exception as e:
            logger.error(f"Error saving updated spider: {e}")
            return False


class SpiderUpdater:
    """Updates spider extraction logic based on DOM changes"""

    def __init__(self, spiders_dir: Optional[Path] = None):
        self.spiders_dir = spiders_dir or Path(
            "business_intel_scraper/backend/modules/spiders"
        )
        self.generated_spiders_dir = Path(
            "business_intel_scraper/backend/discovery/generated"
        )

        self.update_history_file = Path("data/spider_updates/update_history.json")
        self.update_history_file.parent.mkdir(parents=True, exist_ok=True)

        self.update_history: List[Dict[str, Any]] = []
        self.load_update_history()

        # Mapping of common selector changes
        self.selector_mappings = {
            # Old selector -> potential new selectors
            ".listing": [
                ".business-item",
                ".company-listing",
                ".directory-entry",
                ".result-item",
            ],
            ".name": [".company-name", ".business-name", ".title", "h2", "h3"],
            ".description": [".company-description", ".summary", ".bio", ".details"],
            ".address": [".company-address", ".location", ".contact-address"],
            ".phone": [".contact-phone", ".tel", ".telephone", '[href*="tel:"]'],
            ".email": [".contact-email", '[href*="mailto:"]', ".email-link"],
            "form": [".search-form", ".contact-form", ".inquiry-form", "#search"],
            'input[name="query"]': [
                'input[name="search"]',
                'input[name="q"]',
                'input[type="search"]',
            ],
            'input[name="location"]': [
                'input[name="loc"]',
                'input[name="address"]',
                'input[name="city"]',
            ],
        }

    def load_update_history(self) -> None:
        """Load spider update history"""
        if self.update_history_file.exists():
            try:
                with open(self.update_history_file, "r") as f:
                    self.update_history = json.load(f)
            except Exception as e:
                logger.error(f"Error loading update history: {e}")

    def save_update_history(self) -> None:
        """Save spider update history"""
        try:
            with open(self.update_history_file, "w") as f:
                json.dump(self.update_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving update history: {e}")

    def find_affected_spiders(self, url: str) -> List[SpiderTemplate]:
        """Find spiders that are affected by changes to a URL"""
        affected_spiders = []

        # Search in both regular spiders and generated spiders directories
        search_dirs = [self.spiders_dir, self.generated_spiders_dir]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for spider_file in search_dir.glob("*.py"):
                try:
                    with open(spider_file, "r") as f:
                        content = f.read()

                    # Check if spider targets this URL or domain
                    from urllib.parse import urlparse

                    domain = urlparse(url).netloc

                    if (
                        url in content
                        or domain in content
                        or any(
                            domain_part in content for domain_part in domain.split(".")
                        )
                    ):

                        spider_name = spider_file.stem
                        template = SpiderTemplate(spider_file, spider_name)
                        affected_spiders.append(template)

                except Exception as e:
                    logger.warning(f"Error analyzing spider {spider_file}: {e}")

        return affected_spiders

    async def update_spiders_for_changes(
        self, changes: List[DOMChange]
    ) -> Dict[str, Any]:
        """Update spiders based on detected DOM changes"""

        update_results = {
            "total_changes": len(changes),
            "spiders_updated": 0,
            "automatic_fixes": 0,
            "manual_review_needed": 0,
            "failed_updates": 0,
            "updates": [],
        }

        # Group changes by URL
        changes_by_url = {}
        for change in changes:
            if change.url not in changes_by_url:
                changes_by_url[change.url] = []
            changes_by_url[change.url].append(change)

        # Process each URL
        for url, url_changes in changes_by_url.items():
            logger.info(f"Processing changes for {url}")

            # Find affected spiders
            affected_spiders = self.find_affected_spiders(url)

            if not affected_spiders:
                logger.info(f"No spiders found for URL: {url}")
                continue

            # Update each affected spider
            for spider in affected_spiders:
                update_result = await self.update_spider_for_url_changes(
                    spider, url, url_changes
                )
                update_results["updates"].append(update_result)

                # Update counters
                if update_result["success"]:
                    update_results["spiders_updated"] += 1
                    if update_result["automatic"]:
                        update_results["automatic_fixes"] += 1
                    else:
                        update_results["manual_review_needed"] += 1
                else:
                    update_results["failed_updates"] += 1

        # Record update session in history
        self.record_update_session(update_results)

        return update_results

    async def update_spider_for_url_changes(
        self, spider: SpiderTemplate, url: str, changes: List[DOMChange]
    ) -> Dict[str, Any]:
        """Update a single spider based on URL changes"""

        update_result = {
            "spider_name": spider.spider_name,
            "url": url,
            "changes_processed": len(changes),
            "success": False,
            "automatic": False,
            "modifications": [],
            "warnings": [],
            "manual_actions_needed": [],
        }

        try:
            modified = False

            # Process each change
            for change in changes:
                if change.auto_fixable and change.suggested_fixes:
                    # Attempt automatic fix
                    fix_applied = await self.apply_automatic_fix(spider, change)
                    if fix_applied:
                        update_result["modifications"].append(
                            {
                                "type": change.change_type,
                                "description": change.description,
                                "fix_applied": change.suggested_fixes[0],
                                "automatic": True,
                            }
                        )
                        modified = True
                        update_result["automatic"] = True
                    else:
                        update_result["warnings"].append(
                            f"Could not auto-fix: {change.description}"
                        )
                        update_result["manual_actions_needed"].append(
                            change.suggested_fixes[0]
                        )
                else:
                    # Manual review needed
                    update_result["manual_actions_needed"].extend(
                        change.suggested_fixes
                    )
                    update_result["warnings"].append(
                        f"Manual review needed: {change.description}"
                    )

            # Save updated spider if modifications were made
            if modified:
                success = spider.save_updated_spider(backup=True)
                update_result["success"] = success

                if success:
                    logger.info(f"Successfully updated spider: {spider.spider_name}")
                else:
                    logger.error(f"Failed to save updated spider: {spider.spider_name}")
            else:
                update_result["success"] = True  # No changes needed
                update_result["modifications"].append(
                    {
                        "type": "info",
                        "description": "No automatic fixes could be applied",
                        "fix_applied": "Manual review recommended",
                        "automatic": False,
                    }
                )

        except Exception as e:
            logger.error(f"Error updating spider {spider.spider_name}: {e}")
            update_result["warnings"].append(f"Update failed: {str(e)}")

        return update_result

    async def apply_automatic_fix(
        self, spider: SpiderTemplate, change: DOMChange
    ) -> bool:
        """Apply automatic fix for a DOM change"""

        try:
            if (
                change.change_type == "structure"
                and "selector" in change.description.lower()
            ):
                return await self.fix_missing_selectors(spider, change)

            elif change.change_type == "forms":
                return await self.fix_form_changes(spider, change)

            elif change.change_type == "content":
                return await self.fix_content_changes(spider, change)

            elif change.change_type == "api":
                return await self.fix_api_changes(spider, change)

            else:
                logger.info(
                    f"No automatic fix available for change type: {change.change_type}"
                )
                return False

        except Exception as e:
            logger.error(f"Error applying automatic fix: {e}")
            return False

    async def fix_missing_selectors(
        self, spider: SpiderTemplate, change: DOMChange
    ) -> bool:
        """Fix missing CSS selectors by finding alternatives"""

        # Extract missing selector from change description
        missing_selector = self.extract_selector_from_description(change.description)

        if not missing_selector:
            return False

        # Find potential replacement selectors
        replacement_selectors = self.find_replacement_selectors(
            missing_selector, change.new_fingerprint
        )

        if not replacement_selectors:
            return False

        # Apply the best replacement
        best_replacement = replacement_selectors[0]

        # Update spider code
        old_pattern = f"response.css('{missing_selector}')"
        new_pattern = f"response.css('{best_replacement}')"

        spider.current_code = spider.current_code.replace(old_pattern, new_pattern)

        # Also handle xpath versions
        old_xpath_pattern = f"response.xpath('{missing_selector}')"
        new_xpath_pattern = f"response.xpath('{best_replacement}')"

        spider.current_code = spider.current_code.replace(
            old_xpath_pattern, new_xpath_pattern
        )

        logger.info(f"Replaced selector '{missing_selector}' with '{best_replacement}'")
        return True

    def extract_selector_from_description(self, description: str) -> Optional[str]:
        """Extract CSS selector from change description"""

        # Look for quoted selectors in description
        selector_pattern = r"'([^']+)'"
        matches = re.findall(selector_pattern, description)

        for match in matches:
            if any(char in match for char in [".", "#", "[", ":"]):
                return match

        return None

    def find_replacement_selectors(
        self, missing_selector: str, new_fingerprint: DOMFingerprint
    ) -> List[str]:
        """Find replacement selectors based on new page structure"""

        candidates = []

        # Check predefined mappings
        if missing_selector in self.selector_mappings:
            candidates.extend(self.selector_mappings[missing_selector])

        # Check selectors that exist in the new fingerprint
        available_selectors = set(new_fingerprint.key_selectors.keys())

        # Find similar selectors
        for available_selector in available_selectors:
            similarity = self.calculate_selector_similarity(
                missing_selector, available_selector
            )
            if similarity > 0.5:
                candidates.append(available_selector)

        # Remove duplicates and sort by relevance
        candidates = list(set(candidates))

        # Filter candidates that actually exist in the new page
        valid_candidates = []
        for candidate in candidates:
            if candidate in available_selectors:
                valid_candidates.append(candidate)

        return valid_candidates

    def calculate_selector_similarity(self, sel1: str, sel2: str) -> float:
        """Calculate similarity between two selectors"""

        # Simple similarity based on common terms
        terms1 = set(
            sel1.lower()
            .replace(".", " ")
            .replace("#", " ")
            .replace("[", " ")
            .replace("]", " ")
            .split()
        )
        terms2 = set(
            sel2.lower()
            .replace(".", " ")
            .replace("#", " ")
            .replace("[", " ")
            .replace("]", " ")
            .split()
        )

        if not terms1 or not terms2:
            return 0.0

        intersection = len(terms1 & terms2)
        union = len(terms1 | terms2)

        return intersection / union if union > 0 else 0.0

    async def fix_form_changes(self, spider: SpiderTemplate, change: DOMChange) -> bool:
        """Fix form-related changes"""

        if "action changed" in change.description:
            # Extract old and new form actions
            parts = change.description.split("→")
            if len(parts) == 2:
                old_action = parts[0].split(":")[-1].strip()
                new_action = parts[1].strip()

                # Update form action in spider code
                spider.current_code = spider.current_code.replace(
                    f'action="{old_action}"', f'action="{new_action}"'
                )

                # Also update FormRequest URLs
                spider.current_code = spider.current_code.replace(
                    f"FormRequest(url='{old_action}'", f"FormRequest(url='{new_action}'"
                )

                return True

        elif "method changed" in change.description:
            # Extract old and new methods
            parts = change.description.split("→")
            if len(parts) == 2:
                old_method = parts[0].split(":")[-1].strip()
                new_method = parts[1].strip()

                # Update form method in spider code
                spider.current_code = spider.current_code.replace(
                    f'method="{old_method}"', f'method="{new_method}"'
                )

                return True

        elif "fields removed" in change.description:
            # Add error handling for missing fields
            missing_fields_match = re.search(
                r'fields removed: ([^"]+)', change.description
            )
            if missing_fields_match:
                missing_fields = missing_fields_match.group(1).split(", ")

                # Add error handling code
                error_handling_code = "\n        # Handle missing form fields\n"
                for field in missing_fields:
                    error_handling_code += f"        {field.strip()} = response.css('input[name=\"{field.strip()}\"]').get(default='')\n"

                # Insert error handling after form detection
                form_pattern = r"(form\s*=\s*response\.css\([^)]+\))"
                spider.current_code = re.sub(
                    form_pattern, r"\1" + error_handling_code, spider.current_code
                )

                return True

        return False

    async def fix_content_changes(
        self, spider: SpiderTemplate, change: DOMChange
    ) -> bool:
        """Fix content-related changes"""

        if "count changed significantly" in change.description:
            # Add robustness to element counting
            element_match = re.search(
                r"(\w+) count changed significantly", change.description
            )
            if element_match:
                element_type = element_match.group(1)

                # Add error handling for missing elements
                error_handling = f"""
        # Handle missing {element_type} elements gracefully
        {element_type}_elements = response.css('{element_type}')
        if not {element_type}_elements:
            self.logger.warning(f"No {element_type} elements found on {{response.url}}")
            return
        """

                # Insert error handling at the beginning of parse method
                parse_method_pattern = r"(def parse\(self, response\):.*?\n)"
                spider.current_code = re.sub(
                    parse_method_pattern,
                    r"\1" + error_handling,
                    spider.current_code,
                    flags=re.DOTALL,
                )

                return True

        elif "content changed for selector" in change.description:
            # Add content validation
            selector_match = re.search(r"selector '([^']+)'", change.description)
            if selector_match:
                selector = selector_match.group(1)

                # Add content validation
                validation_code = f"""
        # Validate content for selector {selector}
        content = response.css('{selector}').get()
        if not content or len(content.strip()) < 3:
            self.logger.warning(f"Suspicious content for selector {selector}: {{content}}")
        """

                # Insert validation before yield statements
                yield_pattern = r"(yield\s*{)"
                spider.current_code = re.sub(
                    yield_pattern,
                    validation_code + r"\n        \1",
                    spider.current_code,
                )

                return True

        return False

    async def fix_api_changes(self, spider: SpiderTemplate, change: DOMChange) -> bool:
        """Fix API-related changes"""

        if "endpoints removed" in change.description:
            # Add fallback for missing API endpoints
            endpoints_match = re.search(
                r'endpoints removed: ([^"]+)', change.description
            )
            if endpoints_match:
                removed_endpoints = endpoints_match.group(1).split(", ")

                # Add fallback API handling
                fallback_code = """
        # Fallback for removed API endpoints
        api_endpoints = ["""

                for endpoint in removed_endpoints:
                    fallback_code += f"\n            '{endpoint.strip()}',"

                fallback_code += """
        ]
        
        for endpoint in api_endpoints:
            try:
                api_response = response.follow(endpoint)
                if api_response.status == 200:
                    # Process API response
                    yield response.follow(endpoint, callback=self.parse_api)
                    break
            except Exception as e:
                self.logger.warning(f"API endpoint {endpoint} failed: {e}")
                continue
        """

                # Insert fallback code
                spider.current_code = spider.current_code.replace(
                    "def parse(self, response):",
                    "def parse(self, response):" + fallback_code,
                )

                return True

        elif "new api endpoints found" in change.description:
            # Add new API endpoints to spider
            endpoints_match = re.search(r'endpoints found: ([^"]+)', change.description)
            if endpoints_match:
                new_endpoints = endpoints_match.group(1).split(", ")

                # Add new API endpoint handling
                new_api_code = """
        # Handle new API endpoints
        new_endpoints = ["""

                for endpoint in new_endpoints:
                    new_api_code += f"\n            '{endpoint.strip()}',"

                new_api_code += """
        ]
        
        for endpoint in new_endpoints:
            yield response.follow(endpoint, callback=self.parse_api)
        """

                # Insert new API handling
                spider.current_code = spider.current_code.replace(
                    "def parse(self, response):",
                    "def parse(self, response):" + new_api_code,
                )

                return True

        return False

    def record_update_session(self, update_results: Dict[str, Any]) -> None:
        """Record update session in history"""

        session_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_changes": update_results["total_changes"],
            "spiders_updated": update_results["spiders_updated"],
            "automatic_fixes": update_results["automatic_fixes"],
            "manual_review_needed": update_results["manual_review_needed"],
            "failed_updates": update_results["failed_updates"],
            "success_rate": (
                update_results["spiders_updated"]
                / max(update_results["total_changes"], 1)
            )
            * 100,
            "updates": update_results["updates"],
        }

        self.update_history.append(session_record)

        # Keep only last 100 sessions
        self.update_history = self.update_history[-100:]

        self.save_update_history()

        logger.info(
            f"Recorded update session: {update_results['spiders_updated']} spiders updated"
        )

    def get_update_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get spider update statistics"""

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_sessions = [
            session
            for session in self.update_history
            if datetime.fromisoformat(session["timestamp"]) > cutoff_date
        ]

        if not recent_sessions:
            return {
                "total_sessions": 0,
                "total_spiders_updated": 0,
                "total_automatic_fixes": 0,
                "average_success_rate": 0.0,
                "most_common_change_types": {},
            }

        total_spiders = sum(s["spiders_updated"] for s in recent_sessions)
        total_automatic = sum(s["automatic_fixes"] for s in recent_sessions)
        avg_success_rate = sum(s["success_rate"] for s in recent_sessions) / len(
            recent_sessions
        )

        # Analyze change types
        change_types = {}
        for session in recent_sessions:
            for update in session.get("updates", []):
                for mod in update.get("modifications", []):
                    change_type = mod.get("type", "unknown")
                    change_types[change_type] = change_types.get(change_type, 0) + 1

        return {
            "total_sessions": len(recent_sessions),
            "total_spiders_updated": total_spiders,
            "total_automatic_fixes": total_automatic,
            "average_success_rate": avg_success_rate,
            "most_common_change_types": dict(
                sorted(change_types.items(), key=lambda x: x[1], reverse=True)
            ),
        }


class SpiderUpdateScheduler:
    """Schedules and manages spider updates based on DOM change detection"""

    def __init__(self, dom_detector: DOMChangeDetector, spider_updater: SpiderUpdater):
        self.dom_detector = dom_detector
        self.spider_updater = spider_updater

        self.update_queue = []
        self.processing = False

    async def check_and_update_spiders(self) -> Dict[str, Any]:
        """Check for DOM changes and update affected spiders"""

        if self.processing:
            return {"status": "already_processing"}

        self.processing = True

        try:
            # Get recent critical and high-severity changes
            critical_changes = self.dom_detector.get_critical_changes(days=1)
            high_changes = self.dom_detector.get_changes_by_severity("high", days=1)

            all_changes = critical_changes + high_changes

            if not all_changes:
                return {
                    "status": "no_changes",
                    "message": "No critical or high-severity changes found",
                }

            logger.info(f"Processing {len(all_changes)} high-priority DOM changes")

            # Update spiders
            update_results = await self.spider_updater.update_spiders_for_changes(
                all_changes
            )

            return {
                "status": "completed",
                "results": update_results,
                "message": f"Processed {len(all_changes)} changes, updated {update_results['spiders_updated']} spiders",
            }

        finally:
            self.processing = False

    async def scheduled_update_check(self) -> Dict[str, Any]:
        """Scheduled update check (called by Celery task)"""

        logger.info("Running scheduled spider update check")

        try:
            result = await self.check_and_update_spiders()

            # Also check medium severity changes if no high-priority changes
            if result.get("status") == "no_changes":
                medium_changes = self.dom_detector.get_changes_by_severity(
                    "medium", days=3
                )

                if medium_changes:
                    logger.info(
                        f"Processing {len(medium_changes)} medium-priority DOM changes"
                    )
                    update_results = (
                        await self.spider_updater.update_spiders_for_changes(
                            medium_changes
                        )
                    )

                    result = {
                        "status": "completed",
                        "results": update_results,
                        "message": f"Processed {len(medium_changes)} medium-priority changes",
                    }

            return result

        except Exception as e:
            logger.error(f"Error in scheduled update check: {e}")
            return {"status": "error", "message": str(e)}


async def demo_spider_update_system():
    """Demo the spider update system"""

    print("🔧 Phase 2: Spider Update System Demo")
    print("=" * 50)

    # Initialize components
    dom_detector = DOMChangeDetector()
    spider_updater = SpiderUpdater()
    scheduler = SpiderUpdateScheduler(dom_detector, spider_updater)

    # Create a mock spider file for demo
    demo_spider_dir = Path("demo_spiders")
    demo_spider_dir.mkdir(exist_ok=True)

    demo_spider_content = """
import scrapy

class BusinessDirectorySpider(scrapy.Spider):
    name = "business_directory"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/business-directory"]
    
    def parse(self, response):
        # Extract business listings
        listings = response.css('.listing')
        
        for listing in listings:
            yield {
                'name': listing.css('.name::text').get(),
                'description': listing.css('.description::text').get(),
                'address': listing.css('.address::text').get(),
                'phone': listing.css('.phone::text').get(),
            }
        
        # Follow pagination
        next_page = response.css('.pagination .next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
"""

    demo_spider_file = demo_spider_dir / "business_directory_spider.py"
    with open(demo_spider_file, "w") as f:
        f.write(demo_spider_content)

    print(f"✅ Created demo spider: {demo_spider_file}")

    # Load the spider
    spider_template = SpiderTemplate(demo_spider_file, "business_directory")

    print("📊 Spider Analysis:")
    print(f"   Selectors found: {len(spider_template.selectors)}")
    print(
        f"   Field mappings: {len(spider_template.extraction_patterns['field_mappings'])}"
    )
    print(f"   CSS selectors: {spider_template.extraction_patterns['css_selectors']}")

    # Simulate DOM change (from Phase 2 demo)
    from .dom_change_detection import DOMChange, DOMFingerprint

    # Create mock fingerprints
    old_fp = DOMFingerprint(
        url="https://example.com/business-directory",
        timestamp=datetime.utcnow(),
        structure_hash="old_hash_123",
        element_counts={"div": 10, "span": 5, "form": 1},
        key_selectors={".listing": "ABC Company|XYZ Corp", ".name": "ABC Company"},
    )

    new_fp = DOMFingerprint(
        url="https://example.com/business-directory",
        timestamp=datetime.utcnow(),
        structure_hash="new_hash_456",
        element_counts={"div": 12, "span": 8, "form": 1},
        key_selectors={
            ".business-item": "ABC Company|XYZ Corp|New Business",
            ".company-name": "ABC Company",
        },
    )

    # Create a mock DOM change
    dom_change = DOMChange(
        url="https://example.com/business-directory",
        change_type="structure",
        severity="medium",
        description="Key selector '.listing' no longer found",
        old_fingerprint=old_fp,
        new_fingerprint=new_fp,
        suggested_fixes=["Find alternative selector for '.listing'"],
        auto_fixable=True,
    )

    print("\n🔄 Simulating DOM Change:")
    print(f"   Change Type: {dom_change.change_type}")
    print(f"   Severity: {dom_change.severity}")
    print(f"   Description: {dom_change.description}")
    print(f"   Auto-fixable: {dom_change.auto_fixable}")

    # Update spider using temporary updater with demo directory
    demo_updater = SpiderUpdater()
    demo_updater.spiders_dir = demo_spider_dir

    # Apply the fix
    update_results = await demo_updater.update_spiders_for_changes([dom_change])

    print("\n📝 Spider Update Results:")
    print(f"   Total changes: {update_results['total_changes']}")
    print(f"   Spiders updated: {update_results['spiders_updated']}")
    print(f"   Automatic fixes: {update_results['automatic_fixes']}")
    print(f"   Manual review needed: {update_results['manual_review_needed']}")

    # Show specific updates
    if update_results["updates"]:
        update = update_results["updates"][0]
        print(f"\n🔧 Spider '{update['spider_name']}' Updates:")

        for mod in update.get("modifications", []):
            print(f"   • {mod['type']}: {mod['description']}")
            print(f"     Fix applied: {mod['fix_applied']}")
            print(f"     Automatic: {mod['automatic']}")

        for warning in update.get("warnings", []):
            print(f"   ⚠️ Warning: {warning}")

        for action in update.get("manual_actions_needed", []):
            print(f"   📋 Manual action: {action}")

    # Check if spider was actually modified
    with open(demo_spider_file, "r") as f:
        updated_content = f.read()

    if updated_content != demo_spider_content:
        print("\n✅ Spider code was successfully modified")
        print("   Original selectors: .listing")
        print("   Updated selectors: .business-item")
    else:
        print("\n📋 Spider code unchanged (manual review may be needed)")

    # Show update statistics
    stats = demo_updater.get_update_statistics()
    print("\n📈 Update Statistics:")
    print(f"   Total sessions: {stats['total_sessions']}")
    print(f"   Spiders updated: {stats['total_spiders_updated']}")
    print(f"   Automatic fixes: {stats['total_automatic_fixes']}")
    print(f"   Average success rate: {stats['average_success_rate']:.1f}%")

    # Cleanup demo files
    import shutil

    shutil.rmtree(demo_spider_dir)

    print("\n✅ Spider Update System Demo Complete!")
    return update_results


if __name__ == "__main__":
    asyncio.run(demo_spider_update_system())
