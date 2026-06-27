"""Phase 1 schema: replace stub embeddings table with reference_embeddings,
add healthy_examples and adversarial_examples tables.

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-27
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("embeddings")

    op.create_table(
        "reference_embeddings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("doc_id", sa.Text(), nullable=False),
        sa.Column("doc_type", sa.Text(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(384), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reference_embeddings_doc_id", "reference_embeddings", ["doc_id"])

    op.create_table(
        "healthy_examples",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("doc_type", sa.Text(), nullable=False),
        sa.Column("source_record", sa.JSON(), nullable=False),
        sa.Column("output_text", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "adversarial_examples",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("healthy_example_id", sa.Integer(), nullable=False),
        sa.Column("output_text", sa.Text(), nullable=False),
        sa.Column("archetype", sa.Text(), nullable=False),
        sa.Column("defect_span", sa.Text(), nullable=False),
        sa.Column("expected_flag_type", sa.Text(), nullable=False),
        sa.Column("split_assignment", sa.Text(), nullable=False),
        sa.Column("split_seed", sa.Integer(), nullable=False, server_default="42"),
        sa.ForeignKeyConstraint(["healthy_example_id"], ["healthy_examples.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_adversarial_examples_split",
        "adversarial_examples",
        ["split_assignment"],
    )


def downgrade() -> None:
    op.drop_table("adversarial_examples")
    op.drop_table("healthy_examples")
    op.drop_table("reference_embeddings")

    op.create_table(
        "embeddings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
