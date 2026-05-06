"""Acceptance — track CONCEPT.md §5 acceptance criteria per phase."""
from __future__ import annotations
import streamlit as st
import pandas as pd

from app.db import (
    list_acceptance_criteria, get_acceptance_dashboard, update_acceptance,
    list_runs,
)
from app.ui import inject_theme, page_header, badge, fmt_dt, fmt_id, render_session_sidebar

st.set_page_config(page_title="Acceptance | vibrasim", layout="wide")
inject_theme()
render_session_sidebar()
page_header("Acceptance criteria", "CONCEPT.md §5 acceptance status across all phases")

# ----- Phase summary --------------------------------------------------------
dash = get_acceptance_dashboard()
if dash:
    cols = st.columns(len(dash))
    for col, row in zip(cols, dash):
        col.markdown(
            "<div style='background:#fff;border:1px solid #e5e7eb;border-left:3px solid #2563eb;"
            "border-radius:8px;padding:0.85rem 1rem;text-align:center;'>"
            f"<div style='color:#6b7280;font-size:0.75rem;font-weight:600;letter-spacing:0.04em;"
            f"text-transform:uppercase;'>Phase {row['phase']}</div>"
            f"<div style='color:#1f2937;font-size:1.5rem;font-weight:600;line-height:1.1;margin-top:0.25rem;'>"
            f"{row['n_met']}<span style='color:#9ca3af;font-weight:400;'> / {row['n_total']}</span></div>"
            f"<div style='color:#6b7280;font-size:0.7rem;margin-top:0.25rem;'>"
            f"{row['n_partial']}P · {row['n_pending']}·</div>"
            "</div>",
            unsafe_allow_html=True,
        )

st.markdown("---")

# ----- Phase selector -------------------------------------------------------
phases_available = sorted({row["phase"] for row in dash}) if dash else []
if not phases_available:
    st.info("No acceptance criteria recorded.")
    st.stop()

phase_labels = ["all"] + [f"Phase {p}" for p in phases_available]
sel = st.radio("Filter", phase_labels, horizontal=True, index=0)
phase_filter = None if sel == "all" else int(sel.split()[-1])

criteria = list_acceptance_criteria(phase_filter)

# ----- Criteria table -------------------------------------------------------
df = pd.DataFrame([
    {
        "Phase": c["phase"],
        "Key": c["criterion_key"],
        "Description": c["description"],
        "Status": c["status"],
        "Updated": fmt_dt(c["last_updated"]),
    }
    for c in criteria
])
st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")

# ----- Update status --------------------------------------------------------
st.markdown("### Update criterion status")
options = {f"P{c['phase']} — {c['criterion_key']}": str(c["id"]) for c in criteria}
if not options:
    st.info("Nothing to update at this filter.")
else:
    sel = st.selectbox("Pick criterion", list(options.keys()))
    cid = options[sel]
    cur = next((c for c in criteria if str(c["id"]) == cid), None)
    if cur:
        st.markdown(f"**{cur['description']}**")
        st.markdown(f"Current: {badge(cur['status'])}", unsafe_allow_html=True)

        with st.form(f"update_{cid}"):
            new_status = st.selectbox(
                "New status",
                ["pending", "partially_met", "met", "not_reachable"],
                index=["pending", "partially_met", "met", "not_reachable"].index(cur["status"]),
            )
            runs = list_runs(limit=200)
            run_options = {"-": None}
            for r in runs:
                run_options[f"{fmt_id(r['id'])} — {r['config_name']}"] = str(r["id"])
            run_label = st.selectbox("Evidence run", list(run_options.keys()))
            evidence = st.text_area("Evidence notes", value=cur.get("evidence_notes") or "", height=100)
            if st.form_submit_button("Apply"):
                update_acceptance(
                    cid, new_status,
                    evidence_run_id=run_options[run_label],
                    evidence_notes=evidence or None,
                )
                st.success("Updated.")
                st.rerun()
