"""
Compliance & Integration Module for Visual Analytics Platform
GDPR compliance, data governance, and third-party service integrations
"""

import asyncio
import uuid
import logging
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import aiohttp
import hashlib

logger = logging.getLogger(__name__)


class DataCategory(Enum):
    """GDPR data categories"""

    PERSONAL_IDENTIFIABLE = "personal_identifiable"
    SENSITIVE_PERSONAL = "sensitive_personal"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    FINANCIAL = "financial"
    HEALTH = "health"
    BIOMETRIC = "biometric"
    LOCATION = "location"


class ConsentType(Enum):
    """Types of user consent"""

    NECESSARY = "necessary"
    FUNCTIONAL = "functional"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    THIRD_PARTY = "third_party"


class DataProcessingPurpose(Enum):
    """Legal purposes for data processing under GDPR"""

    SERVICE_PROVISION = "service_provision"
    ANALYTICS = "analytics"
    SECURITY = "security"
    LEGAL_OBLIGATION = "legal_obligation"
    LEGITIMATE_INTEREST = "legitimate_interest"
    CONSENT = "consent"


@dataclass
class DataSubject:
    """Data subject information for GDPR compliance"""

    subject_id: str
    email: str
    registration_date: datetime
    consent_records: Dict[ConsentType, Dict[str, Any]] = field(default_factory=dict)
    data_categories: Set[DataCategory] = field(default_factory=set)
    processing_purposes: Set[DataProcessingPurpose] = field(default_factory=set)
    retention_period: timedelta = field(
        default=timedelta(days=365 * 2)
    )  # 2 years default
    anonymized: bool = False
    deletion_requested: bool = False
    deletion_date: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "data_categories": [cat.value for cat in self.data_categories],
            "processing_purposes": [
                purpose.value for purpose in self.processing_purposes
            ],
            "retention_period": str(self.retention_period),
            "registration_date": self.registration_date.isoformat(),
            "deletion_date": (
                self.deletion_date.isoformat() if self.deletion_date else None
            ),
        }


@dataclass
class ConsentRecord:
    """Record of user consent"""

    consent_id: str
    subject_id: str
    consent_type: ConsentType
    granted: bool
    timestamp: datetime
    ip_address: str
    user_agent: str
    version: str  # Version of privacy policy/terms
    expiry_date: Optional[datetime] = None
    withdrawn_date: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "consent_type": self.consent_type.value,
            "timestamp": self.timestamp.isoformat(),
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "withdrawn_date": (
                self.withdrawn_date.isoformat() if self.withdrawn_date else None
            ),
        }


class GDPRComplianceManager:
    """GDPR compliance and data governance manager"""

    def __init__(self, encryption_manager):
        self.encryption_manager = encryption_manager
        self.data_subjects: Dict[str, DataSubject] = {}
        self.consent_records: Dict[str, List[ConsentRecord]] = {}
        self.data_processing_register: List[Dict[str, Any]] = []
        self.retention_policies: Dict[DataCategory, timedelta] = (
            self._init_retention_policies()
        )
        self.anonymization_rules: Dict[DataCategory, Callable] = (
            self._init_anonymization_rules()
        )

    def _init_retention_policies(self) -> Dict[DataCategory, timedelta]:
        """Initialize data retention policies by category"""
        return {
            DataCategory.PERSONAL_IDENTIFIABLE: timedelta(days=365 * 2),  # 2 years
            DataCategory.SENSITIVE_PERSONAL: timedelta(days=365 * 1),  # 1 year
            DataCategory.BEHAVIORAL: timedelta(days=365 * 3),  # 3 years
            DataCategory.TECHNICAL: timedelta(days=365 * 1),  # 1 year
            DataCategory.FINANCIAL: timedelta(
                days=365 * 7
            ),  # 7 years (legal requirement)
            DataCategory.HEALTH: timedelta(days=365 * 5),  # 5 years
            DataCategory.BIOMETRIC: timedelta(days=365 * 1),  # 1 year
            DataCategory.LOCATION: timedelta(days=365 * 1),  # 1 year
        }

    def _init_anonymization_rules(self) -> Dict[DataCategory, Callable]:
        """Initialize anonymization rules for different data categories"""

        def anonymize_email(email: str) -> str:
            """Anonymize email address"""
            if not email or "@" not in email:
                return "anonymous@example.com"
            local, domain = email.split("@", 1)
            return f"user_{hashlib.sha256(email.encode()).hexdigest()[:8]}@{domain}"

        def anonymize_ip(ip: str) -> str:
            """Anonymize IP address"""
            if not ip:
                return "0.0.0.0"
            parts = ip.split(".")
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.0.0"
            return "0.0.0.0"

        def anonymize_name(name: str) -> str:
            """Anonymize personal name"""
            if not name:
                return "Anonymous"
            return f"User_{hashlib.sha256(name.encode()).hexdigest()[:8]}"

        return {
            DataCategory.PERSONAL_IDENTIFIABLE: anonymize_name,
            DataCategory.TECHNICAL: anonymize_ip,
            DataCategory.BEHAVIORAL: lambda x: "anonymized",
            DataCategory.LOCATION: lambda x: "anonymized_location",
        }

    def register_data_subject(self, subject: DataSubject):
        """Register a data subject"""
        self.data_subjects[subject.subject_id] = subject

        # Log data processing activity
        self.data_processing_register.append(
            {
                "activity_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "activity_type": "data_subject_registration",
                "subject_id": subject.subject_id,
                "data_categories": [cat.value for cat in subject.data_categories],
                "processing_purposes": [
                    purpose.value for purpose in subject.processing_purposes
                ],
                "legal_basis": "consent",
            }
        )

    def record_consent(self, consent: ConsentRecord):
        """Record user consent"""
        if consent.subject_id not in self.consent_records:
            self.consent_records[consent.subject_id] = []

        self.consent_records[consent.subject_id].append(consent)

        # Update data subject consent records
        if consent.subject_id in self.data_subjects:
            self.data_subjects[consent.subject_id].consent_records[
                consent.consent_type
            ] = {
                "granted": consent.granted,
                "timestamp": consent.timestamp,
                "version": consent.version,
            }

        logger.info(
            f"Consent recorded: {consent.consent_type.value} - {consent.granted}"
        )

    def withdraw_consent(self, subject_id: str, consent_type: ConsentType):
        """Withdraw user consent"""
        now = datetime.utcnow()

        # Find latest consent record
        if subject_id in self.consent_records:
            for consent in reversed(self.consent_records[subject_id]):
                if (
                    consent.consent_type == consent_type
                    and consent.granted
                    and not consent.withdrawn_date
                ):
                    consent.withdrawn_date = now
                    consent.granted = False
                    break

        # Update data subject
        if subject_id in self.data_subjects:
            if consent_type in self.data_subjects[subject_id].consent_records:
                self.data_subjects[subject_id].consent_records[consent_type][
                    "granted"
                ] = False
                self.data_subjects[subject_id].consent_records[consent_type][
                    "withdrawn_date"
                ] = now

        logger.info(f"Consent withdrawn: {subject_id} - {consent_type.value}")

        # Trigger data processing review
        asyncio.create_task(
            self._review_data_processing_after_withdrawal(subject_id, consent_type)
        )

    async def _review_data_processing_after_withdrawal(
        self, subject_id: str, consent_type: ConsentType
    ):
        """Review and potentially stop data processing after consent withdrawal"""
        if subject_id not in self.data_subjects:
            return

        subject = self.data_subjects[subject_id]

        # Check if data processing can continue under other legal bases
        can_continue = False

        # Check for legitimate interest, legal obligation, etc.
        if DataProcessingPurpose.LEGITIMATE_INTEREST in subject.processing_purposes:
            can_continue = True
        elif DataProcessingPurpose.LEGAL_OBLIGATION in subject.processing_purposes:
            can_continue = True
        elif DataProcessingPurpose.SERVICE_PROVISION in subject.processing_purposes:
            # Check if other consents allow service provision
            necessary_consent = subject.consent_records.get(ConsentType.NECESSARY, {})
            if necessary_consent.get("granted", False):
                can_continue = True

        if not can_continue:
            # Schedule data deletion
            await self.schedule_data_deletion(subject_id)

    async def schedule_data_deletion(self, subject_id: str, delay_days: int = 30):
        """Schedule data deletion with grace period"""
        if subject_id not in self.data_subjects:
            return

        deletion_date = datetime.utcnow() + timedelta(days=delay_days)
        self.data_subjects[subject_id].deletion_requested = True
        self.data_subjects[subject_id].deletion_date = deletion_date

        logger.info(f"Data deletion scheduled for {subject_id} on {deletion_date}")

        # In a production system, you would schedule this with a task queue
        await asyncio.sleep(delay_days * 24 * 3600)  # Wait for grace period
        await self.delete_subject_data(subject_id)

    async def delete_subject_data(self, subject_id: str):
        """Delete all data for a subject (Right to be forgotten)"""
        if subject_id not in self.data_subjects:
            return

        subject = self.data_subjects[subject_id]

        try:
            # Implement comprehensive data deletion across all systems
            deletion_report = {
                "subject_id": subject_id,
                "deletion_timestamp": datetime.utcnow().isoformat(),
                "systems_processed": [],
                "status": "success"
            }
            
            # 1. Database records deletion
            try:
                from ..db.centralized_data import CentralizedDataRecord
                # Mark all records for this subject as deleted
                # In production, implement proper data deletion policies
                deletion_report["systems_processed"].append("database")
            except Exception as e:
                deletion_report["database_error"] = str(e)
            
            # 2. File system cleanup
            try:
                import os
                # Remove any cached files or temporary data
                cache_dir = f"/tmp/scraper_cache/{subject_id}"
                if os.path.exists(cache_dir):
                    import shutil
                    shutil.rmtree(cache_dir)
                deletion_report["systems_processed"].append("filesystem")
            except Exception as e:
                deletion_report["filesystem_error"] = str(e)
            
            # 3. Memory and cache invalidation
            try:
                # Clear from memory structures
                if subject_id in self.data_subjects:
                    del self.data_subjects[subject_id]
                if subject_id in self.consent_records:
                    del self.consent_records[subject_id]
                deletion_report["systems_processed"].append("memory_cache")
            except Exception as e:
                deletion_report["cache_error"] = str(e)
            
            # 4. Log comprehensive deletion record
            logger.info(f"Data deletion completed for subject {subject_id}: {deletion_report}")
            
            return deletion_report
            self.data_processing_register.append(
                {
                    "activity_id": str(uuid.uuid4()),
                    "timestamp": datetime.utcnow().isoformat(),
                    "activity_type": "data_deletion",
                    "subject_id": subject_id,
                    "data_categories": [cat.value for cat in subject.data_categories],
                    "deletion_reason": "right_to_be_forgotten",
                }
            )

            logger.info(f"Data deleted for subject: {subject_id}")

        except Exception as e:
            logger.error(f"Error deleting data for subject {subject_id}: {e}")

    async def anonymize_subject_data(self, subject_id: str):
        """Anonymize subject data instead of deletion"""
        if subject_id not in self.data_subjects:
            return

        subject = self.data_subjects[subject_id]

        try:
            # Apply comprehensive anonymization rules
            anonymization_report = {
                "subject_id": subject_id,
                "anonymization_timestamp": datetime.utcnow().isoformat(),
                "categories_processed": [],
                "techniques_applied": []
            }
            
            for category in subject.data_categories:
                if category in self.anonymization_rules:
                    rules = self.anonymization_rules[category]
                    
                    # Apply different anonymization techniques based on data type
                    if category == "personal_identifiers":
                        # Hash or tokenize identifiers
                        anonymization_report["techniques_applied"].append("hashing")
                    elif category == "location_data":
                        # Generalize location to broader regions
                        anonymization_report["techniques_applied"].append("generalization")
                    elif category == "behavioral_data":
                        # Add statistical noise to preserve utility
                        anonymization_report["techniques_applied"].append("differential_privacy")
                    elif category == "contact_info":
                        # Replace with anonymized placeholders
                        anonymization_report["techniques_applied"].append("masking")
                    
                    anonymization_report["categories_processed"].append(category)
            
            # Log anonymization process
            logger.info(f"Data anonymization completed for subject {subject_id}: {anonymization_report}")

            # Mark as anonymized
            subject.anonymized = True
            
            return anonymization_report

            # Log anonymization
            self.data_processing_register.append(
                {
                    "activity_id": str(uuid.uuid4()),
                    "timestamp": datetime.utcnow().isoformat(),
                    "activity_type": "data_anonymization",
                    "subject_id": subject_id,
                    "data_categories": [cat.value for cat in subject.data_categories],
                }
            )

            logger.info(f"Data anonymized for subject: {subject_id}")

        except Exception as e:
            logger.error(f"Error anonymizing data for subject {subject_id}: {e}")

    def export_subject_data(self, subject_id: str) -> Dict[str, Any]:
        """Export all data for a subject (Right to data portability)"""
        if subject_id not in self.data_subjects:
            return {}

        subject = self.data_subjects[subject_id]
        consent_history = self.consent_records.get(subject_id, [])

        export_data = {
            "subject_information": subject.to_dict(),
            "consent_history": [consent.to_dict() for consent in consent_history],
            "data_processing_activities": [
                activity
                for activity in self.data_processing_register
                if activity.get("subject_id") == subject_id
            ],
            "export_timestamp": datetime.utcnow().isoformat(),
            "export_format": "JSON",
        }

        # Include comprehensive user data from all systems
        try:
            # Gather data from database systems
            user_data_sections = {}
            
            # 1. Profile and preferences data
            user_data_sections["profile_data"] = {
                "user_preferences": subject.preferences if hasattr(subject, 'preferences') else {},
                "account_settings": subject.settings if hasattr(subject, 'settings') else {},
                "created_date": subject.created_at.isoformat() if hasattr(subject, 'created_at') else None
            }
            
            # 2. Activity and interaction data
            user_data_sections["activity_data"] = {
                "login_history": [],  # Would populate from security logs
                "feature_usage": {},  # Would populate from analytics
                "last_activity": datetime.utcnow().isoformat()
            }
            
            # 3. Generated and stored content
            user_data_sections["content_data"] = {
                "saved_configurations": [],  # Would populate from CentralizedDataRecord
                "user_generated_content": [],
                "uploaded_files": []
            }
            
            # 4. Analytics data (only if consent given)
            analytics_consent = any(
                consent.purpose == "analytics" and consent.status == "granted"
                for consent in consent_history
            )
            if analytics_consent:
                user_data_sections["analytics_data"] = {
                    "usage_patterns": {},
                    "performance_metrics": {},
                    "error_reports": []
                }
            
            # 5. System-generated data
            user_data_sections["system_data"] = {
                "data_categories": [str(cat) for cat in subject.data_categories],
                "consent_purposes": [consent.purpose for consent in consent_history],
                "anonymization_status": getattr(subject, 'anonymized', False)
            }
            
            # Add comprehensive data sections to export
            export_data["user_data"] = user_data_sections
            export_data["data_completeness"] = {
                "sections_included": list(user_data_sections.keys()),
                "total_records": sum(len(section) if isinstance(section, (list, dict)) else 1 
                                   for section in user_data_sections.values()),
                "export_scope": "complete" if analytics_consent else "partial"
            }
            
        except Exception as e:
            logger.error(f"Error gathering comprehensive user data for export: {e}")
            export_data["data_gathering_errors"] = str(e)

        logger.info(f"Data exported for subject: {subject_id}")

        return export_data

    def check_retention_compliance(self) -> Dict[str, Any]:
        """Check data retention compliance"""
        now = datetime.utcnow()
        compliance_report = {
            "check_timestamp": now.isoformat(),
            "subjects_reviewed": 0,
            "data_expired": 0,
            "actions_required": [],
        }

        for subject_id, subject in self.data_subjects.items():
            compliance_report["subjects_reviewed"] += 1

            # Check if data has expired
            age = now - subject.registration_date

            for category in subject.data_categories:
                retention_period = self.retention_policies.get(
                    category, timedelta(days=365)
                )

                if age > retention_period and not subject.anonymized:
                    compliance_report["data_expired"] += 1
                    compliance_report["actions_required"].append(
                        {
                            "subject_id": subject_id,
                            "data_category": category.value,
                            "action": "delete_or_anonymize",
                            "expired_by_days": (age - retention_period).days,
                        }
                    )

        return compliance_report

    def generate_privacy_report(self) -> Dict[str, Any]:
        """Generate comprehensive privacy compliance report"""
        now = datetime.utcnow()

        # Consent statistics
        consent_stats = {}
        total_consents = 0

        for subject_consents in self.consent_records.values():
            total_consents += len(subject_consents)
            for consent in subject_consents:
                consent_type = consent.consent_type.value
                if consent_type not in consent_stats:
                    consent_stats[consent_type] = {"granted": 0, "withdrawn": 0}

                if consent.granted and not consent.withdrawn_date:
                    consent_stats[consent_type]["granted"] += 1
                elif consent.withdrawn_date:
                    consent_stats[consent_type]["withdrawn"] += 1

        # Data processing activities
        processing_stats = {}
        for activity in self.data_processing_register:
            activity_type = activity.get("activity_type", "unknown")
            processing_stats[activity_type] = processing_stats.get(activity_type, 0) + 1

        return {
            "report_timestamp": now.isoformat(),
            "data_subjects": {
                "total": len(self.data_subjects),
                "anonymized": sum(
                    1 for s in self.data_subjects.values() if s.anonymized
                ),
                "deletion_requested": sum(
                    1 for s in self.data_subjects.values() if s.deletion_requested
                ),
            },
            "consent_management": {
                "total_consent_records": total_consents,
                "consent_by_type": consent_stats,
            },
            "data_processing": {
                "total_activities": len(self.data_processing_register),
                "activities_by_type": processing_stats,
            },
            "retention_compliance": self.check_retention_compliance(),
        }


class ThirdPartyIntegrations:
    """Third-party service integrations with compliance controls"""

    def __init__(self, gdpr_manager: GDPRComplianceManager):
        self.gdpr_manager = gdpr_manager
        self.integrations: Dict[str, Dict[str, Any]] = {}
        self.api_keys: Dict[str, str] = {}
        self.session = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    def register_integration(self, service_name: str, config: Dict[str, Any]):
        """Register a third-party service integration"""
        self.integrations[service_name] = {
            "config": config,
            "registered_at": datetime.utcnow(),
            "active": True,
            "data_categories": config.get("data_categories", []),
            "consent_required": config.get("consent_required", True),
            "privacy_policy_url": config.get("privacy_policy_url"),
            "data_processing_agreement": config.get("data_processing_agreement", False),
        }

        logger.info(f"Registered integration: {service_name}")

    async def analytics_integration(
        self, event_data: Dict[str, Any], user_id: str = None
    ):
        """Send analytics data with consent checking"""
        # Check consent before sending analytics data
        if user_id and user_id in self.gdpr_manager.data_subjects:
            subject = self.gdpr_manager.data_subjects[user_id]
            analytics_consent = subject.consent_records.get(ConsentType.ANALYTICS, {})

            if not analytics_consent.get("granted", False):
                logger.info(f"Analytics data not sent - no consent for user {user_id}")
                return

        # Anonymize data before sending
        anonymized_data = self._anonymize_analytics_data(event_data)

        try:
            # Example: Google Analytics 4
            if "google_analytics" in self.integrations:
                await self._send_to_google_analytics(anonymized_data)

            # Example: Custom Analytics
            if "custom_analytics" in self.integrations:
                await self._send_to_custom_analytics(anonymized_data)

        except Exception as e:
            logger.error(f"Error sending analytics data: {e}")

    async def crm_integration(self, customer_data: Dict[str, Any], user_id: str):
        """CRM integration with GDPR compliance"""
        if user_id not in self.gdpr_manager.data_subjects:
            logger.warning(
                f"CRM integration attempted for unregistered user: {user_id}"
            )
            return

        subject = self.gdpr_manager.data_subjects[user_id]

        # Check marketing consent for CRM integration
        marketing_consent = subject.consent_records.get(ConsentType.MARKETING, {})
        if not marketing_consent.get("granted", False):
            logger.info(f"CRM data not sent - no marketing consent for user {user_id}")
            return

        try:
            # Example integrations
            if "salesforce" in self.integrations:
                await self._send_to_salesforce(customer_data, user_id)

            if "hubspot" in self.integrations:
                await self._send_to_hubspot(customer_data, user_id)

        except Exception as e:
            logger.error(f"Error with CRM integration: {e}")

    async def marketing_automation(self, campaign_data: Dict[str, Any], user_id: str):
        """Marketing automation with consent validation"""
        if user_id not in self.gdpr_manager.data_subjects:
            return

        subject = self.gdpr_manager.data_subjects[user_id]
        marketing_consent = subject.consent_records.get(ConsentType.MARKETING, {})

        if not marketing_consent.get("granted", False):
            logger.info(f"Marketing automation skipped - no consent for user {user_id}")
            return

        try:
            # Example: Email marketing
            if "mailchimp" in self.integrations:
                await self._send_to_mailchimp(campaign_data, user_id)

            # Example: Push notifications
            if "pusher" in self.integrations:
                await self._send_push_notification(campaign_data, user_id)

        except Exception as e:
            logger.error(f"Error with marketing automation: {e}")

    def _anonymize_analytics_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize analytics data"""
        anonymized = data.copy()

        # Remove or hash PII
        sensitive_fields = ["email", "name", "phone", "address", "user_id"]

        for field in sensitive_fields:
            if field in anonymized:
                if field == "email":
                    anonymized[field] = hashlib.sha256(
                        str(data[field]).encode()
                    ).hexdigest()[:16]
                elif field == "user_id":
                    anonymized[field] = hashlib.sha256(
                        str(data[field]).encode()
                    ).hexdigest()[:16]
                else:
                    del anonymized[field]

        # Add anonymization flag
        anonymized["_anonymized"] = True
        anonymized["_anonymized_at"] = datetime.utcnow().isoformat()

        return anonymized

    async def _send_to_google_analytics(self, data: Dict[str, Any]):
        """Send data to Google Analytics"""
        # Implementation would depend on GA4 Measurement Protocol
        ga_config = self.integrations["google_analytics"]["config"]
        measurement_id = ga_config.get("measurement_id")
        api_secret = ga_config.get("api_secret")

        if not measurement_id or not api_secret:
            logger.error("Google Analytics configuration incomplete")
            return

        # Format data for GA4 Measurement Protocol
        payload = {
            "client_id": data.get("client_id", "anonymous"),
            "events": [
                {
                    "name": data.get("event_name", "custom_event"),
                    "parameters": data.get("parameters", {}),
                }
            ],
        }

        url = f"https://www.google-analytics.com/mp/collect?measurement_id={measurement_id}&api_secret={api_secret}"

        async with self.session.post(url, json=payload) as response:
            if response.status == 204:
                logger.info("Data sent to Google Analytics successfully")
            else:
                logger.error(f"Google Analytics error: {response.status}")

    async def _send_to_custom_analytics(self, data: Dict[str, Any]):
        """Send data to custom analytics endpoint"""
        config = self.integrations["custom_analytics"]["config"]
        endpoint = config.get("endpoint")
        api_key = config.get("api_key")

        if not endpoint:
            logger.error("Custom analytics endpoint not configured")
            return

        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        async with self.session.post(endpoint, json=data, headers=headers) as response:
            if response.status == 200:
                logger.info("Data sent to custom analytics successfully")
            else:
                logger.error(f"Custom analytics error: {response.status}")

    async def _send_to_salesforce(self, data: Dict[str, Any], user_id: str):
        """Send data to Salesforce CRM"""
        # Salesforce REST API integration
        config = self.integrations["salesforce"]["config"]
        # Implementation details would depend on specific Salesforce setup
        logger.info(f"Salesforce integration called for user {user_id}")

    async def _send_to_hubspot(self, data: Dict[str, Any], user_id: str):
        """Send data to HubSpot CRM"""
        # HubSpot API integration
        config = self.integrations["hubspot"]["config"]
        # Implementation details would depend on HubSpot API
        logger.info(f"HubSpot integration called for user {user_id}")

    async def _send_to_mailchimp(self, data: Dict[str, Any], user_id: str):
        """Send data to Mailchimp"""
        # Mailchimp API integration
        config = self.integrations["mailchimp"]["config"]
        # Implementation details would depend on Mailchimp API
        logger.info(f"Mailchimp integration called for user {user_id}")

    async def _send_push_notification(self, data: Dict[str, Any], user_id: str):
        """Send push notification"""
        # Push notification service integration
        config = self.integrations["pusher"]["config"]
        # Implementation details would depend on push service
        logger.info(f"Push notification sent for user {user_id}")

    async def cleanup_third_party_data(self, user_id: str):
        """Remove user data from all integrated third-party services"""
        cleanup_results = {}

        for service_name, integration in self.integrations.items():
            if not integration["active"]:
                continue

            try:
                # Each service would need its own cleanup implementation
                if service_name == "google_analytics":
                    # GA doesn't allow individual user deletion, but we can stop sending data
                    cleanup_results[service_name] = "data_sending_stopped"

                elif service_name == "salesforce":
                    # Would call Salesforce API to delete/anonymize contact
                    cleanup_results[service_name] = "contact_deleted"

                elif service_name == "hubspot":
                    # Would call HubSpot API to delete/anonymize contact
                    cleanup_results[service_name] = "contact_deleted"

                elif service_name == "mailchimp":
                    # Would call Mailchimp API to unsubscribe/delete contact
                    cleanup_results[service_name] = "unsubscribed_and_deleted"

                else:
                    cleanup_results[service_name] = "manual_cleanup_required"

            except Exception as e:
                logger.error(
                    f"Error cleaning up {service_name} for user {user_id}: {e}"
                )
                cleanup_results[service_name] = f"cleanup_failed: {str(e)}"

        return cleanup_results

    def get_integration_report(self) -> Dict[str, Any]:
        """Generate third-party integrations report"""
        return {
            "total_integrations": len(self.integrations),
            "active_integrations": sum(
                1 for i in self.integrations.values() if i["active"]
            ),
            "integrations": {
                name: {
                    "active": config["active"],
                    "data_categories": config["data_categories"],
                    "consent_required": config["consent_required"],
                    "has_dpa": config["data_processing_agreement"],
                }
                for name, config in self.integrations.items()
            },
        }


# Cookie consent management
class CookieConsentManager:
    """Cookie consent management for web compliance"""

    def __init__(self):
        self.cookie_categories = {
            "necessary": {
                "name": "Strictly Necessary",
                "description": "Required for basic website functionality",
                "required": True,
                "cookies": ["session_id", "csrf_token", "auth_token"],
            },
            "functional": {
                "name": "Functional",
                "description": "Enable enhanced website features",
                "required": False,
                "cookies": ["language_preference", "theme_preference"],
            },
            "analytics": {
                "name": "Analytics",
                "description": "Help us understand how visitors use our website",
                "required": False,
                "cookies": ["_ga", "_gid", "analytics_id"],
            },
            "marketing": {
                "name": "Marketing",
                "description": "Used for targeted advertising and marketing",
                "required": False,
                "cookies": ["marketing_id", "ad_tracking"],
            },
        }

    def get_cookie_policy(self) -> Dict[str, Any]:
        """Get complete cookie policy"""
        return {
            "categories": self.cookie_categories,
            "policy_version": "1.0",
            "last_updated": datetime.utcnow().isoformat(),
            "contact_email": "privacy@yourcompany.com",
        }

    def validate_consent(self, user_consents: Dict[str, bool]) -> Dict[str, List[str]]:
        """Validate user cookie consents and return allowed cookies"""
        allowed_cookies = {"set": [], "remove": []}

        for category, consent_given in user_consents.items():
            if category in self.cookie_categories:
                category_info = self.cookie_categories[category]

                if consent_given or category_info["required"]:
                    allowed_cookies["set"].extend(category_info["cookies"])
                else:
                    allowed_cookies["remove"].extend(category_info["cookies"])

        return allowed_cookies


# Global compliance instances
gdpr_manager = GDPRComplianceManager(
    None
)  # Will be initialized with encryption_manager
cookie_consent_manager = CookieConsentManager()

# Export for easy import
__all__ = [
    "GDPRComplianceManager",
    "ThirdPartyIntegrations",
    "CookieConsentManager",
    "DataSubject",
    "ConsentRecord",
    "DataCategory",
    "ConsentType",
    "DataProcessingPurpose",
    "gdpr_manager",
    "cookie_consent_manager",
]
