"""initial_schema

Revision ID: 001
Revises: 
Create Date: 2026-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums using DO blocks (PostgreSQL doesn't support IF NOT EXISTS for CREATE TYPE)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE projectstatus AS ENUM ('building', 'done', 'planned', 'exploring');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE experimentstatus AS ENUM ('experimenting', 'testing', 'completed');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # projects table
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("stack", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM('building', 'done', 'planned', 'exploring', name='projectstatus', create_type=False),
            nullable=False,
        ),
        sa.Column("github_url", sa.String(500), nullable=True),
        sa.Column("details_url", sa.String(500), nullable=True),
        sa.Column("github_stars", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("github_forks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_commit_date", sa.DateTime(), nullable=True),
        sa.Column("featured", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_projects_id", "projects", ["id"])
    op.create_index("ix_projects_name", "projects", ["name"])

    # blog_posts table
    op.create_table(
        "blog_posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("slug", sa.String(500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("preview", sa.Text(), nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("published_date", sa.DateTime(), nullable=False),
        sa.Column("updated_date", sa.DateTime(), nullable=True),
        sa.Column("read_time_minutes", sa.Integer(), nullable=False),
        sa.Column("views_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("meta_description", sa.String(160), nullable=True),
        sa.Column("meta_keywords", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_blog_posts_id", "blog_posts", ["id"])
    op.create_index("ix_blog_posts_slug", "blog_posts", ["slug"])

    # system_designs table
    op.create_table(
        "system_designs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("stack", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("notes", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("diagram_url", sa.String(500), nullable=True),
        sa.Column("diagram_type", sa.String(50), nullable=True),
        sa.Column("complexity_level", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_system_designs_id", "system_designs", ["id"])

    # lab_experiments table
    op.create_table(
        "lab_experiments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("stack", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM('experimenting', 'testing', 'completed', name='experimentstatus', create_type=False),
            nullable=False,
        ),
        sa.Column("findings", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lab_experiments_id", "lab_experiments", ["id"])

    # analytics table
    op.create_table(
        "analytics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=True),
        sa.Column("resource_id", sa.Integer(), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("event_metadata", sa.JSON(), nullable=True),  # Renamed from 'metadata'
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analytics_id", "analytics", ["id"])
    op.create_index("ix_analytics_event_type", "analytics", ["event_type"])
    op.create_index("ix_analytics_timestamp", "analytics", ["timestamp"])
    op.create_index("ix_analytics_resource", "analytics", ["resource_type", "resource_id"])

    # dashboard_metrics table
    op.create_table(
        "dashboard_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("projects_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("blog_posts_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("system_designs_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lab_experiments_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_views", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("api_requests_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("uptime_percentage", sa.Float(), nullable=False, server_default="100.0"),
        sa.Column("avg_response_time_ms", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date"),
    )
    op.create_index("ix_dashboard_metrics_id", "dashboard_metrics", ["id"])
    op.create_index("ix_dashboard_metrics_date", "dashboard_metrics", ["date"])


def downgrade() -> None:
    op.drop_table("dashboard_metrics")
    op.drop_table("analytics")
    op.drop_table("lab_experiments")
    op.drop_table("system_designs")
    op.drop_table("blog_posts")
    op.drop_table("projects")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS projectstatus")
    op.execute("DROP TYPE IF EXISTS experimentstatus")
