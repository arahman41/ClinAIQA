"""
Tests for the EvalRunner combining Layer 1 grounding and Layer 2 scoring.
All external calls (grounding pipeline, scorer) are mocked.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest

from clinaiqa.compliance.rules import ComplianceFlag, Severity
from clinaiqa.data.schemas import DocType, FlagType
from clinaiqa.eval.runner import EvalResult, EvalRunner, Flag
from clinaiqa.eval.scorer import PropertyVerdict
from clinaiqa.retrieval.grounder import GroundingReport, SentenceGroundingResult


def _grounded_result(sentence: str) -> SentenceGroundingResult:
    return SentenceGroundingResult(
        sentence=sentence,
        grounded=True,
        cosine_similarity=0.85,
        best_passage="matching passage",
        best_passage_doc_id="doc1",
    )


def _ungrounded_result(sentence: str) -> SentenceGroundingResult:
    return SentenceGroundingResult(
        sentence=sentence,
        grounded=False,
        cosine_similarity=0.20,
        best_passage=None,
        best_passage_doc_id=None,
    )


def _clean_verdict(name: str) -> PropertyVerdict:
    return PropertyVerdict(
        property_name=name,
        flag_type=FlagType.HALLUCINATION,
        violated=False,
        confidence=0.10,
        triggering_phrase="",
        reasoning="no violation found",
    )


def _violated_verdict(name: str) -> PropertyVerdict:
    return PropertyVerdict(
        property_name=name,
        flag_type=FlagType.HALLUCINATION,
        violated=True,
        confidence=0.92,
        triggering_phrase="bad claim",
        reasoning="claim not in source",
    )


@pytest.mark.harness
def test_clean_output_not_flagged():
    report = GroundingReport(sentences=[_grounded_result("Good sentence.")])
    verdicts = [_clean_verdict("fact_grounding")]

    with (
        patch("clinaiqa.eval.runner.run_grounding_pipeline", return_value=report),
        patch("clinaiqa.eval.runner.score_output", return_value=verdicts),
    ):
        runner = EvalRunner()
        result = runner.evaluate("Good sentence.", '{"key": "value"}')

    assert not result.flagged
    assert result.flags == []


@pytest.mark.harness
def test_ungrounded_sentence_causes_flag():
    report = GroundingReport(sentences=[_ungrounded_result("Bad sentence.")])
    verdicts = [_clean_verdict("fact_grounding")]

    with (
        patch("clinaiqa.eval.runner.run_grounding_pipeline", return_value=report),
        patch("clinaiqa.eval.runner.score_output", return_value=verdicts),
    ):
        runner = EvalRunner()
        result = runner.evaluate("Bad sentence.", '{"key": "value"}')

    assert result.flagged
    assert any(f.source == "layer1" for f in result.flags)


@pytest.mark.harness
def test_violated_rubric_property_causes_flag():
    report = GroundingReport(sentences=[_grounded_result("Good sentence.")])
    verdicts = [_violated_verdict("medication_accuracy")]

    with (
        patch("clinaiqa.eval.runner.run_grounding_pipeline", return_value=report),
        patch("clinaiqa.eval.runner.score_output", return_value=verdicts),
    ):
        runner = EvalRunner()
        result = runner.evaluate("Good sentence.", '{"key": "value"}')

    assert result.flagged
    assert any(f.source == "layer2" for f in result.flags)


@pytest.mark.harness
def test_result_contains_grounding_report():
    report = GroundingReport(sentences=[_grounded_result("Sentence.")])
    verdicts = [_clean_verdict("fact_grounding")]

    with (
        patch("clinaiqa.eval.runner.run_grounding_pipeline", return_value=report),
        patch("clinaiqa.eval.runner.score_output", return_value=verdicts),
    ):
        runner = EvalRunner()
        result = runner.evaluate("Sentence.", "{}")

    assert result.grounding_report is report


@pytest.mark.harness
def test_result_contains_property_verdicts():
    report = GroundingReport(sentences=[_grounded_result("Sentence.")])
    verdicts = [_clean_verdict("fact_grounding")]

    with (
        patch("clinaiqa.eval.runner.run_grounding_pipeline", return_value=report),
        patch("clinaiqa.eval.runner.score_output", return_value=verdicts),
    ):
        runner = EvalRunner()
        result = runner.evaluate("Sentence.", "{}")

    assert result.property_verdicts == verdicts


@pytest.mark.harness
def test_both_l1_and_l2_flags_present_when_both_triggered():
    report = GroundingReport(sentences=[_ungrounded_result("Bad.")])
    verdicts = [_violated_verdict("medication_accuracy")]

    with (
        patch("clinaiqa.eval.runner.run_grounding_pipeline", return_value=report),
        patch("clinaiqa.eval.runner.score_output", return_value=verdicts),
    ):
        runner = EvalRunner()
        result = runner.evaluate("Bad.", "{}")

    sources = {f.source for f in result.flags}
    assert "layer1" in sources
    assert "layer2" in sources


@pytest.mark.harness
def test_compliance_flag_causes_layer3_flag():
    report = GroundingReport(sentences=[_grounded_result("Good sentence.")])
    verdicts = [_clean_verdict("fact_grounding")]
    cflags = [
        ComplianceFlag(
            rule_id="ABS-001",
            severity=Severity.HIGH,
            triggering_phrase="guaranteed",
            reasoning="absolute claim",
        )
    ]

    with (
        patch("clinaiqa.eval.runner.run_grounding_pipeline", return_value=report),
        patch("clinaiqa.eval.runner.score_output", return_value=verdicts),
        patch("clinaiqa.eval.runner.scan_output", return_value=cflags),
    ):
        runner = EvalRunner()
        result = runner.evaluate("Good sentence.", "{}", doc_type=DocType.PATIENT_RECORD)

    assert result.flagged
    layer3 = [f for f in result.flags if f.source == "layer3"]
    assert len(layer3) == 1
    assert layer3[0].rule_id == "ABS-001"
    assert layer3[0].severity == Severity.HIGH.value
    assert layer3[0].flag_type == FlagType.COMPLIANCE.value


@pytest.mark.harness
def test_layer3_skipped_when_no_doc_type():
    report = GroundingReport(sentences=[_grounded_result("Good.")])
    verdicts = [_clean_verdict("fact_grounding")]

    with (
        patch("clinaiqa.eval.runner.run_grounding_pipeline", return_value=report),
        patch("clinaiqa.eval.runner.score_output", return_value=verdicts),
        patch("clinaiqa.eval.runner.scan_output") as mock_scan,
    ):
        runner = EvalRunner()
        result = runner.evaluate("Good.", "{}")

    mock_scan.assert_not_called()
    assert not result.flagged


@pytest.mark.harness
def test_flag_is_dataclass_with_expected_fields():
    report = GroundingReport(sentences=[_ungrounded_result("Bad.")])
    verdicts = [_clean_verdict("fact_grounding")]

    with (
        patch("clinaiqa.eval.runner.run_grounding_pipeline", return_value=report),
        patch("clinaiqa.eval.runner.score_output", return_value=verdicts),
    ):
        runner = EvalRunner()
        result = runner.evaluate("Bad.", "{}")

    flag = result.flags[0]
    assert isinstance(flag, Flag)
    assert flag.source == "layer1"
    assert flag.triggering_phrase == "Bad."
