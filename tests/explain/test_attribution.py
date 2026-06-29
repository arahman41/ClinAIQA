"""
Tests for Layer 4 phrase-level attribution.

build_attribution is a pure function over an EvalResult, so no mocking is needed.
The guarantee under test: every flag links to a specific driving phrase, with a
char span into the output and (for grounding flags) the reference passage.
"""
from __future__ import annotations

import pytest

from clinaiqa.explain.attribution import FlagAttribution, build_attribution
from clinaiqa.eval.runner import EvalResult, Flag
from clinaiqa.retrieval.grounder import GroundingReport, SentenceGroundingResult


_OUTPUT = "Patient is stable. This treatment is guaranteed to cure you."


def _layer1_flag(sentence: str) -> Flag:
    return Flag(
        flag_type="grounding",
        source="layer1",
        property_name=None,
        triggering_phrase=sentence,
        reasoning="cosine_similarity=0.200 below threshold",
    )


def _layer3_flag(phrase: str) -> Flag:
    return Flag(
        flag_type="compliance",
        source="layer3",
        property_name=None,
        triggering_phrase=phrase,
        reasoning="absolute claim",
        rule_id="ABS-001",
        severity="high",
    )


@pytest.mark.harness
def test_every_flag_gets_an_attribution():
    flags = [_layer1_flag("Patient is stable."), _layer3_flag("guaranteed to cure")]
    result = EvalResult(output_text=_OUTPUT, flagged=True, flags=flags)

    attributions = build_attribution(result)

    assert len(attributions) == len(flags)
    assert all(isinstance(a, FlagAttribution) for a in attributions)
    assert all(a.phrase != "" for a in attributions)


@pytest.mark.harness
def test_attribution_locates_phrase_span():
    flags = [_layer3_flag("guaranteed to cure")]
    result = EvalResult(output_text=_OUTPUT, flagged=True, flags=flags)

    attr = build_attribution(result)[0]

    assert attr.start >= 0
    assert _OUTPUT[attr.start : attr.end] == "guaranteed to cure"


@pytest.mark.harness
def test_grounding_attribution_includes_reference_passage():
    sentence = "Patient is stable."
    report = GroundingReport(
        sentences=[
            SentenceGroundingResult(
                sentence=sentence,
                grounded=False,
                cosine_similarity=0.20,
                best_passage="The patient's condition was recorded as stable.",
                best_passage_doc_id="doc1",
            )
        ]
    )
    result = EvalResult(
        output_text=_OUTPUT,
        flagged=True,
        flags=[_layer1_flag(sentence)],
        grounding_report=report,
    )

    attr = build_attribution(result)[0]

    assert attr.reference_passage == "The patient's condition was recorded as stable."


@pytest.mark.harness
def test_compliance_attribution_carries_rule_id_and_severity():
    result = EvalResult(
        output_text=_OUTPUT, flagged=True, flags=[_layer3_flag("guaranteed to cure")]
    )

    attr = build_attribution(result)[0]

    assert attr.rule_id == "ABS-001"
    assert attr.severity == "high"


@pytest.mark.harness
def test_phrase_not_in_text_yields_negative_span():
    flag = _layer3_flag("phrase that is absent")
    result = EvalResult(output_text=_OUTPUT, flagged=True, flags=[flag])

    attr = build_attribution(result)[0]

    assert attr.start == -1
    assert attr.end == -1


@pytest.mark.harness
def test_clean_result_yields_no_attributions():
    result = EvalResult(output_text=_OUTPUT, flagged=False, flags=[])
    assert build_attribution(result) == []
