"""
Layer 1 grounding: assign a grounding score and verdict to each sentence.

Every sentence receives either:
  - grounded=True, best_passage reference, cosine_similarity score
  - grounded=False, best_passage=None, cosine_similarity below threshold

A scoring failure must never default to a silent pass.
If retrieval returns no passages, the sentence is flagged UNGROUNDED.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from clinaiqa.retrieval.store import retrieve_top_k
from clinaiqa.settings import settings


@dataclass
class SentenceGroundingResult:
    sentence: str
    grounded: bool
    cosine_similarity: float
    best_passage: str | None
    best_passage_doc_id: str | None


@dataclass
class GroundingReport:
    sentences: list[SentenceGroundingResult] = field(default_factory=list)

    @property
    def all_grounded(self) -> bool:
        return bool(self.sentences) and all(s.grounded for s in self.sentences)

    @property
    def ungrounded_sentences(self) -> list[SentenceGroundingResult]:
        return [s for s in self.sentences if not s.grounded]

    @property
    def coverage(self) -> float:
        """Fraction of sentences with a grounding score (always 1.0 by design)."""
        return 1.0 if self.sentences else 0.0


def ground_sentence(
    sentence: str,
    threshold: float | None = None,
    top_k: int | None = None,
) -> SentenceGroundingResult:
    """
    Retrieve top-k passages and score one sentence.
    Returns UNGROUNDED if no passages are retrieved or all are below threshold.
    Raises sqlalchemy.exc.OperationalError if retrieval itself fails (fail toward flagging).
    """
    threshold = threshold if threshold is not None else settings.grounding_threshold
    top_k = top_k if top_k is not None else settings.retrieval_top_k

    passages = retrieve_top_k(sentence, top_k=top_k)

    if not passages:
        return SentenceGroundingResult(
            sentence=sentence,
            grounded=False,
            cosine_similarity=0.0,
            best_passage=None,
            best_passage_doc_id=None,
        )

    best = passages[0]
    sim = best["cosine_similarity"]

    return SentenceGroundingResult(
        sentence=sentence,
        grounded=sim >= threshold,
        cosine_similarity=sim,
        best_passage=best["chunk_text"],
        best_passage_doc_id=best["doc_id"],
    )


def ground_sentences(
    sentences: list[str],
    threshold: float | None = None,
    top_k: int | None = None,
) -> GroundingReport:
    """
    Ground every sentence in the list and return a GroundingReport.
    All sentences receive a result (grounded or flagged); none are skipped.
    """
    if not sentences:
        return GroundingReport()

    results = [ground_sentence(s, threshold=threshold, top_k=top_k) for s in sentences]
    return GroundingReport(sentences=results)
