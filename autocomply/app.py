"""
AutoComply — Streamlit UI  (Palantir Blueprint dark theme)

Run with:  streamlit run app.py
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from frameworks.disp_controls import get_controls as get_disp
from frameworks.essential_eight import get_controls as get_e8
from frameworks.iso27001_controls import get_controls as get_iso27001
from ingestion.document_loader import load_document_from_bytes
from nlp.embedder import Embedder
from nlp.matcher import (
    STATUS_COVERED,
    STATUS_MISSING,
    STATUS_PARTIAL,
    match_controls_to_document,
)
from reporting.report_generator import (
    build_full_report,
    export_json,
    export_markdown,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Page config — must be the very first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AutoComply | Defence Compliance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Palantir Blueprint dark-theme CSS injection
# ─────────────────────────────────────────────────────────────────────────────
BLUEPRINT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Design tokens ──────────────────────────────────────────────────── */
:root {
  --bg0:  #111418;
  --bg1:  #1C2127;
  --bg2:  #252A31;
  --bg3:  #2F343C;
  --bg4:  #383E47;
  --bg5:  #404854;
  --g1:   #5F6B7C;
  --g2:   #738091;
  --g3:   #8F99A8;
  --g4:   #ABB3BF;
  --g5:   #C5CBD3;
  --fg:   #F6F7F9;
  --blue1: #184A90;
  --blue2: #215DB0;
  --blue3: #2D72D2;
  --blue4: #4C90F0;
  --blue5: #8ABBFF;
  --green2: #1C6E42;
  --green3: #238551;
  --green4: #32A467;
  --green5: #72CA9B;
  --amber2: #935610;
  --amber3: #C87619;
  --amber4: #EC9A3C;
  --amber5: #FBB360;
  --red2:  #AC2F33;
  --red3:  #CD4246;
  --red4:  #E76A6E;
  --red5:  #FA999C;
  --border:  rgba(255,255,255,0.08);
  --border2: rgba(255,255,255,0.14);
  --border3: rgba(255,255,255,0.20);
  --shadow:  0 2px 6px rgba(0,0,0,0.4);
  --shadow2: 0 4px 14px rgba(0,0,0,0.55);
  --radius: 3px;
  --ui:   'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
}

/* ── Global ─────────────────────────────────────────────────────────── */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background-color: var(--bg1) !important;
  font-family: var(--ui) !important;
  color: var(--fg) !important;
}
* { box-sizing: border-box; }

/* ── Sidebar ─────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background-color: var(--bg0) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stMarkdown p {
  color: var(--g1) !important;
  font-family: var(--mono) !important;
  font-size: 10px !important;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin: 0;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  color: var(--g3) !important;
  font-family: var(--mono) !important;
  font-size: 10px !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.14em !important;
}
[data-testid="stSidebar"] hr {
  border-color: var(--border) !important;
  margin: 10px 0 !important;
}
[data-testid="stSidebar"] label {
  color: var(--g4) !important;
  font-family: var(--mono) !important;
  font-size: 10px !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
}

/* ── Main block container ─────────────────────────────────────────────── */
.main .block-container {
  padding-top: 0 !important;
  padding-left: 1.5rem !important;
  padding-right: 1.5rem !important;
  max-width: 100% !important;
}

/* ── Headings ─────────────────────────────────────────────────────────── */
h1, h2, h3, h4 {
  color: var(--fg) !important;
  font-family: var(--ui) !important;
  font-weight: 600 !important;
}
h2 { font-size: 16px !important; letter-spacing: 0.02em; }
h3 { font-size: 13px !important; text-transform: uppercase; letter-spacing: 0.08em; color: var(--g4) !important; }
p  { color: var(--g4) !important; font-size: 13px !important; line-height: 1.5 !important; }

/* ── Primary action button ────────────────────────────────────────────── */
.stButton > button[kind="primary"] {
  background: var(--blue3) !important;
  color: var(--fg) !important;
  border: none !important;
  border-radius: var(--radius) !important;
  font-family: var(--mono) !important;
  font-size: 11px !important;
  font-weight: 600 !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  height: 32px !important;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.07), var(--shadow) !important;
  transition: background 0.1s ease !important;
}
.stButton > button[kind="primary"]:hover { background: var(--blue2) !important; }
.stButton > button[kind="primary"]:active { background: var(--blue1) !important; }
.stButton > button[kind="primary"]:disabled {
  background: var(--bg4) !important;
  color: var(--g1) !important;
  cursor: not-allowed !important;
}

/* Secondary / default button */
.stButton > button:not([kind="primary"]) {
  background: var(--bg3) !important;
  color: var(--g4) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--radius) !important;
  font-family: var(--mono) !important;
  font-size: 11px !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
  height: 32px !important;
}
.stButton > button:not([kind="primary"]):hover {
  background: var(--bg4) !important;
  border-color: var(--border3) !important;
  color: var(--fg) !important;
}

/* ── Download buttons ─────────────────────────────────────────────────── */
[data-testid="stDownloadButton"] > button {
  background: var(--bg3) !important;
  border: 1px solid var(--border2) !important;
  color: var(--blue5) !important;
  font-family: var(--mono) !important;
  font-size: 10px !important;
  text-transform: uppercase !important;
  letter-spacing: 0.09em !important;
  height: 32px !important;
  border-radius: var(--radius) !important;
}
[data-testid="stDownloadButton"] > button:hover {
  background: var(--bg4) !important;
  border-color: var(--blue3) !important;
}

/* ── Checkboxes ───────────────────────────────────────────────────────── */
[data-testid="stCheckbox"] > label {
  font-family: var(--mono) !important;
  font-size: 11px !important;
  color: var(--g4) !important;
  text-transform: uppercase !important;
  letter-spacing: 0.07em !important;
}

/* ── File uploader ────────────────────────────────────────────────────── */
[data-testid="stFileUploadDropzone"] {
  background: var(--bg2) !important;
  border: 1px dashed rgba(76,144,240,0.35) !important;
  border-radius: var(--radius) !important;
}
[data-testid="stFileUploadDropzone"]:hover {
  border-color: var(--blue3) !important;
  background: var(--bg3) !important;
}
[data-testid="stFileUploadDropzone"] p,
[data-testid="stFileUploadDropzone"] span,
[data-testid="stFileUploadDropzone"] small {
  color: var(--g2) !important;
  font-family: var(--mono) !important;
  font-size: 10px !important;
}

/* ── Metrics ──────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-top: 2px solid var(--blue3) !important;
  border-radius: var(--radius) !important;
  padding: 14px 16px !important;
}
[data-testid="stMetricLabel"] > div {
  color: var(--g2) !important;
  font-family: var(--mono) !important;
  font-size: 9px !important;
  text-transform: uppercase !important;
  letter-spacing: 0.12em !important;
}
[data-testid="stMetricValue"] > div {
  color: var(--fg) !important;
  font-family: var(--mono) !important;
  font-size: 1.55rem !important;
  font-weight: 500 !important;
}
[data-testid="stMetricDelta"] { display: none !important; }

/* ── Tabs ─────────────────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
  background: transparent !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 0 !important;
  padding: 0 !important;
}
[data-testid="stTabs"] [role="tab"] {
  background: transparent !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0 !important;
  color: var(--g2) !important;
  font-family: var(--mono) !important;
  font-size: 10px !important;
  font-weight: 500 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.1em !important;
  padding: 10px 18px !important;
  margin: 0 !important;
  transition: all 0.1s !important;
}
[data-testid="stTabs"] [role="tab"]:hover {
  color: var(--g5) !important;
  background: var(--bg3) !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
  color: var(--blue5) !important;
  border-bottom-color: var(--blue3) !important;
  background: transparent !important;
}

/* ── DataFrames ───────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  overflow: hidden !important;
}
[data-testid="stDataFrame"] iframe { background: var(--bg2) !important; }

/* ── Alerts ───────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
  border-radius: var(--radius) !important;
  font-family: var(--mono) !important;
  font-size: 11px !important;
  letter-spacing: 0.04em !important;
  border: none !important;
  border-left: 3px solid !important;
}
[data-testid="stAlert"][data-baseweb="notification"] {
  background: rgba(44,114,210,0.1) !important;
  border-left-color: var(--blue3) !important;
  color: var(--blue5) !important;
}
div[data-testid="stSuccessMessage"],
[class*="stSuccess"] {
  background: rgba(35,133,81,0.1) !important;
  border-left: 3px solid var(--green4) !important;
  color: var(--green5) !important;
  font-family: var(--mono) !important;
  font-size: 11px !important;
  border-radius: var(--radius) !important;
}
div[data-testid="stErrorMessage"],
[class*="stError"] {
  background: rgba(205,66,70,0.1) !important;
  border-left: 3px solid var(--red3) !important;
  color: var(--red5) !important;
  font-family: var(--mono) !important;
  font-size: 11px !important;
}

/* ── Spinner ──────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] > div { border-top-color: var(--blue4) !important; }
[data-testid="stSpinner"] p { color: var(--g3) !important; font-family: var(--mono) !important; font-size: 11px !important; }

/* ── Dividers ─────────────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; margin: 1rem 0 !important; }

/* ── Scrollbars ───────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg1); }
::-webkit-scrollbar-thumb { background: var(--bg5); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--g1); }

/* ── Hide Streamlit chrome ────────────────────────────────────────────── */
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden !important; height: 0 !important; }

/* ── Sidebar caption ──────────────────────────────────────────────────── */
[data-testid="stSidebar"] .stCaption {
  color: var(--g1) !important;
  font-family: var(--mono) !important;
  font-size: 9px !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
}
</style>
"""

# ─────────────────────────────────────────────────────────────────────────────
# HTML component builders
# ─────────────────────────────────────────────────────────────────────────────

def _topbar(doc_name: str = "", clause_count: int = 0) -> str:
    # All styles must stay on ONE line — Streamlit's CommonMark parser treats
    # 4-space-indented lines inside an f-string as fenced code blocks.
    if doc_name:
        status_html = f'<span style="color:#32A467;font-size:10px;font-weight:600;letter-spacing:0.1em">● DOCUMENT LOADED</span>'
        doc_badge   = f'<span style="color:#5F6B7C;font-size:10px;letter-spacing:0.06em;font-family:\'JetBrains Mono\',monospace">{doc_name}&nbsp;·&nbsp;{clause_count:,} clauses</span>&nbsp;&nbsp;'
    else:
        status_html = '<span style="color:#5F6B7C;font-size:10px;font-weight:600;letter-spacing:0.1em">● AWAITING INPUT</span>'
        doc_badge   = ""

    classification = '<div style="border:1px solid rgba(231,106,110,0.35);color:#E76A6E;font-size:9px;font-weight:700;letter-spacing:0.14em;padding:2px 8px;border-radius:2px">OFFICIAL USE ONLY</div>'

    return (
        '<div style="background:#111418;border-bottom:1px solid rgba(255,255,255,0.07);display:flex;align-items:center;justify-content:space-between;padding:0 24px;height:46px;margin:-0.5rem -1.5rem 1.5rem -1.5rem;font-family:\'JetBrains Mono\',monospace">'
        '<div style="display:flex;align-items:center;gap:14px">'
        '<div style="color:#4C90F0;font-size:13px;font-weight:700;letter-spacing:0.16em">AUTO<span style="color:#F6F7F9">COMPLY</span></div>'
        '<div style="width:1px;height:18px;background:rgba(255,255,255,0.08)"></div>'
        '<div style="color:#5F6B7C;font-size:9px;letter-spacing:0.14em;text-transform:uppercase">Defence Compliance Gap Analyser &nbsp;·&nbsp; v1.0</div>'
        '</div>'
        f'<div style="display:flex;align-items:center;gap:14px">{doc_badge}{status_html}&nbsp;&nbsp;{classification}</div>'
        '</div>'
    )


def _section_label(text: str, sub: str = "") -> str:
    # Single-line styles only — avoids CommonMark indented-code-block misparse
    sub_html = f'<div style="color:#5F6B7C;font-size:9px;letter-spacing:0.08em;margin-top:2px">{sub}</div>' if sub else ""
    return (
        '<div style="border-left:3px solid #2D72D2;padding:3px 0 3px 12px;margin-bottom:14px;font-family:\'JetBrains Mono\',monospace">'
        f'<div style="color:#F6F7F9;font-size:11px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase">{text}</div>'
        f'{sub_html}'
        '</div>'
    )


def _score_card(fw_name: str, icon: str, score: float,
                covered: int, partial: int, missing: int, total: int) -> str:
    colour  = "#32A467" if score >= 70 else "#EC9A3C" if score >= 40 else "#E76A6E"
    pct_cov = covered / total * 100 if total else 0
    pct_par = partial / total * 100 if total else 0
    pct_mis = missing / total * 100 if total else 0
    return (
        '<div style="background:#252A31;border:1px solid rgba(255,255,255,0.08);border-top:2px solid #2D72D2;border-radius:3px;padding:18px 20px;font-family:\'JetBrains Mono\',monospace;height:100%">'
        '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px">'
        f'<div style="color:#738091;font-size:9px;font-weight:600;letter-spacing:0.14em;text-transform:uppercase">{fw_name}</div>'
        f'<div style="font-size:16px">{icon}</div>'
        '</div>'
        f'<div style="font-size:2.6rem;font-weight:700;color:{colour};line-height:1;margin-bottom:2px">{score}</div>'
        '<div style="color:#5F6B7C;font-size:8px;letter-spacing:0.12em;margin-bottom:14px">/ 100 COMPLIANCE SCORE</div>'
        '<div style="display:flex;height:4px;border-radius:2px;overflow:hidden;gap:1px;margin-bottom:12px">'
        f'<div style="width:{pct_cov:.1f}%;background:#32A467;height:4px"></div>'
        f'<div style="width:{pct_par:.1f}%;background:#EC9A3C;height:4px"></div>'
        f'<div style="width:{pct_mis:.1f}%;background:#E76A6E;height:4px"></div>'
        '</div>'
        '<div style="display:flex;gap:5px;flex-wrap:wrap">'
        f'<span style="background:rgba(50,164,103,0.12);color:#72CA9B;font-size:9px;font-weight:600;letter-spacing:0.07em;padding:2px 7px;border-radius:2px">✓ {covered} COV</span>'
        f'<span style="background:rgba(236,154,60,0.12);color:#FBB360;font-size:9px;font-weight:600;letter-spacing:0.07em;padding:2px 7px;border-radius:2px">~ {partial} PAR</span>'
        f'<span style="background:rgba(231,106,110,0.12);color:#FA999C;font-size:9px;font-weight:600;letter-spacing:0.07em;padding:2px 7px;border-radius:2px">✗ {missing} MIS</span>'
        '</div>'
        '</div>'
    )


def _landing_card(icon: str, name: str, count: int, desc: str) -> str:
    return (
        '<div style="background:#252A31;border:1px solid rgba(255,255,255,0.07);border-top:2px solid #2D72D2;border-radius:3px;padding:22px 20px;font-family:\'JetBrains Mono\',monospace;height:100%">'
        f'<div style="font-size:1.4rem;margin-bottom:10px">{icon}</div>'
        f'<div style="color:#F6F7F9;font-size:11px;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:4px">{name}</div>'
        f'<div style="color:#4C90F0;font-size:2rem;font-weight:700;line-height:1;margin-bottom:2px">{count}</div>'
        '<div style="color:#5F6B7C;font-size:9px;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:12px">Controls</div>'
        f'<div style="color:#738091;font-size:10px;line-height:1.55">{desc}</div>'
        '</div>'
    )


def _progress_bar(score: float) -> str:
    colour = "#32A467" if score >= 70 else "#EC9A3C" if score >= 40 else "#E76A6E"
    return (
        '<div style="background:#2F343C;border-radius:2px;height:5px;margin-bottom:18px;overflow:hidden">'
        f'<div style="background:{colour};width:{score}%;height:5px;border-radius:2px;transition:width 0.4s ease;box-shadow:0 0 6px {colour}66"></div>'
        '</div>'
    )


def _controls_table(results: List[Dict[str, Any]]) -> str:
    """Render the controls as a Blueprint-styled HTML table."""
    status_cfg = {
        STATUS_COVERED: ("#d1fae5", "#32A467", "#1C4532", "✓ COVERED"),
        STATUS_PARTIAL:  ("#fef3c7", "#EC9A3C", "#3D2405", "~ PARTIAL"),
        STATUS_MISSING:  ("#fee2e2", "#E76A6E", "#3B1219", "✗ MISSING"),
    }

    rows = ""
    for r in results:
        bg, colour, tag_bg, label = status_cfg.get(
            r["status"], ("#2F343C", "#ABB3BF", "#2F343C", r["status"])
        )
        clause = r["best_matching_clause"]
        if len(clause) > 220:
            clause = clause[:220] + "…"
        # escape any HTML in clause
        clause = clause.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        req    = r["control_text"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        rows += f"""
        <tr style="border-bottom:1px solid rgba(255,255,255,0.05)">
          <td style="padding:10px 12px;font-family:'JetBrains Mono',monospace;
                     font-size:10px;font-weight:600;color:#4C90F0;
                     white-space:nowrap;vertical-align:top">{r['control_id']}</td>
          <td style="padding:10px 12px;font-size:11px;color:#ABB3BF;
                     line-height:1.45;max-width:280px;vertical-align:top">{req}</td>
          <td style="padding:10px 12px;text-align:center;vertical-align:top;white-space:nowrap">
            <span style="background:{tag_bg};color:{colour};border:1px solid {colour}33;
                         font-family:'JetBrains Mono',monospace;font-size:9px;
                         font-weight:700;letter-spacing:0.1em;
                         padding:2px 8px;border-radius:2px">{label}</span>
          </td>
          <td style="padding:10px 12px;text-align:center;vertical-align:top;
                     font-family:'JetBrains Mono',monospace;font-size:10px;
                     color:{colour};white-space:nowrap">
            {r['confidence_score']:.0%}
          </td>
          <td style="padding:10px 12px;font-size:10px;color:#5F6B7C;
                     font-style:italic;max-width:320px;line-height:1.45;vertical-align:top">
            {clause if clause else '—'}
          </td>
        </tr>
        """

    return f"""
    <div style="border:1px solid rgba(255,255,255,0.07);border-radius:3px;overflow:hidden;margin-bottom:20px">
      <table style="width:100%;border-collapse:collapse;background:#1C2127">
        <thead>
          <tr style="background:#111418;border-bottom:1px solid rgba(255,255,255,0.1)">
            <th style="padding:9px 12px;font-family:'JetBrains Mono',monospace;font-size:9px;
                       color:#5F6B7C;font-weight:600;letter-spacing:0.12em;
                       text-transform:uppercase;text-align:left;white-space:nowrap">ID</th>
            <th style="padding:9px 12px;font-family:'JetBrains Mono',monospace;font-size:9px;
                       color:#5F6B7C;font-weight:600;letter-spacing:0.12em;
                       text-transform:uppercase;text-align:left">Requirement</th>
            <th style="padding:9px 12px;font-family:'JetBrains Mono',monospace;font-size:9px;
                       color:#5F6B7C;font-weight:600;letter-spacing:0.12em;
                       text-transform:uppercase;text-align:center;white-space:nowrap">Status</th>
            <th style="padding:9px 12px;font-family:'JetBrains Mono',monospace;font-size:9px;
                       color:#5F6B7C;font-weight:600;letter-spacing:0.12em;
                       text-transform:uppercase;text-align:center;white-space:nowrap">Score</th>
            <th style="padding:9px 12px;font-family:'JetBrains Mono',monospace;font-size:9px;
                       color:#5F6B7C;font-weight:600;letter-spacing:0.12em;
                       text-transform:uppercase;text-align:left">Best Match</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    """


# ─────────────────────────────────────────────────────────────────────────────
# Plotly dark theme
# ─────────────────────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#1C2127",
    plot_bgcolor="#1C2127",
    font=dict(family="JetBrains Mono, monospace", color="#ABB3BF", size=11),
    margin=dict(t=46, b=26, l=16, r=16),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(255,255,255,0.1)",
        borderwidth=1,
        font=dict(size=10),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        linecolor="rgba(255,255,255,0.1)",
        tickfont=dict(size=9),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        linecolor="rgba(255,255,255,0.1)",
        tickfont=dict(size=9),
    ),
)


# ─────────────────────────────────────────────────────────────────────────────
# Framework registry
# ─────────────────────────────────────────────────────────────────────────────
FRAMEWORKS: Dict[str, List[Dict[str, str]]] = {
    "ISO 27001":       get_iso27001(),
    "DISP":            get_disp(),
    "Essential Eight": get_e8(),
}
FW_ICONS = {
    "ISO 27001":       "📋",
    "DISP":            "🇦🇺",
    "Essential Eight": "🔐",
}
FW_DESC = {
    "ISO 27001":       "International information security standard — Annex A controls covering governance, access, cryptography, operations, and more.",
    "DISP":            "Australian Defence Industry Security Program — physical, personnel, information and cyber security requirements.",
    "Essential Eight": "ASD Essential Eight Maturity Level 2 — Australia's baseline cyber mitigation strategies.",
}


# ─────────────────────────────────────────────────────────────────────────────
# Cached model + control embeddings
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading NLP model and pre-computing control embeddings…")
def _load_embedder():
    embedder = Embedder()
    ctrl_embs: Dict[str, Any] = {}
    for fw_name, controls in FRAMEWORKS.items():
        texts = [c["control_text"] for c in controls]
        ctrl_embs[fw_name] = embedder.embed_controls(texts)
    return embedder, ctrl_embs


# ─────────────────────────────────────────────────────────────────────────────
# Per-framework tab renderer
# ─────────────────────────────────────────────────────────────────────────────
def _render_fw_tab(
    fw_name: str,
    results: List[Dict[str, Any]],
    summary: Dict[str, Any],
) -> None:
    score = summary["compliance_score"]

    # ── Score row ──────────────────────────────────────────────────────────
    st.markdown(_section_label("Coverage Overview"), unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Compliance Score",    f"{score} / 100")
    m2.metric("✓ Covered",  f"{summary['covered_count']}  ({summary['covered_pct']}%)")
    m3.metric("~ Partial",  f"{summary['partial_count']}  ({summary['partial_pct']}%)")
    m4.metric("✗ Missing",  f"{summary['missing_count']}  ({summary['missing_pct']}%)")

    st.markdown(_progress_bar(score), unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Left: table  |  Right: donut ──────────────────────────────────────
    col_table, col_chart = st.columns([2, 1], gap="large")

    with col_table:
        st.markdown(_section_label("Control Findings", f"{len(results)} controls assessed"), unsafe_allow_html=True)
        st.markdown(_controls_table(results), unsafe_allow_html=True)

    with col_chart:
        st.markdown(_section_label("Breakdown"), unsafe_allow_html=True)
        fig = go.Figure(
            go.Pie(
                labels=["Covered", "Partial", "Missing"],
                values=[summary["covered_count"], summary["partial_count"], summary["missing_count"]],
                hole=0.62,
                marker=dict(
                    colors=["#32A467", "#EC9A3C", "#E76A6E"],
                    line=dict(color="#1C2127", width=2),
                ),
                textinfo="label+percent",
                textfont=dict(size=9, family="JetBrains Mono, monospace"),
                hovertemplate="%{label}: %{value}<extra></extra>",
            )
        )
        fig.add_annotation(
            text=f"<b>{score}</b>",
            font=dict(size=22, color="#F6F7F9", family="JetBrains Mono, monospace"),
            showarrow=False, x=0.5, y=0.55,
        )
        fig.add_annotation(
            text="score",
            font=dict(size=9, color="#5F6B7C", family="JetBrains Mono, monospace"),
            showarrow=False, x=0.5, y=0.42,
        )
        fig.update_layout(**PLOTLY_LAYOUT, height=320, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

        # Mini stat cards
        for status, bg, fg, label, items in [
            (STATUS_COVERED, "rgba(50,164,103,0.10)",  "#32A467", "COVERED",  [r for r in results if r["status"] == STATUS_COVERED]),
            (STATUS_PARTIAL,  "rgba(236,154,60,0.10)",  "#EC9A3C", "PARTIAL",  [r for r in results if r["status"] == STATUS_PARTIAL]),
            (STATUS_MISSING,  "rgba(231,106,110,0.10)", "#E76A6E", "MISSING",  [r for r in results if r["status"] == STATUS_MISSING]),
        ]:
            ids = ", ".join(r["control_id"] for r in items) or "—"
            st.markdown(
                f"""<div style="background:{bg};border-left:2px solid {fg};border-radius:2px;
                    padding:8px 12px;margin-bottom:6px;font-family:'JetBrains Mono',monospace">
                  <div style="color:{fg};font-size:9px;font-weight:700;letter-spacing:0.1em">{label}</div>
                  <div style="color:#738091;font-size:9px;margin-top:3px;line-height:1.4">{ids}</div>
                </div>""",
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Main app
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    st.markdown(BLUEPRINT_CSS, unsafe_allow_html=True)

    # Pre-load model
    embedder, precomputed_embeddings = _load_embedder()

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            '<div style="padding:18px 0 4px;font-family:\'JetBrains Mono\',monospace;'
            'font-size:10px;font-weight:700;color:#5F6B7C;letter-spacing:0.2em;'
            'text-transform:uppercase">AutoComply</div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")

        st.markdown("### Frameworks")
        selected: Dict[str, bool] = {}
        for fw_name in FRAMEWORKS:
            selected[fw_name] = st.checkbox(
                fw_name,
                value=True,
                key=f"fw_{fw_name}",
            )
        active_fws = [k for k, v in selected.items() if v]

        st.markdown("---")
        st.markdown("### Document")
        uploaded = st.file_uploader(
            "Upload PDF or DOCX",
            type=["pdf", "docx"],
            help="Security policy document to assess.",
            label_visibility="collapsed",
        )
        st.markdown(
            '<div style="color:#5F6B7C;font-family:\'JetBrains Mono\',monospace;'
            'font-size:9px;letter-spacing:0.07em;margin-top:4px">PDF · DOCX</div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")
        analyse_btn = st.button(
            "Run Analysis",
            type="primary",
            disabled=(uploaded is None or not active_fws),
            use_container_width=True,
        )

        if not active_fws:
            st.warning("Select at least one framework.")

        st.markdown("---")
        # framework summary counts
        for fw_name in active_fws:
            n = len(FRAMEWORKS[fw_name])
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'font-family:\'JetBrains Mono\',monospace;font-size:9px;'
                f'color:#5F6B7C;padding:2px 0;letter-spacing:0.07em">'
                f'<span>{fw_name}</span><span style="color:#4C90F0">{n} ctrl</span></div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.caption("v1.0 · Australian Defence Sector")

    # ── Top bar ───────────────────────────────────────────────────────────────
    if not analyse_btn or uploaded is None:
        st.markdown(_topbar(), unsafe_allow_html=True)
        # Landing page
        st.markdown(_section_label("Compliance Frameworks", "Select frameworks in the sidebar"), unsafe_allow_html=True)
        cols = st.columns(3, gap="medium")
        for col, (fw_name, icon) in zip(cols, FW_ICONS.items()):
            with col:
                st.markdown(
                    _landing_card(icon, fw_name, len(FRAMEWORKS[fw_name]), FW_DESC[fw_name]),
                    unsafe_allow_html=True,
                )
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("Upload a security policy document (PDF or DOCX) and click **Run Analysis** to begin.")
        return

    # ── 1. Extract clauses ────────────────────────────────────────────────────
    with st.spinner("Extracting document clauses…"):
        try:
            clauses = load_document_from_bytes(uploaded.read(), uploaded.name)
        except Exception as exc:
            st.markdown(_topbar(), unsafe_allow_html=True)
            st.error(f"Document load failed: {exc}")
            return

    if not clauses:
        st.markdown(_topbar(), unsafe_allow_html=True)
        st.error("No text extracted from document — check the file is not scanned/image-only.")
        return

    st.markdown(_topbar(uploaded.name, len(clauses)), unsafe_allow_html=True)
    st.success(f"Document parsed — {len(clauses):,} clauses extracted from {uploaded.name}")

    # ── 2. Embed clauses ──────────────────────────────────────────────────────
    with st.spinner("Computing semantic embeddings…"):
        try:
            clause_embs = embedder.embed_clauses(clauses)
        except Exception as exc:
            st.error(f"Embedding failed: {exc}")
            return

    # ── 3. Gap analysis ───────────────────────────────────────────────────────
    all_results: Dict[str, List[Dict[str, Any]]] = {}
    with st.spinner("Running compliance gap analysis…"):
        for fw_name in active_fws:
            all_results[fw_name] = match_controls_to_document(
                FRAMEWORKS[fw_name], precomputed_embeddings[fw_name], clauses, clause_embs
            )

    # ── 4. Build report ───────────────────────────────────────────────────────
    report    = build_full_report(all_results, uploaded.name)
    summaries = report["framework_summaries"]
    overall   = report["report_metadata"]["overall_compliance_score"]

    # ── 5. Tabs ───────────────────────────────────────────────────────────────
    tab_labels = ["  ◈ Summary  "] + [
        f"  {FW_ICONS[fw]}  {fw}  " for fw in active_fws
    ]
    tabs = st.tabs(tab_labels)

    # ── Summary tab ───────────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown(_section_label("Overall Assessment", f"{len(active_fws)} frameworks · {sum(len(r) for r in all_results.values())} controls"), unsafe_allow_html=True)

        # Overall score bar
        ov_col = "#32A467" if overall >= 70 else "#EC9A3C" if overall >= 40 else "#E76A6E"
        st.markdown(
            f'<div style="font-family:\'JetBrains Mono\',monospace;'
            f'font-size:28px;font-weight:700;color:{ov_col};margin-bottom:4px">'
            f'{overall}<span style="font-size:14px;color:#5F6B7C"> / 100</span></div>'
            f'<div style="color:#5F6B7C;font-size:9px;letter-spacing:0.12em;'
            f'text-transform:uppercase;margin-bottom:10px">Overall Compliance Score</div>',
            unsafe_allow_html=True,
        )
        st.markdown(_progress_bar(overall), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        # Per-framework score cards
        st.markdown(_section_label("Framework Scores"), unsafe_allow_html=True)
        sc_cols = st.columns(len(active_fws), gap="medium")
        for col, fw_name in zip(sc_cols, active_fws):
            s = summaries[fw_name]
            with col:
                st.markdown(
                    _score_card(
                        fw_name, FW_ICONS[fw_name], s["compliance_score"],
                        s["covered_count"], s["partial_count"], s["missing_count"],
                        s["total_controls"],
                    ),
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # Stacked bar + radar side by side
        chart_left, chart_right = st.columns(2, gap="large")

        with chart_left:
            st.markdown(_section_label("Coverage by Framework"), unsafe_allow_html=True)
            fig_bar = go.Figure()
            for label, colour, key in [
                ("Covered", "#32A467", "covered_pct"),
                ("Partial",  "#EC9A3C", "partial_pct"),
                ("Missing",  "#E76A6E", "missing_pct"),
            ]:
                fig_bar.add_trace(go.Bar(
                    name=label,
                    x=active_fws,
                    y=[summaries[fw][key] for fw in active_fws],
                    marker_color=colour,
                    marker_line_color="rgba(0,0,0,0.3)",
                    marker_line_width=0.5,
                    hovertemplate=f"{label}: %{{y:.1f}}%<extra></extra>",
                ))
            layout_bar = {**PLOTLY_LAYOUT, "barmode": "stack", "height": 300}
            layout_bar["yaxis"] = {**layout_bar.get("yaxis", {}), "range": [0, 100], "ticksuffix": "%"}
            fig_bar.update_layout(**layout_bar)
            st.plotly_chart(fig_bar, use_container_width=True)

        with chart_right:
            st.markdown(_section_label("Missing Controls Heatmap"), unsafe_allow_html=True)
            # Bar chart of missing counts per framework
            fig_miss = go.Figure(go.Bar(
                x=active_fws,
                y=[summaries[fw]["missing_count"] for fw in active_fws],
                marker_color="#E76A6E",
                marker_line_color="rgba(0,0,0,0.3)",
                marker_line_width=0.5,
                text=[summaries[fw]["missing_count"] for fw in active_fws],
                textposition="outside",
                textfont=dict(size=10, color="#FA999C", family="JetBrains Mono, monospace"),
                hovertemplate="%{x}: %{y} missing<extra></extra>",
            ))
            layout_miss = {**PLOTLY_LAYOUT, "height": 300}
            layout_miss["yaxis"] = {**layout_miss.get("yaxis", {}), "title": "Missing Controls"}
            fig_miss.update_layout(**layout_miss)
            st.plotly_chart(fig_miss, use_container_width=True)

        # Summary table
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(_section_label("Summary Table"), unsafe_allow_html=True)
        rows_html = ""
        for fw in active_fws:
            s = summaries[fw]
            sc = s["compliance_score"]
            sc_colour = "#32A467" if sc >= 70 else "#EC9A3C" if sc >= 40 else "#E76A6E"
            rows_html += f"""
            <tr style="border-bottom:1px solid rgba(255,255,255,0.05)">
              <td style="padding:10px 14px;font-family:'JetBrains Mono',monospace;
                         font-size:10px;color:#4C90F0;white-space:nowrap">{FW_ICONS[fw]} {fw}</td>
              <td style="padding:10px 14px;font-family:'JetBrains Mono',monospace;
                         font-size:10px;color:#ABB3BF;text-align:center">{s['total_controls']}</td>
              <td style="padding:10px 14px;font-family:'JetBrains Mono',monospace;
                         font-size:10px;color:#32A467;text-align:center">
                {s['covered_count']} <span style="color:#5F6B7C">({s['covered_pct']}%)</span></td>
              <td style="padding:10px 14px;font-family:'JetBrains Mono',monospace;
                         font-size:10px;color:#EC9A3C;text-align:center">
                {s['partial_count']} <span style="color:#5F6B7C">({s['partial_pct']}%)</span></td>
              <td style="padding:10px 14px;font-family:'JetBrains Mono',monospace;
                         font-size:10px;color:#E76A6E;text-align:center">
                {s['missing_count']} <span style="color:#5F6B7C">({s['missing_pct']}%)</span></td>
              <td style="padding:10px 14px;font-family:'JetBrains Mono',monospace;
                         font-size:12px;font-weight:700;color:{sc_colour};text-align:center">{sc}</td>
            </tr>
            """
        st.markdown(f"""
        <div style="border:1px solid rgba(255,255,255,0.07);border-radius:3px;overflow:hidden">
          <table style="width:100%;border-collapse:collapse;background:#1C2127">
            <thead>
              <tr style="background:#111418;border-bottom:1px solid rgba(255,255,255,0.1)">
                <th style="padding:9px 14px;font-family:'JetBrains Mono',monospace;font-size:9px;
                           color:#5F6B7C;font-weight:600;letter-spacing:0.12em;
                           text-transform:uppercase;text-align:left">Framework</th>
                <th style="padding:9px 14px;font-family:'JetBrains Mono',monospace;font-size:9px;
                           color:#5F6B7C;font-weight:600;letter-spacing:0.12em;
                           text-transform:uppercase;text-align:center">Total</th>
                <th style="padding:9px 14px;font-family:'JetBrains Mono',monospace;font-size:9px;
                           color:#32A467;font-weight:600;letter-spacing:0.12em;
                           text-transform:uppercase;text-align:center">Covered</th>
                <th style="padding:9px 14px;font-family:'JetBrains Mono',monospace;font-size:9px;
                           color:#EC9A3C;font-weight:600;letter-spacing:0.12em;
                           text-transform:uppercase;text-align:center">Partial</th>
                <th style="padding:9px 14px;font-family:'JetBrains Mono',monospace;font-size:9px;
                           color:#E76A6E;font-weight:600;letter-spacing:0.12em;
                           text-transform:uppercase;text-align:center">Missing</th>
                <th style="padding:9px 14px;font-family:'JetBrains Mono',monospace;font-size:9px;
                           color:#5F6B7C;font-weight:600;letter-spacing:0.12em;
                           text-transform:uppercase;text-align:center">Score</th>
              </tr>
            </thead>
            <tbody>{rows_html}</tbody>
          </table>
        </div>
        """, unsafe_allow_html=True)

        # Export
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(_section_label("Export Report"), unsafe_allow_html=True)
        stem = uploaded.name.rsplit(".", 1)[0]
        dl1, dl2, _ = st.columns([1, 1, 2])
        with dl1:
            st.download_button(
                "⬇ JSON Report",
                data=export_json(report),
                file_name=f"autocomply_{stem}.json",
                mime="application/json",
                use_container_width=True,
            )
        with dl2:
            st.download_button(
                "⬇ Markdown Report",
                data=export_markdown(report),
                file_name=f"autocomply_{stem}.md",
                mime="text/markdown",
                use_container_width=True,
            )

    # ── Per-framework tabs ─────────────────────────────────────────────────────
    for i, fw_name in enumerate(active_fws):
        with tabs[i + 1]:
            st.markdown(
                _section_label(fw_name, f"{FW_DESC[fw_name]}"),
                unsafe_allow_html=True,
            )
            _render_fw_tab(fw_name, all_results[fw_name], summaries[fw_name])


if __name__ == "__main__":
    main()
