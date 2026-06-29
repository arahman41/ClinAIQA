"""
Tests for the Layer 3 compliance scanner.

Deterministic rule tests run with no LLM client. LLM-assisted rule tests mock
the client so they stay deterministic and free.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from clinaiqa.compliance.rules import (
    ABSOLUTE_CLAIM_RULE,
    DIAGNOSIS_DISCLAIMER_RULE,
    HIPAA_PHRASING_RULE,
    REQUIRED_DISCLAIMER_RULE,
    Severity,
)
from clinaiqa.compliance.scanner import scan_output
from clinaiqa.data.schemas import DocType, FlagType

import pytest


def _mock_client(violated: bool, confidence: float = 0.95, phrase: str = "patient identifier") -> MagicMock:
    mock = MagicMock()
    mock.score.return_value = {
        "violated": violated,
        "confidence": confidence,
        "triggering_phrase": phrase if violated else "",
        "reasoning": "test reasoning",
    }
    return mock


@pytest.mark.harness
def test_absolute_claim_produces_compliance_flag():
    text = "This treatment is guaranteed to cure your condition."
    flags = scan_output(text, DocType.PATIENT_RECORD, [ABSOLUTE_CLAIM_RULE])

    assert len(flags) == 1
    flag = flags[0]
    assert flag.rule_id == ABSOLUTE_CLAIM_RULE.rule_id
    assert flag.severity == Severity.HIGH
    assert flag.flag_type == FlagType.COMPLIANCE
    assert "guaranteed" in flag.triggering_phrase.lower()


@pytest.mark.harness
def test_clean_output_produces_no_absolute_claim_flag():
    text = "The facility reported 120 beds and standard staffing levels."
    flags = scan_output(text, DocType.CMS_FACILITY, [ABSOLUTE_CLAIM_RULE])
    assert flags == []


@pytest.mark.harness
def test_missing_required_disclaimer_is_flagged():
    text = "Take 200mg twice daily for your symptoms."
    flags = scan_output(text, DocType.PATIENT_RECORD, [REQUIRED_DISCLAIMER_RULE])
    assert len(flags) == 1
    assert flags[0].rule_id == REQUIRED_DISCLAIMER_RULE.rule_id
    assert flags[0].triggering_phrase != ""


@pytest.mark.harness
def test_present_disclaimer_not_flagged():
    text = "Take 200mg twice daily. Consult your physician before changing your dose."
    flags = scan_output(text, DocType.PATIENT_RECORD, [REQUIRED_DISCLAIMER_RULE])
    assert flags == []


@pytest.mark.harness
def test_definitive_diagnosis_without_disclaimer_is_flagged():
    text = "You have stage 2 hypertension and need immediate treatment."
    flags = scan_output(text, DocType.PATIENT_RECORD, [DIAGNOSIS_DISCLAIMER_RULE])
    assert len(flags) == 1
    assert flags[0].rule_id == DIAGNOSIS_DISCLAIMER_RULE.rule_id
    assert "you have" in flags[0].triggering_phrase.lower()


@pytest.mark.harness
def test_non_diagnostic_text_does_not_trigger_diagnosis_rule():
    text = "Your appointment is scheduled for Tuesday at the clinic."
    flags = scan_output(text, DocType.PATIENT_RECORD, [DIAGNOSIS_DISCLAIMER_RULE])
    assert flags == []


@pytest.mark.harness
def test_diagnosis_with_disclaimer_not_flagged():
    text = "You have stage 2 hypertension. This is not a diagnosis; consult your physician."
    flags = scan_output(text, DocType.PATIENT_RECORD, [DIAGNOSIS_DISCLAIMER_RULE])
    assert flags == []


@pytest.mark.harness
def test_llm_rule_flags_when_model_says_violated():
    with patch("clinaiqa.compliance.scanner.get_client", return_value=_mock_client(True, phrase="John Doe SSN 123")):
        flags = scan_output("some text", DocType.PATIENT_RECORD, [HIPAA_PHRASING_RULE])
    assert len(flags) == 1
    assert flags[0].rule_id == HIPAA_PHRASING_RULE.rule_id
    assert flags[0].severity == HIPAA_PHRASING_RULE.severity
    assert flags[0].flag_type == FlagType.COMPLIANCE


@pytest.mark.harness
def test_llm_rule_not_flagged_when_clean():
    with patch("clinaiqa.compliance.scanner.get_client", return_value=_mock_client(False)):
        flags = scan_output("some text", DocType.PATIENT_RECORD, [HIPAA_PHRASING_RULE])
    assert flags == []


@pytest.mark.harness
def test_llm_rule_low_confidence_not_flagged():
    mock = _mock_client(violated=True, confidence=0.30)
    with patch("clinaiqa.compliance.scanner.get_client", return_value=mock):
        flags = scan_output(
            "some text", DocType.PATIENT_RECORD, [HIPAA_PHRASING_RULE], confidence_threshold=0.70
        )
    assert flags == []


@pytest.mark.harness
def test_llm_rule_error_propagates():
    """A scoring failure must never silently pass (fail toward flagging upstream)."""
    from clinaiqa.llm.client import LLMError

    mock = MagicMock()
    mock.score.side_effect = LLMError("boom")
    with patch("clinaiqa.compliance.scanner.get_client", return_value=mock):
        with pytest.raises(LLMError):
            scan_output("some text", DocType.PATIENT_RECORD, [HIPAA_PHRASING_RULE])


@pytest.mark.harness
def test_deterministic_rule_needs_no_client():
    """Scanning a deterministic-only rule list must not construct an LLM client."""
    flags = scan_output("guaranteed to cure", DocType.PATIENT_RECORD, [ABSOLUTE_CLAIM_RULE])
    assert len(flags) == 1
