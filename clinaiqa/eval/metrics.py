"""
Precision, recall, and F1 computation for ClinAIQA evaluation results.

Usage:
    report = compute_metrics(eval_results, ground_truths)
    print(report)

ground_truths is a parallel list of booleans: True = truly adversarial (should be flagged).
eval_results[i].flagged = True means the harness flagged that example.
"""
from __future__ import annotations

from dataclasses import dataclass

from clinaiqa.eval.runner import EvalResult


@dataclass
class MetricsReport:
    n_total: int
    n_flagged: int
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    precision: float
    recall: float
    f1: float

    def __str__(self) -> str:
        return (
            f"ClinAIQA Evaluation Report\n"
            f"  Total examples : {self.n_total}\n"
            f"  Flagged        : {self.n_flagged}\n"
            f"  True positives : {self.true_positives}\n"
            f"  False positives: {self.false_positives}\n"
            f"  False negatives: {self.false_negatives}\n"
            f"  True negatives : {self.true_negatives}\n"
            f"  Precision      : {self.precision:.3f}\n"
            f"  Recall         : {self.recall:.3f}\n"
            f"  F1             : {self.f1:.3f}\n"
        )


def compute_metrics(
    results: list[EvalResult],
    ground_truths: list[bool],
) -> MetricsReport:
    """
    Compute precision, recall, and F1 from EvalResult list vs parallel ground truth list.

    ground_truths[i] = True means example i is truly adversarial (should be flagged).
    results[i].flagged = True means the harness flagged that example.
    """
    if len(results) != len(ground_truths):
        raise ValueError(
            f"results and ground_truths must have the same length, "
            f"got {len(results)} vs {len(ground_truths)}"
        )

    if not results:
        return MetricsReport(
            n_total=0, n_flagged=0,
            true_positives=0, false_positives=0,
            false_negatives=0, true_negatives=0,
            precision=0.0, recall=0.0, f1=0.0,
        )

    tp = fp = fn = tn = 0
    for result, is_adversarial in zip(results, ground_truths):
        if result.flagged and is_adversarial:
            tp += 1
        elif result.flagged and not is_adversarial:
            fp += 1
        elif not result.flagged and is_adversarial:
            fn += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return MetricsReport(
        n_total=len(results),
        n_flagged=tp + fp,
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
        true_negatives=tn,
        precision=precision,
        recall=recall,
        f1=f1,
    )
