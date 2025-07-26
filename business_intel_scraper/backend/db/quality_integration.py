"""
Data Quality Integration Pipeline

Integrates the data quality and provenance system with the existing
business intelligence scraping pipeline.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Any
from dataclasses import dataclass
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .quality_models import EntityRecord, DataSource, RawDataRecord
from .quality_engine import quality_engine
from .provenance_tracker import provenance_tracker
from .correction_system import correction_manager
from .alert_system import alert_manager
from ..db.models import Entity  # Existing entity model

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of processing a scraped entity"""

    entity_id: str
    success: bool
    quality_score: float
    provenance_recorded: bool
    alerts_generated: int
    issues: List[str]
    processing_time_ms: float


class QualityIntegrationPipeline:
    """Main pipeline for integrating quality system with scraping"""

    def __init__(self):
        self.processing_stats = {
            "entities_processed": 0,
            "quality_assessments": 0,
            "provenance_records": 0,
            "alerts_generated": 0,
            "errors": 0,
        }

    async def process_scraped_entity(
        self,
        entity_data: Dict[str, Any],
        raw_content: str,
        source_info: Dict[str, Any],
        session: AsyncSession,
    ) -> ProcessingResult:
        """Process a newly scraped entity through the quality pipeline"""
        start_time = datetime.now()
        entity_id = entity_data.get("entity_id") or entity_data.get("id")

        if not entity_id:
            logger.error("Entity ID missing from scraped data")
            return ProcessingResult(
                entity_id="unknown",
                success=False,
                quality_score=0.0,
                provenance_recorded=False,
                alerts_generated=0,
                issues=["Missing entity ID"],
                processing_time_ms=0,
            )

        issues = []
        alerts_generated = 0

        try:
            # 1. Ensure data source is registered
            data_source = await self._ensure_data_source(source_info, session)

            # 2. Record raw data
            raw_record = await self._record_raw_data(
                raw_content, source_info, entity_data, session
            )

            # 3. Create or update entity record
            entity_record = await self._create_or_update_entity(
                entity_data, raw_record, session
            )

            # 4. Record provenance for each field
            await self._record_field_provenance(
                entity_record, entity_data, raw_record, source_info, session
            )

            # 5. Assess quality
            quality_assessment = await quality_engine.assess_entity_quality(
                entity_record.entity_id, session, force_refresh=True
            )

            # 6. Update entity with quality scores
            if quality_assessment:
                entity_record.overall_quality_score = quality_assessment.overall_score
                entity_record.has_issues = quality_assessment.overall_score < 0.6

            # 7. Process alerts
            alerts = await alert_manager.process_entity_alerts(entity_record, session)
            alerts_generated = len(alerts)

            # 8. Generate auto-corrections if quality is low
            if quality_assessment and quality_assessment.overall_score < 0.7:
                await self._generate_auto_corrections(entity_record, session)

            await session.commit()

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            # Update stats
            self.processing_stats["entities_processed"] += 1
            self.processing_stats["quality_assessments"] += (
                1 if quality_assessment else 0
            )
            self.processing_stats["provenance_records"] += 1
            self.processing_stats["alerts_generated"] += alerts_generated

            logger.info(
                f"Successfully processed entity {entity_id} (quality: {quality_assessment.overall_score:.3f})"
            )

            return ProcessingResult(
                entity_id=entity_id,
                success=True,
                quality_score=(
                    quality_assessment.overall_score if quality_assessment else 0.0
                ),
                provenance_recorded=True,
                alerts_generated=alerts_generated,
                issues=issues,
                processing_time_ms=processing_time,
            )

        except Exception as e:
            logger.error(f"Error processing entity {entity_id}: {e}")
            await session.rollback()

            self.processing_stats["errors"] += 1

            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return ProcessingResult(
                entity_id=entity_id,
                success=False,
                quality_score=0.0,
                provenance_recorded=False,
                alerts_generated=0,
                issues=[str(e)],
                processing_time_ms=processing_time,
            )

    async def _ensure_data_source(
        self, source_info: Dict[str, Any], session: AsyncSession
    ) -> DataSource:
        """Ensure data source is registered"""
        url_pattern = source_info.get("base_url", "")
        source_name = source_info.get("name", url_pattern)

        # Check if source exists
        source_query = select(DataSource).where(DataSource.url_pattern == url_pattern)
        existing_source = (await session.execute(source_query)).scalar_one_or_none()

        if existing_source:
            # Update last scraped time
            existing_source.last_scraped = datetime.now(timezone.utc)
            return existing_source

        # Create new source
        new_source = DataSource(
            name=source_name,
            url_pattern=url_pattern,
            source_type=source_info.get("type", "web"),
            reliability_score=0.8,  # Default score for new sources
            is_active=True,
            metadata={
                "scraper_type": source_info.get("scraper_type"),
                "extraction_method": source_info.get("extraction_method"),
                "created_from": "integration_pipeline",
            },
        )

        session.add(new_source)
        await session.flush()

        logger.info(f"Registered new data source: {source_name}")
        return new_source

    async def _record_raw_data(
        self,
        raw_content: str,
        source_info: Dict[str, Any],
        entity_data: Dict[str, Any],
        session: AsyncSession,
    ) -> RawDataRecord:
        """Record raw scraped data"""
        raw_record = RawDataRecord(
            source_url=source_info.get("url", ""),
            content_hash=provenance_tracker._calculate_content_hash(raw_content),
            raw_content=raw_content,
            content_type=source_info.get("content_type", "text/html"),
            scraped_at=datetime.now(timezone.utc),
            scraper_version=source_info.get("scraper_version", "1.0"),
            extraction_metadata={
                "scraper_type": source_info.get("scraper_type"),
                "extraction_method": source_info.get("extraction_method"),
                "user_agent": source_info.get("user_agent"),
                "response_time_ms": source_info.get("response_time_ms"),
                "status_code": source_info.get("status_code"),
            },
        )

        session.add(raw_record)
        await session.flush()

        return raw_record

    async def _create_or_update_entity(
        self,
        entity_data: Dict[str, Any],
        raw_record: RawDataRecord,
        session: AsyncSession,
    ) -> EntityRecord:
        """Create or update entity record"""
        entity_id = entity_data.get("entity_id") or entity_data.get("id")

        # Check if entity exists
        entity_query = select(EntityRecord).where(EntityRecord.entity_id == entity_id)
        existing_entity = (await session.execute(entity_query)).scalar_one_or_none()

        if existing_entity:
            # Update existing entity
            existing_entity.data.update(entity_data)
            existing_entity.updated_at = datetime.now(timezone.utc)
            existing_entity.last_seen = datetime.now(timezone.utc)
            existing_entity.raw_data_records.append(raw_record)

            # Record change
            await provenance_tracker.record_entity_change(
                {
                    "change_type": "update",
                    "changed_by": "scraping_pipeline",
                    "reason": "Updated from new scrape",
                    "source": raw_record.source_url,
                    "metadata": {
                        "raw_record_id": raw_record.record_id,
                        "scraper_version": raw_record.scraper_version,
                    },
                },
                existing_entity,
                session,
            )

            return existing_entity

        # Create new entity
        new_entity = EntityRecord(
            entity_id=entity_id,
            entity_type=entity_data.get("entity_type", "unknown"),
            data=entity_data,
            overall_quality_score=0.0,  # Will be calculated
            has_issues=False,
            is_active=True,
            is_duplicate=False,
            first_seen=datetime.now(timezone.utc),
            last_seen=datetime.now(timezone.utc),
            raw_data_records=[raw_record],
        )

        session.add(new_entity)
        await session.flush()

        logger.info(f"Created new entity record: {entity_id}")
        return new_entity

    async def _record_field_provenance(
        self,
        entity_record: EntityRecord,
        entity_data: Dict[str, Any],
        raw_record: RawDataRecord,
        source_info: Dict[str, Any],
        session: AsyncSession,
    ):
        """Record provenance for each entity field"""
        for field_name, field_value in entity_data.items():
            if field_name in ["entity_id", "id", "entity_type"]:
                continue  # Skip system fields

            await provenance_tracker.record_field_provenance(
                {
                    "entity_id": entity_record.entity_id,
                    "field_name": field_name,
                    "field_value": (
                        str(field_value) if field_value is not None else None
                    ),
                    "source_url": raw_record.source_url,
                    "raw_record_id": raw_record.record_id,
                    "extraction_method": source_info.get(
                        "extraction_method", "unknown"
                    ),
                    "extraction_confidence": source_info.get("confidence", 0.8),
                    "metadata": {
                        "scraper_type": source_info.get("scraper_type"),
                        "field_xpath": source_info.get("field_selectors", {}).get(
                            field_name
                        ),
                        "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                },
                entity_record,
                session,
            )

    async def _generate_auto_corrections(
        self, entity_record: EntityRecord, session: AsyncSession
    ):
        """Generate automated correction suggestions for low-quality entities"""
        try:
            suggestions = await correction_manager.auto_engine.generate_suggestions(
                entity_record, session
            )

            # Submit high-confidence suggestions
            for suggestion in suggestions:
                if suggestion.confidence >= suggestion.auto_apply_threshold:
                    correction_data = {
                        "entity_id": suggestion.entity_id,
                        "field_name": suggestion.field_name,
                        "current_value": suggestion.current_value,
                        "suggested_value": suggestion.suggested_value,
                        "correction_type": suggestion.correction_type.value,
                        "submitted_by": "auto_correction_system",
                        "submission_source": "integration_pipeline",
                        "reason": suggestion.reason,
                        "evidence": "\n".join(suggestion.evidence),
                        "auto_apply": True,
                    }

                    await correction_manager.submit_correction(correction_data, session)

        except Exception as e:
            logger.error(
                f"Error generating auto-corrections for {entity_record.entity_id}: {e}"
            )

    async def process_batch_entities(
        self, entities_data: List[Dict[str, Any]], session: AsyncSession
    ) -> Dict[str, Any]:
        """Process a batch of scraped entities"""
        logger.info(f"Processing batch of {len(entities_data)} entities")

        results = {
            "total_entities": len(entities_data),
            "successful": 0,
            "failed": 0,
            "avg_quality_score": 0.0,
            "total_alerts": 0,
            "processing_results": [],
        }

        quality_scores = []

        for entity_data in entities_data:
            source_info = entity_data.get("_source_info", {})
            raw_content = entity_data.get("_raw_content", "")

            # Remove metadata fields from entity data
            clean_entity_data = {
                k: v for k, v in entity_data.items() if not k.startswith("_")
            }

            result = await self.process_scraped_entity(
                clean_entity_data, raw_content, source_info, session
            )

            results["processing_results"].append(
                {
                    "entity_id": result.entity_id,
                    "success": result.success,
                    "quality_score": result.quality_score,
                    "alerts_generated": result.alerts_generated,
                    "issues": result.issues,
                    "processing_time_ms": result.processing_time_ms,
                }
            )

            if result.success:
                results["successful"] += 1
                quality_scores.append(result.quality_score)
            else:
                results["failed"] += 1

            results["total_alerts"] += result.alerts_generated

        # Calculate average quality score
        if quality_scores:
            results["avg_quality_score"] = sum(quality_scores) / len(quality_scores)

        logger.info(
            f"Batch processing complete: {results['successful']}/{results['total_entities']} successful"
        )
        return results

    async def migrate_existing_entities(
        self, session: AsyncSession, batch_size: int = 100
    ) -> Dict[str, Any]:
        """Migrate existing entities to the quality system"""
        logger.info("Starting migration of existing entities to quality system")

        # Get existing entities from the old model
        entity_query = select(Entity).limit(batch_size)
        existing_entities = (await session.execute(entity_query)).scalars().all()

        migration_results = {
            "entities_migrated": 0,
            "quality_assessments_created": 0,
            "errors": [],
        }

        for entity in existing_entities:
            try:
                # Convert to new format
                entity_data = {
                    "entity_id": entity.id,
                    "entity_type": getattr(entity, "type", "company"),
                    "name": getattr(entity, "name", ""),
                    "description": getattr(entity, "description", ""),
                    "metadata": getattr(entity, "metadata", {}),
                }

                # Add other fields if they exist
                for field in ["address", "phone", "email", "website", "industry"]:
                    if hasattr(entity, field):
                        value = getattr(entity, field)
                        if value:
                            entity_data[field] = value

                source_info = {
                    "url": "migrated_from_legacy",
                    "name": "Legacy Migration",
                    "type": "migration",
                    "scraper_type": "migration_script",
                }

                # Process through pipeline
                result = await self.process_scraped_entity(
                    entity_data, json.dumps(entity_data), source_info, session
                )

                if result.success:
                    migration_results["entities_migrated"] += 1
                    migration_results["quality_assessments_created"] += 1
                else:
                    migration_results["errors"].append(
                        f"Entity {entity.id}: {', '.join(result.issues)}"
                    )

            except Exception as e:
                logger.error(f"Error migrating entity {entity.id}: {e}")
                migration_results["errors"].append(f"Entity {entity.id}: {str(e)}")

        logger.info(
            f"Migration complete: {migration_results['entities_migrated']} entities migrated"
        )
        return migration_results

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        return {
            **self.processing_stats,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def reset_stats(self):
        """Reset processing statistics"""
        self.processing_stats = {
            "entities_processed": 0,
            "quality_assessments": 0,
            "provenance_records": 0,
            "alerts_generated": 0,
            "errors": 0,
        }


class QualityMiddleware:
    """Middleware for integrating quality processing into existing scrapers"""

    def __init__(self, pipeline: QualityIntegrationPipeline):
        self.pipeline = pipeline

    async def process_scraped_data(
        self, data: Dict[str, Any], session: AsyncSession
    ) -> Dict[str, Any]:
        """Middleware function to process scraped data through quality pipeline"""

        # Extract metadata
        source_info = data.pop("_source_info", {})
        raw_content = data.pop("_raw_content", "")

        # Process through quality pipeline
        result = await self.pipeline.process_scraped_entity(
            data, raw_content, source_info, session
        )

        # Add quality information to response
        data["_quality_info"] = {
            "quality_score": result.quality_score,
            "has_issues": result.quality_score < 0.6,
            "alerts_generated": result.alerts_generated,
            "processing_success": result.success,
        }

        return data


# Global instances
quality_integration_pipeline = QualityIntegrationPipeline()
quality_middleware = QualityMiddleware(quality_integration_pipeline)
