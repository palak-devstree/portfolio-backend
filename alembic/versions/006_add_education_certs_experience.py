"""add education certificates experience tables

Revision ID: 006
Revises: 005
Create Date: 2026-04-27 13:00:00.000000

Adds three new tables for professional background:
  - education: academic qualifications
  - certificates: professional certifications
  - experience: work history

Also adds visibility flags to profile:
  - show_education (default True)
  - show_certificates (default True)
  - show_experience (default True)
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create education table
    op.create_table(
        "education",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("institution", sa.String(255), nullable=False),
        sa.Column("degree", sa.String(255), nullable=False),
        sa.Column("field_of_study", sa.String(255), nullable=True),
        sa.Column("start_date", sa.String(50), nullable=True),
        sa.Column("end_date", sa.String(50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_education_id"), "education", ["id"], unique=False)

    # Create certificates table
    op.create_table(
        "certificates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("issuer", sa.String(255), nullable=False),
        sa.Column("issue_date", sa.String(50), nullable=True),
        sa.Column("expiry_date", sa.String(50), nullable=True),
        sa.Column("credential_id", sa.String(255), nullable=True),
        sa.Column("credential_url", sa.String(500), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_certificates_id"), "certificates", ["id"], unique=False)

    # Create experience table
    op.create_table(
        "experience",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("position", sa.String(255), nullable=False),
        sa.Column("company_url", sa.String(500), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("start_date", sa.String(50), nullable=True),
        sa.Column("end_date", sa.String(50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("technologies", ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("project_urls", ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_experience_id"), "experience", ["id"], unique=False)

    # Add visibility flags to profile table
    op.add_column(
        "profile",
        sa.Column("show_education", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.add_column(
        "profile",
        sa.Column("show_certificates", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.add_column(
        "profile",
        sa.Column("show_experience", sa.Boolean(), nullable=False, server_default="true"),
    )


def downgrade() -> None:
    # Drop visibility flags from profile
    op.drop_column("profile", "show_experience")
    op.drop_column("profile", "show_certificates")
    op.drop_column("profile", "show_education")

    # Drop tables
    op.drop_index(op.f("ix_experience_id"), table_name="experience")
    op.drop_table("experience")
    op.drop_index(op.f("ix_certificates_id"), table_name="certificates")
    op.drop_table("certificates")
    op.drop_index(op.f("ix_education_id"), table_name="education")
    op.drop_table("education")
