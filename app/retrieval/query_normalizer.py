

"""
Normalize conversational queries before vector retrieval.
"""

import re


FILLER_PATTERNS = [
    r"^\s*and\s+",
    r"^\s*what\s+about\s+",
    r"^\s*how\s+about\s+",
    r"^\s*what\s+about\s+",
]


def normalize_query(query: str) -> str:
    """
    Remove common conversational filler while preserving
    the actual subject of the question.
    """

    normalized = query.strip().lower()

    for pattern in FILLER_PATTERNS:
        normalized = re.sub(
            pattern,
            "",
            normalized,
            count=1,
        )

    # Remove trailing question punctuation.
    normalized = normalized.strip(" ?!.")

    # Simple plural normalization for common policy terms.
    replacements = {
        "annual leaves": "annual leave",
        "casual leaves": "casual leave",
        "medical leaves": "medical leave",
    }

    normalized = replacements.get(
        normalized,
        normalized,
    )

    return normalized