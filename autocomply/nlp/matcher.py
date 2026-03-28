"""
Semantic matcher for AutoComply.

Computes cosine similarity between pre-computed framework control embeddings
and document clause embeddings to determine whether each compliance
requirement is covered, partially covered, or missing in the uploaded policy.

Thresholds
----------
    >= 0.65  →  COVERED   (green)  — high-confidence semantic match
    0.40–0.65 →  PARTIAL   (amber)  — partial or indirect coverage
    <  0.40  →  MISSING   (red)    — no meaningful coverage found
"""

import logging
from typing import Any, Dict, List

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Status constants — single source of truth referenced across the project
# ---------------------------------------------------------------------------
STATUS_COVERED = "COVERED"
STATUS_PARTIAL  = "PARTIAL"
STATUS_MISSING  = "MISSING"

# Hex colours used in both the Streamlit UI and the Markdown report
STATUS_COLOURS: Dict[str, str] = {
    STATUS_COVERED: "#2ECC71",  # Green
    STATUS_PARTIAL:  "#F39C12",  # Amber
    STATUS_MISSING:  "#E74C3C",  # Red
}

# Coverage thresholds
_COVERED_THRESHOLD = 0.65
_PARTIAL_THRESHOLD  = 0.40


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def match_controls_to_document(
    controls: List[Dict[str, str]],
    control_embeddings: np.ndarray,
    clauses: List[str],
    clause_embeddings: np.ndarray,
) -> List[Dict[str, Any]]:
    """Match each framework control against all document clauses.

    For every control the best-matching clause is identified using cosine
    similarity and the result is categorised as COVERED / PARTIAL / MISSING
    based on the similarity score.

    Args:
        controls:           List of control dicts (``control_id``, ``control_text``,
                            ``framework``).
        control_embeddings: Pre-computed embeddings, shape ``(n_controls, dim)``.
        clauses:            List of document clause strings.
        clause_embeddings:  Pre-computed clause embeddings, shape ``(n_clauses, dim)``.

    Returns:
        List of result dicts — one per control — each containing:

        .. code-block:: python

            {
                "control_id":           str,
                "control_text":         str,
                "status":               "COVERED" | "PARTIAL" | "MISSING",
                "confidence_score":     float,   # 0.0 – 1.0
                "best_matching_clause": str,
                "framework":            str,
            }
    """
    if not clauses:
        logger.warning("No document clauses available — all controls marked MISSING.")
        return _build_missing_results(controls)

    # Full similarity matrix: shape (n_controls, n_clauses)
    # Both embedding matrices are L2-normalised so cosine_similarity == dot product
    sim_matrix = cosine_similarity(control_embeddings, clause_embeddings)
    logger.info(
        "Similarity matrix computed: %d controls × %d clauses",
        len(controls),
        len(clauses),
    )

    results: List[Dict[str, Any]] = []
    for idx, control in enumerate(controls):
        row          = sim_matrix[idx]
        best_idx     = int(np.argmax(row))
        best_score   = float(row[best_idx])
        best_clause  = clauses[best_idx]
        status       = _score_to_status(best_score)

        results.append(
            {
                "control_id":           control["control_id"],
                "control_text":         control["control_text"],
                "status":               status,
                "confidence_score":     round(best_score, 4),
                "best_matching_clause": best_clause,
                "framework":            control["framework"],
            }
        )
        logger.debug(
            "%s  score=%.4f  status=%s",
            control["control_id"],
            best_score,
            status,
        )

    return results


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _score_to_status(score: float) -> str:
    """Map a cosine-similarity score to a coverage status label."""
    if score >= _COVERED_THRESHOLD:
        return STATUS_COVERED
    if score >= _PARTIAL_THRESHOLD:
        return STATUS_PARTIAL
    return STATUS_MISSING


def _build_missing_results(controls: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Return MISSING result dicts for all controls (used when no clauses exist)."""
    return [
        {
            "control_id":           c["control_id"],
            "control_text":         c["control_text"],
            "status":               STATUS_MISSING,
            "confidence_score":     0.0,
            "best_matching_clause": "No document clauses could be extracted.",
            "framework":            c["framework"],
        }
        for c in controls
    ]
