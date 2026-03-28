"""
AutoComply — Command-line entry point.

Runs a full compliance gap analysis from the terminal without the Streamlit UI.
Results are printed to stdout and exported as JSON + Markdown report files.

Usage
-----
    # Analyse against all three frameworks (default)
    python main.py policy.pdf

    # Select specific frameworks
    python main.py policy.docx --frameworks iso27001,disp

    # Custom output directory
    python main.py policy.pdf --frameworks iso27001,disp,e8_ml1,e8_ml2,e8_ml3 --output-dir ./reports

Available framework keys
------------------------
    iso27001   — ISO 27001 Annex A (20 controls)
    disp       — Defence Industry Security Program (10 controls)
    e8_ml1     — ASD Essential Eight Maturity Level 1 (8 controls)
    e8_ml2     — ASD Essential Eight Maturity Level 2 (8 controls)
    e8_ml3     — ASD Essential Eight Maturity Level 3 (8 controls)
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Ensure the project root is on sys.path when running as a script
sys.path.insert(0, str(Path(__file__).parent))

from frameworks.disp_controls import get_controls as get_disp
from frameworks.essential_eight import get_controls as get_e8_ml2, get_ml1_controls as get_e8_ml1, get_ml3_controls as get_e8_ml3
from frameworks.iso27001_controls import get_controls as get_iso27001
from ingestion.document_loader import load_document
from nlp.embedder import Embedder
from nlp.matcher import match_controls_to_document
from reporting.report_generator import build_full_report, export_json, export_markdown

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)-8s]  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Framework registry
# ---------------------------------------------------------------------------
AVAILABLE_FRAMEWORKS: Dict[str, Tuple[str, callable]] = {
    "iso27001": ("ISO 27001",       get_iso27001),
    "disp":     ("DISP",            get_disp),
    "e8_ml1":   ("Essential Eight ML1", get_e8_ml1),
    "e8_ml2":   ("Essential Eight ML2", get_e8_ml2),
    "e8_ml3":   ("Essential Eight ML3", get_e8_ml3),
}

_SEPARATOR = "=" * 62


# ---------------------------------------------------------------------------
# Core analysis pipeline
# ---------------------------------------------------------------------------

def run_analysis(
    document_path: str,
    framework_keys: List[str],
    output_dir: str,
) -> None:
    """Execute the full compliance gap analysis pipeline.

    Steps
    -----
    1. Load and pre-process the document.
    2. Initialise the NLP embedder.
    3. Pre-embed all selected framework controls.
    4. Embed document clauses.
    5. Match controls to clauses.
    6. Build and export reports.
    7. Print a summary to stdout.

    Args:
        document_path:  Path to the PDF or DOCX document to analyse.
        framework_keys: List of framework keys (e.g. ``['iso27001', 'disp']``).
        output_dir:     Directory where JSON and Markdown reports are saved.
    """
    # ── 1. Load document ──────────────────────────────────────────────────
    logger.info("Loading document: %s", document_path)
    try:
        clauses = load_document(document_path)
    except (FileNotFoundError, ValueError) as exc:
        logger.error("Document load failed: %s", exc)
        sys.exit(1)

    logger.info("Extracted %d clauses from document.", len(clauses))
    if not clauses:
        logger.error("No clauses extracted — the document may be empty or unreadable.")
        sys.exit(1)

    # ── 2. Initialise embedder ────────────────────────────────────────────
    logger.info("Initialising NLP embedder (model: all-MiniLM-L6-v2)…")
    embedder = Embedder()

    # ── 3. Pre-embed framework controls ───────────────────────────────────
    selected_controls: Dict[str, list] = {}
    control_embeddings: Dict[str, object] = {}

    for key in framework_keys:
        fw_display_name, get_controls_fn = AVAILABLE_FRAMEWORKS[key]
        controls = get_controls_fn()
        texts    = [c["control_text"] for c in controls]
        logger.info("Embedding %d controls for %s…", len(texts), fw_display_name)
        control_embeddings[fw_display_name] = embedder.embed_controls(texts)
        selected_controls[fw_display_name]  = controls

    # ── 4. Embed document clauses ─────────────────────────────────────────
    logger.info("Embedding %d document clauses…", len(clauses))
    clause_embeddings = embedder.embed_clauses(clauses)

    # ── 5. Match controls to clauses ──────────────────────────────────────
    all_results: Dict[str, list] = {}
    for fw_name, controls in selected_controls.items():
        logger.info("Running gap analysis for %s…", fw_name)
        all_results[fw_name] = match_controls_to_document(
            controls,
            control_embeddings[fw_name],
            clauses,
            clause_embeddings,
        )

    # ── 6. Build and export reports ───────────────────────────────────────
    doc_name = Path(document_path).name
    report   = build_full_report(all_results, doc_name)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(document_path).stem

    json_path = out_dir / f"autocomply_report_{stem}.json"
    md_path   = out_dir / f"autocomply_report_{stem}.md"

    json_path.write_text(export_json(report),     encoding="utf-8")
    md_path.write_text(export_markdown(report),   encoding="utf-8")

    logger.info("JSON report  → %s", json_path.resolve())
    logger.info("MD report    → %s", md_path.resolve())

    # ── 7. Print console summary ──────────────────────────────────────────
    _print_summary(report, json_path, md_path)


def _print_summary(report: dict, json_path: Path, md_path: Path) -> None:
    """Print a formatted compliance summary table to stdout."""
    meta = report["report_metadata"]

    print()
    print(_SEPARATOR)
    print("  AutoComply — Compliance Gap Analysis Results")
    print(_SEPARATOR)
    print(f"  Document : {meta['document_name']}")
    print(f"  Overall  : {meta['overall_compliance_score']} / 100")
    print()

    for fw_name, s in report["framework_summaries"].items():
        bar_width = 30
        filled    = int(s["compliance_score"] / 100 * bar_width)
        bar       = "█" * filled + "░" * (bar_width - filled)
        print(f"  {fw_name}")
        print(f"    [{bar}] {s['compliance_score']} / 100")
        print(
            f"    ✅ Covered : {s['covered_count']:>2} / {s['total_controls']}  "
            f"({s['covered_pct']}%)"
        )
        print(
            f"    ⚠️ Partial : {s['partial_count']:>2} / {s['total_controls']}  "
            f"({s['partial_pct']}%)"
        )
        print(
            f"    ❌ Missing : {s['missing_count']:>2} / {s['total_controls']}  "
            f"({s['missing_pct']}%)"
        )
        print()

    print(f"  Reports saved to:")
    print(f"    {json_path.resolve()}")
    print(f"    {md_path.resolve()}")
    print(_SEPARATOR)
    print()


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autocomply",
        description=(
            "AutoComply — AI-powered compliance gap analysis tool for "
            "Australian Defence sector organisations."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py security_policy.pdf
  python main.py policy.docx --frameworks iso27001,disp
  python main.py policy.pdf  --frameworks iso27001,disp,e8 --output-dir ./reports

Framework keys:
  iso27001  — ISO 27001:2022 Annex A  (20 controls)
  disp      — DISP                   (10 controls)
  e8        — ASD Essential Eight ML2 ( 8 controls)
        """,
    )
    parser.add_argument(
        "document",
        help="Path to the PDF or DOCX security policy document to analyse.",
    )
    parser.add_argument(
        "--frameworks",
        default="iso27001,disp,e8",
        metavar="KEYS",
        help=(
            "Comma-separated framework keys to analyse. "
            "Options: iso27001, disp, e8  (default: all three)"
        ),
    )
    parser.add_argument(
        "--output-dir",
        default="./reports",
        metavar="DIR",
        help="Directory for output JSON and Markdown reports  (default: ./reports)",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args   = parser.parse_args()

    # Validate framework keys
    framework_keys = [k.strip().lower() for k in args.frameworks.split(",") if k.strip()]
    invalid = [k for k in framework_keys if k not in AVAILABLE_FRAMEWORKS]
    if invalid:
        parser.error(
            f"Unknown framework key(s): {', '.join(invalid)}.  "
            f"Valid options: {', '.join(AVAILABLE_FRAMEWORKS)}"
        )
    if not framework_keys:
        parser.error("At least one framework key must be specified.")

    run_analysis(args.document, framework_keys, args.output_dir)


if __name__ == "__main__":
    main()
