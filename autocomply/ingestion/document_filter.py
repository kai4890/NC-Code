"""
Document boilerplate filter for AutoComply.

Detects and removes template instructions, placeholder text, and
non-policy language from parsed document clauses before embedding.
No external dependencies — stdlib re only.
"""

import re
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Category 1 — Placeholder patterns
# ---------------------------------------------------------------------------

# Square bracket fill-in: short or contains known fill-in vocabulary
_SQ_PLACEHOLDER = re.compile(
    r'\[(?:Insert|Enter|Add|Your|Organisation|Organization|Company|Department|'
    r'Name|Date|Title|Role|Position|Ref(?:erence)?|Author|Version|Place|Location|'
    r'Country|Number|Type|Description|Contact|Email|Phone|Address|Signature|'
    r'Manager|Officer|Director|Approver|dd|mm|yyyy|XX)[^\]]*\]',
    re.IGNORECASE,
)
_ANGLE_PLACEHOLDER = re.compile(r'<<[^>]*>>')
_CURLY_PLACEHOLDER = re.compile(r'\{[^}]*\}')


def _has_placeholder(clause: str) -> bool:
    return bool(
        _SQ_PLACEHOLDER.search(clause)
        or _ANGLE_PLACEHOLDER.search(clause)
        or _CURLY_PLACEHOLDER.search(clause)
    )


def _bracket_word_ratio(clause: str) -> float:
    """Fraction of words that sit inside any bracket type."""
    total = len(clause.split())
    if total == 0:
        return 0.0
    bracketed = re.findall(r'[\[\({<][^\]\)}>]*[\]\)}>]', clause)
    inside_words = sum(len(b.split()) for b in bracketed)
    return inside_words / total


# ---------------------------------------------------------------------------
# Category 2 — Instruction/directive language (prefix match)
# ---------------------------------------------------------------------------

_INSTRUCTION_PREFIX = re.compile(
    r'^(?:guidance\s*:|note\s*:|tip\s*:|instructions?\s*:|how\s+to\b|'
    r'to\s+complete\b|edit\s+this\b|delete\s+this\b|insert\s+|replace\s+|'
    r'customis[e]|customiz[e]|to-?do\b|fixme\b|see\s+also\b|refer\s+to\b|'
    r'please\s+note\b|important\s*:|warning\s*:)',
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Category 3 — Meta-document language (anywhere in clause)
# ---------------------------------------------------------------------------

_META_PHRASES = re.compile(
    r'this\s+template|this\s+document\s+template|'
    r'in\s+accordance\s+with\s+the\s+needs\s+of\s+your\s+organ[i]s[a-z]*|'
    r'once\s+you\s+complete\s+the\s+template|delete\s+this\s+page|'
    r'refresh\s+the\s+page\s+numbers?|table\s+of\s+contents?|'
    r'document\s+change\s+log|date\s+of\s+approval|'
    r'assigned\s+review\s+period|reviewed\s+by|'
    r'approved\s+by\s*\[|author\s*\[|'
    r'implementation\s+guidance|for\s+guidance\s+purposes?|'
    r'guidance\s+has\s+been\s+added|'
    r'should\s+not\s+appear\s+in\s+your\s+final|'
    r'example\s+topics?|can\s+be\s+customis[e]d|can\s+be\s+customiz[e]d',
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Category 4 — Structural/administrative content
# ---------------------------------------------------------------------------

_PAGE_NUMBER = re.compile(r'\bpage\s+\d+\s+of\s+\d+\b', re.IGNORECASE)

_VERSION_LINE = re.compile(r'(?:^version\s*[-–]\s*\d|^v\d+\.\d+)', re.IGNORECASE)

# TOC: line <= 80 chars ending with dots/spaces then a page number
_TOC_ENTRY = re.compile(r'^.{5,80}[\s.…]{2,}\d{1,3}\s*$')
# Numbered section heading with trailing page ref: "3.1 Governance ... 5"
_TOC_ENTRY2 = re.compile(r'^\d+(?:\.\d+)*\s+\w.{0,60}\s+\d{1,3}\s*$')

# Single-line document metadata labels (with optional colon + short value)
_METADATA_LINE = re.compile(
    r'^(?:author|version|date|ref(?:erence)?|title|status|classification|'
    r'document\s+(?:id|ref(?:erence)?|number)|revision|approved\s+by|'
    r'created\s+by|owner|review\s+date|document\s+owner)\s*[:\-–]?\s*.{0,50}$',
    re.IGNORECASE,
)

_COPYRIGHT = re.compile(
    r'disclaimer|no\s+representations?\b|does\s+not\s+accept\s+any\s+liability|'
    r'for\s+general\s+guidance\s+only|all\s+rights\s+reserved|©|\bcopyright\b',
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Category 5 — Low-quality clauses
# ---------------------------------------------------------------------------

_MIN_WORDS = 8
_CAPS_THRESHOLD = 0.60

_VERBS = re.compile(
    r'\b(?:must|shall|should|will|is|are|was|were|has|have|'
    r'requires?|ensures?|maintains?|provides?|defines?|applies?|'
    r'includes?|excludes?|prohibits?|allows?|restricts?)\b',
    re.IGNORECASE,
)


def _is_low_quality(clause: str) -> bool:
    words = clause.split()
    if len(words) < _MIN_WORDS:
        return True
    caps = sum(1 for w in words if w and w[0].isupper() and len(w) > 1)
    if caps / len(words) > _CAPS_THRESHOLD:
        return True
    if not _VERBS.search(clause):
        return True
    return False


# ---------------------------------------------------------------------------
# Removal classifier
# ---------------------------------------------------------------------------

def _removal_reason(clause: str) -> str | None:
    """Return why a clause should be removed, or None to keep it."""
    stripped = clause.strip()

    # Cat 1 — placeholders
    if _has_placeholder(stripped):
        return "placeholder"
    if _bracket_word_ratio(stripped) > 0.25:
        return "bracket_heavy"

    # Cat 2 — instruction prefix
    if _INSTRUCTION_PREFIX.match(stripped):
        return "instruction_prefix"

    # Cat 3 — meta-document language
    if _META_PHRASES.search(stripped):
        return "meta_document"

    # Cat 4 — structural / admin
    if _PAGE_NUMBER.search(stripped):
        return "page_number"
    if _VERSION_LINE.match(stripped):
        return "version_line"
    if _TOC_ENTRY.match(stripped) or _TOC_ENTRY2.match(stripped):
        return "toc_entry"
    if _METADATA_LINE.match(stripped):
        return "metadata_line"
    if _COPYRIGHT.search(stripped):
        return "copyright_disclaimer"

    # Cat 5 — low quality
    if _is_low_quality(stripped):
        return "low_quality"

    return None


# ---------------------------------------------------------------------------
# Quality labels
# ---------------------------------------------------------------------------

LABEL_GENUINE  = "GENUINE_POLICY"
LABEL_PARTIAL  = "PARTIAL_TEMPLATE"
LABEL_TEMPLATE = "TEMPLATE_DOCUMENT"

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def filter_boilerplate(
    clauses: List[str],
) -> Tuple[List[str], List[str], str]:
    """Filter boilerplate, template, and non-policy text from parsed clauses.

    Applies five detection categories (placeholders, instruction language,
    meta-document phrases, structural content, low-quality clauses) and
    computes a document quality label from the removal ratio.

    Args:
        clauses: Raw clause list from the document loader.

    Returns:
        Tuple of:
        - cleaned:  Clauses judged to contain genuine policy content.
        - removed:  Clauses that were filtered out (for logging / debug).
        - label:    One of LABEL_GENUINE, LABEL_PARTIAL, LABEL_TEMPLATE.
    """
    cleaned: List[str] = []
    removed: List[str] = []

    for clause in clauses:
        if _removal_reason(clause) is None:
            cleaned.append(clause)
        else:
            removed.append(clause)

    total = len(clauses)
    if total == 0:
        return cleaned, removed, LABEL_GENUINE

    removal_ratio = len(removed) / total

    if removal_ratio > 0.45:
        label = LABEL_TEMPLATE
    elif removal_ratio > 0.20:
        label = LABEL_PARTIAL
    else:
        label = LABEL_GENUINE

    return cleaned, removed, label
