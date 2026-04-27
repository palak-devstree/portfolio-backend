"""add description_points and about headings

Revision ID: 007
Revises: 006
Create Date: 2026-04-27 13:30:00.000000

Adds:
  - description_points (ARRAY) to education and experience tables
  - heading_learning, heading_building, heading_exploring to profile table
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add description_points to education table
    op.add_column(
        "education",
        sa.Column("description_points", ARRAY(sa.String()), nullable=False, server_default="{}"),
    )
    
    # Add description_points to experience table
    op.add_column(
        "experience",
        sa.Column("description_points", ARRAY(sa.String()), nullable=False, server_default="{}"),
    )
    
    # Add about section headings to profile table
    op.add_column(
        "profile",
        sa.Column("heading_learning", sa.String(255), nullable=True, server_default="Currently Learning"),
    )
    op.add_column(
        "profile",
        sa.Column("heading_building", sa.String(255), nullable=True, server_default="Currently Building"),
    )
    op.add_column(
        "profile",
        sa.Column("heading_exploring", sa.String(255), nullable=True, server_default="Currently Exploring"),
    )
    
    # Back-fill existing rows with defaults
    op.execute("UPDATE profile SET heading_learning = 'Currently Learning' WHERE heading_learning IS NULL")
    op.execute("UPDATE profile SET heading_building = 'Currently Building' WHERE heading_building IS NULL")
    op.execute("UPDATE profile SET heading_exploring = 'Currently Exploring' WHERE heading_exploring IS NULL")


def downgrade() -> None:
    # Drop about section headings from profile
    op.drop_column("profile", "heading_exploring")
    op.drop_column("profile", "heading_building")
    op.drop_column("profile", "heading_learning")
    
    # Drop description_points from experience
    op.drop_column("experience", "description_points")
    
    # Drop description_points from education
    op.drop_column("education", "description_points")
