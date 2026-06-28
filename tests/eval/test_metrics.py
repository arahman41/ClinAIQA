"""
Tests for precision/recall computation.
Uses in-memory EvalResult and ground truth lists only.
"""
from __future__ import annotations

import pytest

from clinaiqa.eval.metrics import MetricsReport, compute_metrics
from clinaiqa.eval.runner import EvalResult


def _flagged(text: str = "text") -> EvalResult:
    return EvalResult(output_text=text, flagged=True)


def _clean(text: str = "text") -> EvalResult:
    return EvalResult(output_text=text, flagged=False)


@pytest.mark.harness
def test_perfect_precision_and_recall():
    results = [_flagged("bad"), _clean("good")]
    ground_truths = [True, False]
    report = compute_metrics(results, ground_truths)
    assert report.precision == pytest.approx(1.0)
    assert report.recall == pytest.approx(1.0)


@pytest.mark.harness
def test_zero_recall_when_nothing_flagged():
    results = [_clean("bad")]
    ground_truths = [True]
    report = compute_metrics(results, ground_truths)
    assert report.recall == pytest.approx(0.0)
    assert report.true_positives == 0
    assert report.false_negatives == 1


@pytest.mark.harness
def test_zero_precision_when_only_false_positives():
    results = [_flagged("good")]
    ground_truths = [False]
    report = compute_metrics(results, ground_truths)
    assert report.precision == pytest.approx(0.0)
    assert report.false_positives == 1
    assert report.true_positives == 0


@pytest.mark.harness
def test_partial_recall():
    results = [_flagged("bad1"), _clean("bad2"), _flagged("bad3")]
    ground_truths = [True, True, True]
    report = compute_metrics(results, ground_truths)
    assert report.recall == pytest.approx(2 / 3)
    assert report.true_positives == 2
    assert report.false_negatives == 1


@pytest.mark.harness
def test_f1_harmonic_mean():
    results = [_flagged("a"), _flagged("b"), _clean("c")]
    ground_truths = [True, False, True]
    report = compute_metrics(results, ground_truths)
    # TP=1, FP=1, FN=1 -> precision=0.5, recall=0.5, f1=0.5
    assert report.precision == pytest.approx(0.5)
    assert report.recall == pytest.approx(0.5)
    assert report.f1 == pytest.approx(0.5)


@pytest.mark.harness
def test_counts_match_n_total():
    results = [_flagged("a"), _clean("b"), _flagged("c"), _clean("d")]
    ground_truths = [True, False, False, True]
    report = compute_metrics(results, ground_truths)
    assert report.n_total == 4
    total = (
        report.true_positives
        + report.false_positives
        + report.false_negatives
        + report.true_negatives
    )
    assert total == 4


@pytest.mark.harness
def test_mismatched_lengths_raise():
    with pytest.raises(ValueError, match="length"):
        compute_metrics([_flagged()], [True, False])


@pytest.mark.harness
def test_empty_inputs_return_zero_metrics():
    report = compute_metrics([], [])
    assert report.n_total == 0
    assert report.precision == 0.0
    assert report.recall == 0.0
    assert report.f1 == 0.0


@pytest.mark.harness
def test_report_str_is_em_dash_free():
    results = [_flagged("a"), _clean("b")]
    ground_truths = [True, False]
    report = compute_metrics(results, ground_truths)
    assert "—" not in str(report)
