"""Fix source_record column type from JSON to JSONB and make split_seed nullable.

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "healthy_examples",
        "source_record",
        type_=postgresql.JSONB(),
        postgresql_using="source_record::jsonb",
        existing_nullable=False,
    )

    op.alter_column(
        "adversarial_examples",
        "split_seed",
        existing_type=sa.Integer(),
        nullable=True,
        server_default=None,
    )


def downgrade() -> None:
    op.alter_column(
        "adversarial_examples",
        "split_seed",
        existing_type=sa.Integer(),
        nullable=False,
        server_default="42",
    )

    op.alter_column(
        "healthy_examples",
        "source_record",
        type_=sa.JSON(),
        postgresql_using="source_record::json",
        existing_nullable=False,
    )
