"""Runs — launch a simulation run and track its status."""
from __future__ import annotations
import json
import streamlit as st
import pandas as pd

from app.db import (
    list_configs, list_runs, get_run, create_run, update_run_status,
)
from app.report import build_report, render_markdown, render_pdf
from app.snapshot_import import import_run_from_snapshots
from app.ui import inject_theme, page_header, require_active_session, badge, fmt_dt, fmt_id

st.set_page_config(page_title="Runs | vibrasim", layout="wide")
inject_theme()
page_header("Runs", "Launch a simulation run from a saved config and track results")

session_id = require_active_session()
if not session_id:
    st.stop()

# ----- Launch a new run ------------------------------------------------------
configs = list_configs()
if not configs:
    st.info("No configs saved yet. Save one on the Config page first.")
else:
    with st.expander("Launch a new run", expanded=True):
        with st.form("new_run"):
            cfg_options = {f"{c['name']} ({fmt_dt(c['created_at'])})": str(c["id"]) for c in configs}
            cfg_label = st.selectbox("Config", list(cfg_options.keys()))
            c1, c2, c3 = st.columns(3)
            rng_seed = c1.number_input("RNG seed", value=42, step=1)
            duration_s = c2.number_input("Duration (s)", value=30.0, format="%g")
            snap_every = c3.number_input("Snapshot every (s)", value=0.5, format="%g")
            snap_dir = st.text_input(
                "Snapshot directory (optional)",
                placeholder="e.g. snapshots/session5_run1",
            )
            notes = st.text_area("Run notes", height=70)
            submitted = st.form_submit_button("Register run")
            if submitted:
                run_id = create_run(
                    session_id=session_id,
                    config_id=cfg_options[cfg_label],
                    rng_seed=int(rng_seed),
                    duration_s=float(duration_s),
                    snapshot_every=float(snap_every) if snap_every > 0 else None,
                    snapshot_dir=snap_dir or None,
                )
                if notes:
                    update_run_status(run_id, "pending", notes=notes)
                st.success(f"Registered run {fmt_id(run_id)}.")
                snap_path = snap_dir or f"snapshots/run_{str(run_id)[:8]}"
                st.markdown(
                    "**Workflow:**\n\n"
                    "1. Execute the simulator and write snapshots to disk:\n\n"
                    f"```bash\n"
                    f"uv run python -m world run \\\n"
                    f"    --duration {duration_s} \\\n"
                    f"    --seed {rng_seed} \\\n"
                    f"    --snapshot-every {snap_every} \\\n"
                    f"    --snapshot-dir {snap_path}\n"
                    f"```\n\n"
                    "2. Set this run's status to **completed** below, "
                    "with the snapshot directory pointed at the same path.\n\n"
                    "3. Click **Import observations from snapshots** "
                    "to populate the database from the `.npz` files."
                )

st.markdown("---")

# ----- Existing runs ---------------------------------------------------------
all_runs = list_runs(session_id=session_id, limit=200)
st.markdown("### Runs in this session")
if not all_runs:
    st.info("No runs registered for this session.")
    st.stop()

df = pd.DataFrame([
    {
        "id": fmt_id(r["id"]),
        "Config": r["config_name"],
        "Seed": r["rng_seed"],
        "Duration s": r["duration_s"],
        "Status": r["status"],
        "Started": fmt_dt(r["started_at"]),
        "Wall s": r["wall_s"],
    }
    for r in all_runs
])
st.dataframe(df, use_container_width=True, hide_index=True)

# ----- Update a run's status -------------------------------------------------
st.markdown("### Update run status")
run_options = {f"{fmt_id(r['id'])} — {r['config_name']} ({r['status']})": str(r["id"]) for r in all_runs}
sel = st.selectbox("Pick run", list(run_options.keys()))
run_id = run_options[sel]
run = get_run(run_id)

if run:
    c1, c2, c3 = st.columns(3)
    new_status = c1.selectbox(
        "New status",
        ["pending", "running", "completed", "failed", "cancelled"],
        index=["pending", "running", "completed", "failed", "cancelled"].index(run["status"]),
    )
    wall_s = c2.number_input("Wall time (s)", value=float(run.get("wall_s") or 0.0), format="%g")
    mark_ended = c3.checkbox("Set ended_at to now", value=(new_status in ("completed", "failed", "cancelled")))
    extra_notes = st.text_area("Append notes", height=60)
    if st.button("Apply"):
        update_run_status(
            run_id,
            new_status,
            wall_s=wall_s if wall_s > 0 else None,
            ended_at_now=mark_ended,
            notes=(run.get("notes") or "") + ("\n" + extra_notes if extra_notes else ""),
        )
        st.success("Updated.")
        st.rerun()

    # Show config params
    with st.expander("Config used", expanded=False):
        params = run.get("config_params")
        if isinstance(params, str):
            params = json.loads(params)
        st.json(params or {})

    # ----- Import observations from snapshot directory -------------------
    st.markdown("### Import observations from snapshots")
    st.caption(
        "Walks every `snapshot_t*.npz` in the given directory, derives "
        "per-snapshot counts and species, and writes them to the run's "
        "`observations` and `species_observations` tables. Use this when "
        "the simulator wrote snapshots to disk but did not record observations live."
    )
    from pathlib import Path as _Path
    repo_root = _Path(__file__).resolve().parents[2]
    default_dir = run.get("snapshot_dir") or str(repo_root / "snapshots" / "v2-acceptance")
    imp_dir = st.text_input("Snapshot directory", value=default_dir, key=f"imp_{run_id}")
    cimp1, cimp2 = st.columns([1, 2])
    if cimp1.button("Import"):
        with st.spinner(f"Reading snapshots from {imp_dir}..."):
            try:
                result = import_run_from_snapshots(run_id, imp_dir, replace=True)
                if result.get("error"):
                    st.error(result["error"])
                else:
                    st.success(
                        f"Imported {result['snapshots']} snapshots; "
                        f"{result['species_total']} species "
                        f"({result['species_first_seen']} first-seen events)."
                    )
            except Exception as e:
                st.error(f"Import failed: {e}")

    # ----- Report --------------------------------------------------------
    st.markdown("---")
    st.markdown("### Report")
    st.caption(
        "After a completed run, generate a natural-language summary. The full "
        "version with charts lives on the Results page."
    )
    cgen, cpdf = st.columns([1, 2])
    if cgen.button("Generate report for this run", type="primary"):
        with st.spinner("Building narrative..."):
            report = build_report(run_id)
            st.session_state[f"report_{run_id}"] = report
    report = st.session_state.get(f"report_{run_id}")
    if report:
        st.markdown(render_markdown(report))
        try:
            pdf_bytes = render_pdf(report)
            cpdf.download_button(
                "Download PDF",
                data=pdf_bytes,
                file_name=f"vibrasim_run_{str(run_id)[:8]}_report.pdf",
                mime="application/pdf",
            )
        except Exception as e:
            st.warning(f"PDF generation failed: {e}")
