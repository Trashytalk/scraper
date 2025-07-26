"""
Migration: Add Centralized Data Management Tables

Creates tables for centralized data storage, analytics, and deduplication
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "003_centralized_data"
down_revision = "002_initial_tables"
branch_labels = None
depends_on = None


def upgrade():
    """Add centralized data management tables"""

    # Create centralized_data table
    op.create_table(
        "centralized_data",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("record_uuid", sa.String(36), unique=True, index=True),
        # Source tracking
        sa.Column("source_job_id", sa.Integer(), index=True),
        sa.Column("source_job_name", sa.String(255), index=True),
        sa.Column("source_job_type", sa.String(50), index=True),
        sa.Column("source_url", sa.String(2048), index=True),
        # Data content
        sa.Column("raw_data", sa.JSON()),
        sa.Column("processed_data", sa.JSON()),
        # Metadata
        sa.Column("data_type", sa.String(50), index=True),
        sa.Column("content_hash", sa.String(64), index=True),
        # Timestamps
        sa.Column("scraped_at", sa.DateTime(), index=True),
        sa.Column("centralized_at", sa.DateTime(), index=True),
        sa.Column("last_updated", sa.DateTime()),
        # Quality metrics
        sa.Column("data_quality_score", sa.Integer(), default=0),
        sa.Column("completeness_score", sa.Integer(), default=0),
        sa.Column("validation_status", sa.String(20), default="pending"),
        # Analytics fields
        sa.Column("word_count", sa.Integer(), default=0),
        sa.Column("link_count", sa.Integer(), default=0),
        sa.Column("image_count", sa.Integer(), default=0),
    )

    # Create indexes for centralized_data
    op.create_index(
        "idx_source_job", "centralized_data", ["source_job_id", "source_job_type"]
    )
    op.create_index(
        "idx_data_type_time", "centralized_data", ["data_type", "scraped_at"]
    )
    op.create_index(
        "idx_quality_time", "centralized_data", ["data_quality_score", "centralized_at"]
    )
    op.create_index("idx_content_hash", "centralized_data", ["content_hash"])

    # Create data_analytics table
    op.create_table(
        "data_analytics",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        # Time period
        sa.Column("date", sa.DateTime(), index=True),
        sa.Column("period_type", sa.String(20), index=True),
        # Aggregated metrics
        sa.Column("total_records", sa.Integer(), default=0),
        sa.Column("total_jobs", sa.Integer(), default=0),
        sa.Column("unique_sources", sa.Integer(), default=0),
        sa.Column("avg_quality_score", sa.Integer(), default=0),
        # Data type breakdown
        sa.Column("news_records", sa.Integer(), default=0),
        sa.Column("ecommerce_records", sa.Integer(), default=0),
        sa.Column("social_media_records", sa.Integer(), default=0),
        sa.Column("other_records", sa.Integer(), default=0),
        # Performance metrics
        sa.Column("avg_processing_time", sa.Integer(), default=0),
        sa.Column("success_rate", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
    )

    # Create data_deduplication table
    op.create_table(
        "data_deduplication",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("content_hash", sa.String(64), index=True),
        sa.Column("canonical_record_id", sa.Integer()),
        sa.Column("duplicate_record_ids", sa.JSON()),
        sa.Column("similarity_score", sa.Integer(), default=0),
        sa.Column("dedup_method", sa.String(50)),
        sa.Column("created_at", sa.DateTime()),
    )

    # Add foreign key constraint
    op.create_foreign_key(
        "fk_canonical_record",
        "data_deduplication",
        "centralized_data",
        ["canonical_record_id"],
        ["id"],
    )


def downgrade():
    """Remove centralized data management tables"""

    # Drop foreign key constraint first
    op.drop_constraint("fk_canonical_record", "data_deduplication", type_="foreignkey")

    # Drop tables
    op.drop_table("data_deduplication")
    op.drop_table("data_analytics")
    op.drop_table("centralized_data")
