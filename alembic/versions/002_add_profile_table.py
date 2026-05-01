"""add_profile_table

Revision ID: 002
Revises: 001
Create Date: 2026-04-24 13:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # profile table
    op.create_table(
        "profile",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("job_title", sa.String(255), nullable=False),
        sa.Column("tagline", sa.String(500), nullable=False),
        sa.Column("years_of_experience", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("professional_summary", sa.Text(), nullable=False),
        sa.Column("skills", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("resume_url", sa.String(500), nullable=True),
        sa.Column("github_url", sa.String(500), nullable=True),
        sa.Column("linkedin_url", sa.String(500), nullable=True),
        sa.Column("twitter_url", sa.String(500), nullable=True),
        sa.Column("website_url", sa.String(500), nullable=True),
        sa.Column("show_blog", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("show_projects", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("show_system_designs", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("show_lab", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("show_about", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("current_learning", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("current_building", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("current_exploring", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_profile_id", "profile", ["id"])


def downgrade() -> None:
    op.drop_table("profile")
