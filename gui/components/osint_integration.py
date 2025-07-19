"""
OSINT Integration System with Social Media Analysis
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QGroupBox, QLabel, QPushButton, QComboBox, QCheckBox,
                            QLineEdit, QTextEdit, QListWidget, QTableWidget,
                            QTableWidgetItem, QTabWidget, QProgressBar,
                            QTreeWidget, QTreeWidgetItem, QSplitter, QSpinBox,
                            QDateTimeEdit, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QDateTime
from PyQt6.QtGui import QFont, QColor, QPixmap, QIcon
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import re
import asyncio
import aiohttp
import hashlib
import base64
import logging
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

@dataclass
class OSINTTarget:
    """OSINT investigation target"""
    identifier: str  # domain, email, username, IP, etc.
    target_type: str  # domain, email, username, ip, phone, etc.
    priority: int = 1  # 1-5 priority level
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class OSINTResult:
    """OSINT investigation result"""
    target: str
    source_module: str
    result_type: str  # profile, email, domain, ip, social, leak, etc.
    data: Dict[str, Any]
    confidence: float = 0.0  # 0.0-1.0
    discovered_at: datetime = field(default_factory=datetime.now)
    verified: bool = False
    risk_level: str = "unknown"  # low, medium, high, critical

@dataclass
class SocialMediaProfile:
    """Social media profile information"""
    platform: str
    username: str
    url: str
    display_name: str = ""
    bio: str = ""
    followers: int = 0
    following: int = 0
    posts: int = 0
    verified: bool = False
    profile_image: str = ""
    last_activity: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class OSINTModule:
    """Base class for OSINT modules"""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        self.rate_limit = 1.0  # seconds between requests
        self.timeout = 30  # request timeout
        self.last_request = 0
        
    async def investigate(self, target: OSINTTarget) -> List[OSINTResult]:
        """Override in subclasses"""
        raise NotImplementedError
    
    def can_handle(self, target_type: str) -> bool:
        """Override in subclasses"""
        return False

class SpiderFootIntegration(OSINTModule):
    """Integration with existing SpiderFoot functionality"""
    
    def __init__(self):
        super().__init__("SpiderFoot")
        self.base_url = "http://localhost:5001"  # Default SpiderFoot API
        self.session = None
        
    def can_handle(self, target_type: str) -> bool:
        return target_type in ["domain", "ip", "email", "username"]
    
    async def investigate(self, target: OSINTTarget) -> List[OSINTResult]:
        """Run SpiderFoot scan via API"""
        results = []
        
        try:
            # Start SpiderFoot scan
            scan_id = await self._start_scan(target)
            if not scan_id:
                return results
            
            # Poll for results
            scan_results = await self._get_scan_results(scan_id)
            
            # Convert SpiderFoot results to OSINTResult format
            for result in scan_results:
                osint_result = OSINTResult(
                    target=target.identifier,
                    source_module="SpiderFoot",
                    result_type=result.get("type", "unknown"),
                    data=result,
                    confidence=self._calculate_confidence(result),
                    risk_level=self._assess_risk(result)
                )
                results.append(osint_result)
                
        except Exception as e:
            logger.error(f"SpiderFoot integration error: {e}")
        
        return results
    
    async def _start_scan(self, target: OSINTTarget) -> Optional[str]:
        """Start SpiderFoot scan"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Configure modules based on target type
            modules = self._get_modules_for_target(target.target_type)
            
            scan_data = {
                "scanname": f"OSINT_{target.identifier}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "scantarget": target.identifier,
                "modulelist": ",".join(modules),
                "typelist": target.target_type
            }
            
            async with self.session.post(f"{self.base_url}/startscan", data=scan_data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("id")
                    
        except Exception as e:
            logger.error(f"Error starting SpiderFoot scan: {e}")
        
        return None
    
    async def _get_scan_results(self, scan_id: str, max_wait: int = 300) -> List[Dict]:
        """Get SpiderFoot scan results"""
        if not self.session:
            return []
        
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < max_wait:
            try:
                # Check scan status
                async with self.session.get(f"{self.base_url}/scansummary", 
                                          params={"id": scan_id}) as response:
                    if response.status == 200:
                        summary = await response.json()
                        status = summary.get("status", "UNKNOWN")
                        
                        if status == "FINISHED":
                            # Get detailed results
                            return await self._fetch_detailed_results(scan_id)
                        elif status == "ERROR":
                            logger.error(f"SpiderFoot scan {scan_id} failed")
                            break
                        
                # Wait before next check
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error checking scan status: {e}")
                break
        
        return []
    
    async def _fetch_detailed_results(self, scan_id: str) -> List[Dict]:
        """Fetch detailed scan results"""
        if not self.session:
            return []
        
        try:
            async with self.session.get(f"{self.base_url}/scaneventresults", 
                                      params={"id": scan_id, "format": "json"}) as response:
                if response.status == 200:
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Error fetching detailed results: {e}")
        
        return []
    
    def _get_modules_for_target(self, target_type: str) -> List[str]:
        """Get appropriate SpiderFoot modules for target type"""
        module_map = {
            "domain": [
                "sfp_dnsresolve", "sfp_dnsbrute", "sfp_whois", "sfp_crt",
                "sfp_virustotal", "sfp_shodan", "sfp_censys", "sfp_urlscan"
            ],
            "ip": [
                "sfp_geoip", "sfp_shodan", "sfp_censys", "sfp_virustotal",
                "sfp_threatminer", "sfp_otx", "sfp_abuseipdb"
            ],
            "email": [
                "sfp_haveibeenpwned", "sfp_hunter", "sfp_emailrep",
                "sfp_skymem", "sfp_clearbit"
            ],
            "username": [
                "sfp_whatsmyname", "sfp_social", "sfp_github", "sfp_twitter"
            ]
        }
        
        return module_map.get(target_type, ["sfp_dnsresolve"])
    
    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate confidence score for result"""
        # Simple confidence calculation based on result type and data
        result_type = result.get("type", "")
        data = result.get("data", "")
        
        if result_type in ["IP_ADDRESS", "DOMAIN_NAME"]:
            return 0.9
        elif result_type in ["EMAIL_ADDRESS", "PHONE_NUMBER"]:
            return 0.8
        elif result_type in ["SOCIAL_MEDIA", "USERNAME"]:
            return 0.7
        elif "BREACH" in result_type:
            return 0.95
        else:
            return 0.5
    
    def _assess_risk(self, result: Dict) -> str:
        """Assess risk level of result"""
        result_type = result.get("type", "")
        data = result.get("data", "").lower()
        
        if "breach" in result_type.lower() or "leak" in data:
            return "critical"
        elif "malware" in data or "blacklist" in data:
            return "high"
        elif "social" in result_type.lower():
            return "medium"
        else:
            return "low"

class SocialMediaAnalyzer(OSINTModule):
    """Social media profile analyzer"""
    
    def __init__(self):
        super().__init__("SocialMedia")
        self.platforms = [
            "twitter", "linkedin", "facebook", "instagram", "github",
            "reddit", "tiktok", "youtube", "telegram", "discord"
        ]
        
    def can_handle(self, target_type: str) -> bool:
        return target_type in ["username", "email", "domain"]
    
    async def investigate(self, target: OSINTTarget) -> List[OSINTResult]:
        """Analyze social media presence"""
        results = []
        
        if target.target_type == "username":
            profiles = await self._find_username_profiles(target.identifier)
            for profile in profiles:
                result = OSINTResult(
                    target=target.identifier,
                    source_module="SocialMedia",
                    result_type="social_profile",
                    data=profile.__dict__,
                    confidence=0.8,
                    risk_level="medium"
                )
                results.append(result)
        
        elif target.target_type == "domain":
            social_links = await self._find_domain_social_links(target.identifier)
            for link in social_links:
                result = OSINTResult(
                    target=target.identifier,
                    source_module="SocialMedia",
                    result_type="social_link",
                    data=link,
                    confidence=0.7,
                    risk_level="low"
                )
                results.append(result)
        
        return results
    
    async def _find_username_profiles(self, username: str) -> List[SocialMediaProfile]:
        """Find social media profiles for username"""
        profiles = []
        
        # Common social media URL patterns
        platforms = {
            "twitter": "https://twitter.com/{}",
            "github": "https://github.com/{}",
            "instagram": "https://instagram.com/{}",
            "linkedin": "https://linkedin.com/in/{}",
            "reddit": "https://reddit.com/user/{}",
            "youtube": "https://youtube.com/c/{}",
            "tiktok": "https://tiktok.com/@{}"
        }
        
        async with aiohttp.ClientSession() as session:
            for platform, url_pattern in platforms.items():
                url = url_pattern.format(username)
                
                try:
                    async with session.head(url, timeout=10, allow_redirects=True) as response:
                        if response.status == 200:
                            profile = SocialMediaProfile(
                                platform=platform,
                                username=username,
                                url=url
                            )
                            
                            # Try to get additional profile info
                            await self._enrich_profile(session, profile)
                            profiles.append(profile)
                            
                except Exception as e:
                    logger.debug(f"Profile check failed for {platform}: {e}")
        
        return profiles
    
    async def _enrich_profile(self, session: aiohttp.ClientSession, profile: SocialMediaProfile):
        """Enrich profile with additional information"""
        try:
            async with session.get(profile.url, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Extract basic information from HTML (simple parsing)
                    if profile.platform == "github":
                        profile.display_name = self._extract_github_name(content)
                        profile.bio = self._extract_github_bio(content)
                    elif profile.platform == "linkedin":
                        profile.display_name = self._extract_linkedin_name(content)
                    
        except Exception as e:
            logger.debug(f"Profile enrichment failed: {e}")
    
    def _extract_github_name(self, html: str) -> str:
        """Extract GitHub display name"""
        match = re.search(r'<span[^>]*itemprop="name"[^>]*>([^<]+)</span>', html)
        return match.group(1).strip() if match else ""
    
    def _extract_github_bio(self, html: str) -> str:
        """Extract GitHub bio"""
        match = re.search(r'<div[^>]*class="[^"]*user-profile-bio[^"]*"[^>]*>([^<]+)</div>', html)
        return match.group(1).strip() if match else ""
    
    def _extract_linkedin_name(self, html: str) -> str:
        """Extract LinkedIn name"""
        match = re.search(r'<title>([^|]+)\|', html)
        return match.group(1).strip() if match else ""
    
    async def _find_domain_social_links(self, domain: str) -> List[Dict[str, str]]:
        """Find social media links associated with domain"""
        social_links = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Check domain's main page for social links
                async with session.get(f"https://{domain}", timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Look for social media links
                        social_patterns = {
                            "twitter": r'https?://(?:www\.)?twitter\.com/[a-zA-Z0-9_]+',
                            "facebook": r'https?://(?:www\.)?facebook\.com/[a-zA-Z0-9._]+',
                            "linkedin": r'https?://(?:www\.)?linkedin\.com/(?:company|in)/[a-zA-Z0-9._-]+',
                            "instagram": r'https?://(?:www\.)?instagram\.com/[a-zA-Z0-9._]+',
                            "youtube": r'https?://(?:www\.)?youtube\.com/(?:channel|c|user)/[a-zA-Z0-9._-]+',
                            "github": r'https?://(?:www\.)?github\.com/[a-zA-Z0-9._-]+'
                        }
                        
                        for platform, pattern in social_patterns.items():
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                social_links.append({
                                    "platform": platform,
                                    "url": match,
                                    "found_on": domain
                                })
        
        except Exception as e:
            logger.debug(f"Domain social link search failed: {e}")
        
        return social_links

class DataBreachChecker(OSINTModule):
    """Check for data breaches and leaks"""
    
    def __init__(self):
        super().__init__("DataBreach")
        
    def can_handle(self, target_type: str) -> bool:
        return target_type in ["email", "domain", "username"]
    
    async def investigate(self, target: OSINTTarget) -> List[OSINTResult]:
        """Check for data breaches"""
        results = []
        
        if target.target_type == "email":
            breaches = await self._check_email_breaches(target.identifier)
            for breach in breaches:
                result = OSINTResult(
                    target=target.identifier,
                    source_module="DataBreach",
                    result_type="data_breach",
                    data=breach,
                    confidence=0.9,
                    risk_level="critical"
                )
                results.append(result)
        
        return results
    
    async def _check_email_breaches(self, email: str) -> List[Dict]:
        """Check email against breach databases"""
        breaches = []
        
        # This would integrate with services like:
        # - Have I Been Pwned API
        # - DeHashed
        # - Intelligence X
        # For demonstration, returning mock data
        
        mock_breaches = [
            {
                "breach_name": "Example Breach 2023",
                "date_discovered": "2023-05-15",
                "records_affected": 1500000,
                "data_types": ["emails", "passwords", "usernames"],
                "severity": "high",
                "source": "mock_data"
            }
        ]
        
        return mock_breaches

class OSINTWorker(QThread):
    """Background worker for OSINT investigations"""
    
    progress_updated = pyqtSignal(int)
    result_found = pyqtSignal(object)  # OSINTResult
    investigation_complete = pyqtSignal(str)  # target identifier
    error_occurred = pyqtSignal(str)
    
    def __init__(self, targets: List[OSINTTarget], modules: List[OSINTModule]):
        super().__init__()
        self.targets = targets
        self.modules = modules
        self.is_running = True
        
    def run(self):
        """Run OSINT investigation"""
        try:
            total_targets = len(self.targets)
            
            for i, target in enumerate(self.targets):
                if not self.is_running:
                    break
                
                # Run investigation with applicable modules
                for module in self.modules:
                    if not self.is_running:
                        break
                    
                    if module.enabled and module.can_handle(target.target_type):
                        try:
                            # Create event loop for async operation
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            
                            results = loop.run_until_complete(module.investigate(target))
                            
                            for result in results:
                                self.result_found.emit(result)
                            
                            loop.close()
                            
                        except Exception as e:
                            self.error_occurred.emit(f"Module {module.name} error: {e}")
                
                self.investigation_complete.emit(target.identifier)
                progress = int((i + 1) / total_targets * 100)
                self.progress_updated.emit(progress)
                
        except Exception as e:
            self.error_occurred.emit(f"Investigation error: {e}")
    
    def stop(self):
        """Stop investigation"""
        self.is_running = False

class OSINTIntegrationWidget(QWidget):
    """Main OSINT integration widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize modules
        self.modules = [
            SpiderFootIntegration(),
            SocialMediaAnalyzer(),
            DataBreachChecker()
        ]
        
        self.targets: List[OSINTTarget] = []
        self.results: List[OSINTResult] = []
        self.current_worker = None
        
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Setup the OSINT UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Target management tab
        target_tab = self.create_target_tab()
        self.tabs.addTab(target_tab, "Targets")
        
        # Investigation tab
        investigation_tab = self.create_investigation_tab()
        self.tabs.addTab(investigation_tab, "Investigation")
        
        # Results tab
        results_tab = self.create_results_tab()
        self.tabs.addTab(results_tab, "Results")
        
        # Social media tab
        social_tab = self.create_social_tab()
        self.tabs.addTab(social_tab, "Social Media")
        
        # Reports tab
        reports_tab = self.create_reports_tab()
        self.tabs.addTab(reports_tab, "Reports")
        
        layout.addWidget(self.tabs)
    
    def create_target_tab(self) -> QWidget:
        """Create target management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Target input
        input_group = QGroupBox("Add Target")
        input_layout = QGridLayout(input_group)
        
        input_layout.addWidget(QLabel("Target:"), 0, 0)
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("domain.com, email@example.com, username, IP address...")
        input_layout.addWidget(self.target_input, 0, 1)
        
        input_layout.addWidget(QLabel("Type:"), 1, 0)
        self.target_type = QComboBox()
        self.target_type.addItems(["domain", "email", "username", "ip", "phone"])
        input_layout.addWidget(self.target_type, 1, 1)
        
        input_layout.addWidget(QLabel("Priority:"), 2, 0)
        self.target_priority = QSpinBox()
        self.target_priority.setRange(1, 5)
        self.target_priority.setValue(3)
        input_layout.addWidget(self.target_priority, 2, 1)
        
        self.add_target_btn = QPushButton("Add Target")
        input_layout.addWidget(self.add_target_btn, 3, 0, 1, 2)
        
        # Target list
        targets_group = QGroupBox("Targets")
        targets_layout = QVBoxLayout(targets_group)
        
        self.targets_table = QTableWidget()
        self.targets_table.setColumnCount(5)
        self.targets_table.setHorizontalHeaderLabels(["Target", "Type", "Priority", "Added", "Status"])
        self.targets_table.horizontalHeader().setStretchLastSection(True)
        targets_layout.addWidget(self.targets_table)
        
        # Target actions
        target_actions = QHBoxLayout()
        self.remove_target_btn = QPushButton("Remove Selected")
        self.clear_targets_btn = QPushButton("Clear All")
        self.import_targets_btn = QPushButton("Import from File")
        self.export_targets_btn = QPushButton("Export Targets")
        
        target_actions.addWidget(self.remove_target_btn)
        target_actions.addWidget(self.clear_targets_btn)
        target_actions.addWidget(self.import_targets_btn)
        target_actions.addWidget(self.export_targets_btn)
        target_actions.addStretch()
        
        targets_layout.addLayout(target_actions)
        
        layout.addWidget(input_group)
        layout.addWidget(targets_group)
        
        return widget
    
    def create_investigation_tab(self) -> QWidget:
        """Create investigation control tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Module configuration
        modules_group = QGroupBox("OSINT Modules")
        modules_layout = QVBoxLayout(modules_group)
        
        self.module_checkboxes = {}
        for module in self.modules:
            checkbox = QCheckBox(f"{module.name} - {module.__class__.__doc__ or 'No description'}")
            checkbox.setChecked(module.enabled)
            self.module_checkboxes[module.name] = checkbox
            modules_layout.addWidget(checkbox)
        
        # Investigation controls
        control_group = QGroupBox("Investigation Control")
        control_layout = QHBoxLayout(control_group)
        
        self.start_investigation_btn = QPushButton("Start Investigation")
        self.stop_investigation_btn = QPushButton("Stop Investigation")
        self.stop_investigation_btn.setEnabled(False)
        
        control_layout.addWidget(self.start_investigation_btn)
        control_layout.addWidget(self.stop_investigation_btn)
        control_layout.addStretch()
        
        # Progress
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Ready to start investigation")
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        
        # Live results
        live_group = QGroupBox("Live Results")
        live_layout = QVBoxLayout(live_group)
        
        self.live_results = QTextEdit()
        self.live_results.setMaximumHeight(200)
        self.live_results.setReadOnly(True)
        live_layout.addWidget(self.live_results)
        
        layout.addWidget(modules_group)
        layout.addWidget(control_group)
        layout.addWidget(progress_group)
        layout.addWidget(live_group)
        
        return widget
    
    def create_results_tab(self) -> QWidget:
        """Create results display tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Results filter
        filter_group = QGroupBox("Filter Results")
        filter_layout = QHBoxLayout(filter_group)
        
        filter_layout.addWidget(QLabel("Source:"))
        self.source_filter = QComboBox()
        self.source_filter.addItem("All Sources")
        filter_layout.addWidget(self.source_filter)
        
        filter_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types")
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addWidget(QLabel("Risk:"))
        self.risk_filter = QComboBox()
        self.risk_filter.addItems(["All Risks", "Critical", "High", "Medium", "Low"])
        filter_layout.addWidget(self.risk_filter)
        
        self.apply_filter_btn = QPushButton("Apply Filter")
        filter_layout.addWidget(self.apply_filter_btn)
        
        filter_layout.addStretch()
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "Target", "Source", "Type", "Risk", "Confidence", "Discovered", "Verified"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        # Results details
        details_group = QGroupBox("Result Details")
        details_layout = QVBoxLayout(details_group)
        
        self.result_details = QTextEdit()
        self.result_details.setMaximumHeight(150)
        self.result_details.setReadOnly(True)
        details_layout.addWidget(self.result_details)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top part
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.addWidget(filter_group)
        top_layout.addWidget(self.results_table)
        
        splitter.addWidget(top_widget)
        splitter.addWidget(details_group)
        splitter.setSizes([400, 150])
        
        layout.addWidget(splitter)
        
        return widget
    
    def create_social_tab(self) -> QWidget:
        """Create social media analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Social media profiles
        profiles_group = QGroupBox("Social Media Profiles")
        profiles_layout = QVBoxLayout(profiles_group)
        
        self.social_tree = QTreeWidget()
        self.social_tree.setHeaderLabels(["Platform", "Username", "Display Name", "Verified"])
        profiles_layout.addWidget(self.social_tree)
        
        # Profile details
        profile_details_group = QGroupBox("Profile Details")
        profile_details_layout = QVBoxLayout(profile_details_group)
        
        self.profile_details = QTextEdit()
        self.profile_details.setMaximumHeight(200)
        self.profile_details.setReadOnly(True)
        profile_details_layout.addWidget(self.profile_details)
        
        layout.addWidget(profiles_group)
        layout.addWidget(profile_details_group)
        
        return widget
    
    def create_reports_tab(self) -> QWidget:
        """Create reports tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Report generation
        report_group = QGroupBox("Generate Report")
        report_layout = QGridLayout(report_group)
        
        report_layout.addWidget(QLabel("Report Type:"), 0, 0)
        self.report_type = QComboBox()
        self.report_type.addItems(["Summary", "Detailed", "Social Media", "Risk Assessment"])
        report_layout.addWidget(self.report_type, 0, 1)
        
        report_layout.addWidget(QLabel("Format:"), 1, 0)
        self.report_format = QComboBox()
        self.report_format.addItems(["JSON", "PDF", "HTML", "CSV"])
        report_layout.addWidget(self.report_format, 1, 1)
        
        self.generate_report_btn = QPushButton("Generate Report")
        report_layout.addWidget(self.generate_report_btn, 2, 0, 1, 2)
        
        # Report preview
        preview_group = QGroupBox("Report Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.report_preview = QTextEdit()
        self.report_preview.setReadOnly(True)
        preview_layout.addWidget(self.report_preview)
        
        layout.addWidget(report_group)
        layout.addWidget(preview_group)
        
        return widget
    
    def connect_signals(self):
        """Connect UI signals"""
        self.add_target_btn.clicked.connect(self.add_target)
        self.remove_target_btn.clicked.connect(self.remove_selected_target)
        self.clear_targets_btn.clicked.connect(self.clear_targets)
        
        self.start_investigation_btn.clicked.connect(self.start_investigation)
        self.stop_investigation_btn.clicked.connect(self.stop_investigation)
        
        self.apply_filter_btn.clicked.connect(self.apply_results_filter)
        self.results_table.itemSelectionChanged.connect(self.show_result_details)
        
        self.social_tree.itemSelectionChanged.connect(self.show_profile_details)
        
        self.generate_report_btn.clicked.connect(self.generate_report)
        
        # Update module checkboxes
        for name, checkbox in self.module_checkboxes.items():
            checkbox.stateChanged.connect(lambda state, n=name: self.toggle_module(n, state))
    
    def add_target(self):
        """Add new OSINT target"""
        identifier = self.target_input.text().strip()
        if not identifier:
            return
        
        target = OSINTTarget(
            identifier=identifier,
            target_type=self.target_type.currentText(),
            priority=self.target_priority.value()
        )
        
        self.targets.append(target)
        self.update_targets_table()
        
        self.target_input.clear()
    
    def update_targets_table(self):
        """Update targets table"""
        self.targets_table.setRowCount(len(self.targets))
        
        for i, target in enumerate(self.targets):
            self.targets_table.setItem(i, 0, QTableWidgetItem(target.identifier))
            self.targets_table.setItem(i, 1, QTableWidgetItem(target.target_type))
            self.targets_table.setItem(i, 2, QTableWidgetItem(str(target.priority)))
            self.targets_table.setItem(i, 3, QTableWidgetItem(
                target.created_at.strftime("%Y-%m-%d %H:%M")
            ))
            self.targets_table.setItem(i, 4, QTableWidgetItem("Pending"))
    
    def remove_selected_target(self):
        """Remove selected target"""
        current_row = self.targets_table.currentRow()
        if current_row >= 0:
            del self.targets[current_row]
            self.update_targets_table()
    
    def clear_targets(self):
        """Clear all targets"""
        self.targets.clear()
        self.update_targets_table()
    
    def toggle_module(self, module_name: str, state: int):
        """Toggle OSINT module"""
        for module in self.modules:
            if module.name == module_name:
                module.enabled = state == Qt.CheckState.Checked.value
                break
    
    def start_investigation(self):
        """Start OSINT investigation"""
        if not self.targets:
            self.progress_label.setText("No targets defined")
            return
        
        # Enable only checked modules
        enabled_modules = []
        for module in self.modules:
            if module.enabled:
                enabled_modules.append(module)
        
        if not enabled_modules:
            self.progress_label.setText("No modules enabled")
            return
        
        # Start worker thread
        self.current_worker = OSINTWorker(self.targets.copy(), enabled_modules)
        self.current_worker.progress_updated.connect(self.progress_bar.setValue)
        self.current_worker.result_found.connect(self.add_result)
        self.current_worker.investigation_complete.connect(self.target_complete)
        self.current_worker.error_occurred.connect(self.investigation_error)
        
        self.start_investigation_btn.setEnabled(False)
        self.stop_investigation_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Investigation started...")
        
        self.current_worker.start()
    
    def stop_investigation(self):
        """Stop current investigation"""
        if self.current_worker:
            self.current_worker.stop()
            self.current_worker = None
        
        self.start_investigation_btn.setEnabled(True)
        self.stop_investigation_btn.setEnabled(False)
        self.progress_label.setText("Investigation stopped")
    
    def add_result(self, result: OSINTResult):
        """Add investigation result"""
        self.results.append(result)
        self.update_results_table()
        
        # Add to live results
        result_text = f"[{result.source_module}] {result.target} - {result.result_type} (Risk: {result.risk_level})\n"
        self.live_results.append(result_text)
        
        # Update social media tree if applicable
        if result.result_type == "social_profile":
            self.update_social_tree(result)
    
    def target_complete(self, target_identifier: str):
        """Handle target completion"""
        self.progress_label.setText(f"Completed: {target_identifier}")
    
    def investigation_error(self, error_message: str):
        """Handle investigation error"""
        self.live_results.append(f"ERROR: {error_message}\n")
    
    def update_results_table(self):
        """Update results table"""
        self.results_table.setRowCount(len(self.results))
        
        for i, result in enumerate(self.results):
            self.results_table.setItem(i, 0, QTableWidgetItem(result.target))
            self.results_table.setItem(i, 1, QTableWidgetItem(result.source_module))
            self.results_table.setItem(i, 2, QTableWidgetItem(result.result_type))
            self.results_table.setItem(i, 3, QTableWidgetItem(result.risk_level))
            self.results_table.setItem(i, 4, QTableWidgetItem(f"{result.confidence:.2f}"))
            self.results_table.setItem(i, 5, QTableWidgetItem(
                result.discovered_at.strftime("%Y-%m-%d %H:%M")
            ))
            self.results_table.setItem(i, 6, QTableWidgetItem(
                "Yes" if result.verified else "No"
            ))
            
            # Color-code by risk level
            if result.risk_level == "critical":
                color = QColor(255, 0, 0, 50)
            elif result.risk_level == "high":
                color = QColor(255, 165, 0, 50)
            elif result.risk_level == "medium":
                color = QColor(255, 255, 0, 50)
            else:
                color = QColor(0, 255, 0, 50)
            
            for col in range(self.results_table.columnCount()):
                item = self.results_table.item(i, col)
                if item:
                    item.setBackground(color)
    
    def show_result_details(self):
        """Show details for selected result"""
        current_row = self.results_table.currentRow()
        if current_row >= 0 and current_row < len(self.results):
            result = self.results[current_row]
            
            details = f"""
Target: {result.target}
Source Module: {result.source_module}
Result Type: {result.result_type}
Risk Level: {result.risk_level}
Confidence: {result.confidence:.2f}
Discovered: {result.discovered_at}
Verified: {'Yes' if result.verified else 'No'}

Data:
{json.dumps(result.data, indent=2)}
            """.strip()
            
            self.result_details.setText(details)
    
    def update_social_tree(self, result: OSINTResult):
        """Update social media tree with result"""
        if result.result_type == "social_profile":
            data = result.data
            platform = data.get("platform", "Unknown")
            username = data.get("username", "Unknown")
            display_name = data.get("display_name", "")
            verified = "Yes" if data.get("verified", False) else "No"
            
            item = QTreeWidgetItem([platform, username, display_name, verified])
            item.setData(0, Qt.ItemDataRole.UserRole, result)
            self.social_tree.addTopLevelItem(item)
    
    def show_profile_details(self):
        """Show social media profile details"""
        current_item = self.social_tree.currentItem()
        if current_item:
            result = current_item.data(0, Qt.ItemDataRole.UserRole)
            if result:
                data = result.data
                
                details = f"""
Platform: {data.get("platform", "Unknown")}
Username: {data.get("username", "Unknown")}
Display Name: {data.get("display_name", "N/A")}
URL: {data.get("url", "N/A")}
Bio: {data.get("bio", "N/A")}
Followers: {data.get("followers", "N/A")}
Following: {data.get("following", "N/A")}
Posts: {data.get("posts", "N/A")}
Verified: {'Yes' if data.get("verified", False) else 'No'}
Last Activity: {data.get("last_activity", "N/A")}
                """.strip()
                
                self.profile_details.setText(details)
    
    def apply_results_filter(self):
        """Apply results filter"""
        # Implementation would filter results table based on selected criteria
        pass
    
    def generate_report(self):
        """Generate investigation report"""
        report_type = self.report_type.currentText()
        format_type = self.report_format.currentText()
        
        if format_type == "JSON":
            report = self.generate_json_report(report_type)
        else:
            report = f"Report generation for {format_type} not implemented yet."
        
        self.report_preview.setText(report)
    
    def generate_json_report(self, report_type: str) -> str:
        """Generate JSON report"""
        report_data = {
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "targets": [
                {
                    "identifier": t.identifier,
                    "type": t.target_type,
                    "priority": t.priority
                }
                for t in self.targets
            ],
            "results": [
                {
                    "target": r.target,
                    "source_module": r.source_module,
                    "result_type": r.result_type,
                    "risk_level": r.risk_level,
                    "confidence": r.confidence,
                    "discovered_at": r.discovered_at.isoformat(),
                    "verified": r.verified,
                    "data": r.data
                }
                for r in self.results
            ],
            "summary": {
                "total_targets": len(self.targets),
                "total_results": len(self.results),
                "high_risk_results": len([r for r in self.results if r.risk_level in ["high", "critical"]]),
                "verified_results": len([r for r in self.results if r.verified])
            }
        }
        
        return json.dumps(report_data, indent=2)
