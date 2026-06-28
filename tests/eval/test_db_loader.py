"""
Tests for the DB loader wiring.

These do NOT touch a live database. They verify that:
  1. The ORM relationship that Layer 2 scoring depends on is configured, so
     ex.healthy_example.source_record resolves to the parent record.
  2. The loader module exposes the expected functions.
"""
from __future__ import annotations

import pytest
from sqlalchemy import inspect

from clinaiqa.db.models import AdversarialExample


@pytest.mark.harness
def test_adversarial_example_has_healthy_example_relationship():
    rels = inspect(AdversarialExample).relationships
    assert "healthy_example" in rels.keys()
    assert rels["healthy_example"].mapper.class_.__name__ == "HealthyExample"


@pytest.mark.harness
def test_db_loader_exposes_expected_functions():
    from clinaiqa.eval import db_loader

    assert hasattr(db_loader, "load_tuning_from_db")
    assert hasattr(db_loader, "load_heldout_from_db_for_final_report")
    assert hasattr(db_loader, "load_healthy_from_db")
