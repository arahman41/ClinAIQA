"""
Embed the reference corpus (healthy source records) into pgvector.

Run with: python -m clinaiqa.retrieval.embed_reference_docs
Requires the Docker Compose stack to be up, migrations applied, and seed_db run first.
Safe to re-run: clears existing reference_embeddings before inserting.
"""

import sys

from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session

from clinaiqa.data.generate_healthy import generate_healthy_examples
from clinaiqa.db.models import ReferenceEmbedding
from clinaiqa.retrieval.chunker import chunk_into_sentences
from clinaiqa.retrieval.embedder import embed
from clinaiqa.settings import settings


def build_chunks(healthy_examples) -> list[dict]:
    """Convert healthy source records into embeddable text chunks."""
    chunks: list[dict] = []
    for h in healthy_examples:
        doc_id = h.source_record.get(
            "facility_id",
            h.source_record.get(
                "guideline_id",
                h.source_record.get("patient_id", "unknown"),
            ),
        )
        doc_type = h.doc_type.value
        full_text = h.output_text
        sentences = chunk_into_sentences(full_text)
        for idx, sentence in enumerate(sentences):
            chunks.append(
                {
                    "doc_id": doc_id,
                    "doc_type": doc_type,
                    "chunk_index": idx,
                    "chunk_text": sentence,
                }
            )
    return chunks


def main() -> None:
    url = settings.database_url_sync
    if not url:
        print("ERROR: DATABASE_URL_SYNC is not set.", file=sys.stderr)
        sys.exit(1)

    healthy_examples = generate_healthy_examples()
    chunks = build_chunks(healthy_examples)
    print(f"Built {len(chunks)} chunks from {len(healthy_examples)} healthy examples.")

    if not chunks:
        print("ERROR: no chunks produced; aborting to avoid wiping the reference corpus.", file=sys.stderr)
        sys.exit(1)

    texts = [c["chunk_text"] for c in chunks]
    print(f"Generating embeddings with model '{settings.embedding_model}'...")
    vectors = embed(texts)

    if len(vectors) != len(chunks):
        print(
            f"ERROR: embed() returned {len(vectors)} vectors for {len(chunks)} chunks.",
            file=sys.stderr,
        )
        sys.exit(1)

    engine = create_engine(url, echo=False)
    with Session(engine) as session:
        session.execute(delete(ReferenceEmbedding))

        rows = [
            ReferenceEmbedding(
                doc_id=c["doc_id"],
                doc_type=c["doc_type"],
                chunk_index=c["chunk_index"],
                chunk_text=c["chunk_text"],
                embedding=v,
            )
            for c, v in zip(chunks, vectors)
        ]
        session.add_all(rows)
        session.commit()
        count = session.query(ReferenceEmbedding).count()

    print(f"Stored {count} reference embeddings in pgvector.")


if __name__ == "__main__":
    main()
