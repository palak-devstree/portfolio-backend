"""add image_url to education and experience

Revision ID: 009
Revises: 008
Create Date: 2026-04-28 10:00:00.000000

Adds image_url field to education and experience tables for logos/images.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add image_url to education table
    op.add_column(
        "education",
        sa.Column("image_url", sa.String(500), nullable=True),
    )
    
    # Add image_url to experience table
    op.add_column(
        "experience",
        sa.Column("image_url", sa.String(500), nullable=True),
    )


def downgrade() -> None:
    # Drop image_url from experience
    op.drop_column("experience", "image_url")
    
    # Drop image_url from education
    op.drop_column("education", "image_url")
