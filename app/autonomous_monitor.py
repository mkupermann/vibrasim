"""EQMOD — autonomous loop monitor (Streamlit).

Live dashboard that reads the autonomous loop's metrics CSV +
EMERGENCE / NEGATIVE_CONTROL JSON files. Does NOT spawn its own
substrate — it just reads the running loop's state from disk, so
running this alongside `agent.run_autonomous` is safe.

Run:
    uv run streamlit run app/autonomous_monitor.py --server.port 8505
    # open http://localhost:8505
"""
from __future__ import annotations
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


METRICS_PATH = Path.home() / ".eqmod" / "autonomous" / "metrics.csv"
MARKER_STATE_PATH = Path.home() / ".eqmod" / "autonomous" / "marker_state.json"
CONTROL_PATH = Path.home() / ".eqmod" / "autonomous" / "NEGATIVE_CONTROL.json"
SNAPSHOTS_DIR = Path.home() / ".eqmod" / "autonomous" / "snapshots"


st.set_page_config(page_title="EQMOD — Autonomous Loop Monitor", layout="wide")
st.title("EQMOD — Autonomous Loop Monitor")
st.caption(
    "Live read of the autonomous loop's metrics + emergence + "
    "negative-control state from disk. The substrate runs in a "
    "separate process; this page only displays it."
)


def _load_metrics() -> pd.DataFrame:
    if not METRICS_PATH.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(METRICS_PATH)
    except Exception:
        return pd.DataFrame()
    return df


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


# ----- Top status bar -----------------------------------------------------

emergence = _load_json(MARKER_STATE_PATH)
control = _load_json(CONTROL_PATH)

col_status, col_em, col_ctl = st.columns([2, 2, 2])
with col_status:
    if METRICS_PATH.exists():
        mtime = METRICS_PATH.stat().st_mtime
        age = time.time() - mtime
        if age < 30:
            st.success(f"🟢 Live — last metric {age:.0f}s ago")
        elif age < 120:
            st.warning(f"🟡 Stale — last metric {age:.0f}s ago")
        else:
            st.error(f"🔴 Inactive — last metric {age/60:.1f} min ago")
    else:
        st.info("⚪ No metrics file. Start `python -m agent.run_autonomous`.")

with col_em:
    if emergence:
        st.success(
            f"🟢 EMERGENCE on cycle {emergence.get('cycle', '?')} — "
            f"{emergence.get('markers', {}).get('count', 0)}/5 markers"
        )
    else:
        st.info("⏳ No emergence yet")

with col_ctl:
    if control:
        passed = control.get("pass", False)
        max_seen = control.get("max_markers_seen", "?")
        if passed:
            st.success(f"✓ Negative control PASSED (max {max_seen}/5)")
        else:
            st.error(f"✗ Negative control FAILED (max {max_seen}/5)")
    else:
        st.info("Run `python -m agent.run_negative_control` for the discriminating test.")


# ----- Metrics --------------------------------------------------------

st.divider()
df = _load_metrics()

if df.empty:
    st.warning("No metrics rows yet. The loop typically writes its first row after the first cycle (~10-30s).")
else:
    awake = df[df["phase"] == "awake"].copy() if "phase" in df.columns else df

    # Quick numeric strip
    if not awake.empty:
        latest = awake.iloc[-1]
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Cycle", int(latest["cycle"]))
        m2.metric("Atoms", int(latest["n_atoms"]))
        m3.metric("Bridges", int(latest["n_bridges"]))
        m4.metric("Patterns", int(latest["n_patterns"]))
        m5.metric("Pred. error", f"{float(latest['prediction_error']):.3f}")
        m6.metric("BTSP", f"{float(latest['btsp_potentiation']):.1f}")

    st.subheader("📈 Cycle-by-cycle trajectory")
    if not awake.empty and len(awake) > 0:
        chart_data = awake.set_index("cycle")[
            ["n_atoms", "n_bridges", "n_patterns"]
        ]
        st.line_chart(chart_data, height=240)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Prediction error**")
            st.line_chart(
                awake.set_index("cycle")[["prediction_error"]], height=200
            )
        with col_b:
            st.markdown("**BTSP potentiation (self-modification)**")
            st.line_chart(
                awake.set_index("cycle")[["btsp_potentiation"]], height=200
            )

        st.markdown("**Firings per cycle**")
        st.line_chart(
            awake.set_index("cycle")[["fires_in_cycle"]], height=200
        )

    # Tail of the metrics CSV
    with st.expander(f"Recent metrics rows (last 15 of {len(df)})"):
        st.dataframe(df.tail(15), use_container_width=True)


# ----- EMERGENCE detail ----------------------------------------------

if emergence:
    st.divider()
    st.subheader("🎯 marker_state.json")
    markers = emergence.get("markers", {})
    cols = st.columns(5)
    for i, key in enumerate([
        "1_self_model_nonempty",
        "2_workspace_winner",
        "3_prediction_loop_closed",
        "4_self_modification_fired",
        "5_pattern_repertoire_growing",
    ]):
        ok = bool(markers.get(key, False))
        with cols[i]:
            label = key.split("_", 1)[1].replace("_", " ")
            (st.success if ok else st.error)(
                f"{'✅' if ok else '❌'} {label}"
            )
    st.caption(emergence.get("interpretation", ""))


# ----- Snapshot list -------------------------------------------------

if SNAPSHOTS_DIR.exists():
    snapshots = sorted(SNAPSHOTS_DIR.glob("autonomous_cycle_*.npz"))
    if snapshots:
        st.divider()
        st.subheader(f"💾 Snapshots ({len(snapshots)})")
        st.caption(
            f"From `{SNAPSHOTS_DIR}`. Each snapshot persists the substrate's "
            "full state (atoms + bridges + eligibility traces + workspace + "
            "self-model) for offline analysis."
        )
        with st.expander("Snapshot list"):
            for s in snapshots[-10:]:
                size_kb = s.stat().st_size / 1024
                st.text(f"{s.name}  ({size_kb:.0f} KB)")


# ----- Auto-refresh ---------------------------------------------------

st.divider()
auto_refresh = st.checkbox("Auto-refresh every 5 seconds", value=True)
if auto_refresh:
    time.sleep(5)
    st.rerun()
