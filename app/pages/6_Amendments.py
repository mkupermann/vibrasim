"""Amendments — substrate amendment tracker."""
from __future__ import annotations
import streamlit as st
import pandas as pd

from app.db import (
    list_amendments, get_amendment, create_amendment, update_amendment_status,
    list_sessions,
)
from app.ui import inject_theme, page_header, badge, fmt_dt, render_session_sidebar

st.set_page_config(page_title="Amendments | vibrasim", layout="wide")
inject_theme()
render_session_sidebar()
page_header("Amendments", "Substrate-level amendments to CONCEPT.md and their decisions")

# ----- Filter ---------------------------------------------------------------
status_filter = st.radio(
    "Filter by status",
    ["all", "proposed", "in_progress", "implemented", "rejected", "deferred"],
    horizontal=True,
    index=0,
)
amendments = list_amendments(None if status_filter == "all" else status_filter)

if amendments:
    df = pd.DataFrame([
        {
            "#": a["number"],
            "Title": a["title"],
            "Section": a.get("spec_section") or "-",
            "Status": a["status"],
            "Proposed": fmt_dt(a["proposed_at"]),
            "Decided": fmt_dt(a.get("decided_at")),
        }
        for a in amendments
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No amendments at that status.")

st.markdown("---")

# ----- Detail view ----------------------------------------------------------
all_amendments = list_amendments()
if all_amendments:
    options = {f"{a['number']} — {a['title']}": str(a["id"]) for a in all_amendments}
    sel = st.selectbox("Inspect amendment", list(options.keys()))
    aid = options[sel]
    a = get_amendment(aid)

    if a:
        st.markdown(f"### {a['number']} — {a['title']}")
        st.markdown(f"Status: {badge(a['status'])}", unsafe_allow_html=True)
        st.markdown(f"**Section:** {a.get('spec_section') or '-'}")
        st.markdown("**Description**")
        st.write(a["description"])
        if a.get("motivation"):
            st.markdown("**Motivation**")
            st.write(a["motivation"])
        if a.get("notes"):
            st.markdown("**Notes**")
            st.write(a["notes"])

        # Decide action
        st.markdown("#### Decide / update")
        sessions = list_sessions(limit=200)
        with st.form(f"update_amendment_{aid}"):
            new_status = st.selectbox(
                "New status",
                ["proposed", "in_progress", "implemented", "rejected", "deferred"],
                index=["proposed", "in_progress", "implemented", "rejected", "deferred"].index(a["status"]),
            )
            sess_options = {"-": None}
            for s in sessions:
                sess_options[f"#{s['session_number']} — {s['title']}"] = str(s["id"])
            sess_label = st.selectbox("Decided in session", list(sess_options.keys()))
            commit = st.text_input("Implementation commit (SHA)", value=a.get("impl_commit") or "")
            new_notes = st.text_area("Notes", value=a.get("notes") or "", height=80)
            if st.form_submit_button("Apply"):
                update_amendment_status(
                    aid,
                    new_status,
                    decided_session=sess_options[sess_label],
                    impl_commit=commit or None,
                    notes=new_notes or None,
                )
                st.success("Updated.")
                st.rerun()

st.markdown("---")

# ----- Create new amendment -------------------------------------------------
with st.expander("Propose a new amendment"):
    sessions = list_sessions(limit=200)
    with st.form("new_amendment"):
        c1, c2 = st.columns([1, 3])
        number = c1.text_input("Number", placeholder="e.g. R5")
        title = c2.text_input("Title")
        section = st.text_input("Section in CONCEPT.md", placeholder="e.g. §4.7")
        description = st.text_area("Description", height=120)
        motivation = st.text_area("Motivation (empirical reason)", height=80)
        sess_options = {"-": None}
        for s in sessions:
            sess_options[f"#{s['session_number']} — {s['title']}"] = str(s["id"])
        sess_label = st.selectbox("Proposed in session", list(sess_options.keys()))
        if st.form_submit_button("Create"):
            if not (number and title and description):
                st.error("Number, title, and description are required.")
            else:
                create_amendment(
                    number, title, description,
                    spec_section=section or None,
                    motivation=motivation or None,
                    proposed_session=sess_options[sess_label],
                )
                st.success("Created.")
                st.rerun()
