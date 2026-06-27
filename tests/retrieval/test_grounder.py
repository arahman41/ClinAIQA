"""
Tests for Layer 1 grounding logic.
The LLM and pgvector retrieval are mocked so these tests are deterministic and free.
"""

from unittest.mock import patch

import pytest

from clinaiqa.retrieval.grounder import (
    GroundingReport,
    SentenceGroundingResult,
    ground_sentence,
    ground_sentences,
)


def _passage(chunk_text: str, sim: float) -> dict:
    return {
        "id": 1,
        "doc_id": "SYN-001",
        "doc_type": "cms_facility",
        "chunk_text": chunk_text,
        "cosine_similarity": sim,
    }


@pytest.mark.harness
def test_grounded_when_similarity_above_threshold():
    with patch("clinaiqa.retrieval.grounder.retrieve_top_k") as mock_retrieve:
        mock_retrieve.return_value = [_passage("supporting passage", 0.85)]
        result = ground_sentence("The facility has a 4-star rating.", threshold=0.70)
    assert result.grounded is True
    assert result.cosine_similarity == pytest.approx(0.85)
    assert result.best_passage == "supporting passage"


@pytest.mark.harness
def test_ungrounded_when_similarity_below_threshold():
    with patch("clinaiqa.retrieval.grounder.retrieve_top_k") as mock_retrieve:
        mock_retrieve.return_value = [_passage("unrelated passage", 0.45)]
        result = ground_sentence("The facility has a cardiac ICU.", threshold=0.70)
    assert result.grounded is False
    assert result.cosine_similarity == pytest.approx(0.45)


@pytest.mark.harness
def test_ungrounded_when_no_passages_returned():
    with patch("clinaiqa.retrieval.grounder.retrieve_top_k") as mock_retrieve:
        mock_retrieve.return_value = []
        result = ground_sentence("Some claim.", threshold=0.70)
    assert result.grounded is False
    assert result.cosine_similarity == 0.0
    assert result.best_passage is None


@pytest.mark.harness
def test_exactly_at_threshold_is_grounded():
    with patch("clinaiqa.retrieval.grounder.retrieve_top_k") as mock_retrieve:
        mock_retrieve.return_value = [_passage("passage at threshold", 0.70)]
        result = ground_sentence("A claim.", threshold=0.70)
    assert result.grounded is True


@pytest.mark.harness
def test_ground_sentences_all_receive_result():
    sentences = ["Sentence one.", "Sentence two.", "Sentence three."]
    with patch("clinaiqa.retrieval.grounder.retrieve_top_k") as mock_retrieve:
        mock_retrieve.return_value = [_passage("some passage", 0.80)]
        report = ground_sentences(sentences, threshold=0.70)
    assert len(report.sentences) == 3


@pytest.mark.harness
def test_grounding_report_coverage_is_always_1():
    with patch("clinaiqa.retrieval.grounder.retrieve_top_k") as mock_retrieve:
        mock_retrieve.return_value = [_passage("p", 0.50)]
        report = ground_sentences(["a", "b", "c"], threshold=0.70)
    assert report.coverage == pytest.approx(1.0)


@pytest.mark.harness
def test_grounding_report_ungrounded_sentences():
    sentences = ["Grounded sentence.", "Ungrounded claim."]
    sims = [0.85, 0.40]

    call_count = [0]

    def side_effect(query, **kwargs):
        sim = sims[call_count[0]]
        call_count[0] += 1
        return [_passage("passage", sim)]

    with patch("clinaiqa.retrieval.grounder.retrieve_top_k", side_effect=side_effect):
        report = ground_sentences(sentences, threshold=0.70)

    assert len(report.ungrounded_sentences) == 1
    assert report.ungrounded_sentences[0].sentence == "Ungrounded claim."


@pytest.mark.harness
def test_empty_sentence_list_returns_empty_report():
    report = ground_sentences([])
    assert report.sentences == []
    assert report.coverage == 0.0
