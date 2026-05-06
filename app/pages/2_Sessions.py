"""Sessions — create, edit, end, attach notes to research sessions."""
from __future__ import annotations
import streamlit as st
import pandas as pd

from app.db import (
    list_sessions, get_session, create_session, update_session,
    add_note, list_notes,
)
from app.ui import inject_theme, page_header, badge, fmt_dt, render_session_sidebar

st.set_page_config(page_title="Sessions | vibrasim", layout="wide")
inject_theme()
render_session_sidebar()
page_header("Sessions", "A session is a coherent block of work — one question, one outcome")

# ----- Create new session ----------------------------------------------------
with st.expander("Create a new session", expanded=False):
    with st.form("new_session"):
        c1, c2 = st.columns(2)
        researcher = c1.text_input("Researcher", value="Michael")
        title = c2.text_input("Title", placeholder="e.g. Phase 5 substrate calibration")
        question = st.text_area(
            "Research question",
            placeholder="What are we trying to find out?",
            height=80,
        )
        hypothesis = st.text_area(
            "Hypothesis", placeholder="What do we expect?", height=80,
        )
        submitted = st.form_submit_button("Create session")
        if submitted:
            if not (researcher and title):
                st.error("Researcher and title are required.")
            else:
                sid = create_session(researcher, title, question or None, hypothesis or None)
                st.session_state["active_session_id"] = sid
                st.success(f"Created session. Active session set.")
                st.rerun()

st.markdown("---")

# ----- Sessions table --------------------------------------------------------
sessions = list_sessions(limit=500)

if not sessions:
    st.info("No sessions yet.")
    st.stop()

st.markdown("### All sessions")
df = pd.DataFrame([
    {
        "#": s["session_number"],
        "Title": s["title"],
        "Researcher": s["researcher"],
        "Started": fmt_dt(s["started_at"]),
        "Ended": fmt_dt(s["ended_at"]),
        "Configs": s["n_configs"],
        "Runs": s["n_runs"],
        "Status": s["status"],
        "id": str(s["id"]),
    }
    for s in sessions
])
st.dataframe(df.drop(columns=["id"]), use_container_width=True, hide_index=True)

st.markdown("---")

# ----- Detail view: pick + edit ---------------------------------------------
options = {f"#{s['session_number']} — {s['title']}": str(s["id"]) for s in sessions}
sel_label = st.selectbox("Inspect session", list(options.keys()))
sel_id = options[sel_label]
session = get_session(sel_id)

if not session:
    st.warning("Session not found.")
    st.stop()

c1, c2 = st.columns([2, 1])

with c1:
    st.markdown(f"### Session #{session['session_number']} — {session['title']}")
    st.markdown(
        f"Researcher: **{session['researcher']}**  ·  Started: {fmt_dt(session['started_at'])}  ·  "
        f"Status: {badge(session['status'])}",
        unsafe_allow_html=True,
    )
    with st.form("edit_session"):
        new_title = st.text_input("Title", value=session["title"])
        new_question = st.text_area("Research question", value=session.get("question") or "", height=80)
        new_hypothesis = st.text_area("Hypothesis", value=session.get("hypothesis") or "", height=80)
        new_outcome = st.text_area("Outcome", value=session.get("outcome") or "", height=100)
        new_notes = st.text_area("Free-form notes", value=session.get("notes") or "", height=100)
        new_status = st.selectbox(
            "Status",
            ["active", "paused", "completed", "abandoned"],
            index=["active", "paused", "completed", "abandoned"].index(session["status"]),
        )
        c_save, c_set, c_end = st.columns(3)
        save = c_save.form_submit_button("Save changes")
        set_active = c_set.form_submit_button("Set as active")
        end_session = c_end.form_submit_button("Mark completed")
        if save:
            fields = {
                "title": new_title,
                "question": new_question or None,
                "hypothesis": new_hypothesis or None,
                "outcome": new_outcome or None,
                "notes": new_notes or None,
                "status": new_status,
            }
            update_session(sel_id, **fields)
            st.success("Saved.")
            st.rerun()
        if set_active:
            st.session_state["active_session_id"] = sel_id
            st.success("Active session updated.")
        if end_session:
            update_session(sel_id, status="completed")
            st.success("Session marked completed.")
            st.rerun()

with c2:
    st.markdown("### Notes")
    with st.form("add_note"):
        body = st.text_area("New note", height=100)
        tag = st.selectbox("Tag", ["", "observation", "decision", "todo", "result"])
        if st.form_submit_button("Add note") and body.strip():
            add_note(sel_id, body, tag or None)
            st.rerun()
    notes = list_notes(sel_id)
    if not notes:
        st.caption("No notes yet.")
    else:
        for n in notes:
            tag_html = f"<span style='color:#2563eb;font-size:0.75rem;'>[{n['tag']}]</span> " if n.get("tag") else ""
            st.markdown(
                f"<div style='border-left:3px solid #e5e7eb;padding:0.25rem 0.75rem;margin:0.5rem 0;'>"
                f"<div style='font-size:0.75rem;color:#6b7280;'>{fmt_dt(n['created_at'])}</div>"
                f"<div>{tag_html}{n['body']}</div></div>",
                unsafe_allow_html=True,
            )
