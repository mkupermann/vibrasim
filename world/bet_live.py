"""Live 3D PyVista visualisation for BET / belief-path experiments.

Main-thread viewer (VTK is happier on the UI thread than `LivePreview`'s
background thread). Call from experiment runners with ``--live``:

    from world.bet_live import run_ticks_live

    run_ticks_live(world, n_ticks, dt, title="BP-A1 cluster", live=True)

Keyboard while open:
  q / Esc   close early and finish remaining ticks headless
  space     pause / resume physics
  s         single step when paused
"""
from __future__ import annotations

import time
from typing import Callable, Optional

import numpy as np

from world.physics import tick

COLOR_VIBR_EVEN = (0.29, 0.56, 0.89)
COLOR_VIBR_ODD = (0.91, 0.30, 0.24)
COLOR_ELECTRON = (0.95, 0.61, 0.07)
COLOR_ATOM = (1.0, 1.0, 1.0)

RADIUS_BY_LEVEL = {l: 1.0 + l * 0.5 for l in range(1, 33)}
RADIUS_BY_LEVEL[4] = 3.0
COLOR_BY_LEVEL = {
    1: COLOR_ELECTRON,
    2: (0.85, 0.85, 0.90),
    3: (0.95, 0.92, 0.85),
    4: COLOR_ATOM,
}
for _l in range(5, 33):
    _t = (_l - 5) / 27.0
    COLOR_BY_LEVEL[_l] = (0.3 + 0.7 * _t, 0.9 - 0.5 * _t, 1.0 - 0.8 * _t)


def _level_counts(world) -> str:
    parts = []
    for L, name in ((1, "e-"), (2, "pair"), (3, "triad"), (4, "atom")):
        n = int(((world.k_level[: world.k_count] == L) & world.k_alive[: world.k_count]).sum())
        if n:
            parts.append(f"{name} {n}")
    n_mol = int(((world.k_level[: world.k_count] >= 5) & world.k_alive[: world.k_count]).sum())
    if n_mol:
        parts.append(f"mol {n_mol}")
    n_v = int(world.s_alive.sum())
    parts.insert(0, f"vibr {n_v}")
    return "  ".join(parts)


class BetLiveView:
    """Single-window live view driven from the experiment's main thread."""

    def __init__(self, title: str = "EQMOD BET live"):
        self.title = title
        self._pl = None
        self._closed = False
        self.playing = True
        self._step_once = False
        self._user_quit = False

    def open(self, world) -> bool:
        try:
            import pyvista as pv
        except ImportError:
            print("[bet_live] pyvista not installed — live view disabled")
            return False
        try:
            bx, by, bz = world.config.box_size
            pl = pv.Plotter(title=self.title)
            pl.set_background("black")
            box = pv.Box(bounds=(0, bx, 0, by, 0, bz))
            pl.add_mesh(box, style="wireframe", color=(0.3, 0.3, 0.35), line_width=1, name="box")
            pl.add_key_event("space", self._toggle_play)
            pl.add_key_event("s", self._request_step)
            pl.add_key_event("q", self._request_quit)
            pl.camera_position = "iso"
            pl.show(interactive_update=True, auto_close=False)
            self._pl = pl
            self._rebuild(world, hud_extra="")
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

    def _rebuild(self, world, hud_extra: str = "") -> None:
        import pyvista as pv

        pl = self._pl
        if pl is None:
            return
        # Clear dynamic actors by name if present
        for name in ("vibrations", "nodes", "hud"):
            try:
                pl.remove_actor(name, render=False)
            except Exception:
                pass

        w = world
        if w.n_alive > 0:
            mask = w.s_alive
            pts = w.s_pos[mask]
            if len(pts) > 0:
                cloud = pv.PolyData(pts.copy())
                pol = w.s_pol[mask]
                colors = np.where(
                    pol[:, None],
                    np.array(COLOR_VIBR_EVEN),
                    np.array(COLOR_VIBR_ODD),
                )
                cloud["colors"] = (colors * 255).astype(np.uint8)
                pl.add_mesh(
                    cloud, scalars="colors", rgb=True,
                    style="points", point_size=6, render_points_as_spheres=True,
                    name="vibrations",
                )

        if w.k_count > 0:
            idx = np.where(w.k_alive[: w.k_count])[0]
            if len(idx) > 0:
                positions = w.k_pos[idx].copy()
                levels = w.k_level[idx].astype(np.int32)
                radii = np.array([RADIUS_BY_LEVEL.get(int(L), 1.0) for L in levels])
                colors = np.array([COLOR_BY_LEVEL.get(int(L), COLOR_ATOM) for L in levels])
                pc = pv.PolyData(positions)
                pc["radius"] = radii
                pc["colors"] = (colors * 255).astype(np.uint8)
                unit = pv.Sphere(radius=1.0, theta_resolution=16, phi_resolution=16)
                glyphs = pc.glyph(geom=unit, scale="radius", orient=False)
                pl.add_mesh(glyphs, scalars="colors", rgb=True, smooth_shading=True, name="nodes")

        hud = (
            f"{self.title}\n"
            f"t={w.t:7.2f}s   {_level_counts(w)}\n"
            f"{'[PAUSED space=play]' if not self.playing else '[playing space=pause]'}  "
            f"s=step  q=skip rest headless\n"
            f"{hud_extra}"
        )
        pl.add_text(hud, position="upper_left", font_size=10, color="white", name="hud")

    def run_ticks(
        self,
        world,
        n_ticks: int,
        dt: float,
        *,
        ticks_per_frame: int = 5,
        hud_fn: Optional[Callable] = None,
    ) -> int:
        """Advance *n_ticks*; returns ticks actually simulated (may equal n_ticks after headless catch-up)."""
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
        except KeyboardInterrupt:
            self._user_quit = True

        # Finish remaining ticks headless if user closed / quit early
        while done < n_ticks:
            tick(world, dt)
            world.t += dt
            done += 1
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
    """Physics loop with optional live 3D window.

    When ``live`` is False, identical to a plain tick loop (headless BETs unchanged).
    """
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
