import pytest

from clinaiqa.settings import settings


@pytest.mark.harness
def test_hallucination_confidence_threshold_exists():
    assert 0.0 < settings.hallucination_confidence_threshold <= 1.0
