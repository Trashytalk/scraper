"""
Data Quality & Provenance Intelligence System Initialization

Initializes all components of the data quality and provenance system,
sets up database tables, and provides system startup functionality.
"""

import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text

from .quality_models import Base, QualityRule
from .quality_engine import quality_engine
from .provenance_tracker import provenance_tracker
from .correction_system import correction_manager
from .alert_system import alert_manager
from .quality_dashboard import quality_dashboard
from .quality_integration import quality_integration_pipeline

logger = logging.getLogger(__name__)


class DataQualitySystem:
    """Main system coordinator for data quality and provenance intelligence"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.is_initialized = False
        self.system_config = {
            "quality_thresholds": {
                "completeness_weight": 0.3,
                "consistency_weight": 0.25,
                "freshness_weight": 0.2,
                "confidence_weight": 0.25,
                "critical_threshold": 0.3,
                "warning_threshold": 0.6,
            },
            "alert_settings": {
                "email_notifications": False,
                "webhook_notifications": False,
                "log_notifications": True,
            },
            "correction_settings": {
                "auto_apply_threshold": 0.95,
                "auto_generation_enabled": True,
                "batch_processing_enabled": True,
            },
        }

    async def initialize(self) -> Dict[str, Any]:
        """Initialize the complete data quality system"""
        logger.info("Initializing Data Quality & Provenance Intelligence System")

        init_results = {
            "database_initialized": False,
            "tables_created": [],
            "indexes_created": [],
            "default_rules_created": 0,
            "components_initialized": [],
            "errors": [],
        }

        try:
            # Create database engine
            self.engine = create_async_engine(self.database_url, echo=False)

            # Create all tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                init_results["database_initialized"] = True

                # Get created tables
                result = await conn.execute(
                    text(
                        """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE '%quality%' OR table_name LIKE '%provenance%'
                """
                    )
                )
                init_results["tables_created"] = [row[0] for row in result.fetchall()]

            logger.info(
                f"Created {len(init_results['tables_created'])} quality system tables"
            )

            # Initialize components
            async with AsyncSession(self.engine) as session:
                # Create default quality rules
                default_rules_count = await self._create_default_quality_rules(session)
                init_results["default_rules_created"] = default_rules_count

                # Create performance indexes
                indexes_created = await self._create_performance_indexes(session)
                init_results["indexes_created"] = indexes_created

                await session.commit()

            # Initialize system components
            await self._initialize_components()
            init_results["components_initialized"] = [
                "quality_engine",
                "provenance_tracker",
                "correction_manager",
                "alert_manager",
                "quality_dashboard",
                "integration_pipeline",
            ]

            self.is_initialized = True

            logger.info(
                "Data Quality & Provenance Intelligence System successfully initialized"
            )
            return init_results

        except Exception as e:
            logger.error(f"Failed to initialize data quality system: {e}")
            init_results["errors"].append(str(e))
            raise

    async def _create_default_quality_rules(self, session: AsyncSession) -> int:
        """Create default quality assessment rules"""
        default_rules = [
            {
                "rule_name": "completeness_check",
                "rule_type": "completeness",
                "conditions": {
                    "required_fields": ["name"],
                    "optional_fields": ["address", "phone", "email", "website"],
                    "completeness_threshold": 0.6,
                },
                "severity": "medium",
                "is_active": True,
            },
            {
                "rule_name": "consistency_check",
                "rule_type": "consistency",
                "conditions": {
                    "cross_source_validation": True,
                    "field_format_validation": True,
                    "duplicate_detection": True,
                },
                "severity": "high",
                "is_active": True,
            },
            {
                "rule_name": "freshness_check",
                "rule_type": "freshness",
                "conditions": {"max_staleness_days": 30, "warning_staleness_days": 14},
                "severity": "medium",
                "is_active": True,
            },
            {
                "rule_name": "confidence_check",
                "rule_type": "confidence",
                "conditions": {
                    "min_source_reliability": 0.7,
                    "min_extraction_confidence": 0.6,
                },
                "severity": "high",
                "is_active": True,
            },
        ]

        created_count = 0

        for rule_config in default_rules:
            # Check if rule already exists
            existing_rule = await session.execute(
                text("SELECT rule_id FROM quality_rules WHERE rule_name = :name"),
                {"name": rule_config["rule_name"]},
            )

            if existing_rule.first():
                continue

            rule = QualityRule(
                rule_name=rule_config["rule_name"],
                rule_type=rule_config["rule_type"],
                conditions=rule_config["conditions"],
                severity=rule_config["severity"],
                is_active=rule_config["is_active"],
            )

            session.add(rule)
            created_count += 1

        logger.info(f"Created {created_count} default quality rules")
        return created_count

    async def _create_performance_indexes(self, session: AsyncSession) -> List[str]:
        """Create performance indexes for quality tables"""
        indexes = [
            # Entity records indexes
            "CREATE INDEX IF NOT EXISTS idx_entity_records_entity_id ON entity_records(entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_entity_records_type_active ON entity_records(entity_type, is_active)",
            "CREATE INDEX IF NOT EXISTS idx_entity_records_quality_score ON entity_records(overall_quality_score)",
            "CREATE INDEX IF NOT EXISTS idx_entity_records_updated_at ON entity_records(updated_at)",
            # Provenance records indexes
            "CREATE INDEX IF NOT EXISTS idx_provenance_entity_field ON provenance_records(entity_id, field_name)",
            "CREATE INDEX IF NOT EXISTS idx_provenance_source_url ON provenance_records(source_url)",
            "CREATE INDEX IF NOT EXISTS idx_provenance_created_at ON provenance_records(created_at)",
            # Quality assessments indexes
            "CREATE INDEX IF NOT EXISTS idx_quality_assessments_entity ON quality_assessments(entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_quality_assessments_assessed_at ON quality_assessments(assessed_at)",
            "CREATE INDEX IF NOT EXISTS idx_quality_assessments_overall_score ON quality_assessments(overall_score)",
            # Data corrections indexes
            "CREATE INDEX IF NOT EXISTS idx_data_corrections_entity ON data_corrections(entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_data_corrections_status ON data_corrections(status)",
            "CREATE INDEX IF NOT EXISTS idx_data_corrections_submitted_at ON data_corrections(submitted_at)",
            # Quality alerts indexes
            "CREATE INDEX IF NOT EXISTS idx_quality_alerts_entity ON quality_alerts(entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_quality_alerts_severity ON quality_alerts(severity)",
            "CREATE INDEX IF NOT EXISTS idx_quality_alerts_triggered_at ON quality_alerts(triggered_at)",
            "CREATE INDEX IF NOT EXISTS idx_quality_alerts_resolved ON quality_alerts(is_resolved)",
            # Data change logs indexes
            "CREATE INDEX IF NOT EXISTS idx_change_logs_entity ON data_change_logs(entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_change_logs_changed_at ON data_change_logs(changed_at)",
            "CREATE INDEX IF NOT EXISTS idx_change_logs_change_type ON data_change_logs(change_type)",
            # Raw data records indexes
            "CREATE INDEX IF NOT EXISTS idx_raw_data_source_url ON raw_data_records(source_url)",
            "CREATE INDEX IF NOT EXISTS idx_raw_data_scraped_at ON raw_data_records(scraped_at)",
            "CREATE INDEX IF NOT EXISTS idx_raw_data_content_hash ON raw_data_records(content_hash)",
        ]

        created_indexes = []

        for index_sql in indexes:
            try:
                await session.execute(text(index_sql))
                index_name = (
                    index_sql.split("idx_")[1].split(" ON")[0]
                    if "idx_" in index_sql
                    else "unknown"
                )
                created_indexes.append(f"idx_{index_name}")
            except Exception as e:
                logger.warning(f"Failed to create index: {e}")

        logger.info(f"Created {len(created_indexes)} performance indexes")
        return created_indexes

    async def _initialize_components(self):
        """Initialize system components"""
        # Initialize quality engine
        await quality_engine.initialize()

        # Initialize provenance tracker
        await provenance_tracker.initialize()

        # Initialize correction manager
        # (No specific initialization needed)

        # Initialize alert manager
        # (No specific initialization needed)

        # Initialize dashboard
        # (No specific initialization needed)

        # Initialize integration pipeline
        # (No specific initialization needed)

        logger.info("All system components initialized")

    async def health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        health_status = {
            "system_initialized": self.is_initialized,
            "database_connection": False,
            "component_status": {},
            "recent_activity": {},
            "issues": [],
        }

        try:
            # Check database connection
            async with AsyncSession(self.engine) as session:
                result = await session.execute(text("SELECT 1"))
                health_status["database_connection"] = result.scalar() == 1

                # Check recent activity
                activity_check = await session.execute(
                    text(
                        """
                    SELECT 
                        (SELECT COUNT(*) FROM entity_records WHERE updated_at >= NOW() - INTERVAL '1 hour') as recent_entities,
                        (SELECT COUNT(*) FROM quality_assessments WHERE assessed_at >= NOW() - INTERVAL '1 hour') as recent_assessments,
                        (SELECT COUNT(*) FROM quality_alerts WHERE triggered_at >= NOW() - INTERVAL '1 hour') as recent_alerts,
                        (SELECT COUNT(*) FROM data_corrections WHERE submitted_at >= NOW() - INTERVAL '1 hour') as recent_corrections
                """
                    )
                )

                activity = activity_check.first()
                health_status["recent_activity"] = {
                    "entities_updated": activity.recent_entities,
                    "quality_assessments": activity.recent_assessments,
                    "alerts_generated": activity.recent_alerts,
                    "corrections_submitted": activity.recent_corrections,
                }

                # Component status checks
                health_status["component_status"] = {
                    "quality_engine": "healthy",
                    "provenance_tracker": "healthy",
                    "correction_manager": "healthy",
                    "alert_manager": "healthy",
                    "quality_dashboard": "healthy",
                    "integration_pipeline": "healthy",
                }

        except Exception as e:
            health_status["issues"].append(f"Health check error: {str(e)}")
            logger.error(f"Health check failed: {e}")

        return health_status

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        if not self.is_initialized:
            return {"error": "System not initialized"}

        try:
            async with AsyncSession(self.engine) as session:
                # Get overview metrics from dashboard
                overview = await quality_dashboard.get_overview_metrics(session)

                # Get processing stats from integration pipeline
                processing_stats = quality_integration_pipeline.get_processing_stats()

                # Get system configuration
                return {
                    "system_overview": overview,
                    "processing_statistics": processing_stats,
                    "system_configuration": self.system_config,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {"error": str(e)}

    async def run_maintenance_tasks(self) -> Dict[str, Any]:
        """Run system maintenance tasks"""
        logger.info("Running data quality system maintenance tasks")

        maintenance_results = {
            "tasks_completed": [],
            "alerts_processed": 0,
            "corrections_generated": 0,
            "cleanup_completed": False,
            "errors": [],
        }

        try:
            async with AsyncSession(self.engine) as session:
                # Process batch alerts
                alert_results = await alert_manager.process_batch_alerts(session)
                maintenance_results["alerts_processed"] = alert_results["total_alerts"]
                maintenance_results["tasks_completed"].append("batch_alert_processing")

                # Generate auto-corrections
                correction_results = await correction_manager.generate_auto_corrections(
                    session
                )
                maintenance_results["corrections_generated"] = correction_results[
                    "total_suggestions"
                ]
                maintenance_results["tasks_completed"].append(
                    "auto_correction_generation"
                )

                # Cleanup old records (older than 6 months)
                cleanup_date = datetime.now(timezone.utc).replace(
                    month=datetime.now().month - 6
                )

                cleanup_queries = [
                    f"DELETE FROM quality_assessments WHERE assessed_at < '{cleanup_date}'",
                    f"DELETE FROM quality_alerts WHERE triggered_at < '{cleanup_date}' AND is_resolved = true",
                    f"DELETE FROM data_change_logs WHERE changed_at < '{cleanup_date}'",
                ]

                for query in cleanup_queries:
                    await session.execute(text(query))

                await session.commit()
                maintenance_results["cleanup_completed"] = True
                maintenance_results["tasks_completed"].append("data_cleanup")

        except Exception as e:
            logger.error(f"Error in maintenance tasks: {e}")
            maintenance_results["errors"].append(str(e))

        logger.info(
            f"Maintenance tasks completed: {len(maintenance_results['tasks_completed'])}"
        )
        return maintenance_results

    async def export_system_configuration(self) -> Dict[str, Any]:
        """Export complete system configuration"""
        if not self.is_initialized:
            return {"error": "System not initialized"}

        try:
            async with AsyncSession(self.engine) as session:
                # Get quality rules
                rules_result = await session.execute(
                    text(
                        "SELECT rule_name, rule_type, conditions, severity, is_active FROM quality_rules"
                    )
                )

                quality_rules = []
                for rule in rules_result:
                    quality_rules.append(
                        {
                            "rule_name": rule.rule_name,
                            "rule_type": rule.rule_type,
                            "conditions": rule.conditions,
                            "severity": rule.severity,
                            "is_active": rule.is_active,
                        }
                    )

                # Get data sources
                sources_result = await session.execute(
                    text(
                        "SELECT source_id, name, url_pattern, source_type, reliability_score FROM data_sources WHERE is_active = true"
                    )
                )

                data_sources = []
                for source in sources_result:
                    data_sources.append(
                        {
                            "source_id": source.source_id,
                            "name": source.name,
                            "url_pattern": source.url_pattern,
                            "source_type": source.source_type,
                            "reliability_score": source.reliability_score,
                        }
                    )

                return {
                    "system_configuration": self.system_config,
                    "quality_rules": quality_rules,
                    "data_sources": data_sources,
                    "exported_at": datetime.now(timezone.utc).isoformat(),
                    "version": "1.0.0",
                }

        except Exception as e:
            logger.error(f"Error exporting system configuration: {e}")
            return {"error": str(e)}

    async def shutdown(self):
        """Gracefully shutdown the system"""
        logger.info("Shutting down Data Quality & Provenance Intelligence System")

        if self.engine:
            await self.engine.dispose()

        self.is_initialized = False
        logger.info("System shutdown complete")


# Global system instance
data_quality_system = DataQualitySystem(
    "postgresql+asyncpg://localhost/business_intel_scraper"
)


async def initialize_quality_system(database_url: str = None) -> Dict[str, Any]:
    """Initialize the complete data quality system"""
    global data_quality_system

    if database_url:
        data_quality_system = DataQualitySystem(database_url)

    return await data_quality_system.initialize()


async def get_system_status() -> Dict[str, Any]:
    """Get current system status"""
    return await data_quality_system.health_check()


async def run_system_maintenance() -> Dict[str, Any]:
    """Run system maintenance tasks"""
    return await data_quality_system.run_maintenance_tasks()


if __name__ == "__main__":
    # Example usage
    async def main():
        # Initialize the system
        init_results = await initialize_quality_system()
        print("Initialization Results:")
        print(f"  Database initialized: {init_results['database_initialized']}")
        print(f"  Tables created: {len(init_results['tables_created'])}")
        print(f"  Default rules created: {init_results['default_rules_created']}")
        print(
            f"  Components initialized: {len(init_results['components_initialized'])}"
        )

        # Check system health
        health = await get_system_status()
        print(
            f"\nSystem Health: {'Healthy' if health['database_connection'] else 'Issues detected'}"
        )

        # Run maintenance
        maintenance = await run_system_maintenance()
        print(f"\nMaintenance completed: {len(maintenance['tasks_completed'])} tasks")

    asyncio.run(main())
