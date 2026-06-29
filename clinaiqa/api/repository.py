"""
Audit record persistence.

AuditRepository is the abstraction the API depends on. SqlAlchemyAuditRepository
is the production implementation backed by the audit_records table.
InMemoryAuditRepository is used in tests so endpoint behavior is verified with no
database.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol

from sqlalchemy.orm import Session

from clinaiqa.db.models import AuditRecord


@dataclass
class AuditData:
    doc_type: str
    output_text: str
    source_record: dict
    verdict: str
    flags: list[dict] = field(default_factory=list)


@dataclass
class StoredAudit:
    id: int
    created_at: datetime
    doc_type: str
    output_text: str
    source_record: dict
    verdict: str
    flags: list[dict]


class AuditRepository(Protocol):
    def save(self, data: AuditData) -> StoredAudit: ...
    def get(self, audit_id: int) -> StoredAudit | None: ...
    def pass_rate_history(self) -> list[StoredAudit]: ...


class InMemoryAuditRepository:
    """Non-persistent repository for tests."""

    def __init__(self) -> None:
        self._store: dict[int, StoredAudit] = {}
        self._next_id = 1

    def save(self, data: AuditData) -> StoredAudit:
        record = StoredAudit(
            id=self._next_id,
            created_at=datetime.now(timezone.utc),
            doc_type=data.doc_type,
            output_text=data.output_text,
            source_record=data.source_record,
            verdict=data.verdict,
            flags=data.flags,
        )
        self._store[record.id] = record
        self._next_id += 1
        return record

    def get(self, audit_id: int) -> StoredAudit | None:
        return self._store.get(audit_id)

    def pass_rate_history(self) -> list[StoredAudit]:
        return sorted(self._store.values(), key=lambda r: r.created_at)


class SqlAlchemyAuditRepository:
    """Production repository backed by the audit_records table."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _to_stored(row: AuditRecord) -> StoredAudit:
        return StoredAudit(
            id=row.id,
            created_at=row.created_at,
            doc_type=row.doc_type,
            output_text=row.output_text,
            source_record=row.source_record,
            verdict=row.verdict,
            flags=row.flags,
        )

    def save(self, data: AuditData) -> StoredAudit:
        row = AuditRecord(
            doc_type=data.doc_type,
            output_text=data.output_text,
            source_record=data.source_record,
            verdict=data.verdict,
            flags=data.flags,
        )
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return self._to_stored(row)

    def get(self, audit_id: int) -> StoredAudit | None:
        row = self._session.get(AuditRecord, audit_id)
        return self._to_stored(row) if row is not None else None

    def pass_rate_history(self) -> list[StoredAudit]:
        rows = (
            self._session.query(AuditRecord)
            .order_by(AuditRecord.created_at.asc())
            .all()
        )
        return [self._to_stored(r) for r in rows]
