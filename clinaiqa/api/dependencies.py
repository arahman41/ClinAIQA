"""
FastAPI dependency providers.

Both the evaluation runner and the audit repository are provided through
dependencies so tests can override them with a stub runner and an in-memory
repository (no LLM calls, no database).
"""
from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from clinaiqa.api.repository import AuditRepository, SqlAlchemyAuditRepository
from clinaiqa.eval.runner import EvalRunner
from clinaiqa.settings import settings


@lru_cache(maxsize=1)
def _engine():
    if not settings.database_url_sync:
        raise RuntimeError("DATABASE_URL_SYNC is not set.")
    return create_engine(settings.database_url_sync)


def get_runner() -> EvalRunner:
    return EvalRunner()


def get_repository() -> Iterator[AuditRepository]:
    with Session(_engine()) as session:
        yield SqlAlchemyAuditRepository(session)
