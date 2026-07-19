"""Live 3D visualisation for BET / belief-path experiments.

Ontology (matches the belief path):

  FREE VIBRATIONS  = a **hidden continuous field**, stacked in **frequency layers**
                     (not discrete particles, not interrupted wave packets).
  BOUND MATTER     = electrons / pairs / triads / atoms / molecules as spheres
                     that *condense out of* the field.

Field rendering:
  - Partition free vibrations into log-frequency **bands** (layers / dimensions).
  - Each band is a translucent **continuous sheet** spanning the box.
  - Sheet height undulates from the summed, endless phase field of all
    contributors in that band (Gaussian kernels in xy, plane-wave phase in time).
  - No finite wavelets that start/stop mid-space.

Keyboard: space pause · s step · r camera · q quit
"""
from __future__ import annotations

import time
from typing import Callable, List, Optional, Sequence, Tuple

import numpy as np

from world.physics import tick

# Bound-matter palette
COLOR_ELECTRON = np.array([1.00, 0.65, 0.05])
COLOR_PAIR = np.array([0.75, 0.80, 0.90])
COLOR_TRIAD = np.array([1.00, 0.90, 0.55])
COLOR_ATOM = np.array([1.00, 1.00, 1.00])
COLOR_MOL_BASE = np.array([0.20, 1.00, 0.45])

RADIUS_BY_LEVEL = {1: 1.4, 2: 1.8, 3: 2.2, 4: 2.8}
for _l in range(5, 33):
    RADIUS_BY_LEVEL[_l] = 3.2 + 0.25 * (_l - 5)

COLOR_BY_LEVEL = {
    1: COLOR_ELECTRON,
    2: COLOR_PAIR,
    3: COLOR_TRIAD,
    4: COLOR_ATOM,
}
for _l in range(5, 33):
    t = min(1.0, (_l - 5) / 12.0)
    COLOR_BY_LEVEL[_l] = (1.0 - t) * COLOR_MOL_BASE + t * np.array([1.0, 0.2, 0.9])

# Frequency-layer colours (low → high band)
LAYER_COLORS = [
    np.array([0.20, 0.55, 1.00]),  # deep blue  — low band
    np.array([0.15, 0.95, 0.85]),  # cyan       — mid
    np.array([0.95, 0.35, 0.95]),  # violet     — high
    np.array([1.00, 0.45, 0.20]),  # orange-red — very high
]

# Field mesh resolution (balance quality vs speed)
FIELD_RES = 48          # grid samples per axis on each layer
FIELD_SIGMA = 6.0       # spatial kernel of each vibration's contribution (world units)
FIELD_AMP = 2.2         # vertical undulation amplitude
FIELD_K0 = 0.35         # spatial wave number scale
FIELD_OPACITY = 0.42

LEGEND = (
    "LEGEND — belief ontology\n"
    "  TRANSLUCENT SHEETS  = free vibration FIELD\n"
    "    stacked layers    = frequency dimensions (low→high)\n"
    "    endless undulation = continuous wave field (not particles)\n"
    "  ORANGE spheres      = electrons (bound)\n"
    "  WHITE               = atoms\n"
    "  GREEN→MAGENTA       = molecules\n"
    "KEYS  space pause  s step  r camera  q quit"
)


def _level_counts(world) -> str:
    parts = [f"field-src {int(world.s_alive.sum())}"]
    names = {1: "e-", 2: "pair", 3: "triad", 4: "atom"}
    for L, name in names.items():
        n = int(((world.k_level[: world.k_count] == L) & world.k_alive[: world.k_count]).sum())
        parts.append(f"{name} {n}")
    n_mol = int(((world.k_level[: world.k_count] >= 5) & world.k_alive[: world.k_count]).sum())
    parts.append(f"mol {n_mol}")
    return " | ".join(parts)


def _content_bounds(world) -> Optional[tuple]:
    pts = []
    if world.n_alive > 0:
        m = world.s_alive
        if m.any():
            pts.append(world.s_pos[m])
    if world.k_count > 0:
        m = world.k_alive[: world.k_count]
        if m.any():
            pts.append(world.k_pos[: world.k_count][m])
    bx, by, bz = world.config.box_size
    # Always include full box so the field layers stay in frame
    if not pts:
        return (0.0, float(bx), 0.0, float(by), 0.0, float(bz))
    allp = np.vstack(pts)
    lo = np.minimum(allp.min(axis=0), 0.0)
    hi = np.maximum(allp.max(axis=0), [bx, by, bz])
    pad = 2.0
    return (
        float(lo[0] - pad), float(hi[0] + pad),
        float(lo[1] - pad), float(hi[1] + pad),
        float(lo[2] - pad), float(hi[2] + pad),
    )


def _band_index(freq: float, n_bands: int) -> int:
    """Map frequency to layer index 0..n_bands-1 by log decade."""
    logf = np.log10(max(freq, 10.0))
    # decades roughly 2..5 → map to bands
    u = (logf - 2.0) / 3.0  # 100..10000
    u = float(np.clip(u, 0.0, 0.999))
    return int(u * n_bands)


def build_vibration_field_layers(
    world,
    *,
    n_bands: int = 4,
    res: int = FIELD_RES,
) -> List[Tuple[object, np.ndarray, float]]:
    """Build continuous layered field surfaces from free vibrations.

    Returns list of (pyvista StructuredGrid or PolyData, rgb color, opacity).
    Each layer is an **uninterrupted** undulating sheet spanning the full box
    in x–y, stacked along z by frequency band (a visual of hidden dimensions).
    """
    import pyvista as pv

    mask = np.asarray(world.s_alive, dtype=bool)
    if not mask.any():
        return []

    pos = np.ascontiguousarray(world.s_pos[mask], dtype=np.float64)
    freq = np.ascontiguousarray(world.s_freq[mask], dtype=np.float64)
    pol = np.asarray(world.s_pol[mask], dtype=bool)
    vel = np.ascontiguousarray(world.s_vel[mask], dtype=np.float64)
    t = float(world.t)
    bx, by, bz = map(float, world.config.box_size)

    # Assign each free vibration to a frequency layer
    bands = np.array([_band_index(float(f), n_bands) for f in freq], dtype=np.int32)

    # Base z of each layer (stacked dimensions)
    # leave room at bottom/top of box
    z_bases = np.linspace(0.12 * bz, 0.88 * bz, n_bands)

    xs = np.linspace(0.0, bx, res)
    ys = np.linspace(0.0, by, res)
    XX, YY = np.meshgrid(xs, ys, indexing="xy")  # shape (res, res)

    layers_out: List[Tuple[object, np.ndarray, float]] = []
    sigma2 = FIELD_SIGMA * FIELD_SIGMA
    two_pi = 2.0 * np.pi

    for b in range(n_bands):
        sel = bands == b
        if not np.any(sel):
            # empty layer: still draw a faint flat sheet (the dimension exists, quiet)
            ZZ = np.full_like(XX, z_bases[b])
            grid = pv.StructuredGrid(XX, YY, ZZ)
            col = LAYER_COLORS[b % len(LAYER_COLORS)]
            layers_out.append((grid, col, FIELD_OPACITY * 0.25))
            continue

        p = pos[sel]
        f = freq[sel]
        po = pol[sel]
        v = vel[sel]

        # Continuous field Φ(x,y) = Σ A_i exp(-r²/2σ²) sin(k_i·r + ω_i t)
        # endless: no packet window; contributions fill the whole plane
        field = np.zeros((res, res), dtype=np.float64)
        # polarity skew for colour modulation later
        even_mass = float(np.sum(po))
        odd_mass = float(np.sum(~po))
        total = max(even_mass + odd_mass, 1.0)

        for i in range(p.shape[0]):
            px, py = float(p[i, 0]), float(p[i, 1])
            dx = XX - px
            dy = YY - py
            # periodic wrap distance (shortest on torus)
            dx -= bx * np.round(dx / bx)
            dy -= by * np.round(dy / by)
            r2 = dx * dx + dy * dy
            amp = np.exp(-0.5 * r2 / sigma2)

            # wave vector from velocity (or default)
            sp = float(np.linalg.norm(v[i]))
            if sp > 1e-6:
                kx = FIELD_K0 * (1.0 + 0.5 * np.log10(max(f[i], 10.0))) * (v[i, 0] / sp)
                ky = FIELD_K0 * (1.0 + 0.5 * np.log10(max(f[i], 10.0))) * (v[i, 1] / sp)
            else:
                kmag = FIELD_K0 * (1.0 + 0.4 * np.log10(max(f[i], 10.0)))
                kx, ky = kmag, 0.3 * kmag

            omega = 0.015 * float(f[i])
            # polarity flips phase sign so even/odd interfere
            sign = 1.0 if po[i] else -1.0
            phase = sign * (kx * dx + ky * dy + omega * t)
            field += amp * np.sin(phase)

        # Normalise so undulation stays visible regardless of particle count
        peak = float(np.max(np.abs(field))) + 1e-9
        field = (field / peak) * FIELD_AMP

        ZZ = z_bases[b] + field
        grid = pv.StructuredGrid(XX, YY, ZZ)

        # Layer colour: mix even/odd mass into base band colour
        base = LAYER_COLORS[b % len(LAYER_COLORS)].copy()
        if odd_mass > even_mass:
            base = 0.65 * base + 0.35 * np.array([1.0, 0.25, 0.30])
        else:
            base = 0.65 * base + 0.35 * np.array([0.20, 0.50, 1.0])
        base = np.clip(base, 0.0, 1.0)
        opacity = FIELD_OPACITY * (0.55 + 0.45 * min(1.0, p.shape[0] / 40.0))
        layers_out.append((grid, base, float(opacity)))

    return layers_out


# Back-compat alias (interactive.py may import wave builder)
def build_vibration_waves(world):
    """Deprecated particle-wave API — returns field layers as a MultiBlock-like list.

    interactive.py expects (waves, backbone); we return (multiblock, None)
    for a soft transition, or None if empty.
    """
    import pyvista as pv

    layers = build_vibration_field_layers(world)
    if not layers:
        return None, None
    mb = pv.MultiBlock()
    for i, (grid, col, _op) in enumerate(layers):
        g = grid.copy()
        # solid colour array for multiblock path
        n = g.n_points
        rgb = np.tile((np.clip(col, 0, 1) * 255).astype(np.uint8), (n, 1))
        g["rgb"] = rgb
        mb.append(g)
    return mb, None


class BetLiveView:
    """Single-window live view driven from the experiment's main thread."""

    def __init__(self, title: str = "EQMOD BET live"):
        self.title = title
        self._pl = None
        self._closed = False
        self.playing = True
        self._step_once = False
        self._user_quit = False
        self._show_field = True
        self._show_nodes = True
        self._frame = 0

    def open(self, world) -> bool:
        try:
            import pyvista as pv
        except ImportError:
            print("[bet_live] pyvista not installed — live view disabled")
            return False
        try:
            bx, by, bz = world.config.box_size
            pl = pv.Plotter(title=self.title, window_size=(1280, 800))
            pl.set_background((0.02, 0.02, 0.05))  # deep space, not pure black
            box = pv.Box(bounds=(0, bx, 0, by, 0, bz))
            pl.add_mesh(
                box, style="wireframe", color=(0.40, 0.42, 0.55),
                line_width=2, name="box", opacity=0.85,
            )
            try:
                pl.enable_lightkit()
            except Exception:
                pass
            pl.add_key_event("space", self._toggle_play)
            pl.add_key_event("s", self._request_step)
            pl.add_key_event("q", self._request_quit)
            pl.add_key_event("r", lambda: self._reset_camera(world))
            pl.show(interactive_update=True, auto_close=False)
            self._pl = pl
            self._rebuild(world, hud_extra="field layers initialising…")
            self._reset_camera(world)
            pl.update()
            return True
        except Exception as exc:
            print(f"[bet_live] could not open window: {exc}")
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
            b = _content_bounds(world) if world is not None else None
            if b is not None:
                pl.reset_camera(bounds=b)
            else:
                pl.camera_position = "iso"
                pl.reset_camera()
            pl.camera.zoom(1.05)
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

    def _clear_dynamic(self, pl) -> None:
        # remove known dynamic names
        for name in list(getattr(pl.renderer, "actors", {}).keys()):
            s = str(name)
            if s in ("box",):
                continue
            if any(
                k in s
                for k in (
                    "field", "layer", "node", "vibr", "glyph", "hud", "legend",
                    "PolyData", "Structured", "MultiBlock",
                )
            ):
                try:
                    pl.remove_actor(name, render=False)
                except Exception:
                    pass
        for name in ("hud", "legend", "nodes"):
            try:
                pl.remove_actor(name, render=False)
            except Exception:
                pass

    def _rebuild(self, world, hud_extra: str = "") -> None:
        import pyvista as pv

        pl = self._pl
        if pl is None:
            return
        self._clear_dynamic(pl)
        w = world
        self._frame += 1

        # --- HIDDEN FIELD: continuous layered sheets ---
        if self._show_field:
            layers = build_vibration_field_layers(w, n_bands=4, res=FIELD_RES)
            for i, (grid, col, opacity) in enumerate(layers):
                try:
                    pl.add_mesh(
                        grid,
                        color=tuple(float(c) for c in col),
                        opacity=opacity,
                        smooth_shading=True,
                        name=f"field_layer_{i}",
                        show_edges=False,
                        specular=0.35,
                        specular_power=15,
                    )
                except Exception:
                    # fallback without fancy lighting
                    pl.add_mesh(
                        grid,
                        color=tuple(float(c) for c in col),
                        opacity=opacity,
                        name=f"field_layer_{i}",
                    )

        # --- BOUND MATTER: discrete spheres ---
        if self._show_nodes and w.k_count > 0:
            alive = np.asarray(w.k_alive[: w.k_count], dtype=bool)
            idx = np.where(alive)[0]
            if len(idx) > 0:
                positions = np.ascontiguousarray(w.k_pos[idx], dtype=np.float64)
                levels = w.k_level[idx].astype(np.int32)
                radii = np.array(
                    [RADIUS_BY_LEVEL.get(int(L), 2.0) for L in levels], dtype=np.float64
                )
                colors = np.array(
                    [COLOR_BY_LEVEL.get(int(L), COLOR_ATOM) for L in levels],
                    dtype=np.float64,
                )
                pc = pv.PolyData(positions)
                pc["rgb"] = (np.clip(colors, 0, 1) * 255.0).astype(np.uint8)
                pc["r"] = radii
                sphere = pv.Sphere(radius=1.0, theta_resolution=16, phi_resolution=16)
                glyphs = pc.glyph(geom=sphere, scale="r", orient=False, factor=1.0)
                pl.add_mesh(
                    glyphs, scalars="rgb", rgb=True, smooth_shading=True,
                    name="nodes", opacity=1.0,
                )

        hud = (
            f"{self.title}\n"
            f"t={w.t:7.2f}s\n"
            f"{_level_counts(w)}\n"
            f"{'[PAUSED]' if not self.playing else '[PLAYING]'}  space/s/r/q\n"
            f"{hud_extra}"
        )
        pl.add_text(hud, position="upper_left", font_size=11, color="white", name="hud")
        pl.add_text(LEGEND, position="lower_left", font_size=9, color=(0.70, 0.85, 0.90), name="legend")

        if self._frame % 12 == 1:
            self._reset_camera(w)

    def run_ticks(
        self,
        world,
        n_ticks: int,
        dt: float,
        *,
        ticks_per_frame: int = 5,
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
                self._rebuild(world, hud_extra=extra)
                self._pl.update()
                time.sleep(0.02 if self.playing else 0.04)
        except KeyboardInterrupt:
            self._user_quit = True

        while done < n_ticks:
            tick(world, dt)
            world.t += dt
            done += 1

        if self._window_alive() and not self._user_quit:
            try:
                self._rebuild(world, hud_extra=f"DONE {done}/{n_ticks}")
                self._pl.update()
                time.sleep(2.0)
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


def run_ticks_live(
    world,
    n_ticks: int,
    dt: float,
    *,
    live: bool = False,
    title: str = "EQMOD BET live",
    ticks_per_frame: int = 5,
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
