"""
pgvector store: persist reference document embeddings and retrieve
the top-k most similar passages for a query embedding.
"""

from __future__ import annotations

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from clinaiqa.db.models import ReferenceEmbedding
from clinaiqa.retrieval.embedder import embed
from clinaiqa.settings import settings


def _engine():
    url = settings.database_url_sync
    if not url:
        raise RuntimeError("DATABASE_URL_SYNC is not set.")
    return create_engine(url, echo=False)


def store_reference_chunks(
    chunks: list[dict],
) -> int:
    """
    Persist a list of reference chunks to the reference_embeddings table.
    Each chunk dict must have: doc_id, doc_type, chunk_index, chunk_text.
    Returns the number of rows inserted.
    """
    if not chunks:
        return 0

    texts = [c["chunk_text"] for c in chunks]
    vectors = embed(texts)

    engine = _engine()
    with Session(engine) as session:
        rows = []
        for chunk, vector in zip(chunks, vectors):
            rows.append(
                ReferenceEmbedding(
                    doc_id=chunk["doc_id"],
                    doc_type=chunk["doc_type"],
                    chunk_index=chunk["chunk_index"],
                    chunk_text=chunk["chunk_text"],
                    embedding=vector,
                )
            )
        session.add_all(rows)
        session.commit()
    return len(rows)


def retrieve_top_k(
    query_text: str,
    top_k: int | None = None,
) -> list[dict]:
    """
    Embed query_text and return the top_k most similar reference passages.
    Each result dict has: id, doc_id, doc_type, chunk_text, cosine_similarity.
    """
    top_k = top_k if top_k is not None else settings.retrieval_top_k
    query_vec = embed_query(query_text)
    vec_literal = "[" + ",".join(f"{v:.8f}" for v in query_vec) + "]"

    engine = _engine()
    with Session(engine) as session:
        rows = session.execute(
            text(
                "SELECT id, doc_id, doc_type, chunk_text, "
                "1 - (embedding <=> :vec::vector) AS cosine_similarity "
                "FROM reference_embeddings "
                "ORDER BY embedding <=> :vec::vector "
                "LIMIT :k"
            ),
            {"vec": vec_literal, "k": top_k},
        ).fetchall()

    return [
        {
            "id": r.id,
            "doc_id": r.doc_id,
            "doc_type": r.doc_type,
            "chunk_text": r.chunk_text,
            "cosine_similarity": float(r.cosine_similarity),
        }
        for r in rows
    ]


def embed_query(text: str) -> list[float]:
    from clinaiqa.retrieval.embedder import embed_one
    return embed_one(text)
