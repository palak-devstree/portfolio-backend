"""skills_to_jsonb

Revision ID: 004
Revises: 003
Create Date: 2026-04-27 10:00:00.000000

Migrates the `skills` column from ARRAY(String) to JSONB so that skills can
be stored as a list of {category, skills[]} objects.

Existing flat string arrays are automatically converted to a single
"General" category containing all previous skills.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add a temporary JSONB column
    op.add_column("profile", sa.Column("skills_jsonb", postgresql.JSONB(), nullable=True))

    # Migrate existing flat array data into [{category: "General", skills: [...]}]
    op.execute(
        """
        UPDATE profile
        SET skills_jsonb = jsonb_build_array(
            jsonb_build_object(
                'category', 'General',
                'skills', to_jsonb(skills)
            )
        )
        WHERE skills IS NOT NULL AND array_length(skills, 1) > 0
        """
    )

    # For rows with empty/null skills, set to empty array
    op.execute(
        """
        UPDATE profile
        SET skills_jsonb = '[]'::jsonb
        WHERE skills_jsonb IS NULL
        """
    )

    # Drop old column and rename new one
    op.drop_column("profile", "skills")
    op.alter_column("profile", "skills_jsonb", new_column_name="skills", nullable=False,
                    server_default="'[]'::jsonb")


def downgrade() -> None:
    # Add back the ARRAY column
    op.add_column("profile", sa.Column("skills_arr", postgresql.ARRAY(sa.String()), nullable=True))

    # Flatten all skills from all categories back into a single array
    op.execute(
        """
        UPDATE profile
        SET skills_arr = ARRAY(
            SELECT jsonb_array_elements_text(cat->'skills')
            FROM jsonb_array_elements(skills) AS cat
        )
        """
    )

    op.execute("UPDATE profile SET skills_arr = '{}' WHERE skills_arr IS NULL")

    op.drop_column("profile", "skills")
    op.alter_column("profile", "skills_arr", new_column_name="skills", nullable=False,
                    server_default="'{}'")
