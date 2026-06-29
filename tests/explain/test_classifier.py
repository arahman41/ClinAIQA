"""
Tests for the Layer 4 SHAP-backed flag classifier.

Feature extraction and the learned classifier use numpy and scikit-learn. The
SHAP explanation test skips where shap is not installed (it runs in the
container, which has the full requirements).
"""
from __future__ import annotations

import pytest

from clinaiqa.explain.classifier import (
    FEATURE_NAMES,
    FlagClassifier,
    extract_features,
)
from clinaiqa.eval.runner import EvalResult, Flag
from clinaiqa.eval.scorer import PropertyVerdict
from clinaiqa.data.schemas import FlagType
from clinaiqa.retrieval.grounder import GroundingReport, SentenceGroundingResult


def _result_clean() -> EvalResult:
    report = GroundingReport(
        sentences=[
            SentenceGroundingResult(
                sentence="Grounded.",
                grounded=True,
                cosine_similarity=0.90,
                best_passage="passage",
                best_passage_doc_id="d1",
            )
        ]
    )
    verdicts = [
        PropertyVerdict("fact_grounding", FlagType.HALLUCINATION, False, 0.05, "", "ok")
    ]
    return EvalResult(
        output_text="Grounded.",
        flagged=False,
        flags=[],
        grounding_report=report,
        property_verdicts=verdicts,
    )


def _result_flagged() -> EvalResult:
    report = GroundingReport(
        sentences=[
            SentenceGroundingResult(
                sentence="Bad.",
                grounded=False,
                cosine_similarity=0.10,
                best_passage=None,
                best_passage_doc_id=None,
            )
        ]
    )
    verdicts = [
        PropertyVerdict("medication_accuracy", FlagType.HALLUCINATION, True, 0.95, "wrong drug", "bad")
    ]
    flags = [
        Flag("hallucination", "layer2", "medication_accuracy", "wrong drug", "bad"),
        Flag("compliance", "layer3", None, "guaranteed", "absolute claim", rule_id="ABS-001", severity="high"),
    ]
    return EvalResult(
        output_text="Bad.",
        flagged=True,
        flags=flags,
        grounding_report=report,
        property_verdicts=verdicts,
    )


@pytest.mark.harness
def test_extract_features_returns_one_value_per_feature():
    feats = extract_features(_result_clean())
    assert len(feats) == len(FEATURE_NAMES)
    assert all(isinstance(f, float) for f in feats)


@pytest.mark.harness
def test_flagged_result_has_stronger_signal_than_clean():
    clean = dict(zip(FEATURE_NAMES, extract_features(_result_clean())))
    flagged = dict(zip(FEATURE_NAMES, extract_features(_result_flagged())))

    assert flagged["min_grounding_similarity"] < clean["min_grounding_similarity"]
    assert flagged["ungrounded_sentence_count"] > clean["ungrounded_sentence_count"]
    assert flagged["layer2_violation_count"] > clean["layer2_violation_count"]
    assert flagged["layer3_flag_count"] > clean["layer3_flag_count"]


@pytest.mark.harness
def test_classifier_learns_separable_data():
    # Clean examples (label 0) have high similarity and no violations; flagged
    # examples (label 1) have low similarity and violations.
    X = [
        [0.9, 0.0, 0.05, 0.0, 0.0, 0.0],
        [0.85, 0.0, 0.10, 0.0, 0.0, 0.0],
        [0.1, 1.0, 0.95, 1.0, 1.0, 3.0],
        [0.2, 1.0, 0.90, 1.0, 0.0, 0.0],
    ]
    y = [0, 0, 1, 1]
    clf = FlagClassifier().fit(X, y)

    p_clean = clf.predict_proba([[0.9, 0.0, 0.05, 0.0, 0.0, 0.0]])[0]
    p_flagged = clf.predict_proba([[0.1, 1.0, 0.95, 1.0, 1.0, 3.0]])[0]

    assert p_flagged > 0.5
    assert p_clean < 0.5


@pytest.mark.harness
def test_save_load_roundtrip_preserves_predictions(tmp_path):
    X = [
        [0.9, 0.0, 0.05, 0.0, 0.0, 0.0],
        [0.85, 0.0, 0.10, 0.0, 0.0, 0.0],
        [0.1, 1.0, 0.95, 1.0, 1.0, 3.0],
        [0.2, 1.0, 0.90, 1.0, 0.0, 0.0],
    ]
    y = [0, 0, 1, 1]
    clf = FlagClassifier().fit(X, y)

    path = tmp_path / "flag_classifier.json"
    clf.save(path)
    loaded = FlagClassifier.load(path)

    probe = [[0.1, 1.0, 0.95, 1.0, 1.0, 3.0]]
    assert loaded.predict_proba(probe)[0] == pytest.approx(clf.predict_proba(probe)[0], abs=1e-9)


def test_explain_returns_a_contribution_per_feature():
    pytest.importorskip("shap")
    X = [
        [0.9, 0.0, 0.05, 0.0, 0.0, 0.0],
        [0.85, 0.0, 0.10, 0.0, 0.0, 0.0],
        [0.1, 1.0, 0.95, 1.0, 1.0, 3.0],
        [0.2, 1.0, 0.90, 1.0, 0.0, 0.0],
    ]
    y = [0, 0, 1, 1]
    clf = FlagClassifier().fit(X, y)

    contributions = clf.explain([0.1, 1.0, 0.95, 1.0, 1.0, 3.0])

    assert len(contributions) == len(FEATURE_NAMES)
    names = [c.feature_name for c in contributions]
    assert names == FEATURE_NAMES
    assert all(isinstance(c.shap_value, float) for c in contributions)
