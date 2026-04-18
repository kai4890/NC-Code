# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AutoComply** is an AI-powered compliance gap analysis tool for Australian Defence sector organizations. It analyzes security policy documents (PDF/DOCX) against compliance frameworks (ISO 27001, DISP, ASD Essential Eight) using semantic embeddings and cosine similarity matching.

## Running the Application

**Streamlit web UI** (interactive):
```bash
streamlit run app.py
```

**CLI** (headless/batch analysis):
```bash
python main.py policy.pdf --frameworks iso27001,disp,e8_ml2 --output-dir ./reports
```

Supported framework keys: `iso27001`, `disp`, `e8_ml1`, `e8_ml2`, `e8_ml3`

**Install dependencies**:
```bash
pip install -r requirements.txt
```

## Architecture

The system is a **multi-stage pipeline**:

```
Document (PDF/DOCX)
  → ingestion/document_loader.py   — extract & clean clauses
  → nlp/embedder.py                — embed clauses + controls (all-MiniLM-L6-v2)
  → nlp/matcher.py                 — cosine similarity → COVERED/PARTIAL/MISSING
  → reporting/report_generator.py  — JSON + Markdown export
  → app.py / main.py               — Streamlit UI or CLI output
```

Both `app.py` (Streamlit) and `main.py` (CLI) orchestrate the same underlying pipeline — they share the same modules but differ in I/O.

## Key Details

**Similarity thresholds** (in `nlp/matcher.py`):
- `COVERED` — score ≥ 0.65
- `PARTIAL` — 0.40 ≤ score < 0.65
- `MISSING` — score < 0.40

**Scoring model** (in `reporting/report_generator.py`): COVERED=1.0pt, PARTIAL=0.5pt, MISSING=0pt → percentage score.

**Embeddings**: L2-normalized so cosine similarity equals dot product. Model is a singleton loaded lazily (`nlp/embedder.py`). In Streamlit, `@st.cache_resource` ensures one model instance.

**Framework controls** are hardcoded Python dicts in `frameworks/`. Each module exposes a `get_controls()` function returning a list of `{control_id, control_text, framework}` dicts. Both `app.py` and `main.py` maintain a `FRAMEWORKS` / `AVAILABLE_FRAMEWORKS` registry dict mapping string keys to these getter functions.

## Adding a New Compliance Framework

1. Create `frameworks/new_framework.py` with a `get_controls() -> List[dict]` function
2. Add an entry to `AVAILABLE_FRAMEWORKS` in `main.py`
3. Add an entry to `FRAMEWORKS` in `app.py`

## Notable Constraints

- No config files — similarity thresholds and model name are hardcoded
- No database — all controls are version-controlled Python dicts
- `document_loader.py` strips classification markings (`UNCLASSIFIED`, `SECRET`, etc.) and page numbers from extracted text before embedding
