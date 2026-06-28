"""
Seeded split of adversarial examples into rubric-tuning and held-out sets.

THE HELD-OUT SET IS NEVER USED DURING RUBRIC DESIGN OR TUNING.
See agent_docs/testing.md for the full leak-free discipline.

Public API:
  assign_split(examples, seed, heldout_fraction) -> list[AdversarialExample]
  load_tuning_set(examples) -> list[AdversarialExample]
  load_heldout_for_final_report(examples) -> list[AdversarialExample]
"""

import random

from clinaiqa.data.schemas import AdversarialExample, SplitAssignment
from clinaiqa.settings import settings


def assign_split(
    examples: list[AdversarialExample],
    seed: int | None = None,
    heldout_fraction: float | None = None,
) -> list[AdversarialExample]:
    """
    Assign each example to TUNING or HELDOUT using a fixed seed.
    Returns a new list with split_assignment and split_seed set.
    Call this exactly once; do not re-split after tuning has begun.
    """
    seed = seed if seed is not None else settings.split_seed
    heldout_fraction = heldout_fraction if heldout_fraction is not None else settings.heldout_fraction

    if not (0.0 < heldout_fraction < 1.0):
        raise ValueError(
            f"heldout_fraction must be in (0, 1), got {heldout_fraction}. "
            "Use a decimal fraction such as 0.25 for 25 percent."
        )

    rng = random.Random(seed)
    assigned: list[AdversarialExample] = []
    for ex in examples:
        roll = rng.random()
        assignment = SplitAssignment.HELDOUT if roll < heldout_fraction else SplitAssignment.TUNING
        assigned.append(ex.model_copy(update={"split_assignment": assignment, "split_seed": seed}))
    return assigned


def load_tuning_set(examples: list[AdversarialExample]) -> list[AdversarialExample]:
    """Return only the tuning examples. Safe to use during rubric development."""
    return [ex for ex in examples if ex.split_assignment == SplitAssignment.TUNING]


def load_heldout_for_final_report(examples: list[AdversarialExample]) -> list[AdversarialExample]:
    """
    Return the held-out examples.

    WARNING: Call this function ONLY at the very end of the build to compute the
    final reported precision and recall (python -m clinaiqa.eval.report_metrics).
    Never call it during rubric design, threshold selection, or prompt tuning.
    Doing so invalidates the reported metric.
    """
    return [ex for ex in examples if ex.split_assignment == SplitAssignment.HELDOUT]
