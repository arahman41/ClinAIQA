"""Add audit_records table for persisted API audit verdicts.

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-29
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("doc_type", sa.Text(), nullable=False),
        sa.Column("output_text", sa.Text(), nullable=False),
        sa.Column("source_record", postgresql.JSONB(), nullable=False),
        sa.Column("verdict", sa.Text(), nullable=False),
        sa.Column("flags", postgresql.JSONB(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_records")
