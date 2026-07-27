"""Live 3D visualisation for BET / belief-path experiments.

Ontology:
  FREE VIBRATIONS = continuous **frequency-layered field** (hidden dimensions)
  BOUND MATTER    = spheres (electrons / atoms / molecules)

Rendering strategy (anti-flicker):
  - Create field layer meshes **once**
  - Each frame only **update point coordinates / scalars** (no remove+re-add)
  - Bound-matter glyphs rebuilt only when counts change

Keyboard: space pause · s step · r camera · q quit
"""
from __future__ import annotations

import time
from typing import Callable, List, Optional, Tuple

import numpy as np

from world.physics import tick
from world.gpu_viz import (
    apply_plotter_gpu,
    configure_pyvista_gpu,
    field_resolution_for_gpu,
    request_high_performance_gpu,
)

request_high_performance_gpu()

# Bound matter
COLOR_ELECTRON = np.array([1.00, 0.55, 0.00])
COLOR_PAIR = np.array([0.75, 0.80, 0.95])
COLOR_TRIAD = np.array([1.00, 0.88, 0.45])
COLOR_ATOM = np.array([1.00, 1.00, 1.00])
COLOR_MOL = np.array([0.25, 1.00, 0.50])

RADIUS_BY_LEVEL = {1: 1.6, 2: 2.0, 3: 2.4, 4: 3.0}
for _l in range(5, 33):
    RADIUS_BY_LEVEL[_l] = 3.4 + 0.25 * (_l - 5)

COLOR_BY_LEVEL = {
    1: COLOR_ELECTRON,
    2: COLOR_PAIR,
    3: COLOR_TRIAD,
    4: COLOR_ATOM,
}
for _l in range(5, 33):
    t = min(1.0, (_l - 5) / 12.0)
    COLOR_BY_LEVEL[_l] = (1.0 - t) * COLOR_MOL + t * np.array([1.0, 0.25, 0.95])

# Field layers (frequency dimensions) — bright, high opacity so they READ
LAYER_COLORS = [
    (0.25, 0.65, 1.00),   # low  — blue
    (0.10, 1.00, 0.85),   # mid  — cyan
    (0.95, 0.40, 1.00),   # high — magenta
    (1.00, 0.55, 0.15),   # vhi  — orange
]

FIELD_RES_DEFAULT = 40
FIELD_SIGMA = 7.0
FIELD_AMP = 3.5
FIELD_K0 = 0.40
FIELD_OPACITY = 0.72  # visible, not ghostly

LEGEND = (
    "LEGEND\n"
    "  COLOURED SHEETS = free vibration FIELD (4 frequency layers)\n"
    "    undulation    = continuous endless wave\n"
    "  ORANGE spheres  = electrons (bound)\n"
    "  WHITE           = atoms\n"
    "  GREEN/MAGENTA   = molecules\n"
    "KEYS  space pause  s step  r camera  q quit"
)


def _level_counts(world) -> str:
    n_v = int(world.s_alive.sum())
    parts = [f"field-src {n_v}"]
    for L, name in ((1, "e-"), (2, "pair"), (3, "triad"), (4, "atom")):
        n = int(((world.k_level[: world.k_count] == L) & world.k_alive[: world.k_count]).sum())
        parts.append(f"{name} {n}")
    n_mol = int(((world.k_level[: world.k_count] >= 5) & world.k_alive[: world.k_count]).sum())
    parts.append(f"mol {n_mol}")
    return " | ".join(parts)


def _band_index(freq: float, n_bands: int) -> int:
    logf = np.log10(max(freq, 10.0))
    u = float(np.clip((logf - 2.0) / 3.0, 0.0, 0.999))
    return int(u * n_bands)


def compute_layer_heights(
    world,
    *,
    n_bands: int,
    res: int,
    xs: np.ndarray,
    ys: np.ndarray,
    z_bases: np.ndarray,
) -> Tuple[List[np.ndarray], List[int]]:
    """Return list of Z arrays (res x res) per band, and source counts per band."""
    bx, by, bz = map(float, world.config.box_size)
    XX, YY = np.meshgrid(xs, ys, indexing="xy")
    heights: List[np.ndarray] = []
    counts: List[int] = []

    mask = np.asarray(world.s_alive, dtype=bool)
    if not mask.any():
        for b in range(n_bands):
            heights.append(np.full((res, res), z_bases[b], dtype=np.float64))
            counts.append(0)
        return heights, counts

    pos = np.ascontiguousarray(world.s_pos[mask], dtype=np.float64)
    freq = np.ascontiguousarray(world.s_freq[mask], dtype=np.float64)
    pol = np.asarray(world.s_pol[mask], dtype=bool)
    vel = np.ascontiguousarray(world.s_vel[mask], dtype=np.float64)
    t = float(world.t)
    bands = np.array([_band_index(float(f), n_bands) for f in freq], dtype=np.int32)
    sigma2 = FIELD_SIGMA * FIELD_SIGMA

    for b in range(n_bands):
        sel = bands == b
        counts.append(int(np.sum(sel)))
        if not np.any(sel):
            # gentle idle ripple so empty layers still “exist”
            idle = 0.25 * np.sin(0.15 * XX + 0.8 * t) * np.cos(0.12 * YY - 0.5 * t)
            heights.append(z_bases[b] + idle)
            continue

        p = pos[sel]
        f = freq[sel]
        po = pol[sel]
        v = vel[sel]
        field = np.zeros((res, res), dtype=np.float64)

        # Cap contributors for speed (GPU still draws full mesh)
        n_use = min(p.shape[0], 80)
        step = max(1, p.shape[0] // n_use)
        for i in range(0, p.shape[0], step):
            px, py = float(p[i, 0]), float(p[i, 1])
            dx = XX - px
            dy = YY - py
            dx -= bx * np.round(dx / bx)
            dy -= by * np.round(dy / by)
            r2 = dx * dx + dy * dy
            amp = np.exp(-0.5 * r2 / sigma2)
            sp = float(np.linalg.norm(v[i]))
            kmag = FIELD_K0 * (1.0 + 0.45 * np.log10(max(float(f[i]), 10.0)))
            if sp > 1e-6:
                kx = kmag * (v[i, 0] / sp)
                ky = kmag * (v[i, 1] / sp)
            else:
                kx, ky = kmag, 0.25 * kmag
            omega = 0.02 * float(f[i])
            sign = 1.0 if po[i] else -1.0
            field += amp * np.sin(sign * (kx * dx + ky * dy + omega * t))

        peak = float(np.max(np.abs(field))) + 1e-9
        field = (field / peak) * FIELD_AMP
        heights.append(z_bases[b] + field)

    return heights, counts


class BetLiveView:
    def __init__(self, title: str = "EQMOD BET live"):
        self.title = title
        self._pl = None
        self._closed = False
        self.playing = True
        self._step_once = False
        self._user_quit = False
        self._frame = 0
        # Stable field state (anti-flicker)
        self._n_bands = 4
        self._res = FIELD_RES_DEFAULT
        self._xs = None
        self._ys = None
        self._XX = None
        self._YY = None
        self._z_bases = None
        self._layer_grids = []      # pyvista StructuredGrid
        self._layer_actors = []
        self._field_ready = False
        self._node_actor = None
        self._last_node_count = -1
        self._hud_actor = None
        self._legend_actor = None

    def open(self, world) -> bool:
        try:
            import pyvista as pv
        except ImportError:
            print("[bet_live] pyvista not installed")
            return False
        try:
            configure_pyvista_gpu(8, True)
            self._res = field_resolution_for_gpu()
            # Cap for interactive FPS (still dense enough to see waves)
            self._res = int(min(max(self._res, 36), 56))

            bx, by, bz = map(float, world.config.box_size)
            pl = pv.Plotter(title=self.title, window_size=(1600, 1000))
            pl.set_background((0.04, 0.05, 0.08))
            box = pv.Box(bounds=(0, bx, 0, by, 0, bz))
            pl.add_mesh(
                box, style="wireframe", color=(0.55, 0.58, 0.70),
                line_width=2, name="box",
            )
            # No lightkit / fancy lighting — AMD driver shader crashes
            pl.add_key_event("space", self._toggle_play)
            pl.add_key_event("s", self._request_step)
            pl.add_key_event("q", self._request_quit)
            pl.add_key_event("r", lambda: self._reset_camera(world))

            # Build stable field meshes ONCE
            self._xs = np.linspace(0.0, bx, self._res)
            self._ys = np.linspace(0.0, by, self._res)
            self._XX, self._YY = np.meshgrid(self._xs, self._ys, indexing="xy")
            self._z_bases = np.linspace(0.15 * bz, 0.85 * bz, self._n_bands)

            heights, counts = compute_layer_heights(
                world,
                n_bands=self._n_bands,
                res=self._res,
                xs=self._xs,
                ys=self._ys,
                z_bases=self._z_bases,
            )
            self._layer_grids = []
            self._layer_actors = []
            for b in range(self._n_bands):
                grid = pv.StructuredGrid(self._XX, self._YY, heights[b])
                col = LAYER_COLORS[b]
                # Flat shading, no specular — avoids "Could not set shader program" on AMD
                actor = pl.add_mesh(
                    grid,
                    color=col,
                    opacity=FIELD_OPACITY,
                    smooth_shading=False,
                    name=f"field_layer_{b}",
                    show_edges=False,
                    lighting=False,
                )
                self._layer_grids.append(grid)
                self._layer_actors.append(actor)

            self._legend_actor = pl.add_text(
                LEGEND, position="lower_left", font_size=9,
                color=(0.80, 0.90, 0.95), name="legend",
            )
            self._hud_actor = pl.add_text(
                "", position="upper_left", font_size=11, color="white", name="hud",
            )

            pl.show(interactive_update=True, auto_close=False)
            gpu_info = apply_plotter_gpu(pl)
            self._pl = pl
            self._field_ready = True
            self._update_hud(world, f"GPU layers ready res={self._res} | {gpu_info[:70]}")
            self._update_nodes(world, force=True)
            self._reset_camera(world)
            pl.update()
            print(f"[bet_live] field layers ON res={self._res} counts={counts}")
            return True
        except Exception as exc:
            print(f"[bet_live] open failed: {exc}")
            import traceback
            traceback.print_exc()
            self._pl = None
            return False

    def _toggle_play(self):
        self.playing = not self.playing

    def _request_step(self):
        self._step_once = True

    def _request_quit(self):
        self._user_quit = True

    def _reset_camera(self, world=None):
        pl = self._pl
        if pl is None:
            return
        try:
            bx, by, bz = world.config.box_size if world is not None else (60, 60, 60)
            pl.reset_camera(bounds=(0, bx, 0, by, 0, bz))
            pl.camera.zoom(1.1)
            pl.camera_position = "iso"
            pl.reset_camera(bounds=(0, bx, 0, by, 0, bz))
        except Exception:
            try:
                pl.camera_position = "iso"
                pl.reset_camera()
            except Exception:
                pass

    def _window_alive(self) -> bool:
        pl = self._pl
        if pl is None or self._closed:
            return False
        try:
            if not getattr(pl, "iren", None) or not pl.render_window:
                return False
        except Exception:
            return False
        return True

    def _update_field(self, world) -> List[int]:
        """In-place Z update — no actor remove (stops flicker)."""
        if not self._field_ready or self._pl is None:
            return [0] * self._n_bands
        heights, counts = compute_layer_heights(
            world,
            n_bands=self._n_bands,
            res=self._res,
            xs=self._xs,
            ys=self._ys,
            z_bases=self._z_bases,
        )
        for b in range(self._n_bands):
            grid = self._layer_grids[b]
            # StructuredGrid points: VTK order (i,j,k) — for 2D surface k=1
            # pyvista StructuredGrid(XX,YY,ZZ) stores points in Fortran-ish order
            # Easiest robust update: replace points from new StructuredGrid
            import pyvista as pv
            new_g = pv.StructuredGrid(self._XX, self._YY, heights[b])
            grid.points = new_g.points.copy()
            try:
                grid.GetPointData().Modified()
                grid.Modified()
            except Exception:
                pass
            try:
                # Tell the mapper the geometry changed (critical for live updates)
                if b < len(self._layer_actors) and self._layer_actors[b] is not None:
                    m = self._layer_actors[b].GetMapper()
                    if m is not None:
                        m.Update()
            except Exception:
                pass
        return counts

    def _update_nodes(self, world, force: bool = False) -> None:
        import pyvista as pv

        pl = self._pl
        if pl is None:
            return
        n_alive = int(world.k_alive[: world.k_count].sum()) if world.k_count else 0
        if not force and n_alive == self._last_node_count and self._frame % 3 != 0:
            # still refresh positions occasionally
            if self._node_actor is None:
                return
        self._last_node_count = n_alive

        if self._node_actor is not None:
            try:
                pl.remove_actor(self._node_actor, render=False)
            except Exception:
                pass
            self._node_actor = None

        if n_alive == 0:
            return
        idx = np.where(world.k_alive[: world.k_count])[0]
        positions = np.ascontiguousarray(world.k_pos[idx], dtype=np.float64)
        levels = world.k_level[idx].astype(np.int32)
        radii = np.array([RADIUS_BY_LEVEL.get(int(L), 2.0) for L in levels], dtype=np.float64)
        colors = np.array(
            [COLOR_BY_LEVEL.get(int(L), COLOR_ATOM) for L in levels],
            dtype=np.float64,
        )
        pc = pv.PolyData(positions)
        pc["rgb"] = (np.clip(colors, 0, 1) * 255).astype(np.uint8)
        pc["r"] = radii
        sphere = pv.Sphere(radius=1.0, theta_resolution=14, phi_resolution=14)
        glyphs = pc.glyph(geom=sphere, scale="r", orient=False, factor=1.0)
        self._node_actor = pl.add_mesh(
            glyphs, scalars="rgb", rgb=True, smooth_shading=False,
            lighting=False, name="nodes", opacity=1.0,
        )

    def _update_hud(self, world, extra: str = "") -> None:
        pl = self._pl
        if pl is None:
            return
        # remove+readd text is ok occasionally; do every frame via remove
        try:
            pl.remove_actor("hud", render=False)
        except Exception:
            pass
        text = (
            f"{self.title}\n"
            f"t={world.t:7.2f}s\n"
            f"{_level_counts(world)}\n"
            f"{'[PAUSED]' if not self.playing else '[PLAYING]'}  space/s/r/q\n"
            f"{extra}"
        )
        pl.add_text(text, position="upper_left", font_size=11, color="white", name="hud")

    def _frame_update(self, world, extra: str = "") -> None:
        self._frame += 1
        counts = self._update_field(world)
        self._update_nodes(world, force=(self._frame % 5 == 0))
        self._update_hud(
            world,
            extra + f" | layers src {counts}",
        )
        if self._pl is not None:
            self._pl.render()  # full render, not only update

    def run_ticks(
        self,
        world,
        n_ticks: int,
        dt: float,
        *,
        ticks_per_frame: int = 3,
        hud_fn: Optional[Callable] = None,
    ) -> int:
        if self._pl is None:
            for _ in range(n_ticks):
                tick(world, dt)
                world.t += dt
            return n_ticks

        done = 0
        tpf = max(1, int(ticks_per_frame))
        try:
            while done < n_ticks:
                if self._user_quit or not self._window_alive():
                    break
                if self.playing or self._step_once:
                    n = 1 if self._step_once else min(tpf, n_ticks - done)
                    for _ in range(n):
                        tick(world, dt)
                        world.t += dt
                        done += 1
                    self._step_once = False
                extra = hud_fn(world, done, n_ticks) if hud_fn else f"tick {done}/{n_ticks}"
                self._frame_update(world, extra)
                if not self.playing:
                    time.sleep(0.04)
                else:
                    time.sleep(0.016)  # ~60 fps cap, reduces flicker thrash
        except KeyboardInterrupt:
            self._user_quit = True

        while done < n_ticks:
            tick(world, dt)
            world.t += dt
            done += 1

        if self._window_alive() and not self._user_quit:
            try:
                self._frame_update(world, f"DONE {done}/{n_ticks}")
                time.sleep(1.5)
            except Exception:
                pass
        return done

    def close(self) -> None:
        if self._pl is not None and not self._closed:
            try:
                self._pl.close()
            except Exception:
                pass
            self._closed = True
            self._pl = None
            self._field_ready = False


def run_ticks_live(
    world,
    n_ticks: int,
    dt: float,
    *,
    live: bool = False,
    title: str = "EQMOD BET live",
    ticks_per_frame: int = 3,
    hud_fn: Optional[Callable] = None,
) -> None:
    if not live or n_ticks <= 0:
        for _ in range(n_ticks):
            tick(world, dt)
            world.t += dt
        return

    view = BetLiveView(title=title)
    if not view.open(world):
        for _ in range(n_ticks):
            tick(world, dt)
            world.t += dt
        return
    try:
        view.run_ticks(world, n_ticks, dt, ticks_per_frame=ticks_per_frame, hud_fn=hud_fn)
    finally:
        view.close()


# Compat for interactive.py
def build_vibration_field_layers(world, n_bands: int = 4, res: int = 40):
    """Return list of (grid, color, opacity) for one-shot builds."""
    import pyvista as pv

    bx, by, bz = map(float, world.config.box_size)
    xs = np.linspace(0.0, bx, res)
    ys = np.linspace(0.0, by, res)
    z_bases = np.linspace(0.15 * bz, 0.85 * bz, n_bands)
    heights, _ = compute_layer_heights(
        world, n_bands=n_bands, res=res, xs=xs, ys=ys, z_bases=z_bases,
    )
    XX, YY = np.meshgrid(xs, ys, indexing="xy")
    out = []
    for b in range(n_bands):
        grid = pv.StructuredGrid(XX, YY, heights[b])
        out.append((grid, np.array(LAYER_COLORS[b]), FIELD_OPACITY))
    return out


def build_vibration_waves(world):
    layers = build_vibration_field_layers(world)
    if not layers:
        return None, None
    import pyvista as pv
    mb = pv.MultiBlock()
    for grid, col, _ in layers:
        mb.append(grid)
    return mb, None
