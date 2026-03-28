"""
Semantic matcher for AutoComply.

Computes a hybrid score from cosine-similarity embeddings and domain-keyword
signals to determine whether each compliance requirement is covered, partially
covered, or missing in the uploaded policy.

Hybrid score
------------
    hybrid = 0.80 × embedding_score + 0.20 × keyword_score

    Retrieval uses the top-3 candidate clauses per control (by embedding
    similarity); the hybrid score selects the winner among those 3.

Thresholds
----------
    >= 0.75  →  COVERED   (green)  — high-confidence match
    0.55–0.75 →  PARTIAL   (amber)  — partial or indirect coverage
    <  0.55  →  MISSING   (red)    — no meaningful coverage found
"""

import logging
from typing import Any, Dict, List

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .rules import keyword_score

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

# Coverage thresholds (applied to hybrid score)
_COVERED_THRESHOLD  = 0.75
_PARTIAL_THRESHOLD  = 0.55
_EMBEDDING_WEIGHT   = 0.80
_KEYWORD_WEIGHT     = 0.20
_TOP_K              = 3


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
                "confidence_score":     float,   # hybrid score 0.0 – 1.0
                "embedding_score":      float,   # raw cosine similarity 0.0 – 1.0
                "keyword_score":        float,   # domain-term lexical score 0.0 – 1.0
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

    n_top = min(_TOP_K, len(clauses))

    results: List[Dict[str, Any]] = []
    for idx, control in enumerate(controls):
        row = sim_matrix[idx]
        cid = control["control_id"]

        # Retrieve top-5 candidate clause indices by embedding similarity
        top_indices = np.argpartition(row, -n_top)[-n_top:]

        best_hybrid  = -1.0
        best_emb     = 0.0
        best_kw      = 0.0
        best_clause  = ""

        for ci in top_indices:
            emb_s  = float(row[ci])
            kw_s   = keyword_score(cid, clauses[ci])
            hybrid = _EMBEDDING_WEIGHT * emb_s + _KEYWORD_WEIGHT * kw_s
            if hybrid > best_hybrid:
                best_hybrid = hybrid
                best_emb    = emb_s
                best_kw     = kw_s
                best_clause = clauses[ci]

        status = _score_to_status(best_hybrid)

        results.append(
            {
                "control_id":           cid,
                "control_text":         control["control_text"],
                "status":               status,
                "confidence_score":     round(best_hybrid, 4),
                "embedding_score":      round(best_emb, 4),
                "keyword_score":        round(best_kw, 4),
                "best_matching_clause": best_clause,
                "framework":            control["framework"],
            }
        )
        logger.debug(
            "%s  hybrid=%.4f  emb=%.4f  kw=%.4f  status=%s",
            cid,
            best_hybrid,
            best_emb,
            best_kw,
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
            "embedding_score":      0.0,
            "keyword_score":        0.0,
            "best_matching_clause": "No document clauses could be extracted.",
            "framework":            c["framework"],
        }
        for c in controls
    ]
