"""add site copy fields to profile

Revision ID: 005
Revises: 004
Create Date: 2026-04-27 12:00:00.000000

Adds customisable site-copy columns to the profile table:
  - navbar_brand          (e.g. "palak.ops")
  - hero_badge            (e.g. "AI · Backend · Infra")
  - hero_cluster_label    (e.g. "inference.cluster.us-west-2")
  - subtitle_projects     (e.g. "backend systems, APIs, infrastructure")
  - subtitle_writing      (e.g. "long-form notes on systems & engineering")
  - subtitle_designs      (e.g. "architectures for real-world scale")
  - subtitle_lab          (e.g. "experiments, benchmarks & research")
  - subtitle_about        (e.g. "background, focus, stack")
  - subtitle_contact      (e.g. "open inbox / fast reply")
  - contact_response_note (e.g. "responses usually within 72h")
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_DEFAULTS = {
    "navbar_brand": "",          # empty → derived from full_name on frontend
    "hero_badge": "AI · Backend · Infra",
    "hero_cluster_label": "inference.cluster.us-west-2",
    "subtitle_projects": "backend systems, APIs, infrastructure",
    "subtitle_writing": "long-form notes on systems & engineering",
    "subtitle_designs": "architectures for real-world scale",
    "subtitle_lab": "experiments, benchmarks & research",
    "subtitle_about": "background, focus, stack",
    "subtitle_contact": "open inbox / fast reply",
    "contact_response_note": "responses usually within 72h",
}


def upgrade() -> None:
    for col, default in _DEFAULTS.items():
        op.add_column(
            "profile",
            sa.Column(col, sa.String(255), nullable=True, server_default=default),
        )
    # Back-fill existing rows with the defaults
    for col, default in _DEFAULTS.items():
        op.execute(f"UPDATE profile SET {col} = '{default}' WHERE {col} IS NULL OR {col} = ''")


def downgrade() -> None:
    for col in _DEFAULTS:
        op.drop_column("profile", col)
