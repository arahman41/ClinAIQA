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

# Matches any known abbreviation followed by a period, case-insensitively.
# Sorted longest-first so longer abbreviations take precedence in alternation.
_ABBREV_RE = re.compile(
    r"\b(" + "|".join(re.escape(a) for a in sorted(_ABBREVS, key=len, reverse=True)) + r")\.",
    re.IGNORECASE,
)

# Null byte is used as a temporary placeholder to protect abbreviation periods.
_PLACEHOLDER = "\x00"


def chunk_into_sentences(text: str) -> list[str]:
    """
    Split text into non-empty sentences.
    Returns an empty list for blank input rather than raising.
    Known medical abbreviations (mg, mcg, fev1, etc.) are protected from
    false sentence boundaries.
    """
    text = text.strip()
    if not text:
        return []

    # Replace periods after known abbreviations with a placeholder so the
    # sentence-boundary regex does not split on them.
    protected = _ABBREV_RE.sub(lambda m: m.group(1) + _PLACEHOLDER, text)

    raw = _SENTENCE_RE.split(protected)
    sentences: list[str] = []
    for s in raw:
        s = s.replace(_PLACEHOLDER, ".").strip()
        if s:
            sentences.append(s)

    if not sentences:
        return [text]
    return sentences
