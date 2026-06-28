"""
Tests for the Layer 2 scorer.
All tests mock the LLM client so they are deterministic and free.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from clinaiqa.eval.rubric import LAYER2_RUBRIC
from clinaiqa.eval.scorer import PropertyVerdict, score_output


_CLEAN_SOURCE = '{"facility": "Sunrise Medical Center", "bed_count": 120}'
_CLEAN_OUTPUT = "Sunrise Medical Center is a 120-bed facility."


def _mock_client(violated: bool, confidence: float = 0.95, phrase: str = "test phrase") -> MagicMock:
    mock = MagicMock()
    mock.score.return_value = {
        "violated": violated,
        "confidence": confidence,
        "triggering_phrase": phrase if violated else "",
        "reasoning": "test reasoning",
    }
    return mock


@pytest.mark.harness
def test_score_output_returns_one_verdict_per_property():
    with patch("clinaiqa.eval.scorer.get_client", return_value=_mock_client(False)):
        verdicts = score_output(_CLEAN_OUTPUT, _CLEAN_SOURCE, LAYER2_RUBRIC)
    assert len(verdicts) == len(LAYER2_RUBRIC)


@pytest.mark.harness
def test_score_output_not_violated_when_output_is_clean():
    with patch("clinaiqa.eval.scorer.get_client", return_value=_mock_client(False)):
        verdicts = score_output(_CLEAN_OUTPUT, _CLEAN_SOURCE, LAYER2_RUBRIC)
    assert all(not v.violated for v in verdicts)


@pytest.mark.harness
def test_score_output_violated_when_llm_says_so():
    with patch("clinaiqa.eval.scorer.get_client", return_value=_mock_client(True, phrase="bad claim")):
        verdicts = score_output(_CLEAN_OUTPUT, _CLEAN_SOURCE, LAYER2_RUBRIC)
    assert all(v.violated for v in verdicts)


@pytest.mark.harness
def test_verdict_carries_property_name():
    with patch("clinaiqa.eval.scorer.get_client", return_value=_mock_client(False)):
        verdicts = score_output(_CLEAN_OUTPUT, _CLEAN_SOURCE, LAYER2_RUBRIC)
    names = {v.property_name for v in verdicts}
    assert names == {p.name for p in LAYER2_RUBRIC}


@pytest.mark.harness
def test_verdict_carries_flag_type():
    with patch("clinaiqa.eval.scorer.get_client", return_value=_mock_client(True)):
        verdicts = score_output(_CLEAN_OUTPUT, _CLEAN_SOURCE, LAYER2_RUBRIC)
    for v, prop in zip(verdicts, LAYER2_RUBRIC):
        assert v.flag_type == prop.expected_flag_type


@pytest.mark.harness
def test_low_confidence_verdict_not_violated():
    """A violation below the confidence threshold must NOT trigger a flag."""
    mock = _mock_client(violated=True, confidence=0.30, phrase="maybe")
    with patch("clinaiqa.eval.scorer.get_client", return_value=mock):
        verdicts = score_output(
            _CLEAN_OUTPUT, _CLEAN_SOURCE, LAYER2_RUBRIC, confidence_threshold=0.70
        )
    assert all(not v.violated for v in verdicts)


@pytest.mark.harness
def test_prompt_is_rendered_without_format_error():
    """The rubric prompt contains literal JSON braces; rendering must not raise
    and must substitute both placeholders with the real output and source."""
    captured: dict[str, str] = {}

    def _capture(prompt: str) -> dict:
        captured["prompt"] = prompt
        return {"violated": False, "confidence": 0.0, "triggering_phrase": "", "reasoning": "ok"}

    mock = MagicMock()
    mock.score.side_effect = _capture
    with patch("clinaiqa.eval.scorer.get_client", return_value=mock):
        score_output(_CLEAN_OUTPUT, _CLEAN_SOURCE, LAYER2_RUBRIC[:1])

    assert _CLEAN_OUTPUT in captured["prompt"]
    assert _CLEAN_SOURCE in captured["prompt"]
    assert "{output_text}" not in captured["prompt"]
    assert "{source_record}" not in captured["prompt"]


@pytest.mark.harness
def test_parse_failure_raises_llm_error():
    """If the LLM returns unparseable JSON the scorer must raise (not silently pass)."""
    from clinaiqa.llm.client import LLMError

    mock = MagicMock()
    mock.score.side_effect = LLMError("parse failure")
    with patch("clinaiqa.eval.scorer.get_client", return_value=mock):
        with pytest.raises(LLMError):
            score_output(_CLEAN_OUTPUT, _CLEAN_SOURCE, LAYER2_RUBRIC[:1])
