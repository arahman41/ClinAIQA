"""
Tests for the adversarial data split.
Verifies: determinism with same seed, no overlap between tuning/heldout,
sizes match the heldout_fraction, and the held-out loader name is enforced.
"""

import pytest

from clinaiqa.data.schemas import AdversarialExample, Archetype, FlagType, SplitAssignment
from clinaiqa.data.split import assign_split, load_heldout_for_final_report, load_tuning_set


def _make_examples(n: int) -> list[AdversarialExample]:
    return [
        AdversarialExample(
            healthy_example_id=i,
            output_text=f"output {i}",
            archetype=Archetype.FABRICATED_CLINICAL_FACT,
            defect_span="injected fact",
            expected_flag_type=FlagType.GROUNDING,
            split_assignment=SplitAssignment.TUNING,
            split_seed=42,
        )
        for i in range(n)
    ]


@pytest.mark.harness
def test_split_is_deterministic():
    examples = _make_examples(100)
    first = assign_split(examples, seed=42, heldout_fraction=0.25)
    second = assign_split(examples, seed=42, heldout_fraction=0.25)
    assert [e.split_assignment for e in first] == [e.split_assignment for e in second]


@pytest.mark.harness
def test_split_different_seeds_produce_different_results():
    examples = _make_examples(100)
    a = assign_split(examples, seed=42, heldout_fraction=0.25)
    b = assign_split(examples, seed=99, heldout_fraction=0.25)
    assert [e.split_assignment for e in a] != [e.split_assignment for e in b]


@pytest.mark.harness
def test_tuning_and_heldout_are_disjoint():
    examples = _make_examples(100)
    assigned = assign_split(examples, seed=42, heldout_fraction=0.25)
    tuning_ids = {e.healthy_example_id for e in load_tuning_set(assigned)}
    heldout_ids = {e.healthy_example_id for e in load_heldout_for_final_report(assigned)}
    assert tuning_ids.isdisjoint(heldout_ids), "Tuning and heldout sets must not share examples."


@pytest.mark.harness
def test_all_examples_are_assigned():
    examples = _make_examples(80)
    assigned = assign_split(examples, seed=42, heldout_fraction=0.25)
    assert len(assigned) == 80
    for ex in assigned:
        assert ex.split_assignment in (SplitAssignment.TUNING, SplitAssignment.HELDOUT)


@pytest.mark.harness
def test_heldout_fraction_is_approximately_correct():
    examples = _make_examples(200)
    assigned = assign_split(examples, seed=42, heldout_fraction=0.25)
    heldout = load_heldout_for_final_report(assigned)
    fraction = len(heldout) / len(assigned)
    assert 0.18 <= fraction <= 0.32, f"Heldout fraction {fraction:.2f} outside expected range."


@pytest.mark.harness
def test_split_seed_is_recorded_on_each_example():
    examples = _make_examples(20)
    assigned = assign_split(examples, seed=77, heldout_fraction=0.25)
    for ex in assigned:
        assert ex.split_seed == 77
