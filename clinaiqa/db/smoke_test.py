"""
Run with: python -m clinaiqa.db.smoke_test
Requires the Docker Compose stack to be up and migrations applied.
Inserts one dummy 1536-dim vector, runs a cosine similarity query to confirm
pgvector is working, then rolls back so no data is left behind.
"""
import random

from sqlalchemy import create_engine, text

from clinaiqa.settings import settings


def main() -> None:
    url = settings.database_url_sync
    if not url:
        raise RuntimeError(
            "DATABASE_URL_SYNC is not set. Copy .env.example to .env and fill it in."
        )

    engine = create_engine(url, echo=False)

    dummy_vec = [random.uniform(-1, 1) for _ in range(1536)]
    vec_literal = "[" + ",".join(f"{v:.6f}" for v in dummy_vec) + "]"

    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO embeddings (source_text, embedding) VALUES (:txt, :vec::vector)"),
            {"txt": "smoke test passage", "vec": vec_literal},
        )

        row = conn.execute(
            text(
                "SELECT id, source_text, 1 - (embedding <=> :vec::vector) AS cosine_sim "
                "FROM embeddings ORDER BY embedding <=> :vec::vector LIMIT 1"
            ),
            {"vec": vec_literal},
        ).fetchone()

        if row is None:
            raise RuntimeError("pgvector smoke test: SELECT returned no rows after INSERT.")

        conn.rollback()

    print("pgvector smoke test passed.")
    print(f"  Nearest row id={row.id}, text='{row.source_text}', cosine_sim={row.cosine_sim:.6f}")


if __name__ == "__main__":
    main()
