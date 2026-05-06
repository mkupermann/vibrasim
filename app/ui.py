"""Shared UI helpers — theme injection, badges, formatting."""
from __future__ import annotations
from pathlib import Path
import streamlit as st

from app.db import list_sessions, create_session

THEME_PATH = Path(__file__).parent / "theme" / "style.css"


def inject_theme() -> None:
    """Inject the dashboard's custom CSS once per page."""
    if THEME_PATH.exists():
        st.markdown(f"<style>{THEME_PATH.read_text()}</style>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str | None = None) -> None:
    if subtitle:
        st.markdown(
            f"<div style='border-bottom:2px solid #2563eb;padding-bottom:0.5rem;margin-bottom:1.25rem;'>"
            f"<h1 style='margin:0;border:none;padding:0;font-size:1.75rem;font-weight:600;'>{title}</h1>"
            f"<p style='color:#6b7280;margin:0.35rem 0 0;'>{subtitle}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f"# {title}")


def badge(status: str, label: str | None = None) -> str:
    """Return an HTML badge span for the given status."""
    cls = f"vs-badge vs-badge-{status.replace('_', '-')}"
    text = (label or status).replace("_", " ")
    return f"<span class='{cls}'>{text}</span>"


def render_badge(status: str, label: str | None = None) -> None:
    st.markdown(badge(status, label), unsafe_allow_html=True)


def fmt_dt(dt) -> str:
    if dt is None:
        return "-"
    return dt.strftime("%Y-%m-%d %H:%M")


def fmt_id(uid) -> str:
    """Short representation for UUIDs."""
    if uid is None:
        return "-"
    s = str(uid)
    return s[:8]


def render_session_sidebar() -> str | None:
    """Render the 'Active session' picker in the sidebar of every page.

    Always available — even on pages other than Sessions. Returns the
    currently-active session id (or None if there are no sessions).
    """
    with st.sidebar:
        st.markdown("### Active session")
        sessions = list_sessions(limit=200)
        if not sessions:
            st.caption("No sessions yet.")
            with st.form("sb_create_session", clear_on_submit=True):
                t = st.text_input("Title", placeholder="e.g. Phase 5 calibration")
                r = st.text_input("Researcher", value="Michael")
                if st.form_submit_button("Create + activate"):
                    if t and r:
                        sid = create_session(r, t)
                        st.session_state["active_session_id"] = sid
                        st.rerun()
            return None
        active = st.session_state.get("active_session_id")
        options = {f"#{s['session_number']} — {s['title']}": str(s["id"]) for s in sessions}
        labels = list(options.keys())
        idx = 0
        if active:
            for i, label in enumerate(labels):
                if options[label] == str(active):
                    idx = i
                    break
        choice = st.selectbox("Pick session", labels, index=idx, key="sb_pick_session")
        st.session_state["active_session_id"] = options[choice]
        return options[choice]


def require_active_session() -> str | None:
    """Return the active session id, rendering the sidebar picker if needed.

    Pages call this near the top. The picker is always rendered in the sidebar
    so the user can switch sessions or create a new one without leaving the page.
    """
    sid = render_session_sidebar()
    if not sid:
        st.warning(
            "No active research session. Create one in the sidebar (or on the "
            "Sessions page) before continuing."
        )
        return None
    return sid
