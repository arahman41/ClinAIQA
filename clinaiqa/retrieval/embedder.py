"""
Wrapper around sentence-transformers for generating embeddings.
Loaded lazily so import cost is only paid when first used.
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from clinaiqa.settings import settings

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=4)
def _load_model(model_name: str) -> "SentenceTransformer":
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def embed(texts: list[str]) -> list[list[float]]:
    """
    Return a list of embedding vectors, one per input text.
    Raises ValueError for an empty input list.
    """
    if not texts:
        raise ValueError("embed() called with an empty list of texts.")
    model = _load_model(settings.embedding_model)
    vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return [v.tolist() for v in vectors]


def embed_one(text: str) -> list[float]:
    """Convenience wrapper for a single text."""
    return embed([text])[0]
