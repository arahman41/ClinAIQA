"""
Layer 2 scorer: evaluate output text against a rubric property list using Claude.

Each property is scored independently. On LLMError the exception propagates
(fail toward flagging - the caller decides whether to treat a scoring failure as
a flag). A violation only counts when the model's confidence meets the threshold.
"""
from __future__ import annotations

from dataclasses import dataclass

from clinaiqa.data.schemas import FlagType
from clinaiqa.eval.rubric import RubricProperty
from clinaiqa.llm.client import get_client
from clinaiqa.settings import settings


@dataclass
class PropertyVerdict:
    property_name: str
    flag_type: FlagType
    violated: bool
    confidence: float
    triggering_phrase: str
    reasoning: str


def _render(template: str, output_text: str, source_record: str) -> str:
    """Fill the two placeholders without str.format().

    The rubric prompt embeds a literal JSON schema with curly braces, so
    str.format() would raise on them. Targeted replacement is brace-safe.
    """
    return template.replace("{source_record}", source_record).replace(
        "{output_text}", output_text
    )


def score_output(
    output_text: str,
    source_record: str,
    rubric: list[RubricProperty],
    confidence_threshold: float | None = None,
) -> list[PropertyVerdict]:
    """
    Score output_text against every property in the rubric.
    Returns one PropertyVerdict per property.
    Raises LLMError on parse failure (never silently passes a scoring error).
    """
    threshold = (
        confidence_threshold
        if confidence_threshold is not None
        else settings.hallucination_confidence_threshold
    )
    client = get_client()
    verdicts: list[PropertyVerdict] = []

    for prop in rubric:
        prompt = _render(prop.prompt_template, output_text, source_record)
        result = client.score(prompt)

        raw_violated = bool(result.get("violated", False))
        confidence = float(result.get("confidence", 0.0))
        triggered = raw_violated and confidence >= threshold

        verdicts.append(
            PropertyVerdict(
                property_name=prop.name,
                flag_type=prop.expected_flag_type,
                violated=triggered,
                confidence=confidence,
                triggering_phrase=str(result.get("triggering_phrase", "")),
                reasoning=str(result.get("reasoning", "")),
            )
        )

    return verdicts
