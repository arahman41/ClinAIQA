"""
Database loaders for the evaluation harness.

load_tuning_from_db():
    Returns adversarial examples assigned to the tuning split.
    Safe to call during rubric development and threshold selection.

load_heldout_from_db_for_final_report():
    Returns adversarial examples assigned to the held-out split.

    WARNING: Call this ONLY inside report_metrics.py to compute the final
    reported precision and recall. Never call it during rubric design,
    threshold selection, or prompt tuning. Doing so invalidates the metric.

load_healthy_from_db():
    Returns all healthy examples (the negative class for precision measurement).
"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from clinaiqa.data.schemas import SplitAssignment
from clinaiqa.db.models import AdversarialExample as DBAdversarialExample
from clinaiqa.db.models import HealthyExample as DBHealthyExample
from clinaiqa.settings import settings


def _get_session() -> Session:
    engine = create_engine(settings.database_url_sync)
    return Session(engine)


def load_tuning_from_db(session: Session | None = None) -> list[DBAdversarialExample]:
    """Return all adversarial examples in the tuning split."""
    own_session = session is None
    s = session or _get_session()
    try:
        return (
            s.query(DBAdversarialExample)
            .filter(DBAdversarialExample.split_assignment == SplitAssignment.TUNING.value)
            .all()
        )
    finally:
        if own_session:
            s.close()


def load_heldout_from_db_for_final_report(
    session: Session | None = None,
) -> list[DBAdversarialExample]:
    """
    Return all adversarial examples in the held-out split.

    WARNING: Call this ONLY from report_metrics.py.
    """
    own_session = session is None
    s = session or _get_session()
    try:
        return (
            s.query(DBAdversarialExample)
            .filter(DBAdversarialExample.split_assignment == SplitAssignment.HELDOUT.value)
            .all()
        )
    finally:
        if own_session:
            s.close()


def load_healthy_from_db(session: Session | None = None) -> list[DBHealthyExample]:
    """Return all healthy (negative) examples."""
    own_session = session is None
    s = session or _get_session()
    try:
        return s.query(DBHealthyExample).all()
    finally:
        if own_session:
            s.close()
