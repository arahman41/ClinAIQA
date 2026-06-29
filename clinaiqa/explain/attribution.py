"""
Layer 4 explainability: phrase-level attribution.

Every flag produced by the harness links to the specific phrase in the output
that drove it, with a character span and (for grounding flags) the reference
passage that was retrieved. This is the attribution guarantee from the PRD; the
SHAP-backed classifier in classifier.py adds feature-level depth on top.
"""
from __future__ import annotations

from dataclasses import dataclass

from clinaiqa.eval.runner import EvalResult


@dataclass
class FlagAttribution:
    source: str                      # "layer1", "layer2", or "layer3"
    flag_type: str
    phrase: str                      # the driving phrase, verbatim from the flag
    start: int                       # char offset into output_text, -1 if not locatable
    end: int                         # exclusive end offset, -1 if not locatable
    reasoning: str = ""
    reference_passage: str | None = None  # supporting/contradicting passage (grounding flags)
    rule_id: str | None = None       # compliance flags
    severity: str | None = None      # compliance flags


def build_attribution(eval_result: EvalResult) -> list[FlagAttribution]:
    """Map every flag in eval_result to a FlagAttribution.

    Guarantees one attribution per flag. For grounding (layer1) flags the
    reference passage is looked up from the grounding report by matching the
    flagged sentence.
    """
    text = eval_result.output_text

    passage_by_sentence: dict[str, str | None] = {}
    if eval_result.grounding_report is not None:
        for sr in eval_result.grounding_report.sentences:
            passage_by_sentence[sr.sentence] = sr.best_passage

    attributions: list[FlagAttribution] = []
    for flag in eval_result.flags:
        phrase = flag.triggering_phrase
        start = text.find(phrase) if phrase else -1
        end = start + len(phrase) if start >= 0 else -1
        reference_passage = (
            passage_by_sentence.get(phrase) if flag.source == "layer1" else None
        )
        attributions.append(
            FlagAttribution(
                source=flag.source,
                flag_type=flag.flag_type,
                phrase=phrase,
                start=start,
                end=end,
                reasoning=flag.reasoning,
                reference_passage=reference_passage,
                rule_id=flag.rule_id,
                severity=flag.severity,
            )
        )
    return attributions
