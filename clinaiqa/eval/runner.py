"""
EvalRunner: orchestrates Layer 1 grounding and Layer 2 rubric scoring.

For every output text:
  1. Run the Layer 1 grounding pipeline (chunk + ground each sentence).
  2. Score the full output against each rubric property (Layer 2 scorer).
  3. Aggregate ungrounded sentences and violated properties into a single EvalResult.

A scoring failure must never silently pass. LLMError from Layer 2 propagates to
the caller, which decides how to treat the failure (report_metrics counts it as
flagged, fail toward flagging).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from clinaiqa.compliance.scanner import scan_output
from clinaiqa.data.schemas import DocType
from clinaiqa.eval.rubric import LAYER2_RUBRIC, RubricProperty
from clinaiqa.eval.scorer import PropertyVerdict, score_output
from clinaiqa.retrieval.grounder import GroundingReport
from clinaiqa.retrieval.pipeline import run_grounding_pipeline


@dataclass
class Flag:
    flag_type: str
    source: str          # "layer1", "layer2", or "layer3"
    property_name: str | None
    triggering_phrase: str
    reasoning: str
    rule_id: str | None = None      # set for layer3 compliance flags
    severity: str | None = None     # set for layer3 compliance flags


@dataclass
class EvalResult:
    output_text: str
    flagged: bool
    flags: list[Flag] = field(default_factory=list)
    grounding_report: GroundingReport | None = None
    property_verdicts: list[PropertyVerdict] = field(default_factory=list)


class EvalRunner:
    def __init__(self, rubric: list[RubricProperty] | None = None) -> None:
        self._rubric = rubric if rubric is not None else LAYER2_RUBRIC

    def evaluate(
        self,
        output_text: str,
        source_record: str,
        doc_type: DocType | None = None,
    ) -> EvalResult:
        """
        Run Layer 1 and Layer 2 on output_text, plus Layer 3 when doc_type is given.
        Returns EvalResult. Raises LLMError if Layer 2 or Layer 3 scoring fails
        (fail toward flagging).
        """
        grounding_report = run_grounding_pipeline(output_text)
        property_verdicts = score_output(output_text, source_record, self._rubric)

        flags: list[Flag] = []

        for sr in grounding_report.ungrounded_sentences:
            flags.append(
                Flag(
                    flag_type="grounding",
                    source="layer1",
                    property_name=None,
                    triggering_phrase=sr.sentence,
                    reasoning=f"cosine_similarity={sr.cosine_similarity:.3f} below threshold",
                )
            )

        for verdict in property_verdicts:
            if verdict.violated:
                flags.append(
                    Flag(
                        flag_type=verdict.flag_type.value,
                        source="layer2",
                        property_name=verdict.property_name,
                        triggering_phrase=verdict.triggering_phrase,
                        reasoning=verdict.reasoning,
                    )
                )

        if doc_type is not None:
            for cflag in scan_output(output_text, doc_type):
                flags.append(
                    Flag(
                        flag_type=cflag.flag_type.value,
                        source="layer3",
                        property_name=None,
                        triggering_phrase=cflag.triggering_phrase,
                        reasoning=cflag.reasoning,
                        rule_id=cflag.rule_id,
                        severity=cflag.severity.value,
                    )
                )

        return EvalResult(
            output_text=output_text,
            flagged=len(flags) > 0,
            flags=flags,
            grounding_report=grounding_report,
            property_verdicts=property_verdicts,
        )
