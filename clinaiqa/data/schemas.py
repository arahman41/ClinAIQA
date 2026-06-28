from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DocType(str, Enum):
    CMS_FACILITY = "cms_facility"
    CLINICAL_GUIDELINE = "clinical_guideline"
    PATIENT_RECORD = "patient_record"


class Archetype(str, Enum):
    """Adversarial defect archetypes A-H from agent_docs/synthetic_data_archetypes.md."""

    FABRICATED_CLINICAL_FACT = "A"
    WRONG_MEDICATION_NAME = "B"
    FABRICATED_STATISTIC = "C"
    DIAGNOSIS_WITHOUT_DISCLAIMER = "D"
    MISSING_REQUIRED_DISCLAIMER = "E"
    DISALLOWED_ABSOLUTE_CLAIM = "F"
    HIPAA_ADJACENT_PHRASING = "G"
    SUBTLE_DRIFT = "H"


class FlagType(str, Enum):
    GROUNDING = "grounding"
    HALLUCINATION = "hallucination"
    COMPLIANCE = "compliance"


ARCHETYPE_FLAG_MAP: dict[Archetype, FlagType] = {
    Archetype.FABRICATED_CLINICAL_FACT: FlagType.GROUNDING,
    Archetype.WRONG_MEDICATION_NAME: FlagType.HALLUCINATION,
    Archetype.FABRICATED_STATISTIC: FlagType.HALLUCINATION,
    Archetype.DIAGNOSIS_WITHOUT_DISCLAIMER: FlagType.COMPLIANCE,
    Archetype.MISSING_REQUIRED_DISCLAIMER: FlagType.COMPLIANCE,
    Archetype.DISALLOWED_ABSOLUTE_CLAIM: FlagType.COMPLIANCE,
    Archetype.HIPAA_ADJACENT_PHRASING: FlagType.COMPLIANCE,
    Archetype.SUBTLE_DRIFT: FlagType.GROUNDING,
}


class SplitAssignment(str, Enum):
    TUNING = "tuning"
    HELDOUT = "heldout"


class HealthyExample(BaseModel):
    doc_type: DocType
    source_record: dict[str, Any]
    output_text: str


class AdversarialExample(BaseModel):
    healthy_example_id: int
    output_text: str
    archetype: Archetype
    defect_span: str
    expected_flag_type: FlagType
    split_assignment: SplitAssignment = SplitAssignment.TUNING
    split_seed: int | None = None
