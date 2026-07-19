"""Live 3D PyVista visualisation for BET / belief-path experiments.

Main-thread viewer. Entities are **large, colour-coded spheres** so they are
actually visible (not 6px dust on black):

  FREE VIBRATIONS  blue (even polarity) / red (odd)  — mid-size spheres
  ELECTRON (L1)    bright orange
  PAIR (L2)        silver
  TRIAD (L3)       cream
  ATOM (L4)        white (largest of the small set)
  MOLECULE (L5+)   green → magenta by level

Also draws short **velocity sticks** on free vibrations (motion / “wave” cue)
and a legend. Camera recentres on content each frame.

Keyboard:
  space  pause / play
  s      single step when paused
  q      quit / skip rest headless
  r      reset camera to content
  1–5    toggle visibility filters (see HUD)
"""
from __future__ import annotations

import time
from typing import Callable, Optional

import numpy as np

from world.physics import tick

# Bright, high-contrast palette (0–1 RGB)
COLOR_VIBR_EVEN = np.array([0.15, 0.55, 1.00])   # electric blue
COLOR_VIBR_ODD = np.array([1.00, 0.20, 0.25])    # hot red
COLOR_ELECTRON = np.array([1.00, 0.65, 0.05])    # amber
COLOR_PAIR = np.array([0.75, 0.80, 0.90])
COLOR_TRIAD = np.array([1.00, 0.90, 0.55])
COLOR_ATOM = np.array([1.00, 1.00, 1.00])
COLOR_MOL_BASE = np.array([0.20, 1.00, 0.45])

# Visual radii in world units (box is typically 60–80)
R_VIBR = 0.85
RADIUS_BY_LEVEL = {
    1: 1.4,   # electron
    2: 1.8,   # pair
    3: 2.2,   # triad
    4: 2.8,   # atom
}
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

LEGEND = (
    "LEGEND\n"
    "  BLUE / RED spheres = free vibrations (even / odd polarity)\n"
    "  short sticks         = velocity (motion)\n"
    "  ORANGE              = electrons\n"
    "  SILVER / CREAM      = pairs / triads\n"
    "  WHITE               = atoms\n"
    "  GREEN→MAGENTA       = molecules (higher level)\n"
    "KEYS  space pause  s step  r camera  q quit"
)


def _level_counts(world) -> str:
    parts = [f"vibr {int(world.s_alive.sum())}"]
    names = {1: "e-", 2: "pair", 3: "triad", 4: "atom"}
    for L, name in names.items():
        n = int(((world.k_level[: world.k_count] == L) & world.k_alive[: world.k_count]).sum())
        parts.append(f"{name} {n}")
    n_mol = int(((world.k_level[: world.k_count] >= 5) & world.k_alive[: world.k_count]).sum())
    parts.append(f"mol {n_mol}")
    return " | ".join(parts)


def _content_bounds(world) -> Optional[tuple]:
    """Axis-aligned bounds of all visible content, or None if empty."""
    pts = []
    if world.n_alive > 0:
        m = world.s_alive
        if m.any():
            pts.append(world.s_pos[m])
    if world.k_count > 0:
        m = world.k_alive[: world.k_count]
        if m.any():
            pts.append(world.k_pos[: world.k_count][m])
    if not pts:
        return None
    allp = np.vstack(pts)
    lo = allp.min(axis=0)
    hi = allp.max(axis=0)
    # pad
    pad = 4.0
    lo = lo - pad
    hi = hi + pad
    return (float(lo[0]), float(hi[0]), float(lo[1]), float(hi[1]), float(lo[2]), float(hi[2]))


class BetLiveView:
    """Single-window live view driven from the experiment's main thread."""

    def __init__(self, title: str = "EQMOD BET live"):
        self.title = title
        self._pl = None
        self._closed = False
        self.playing = True
        self._step_once = False
        self._user_quit = False
        self._show_vibr = True
        self._show_nodes = True
        self._show_vel = True
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
            pl.set_background("black")
            # Soft grey box so content pops
            box = pv.Box(bounds=(0, bx, 0, by, 0, bz))
            pl.add_mesh(
                box, style="wireframe", color=(0.45, 0.45, 0.55),
                line_width=2, name="box", opacity=0.9,
            )
            # Lighting
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
            self._rebuild(world, hud_extra="starting…")
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
            pl.camera.zoom(1.15)
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
        for name in ("vibrations", "vib_vel", "nodes", "hud", "legend"):
            try:
                pl.remove_actor(name, render=False)
            except Exception:
                pass
        # Also strip leftover actors that share prefixes (pyvista renames sometimes)
        try:
            actors = list(getattr(pl.renderer, "actors", {}).keys())
            for name in actors:
                if any(k in str(name) for k in ("vibr", "node", "glyph", "PolyData")):
                    try:
                        pl.remove_actor(name, render=False)
                    except Exception:
                        pass
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

        # --- FREE VIBRATIONS as large coloured spheres ---
        if self._show_vibr and w.n_alive > 0:
            mask = np.asarray(w.s_alive, dtype=bool)
            n = int(mask.sum())
            if n > 0:
                pts = np.ascontiguousarray(w.s_pos[mask], dtype=np.float64)
                pol = np.asarray(w.s_pol[mask], dtype=bool)
                colors = np.zeros((n, 3), dtype=np.float64)
                colors[pol] = COLOR_VIBR_EVEN
                colors[~pol] = COLOR_VIBR_ODD
                # Slight frequency brightness variation so bands differ
                freq = np.asarray(w.s_freq[mask], dtype=np.float64)
                f01 = np.clip(np.log10(np.maximum(freq, 10.0)) / 5.0, 0.0, 1.0)
                colors = colors * (0.65 + 0.35 * f01[:, None])
                colors = np.clip(colors, 0.0, 1.0)

                pc = pv.PolyData(pts)
                pc["rgb"] = (colors * 255.0).astype(np.uint8)
                pc["r"] = np.full(n, R_VIBR, dtype=np.float64)
                sphere = pv.Sphere(radius=1.0, theta_resolution=12, phi_resolution=12)
                glyphs = pc.glyph(geom=sphere, scale="r", orient=False, factor=1.0)
                pl.add_mesh(
                    glyphs, scalars="rgb", rgb=True, smooth_shading=True,
                    name="vibrations", opacity=0.95,
                )

                # Velocity sticks (motion / wave cue)
                if self._show_vel:
                    vel = np.ascontiguousarray(w.s_vel[mask], dtype=np.float64)
                    speed = np.linalg.norm(vel, axis=1, keepdims=True)
                    speed = np.maximum(speed, 1e-6)
                    direction = vel / speed
                    # stick length proportional to speed, capped
                    length = np.clip(speed.ravel() * 0.08, 0.5, 3.5)
                    ends = pts + direction * length[:, None]
                    # lines: pack as cells
                    line_pts = np.vstack([pts, ends])
                    lines = np.zeros((n, 3), dtype=np.int64)
                    lines[:, 0] = 2
                    lines[:, 1] = np.arange(n)
                    lines[:, 2] = np.arange(n, 2 * n)
                    pdata = pv.PolyData()
                    pdata.points = line_pts
                    pdata.lines = lines.ravel()
                    pl.add_mesh(
                        pdata, color=(0.9, 0.9, 0.3), line_width=2,
                        name="vib_vel", opacity=0.7,
                    )

        # --- NODES (electrons → molecules) as large spheres ---
        if self._show_nodes and w.k_count > 0:
            alive = np.asarray(w.k_alive[: w.k_count], dtype=bool)
            idx = np.where(alive)[0]
            if len(idx) > 0:
                positions = np.ascontiguousarray(w.k_pos[idx], dtype=np.float64)
                levels = w.k_level[idx].astype(np.int32)
                radii = np.array([RADIUS_BY_LEVEL.get(int(L), 2.0) for L in levels], dtype=np.float64)
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

        # HUD + legend
        hud = (
            f"{self.title}\n"
            f"t={w.t:7.2f}s\n"
            f"{_level_counts(w)}\n"
            f"{'[PAUSED]' if not self.playing else '[PLAYING]'}  "
            f"space/s/r/q\n"
            f"{hud_extra}"
        )
        pl.add_text(hud, position="upper_left", font_size=11, color="white", name="hud")
        pl.add_text(LEGEND, position="lower_left", font_size=9, color=(0.75, 0.85, 0.75), name="legend")

        # Keep content framed
        if self._frame % 8 == 1:
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
                if not self.playing:
                    time.sleep(0.03)
                else:
                    time.sleep(0.01)  # slight yield so window stays responsive
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
