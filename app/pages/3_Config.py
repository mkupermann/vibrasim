"""Config — edit / save / load WorldConfig snapshots."""
from __future__ import annotations
import json
from pathlib import Path

import streamlit as st

from app.db import list_configs, save_config, get_config
from app.ui import inject_theme, page_header, require_active_session, fmt_dt

# Map of editable fields with their default + grouping.
FIELD_GROUPS = {
    "Box & integration": [
        ("box_size_x", "Box X", 1000.0, "float"),
        ("box_size_y", "Box Y", 1000.0, "float"),
        ("box_size_z", "Box Z", 1000.0, "float"),
        ("dt", "dt (s)", 1.0 / 60.0, "float"),
        ("rng_seed", "RNG seed", 42, "int"),
    ],
    "Vibrations": [
        ("n_initial_vibrations", "Initial count", 1000, "int"),
        ("freq_min", "Freq min (Hz)", 100.0, "float"),
        ("freq_max", "Freq max (Hz)", 10000.0, "float"),
        ("freq_distribution", "Freq distribution", "log", "str"),
        ("speed_min", "Speed min", 10.0, "float"),
        ("speed_max", "Speed max", 50.0, "float"),
        ("polarity_split", "Polarity split", 0.5, "float"),
        ("n_vibrations_max", "n_vibrations_max", 4096, "int"),
    ],
    "Binding & decay": [
        ("freq_ratio", "Freq ratio", 0.08, "float"),
        ("freq_tolerance", "Freq tolerance", 0.005, "float"),
        ("pair_decay_time", "Pair decay (s)", 5.0, "float"),
        ("triad_decay_time", "Triad decay (s)", 30.0, "float"),
    ],
    "Repulsion (§4.6)": [
        ("repulsion_k", "k", 100.0, "float"),
        ("repulsion_cell_size", "Cell size", 100.0, "float"),
        ("repulsion_threshold_ratio", "Threshold ratio", 1000.0, "float"),
    ],
    "Ambient regeneration (§4.7)": [
        ("lambda_gen", "lambda_gen", 0.0001, "float"),
        ("lambda_dec", "lambda_dec", 0.001, "float"),
    ],
    "Caps": [
        ("n_nodes_max", "n_nodes_max", 1024, "int"),
    ],
}


def coerce(val, kind):
    if kind == "int":
        return int(val)
    if kind == "float":
        return float(val)
    return str(val)


st.set_page_config(page_title="Config | vibrasim", layout="wide")
inject_theme()
page_header("Configuration", "Edit, save, and load WorldConfig snapshots")

session_id = require_active_session()
if not session_id:
    st.stop()

# ----- Load existing or start fresh -----------------------------------------
configs = list_configs()
existing_options = ["[fresh defaults]"] + [
    f"{c['name']} — {fmt_dt(c['created_at'])}" for c in configs
]
existing_ids = [None] + [str(c["id"]) for c in configs]

c1, c2 = st.columns([3, 1])
sel = c1.selectbox("Start from", existing_options, index=0)
load = c2.button("Load")

if load and sel != "[fresh defaults]":
    cfg = get_config(existing_ids[existing_options.index(sel)])
    if cfg:
        params = cfg["params"]
        if isinstance(params, str):
            params = json.loads(params)
        st.session_state["config_buffer"] = params
        st.success(f"Loaded {cfg['name']}.")

if "config_buffer" not in st.session_state:
    st.session_state["config_buffer"] = {}

buffer = st.session_state["config_buffer"]

# ----- Editor ----------------------------------------------------------------
st.markdown("### Parameters")
with st.form("edit_config"):
    new_values = {}
    for group_name, fields in FIELD_GROUPS.items():
        st.markdown(f"#### {group_name}")
        cols = st.columns(2)
        for i, (key, label, default, kind) in enumerate(fields):
            current = buffer.get(key, default)
            with cols[i % 2]:
                if kind == "int":
                    new_values[key] = st.number_input(label, value=int(current), step=1, format="%d", key=f"f_{key}")
                elif kind == "float":
                    new_values[key] = st.number_input(
                        label, value=float(current), format="%g", key=f"f_{key}",
                    )
                else:
                    new_values[key] = st.text_input(label, value=str(current), key=f"f_{key}")

    st.markdown("#### Persistence")
    name = st.text_input("Name", value="config_v1", help="Human label for this snapshot")
    notes = st.text_area("Notes", height=80)
    toml_path = st.text_input(
        "TOML path (optional)",
        placeholder="e.g. configs/calibration_session5.toml",
    )

    save = st.form_submit_button("Save snapshot")
    if save:
        # build params dict
        params = {k: coerce(v, k_kind) for (k, _, _, k_kind), v in zip(
            [(k, l, d, kk) for fields in FIELD_GROUPS.values() for k, l, d, kk in fields],
            new_values.values(),
        )}
        # repack box_size tuple if needed (consumer-side normalisation)
        if "box_size_x" in params:
            params["box_size"] = [params.pop("box_size_x"), params.pop("box_size_y"), params.pop("box_size_z")]
        cfg_id = save_config(session_id, name, params, toml_path or None, notes or None)
        st.session_state["config_buffer"] = params
        st.success(f"Saved snapshot. Use it on the Runs page.")

# ----- TOML preview ---------------------------------------------------------
st.markdown("---")
st.markdown("### Preview")
st.json({k: new_values[k] for k in sorted(new_values)})
