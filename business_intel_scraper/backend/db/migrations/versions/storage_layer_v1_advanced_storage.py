"""Advanced Storage Layer Migration

Revision ID: storage_layer_v1
Revises: d4769d349be9
Create Date: 2025-07-19 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "storage_layer_v1"
down_revision: Union[str, Sequence[str], None] = "d4769d349be9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create advanced storage layer tables."""

    # Raw Data table
    op.create_table(
        "raw_data",
        sa.Column("raw_id", sa.String(), primary_key=True),
        sa.Column("content_hash", sa.String(64), nullable=False, index=True),
        sa.Column("source_url", sa.String(), nullable=False, index=True),
        sa.Column("referrer_url", sa.String()),
        sa.Column("source_domain", sa.String(), nullable=False, index=True),
        sa.Column(
            "fetched_at",
            sa.DateTime(),
            nullable=False,
            index=True,
            server_default=sa.func.now(),
        ),
        sa.Column("page_last_modified", sa.DateTime()),
        sa.Column("job_id", sa.String(), nullable=False, index=True),
        sa.Column("spider_name", sa.String(), index=True),
        sa.Column("crawl_depth", sa.Integer(), default=0),
        sa.Column("http_status", sa.Integer(), index=True),
        sa.Column("content_type", sa.String()),
        sa.Column("content_encoding", sa.String()),
        sa.Column("response_time_ms", sa.Integer()),
        sa.Column("storage_backend", sa.String(), nullable=False, default="s3"),
        sa.Column("storage_bucket", sa.String(), nullable=False),
        sa.Column("storage_key", sa.String(), nullable=False),
        sa.Column("content_size_bytes", sa.Integer()),
        sa.Column("is_compressed", sa.Boolean(), default=False),
        sa.Column("request_headers", JSONB()),
        sa.Column("response_headers", JSONB()),
        sa.Column("language", sa.String()),
        sa.Column("charset", sa.String()),
        sa.Column("page_title", sa.String()),
        sa.Column("processing_status", sa.String(), default="pending", index=True),
        sa.Column("extraction_attempted", sa.Boolean(), default=False),
        sa.Column("extraction_successful", sa.Boolean(), default=False),
        sa.Column("extraction_error", sa.Text()),
        sa.Column("content_quality_score", sa.Float()),
        sa.Column("is_duplicate", sa.Boolean(), default=False, index=True),
        sa.Column("similarity_hash", sa.String()),
        sa.Column("attachments", JSONB()),
        sa.Column("linked_resources", JSONB()),
        sa.Column("metadata", JSONB()),
        sa.Column("tags", JSONB()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # Create indexes for raw_data table
    op.create_index("idx_raw_data_job_status", "raw_data", ["job_id", "http_status"])
    op.create_index("idx_raw_data_content_hash", "raw_data", ["content_hash"])
    op.create_index(
        "idx_raw_data_domain_date", "raw_data", ["source_domain", "fetched_at"]
    )
    op.create_index(
        "idx_raw_data_processing",
        "raw_data",
        ["processing_status", "extraction_attempted"],
    )
    op.create_index(
        "idx_raw_data_quality", "raw_data", ["content_quality_score", "is_duplicate"]
    )

    # Structured Entities table
    op.create_table(
        "structured_entities",
        sa.Column("entity_id", sa.String(), primary_key=True),
        sa.Column("entity_type", sa.String(), nullable=False, index=True),
        sa.Column("canonical_name", sa.String(), index=True),
        sa.Column("display_name", sa.String()),
        sa.Column("description", sa.Text()),
        sa.Column("category", sa.String(), index=True),
        sa.Column("subcategory", sa.String(), index=True),
        sa.Column("confidence_score", sa.Float(), index=True),
        sa.Column("importance_score", sa.Float(), index=True),
        sa.Column(
            "extracted_at",
            sa.DateTime(),
            nullable=False,
            index=True,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.Column("first_seen_at", sa.DateTime()),
        sa.Column("last_verified_at", sa.DateTime()),
        sa.Column("extractor_name", sa.String(), nullable=False),
        sa.Column("extractor_version", sa.String(), nullable=False),
        sa.Column("extraction_method", sa.String()),
        sa.Column("structured_data", JSONB(), nullable=False),
        sa.Column("contact_info", JSONB()),
        sa.Column("locations", JSONB()),
        sa.Column("industry_codes", JSONB()),
        sa.Column("business_identifiers", JSONB()),
        sa.Column("financial_data", JSONB()),
        sa.Column("verification_status", sa.String(), default="unverified", index=True),
        sa.Column("verification_source", sa.String()),
        sa.Column("data_quality_score", sa.Float(), index=True),
        sa.Column("completeness_score", sa.Float()),
        sa.Column("primary_source_url", sa.String()),
        sa.Column("source_count", sa.Integer(), default=1),
        sa.Column("metadata", JSONB()),
        sa.Column("tags", JSONB()),
        sa.Column("is_active", sa.Boolean(), default=True, index=True),
        sa.Column("is_verified", sa.Boolean(), default=False, index=True),
        sa.Column("needs_review", sa.Boolean(), default=False, index=True),
    )

    # Create indexes for structured_entities table
    op.create_index(
        "idx_entity_type_name", "structured_entities", ["entity_type", "canonical_name"]
    )
    op.create_index(
        "idx_entity_confidence",
        "structured_entities",
        ["entity_type", "confidence_score"],
    )
    op.create_index(
        "idx_entity_category", "structured_entities", ["category", "subcategory"]
    )
    op.create_index(
        "idx_entity_status", "structured_entities", ["is_active", "verification_status"]
    )
    op.create_index(
        "idx_entity_quality",
        "structured_entities",
        ["data_quality_score", "completeness_score"],
    )
    op.create_index(
        "idx_entity_temporal",
        "structured_entities",
        ["first_seen_at", "last_verified_at"],
    )

    # Raw to Structured Mapping table
    op.create_table(
        "raw_to_structured_mapping",
        sa.Column("mapping_id", sa.String(), primary_key=True),
        sa.Column(
            "raw_id",
            sa.String(),
            sa.ForeignKey("raw_data.raw_id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "entity_id",
            sa.String(),
            sa.ForeignKey("structured_entities.entity_id"),
            nullable=False,
            index=True,
        ),
        sa.Column("extraction_method", sa.String(), nullable=False),
        sa.Column("extraction_confidence", sa.Float(), nullable=False),
        sa.Column("extracted_fields", JSONB()),
        sa.Column("extraction_context", JSONB()),
        sa.Column("field_quality_scores", JSONB()),
        sa.Column("validation_results", JSONB()),
        sa.Column("extraction_errors", JSONB()),
        sa.Column("extractor_name", sa.String(), nullable=False),
        sa.Column("extractor_version", sa.String(), nullable=False),
        sa.Column("processing_time_ms", sa.Integer()),
        sa.Column("contribution_weight", sa.Float(), default=1.0),
        sa.Column("is_primary_source", sa.Boolean(), default=False, index=True),
        sa.Column("field_contributions", JSONB()),
        sa.Column(
            "extracted_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("last_validated", sa.DateTime()),
        sa.Column("status", sa.String(), default="active", index=True),
        sa.Column("extraction_notes", sa.Text()),
        sa.Column("reviewer_notes", sa.Text()),
    )

    # Create indexes and constraints for mapping table
    op.create_index(
        "idx_mapping_raw_entity", "raw_to_structured_mapping", ["raw_id", "entity_id"]
    )
    op.create_index(
        "idx_mapping_entity_confidence",
        "raw_to_structured_mapping",
        ["entity_id", "extraction_confidence"],
    )
    op.create_index(
        "idx_mapping_method",
        "raw_to_structured_mapping",
        ["extraction_method", "extractor_name"],
    )

    # Add unique constraint
    op.create_unique_constraint(
        "uq_raw_entity_extractor",
        "raw_to_structured_mapping",
        ["raw_id", "entity_id", "extractor_name"],
    )

    # Entity Relationships table
    op.create_table(
        "entity_relationships",
        sa.Column("relationship_id", sa.String(), primary_key=True),
        sa.Column(
            "source_entity_id",
            sa.String(),
            sa.ForeignKey("structured_entities.entity_id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "target_entity_id",
            sa.String(),
            sa.ForeignKey("structured_entities.entity_id"),
            nullable=False,
            index=True,
        ),
        sa.Column("relationship_type", sa.String(), nullable=False, index=True),
        sa.Column("relationship_subtype", sa.String(), index=True),
        sa.Column("strength", sa.Float(), default=1.0, index=True),
        sa.Column("confidence", sa.Float(), nullable=False, index=True),
        sa.Column("is_directional", sa.Boolean(), default=True),
        sa.Column("semantic_role", sa.String()),
        sa.Column("evidence_sources", JSONB()),
        sa.Column("extraction_method", sa.String(), nullable=False),
        sa.Column("supporting_text", JSONB()),
        sa.Column("relationship_start_date", sa.DateTime()),
        sa.Column("relationship_end_date", sa.DateTime()),
        sa.Column(
            "extracted_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("last_verified", sa.DateTime()),
        sa.Column("verification_status", sa.String(), default="unverified", index=True),
        sa.Column("quality_score", sa.Float(), index=True),
        sa.Column("validation_notes", sa.Text()),
        sa.Column("extractor_name", sa.String(), nullable=False),
        sa.Column("extractor_version", sa.String(), nullable=False),
        sa.Column("attributes", JSONB()),
        sa.Column("metadata", JSONB()),
        sa.Column("is_active", sa.Boolean(), default=True, index=True),
        sa.Column("needs_review", sa.Boolean(), default=False, index=True),
    )

    # Create indexes and constraints for relationships table
    op.create_index(
        "idx_rel_source_target",
        "entity_relationships",
        ["source_entity_id", "target_entity_id"],
    )
    op.create_index(
        "idx_rel_type",
        "entity_relationships",
        ["relationship_type", "relationship_subtype"],
    )
    op.create_index(
        "idx_rel_strength", "entity_relationships", ["strength", "confidence"]
    )
    op.create_index(
        "idx_rel_temporal",
        "entity_relationships",
        ["relationship_start_date", "relationship_end_date"],
    )

    # Add check constraints for relationships
    op.create_check_constraint(
        "ck_strength_range", "entity_relationships", "strength >= 0 AND strength <= 1"
    )
    op.create_check_constraint(
        "ck_confidence_range",
        "entity_relationships",
        "confidence >= 0 AND confidence <= 1",
    )

    # Data Quality Metrics table
    op.create_table(
        "data_quality_metrics",
        sa.Column("metric_id", sa.String(), primary_key=True),
        sa.Column("scope_type", sa.String(), nullable=False, index=True),
        sa.Column("scope_id", sa.String(), index=True),
        sa.Column(
            "entity_id",
            sa.String(),
            sa.ForeignKey("structured_entities.entity_id"),
            index=True,
        ),
        sa.Column("metric_type", sa.String(), nullable=False, index=True),
        sa.Column("metric_name", sa.String(), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("metric_threshold", sa.Float()),
        sa.Column("score", sa.Float(), index=True),
        sa.Column("grade", sa.String(), index=True),
        sa.Column("passes_threshold", sa.Boolean(), index=True),
        sa.Column("calculation_method", sa.String(), nullable=False),
        sa.Column("sample_size", sa.Integer()),
        sa.Column("calculation_params", JSONB()),
        sa.Column(
            "measurement_date",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("measurement_period_start", sa.DateTime()),
        sa.Column("measurement_period_end", sa.DateTime()),
        sa.Column("previous_value", sa.Float()),
        sa.Column("trend", sa.String(), index=True),
        sa.Column("trend_confidence", sa.Float()),
        sa.Column("issues_identified", JSONB()),
        sa.Column("recommendations", JSONB()),
        sa.Column("calculated_by", sa.String(), nullable=False),
        sa.Column("calculation_version", sa.String(), nullable=False),
        sa.Column("metadata", JSONB()),
        sa.Column("tags", JSONB()),
    )

    # Create indexes for quality metrics table
    op.create_index(
        "idx_quality_scope", "data_quality_metrics", ["scope_type", "scope_id"]
    )
    op.create_index(
        "idx_quality_metric", "data_quality_metrics", ["metric_type", "metric_name"]
    )
    op.create_index("idx_quality_score", "data_quality_metrics", ["score", "grade"])
    op.create_index(
        "idx_quality_temporal",
        "data_quality_metrics",
        ["measurement_date", "scope_type"],
    )
    op.create_index(
        "idx_quality_trend", "data_quality_metrics", ["trend", "passes_threshold"]
    )

    # Data Lineage table
    op.create_table(
        "data_lineage",
        sa.Column("lineage_id", sa.String(), primary_key=True),
        sa.Column("source_type", sa.String(), nullable=False, index=True),
        sa.Column("source_id", sa.String(), nullable=False, index=True),
        sa.Column("target_type", sa.String(), nullable=False, index=True),
        sa.Column("target_id", sa.String(), nullable=False, index=True),
        sa.Column("transformation_type", sa.String(), nullable=False, index=True),
        sa.Column("transformation_name", sa.String(), nullable=False),
        sa.Column("transformation_version", sa.String(), nullable=False),
        sa.Column("lineage_path", JSONB()),
        sa.Column("direct_dependencies", JSONB()),
        sa.Column("dependency_count", sa.Integer(), index=True),
        sa.Column("path_length", sa.Integer(), index=True),
        sa.Column("transformation_params", JSONB()),
        sa.Column("input_schema", JSONB()),
        sa.Column("output_schema", JSONB()),
        sa.Column("transformation_confidence", sa.Float(), index=True),
        sa.Column("data_quality_impact", sa.Float()),
        sa.Column("validation_results", JSONB()),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("transformation_timestamp", sa.DateTime(), nullable=False),
        sa.Column("last_verified", sa.DateTime()),
        sa.Column("processing_job_id", sa.String(), index=True),
        sa.Column("processing_duration_ms", sa.Integer()),
        sa.Column("resource_usage", JSONB()),
        sa.Column("downstream_entities", JSONB()),
        sa.Column("impact_score", sa.Float(), index=True),
        sa.Column("is_active", sa.Boolean(), default=True, index=True),
        sa.Column("needs_refresh", sa.Boolean(), default=False, index=True),
        sa.Column("last_refresh_attempt", sa.DateTime()),
        sa.Column("metadata", JSONB()),
    )

    # Create indexes for lineage table
    op.create_index("idx_lineage_source", "data_lineage", ["source_type", "source_id"])
    op.create_index("idx_lineage_target", "data_lineage", ["target_type", "target_id"])
    op.create_index(
        "idx_lineage_transformation",
        "data_lineage",
        ["transformation_type", "transformation_name"],
    )
    op.create_index(
        "idx_lineage_path", "data_lineage", ["path_length", "dependency_count"]
    )
    op.create_index(
        "idx_lineage_quality",
        "data_lineage",
        ["transformation_confidence", "data_quality_impact"],
    )

    # Storage Metrics table
    op.create_table(
        "storage_metrics",
        sa.Column("metric_id", sa.String(), primary_key=True),
        sa.Column("metric_category", sa.String(), nullable=False, index=True),
        sa.Column("metric_name", sa.String(), nullable=False, index=True),
        sa.Column("metric_description", sa.Text()),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("metric_unit", sa.String()),
        sa.Column("scope", sa.String(), index=True),
        sa.Column("scope_id", sa.String(), index=True),
        sa.Column(
            "measured_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            index=True,
        ),
        sa.Column("measurement_period", sa.String()),
        sa.Column("aggregation_method", sa.String()),
        sa.Column("sample_count", sa.Integer()),
        sa.Column("trend_direction", sa.String(), index=True),
        sa.Column("change_rate", sa.Float()),
        sa.Column("threshold_warning", sa.Float()),
        sa.Column("threshold_critical", sa.Float()),
        sa.Column("alert_level", sa.String(), index=True),
        sa.Column("metadata", JSONB()),
    )

    # Create indexes for storage metrics table
    op.create_index(
        "idx_storage_metrics_category",
        "storage_metrics",
        ["metric_category", "metric_name"],
    )
    op.create_index(
        "idx_storage_metrics_temporal",
        "storage_metrics",
        ["measured_at", "measurement_period"],
    )
    op.create_index(
        "idx_storage_metrics_scope", "storage_metrics", ["scope", "scope_id"]
    )
    op.create_index(
        "idx_storage_metrics_alerts", "storage_metrics", ["alert_level", "measured_at"]
    )


def downgrade() -> None:
    """Drop advanced storage layer tables."""

    # Drop tables in reverse order to handle foreign key constraints
    op.drop_table("storage_metrics")
    op.drop_table("data_lineage")
    op.drop_table("data_quality_metrics")
    op.drop_table("entity_relationships")
    op.drop_table("raw_to_structured_mapping")
    op.drop_table("structured_entities")
    op.drop_table("raw_data")
