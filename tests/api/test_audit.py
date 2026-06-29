"""
Tests for the audit API endpoints.

The evaluation runner and the audit repository are injected, so these tests run
with no LLM calls and no database: a stub runner returns a prebuilt EvalResult
and an in-memory repository captures persistence.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from clinaiqa.api.dependencies import get_repository, get_runner
from clinaiqa.api.main import app
from clinaiqa.api.repository import InMemoryAuditRepository
from clinaiqa.eval.runner import EvalResult, Flag
from clinaiqa.retrieval.grounder import GroundingReport, SentenceGroundingResult


class _StubRunner:
    def __init__(self, result: EvalResult) -> None:
        self._result = result

    def evaluate(self, output_text: str, source_record: str, doc_type=None) -> EvalResult:
        return self._result


def _flagged_result() -> EvalResult:
    report = GroundingReport(
        sentences=[
            SentenceGroundingResult(
                sentence="This treatment is guaranteed to cure you.",
                grounded=False,
                cosine_similarity=0.10,
                best_passage="No such guarantee appears in the record.",
                best_passage_doc_id="d1",
            )
        ]
    )
    flags = [
        Flag(
            flag_type="compliance",
            source="layer3",
            property_name=None,
            triggering_phrase="guaranteed to cure",
            reasoning="absolute claim",
            rule_id="ABS-001",
            severity="high",
        )
    ]
    return EvalResult(
        output_text="This treatment is guaranteed to cure you.",
        flagged=True,
        flags=flags,
        grounding_report=report,
    )


def _clean_result() -> EvalResult:
    return EvalResult(output_text="Patient is stable.", flagged=False, flags=[])


@pytest.fixture
def repo() -> InMemoryAuditRepository:
    return InMemoryAuditRepository()


def _client(result: EvalResult, repo: InMemoryAuditRepository) -> TestClient:
    app.dependency_overrides[get_runner] = lambda: _StubRunner(result)
    app.dependency_overrides[get_repository] = lambda: repo
    return TestClient(app)


def teardown_function() -> None:
    app.dependency_overrides.clear()


def _payload() -> dict:
    return {
        "output_text": "This treatment is guaranteed to cure you.",
        "source_record": {"facility": "Test Clinic"},
        "doc_type": "patient_record",
    }


def test_audit_flagged_output_returns_fail_verdict(repo):
    client = _client(_flagged_result(), repo)
    resp = client.post("/audit", json=_payload())

    assert resp.status_code == 200
    body = resp.json()
    assert body["verdict"] == "fail"
    assert len(body["flags"]) == 1
    flag = body["flags"][0]
    assert flag["rule_id"] == "ABS-001"
    assert flag["severity"] == "high"
    # Layer 4 attribution is attached to each flag.
    assert flag["start"] >= 0
    assert flag["phrase"] == "guaranteed to cure"


def test_audit_clean_output_returns_pass_verdict(repo):
    client = _client(_clean_result(), repo)
    resp = client.post("/audit", json=_payload())

    assert resp.status_code == 200
    assert resp.json()["verdict"] == "pass"
    assert resp.json()["flags"] == []


def test_audit_persists_and_can_be_fetched(repo):
    client = _client(_flagged_result(), repo)
    created = client.post("/audit", json=_payload()).json()

    fetched = client.get(f"/audit/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == created["id"]
    assert fetched.json()["verdict"] == "fail"


def test_fetch_missing_audit_returns_404(repo):
    client = _client(_clean_result(), repo)
    assert client.get("/audit/99999").status_code == 404


def test_pass_rate_history_reflects_stored_audits(repo):
    # One fail, then one pass, sharing the same repository.
    fail_client = _client(_flagged_result(), repo)
    fail_client.post("/audit", json=_payload())
    pass_client = _client(_clean_result(), repo)
    pass_client.post("/audit", json=_payload())

    resp = pass_client.get("/audits/pass-rate")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    assert body["passed"] == 1
    assert body["pass_rate"] == pytest.approx(0.5)


def test_health_still_ok(repo):
    client = _client(_clean_result(), repo)
    assert client.get("/health").json() == {"status": "ok"}
