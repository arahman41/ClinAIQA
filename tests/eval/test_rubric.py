import pytest

from clinaiqa.settings import settings


@pytest.mark.harness
def test_hallucination_confidence_threshold_exists():
    assert 0.0 < settings.hallucination_confidence_threshold <= 1.0


from clinaiqa.data.schemas import FlagType
from clinaiqa.eval.rubric import LAYER2_RUBRIC, RubricProperty


@pytest.mark.harness
def test_rubric_has_at_least_four_properties():
    assert len(LAYER2_RUBRIC) >= 4


@pytest.mark.harness
def test_all_rubric_properties_have_required_fields():
    for prop in LAYER2_RUBRIC:
        assert isinstance(prop, RubricProperty)
        assert prop.name and isinstance(prop.name, str)
        assert prop.description and isinstance(prop.description, str)
        assert "{output_text}" in prop.prompt_template
        assert "{source_record}" in prop.prompt_template
        assert isinstance(prop.expected_flag_type, FlagType)


@pytest.mark.harness
def test_rubric_property_names_are_unique():
    names = [p.name for p in LAYER2_RUBRIC]
    assert len(names) == len(set(names))


@pytest.mark.harness
def test_rubric_covers_hallucination_flag_type():
    flag_types = {p.expected_flag_type for p in LAYER2_RUBRIC}
    assert FlagType.HALLUCINATION in flag_types
