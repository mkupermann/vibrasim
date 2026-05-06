"""Results — observations, species, firing events, plasticity per run."""
from __future__ import annotations
import streamlit as st
import pandas as pd

from app.db import (
    list_runs, get_run, get_observations, get_species,
)
from app.report import build_report, render_markdown, render_pdf
from app.viewer import list_snapshots, load_snapshot, build_figure, species_summary
from app.ui import inject_theme, page_header, require_active_session, fmt_dt, fmt_id

from pathlib import Path

st.set_page_config(page_title="Results | vibrasim", layout="wide")
inject_theme()
page_header("Results", "Per-run observations, molecule species, and metrics")

session_id = require_active_session()
if not session_id:
    st.stop()

runs = list_runs(session_id=session_id, limit=200)
if not runs:
    st.info("No runs in this session yet.")
    st.stop()

run_options = {f"{fmt_id(r['id'])} — {r['config_name']} ({r['status']})": str(r["id"]) for r in runs}
sel = st.selectbox("Pick run", list(run_options.keys()))
run_id = run_options[sel]
run = get_run(run_id)

if not run:
    st.warning("Run not found.")
    st.stop()

c = st.columns(4)
c[0].metric("Config", run["config_name"])
c[1].metric("Seed", run["rng_seed"])
c[2].metric("Duration s", run["duration_s"])
c[3].metric("Wall s", round(run["wall_s"], 2) if run.get("wall_s") else "-")

st.markdown("---")

# ----- Observations ----------------------------------------------------------
obs = get_observations(run_id)
tab_report, tab_view3d, tab_obs, tab_species, tab_raw = st.tabs(
    ["Report", "3D View", "Observations", "Species", "Raw"]
)

with tab_report:
    st.markdown("Generate a natural-language summary of this run.")
    cgen, cdownload = st.columns([1, 2])
    if cgen.button("Generate report", type="primary"):
        with st.spinner("Building narrative..."):
            report = build_report(run_id)
            st.session_state[f"report_{run_id}"] = report
    report = st.session_state.get(f"report_{run_id}")
    if report:
        st.markdown(render_markdown(report))
        try:
            pdf_bytes = render_pdf(report)
            cdownload.download_button(
                "Download PDF",
                data=pdf_bytes,
                file_name=f"vibrasim_run_{str(run_id)[:8]}_report.pdf",
                mime="application/pdf",
            )
        except Exception as e:
            st.warning(f"PDF generation failed: {e}")

with tab_view3d:
    st.markdown(
        "Drag to rotate, scroll to zoom, double-click to reset the view. "
        "Click a layer name in the legend to toggle it; double-click to isolate. "
        "Hover over any point for its identifier, frequency and polarity."
    )

    # Determine snapshot directory
    default_dir = run.get("snapshot_dir") or ""
    snap_root = Path(__file__).resolve().parents[2] / "snapshots"
    available_dirs = []
    if snap_root.exists():
        available_dirs = sorted([p.name for p in snap_root.iterdir() if p.is_dir()])

    c1, c2 = st.columns([3, 2])
    with c1:
        if default_dir:
            st.caption(f"Run snapshot dir: `{default_dir}`")
        snap_dir_input = st.text_input(
            "Snapshot directory",
            value=default_dir or (str(snap_root / available_dirs[0]) if available_dirs else ""),
            help="Absolute path or path relative to the repo root",
        )
    with c2:
        if available_dirs:
            picked = st.selectbox(
                "or pick a known directory",
                ["(keep current)"] + available_dirs,
                index=0,
            )
            if picked != "(keep current)":
                snap_dir_input = str(snap_root / picked)
                st.session_state["_snap_dir_override"] = snap_dir_input

    snap_dir_resolved = Path(
        st.session_state.get("_snap_dir_override", snap_dir_input)
    ) if snap_dir_input else None

    if not snap_dir_resolved or not snap_dir_resolved.exists():
        st.info(
            "No snapshot directory available. Set the run's `snapshot_dir` on the "
            "Runs page, or run the simulator with `--snapshot-dir <path> "
            "--snapshot-every 0.5` so this tab can render real positions."
        )
    else:
        snaps = list_snapshots(snap_dir_resolved)
        if not snaps:
            st.warning(f"No `snapshot_t*.npz` files in {snap_dir_resolved}")
        else:
            times = []
            for p in snaps:
                try:
                    times.append(float(p.stem.split("_t")[-1]))
                except Exception:
                    times.append(0.0)
            slot = st.select_slider(
                f"Time (simulated seconds, {len(snaps)} snapshots)",
                options=list(range(len(snaps))),
                value=len(snaps) - 1,
                format_func=lambda i: f"t = {times[i]:.2f}s",
            )
            chosen = snaps[slot]

            show_vibrations = st.checkbox("Show free vibrations", value=True)
            with st.spinner(f"Loading {chosen.name}..."):
                snap = load_snapshot(chosen)

            # Top-line counts
            n_v = len(snap.v_pos)
            n_k = len(snap.k_pos)
            counts_per_level: dict[int, int] = {}
            for lvl in snap.k_level.tolist():
                counts_per_level[lvl] = counts_per_level.get(lvl, 0) + 1
            mc = st.columns(6)
            mc[0].metric("t", f"{snap.t:.2f}s")
            mc[1].metric("Vibrations alive", n_v)
            mc[2].metric("Atoms", counts_per_level.get(4, 0))
            mc[3].metric("Mol L5", counts_per_level.get(5, 0))
            mc[4].metric("Mol L6+", sum(c for l, c in counts_per_level.items() if l >= 6))
            mc[5].metric("Total nodes", n_k)

            fig = build_figure(snap, show_vibrations=show_vibrations)
            st.plotly_chart(fig, use_container_width=True, theme=None)

            # Species table
            sp = species_summary(snap)
            if sp:
                st.markdown("**Species in this snapshot**")
                import pandas as _pd
                sp_df = _pd.DataFrame(
                    [{"Species": k, "Count": v} for k, v in sorted(sp.items(), key=lambda x: -x[1])]
                )
                st.dataframe(sp_df, use_container_width=True, hide_index=True)

with tab_obs:
    if not obs:
        st.info("No observations recorded for this run.")
    else:
        df = pd.DataFrame(obs)
        cols_to_plot = [c for c in [
            "n_vibrations_alive", "n_atoms", "n_molecule_l5", "n_molecule_l6",
            "n_molecule_l7", "n_molecule_l8", "n_molecule_higher",
        ] if c in df.columns and df[c].notna().any()]
        if cols_to_plot:
            chart_df = df.set_index("simulated_t")[cols_to_plot]
            st.line_chart(chart_df, height=380)
        st.dataframe(df.drop(columns=["id", "run_id"], errors="ignore"),
                     use_container_width=True, hide_index=True)

with tab_species:
    species = get_species(run_id)
    if not species:
        st.info("No species observations.")
    else:
        df = pd.DataFrame(species)
        df = df.rename(columns={
            "species_fingerprint": "Species",
            "max_count": "Max count",
            "first_seen_t": "First seen (s)",
        })
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.bar_chart(df.set_index("Species")["Max count"], height=320)

with tab_raw:
    import json as _json
    params = run.get("config_params")
    if isinstance(params, str):
        params = _json.loads(params)
    st.markdown("**Run record**")
    st.json({k: str(v) if "_at" in k else v for k, v in run.items() if k != "config_params"})
    st.markdown("**Config params**")
    st.json(params or {})
