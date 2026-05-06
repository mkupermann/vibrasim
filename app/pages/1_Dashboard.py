"""Dashboard — programme-level snapshot."""
from __future__ import annotations
import streamlit as st
import pandas as pd

from app.db import (
    list_sessions, list_runs, list_amendments, get_acceptance_dashboard,
)
from app.ui import inject_theme, page_header, badge, render_session_sidebar

st.set_page_config(page_title="Dashboard | vibrasim", layout="wide")
inject_theme()
render_session_sidebar()
page_header("Dashboard", "Programme-level snapshot of the research state")

sessions = list_sessions(limit=500)
runs = list_runs(limit=500)
amendments = list_amendments()
acceptance = get_acceptance_dashboard()

# ----- Top metrics -----------------------------------------------------------
c = st.columns(5)
c[0].metric("Sessions", len(sessions))
c[1].metric("Runs", len(runs))
c[2].metric("Amendments open", sum(1 for a in amendments if a["status"] in ("proposed", "in_progress")))
c[3].metric(
    "Acceptance met",
    sum(r["n_met"] for r in acceptance),
    delta=f"of {sum(r['n_total'] for r in acceptance)} total",
    delta_color="off",
)
c[4].metric(
    "Active phase",
    "5"
    if any(r["phase"] == 5 and r["n_met"] == 0 for r in acceptance)
    else "-",
)

st.markdown("---")

# ----- Acceptance progress per phase ----------------------------------------
st.markdown("### Acceptance progress by phase")
if acceptance:
    df = pd.DataFrame(acceptance)
    df = df.rename(columns={
        "phase": "Phase", "n_total": "Total", "n_met": "Met",
        "n_partial": "Partial", "n_pending": "Pending", "n_blocked": "Blocked",
    })
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No acceptance criteria recorded.")

# ----- Recent runs -----------------------------------------------------------
st.markdown("### Recent runs")
if runs:
    df = pd.DataFrame([
        {
            "started": r["started_at"],
            "config": r["config_name"],
            "duration_s": r["duration_s"],
            "wall_s": r["wall_s"],
            "status": r["status"],
        }
        for r in runs[:15]
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No runs yet.")

# ----- Amendments status -----------------------------------------------------
st.markdown("### Amendments")
if amendments:
    cols = st.columns([1, 4, 2, 2])
    for label, col in zip(["#", "Title", "Section", "Status"], cols):
        col.markdown(f"**{label}**")
    for a in amendments:
        c = st.columns([1, 4, 2, 2])
        c[0].write(a["number"])
        c[1].write(a["title"])
        c[2].write(a.get("spec_section") or "-")
        c[3].markdown(badge(a["status"]), unsafe_allow_html=True)
else:
    st.info("No amendments recorded.")
