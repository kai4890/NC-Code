"""
Report generator for AutoComply.

Computes per-framework summary statistics from matcher results and exports
the full compliance report to both JSON and human-readable Markdown formats.

Scoring model
-------------
    COVERED  →  1.0 point
    PARTIAL  →  0.5 points
    MISSING  →  0.0 points

    compliance_score = (sum of points / total controls) × 100
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Status labels — mirror nlp/matcher.py without creating a circular import
_COVERED = "COVERED"
_PARTIAL  = "PARTIAL"
_MISSING  = "MISSING"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_framework_summary(
    results: List[Dict[str, Any]],
    framework_name: str,
) -> Dict[str, Any]:
    """Compute compliance summary statistics for a single framework.

    Args:
        results:        List of control result dicts from the matcher.
        framework_name: Display name of the framework.

    Returns:
        Dict with keys:

        .. code-block:: python

            {
                "framework":        str,
                "total_controls":   int,
                "covered_count":    int,
                "covered_pct":      float,
                "partial_count":    int,
                "partial_pct":      float,
                "missing_count":    int,
                "missing_pct":      float,
                "compliance_score": float,   # 0 – 100
            }
    """
    total = len(results)
    if total == 0:
        return _empty_summary(framework_name)

    covered = sum(1 for r in results if r["status"] == _COVERED)
    partial  = sum(1 for r in results if r["status"] == _PARTIAL)
    missing  = sum(1 for r in results if r["status"] == _MISSING)

    raw_score        = (covered * 1.0 + partial * 0.5) / total
    compliance_score = round(raw_score * 100, 1)

    return {
        "framework":        framework_name,
        "total_controls":   total,
        "covered_count":    covered,
        "covered_pct":      round(covered / total * 100, 1),
        "partial_count":    partial,
        "partial_pct":      round(partial / total * 100, 1),
        "missing_count":    missing,
        "missing_pct":      round(missing / total * 100, 1),
        "compliance_score": compliance_score,
    }


def build_full_report(
    framework_results: Dict[str, List[Dict[str, Any]]],
    document_name: str,
) -> Dict[str, Any]:
    """Build a complete compliance report from results across all frameworks.

    Args:
        framework_results: Mapping of framework name → list of result dicts.
        document_name:     Original filename of the analysed document.

    Returns:
        Full report dict suitable for JSON serialisation.
    """
    summaries = {
        name: compute_framework_summary(results, name)
        for name, results in framework_results.items()
    }

    scores = [s["compliance_score"] for s in summaries.values()]
    overall_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    return {
        "report_metadata": {
            "document_name":           document_name,
            "generated_at":            datetime.now(timezone.utc).isoformat(),
            "tool":                    "AutoComply v1.0",
            "frameworks_analysed":     list(framework_results.keys()),
            "overall_compliance_score": overall_score,
        },
        "framework_summaries": summaries,
        "detailed_findings":   framework_results,
    }


def export_json(report: Dict[str, Any]) -> str:
    """Serialise the full report to a pretty-printed JSON string.

    Args:
        report: Full report dict from :func:`build_full_report`.

    Returns:
        JSON string (UTF-8, 2-space indented).
    """
    return json.dumps(report, indent=2, ensure_ascii=False)


def export_markdown(report: Dict[str, Any]) -> str:
    """Generate a human-readable Markdown compliance report.

    Args:
        report: Full report dict from :func:`build_full_report`.

    Returns:
        Markdown-formatted string.
    """
    meta      = report["report_metadata"]
    summaries = report["framework_summaries"]
    findings  = report["detailed_findings"]

    lines: List[str] = []

    # ── Header ────────────────────────────────────────────────────────────
    lines += [
        "# AutoComply — Defence Compliance Gap Analysis Report",
        "",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| **Document** | {meta['document_name']} |",
        f"| **Generated** | {meta['generated_at']} |",
        f"| **Tool** | {meta['tool']} |",
        f"| **Overall Score** | **{meta['overall_compliance_score']} / 100** |",
        "",
        "---",
        "",
    ]

    # ── Executive Summary Table ───────────────────────────────────────────
    lines += [
        "## Executive Summary",
        "",
        "| Framework | Controls | Covered | Partial | Missing | Score |",
        "|-----------|----------|---------|---------|---------|-------|",
    ]
    for name, s in summaries.items():
        lines.append(
            f"| {name} "
            f"| {s['total_controls']} "
            f"| {s['covered_count']} ({s['covered_pct']}%) "
            f"| {s['partial_count']} ({s['partial_pct']}%) "
            f"| {s['missing_count']} ({s['missing_pct']}%) "
            f"| **{s['compliance_score']}** |"
        )
    lines += ["", "---", ""]

    # ── Detailed Findings (per framework) ─────────────────────────────────
    for framework_name, results in findings.items():
        s = summaries[framework_name]
        lines += [
            f"## {framework_name} — Detailed Findings",
            "",
            f"> **Score: {s['compliance_score']} / 100** &nbsp;|&nbsp; "
            f"✅ {s['covered_count']} covered &nbsp;|&nbsp; "
            f"⚠️ {s['partial_count']} partial &nbsp;|&nbsp; "
            f"❌ {s['missing_count']} missing",
            "",
        ]

        covered_items = [r for r in results if r["status"] == _COVERED]
        partial_items  = [r for r in results if r["status"] == _PARTIAL]
        missing_items  = [r for r in results if r["status"] == _MISSING]

        if covered_items:
            lines += ["### ✅ Covered Controls", ""]
            for r in covered_items:
                clause = r["best_matching_clause"][:250]
                if len(r["best_matching_clause"]) > 250:
                    clause += "…"
                lines += [
                    f"#### {r['control_id']}  *(score: {r['confidence_score']:.2%})*",
                    f"**Requirement:** {r['control_text']}",
                    f"**Matched clause:** *\"{clause}\"*",
                    "",
                ]

        if partial_items:
            lines += ["### ⚠️ Partially Covered Controls", ""]
            for r in partial_items:
                clause = r["best_matching_clause"][:250]
                if len(r["best_matching_clause"]) > 250:
                    clause += "…"
                lines += [
                    f"#### {r['control_id']}  *(score: {r['confidence_score']:.2%})*",
                    f"**Requirement:** {r['control_text']}",
                    f"**Closest clause:** *\"{clause}\"*",
                    "",
                ]

        if missing_items:
            lines += ["### ❌ Missing Controls", ""]
            for r in missing_items:
                lines += [
                    f"#### {r['control_id']}  *(score: {r['confidence_score']:.2%})*",
                    f"**Requirement:** {r['control_text']}",
                    f"**Status:** No matching clause found in document.",
                    "",
                ]

        lines += ["---", ""]

    lines += [
        "---",
        "",
        "*Report generated by [AutoComply](https://github.com/) "
        "— AI-Powered Compliance Gap Analyser for Australian Defence Sector*",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _empty_summary(framework_name: str) -> Dict[str, Any]:
    """Return a zero-value summary dict for a framework with no results."""
    return {
        "framework":        framework_name,
        "total_controls":   0,
        "covered_count":    0,
        "covered_pct":      0.0,
        "partial_count":    0,
        "partial_pct":      0.0,
        "missing_count":    0,
        "missing_pct":      0.0,
        "compliance_score": 0.0,
    }
