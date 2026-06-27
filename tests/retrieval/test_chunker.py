"""Tests for the sentence chunker (Layer 1 claim extraction)."""

import pytest

from clinaiqa.retrieval.chunker import chunk_into_sentences


@pytest.mark.harness
def test_single_sentence():
    result = chunk_into_sentences("This is a single sentence.")
    assert result == ["This is a single sentence."]


@pytest.mark.harness
def test_multiple_sentences():
    text = "The patient has Type 2 Diabetes. Current medication is Metformin. HbA1c is 7.8 percent."
    result = chunk_into_sentences(text)
    assert len(result) == 3
    assert result[0].startswith("The patient")
    assert result[1].startswith("Current")
    assert result[2].startswith("HbA1c")


@pytest.mark.harness
def test_empty_string_returns_empty_list():
    assert chunk_into_sentences("") == []
    assert chunk_into_sentences("   ") == []


@pytest.mark.harness
def test_all_sentences_are_non_empty():
    text = (
        "Greenfield Skilled Nursing Facility holds an overall CMS rating of 4 stars. "
        "RN hours per resident per day are 0.62. "
        "The facility operates 120 beds at 81 percent occupancy."
    )
    result = chunk_into_sentences(text)
    for s in result:
        assert s.strip() != "", "No sentence should be empty."


@pytest.mark.harness
def test_disclaimer_sentence_is_preserved():
    text = (
        "The patient has hypertension. "
        "This summary does not constitute medical advice. "
        "Consult a qualified clinician."
    )
    result = chunk_into_sentences(text)
    assert any("does not constitute" in s for s in result)


@pytest.mark.harness
def test_clinical_abbreviations_not_split():
    text = "The RN hours per resident per day are 0.62. Total nurse hours are 3.85."
    result = chunk_into_sentences(text)
    assert len(result) == 2
