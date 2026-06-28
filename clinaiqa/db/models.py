from pgvector.sqlalchemy import Vector
from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ReferenceEmbedding(Base):
    """One chunk of a reference document, with its embedding for Layer 1 retrieval."""

    __tablename__ = "reference_embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doc_id: Mapped[str] = mapped_column(Text, nullable=False)
    doc_type: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=False)


class HealthyExample(Base):
    """A synthetic example of correct, grounded healthcare LLM output."""

    __tablename__ = "healthy_examples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doc_type: Mapped[str] = mapped_column(Text, nullable=False)
    source_record: Mapped[dict] = mapped_column(JSONB, nullable=False)
    output_text: Mapped[str] = mapped_column(Text, nullable=False)


class AdversarialExample(Base):
    """A healthy example with one injected defect. Split into tuning vs heldout sets."""

    __tablename__ = "adversarial_examples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    healthy_example_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("healthy_examples.id"), nullable=False
    )
    output_text: Mapped[str] = mapped_column(Text, nullable=False)
    archetype: Mapped[str] = mapped_column(Text, nullable=False)
    defect_span: Mapped[str] = mapped_column(Text, nullable=False)
    expected_flag_type: Mapped[str] = mapped_column(Text, nullable=False)
    split_assignment: Mapped[str] = mapped_column(Text, nullable=False)
    split_seed: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)

    # The parent healthy example. Layer 2 scoring needs its structured source_record
    # to check the adversarial output against the ground-truth facts.
    healthy_example: Mapped["HealthyExample"] = relationship()
