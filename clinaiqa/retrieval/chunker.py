"""
Split healthcare output text into sentence-level claims for Layer 1 grounding.
Uses a regex-based sentence splitter to avoid NLTK data download requirements.
"""

import re

_SENTENCE_RE = re.compile(
    r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s+",
    re.UNICODE,
)

_ABBREVS = frozenset(
    [
        "dr", "mr", "mrs", "ms", "prof", "sr", "jr",
        "vs", "etc", "e.g", "i.e", "fig", "no", "vol",
        "mg", "mcg", "ml", "kg", "lb", "oz", "mmhg",
        "hba1c", "bnp", "ef", "egfr", "fev1",
    ]
)


def chunk_into_sentences(text: str) -> list[str]:
    """
    Split text into non-empty sentences.
    Returns an empty list for blank input rather than raising.
    """
    text = text.strip()
    if not text:
        return []

    raw = _SENTENCE_RE.split(text)
    sentences: list[str] = []
    for s in raw:
        s = s.strip()
        if s:
            sentences.append(s)

    if not sentences:
        return [text]
    return sentences
