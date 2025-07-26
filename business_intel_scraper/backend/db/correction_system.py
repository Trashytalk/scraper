"""
Data Correction & Feedback System

System for handling user-submitted corrections, automated suggestions,
and feedback loops to improve data quality.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import difflib
import re

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from .quality_models import (
    EntityRecord,
    DataCorrection,
    DataChangeLog,
    ProvenanceRecord,
    ChangeType,
)
from .provenance_tracker import provenance_tracker

logger = logging.getLogger(__name__)


class CorrectionType(str, Enum):
    """Types of data corrections"""

    FIX_VALUE = "fix_value"  # Fix incorrect value
    ADD_MISSING = "add_missing"  # Add missing field
    MERGE_ENTITIES = "merge_entities"  # Merge duplicate entities
    SPLIT_ENTITY = "split_entity"  # Split incorrectly merged entity
    FLAG_ERROR = "flag_error"  # Flag as incorrect/suspicious
    UPDATE_STALE = "update_stale"  # Update outdated information


class CorrectionStatus(str, Enum):
    """Status of correction submissions"""

    PENDING = "pending"  # Awaiting review
    APPROVED = "approved"  # Approved but not applied
    APPLIED = "applied"  # Successfully applied
    REJECTED = "rejected"  # Rejected after review
    SUPERSEDED = "superseded"  # Replaced by newer correction


@dataclass
class CorrectionSuggestion:
    """Automated correction suggestion"""

    entity_id: str
    field_name: str
    current_value: Any
    suggested_value: Any
    correction_type: CorrectionType
    confidence: float
    reason: str
    evidence: List[str]
    auto_apply_threshold: float


@dataclass
class ValidationResult:
    """Result of correction validation"""

    is_valid: bool
    confidence: float
    issues: List[str]
    warnings: List[str]
    supporting_evidence: List[str]


class CorrectionValidator:
    """Validates correction suggestions"""

    def __init__(self):
        # Define validation rules by field type
        self.field_validators = {
            "email": self._validate_email,
            "phone": self._validate_phone,
            "url": self._validate_url,
            "registration_id": self._validate_registration_id,
            "address": self._validate_address,
            "date": self._validate_date,
        }

        # Common business suffixes for company name validation
        self.company_suffixes = [
            "inc",
            "corp",
            "llc",
            "ltd",
            "limited",
            "company",
            "co",
            "corporation",
            "incorporated",
            "group",
            "holdings",
            "gmbh",
            "ag",
            "sa",
            "sarl",
            "bv",
            "oy",
            "ab",
        ]

    async def validate_correction(
        self, correction: Dict[str, Any], entity: EntityRecord, session: AsyncSession
    ) -> ValidationResult:
        """Validate a correction suggestion"""
        field_name = correction["field_name"]
        current_value = correction.get("current_value")
        suggested_value = correction["suggested_value"]
        correction_type = correction["correction_type"]

        issues = []
        warnings = []
        evidence = []
        confidence = 0.5

        # Basic validation
        if not suggested_value and correction_type != CorrectionType.FLAG_ERROR:
            issues.append("Suggested value cannot be empty")
            return ValidationResult(False, 0.0, issues, warnings, evidence)

        # Type-specific validation
        field_type = self._infer_field_type(field_name, suggested_value)
        if field_type in self.field_validators:
            try:
                is_valid, field_confidence, field_issues = await self.field_validators[
                    field_type
                ](suggested_value, field_name, entity, session)
                confidence = field_confidence
                issues.extend(field_issues)
            except Exception as e:
                logger.error(f"Error validating {field_type} field: {e}")
                issues.append(f"Validation error: {str(e)}")

        # Check for conflicting corrections
        conflicting_corrections = await self._check_conflicting_corrections(
            entity.entity_id, field_name, suggested_value, session
        )

        if conflicting_corrections:
            warnings.append(
                f"Found {len(conflicting_corrections)} conflicting corrections"
            )
            evidence.append(
                f"Conflicting values: {[c.suggested_value for c in conflicting_corrections]}"
            )

        # Check supporting evidence from other sources
        supporting_sources = await self._find_supporting_evidence(
            entity, field_name, suggested_value, session
        )

        if supporting_sources:
            confidence = min(1.0, confidence + (len(supporting_sources) * 0.1))
            evidence.append(
                f"Supported by {len(supporting_sources)} additional sources"
            )

        # Business logic validation
        business_validation = await self._validate_business_logic(
            entity, field_name, suggested_value, session
        )

        if business_validation["issues"]:
            issues.extend(business_validation["issues"])
        if business_validation["warnings"]:
            warnings.extend(business_validation["warnings"])

        confidence *= business_validation["confidence_multiplier"]

        is_valid = len(issues) == 0

        return ValidationResult(is_valid, confidence, issues, warnings, evidence)

    def _infer_field_type(self, field_name: str, value: Any) -> str:
        """Infer field type from name and value"""
        field_name_lower = field_name.lower()

        if "email" in field_name_lower:
            return "email"
        elif "phone" in field_name_lower or "tel" in field_name_lower:
            return "phone"
        elif "url" in field_name_lower or "website" in field_name_lower:
            return "url"
        elif "registration" in field_name_lower or "reg_id" in field_name_lower:
            return "registration_id"
        elif "address" in field_name_lower:
            return "address"
        elif (
            "date" in field_name_lower
            or isinstance(value, str)
            and re.match(r"\d{4}-\d{2}-\d{2}", value)
        ):
            return "date"
        else:
            return "generic"

    async def _validate_email(
        self, value: str, field_name: str, entity: EntityRecord, session: AsyncSession
    ) -> Tuple[bool, float, List[str]]:
        """Validate email address"""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(email_pattern, value):
            return False, 0.1, ["Invalid email format"]

        # Additional checks
        issues = []
        confidence = 0.8

        # Check for common typos in domains
        domain = value.split("@")[1]
        common_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
        similar_domain = difflib.get_close_matches(
            domain, common_domains, n=1, cutoff=0.8
        )

        if similar_domain and similar_domain[0] != domain:
            issues.append(
                f"Domain '{domain}' is similar to '{similar_domain[0]}' - possible typo"
            )
            confidence = 0.6

        return len(issues) == 0, confidence, issues

    async def _validate_phone(
        self, value: str, field_name: str, entity: EntityRecord, session: AsyncSession
    ) -> Tuple[bool, float, List[str]]:
        """Validate phone number"""
        # Remove all non-digit characters except +
        cleaned = re.sub(r"[^\d+]", "", value)

        issues = []
        confidence = 0.7

        if not cleaned:
            return False, 0.0, ["No digits found in phone number"]

        # Check length
        if len(cleaned.replace("+", "")) < 7:
            issues.append("Phone number too short")
        elif len(cleaned.replace("+", "")) > 15:
            issues.append("Phone number too long")

        # Check format
        if cleaned.startswith("+"):
            confidence = 0.9  # International format preferred
        elif len(cleaned) == 10:
            confidence = 0.8  # Likely domestic format

        return len(issues) == 0, confidence, issues

    async def _validate_url(
        self, value: str, field_name: str, entity: EntityRecord, session: AsyncSession
    ) -> Tuple[bool, float, List[str]]:
        """Validate URL"""
        url_pattern = r"^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$"

        if not re.match(url_pattern, value):
            return False, 0.2, ["Invalid URL format"]

        confidence = 0.8
        issues = []

        # Prefer HTTPS
        if value.startswith("http://"):
            confidence = 0.7
            # Don't mark as issue, just lower confidence

        return True, confidence, issues

    async def _validate_registration_id(
        self, value: str, field_name: str, entity: EntityRecord, session: AsyncSession
    ) -> Tuple[bool, float, List[str]]:
        """Validate company registration ID"""
        # Basic format checks - could be enhanced with country-specific validation
        issues = []
        confidence = 0.6

        if len(value) < 5:
            issues.append("Registration ID too short")

        # Check for reasonable format (alphanumeric with possible separators)
        if not re.match(r"^[A-Z0-9\-/\.]+$", value.upper()):
            issues.append("Registration ID contains invalid characters")

        return len(issues) == 0, confidence, issues

    async def _validate_address(
        self, value: str, field_name: str, entity: EntityRecord, session: AsyncSession
    ) -> Tuple[bool, float, List[str]]:
        """Validate address"""
        issues = []
        confidence = 0.7

        if len(value.strip()) < 10:
            issues.append("Address appears too short")

        # Check for basic address components
        has_number = bool(re.search(r"\d+", value))
        has_street_indicator = bool(
            re.search(
                r"\b(street|st|avenue|ave|road|rd|lane|ln|drive|dr|boulevard|blvd)\b",
                value.lower(),
            )
        )

        if not has_number:
            confidence *= 0.8

        if not has_street_indicator:
            confidence *= 0.9

        return len(issues) == 0, confidence, issues

    async def _validate_date(
        self, value: str, field_name: str, entity: EntityRecord, session: AsyncSession
    ) -> Tuple[bool, float, List[str]]:
        """Validate date"""
        issues = []
        confidence = 0.8

        try:
            # Try parsing common date formats
            if re.match(r"\d{4}-\d{2}-\d{2}", value):
                datetime.strptime(value, "%Y-%m-%d")
            elif re.match(r"\d{2}/\d{2}/\d{4}", value):
                datetime.strptime(value, "%m/%d/%Y")
            elif re.match(r"\d{2}-\d{2}-\d{4}", value):
                datetime.strptime(value, "%m-%d-%Y")
            else:
                issues.append("Unrecognized date format")
                confidence = 0.3
        except ValueError:
            issues.append("Invalid date")
            confidence = 0.1

        return len(issues) == 0, confidence, issues

    async def _check_conflicting_corrections(
        self,
        entity_id: str,
        field_name: str,
        suggested_value: str,
        session: AsyncSession,
    ) -> List[DataCorrection]:
        """Check for conflicting correction submissions"""
        query = (
            select(DataCorrection)
            .join(EntityRecord)
            .where(
                and_(
                    EntityRecord.entity_id == entity_id,
                    DataCorrection.field_name == field_name,
                    DataCorrection.suggested_value != suggested_value,
                    DataCorrection.status.in_(
                        [CorrectionStatus.PENDING, CorrectionStatus.APPROVED]
                    ),
                )
            )
        )

        return (await session.execute(query)).scalars().all()

    async def _find_supporting_evidence(
        self,
        entity: EntityRecord,
        field_name: str,
        suggested_value: str,
        session: AsyncSession,
    ) -> List[str]:
        """Find supporting evidence from other sources"""
        # Look for the same value in provenance records from different sources
        query = (
            select(ProvenanceRecord.source_url)
            .where(
                and_(
                    ProvenanceRecord.entity_id == entity.id,
                    ProvenanceRecord.field_name == field_name,
                    ProvenanceRecord.field_value == suggested_value,
                )
            )
            .distinct()
        )

        sources = (await session.execute(query)).scalars().all()
        return sources

    async def _validate_business_logic(
        self,
        entity: EntityRecord,
        field_name: str,
        suggested_value: str,
        session: AsyncSession,
    ) -> Dict[str, Any]:
        """Apply business logic validation"""
        result = {"issues": [], "warnings": [], "confidence_multiplier": 1.0}

        # Company name validation
        if (
            field_name.lower() in ["name", "company_name"]
            and entity.entity_type == "company"
        ):
            # Check for reasonable company name
            if len(suggested_value.strip()) < 3:
                result["issues"].append("Company name too short")

            # Check for common suffixes
            words = suggested_value.lower().split()
            has_suffix = any(
                word.strip(".,") in self.company_suffixes for word in words
            )

            if not has_suffix:
                result["warnings"].append(
                    "Company name doesn't include common business suffix"
                )
                result["confidence_multiplier"] *= 0.9

        # Person name validation
        elif (
            field_name.lower() in ["name", "person_name"]
            and entity.entity_type == "person"
        ):
            # Basic name validation
            if len(suggested_value.strip().split()) < 2:
                result["warnings"].append("Person name appears to have only one part")
                result["confidence_multiplier"] *= 0.8

        return result


class AutoCorrectionEngine:
    """Engine for generating automated correction suggestions"""

    def __init__(self):
        self.validator = CorrectionValidator()

    async def generate_suggestions(
        self, entity: EntityRecord, session: AsyncSession
    ) -> List[CorrectionSuggestion]:
        """Generate automated correction suggestions for an entity"""
        suggestions = []

        try:
            # Get all provenance for this entity
            prov_query = (
                select(ProvenanceRecord)
                .where(ProvenanceRecord.entity_id == entity.id)
                .options(selectinload(ProvenanceRecord.raw_record))
            )
            provenance_records = (await session.execute(prov_query)).scalars().all()

            # Analyze for common correction patterns
            suggestions.extend(
                await self._suggest_missing_field_fixes(
                    entity, provenance_records, session
                )
            )
            suggestions.extend(await self._suggest_format_fixes(entity, session))
            suggestions.extend(
                await self._suggest_consistency_fixes(
                    entity, provenance_records, session
                )
            )
            suggestions.extend(await self._suggest_duplicate_merges(entity, session))

        except Exception as e:
            logger.error(
                f"Error generating suggestions for entity {entity.entity_id}: {e}"
            )

        return suggestions

    async def _suggest_missing_field_fixes(
        self,
        entity: EntityRecord,
        provenance_records: List[ProvenanceRecord],
        session: AsyncSession,
    ) -> List[CorrectionSuggestion]:
        """Suggest additions for missing required fields"""
        suggestions = []

        # Define required fields by entity type
        required_fields = {
            "company": ["name", "address", "registration_id"],
            "person": ["name"],
            "address": ["street", "city", "country"],
        }

        entity_required = required_fields.get(entity.entity_type, [])

        for field in entity_required:
            if field not in entity.data or not entity.data[field]:
                # Look for this field in raw data
                for prov in provenance_records:
                    if prov.field_name == field and prov.field_value:
                        suggestion = CorrectionSuggestion(
                            entity_id=entity.entity_id,
                            field_name=field,
                            current_value=entity.data.get(field),
                            suggested_value=prov.field_value,
                            correction_type=CorrectionType.ADD_MISSING,
                            confidence=prov.extraction_confidence,
                            reason=f"Found {field} in source data but missing from entity",
                            evidence=[f"Source: {prov.source_url}"],
                            auto_apply_threshold=0.8,
                        )
                        suggestions.append(suggestion)
                        break

        return suggestions

    async def _suggest_format_fixes(
        self, entity: EntityRecord, session: AsyncSession
    ) -> List[CorrectionSuggestion]:
        """Suggest format corrections"""
        suggestions = []

        for field_name, value in entity.data.items():
            if not isinstance(value, str) or not value:
                continue

            # Phone number formatting
            if "phone" in field_name.lower():
                cleaned_phone = re.sub(r"[^\d+]", "", value)
                if cleaned_phone != value and len(cleaned_phone) >= 10:
                    # Format as international if possible
                    if not cleaned_phone.startswith("+"):
                        formatted = (
                            f"+1{cleaned_phone}"
                            if len(cleaned_phone) == 10
                            else f"+{cleaned_phone}"
                        )
                    else:
                        formatted = cleaned_phone

                    suggestion = CorrectionSuggestion(
                        entity_id=entity.entity_id,
                        field_name=field_name,
                        current_value=value,
                        suggested_value=formatted,
                        correction_type=CorrectionType.FIX_VALUE,
                        confidence=0.9,
                        reason="Standardize phone number format",
                        evidence=["Phone number formatting rules"],
                        auto_apply_threshold=0.95,
                    )
                    suggestions.append(suggestion)

            # Email case normalization
            elif "email" in field_name.lower():
                normalized_email = value.lower().strip()
                if normalized_email != value:
                    suggestion = CorrectionSuggestion(
                        entity_id=entity.entity_id,
                        field_name=field_name,
                        current_value=value,
                        suggested_value=normalized_email,
                        correction_type=CorrectionType.FIX_VALUE,
                        confidence=0.95,
                        reason="Normalize email address case",
                        evidence=["Email normalization standards"],
                        auto_apply_threshold=0.98,
                    )
                    suggestions.append(suggestion)

        return suggestions

    async def _suggest_consistency_fixes(
        self,
        entity: EntityRecord,
        provenance_records: List[ProvenanceRecord],
        session: AsyncSession,
    ) -> List[CorrectionSuggestion]:
        """Suggest fixes for consistency issues"""
        suggestions = []

        # Group provenance by field
        field_values = {}
        for prov in provenance_records:
            if prov.field_name not in field_values:
                field_values[prov.field_name] = []
            field_values[prov.field_name].append(
                {
                    "value": prov.field_value,
                    "confidence": prov.extraction_confidence,
                    "source_url": prov.source_url,
                }
            )

        # Check for conflicts and suggest best value
        for field_name, values in field_values.items():
            if len(values) <= 1:
                continue

            # Get unique values
            unique_values = {}
            for val_info in values:
                val = val_info["value"]
                if val not in unique_values:
                    unique_values[val] = []
                unique_values[val].append(val_info)

            if len(unique_values) > 1:
                # Find most confident/frequent value
                best_value = None
                best_score = 0

                for value, instances in unique_values.items():
                    # Score based on confidence and frequency
                    avg_confidence = sum(
                        inst["confidence"] for inst in instances
                    ) / len(instances)
                    frequency_bonus = len(instances) * 0.1
                    score = avg_confidence + frequency_bonus

                    if score > best_score:
                        best_score = score
                        best_value = value

                current_value = entity.data.get(field_name)
                if best_value and best_value != current_value:
                    suggestion = CorrectionSuggestion(
                        entity_id=entity.entity_id,
                        field_name=field_name,
                        current_value=current_value,
                        suggested_value=best_value,
                        correction_type=CorrectionType.FIX_VALUE,
                        confidence=best_score,
                        reason=f"Most reliable value from {len(unique_values[best_value])} sources",
                        evidence=[
                            inst["source_url"] for inst in unique_values[best_value]
                        ],
                        auto_apply_threshold=0.85,
                    )
                    suggestions.append(suggestion)

        return suggestions

    async def _suggest_duplicate_merges(
        self, entity: EntityRecord, session: AsyncSession
    ) -> List[CorrectionSuggestion]:
        """Suggest entity merges for likely duplicates"""
        suggestions = []

        # Find potential duplicates based on similar names
        if "name" in entity.data:
            name = entity.data["name"]

            # Look for entities with similar names
            similar_query = select(EntityRecord).where(
                and_(
                    EntityRecord.entity_type == entity.entity_type,
                    EntityRecord.id != entity.id,
                    EntityRecord.is_active == True,
                )
            )

            similar_entities = (await session.execute(similar_query)).scalars().all()

            for other_entity in similar_entities:
                if "name" not in other_entity.data:
                    continue

                other_name = other_entity.data["name"]

                # Calculate similarity
                similarity = difflib.SequenceMatcher(
                    None, name.lower(), other_name.lower()
                ).ratio()

                if similarity > 0.85:  # High similarity threshold
                    suggestion = CorrectionSuggestion(
                        entity_id=entity.entity_id,
                        field_name="merge_target",
                        current_value=entity.entity_id,
                        suggested_value=other_entity.entity_id,
                        correction_type=CorrectionType.MERGE_ENTITIES,
                        confidence=similarity,
                        reason=f"High name similarity ({similarity:.2f}) with entity {other_entity.entity_id}",
                        evidence=[f"Names: '{name}' vs '{other_name}'"],
                        auto_apply_threshold=0.95,
                    )
                    suggestions.append(suggestion)

        return suggestions


class CorrectionManager:
    """Main manager for data correction system"""

    def __init__(self):
        self.validator = CorrectionValidator()
        self.auto_engine = AutoCorrectionEngine()

    async def submit_correction(
        self, correction_data: Dict[str, Any], session: AsyncSession
    ) -> DataCorrection:
        """Submit a new data correction"""
        # Get entity
        entity_query = select(EntityRecord).where(
            EntityRecord.entity_id == correction_data["entity_id"]
        )
        entity = (await session.execute(entity_query)).scalar_one_or_none()

        if not entity:
            raise ValueError(f"Entity {correction_data['entity_id']} not found")

        # Validate correction
        validation = await self.validator.validate_correction(
            correction_data, entity, session
        )

        # Create correction record
        correction = DataCorrection(
            entity_id=entity.id,
            field_name=correction_data["field_name"],
            current_value=correction_data.get("current_value"),
            suggested_value=correction_data["suggested_value"],
            correction_type=correction_data["correction_type"],
            submitted_by=correction_data["submitted_by"],
            submission_source=correction_data.get("submission_source", "api"),
            reason=correction_data.get("reason"),
            evidence=correction_data.get("evidence"),
            confidence=validation.confidence,
            status=CorrectionStatus.PENDING,
        )

        session.add(correction)
        await session.commit()

        logger.info(
            f"Submitted correction {correction.correction_id} for entity {entity.entity_id}"
        )

        # Auto-apply if high confidence and no issues
        if (
            validation.is_valid
            and validation.confidence >= 0.95
            and correction_data.get("auto_apply", False)
        ):
            await self.apply_correction(correction.correction_id, "system", session)

        return correction

    async def review_correction(
        self,
        correction_id: str,
        reviewer: str,
        decision: str,
        notes: str,
        session: AsyncSession,
    ) -> DataCorrection:
        """Review and approve/reject a correction"""
        correction_query = select(DataCorrection).where(
            DataCorrection.correction_id == correction_id
        )
        correction = (await session.execute(correction_query)).scalar_one_or_none()

        if not correction:
            raise ValueError(f"Correction {correction_id} not found")

        if decision.lower() == "approve":
            correction.status = CorrectionStatus.APPROVED
        elif decision.lower() == "reject":
            correction.status = CorrectionStatus.REJECTED
        else:
            raise ValueError("Decision must be 'approve' or 'reject'")

        correction.reviewed_by = reviewer
        correction.reviewed_at = datetime.now(timezone.utc)
        correction.review_notes = notes

        await session.commit()

        logger.info(f"Correction {correction_id} {decision} by {reviewer}")

        # Auto-apply if approved
        if correction.status == CorrectionStatus.APPROVED:
            await self.apply_correction(correction_id, reviewer, session)

        return correction

    async def apply_correction(
        self, correction_id: str, applied_by: str, session: AsyncSession
    ) -> Optional[DataChangeLog]:
        """Apply an approved correction"""
        correction_query = (
            select(DataCorrection)
            .where(DataCorrection.correction_id == correction_id)
            .options(selectinload(DataCorrection.entity))
        )
        correction = (await session.execute(correction_query)).scalar_one_or_none()

        if not correction:
            raise ValueError(f"Correction {correction_id} not found")

        if correction.status != CorrectionStatus.APPROVED:
            raise ValueError(f"Correction {correction_id} is not approved")

        entity = correction.entity
        field_name = correction.field_name
        old_value = correction.current_value
        new_value = correction.suggested_value

        try:
            # Apply the change
            if correction.correction_type == CorrectionType.MERGE_ENTITIES:
                # Handle entity merge (complex operation)
                change_log = await self._merge_entities(
                    entity, new_value, applied_by, session
                )
            else:
                # Simple field update
                if field_name in entity.data:
                    old_value = entity.data[field_name]

                entity.data[field_name] = new_value
                entity.updated_at = datetime.now(timezone.utc)

                # Record change
                change_log = await provenance_tracker.record_entity_change(
                    {
                        "change_type": ChangeType.CORRECTION.value,
                        "field_name": field_name,
                        "old_value": str(old_value) if old_value else None,
                        "new_value": str(new_value),
                        "changed_by": applied_by,
                        "reason": f"Applied correction {correction_id}",
                        "source": "correction_system",
                        "metadata": {
                            "correction_id": correction_id,
                            "submitted_by": correction.submitted_by,
                            "correction_confidence": correction.confidence,
                        },
                    },
                    entity,
                    session,
                )

            # Update correction status
            correction.status = CorrectionStatus.APPLIED
            correction.applied_at = datetime.now(timezone.utc)
            correction.change_log_id = change_log.change_id

            await session.commit()

            logger.info(
                f"Applied correction {correction_id} to entity {entity.entity_id}"
            )
            return change_log

        except Exception as e:
            logger.error(f"Error applying correction {correction_id}: {e}")
            await session.rollback()
            raise

    async def _merge_entities(
        self,
        primary_entity: EntityRecord,
        target_entity_id: str,
        merged_by: str,
        session: AsyncSession,
    ) -> DataChangeLog:
        """Merge two entities"""
        # Get target entity
        target_query = select(EntityRecord).where(
            EntityRecord.entity_id == target_entity_id
        )
        target_entity = (await session.execute(target_query)).scalar_one_or_none()

        if not target_entity:
            raise ValueError(f"Target entity {target_entity_id} not found")

        # Merge data (primary entity data takes precedence)
        merged_data = target_entity.data.copy()
        merged_data.update(primary_entity.data)

        # Update primary entity
        primary_entity.data = merged_data
        primary_entity.updated_at = datetime.now(timezone.utc)

        # Mark target entity as duplicate
        target_entity.is_duplicate = True
        target_entity.duplicate_of = primary_entity.entity_id
        target_entity.is_active = False

        # Record the merge
        change_log = await provenance_tracker.record_entity_change(
            {
                "change_type": ChangeType.MERGE.value,
                "old_value": target_entity_id,
                "new_value": primary_entity.entity_id,
                "changed_by": merged_by,
                "reason": "Entity merge via correction system",
                "source": "correction_system",
                "metadata": {
                    "merged_entity_id": target_entity_id,
                    "primary_entity_id": primary_entity.entity_id,
                },
            },
            primary_entity,
            session,
        )

        return change_log

    async def get_pending_corrections(
        self, session: AsyncSession, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get pending corrections for review"""
        query = (
            select(DataCorrection)
            .where(DataCorrection.status == CorrectionStatus.PENDING)
            .options(selectinload(DataCorrection.entity))
            .order_by(DataCorrection.submitted_at.desc())
            .limit(limit)
        )

        corrections = (await session.execute(query)).scalars().all()

        result = []
        for correction in corrections:
            result.append(
                {
                    "correction_id": correction.correction_id,
                    "entity_id": correction.entity.entity_id,
                    "entity_type": correction.entity.entity_type,
                    "field_name": correction.field_name,
                    "current_value": correction.current_value,
                    "suggested_value": correction.suggested_value,
                    "correction_type": correction.correction_type,
                    "confidence": correction.confidence,
                    "submitted_by": correction.submitted_by,
                    "submitted_at": correction.submitted_at.isoformat(),
                    "reason": correction.reason,
                    "evidence": correction.evidence,
                }
            )

        return result

    async def generate_auto_corrections(
        self, session: AsyncSession, batch_size: int = 100
    ) -> Dict[str, Any]:
        """Generate automated correction suggestions"""
        logger.info("Starting automatic correction generation")

        # Get entities that might need corrections
        entities_query = (
            select(EntityRecord)
            .where(
                and_(
                    EntityRecord.is_active == True,
                    or_(
                        EntityRecord.has_issues == True,
                        EntityRecord.overall_quality_score < 0.8,
                    ),
                )
            )
            .limit(batch_size)
        )

        entities = (await session.execute(entities_query)).scalars().all()

        results = {
            "processed_entities": 0,
            "total_suggestions": 0,
            "auto_applied": 0,
            "pending_review": 0,
            "errors": [],
        }

        for entity in entities:
            try:
                suggestions = await self.auto_engine.generate_suggestions(
                    entity, session
                )

                for suggestion in suggestions:
                    # Submit as correction
                    correction_data = {
                        "entity_id": suggestion.entity_id,
                        "field_name": suggestion.field_name,
                        "current_value": suggestion.current_value,
                        "suggested_value": suggestion.suggested_value,
                        "correction_type": suggestion.correction_type.value,
                        "submitted_by": "auto_correction_system",
                        "submission_source": "automated",
                        "reason": suggestion.reason,
                        "evidence": "\n".join(suggestion.evidence),
                        "auto_apply": suggestion.confidence
                        >= suggestion.auto_apply_threshold,
                    }

                    correction = await self.submit_correction(correction_data, session)

                    results["total_suggestions"] += 1

                    if correction.status == CorrectionStatus.APPLIED:
                        results["auto_applied"] += 1
                    else:
                        results["pending_review"] += 1

                results["processed_entities"] += 1

            except Exception as e:
                logger.error(
                    f"Error generating suggestions for entity {entity.entity_id}: {e}"
                )
                results["errors"].append(f"Entity {entity.entity_id}: {str(e)}")

        logger.info(
            f"Auto-correction complete: {results['total_suggestions']} suggestions generated"
        )
        return results


# Global correction manager instance
correction_manager = CorrectionManager()
