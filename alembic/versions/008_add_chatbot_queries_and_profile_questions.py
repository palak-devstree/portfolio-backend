"""Add chatbot_queries table and profile chatbot_default_questions

Revision ID: 008
Revises: 007
Create Date: 2026-04-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create chatbot_queries table
    op.create_table(
        'chatbot_queries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('response', sa.Text(), nullable=False),
        sa.Column('intent', sa.String(length=100), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chatbot_queries_id'), 'chatbot_queries', ['id'], unique=False)
    op.create_index(op.f('ix_chatbot_queries_session_id'), 'chatbot_queries', ['session_id'], unique=False)
    op.create_index(op.f('ix_chatbot_queries_created_at'), 'chatbot_queries', ['created_at'], unique=False)

    # Add chatbot_default_questions to profile table
    op.add_column(
        'profile',
        sa.Column(
            'chatbot_default_questions',
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default=sa.text("ARRAY['What projects have you built?', 'What are your core skills?', 'Tell me about your experience']")
        )
    )


def downgrade() -> None:
    # Remove chatbot_default_questions from profile
    op.drop_column('profile', 'chatbot_default_questions')

    # Drop chatbot_queries table
    op.drop_index(op.f('ix_chatbot_queries_created_at'), table_name='chatbot_queries')
    op.drop_index(op.f('ix_chatbot_queries_session_id'), table_name='chatbot_queries')
    op.drop_index(op.f('ix_chatbot_queries_id'), table_name='chatbot_queries')
    op.drop_table('chatbot_queries')
