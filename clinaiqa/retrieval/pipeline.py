"""
Layer 1 pipeline: orchestrates chunker -> grounder -> GroundingReport.

Entry point for submitting an LLM output for grounding evaluation.
All sentences receive a score; none are skipped.
"""

from clinaiqa.retrieval.chunker import chunk_into_sentences
from clinaiqa.retrieval.grounder import GroundingReport, ground_sentences
from clinaiqa.settings import settings


def run_grounding_pipeline(
    output_text: str,
    threshold: float | None = None,
    top_k: int | None = None,
) -> GroundingReport:
    """
    Chunk output_text into sentences, ground each against the reference corpus.
    Returns a GroundingReport covering every sentence.

    Raises ValueError if output_text is blank.
    """
    if not output_text or not output_text.strip():
        raise ValueError("output_text must be a non-empty string.")

    threshold = threshold if threshold is not None else settings.grounding_threshold
    top_k = top_k if top_k is not None else settings.retrieval_top_k

    sentences = chunk_into_sentences(output_text)
    return ground_sentences(sentences, threshold=threshold, top_k=top_k)
