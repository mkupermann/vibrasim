"""3D snapshot viewer — turn a `.npz` snapshot into an interactive Plotly figure.

Built around two ideas:
1.  Each entity type is its own Plotly trace, so the legend doubles as a
    layer toggle. Click a trace name to hide that layer; double-click to
    isolate it.
2.  Every point's hover tooltip carries enough metadata to identify it —
    index, level, frequency, polarity, composition size — so 'zoom in on
    every electron, atom, molecule' is just rotate + mousewheel + hover.
"""
from __future__ import annotations
import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import plotly.graph_objects as go


LEVEL_NAMES = {
    1: "electron",
    2: "pair",
    3: "triad",
    4: "atom",
    5: "molecule (level 5)",
    6: "molecule (level 6)",
    7: "molecule (level 7)",
    8: "molecule (level 8)",
}

# Palette aligned with the dashboard (blue / grey / accent variants).
LEVEL_COLORS = {
    1: "#9ca3af",   # electron — muted grey
    2: "#60a5fa",   # pair — light blue
    3: "#2563eb",   # triad — primary blue
    4: "#1e40af",   # atom — deep blue
    5: "#15803d",   # level-5 molecule — green
    6: "#16a34a",   # level-6 molecule
    7: "#84cc16",   # level-7 molecule
    8: "#ca8a04",   # level-8 molecule
}
HIGHER_COLOR = "#dc2626"           # level 9+
VIBRATION_COLOR = "#cbd5e1"        # very pale grey for free vibrations


@dataclass
class SnapshotData:
    t: float
    box_size: tuple[float, float, float]
    # Vibrations (free-flying)
    v_pos: np.ndarray           # (Nv, 3)
    v_freq: np.ndarray          # (Nv,)
    v_pol: np.ndarray           # (Nv,) bool
    # Nodes (electrons → molecules)
    k_pos: np.ndarray           # (Nk, 3)
    k_level: np.ndarray         # (Nk,) uint
    k_freq: np.ndarray          # (Nk,)
    k_pol: np.ndarray           # (Nk,) bool
    k_comp_size: np.ndarray     # (Nk,) — number of constituents
    species_fp: list[str]       # (Nk,) human fingerprint per node ('' for level<4)


def list_snapshots(snapshot_dir: str | Path) -> list[Path]:
    """Return sorted paths to every snapshot npz in the directory."""
    p = Path(snapshot_dir)
    if not p.exists() or not p.is_dir():
        return []
    return sorted(p.glob("snapshot_t*.npz"))


def _species_fingerprint(level: int, comp_levels: Iterable[int]) -> str:
    """Build a string like 'A33' or 'A3344' from constituent level list."""
    if level < 4:
        return ""
    if level == 4:
        return "A"  # atom
    # Molecule: prefix 'A' then levels of constituents (sorted)
    parts = sorted(int(x) for x in comp_levels)
    return "A" + "".join(str(p) for p in parts)


def load_snapshot(path: str | Path) -> SnapshotData:
    """Read a snapshot npz and return the slimmed-down view used by the viewer."""
    data = np.load(path, allow_pickle=True)
    t = float(data["t"][0])

    cfg_raw = str(data["config_json"][0])
    box = (1000.0, 1000.0, 1000.0)
    try:
        # save_snapshot stores config as a Python repr (single quotes, True/False/None,
        # tuples in parentheses) — ast.literal_eval handles all of that natively,
        # whereas json.loads cannot.
        cfg = ast.literal_eval(cfg_raw)
        b = cfg.get("box_size") or cfg.get("box_size_x")
        if isinstance(b, (list, tuple)):
            box = tuple(float(x) for x in b)
    except Exception:
        pass

    s_alive = data["s_alive"].astype(bool)
    v_pos = data["s_pos"][s_alive]
    v_freq = data["s_freq"][s_alive]
    v_pol = data["s_pol"][s_alive]

    k_alive = data["k_alive"].astype(bool)
    k_pos = data["k_pos"][k_alive]
    k_level = data["k_level"][k_alive].astype(int)
    k_freq = data["k_freq"][k_alive]
    k_pol = data["k_pol"][k_alive]

    # Composition size per node — count of indices in its component span.
    k_comp_offset = data["k_comp_offset"]
    k_comp_used = int(data["k_comp_used"][0])
    alive_idx = np.where(k_alive)[0]
    comp_sizes = np.zeros(len(alive_idx), dtype=int)
    species = []
    k_comp_indices = data["k_comp_indices"]
    for j, kid in enumerate(alive_idx):
        start = int(k_comp_offset[kid])
        # Find span: next offset that's >= start, defaulting to k_comp_used.
        next_offsets = [int(o) for o in k_comp_offset if int(o) > start and int(o) <= k_comp_used]
        end = min(next_offsets) if next_offsets else k_comp_used
        size = max(end - start, 0)
        comp_sizes[j] = size
        if k_level[j] < 4:
            species.append("")
            continue
        # Recursively unwrap to get base levels
        base_levels: list[int] = []
        try:
            comp_ids = k_comp_indices[start:end]
            for cid in comp_ids:
                cid = int(cid)
                if cid < 0 or cid >= len(data["k_level"]):
                    continue
                base_levels.append(int(data["k_level"][cid]))
        except Exception:
            pass
        species.append(_species_fingerprint(int(k_level[j]), base_levels))

    return SnapshotData(
        t=t, box_size=box,
        v_pos=v_pos, v_freq=v_freq, v_pol=v_pol,
        k_pos=k_pos, k_level=k_level, k_freq=k_freq, k_pol=k_pol,
        k_comp_size=comp_sizes, species_fp=species,
    )


def build_figure(snap: SnapshotData, *, show_vibrations: bool = True,
                 max_vibrations: int = 4000) -> go.Figure:
    """Build a Plotly Scatter3d figure with one trace per entity type."""
    fig = go.Figure()

    # Vibrations — pale dots, grouped into one trace, downsampled if huge.
    if show_vibrations and len(snap.v_pos):
        n = len(snap.v_pos)
        if n > max_vibrations:
            idx = np.random.default_rng(42).choice(n, size=max_vibrations, replace=False)
            vp = snap.v_pos[idx]; vf = snap.v_freq[idx]; vpol = snap.v_pol[idx]
            note = f" (sampled {max_vibrations}/{n})"
        else:
            vp, vf, vpol = snap.v_pos, snap.v_freq, snap.v_pol
            note = ""
        hover = [
            f"vibration<br>freq: {f:.1f} Hz<br>polarity: {'+' if p else '−'}"
            for f, p in zip(vf, vpol)
        ]
        fig.add_trace(go.Scatter3d(
            x=vp[:, 0], y=vp[:, 1], z=vp[:, 2],
            mode="markers",
            name=f"vibrations ({n})" + note,
            marker=dict(size=1.6, color=VIBRATION_COLOR, opacity=0.55),
            hovertext=hover, hoverinfo="text",
        ))

    # Nodes — one trace per level (1=electron … 8=molecule, plus higher).
    if len(snap.k_pos):
        levels_present = sorted(set(snap.k_level.tolist()))
        for lvl in levels_present:
            mask = snap.k_level == lvl
            kp = snap.k_pos[mask]
            kf = snap.k_freq[mask]
            kpol = snap.k_pol[mask]
            ksize = snap.k_comp_size[mask]
            kspc = [snap.species_fp[i] for i in np.where(mask)[0]]
            n = int(mask.sum())
            label = LEVEL_NAMES.get(lvl, f"level {lvl}")
            color = LEVEL_COLORS.get(lvl, HIGHER_COLOR)
            # Marker size grows with level so atoms/molecules are visually larger.
            marker_size = {1: 3, 2: 4, 3: 5, 4: 7}.get(lvl, 8 + min(lvl - 5, 3))
            hover = [
                (f"{label}<br>"
                 f"freq: {f:.1f} Hz<br>"
                 f"polarity: {'+' if p else '−'}<br>"
                 f"constituents: {s}"
                 + (f"<br>species: {fp}" if fp else ""))
                for f, p, s, fp in zip(kf, kpol, ksize, kspc)
            ]
            fig.add_trace(go.Scatter3d(
                x=kp[:, 0], y=kp[:, 1], z=kp[:, 2],
                mode="markers",
                name=f"{label} ({n})",
                marker=dict(size=marker_size, color=color, opacity=0.95,
                            line=dict(color="white", width=0.5)),
                hovertext=hover, hoverinfo="text",
            ))

    # Layout — auto-fit axis range to the data extent (with 5% padding on each
    # side). Falls back to box_size only if there's no data. This keeps the
    # view usable even when the snapshot's config_json says a 1000³ box but
    # the simulation actually used 60³ (or vice versa).
    pts = []
    if len(snap.k_pos):
        pts.append(snap.k_pos)
    if show_vibrations and len(snap.v_pos):
        pts.append(snap.v_pos)
    if pts:
        all_pts = np.vstack(pts)
        mn = all_pts.min(axis=0)
        mx = all_pts.max(axis=0)
        # Force a cube so the aspect is preserved; pad by 5%.
        spans = mx - mn
        side = max(spans.max(), 1.0)
        side *= 1.10
        center = (mn + mx) / 2.0
        ranges = [
            [center[0] - side / 2, center[0] + side / 2],
            [center[1] - side / 2, center[1] + side / 2],
            [center[2] - side / 2, center[2] + side / 2],
        ]
    else:
        bx, by, bz = snap.box_size
        ranges = [[0, bx], [0, by], [0, bz]]

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=ranges[0], title="x", backgroundcolor="#ffffff",
                       gridcolor="#e5e7eb", showbackground=True),
            yaxis=dict(range=ranges[1], title="y", backgroundcolor="#ffffff",
                       gridcolor="#e5e7eb", showbackground=True),
            zaxis=dict(range=ranges[2], title="z", backgroundcolor="#ffffff",
                       gridcolor="#e5e7eb", showbackground=True),
            aspectmode="cube",
            camera=dict(eye=dict(x=1.6, y=1.6, z=1.0)),
        ),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#1f2937"),
        legend=dict(
            x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.85)",
            bordercolor="#e5e7eb", borderwidth=1,
        ),
        margin=dict(l=0, r=0, t=10, b=0),
        height=720,
    )
    return fig


def species_summary(snap: SnapshotData) -> dict[str, int]:
    """Return a count per species fingerprint for the snapshot."""
    counts: dict[str, int] = {}
    for fp in snap.species_fp:
        if not fp:
            continue
        counts[fp] = counts.get(fp, 0) + 1
    return counts
