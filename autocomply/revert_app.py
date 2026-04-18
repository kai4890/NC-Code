with open("app.py", "r") as f:
    content = f.read()

# 1. Remove sidebar_visible init
content = content.replace(
    'initial_sidebar_state="expanded",\n)\n\nif "sidebar_visible" not in st.session_state:\n    st.session_state["sidebar_visible"] = True\n',
    'initial_sidebar_state="expanded",\n)\n'
)

# 2. Remove CSS overrides
content = content.replace(
    '\n[data-testid="stSidebar"][aria-expanded="false"] { display: none; }\n.sidebar-toggle { position: fixed; top: 14px; left: 14px; z-index: 999; }',
    ''
)

# 3. Restore sidebar block
old_sidebar_block = """    if st.button("☰"):
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
            st.caption("v1.1 · Australian Defence Sector")
    else:
        active_fws = st.session_state.get("selected_frameworks", [])
        uploaded = None
        analyse_btn = False"""

new_sidebar_block = """    # ── Sidebar ──────────────────────────────────────────────────────────────
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
        st.caption("v1.1 · Australian Defence Sector")"""

content = content.replace(old_sidebar_block, new_sidebar_block)

with open("app.py", "w") as f:
    f.write(content)

print("Reverted sidebar visibility changes in app.py")
