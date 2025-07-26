"""
Data Enrichment System with Commercial API Integration and Human-in-the-Loop Validation
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QComboBox,
    QCheckBox,
    QLineEdit,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QProgressBar,
    QSplitter,
    QSpinBox,
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QRadioButton,
    QButtonGroup,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import asyncio
import aiohttp
import time
import logging
from pathlib import Path
from enum import Enum
import uuid
import sys

# Add config directory to path
config_dir = Path(__file__).parent.parent.parent / "config"
sys.path.insert(0, str(config_dir))

try:
    from config_loader import get_config, save_config
except ImportError:
    # Fallback if config loader not available
    def get_config():
        return {"api_credentials": {}, "tor_config": {"enabled": True}}

    def save_config(config):
        pass


logger = logging.getLogger(__name__)


class EnrichmentProvider(Enum):
    """Commercial enrichment providers"""

    CLEARBIT = "clearbit"
    FULLCONTACT = "fullcontact"
    PIPL = "pipl"
    WHITEPAGES = "whitepages"
    HUNTER = "hunter"
    ZEROBOUNCE = "zerobounce"
    MAXMIND = "maxmind"
    SHODAN = "shodan"
    VIRUSTOTAL = "virustotal"
    OPENCORPORATES = "opencorporates"


class EnrichmentStatus(Enum):
    """Enrichment status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class DataQuality(Enum):
    """Data quality levels"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class EnrichmentRequest:
    """Data enrichment request"""

    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    target: str = ""
    target_type: str = ""  # email, domain, ip, company, person
    providers: List[EnrichmentProvider] = field(default_factory=list)
    priority: int = 1
    auto_approve: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    status: EnrichmentStatus = EnrichmentStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnrichmentResult:
    """Enriched data result"""

    request_id: str
    provider: EnrichmentProvider
    target: str
    data_type: str
    enriched_data: Dict[str, Any]
    confidence_score: float = 0.0
    quality_score: DataQuality = DataQuality.UNKNOWN
    cost: float = 0.0  # API cost if applicable
    processing_time: float = 0.0
    status: EnrichmentStatus = EnrichmentStatus.PENDING
    requires_review: bool = False
    review_notes: str = ""
    reviewed_by: str = ""
    reviewed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationRule:
    """Data validation rule"""

    rule_id: str
    field_name: str
    rule_type: str  # format, range, enum, custom
    rule_params: Dict[str, Any]
    error_message: str
    severity: str = "warning"  # warning, error, critical


class APIProvider:
    """Base class for commercial API providers"""

    def __init__(self, name: str, provider: EnrichmentProvider):
        self.name = name
        self.provider = provider
        self.api_key = ""
        self.base_url = ""
        self.rate_limit = 1.0
        self.timeout = 30
        self.enabled = False
        self.cost_per_request = 0.0
        self.monthly_quota = 0
        self.requests_used = 0
        self.last_request = 0

    async def enrich(self, target: str, target_type: str, **kwargs) -> Dict[str, Any]:
        """Override in subclasses"""
        raise NotImplementedError

    def can_handle(self, target_type: str) -> bool:
        """Override in subclasses"""
        return False

    def calculate_cost(self, request_count: int) -> float:
        """Calculate API cost"""
        return request_count * self.cost_per_request

    def check_quota(self) -> bool:
        """Check if quota is available"""
        return self.requests_used < self.monthly_quota


class ClearbitProvider(APIProvider):
    """Clearbit API integration"""

    def __init__(self):
        super().__init__("Clearbit", EnrichmentProvider.CLEARBIT)
        self.base_url = "https://person-stream.clearbit.com/v2"
        self.cost_per_request = 0.05  # Example cost

    def can_handle(self, target_type: str) -> bool:
        return target_type in ["email", "domain", "company"]

    async def enrich(self, target: str, target_type: str, **kwargs) -> Dict[str, Any]:
        """Enrich data using Clearbit API"""
        if not self.enabled or not self.api_key:
            return {}

        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            async with aiohttp.ClientSession() as session:
                if target_type == "email":
                    url = f"{self.base_url}/people/find?email={target}"
                elif target_type == "domain":
                    url = f"{self.base_url}/companies/find?domain={target}"
                else:
                    return {}

                async with session.get(
                    url, headers=headers, timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._normalize_clearbit_data(data, target_type)
                    else:
                        logger.warning(f"Clearbit API error: {response.status}")
                        return {}

        except Exception as e:
            logger.error(f"Clearbit enrichment error: {e}")
            return {}

    def _normalize_clearbit_data(self, data: Dict, target_type: str) -> Dict[str, Any]:
        """Normalize Clearbit response data"""
        normalized = {
            "provider": "clearbit",
            "target_type": target_type,
            "raw_data": data,
        }

        if target_type == "email" and "person" in data:
            person = data["person"]
            normalized.update(
                {
                    "name": person.get("name", {}),
                    "email": person.get("email"),
                    "location": person.get("location"),
                    "employment": person.get("employment", {}),
                    "social": person.get("social", {}),
                }
            )

        elif target_type == "domain" and "company" in data:
            company = data["company"]
            normalized.update(
                {
                    "name": company.get("name"),
                    "domain": company.get("domain"),
                    "category": company.get("category"),
                    "metrics": company.get("metrics", {}),
                    "tech": company.get("tech", []),
                }
            )

        return normalized


class FullContactProvider(APIProvider):
    """FullContact API integration"""

    def __init__(self):
        super().__init__("FullContact", EnrichmentProvider.FULLCONTACT)
        self.base_url = "https://api.fullcontact.com/v3"
        self.cost_per_request = 0.03

    def can_handle(self, target_type: str) -> bool:
        return target_type in ["email", "phone", "domain"]

    async def enrich(self, target: str, target_type: str, **kwargs) -> Dict[str, Any]:
        """Enrich data using FullContact API"""
        if not self.enabled or not self.api_key:
            return {}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                if target_type == "email":
                    url = f"{self.base_url}/person.enrich"
                    payload = {"email": target}
                elif target_type == "phone":
                    url = f"{self.base_url}/person.enrich"
                    payload = {"phone": target}
                elif target_type == "domain":
                    url = f"{self.base_url}/company.enrich"
                    payload = {"domain": target}
                else:
                    return {}

                async with session.post(
                    url, headers=headers, json=payload, timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._normalize_fullcontact_data(data, target_type)
                    else:
                        logger.warning(f"FullContact API error: {response.status}")
                        return {}

        except Exception as e:
            logger.error(f"FullContact enrichment error: {e}")
            return {}

    def _normalize_fullcontact_data(
        self, data: Dict, target_type: str
    ) -> Dict[str, Any]:
        """Normalize FullContact response data"""
        return {
            "provider": "fullcontact",
            "target_type": target_type,
            "person": data.get("person", {}),
            "company": data.get("company", {}),
            "social": data.get("socialProfiles", []),
            "demographics": data.get("demographics", {}),
            "raw_data": data,
        }


class HunterProvider(APIProvider):
    """Hunter.io API integration for email finding and verification"""

    def __init__(self):
        super().__init__("Hunter", EnrichmentProvider.HUNTER)
        self.base_url = "https://api.hunter.io/v2"
        self.cost_per_request = 0.01

    def can_handle(self, target_type: str) -> bool:
        return target_type in ["email", "domain"]

    async def enrich(self, target: str, target_type: str, **kwargs) -> Dict[str, Any]:
        """Enrich data using Hunter.io API"""
        if not self.enabled or not self.api_key:
            return {}

        params = {"api_key": self.api_key}

        try:
            async with aiohttp.ClientSession() as session:
                if target_type == "email":
                    params["email"] = target
                    url = f"{self.base_url}/email-verifier"
                elif target_type == "domain":
                    params["domain"] = target
                    url = f"{self.base_url}/domain-search"
                else:
                    return {}

                async with session.get(
                    url, params=params, timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._normalize_hunter_data(data, target_type)
                    else:
                        logger.warning(f"Hunter API error: {response.status}")
                        return {}

        except Exception as e:
            logger.error(f"Hunter enrichment error: {e}")
            return {}

    def _normalize_hunter_data(self, data: Dict, target_type: str) -> Dict[str, Any]:
        """Normalize Hunter response data"""
        normalized = {
            "provider": "hunter",
            "target_type": target_type,
            "raw_data": data,
        }

        if target_type == "email":
            result = data.get("data", {})
            normalized.update(
                {
                    "email": result.get("email"),
                    "result": result.get("result"),  # deliverable, undeliverable, risky
                    "score": result.get("score"),
                    "regexp": result.get("regexp"),
                    "gibberish": result.get("gibberish"),
                    "disposable": result.get("disposable"),
                    "webmail": result.get("webmail"),
                    "mx_records": result.get("mx_records"),
                    "smtp_server": result.get("smtp_server"),
                    "smtp_check": result.get("smtp_check"),
                }
            )

        elif target_type == "domain":
            normalized.update(
                {
                    "domain": data.get("data", {}).get("domain"),
                    "disposable": data.get("data", {}).get("disposable"),
                    "webmail": data.get("data", {}).get("webmail"),
                    "pattern": data.get("data", {}).get("pattern"),
                    "organization": data.get("data", {}).get("organization"),
                    "emails": data.get("data", {}).get("emails", []),
                }
            )

        return normalized


class ShodanProvider(APIProvider):
    """Shodan API integration for IP intelligence"""

    def __init__(self):
        super().__init__("Shodan", EnrichmentProvider.SHODAN)
        self.base_url = "https://api.shodan.io"
        self.cost_per_request = 0.01

    def can_handle(self, target_type: str) -> bool:
        return target_type in ["ip", "domain"]

    async def enrich(self, target: str, target_type: str, **kwargs) -> Dict[str, Any]:
        """Enrich data using Shodan API"""
        if not self.enabled or not self.api_key:
            return {}

        params = {"key": self.api_key}

        try:
            async with aiohttp.ClientSession() as session:
                if target_type == "ip":
                    url = f"{self.base_url}/shodan/host/{target}"
                elif target_type == "domain":
                    url = f"{self.base_url}/dns/domain/{target}"
                else:
                    return {}

                async with session.get(
                    url, params=params, timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._normalize_shodan_data(data, target_type)
                    else:
                        logger.warning(f"Shodan API error: {response.status}")
                        return {}

        except Exception as e:
            logger.error(f"Shodan enrichment error: {e}")
            return {}

    def _normalize_shodan_data(self, data: Dict, target_type: str) -> Dict[str, Any]:
        """Normalize Shodan response data"""
        normalized = {
            "provider": "shodan",
            "target_type": target_type,
            "raw_data": data,
        }

        if target_type == "ip":
            normalized.update(
                {
                    "ip": data.get("ip_str"),
                    "organization": data.get("org"),
                    "country": data.get("country_name"),
                    "city": data.get("city"),
                    "isp": data.get("isp"),
                    "ports": data.get("ports", []),
                    "hostnames": data.get("hostnames", []),
                    "services": data.get("data", []),
                    "vulns": data.get("vulns", []),
                    "tags": data.get("tags", []),
                }
            )

        elif target_type == "domain":
            normalized.update(
                {
                    "domain": data.get("domain"),
                    "subdomain_count": data.get("subdomain_count", 0),
                    "subdomains": data.get("data", []),
                }
            )

        return normalized


class DataValidator:
    """Data validation and quality assessment"""

    def __init__(self):
        self.rules: List[ValidationRule] = []
        self.load_default_rules()

    def load_default_rules(self):
        """Load default validation rules"""
        self.rules = [
            ValidationRule(
                rule_id="email_format",
                field_name="email",
                rule_type="format",
                rule_params={
                    "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                },
                error_message="Invalid email format",
            ),
            ValidationRule(
                rule_id="phone_format",
                field_name="phone",
                rule_type="format",
                rule_params={"pattern": r"^\+?[1-9]\d{1,14}$"},
                error_message="Invalid phone format",
            ),
            ValidationRule(
                rule_id="confidence_threshold",
                field_name="confidence_score",
                rule_type="range",
                rule_params={"min": 0.7},
                error_message="Low confidence score",
                severity="warning",
            ),
        ]

    def validate_result(self, result: EnrichmentResult) -> Tuple[bool, List[str]]:
        """Validate enrichment result"""
        errors = []

        for rule in self.rules:
            error = self._apply_rule(rule, result)
            if error:
                errors.append(error)

        is_valid = len([e for e in errors if "critical" in e or "error" in e]) == 0
        return is_valid, errors

    def _apply_rule(
        self, rule: ValidationRule, result: EnrichmentResult
    ) -> Optional[str]:
        """Apply validation rule to result"""
        try:
            if rule.rule_type == "format":
                value = self._get_field_value(result, rule.field_name)
                if value and not re.match(rule.rule_params["pattern"], str(value)):
                    return f"{rule.severity}: {rule.error_message}"

            elif rule.rule_type == "range":
                value = self._get_field_value(result, rule.field_name)
                if value is not None:
                    if "min" in rule.rule_params and value < rule.rule_params["min"]:
                        return f"{rule.severity}: {rule.error_message}"
                    if "max" in rule.rule_params and value > rule.rule_params["max"]:
                        return f"{rule.severity}: {rule.error_message}"

            elif rule.rule_type == "enum":
                value = self._get_field_value(result, rule.field_name)
                if value and value not in rule.rule_params["values"]:
                    return f"{rule.severity}: {rule.error_message}"

        except Exception as e:
            logger.error(f"Rule application error: {e}")

        return None

    def _get_field_value(self, result: EnrichmentResult, field_name: str) -> Any:
        """Get field value from result"""
        if field_name == "confidence_score":
            return result.confidence_score

        # Look in enriched_data
        return result.enriched_data.get(field_name)


class EnrichmentEngine:
    """Main enrichment engine"""

    def __init__(self):
        self.providers: Dict[EnrichmentProvider, APIProvider] = {
            EnrichmentProvider.CLEARBIT: ClearbitProvider(),
            EnrichmentProvider.FULLCONTACT: FullContactProvider(),
            EnrichmentProvider.HUNTER: HunterProvider(),
            EnrichmentProvider.SHODAN: ShodanProvider(),
        }

        self.validator = DataValidator()
        self.requests: Dict[str, EnrichmentRequest] = {}
        self.results: Dict[str, List[EnrichmentResult]] = {}

    async def enrich_data(self, request: EnrichmentRequest) -> List[EnrichmentResult]:
        """Process enrichment request"""
        results = []

        request.status = EnrichmentStatus.PROCESSING
        self.requests[request.request_id] = request

        for provider_enum in request.providers:
            if provider_enum not in self.providers:
                continue

            provider = self.providers[provider_enum]

            if not provider.enabled or not provider.can_handle(request.target_type):
                continue

            try:
                start_time = time.time()

                # Call API
                enriched_data = await provider.enrich(
                    request.target, request.target_type, **request.metadata
                )

                processing_time = time.time() - start_time

                # Create result
                result = EnrichmentResult(
                    request_id=request.request_id,
                    provider=provider_enum,
                    target=request.target,
                    data_type=request.target_type,
                    enriched_data=enriched_data,
                    confidence_score=self._calculate_confidence(enriched_data),
                    quality_score=self._assess_quality(enriched_data),
                    cost=provider.cost_per_request,
                    processing_time=processing_time,
                )

                # Validate result
                is_valid, validation_errors = self.validator.validate_result(result)

                if not is_valid or not request.auto_approve:
                    result.requires_review = True
                    result.status = EnrichmentStatus.REQUIRES_REVIEW
                    result.review_notes = "; ".join(validation_errors)
                else:
                    result.status = EnrichmentStatus.APPROVED

                results.append(result)
                provider.requests_used += 1

            except Exception as e:
                logger.error(f"Enrichment error with {provider.name}: {e}")

                error_result = EnrichmentResult(
                    request_id=request.request_id,
                    provider=provider_enum,
                    target=request.target,
                    data_type=request.target_type,
                    enriched_data={"error": str(e)},
                    status=EnrichmentStatus.FAILED,
                )
                results.append(error_result)

        request.status = EnrichmentStatus.COMPLETED
        self.results[request.request_id] = results

        return results

    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Calculate confidence score based on data completeness"""
        if not data or "error" in data:
            return 0.0

        # Simple confidence calculation based on data fields
        total_fields = len(data)
        filled_fields = len([v for v in data.values() if v])

        base_confidence = filled_fields / total_fields if total_fields > 0 else 0.0

        # Boost confidence for high-value fields
        high_value_fields = ["name", "email", "phone", "company", "location"]
        high_value_count = sum(1 for field in high_value_fields if data.get(field))

        return min(1.0, base_confidence + (high_value_count * 0.1))

    def _assess_quality(self, data: Dict[str, Any]) -> DataQuality:
        """Assess data quality"""
        confidence = self._calculate_confidence(data)

        if confidence >= 0.8:
            return DataQuality.HIGH
        elif confidence >= 0.6:
            return DataQuality.MEDIUM
        elif confidence > 0:
            return DataQuality.LOW
        else:
            return DataQuality.UNKNOWN


class EnrichmentWorker(QThread):
    """Background worker for enrichment tasks"""

    progress_updated = pyqtSignal(int)
    result_ready = pyqtSignal(object)  # EnrichmentResult
    request_complete = pyqtSignal(str)  # request_id
    error_occurred = pyqtSignal(str)

    def __init__(self, engine: EnrichmentEngine, requests: List[EnrichmentRequest]):
        super().__init__()
        self.engine = engine
        self.requests = requests
        self.is_running = True

    def run(self):
        """Run enrichment tasks"""
        try:
            total_requests = len(self.requests)

            for i, request in enumerate(self.requests):
                if not self.is_running:
                    break

                # Create event loop for async operation
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                try:
                    results = loop.run_until_complete(self.engine.enrich_data(request))

                    for result in results:
                        self.result_ready.emit(result)

                    self.request_complete.emit(request.request_id)

                except Exception as e:
                    self.error_occurred.emit(f"Request {request.request_id} error: {e}")

                finally:
                    loop.close()

                # Update progress
                progress = int((i + 1) / total_requests * 100)
                self.progress_updated.emit(progress)

        except Exception as e:
            self.error_occurred.emit(f"Worker error: {e}")

    def stop(self):
        """Stop enrichment worker"""
        self.is_running = False


class ReviewDialog(QDialog):
    """Dialog for human-in-the-loop result review"""

    def __init__(self, result: EnrichmentResult, parent=None):
        super().__init__(parent)
        self.result = result
        self.setup_ui()

    def setup_ui(self):
        """Setup review dialog UI"""
        self.setWindowTitle(f"Review Enrichment Result - {self.result.target}")
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout(self)

        # Result information
        info_group = QGroupBox("Result Information")
        info_layout = QGridLayout(info_group)

        info_layout.addWidget(QLabel("Target:"), 0, 0)
        info_layout.addWidget(QLabel(self.result.target), 0, 1)

        info_layout.addWidget(QLabel("Provider:"), 1, 0)
        info_layout.addWidget(QLabel(self.result.provider.value), 1, 1)

        info_layout.addWidget(QLabel("Confidence:"), 2, 0)
        info_layout.addWidget(QLabel(f"{self.result.confidence_score:.2f}"), 2, 1)

        info_layout.addWidget(QLabel("Quality:"), 3, 0)
        info_layout.addWidget(QLabel(self.result.quality_score.value), 3, 1)

        info_layout.addWidget(QLabel("Cost:"), 4, 0)
        info_layout.addWidget(QLabel(f"${self.result.cost:.3f}"), 4, 1)

        # Validation issues
        if self.result.review_notes:
            issues_group = QGroupBox("Validation Issues")
            issues_layout = QVBoxLayout(issues_group)

            issues_text = QTextEdit()
            issues_text.setMaximumHeight(100)
            issues_text.setPlainText(self.result.review_notes)
            issues_text.setReadOnly(True)
            issues_layout.addWidget(issues_text)

            layout.addWidget(issues_group)

        # Enriched data
        data_group = QGroupBox("Enriched Data")
        data_layout = QVBoxLayout(data_group)

        self.data_text = QTextEdit()
        self.data_text.setPlainText(json.dumps(self.result.enriched_data, indent=2))
        data_layout.addWidget(self.data_text)

        # Review decision
        decision_group = QGroupBox("Review Decision")
        decision_layout = QVBoxLayout(decision_group)

        self.decision_group = QButtonGroup()

        self.approve_radio = QRadioButton("Approve")
        self.reject_radio = QRadioButton("Reject")
        self.modify_radio = QRadioButton("Approve with Modifications")

        self.decision_group.addButton(self.approve_radio, 0)
        self.decision_group.addButton(self.reject_radio, 1)
        self.decision_group.addButton(self.modify_radio, 2)

        self.approve_radio.setChecked(True)

        decision_layout.addWidget(self.approve_radio)
        decision_layout.addWidget(self.reject_radio)
        decision_layout.addWidget(self.modify_radio)

        # Review notes
        self.review_notes = QTextEdit()
        self.review_notes.setPlaceholderText("Add review notes...")
        self.review_notes.setMaximumHeight(100)
        decision_layout.addWidget(QLabel("Review Notes:"))
        decision_layout.addWidget(self.review_notes)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(info_group)
        layout.addWidget(data_group)
        layout.addWidget(decision_group)
        layout.addWidget(buttons)

        # Connect signals
        self.modify_radio.toggled.connect(self.on_modify_toggled)

    def on_modify_toggled(self, checked: bool):
        """Enable data editing when modify is selected"""
        self.data_text.setReadOnly(not checked)

    def get_review_result(self) -> Tuple[str, str, Dict[str, Any]]:
        """Get review result"""
        decision_id = self.decision_group.checkedId()
        decisions = ["approved", "rejected", "approved"]

        decision = decisions[decision_id] if decision_id >= 0 else "approved"
        notes = self.review_notes.toPlainText()

        # Get modified data if applicable
        modified_data = self.result.enriched_data
        if decision_id == 2:  # Approve with modifications
            try:
                modified_data = json.loads(self.data_text.toPlainText())
            except json.JSONDecodeError:
                modified_data = self.result.enriched_data

        return decision, notes, modified_data


class DataEnrichmentWidget(QWidget):
    """Main data enrichment widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.engine = EnrichmentEngine()
        self.current_worker = None
        self.requests: List[EnrichmentRequest] = []
        self.results: List[EnrichmentResult] = []

        # Load configuration
        self.config = get_config()
        self.load_provider_config()

        self.setup_ui()
        self.connect_signals()

    def load_provider_config(self):
        """Load API provider configuration"""
        api_creds = self.config.get("api_credentials", {})

        # Configure providers with loaded credentials
        for provider_enum, provider in self.engine.providers.items():
            provider_name = provider_enum.value
            if provider_name in api_creds:
                creds = api_creds[provider_name]
                provider.api_key = creds.get("api_key", "")
                provider.enabled = creds.get("enabled", False) and bool(
                    provider.api_key
                )
                provider.rate_limit = creds.get("rate_limit", 1.0)
                provider.monthly_quota = creds.get("monthly_quota", 1000)

                logger.info(f"Configured {provider.name}: enabled={provider.enabled}")
            else:
                logger.warning(f"No configuration found for {provider.name}")

    def setup_ui(self):
        """Setup the enrichment UI"""
        layout = QVBoxLayout(self)

        # Create tab widget
        self.tabs = QTabWidget()

        # Configuration tab
        config_tab = self.create_config_tab()
        self.tabs.addTab(config_tab, "Configuration")

        # Enrichment tab
        enrichment_tab = self.create_enrichment_tab()
        self.tabs.addTab(enrichment_tab, "Enrichment")

        # Results tab
        results_tab = self.create_results_tab()
        self.tabs.addTab(results_tab, "Results")

        # Review tab
        review_tab = self.create_review_tab()
        self.tabs.addTab(review_tab, "Review Queue")

        # Analytics tab
        analytics_tab = self.create_analytics_tab()
        self.tabs.addTab(analytics_tab, "Analytics")

        layout.addWidget(self.tabs)

    def create_config_tab(self) -> QWidget:
        """Create API configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # API Provider Configuration
        providers_group = QGroupBox("API Providers")
        providers_layout = QVBoxLayout(providers_group)

        # Create provider configurations
        self.provider_configs = {}

        for provider_enum, provider in self.engine.providers.items():
            provider_frame = QGroupBox(provider.name)
            provider_layout = QGridLayout(provider_frame)

            # Enable checkbox
            enable_cb = QCheckBox("Enabled")
            enable_cb.setChecked(provider.enabled)
            provider_layout.addWidget(enable_cb, 0, 0, 1, 2)

            # API Key
            provider_layout.addWidget(QLabel("API Key:"), 1, 0)
            api_key_edit = QLineEdit()
            api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
            api_key_edit.setText(provider.api_key)
            provider_layout.addWidget(api_key_edit, 1, 1)

            # Rate limit
            provider_layout.addWidget(QLabel("Rate Limit (s):"), 2, 0)
            rate_limit_spin = QSpinBox()
            rate_limit_spin.setRange(1, 60)
            rate_limit_spin.setValue(int(provider.rate_limit))
            provider_layout.addWidget(rate_limit_spin, 2, 1)

            # Monthly quota
            provider_layout.addWidget(QLabel("Monthly Quota:"), 3, 0)
            quota_spin = QSpinBox()
            quota_spin.setRange(0, 1000000)
            quota_spin.setValue(provider.monthly_quota)
            provider_layout.addWidget(quota_spin, 3, 1)

            # Usage
            usage_label = QLabel(f"Used: {provider.requests_used}")
            provider_layout.addWidget(usage_label, 4, 0, 1, 2)

            # Test button
            test_btn = QPushButton("Test API")
            provider_layout.addWidget(test_btn, 5, 0, 1, 2)

            self.provider_configs[provider_enum] = {
                "frame": provider_frame,
                "enabled": enable_cb,
                "api_key": api_key_edit,
                "rate_limit": rate_limit_spin,
                "quota": quota_spin,
                "usage": usage_label,
                "test_btn": test_btn,
            }

            providers_layout.addWidget(provider_frame)

        # Save configuration button
        save_config_btn = QPushButton("Save Configuration")
        providers_layout.addWidget(save_config_btn)

        layout.addWidget(providers_group)

        return widget

    def create_enrichment_tab(self) -> QWidget:
        """Create enrichment control tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Request input
        input_group = QGroupBox("New Enrichment Request")
        input_layout = QGridLayout(input_group)

        input_layout.addWidget(QLabel("Target:"), 0, 0)
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText(
            "email@example.com, domain.com, 192.168.1.1..."
        )
        input_layout.addWidget(self.target_input, 0, 1)

        input_layout.addWidget(QLabel("Type:"), 1, 0)
        self.target_type_combo = QComboBox()
        self.target_type_combo.addItems(["email", "domain", "ip", "company", "person"])
        input_layout.addWidget(self.target_type_combo, 1, 1)

        input_layout.addWidget(QLabel("Priority:"), 2, 0)
        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(1, 5)
        self.priority_spin.setValue(3)
        input_layout.addWidget(self.priority_spin, 2, 1)

        # Provider selection
        providers_label = QLabel("Providers:")
        input_layout.addWidget(providers_label, 3, 0)

        providers_widget = QWidget()
        providers_layout = QHBoxLayout(providers_widget)

        self.provider_checkboxes = {}
        for provider_enum in self.engine.providers:
            cb = QCheckBox(provider_enum.value.title())
            cb.setChecked(True)
            self.provider_checkboxes[provider_enum] = cb
            providers_layout.addWidget(cb)

        input_layout.addWidget(providers_widget, 3, 1)

        # Auto-approve option
        self.auto_approve_cb = QCheckBox("Auto-approve high confidence results")
        input_layout.addWidget(self.auto_approve_cb, 4, 0, 1, 2)

        # Add request button
        self.add_request_btn = QPushButton("Add Request")
        input_layout.addWidget(self.add_request_btn, 5, 0, 1, 2)

        # Requests queue
        queue_group = QGroupBox("Enrichment Queue")
        queue_layout = QVBoxLayout(queue_group)

        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(6)
        self.requests_table.setHorizontalHeaderLabels(
            ["Target", "Type", "Priority", "Providers", "Status", "Created"]
        )
        self.requests_table.horizontalHeader().setStretchLastSection(True)
        queue_layout.addWidget(self.requests_table)

        # Control buttons
        control_layout = QHBoxLayout()

        self.start_enrichment_btn = QPushButton("Start Enrichment")
        self.stop_enrichment_btn = QPushButton("Stop")
        self.stop_enrichment_btn.setEnabled(False)
        self.clear_queue_btn = QPushButton("Clear Queue")

        control_layout.addWidget(self.start_enrichment_btn)
        control_layout.addWidget(self.stop_enrichment_btn)
        control_layout.addWidget(self.clear_queue_btn)
        control_layout.addStretch()

        queue_layout.addLayout(control_layout)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Ready")

        queue_layout.addWidget(self.progress_bar)
        queue_layout.addWidget(self.progress_label)

        layout.addWidget(input_group)
        layout.addWidget(queue_group)

        return widget

    def create_results_tab(self) -> QWidget:
        """Create results display tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Results filters
        filter_group = QGroupBox("Filter Results")
        filter_layout = QHBoxLayout(filter_group)

        filter_layout.addWidget(QLabel("Provider:"))
        self.provider_filter = QComboBox()
        self.provider_filter.addItem("All Providers")
        for provider in EnrichmentProvider:
            self.provider_filter.addItem(provider.value.title())
        filter_layout.addWidget(self.provider_filter)

        filter_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Statuses")
        for status in EnrichmentStatus:
            self.status_filter.addItem(status.value.title())
        filter_layout.addWidget(self.status_filter)

        filter_layout.addWidget(QLabel("Quality:"))
        self.quality_filter = QComboBox()
        self.quality_filter.addItem("All Qualities")
        for quality in DataQuality:
            self.quality_filter.addItem(quality.value.title())
        filter_layout.addWidget(self.quality_filter)

        self.apply_filter_btn = QPushButton("Apply Filter")
        filter_layout.addWidget(self.apply_filter_btn)
        filter_layout.addStretch()

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels(
            [
                "Target",
                "Provider",
                "Confidence",
                "Quality",
                "Status",
                "Cost",
                "Time",
                "Created",
            ]
        )
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        # Result details
        details_group = QGroupBox("Result Details")
        details_layout = QVBoxLayout(details_group)

        self.result_details = QTextEdit()
        self.result_details.setMaximumHeight(200)
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
        splitter.setSizes([400, 200])

        layout.addWidget(splitter)

        return widget

    def create_review_tab(self) -> QWidget:
        """Create review queue tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Review queue
        queue_group = QGroupBox("Results Requiring Review")
        queue_layout = QVBoxLayout(queue_group)

        self.review_table = QTableWidget()
        self.review_table.setColumnCount(7)
        self.review_table.setHorizontalHeaderLabels(
            [
                "Target",
                "Provider",
                "Confidence",
                "Quality",
                "Issues",
                "Created",
                "Action",
            ]
        )
        self.review_table.horizontalHeader().setStretchLastSection(True)
        queue_layout.addWidget(self.review_table)

        # Review actions
        review_actions = QHBoxLayout()

        self.review_selected_btn = QPushButton("Review Selected")
        self.approve_all_btn = QPushButton("Approve All High Quality")
        self.reject_all_low_btn = QPushButton("Reject All Low Quality")

        review_actions.addWidget(self.review_selected_btn)
        review_actions.addWidget(self.approve_all_btn)
        review_actions.addWidget(self.reject_all_low_btn)
        review_actions.addStretch()

        queue_layout.addLayout(review_actions)

        layout.addWidget(queue_group)

        return widget

    def create_analytics_tab(self) -> QWidget:
        """Create analytics tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QGridLayout(stats_group)

        self.total_requests_label = QLabel("0")
        self.total_results_label = QLabel("0")
        self.total_cost_label = QLabel("$0.00")
        self.avg_confidence_label = QLabel("0.00")
        self.pending_reviews_label = QLabel("0")

        stats_layout.addWidget(QLabel("Total Requests:"), 0, 0)
        stats_layout.addWidget(self.total_requests_label, 0, 1)
        stats_layout.addWidget(QLabel("Total Results:"), 0, 2)
        stats_layout.addWidget(self.total_results_label, 0, 3)

        stats_layout.addWidget(QLabel("Total Cost:"), 1, 0)
        stats_layout.addWidget(self.total_cost_label, 1, 1)
        stats_layout.addWidget(QLabel("Avg Confidence:"), 1, 2)
        stats_layout.addWidget(self.avg_confidence_label, 1, 3)

        stats_layout.addWidget(QLabel("Pending Reviews:"), 2, 0)
        stats_layout.addWidget(self.pending_reviews_label, 2, 1)

        # Provider statistics
        provider_stats_group = QGroupBox("Provider Statistics")
        provider_stats_layout = QVBoxLayout(provider_stats_group)

        self.provider_stats_table = QTableWidget()
        self.provider_stats_table.setColumnCount(5)
        self.provider_stats_table.setHorizontalHeaderLabels(
            ["Provider", "Requests", "Success Rate", "Avg Confidence", "Total Cost"]
        )
        provider_stats_layout.addWidget(self.provider_stats_table)

        layout.addWidget(stats_group)
        layout.addWidget(provider_stats_group)

        return widget

    def connect_signals(self):
        """Connect UI signals"""
        self.add_request_btn.clicked.connect(self.add_request)
        self.start_enrichment_btn.clicked.connect(self.start_enrichment)
        self.stop_enrichment_btn.clicked.connect(self.stop_enrichment)
        self.clear_queue_btn.clicked.connect(self.clear_queue)

        self.results_table.itemSelectionChanged.connect(self.show_result_details)
        self.apply_filter_btn.clicked.connect(self.apply_results_filter)

        self.review_selected_btn.clicked.connect(self.review_selected_result)
        self.approve_all_btn.clicked.connect(self.approve_all_high_quality)
        self.reject_all_low_btn.clicked.connect(self.reject_all_low_quality)

    def add_request(self):
        """Add new enrichment request"""
        target = self.target_input.text().strip()
        if not target:
            return

        # Get selected providers
        selected_providers = []
        for provider_enum, checkbox in self.provider_checkboxes.items():
            if checkbox.isChecked():
                selected_providers.append(provider_enum)

        if not selected_providers:
            return

        request = EnrichmentRequest(
            target=target,
            target_type=self.target_type_combo.currentText(),
            providers=selected_providers,
            priority=self.priority_spin.value(),
            auto_approve=self.auto_approve_cb.isChecked(),
        )

        self.requests.append(request)
        self.update_requests_table()

        # Clear input
        self.target_input.clear()

    def update_requests_table(self):
        """Update requests table"""
        self.requests_table.setRowCount(len(self.requests))

        for i, request in enumerate(self.requests):
            self.requests_table.setItem(i, 0, QTableWidgetItem(request.target))
            self.requests_table.setItem(i, 1, QTableWidgetItem(request.target_type))
            self.requests_table.setItem(i, 2, QTableWidgetItem(str(request.priority)))

            providers_text = ", ".join([p.value for p in request.providers])
            self.requests_table.setItem(i, 3, QTableWidgetItem(providers_text))

            self.requests_table.setItem(i, 4, QTableWidgetItem(request.status.value))
            self.requests_table.setItem(
                i, 5, QTableWidgetItem(request.created_at.strftime("%Y-%m-%d %H:%M"))
            )

    def start_enrichment(self):
        """Start enrichment processing"""
        if not self.requests:
            self.progress_label.setText("No requests in queue")
            return

        pending_requests = [
            r for r in self.requests if r.status == EnrichmentStatus.PENDING
        ]
        if not pending_requests:
            self.progress_label.setText("No pending requests")
            return

        # Start worker
        self.current_worker = EnrichmentWorker(self.engine, pending_requests)
        self.current_worker.progress_updated.connect(self.progress_bar.setValue)
        self.current_worker.result_ready.connect(self.add_result)
        self.current_worker.request_complete.connect(self.request_completed)
        self.current_worker.error_occurred.connect(self.enrichment_error)

        self.start_enrichment_btn.setEnabled(False)
        self.stop_enrichment_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Enrichment started...")

        self.current_worker.start()

    def stop_enrichment(self):
        """Stop enrichment processing"""
        if self.current_worker:
            self.current_worker.stop()
            self.current_worker = None

        self.start_enrichment_btn.setEnabled(True)
        self.stop_enrichment_btn.setEnabled(False)
        self.progress_label.setText("Enrichment stopped")

    def clear_queue(self):
        """Clear request queue"""
        self.requests.clear()
        self.update_requests_table()

    def add_result(self, result: EnrichmentResult):
        """Add enrichment result"""
        self.results.append(result)
        self.update_results_table()
        self.update_review_table()
        self.update_analytics()

        # Update progress label
        self.progress_label.setText(
            f"Result from {result.provider.value} for {result.target}"
        )

    def request_completed(self, request_id: str):
        """Handle request completion"""
        # Update request status in table
        for i, request in enumerate(self.requests):
            if request.request_id == request_id:
                self.requests_table.setItem(
                    i, 4, QTableWidgetItem(request.status.value)
                )
                break

    def enrichment_error(self, error_message: str):
        """Handle enrichment error"""
        self.progress_label.setText(f"Error: {error_message}")

    def update_results_table(self):
        """Update results table"""
        self.results_table.setRowCount(len(self.results))

        for i, result in enumerate(self.results):
            self.results_table.setItem(i, 0, QTableWidgetItem(result.target))
            self.results_table.setItem(i, 1, QTableWidgetItem(result.provider.value))
            self.results_table.setItem(
                i, 2, QTableWidgetItem(f"{result.confidence_score:.2f}")
            )
            self.results_table.setItem(
                i, 3, QTableWidgetItem(result.quality_score.value)
            )
            self.results_table.setItem(i, 4, QTableWidgetItem(result.status.value))
            self.results_table.setItem(i, 5, QTableWidgetItem(f"${result.cost:.3f}"))
            self.results_table.setItem(
                i, 6, QTableWidgetItem(f"{result.processing_time:.2f}s")
            )
            self.results_table.setItem(
                i, 7, QTableWidgetItem(result.created_at.strftime("%Y-%m-%d %H:%M"))
            )

            # Color-code by status
            status_colors = {
                EnrichmentStatus.APPROVED: QColor(0, 255, 0, 50),
                EnrichmentStatus.REQUIRES_REVIEW: QColor(255, 255, 0, 50),
                EnrichmentStatus.REJECTED: QColor(255, 0, 0, 50),
                EnrichmentStatus.FAILED: QColor(128, 128, 128, 50),
            }

            color = status_colors.get(result.status, QColor(255, 255, 255, 0))
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
Provider: {result.provider.value}
Data Type: {result.data_type}
Confidence Score: {result.confidence_score:.2f}
Quality Score: {result.quality_score.value}
Status: {result.status.value}
Cost: ${result.cost:.3f}
Processing Time: {result.processing_time:.2f}s
Requires Review: {'Yes' if result.requires_review else 'No'}
Review Notes: {result.review_notes}

Enriched Data:
{json.dumps(result.enriched_data, indent=2)}
            """.strip()

            self.result_details.setText(details)

    def update_review_table(self):
        """Update review queue table"""
        review_results = [
            r
            for r in self.results
            if r.requires_review and r.status == EnrichmentStatus.REQUIRES_REVIEW
        ]

        self.review_table.setRowCount(len(review_results))

        for i, result in enumerate(review_results):
            self.review_table.setItem(i, 0, QTableWidgetItem(result.target))
            self.review_table.setItem(i, 1, QTableWidgetItem(result.provider.value))
            self.review_table.setItem(
                i, 2, QTableWidgetItem(f"{result.confidence_score:.2f}")
            )
            self.review_table.setItem(
                i, 3, QTableWidgetItem(result.quality_score.value)
            )
            self.review_table.setItem(
                i, 4, QTableWidgetItem(result.review_notes[:50] + "...")
            )
            self.review_table.setItem(
                i, 5, QTableWidgetItem(result.created_at.strftime("%Y-%m-%d %H:%M"))
            )

            # Add review button
            review_btn = QPushButton("Review")
            review_btn.clicked.connect(lambda checked, r=result: self.review_result(r))
            self.review_table.setCellWidget(i, 6, review_btn)

    def review_selected_result(self):
        """Review selected result"""
        current_row = self.review_table.currentRow()
        if current_row >= 0:
            review_results = [
                r
                for r in self.results
                if r.requires_review and r.status == EnrichmentStatus.REQUIRES_REVIEW
            ]
            if current_row < len(review_results):
                self.review_result(review_results[current_row])

    def review_result(self, result: EnrichmentResult):
        """Review individual result"""
        dialog = ReviewDialog(result, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            decision, notes, modified_data = dialog.get_review_result()

            result.status = (
                EnrichmentStatus.APPROVED
                if decision == "approved"
                else EnrichmentStatus.REJECTED
            )
            result.review_notes = notes
            result.reviewed_at = datetime.now()
            result.reviewed_by = "User"  # Could be current user

            if decision == "approved":
                result.enriched_data = modified_data

            self.update_results_table()
            self.update_review_table()
            self.update_analytics()

    def approve_all_high_quality(self):
        """Auto-approve all high quality results"""
        for result in self.results:
            if (
                result.requires_review
                and result.status == EnrichmentStatus.REQUIRES_REVIEW
                and result.quality_score == DataQuality.HIGH
                and result.confidence_score >= 0.8
            ):

                result.status = EnrichmentStatus.APPROVED
                result.reviewed_at = datetime.now()
                result.reviewed_by = "Auto"

        self.update_results_table()
        self.update_review_table()
        self.update_analytics()

    def reject_all_low_quality(self):
        """Auto-reject all low quality results"""
        for result in self.results:
            if (
                result.requires_review
                and result.status == EnrichmentStatus.REQUIRES_REVIEW
                and result.quality_score == DataQuality.LOW
            ):

                result.status = EnrichmentStatus.REJECTED
                result.reviewed_at = datetime.now()
                result.reviewed_by = "Auto"

        self.update_results_table()
        self.update_review_table()
        self.update_analytics()

    def apply_results_filter(self):
        """Apply results filter"""
        # Implementation would filter results table based on selected criteria
        pass

    def update_analytics(self):
        """Update analytics display"""
        total_requests = len(self.requests)
        total_results = len(self.results)
        total_cost = sum(r.cost for r in self.results)
        avg_confidence = (
            sum(r.confidence_score for r in self.results) / total_results
            if total_results > 0
            else 0
        )
        pending_reviews = len(
            [
                r
                for r in self.results
                if r.requires_review and r.status == EnrichmentStatus.REQUIRES_REVIEW
            ]
        )

        self.total_requests_label.setText(str(total_requests))
        self.total_results_label.setText(str(total_results))
        self.total_cost_label.setText(f"${total_cost:.3f}")
        self.avg_confidence_label.setText(f"{avg_confidence:.2f}")
        self.pending_reviews_label.setText(str(pending_reviews))

        # Update provider statistics
        provider_stats = {}
        for result in self.results:
            provider = result.provider.value
            if provider not in provider_stats:
                provider_stats[provider] = {
                    "requests": 0,
                    "successes": 0,
                    "total_confidence": 0,
                    "total_cost": 0,
                }

            stats = provider_stats[provider]
            stats["requests"] += 1
            stats["total_confidence"] += result.confidence_score
            stats["total_cost"] += result.cost

            if result.status in [EnrichmentStatus.APPROVED, EnrichmentStatus.COMPLETED]:
                stats["successes"] += 1

        self.provider_stats_table.setRowCount(len(provider_stats))

        for i, (provider, stats) in enumerate(provider_stats.items()):
            success_rate = (
                stats["successes"] / stats["requests"] * 100
                if stats["requests"] > 0
                else 0
            )
            avg_confidence = (
                stats["total_confidence"] / stats["requests"]
                if stats["requests"] > 0
                else 0
            )

            self.provider_stats_table.setItem(i, 0, QTableWidgetItem(provider))
            self.provider_stats_table.setItem(
                i, 1, QTableWidgetItem(str(stats["requests"]))
            )
            self.provider_stats_table.setItem(
                i, 2, QTableWidgetItem(f"{success_rate:.1f}%")
            )
            self.provider_stats_table.setItem(
                i, 3, QTableWidgetItem(f"{avg_confidence:.2f}")
            )
            self.provider_stats_table.setItem(
                i, 4, QTableWidgetItem(f"${stats['total_cost']:.3f}")
            )
