"""vibrasim research dashboard — entry point.

Run with:
    streamlit run app/main.py
"""
from __future__ import annotations
import streamlit as st

from app.db import health_check, list_sessions
from app.ui import inject_theme, fmt_dt, fmt_id, badge, render_session_sidebar

st.set_page_config(
    page_title="vibrasim research",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()

st.markdown(
    "<div style='border-bottom:2px solid #2563eb;padding-bottom:0.5rem;margin-bottom:1.25rem;'>"
    "<h1 style='margin:0;border:none;padding:0;font-size:1.75rem;font-weight:600;'>"
    "vibrasim research dashboard</h1>"
    "<p style='color:#6b7280;margin:0.35rem 0 0;'>Track sessions, configurations, runs, "
    "amendments, and acceptance criteria for the vibration-substrate research programme.</p>"
    "</div>",
    unsafe_allow_html=True,
)

# ----- DB health -------------------------------------------------------------
ok, msg = health_check()
if not ok:
    st.error(f"Database connection failed: {msg}")
    st.markdown(
        "Ensure PostgreSQL is reachable at the DSN in `VIBRASIM_DSN` "
        "and that `db/schema.sql` and `db/seed.sql` have been applied. "
        "See `db/README.md` for setup."
    )
    st.stop()

st.success("Database connection healthy.")

render_session_sidebar()

with st.sidebar:
    st.markdown("---")
    st.markdown("### Navigation")
    st.markdown(
        "Use the page list above to move between Dashboard, Sessions, Config, "
        "Runs, Results, Amendments, and Acceptance."
    )

# ----- Quick overview card --------------------------------------------------
sessions = list_sessions(limit=10)
st.markdown("## Recent sessions")
if not sessions:
    st.info("No research sessions recorded yet.")
else:
    cols = st.columns([1, 4, 2, 1, 1, 1, 2])
    for label, val in zip(
        ["#", "Title", "Researcher", "Configs", "Runs", "Notes", "Status"],
        cols,
    ):
        val.markdown(f"**{label}**")
    for s in sessions:
        c = st.columns([1, 4, 2, 1, 1, 1, 2])
        c[0].write(s["session_number"])
        c[1].write(s["title"])
        c[2].write(s["researcher"])
        c[3].write(s["n_configs"])
        c[4].write(s["n_runs"])
        c[5].write(s["n_notes"])
        c[6].markdown(badge(s["status"]), unsafe_allow_html=True)

st.markdown("---")
st.caption(
    "vibrasim research dashboard — Postgres-backed session log for the "
    "vibration-substrate research programme."
)
