"""Request and response schemas for the audit API."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from clinaiqa.data.schemas import DocType


class AuditRequest(BaseModel):
    output_text: str
    source_record: dict[str, Any]
    doc_type: DocType


class FlagOut(BaseModel):
    source: str
    flag_type: str
    phrase: str
    start: int
    end: int
    reasoning: str = ""
    reference_passage: str | None = None
    rule_id: str | None = None
    severity: str | None = None


class AuditResponse(BaseModel):
    id: int
    created_at: datetime
    doc_type: str
    verdict: str
    flags: list[FlagOut]


class PassRateResponse(BaseModel):
    total: int
    passed: int
    pass_rate: float
    history: list[dict[str, Any]]
