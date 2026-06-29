"""
Layer 3 compliance scanner.

Runs the compliance rule pack over an output text and returns a list of
ComplianceFlag objects, each carrying a rule_id and severity. Deterministic
rules need no LLM. LLM-assisted rules call Claude for a JSON verdict and are
gated on a confidence threshold. A scoring failure (LLMError) propagates so the
caller can fail toward flagging, never a silent pass.
"""
from __future__ import annotations

from clinaiqa.compliance.rules import (
    COMPLIANCE_RULES,
    ComplianceFlag,
    DetectionMethod,
)
from clinaiqa.data.schemas import DocType
from clinaiqa.llm.client import get_client
from clinaiqa.settings import settings


def scan_output(
    output_text: str,
    doc_type: DocType,
    rules: list | None = None,
    confidence_threshold: float | None = None,
) -> list[ComplianceFlag]:
    """Scan output_text against the compliance rules.

    Deterministic rules are evaluated directly from the text. LLM-assisted rules
    are scored by Claude and only flag when confidence meets the threshold. The
    LLM client is constructed lazily, so a deterministic-only scan never needs a
    key or network.
    """
    rules = rules if rules is not None else COMPLIANCE_RULES
    threshold = (
        confidence_threshold
        if confidence_threshold is not None
        else settings.compliance_confidence_threshold
    )

    flags: list[ComplianceFlag] = []
    client = None

    for rule in rules:
        if rule.method == DetectionMethod.DETERMINISTIC:
            flags.extend(rule.detect(output_text, doc_type))
            continue

        if not rule.applies_to(doc_type):
            continue
        if client is None:
            client = get_client()
        result = client.score(rule.render(output_text, doc_type))

        violated = bool(result.get("violated", False))
        confidence = float(result.get("confidence", 0.0))
        if violated and confidence >= threshold:
            flags.append(
                ComplianceFlag(
                    rule_id=rule.rule_id,
                    severity=rule.severity,
                    triggering_phrase=str(result.get("triggering_phrase", "")),
                    reasoning=str(result.get("reasoning", "")),
                )
            )

    return flags
