"""
ClinAIQA audit API.

Endpoints:
  GET  /health             liveness check
  POST /audit              run all layers on a submitted output, persist, return verdict
  GET  /audit/{id}         fetch a stored audit record
  GET  /audits/pass-rate   pass rate over time across stored audits
"""
from __future__ import annotations

import json

from fastapi import Depends, FastAPI, HTTPException

from clinaiqa.api.dependencies import get_repository, get_runner
from clinaiqa.api.repository import AuditData, AuditRepository
from clinaiqa.api.schemas import (
    AuditRequest,
    AuditResponse,
    FlagOut,
    PassRateResponse,
)
from clinaiqa.eval.runner import EvalRunner
from clinaiqa.explain.attribution import build_attribution

app = FastAPI(title="ClinAIQA", version="0.1.0")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


def _flags_payload(result) -> list[dict]:
    """Combine each flag with its Layer 4 attribution into serializable dicts."""
    return [
        FlagOut(
            source=attr.source,
            flag_type=attr.flag_type,
            phrase=attr.phrase,
            start=attr.start,
            end=attr.end,
            reasoning=attr.reasoning,
            reference_passage=attr.reference_passage,
            rule_id=attr.rule_id,
            severity=attr.severity,
        ).model_dump()
        for attr in build_attribution(result)
    ]


@app.post("/audit", response_model=AuditResponse)
def audit(
    request: AuditRequest,
    runner: EvalRunner = Depends(get_runner),
    repository: AuditRepository = Depends(get_repository),
) -> AuditResponse:
    result = runner.evaluate(
        request.output_text,
        json.dumps(request.source_record),
        doc_type=request.doc_type,
    )
    flags = _flags_payload(result)
    verdict = "fail" if result.flagged else "pass"

    stored = repository.save(
        AuditData(
            doc_type=request.doc_type.value,
            output_text=request.output_text,
            source_record=request.source_record,
            verdict=verdict,
            flags=flags,
        )
    )
    return AuditResponse(
        id=stored.id,
        created_at=stored.created_at,
        doc_type=stored.doc_type,
        verdict=stored.verdict,
        flags=stored.flags,
    )


@app.get("/audit/{audit_id}", response_model=AuditResponse)
def get_audit(
    audit_id: int,
    repository: AuditRepository = Depends(get_repository),
) -> AuditResponse:
    stored = repository.get(audit_id)
    if stored is None:
        raise HTTPException(status_code=404, detail="Audit record not found.")
    return AuditResponse(
        id=stored.id,
        created_at=stored.created_at,
        doc_type=stored.doc_type,
        verdict=stored.verdict,
        flags=stored.flags,
    )


@app.get("/audits/pass-rate", response_model=PassRateResponse)
def pass_rate(
    repository: AuditRepository = Depends(get_repository),
) -> PassRateResponse:
    history = repository.pass_rate_history()
    total = len(history)
    passed = sum(1 for record in history if record.verdict == "pass")
    return PassRateResponse(
        total=total,
        passed=passed,
        pass_rate=(passed / total) if total else 0.0,
        history=[
            {"id": r.id, "created_at": r.created_at.isoformat(), "verdict": r.verdict}
            for r in history
        ],
    )
