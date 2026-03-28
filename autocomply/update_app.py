with open("app.py", "r") as f:
    content = f.read()

# 1. Config block
content = content.replace(
    'initial_sidebar_state="expanded",\n)',
    'initial_sidebar_state="expanded",\n)\n\nif "sidebar_visible" not in st.session_state:\n    st.session_state["sidebar_visible"] = True'
)

# 2. CSS block
content = content.replace(
    '  letter-spacing: 0.08em !important;\n}\n</style>',
    '  letter-spacing: 0.08em !important;\n}\n\n[data-testid="stSidebar"][aria-expanded="false"] { display: none; }\n.sidebar-toggle { position: fixed; top: 14px; left: 14px; z-index: 999; }\n</style>'
)

# 3. Sidebar Block
old_sidebar_block = """    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            '<div style="padding:18px 0 4px;font-family:\\'JetBrains Mono\\',monospace;'
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
            '<div style="color:#5F6B7C;font-family:\\'JetBrains Mono\\',monospace;'
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
                f'font-family:\\'JetBrains Mono\\',monospace;font-size:9px;'
                f'color:#5F6B7C;padding:2px 0;letter-spacing:0.07em">'
                f'<span>{fw_name}</span><span style="color:#4C90F0">{{n}} ctrl</span></div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.caption("v1.0 · Australian Defence Sector")"""

new_sidebar_block = """    if st.button("☰"):
        st.session_state["sidebar_visible"] = not st.session_state["sidebar_visible"]

    # ── Sidebar ──────────────────────────────────────────────────────────────
    if st.session_state["sidebar_visible"]:
        with st.sidebar:
            st.markdown(
                '<div style="padding:18px 0 4px;font-family:\\'JetBrains Mono\\',monospace;'
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
                '<div style="color:#5F6B7C;font-family:\\'JetBrains Mono\\',monospace;'
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
                    f'font-family:\\'JetBrains Mono\\',monospace;font-size:9px;'
                    f'color:#5F6B7C;padding:2px 0;letter-spacing:0.07em">'
                    f'<span>{fw_name}</span><span style="color:#4C90F0">{{n}} ctrl</span></div>',
                    unsafe_allow_html=True,
                )

            st.markdown("---")
            st.caption("v1.0 · Australian Defence Sector")
    else:
        active_fws = st.session_state.get("selected_frameworks", [])
        uploaded = None
        analyse_btn = False"""

content = content.replace(old_sidebar_block, new_sidebar_block)

# 4. Invalidation Block
old_inval = """    # ── Invalidate cached results when a new file is uploaded ────────────────
    if uploaded is not None:
        _doc_key = (uploaded.name, uploaded.size)
        if st.session_state.get("_doc_key") != _doc_key:
            st.session_state.pop("results", None)
            st.session_state["_doc_key"] = _doc_key"""

new_inval = """    # ── Invalidate cached results when a new file is uploaded ────────────────
    if uploaded is not None:
        _doc_key = (uploaded.name, uploaded.size)
        if st.session_state.get("_doc_key") != _doc_key:
            st.session_state.pop("results", None)
            st.session_state.pop("analysis_results", None)
            st.session_state["_doc_key"] = _doc_key"""

content = content.replace(old_inval, new_inval)

# 5. Landing Page Block
old_landing = '    if not analyse_btn and "results" not in st.session_state:'
new_landing = '    if not analyse_btn and "analysis_results" not in st.session_state:'
content = content.replace(old_landing, new_landing)

# 6. Saving results
old_save = """        # Persist everything needed to render and export across reruns
        st.session_state["results"] = {
            "report":        report,
            "all_results":   all_results,
            "summaries":     summaries,
            "overall":       overall,
            "doc_name":      uploaded.name,
            "active_fws":    active_fws,
            "quality_label": quality_label,
            "n_clean":       n_clean,
            "n_removed":     n_removed,
            "removal_pct":   removal_pct,
            "json_str":      export_json(report),
            "md_str":        export_markdown(report),
        }"""

new_save = """        # Persist everything needed to render and export across reruns
        st.session_state["analysis_results"] = {
            "report":        report,
            "all_results":   all_results,
            "summaries":     summaries,
            "overall":       overall,
            "quality_label": quality_label,
            "n_clean":       n_clean,
            "n_removed":     n_removed,
            "removal_pct":   removal_pct,
            "json_str":      export_json(report),
            "md_str":        export_markdown(report),
        }
        st.session_state["selected_frameworks"] = active_fws
        st.session_state["document_name"] = uploaded.name
        st.session_state["clause_count"] = n_clean"""

content = content.replace(old_save, new_save)

# 7. Render Block
old_render = """    # ── Render from persisted session state ───────────────────────────────────
    if "results" not in st.session_state:
        return

    state         = st.session_state["results"]
    report        = state["report"]
    all_results   = state["all_results"]
    summaries     = state["summaries"]
    overall       = state["overall"]
    doc_name      = state["doc_name"]
    active_fws    = state["active_fws"]
    quality_label = state["quality_label"]
    n_clean       = state["n_clean"]
    n_removed     = state["n_removed"]
    removal_pct   = state["removal_pct"]"""

new_render = """    # ── Render from persisted session state ───────────────────────────────────
    if "analysis_results" not in st.session_state:
        return

    state         = st.session_state["analysis_results"]
    report        = state["report"]
    all_results   = state["all_results"]
    summaries     = state["summaries"]
    overall       = state["overall"]
    doc_name      = st.session_state["document_name"]
    active_fws    = st.session_state["selected_frameworks"]
    quality_label = state["quality_label"]
    n_clean       = st.session_state["clause_count"]
    n_removed     = state["n_removed"]
    removal_pct   = state["removal_pct"]"""

content = content.replace(old_render, new_render)

with open("app.py", "w") as f:
    f.write(content)

print("Updates applied to app.py")
