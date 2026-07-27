"""Interactive PyVista 3D viewer for the World of Vibrations.

Single-threaded design: the simulator and the renderer share the main loop.
The renderer's `iren.process_events` is called every frame, the simulator
ticks `speed` times between frames, and PyVista's native widgets (sliders,
checkbox buttons, point picker, key bindings) provide all interactivity.

Keyboard shortcuts (rendered into the on-screen HUD):
  space    play / pause
  s        single tick step (when paused)
  r        reset world to fresh seed
  v        toggle vibration point cloud
  n        toggle node spheres
  o        toggle bounding box
  l        toggle node labels (level digits over each node)
  +/-      bump speed (ticks per frame) up/down by 1
  c        reset camera
  S        save snapshot to ./snapshots/<t>.npz
  q        quit

Mouse:
  left-drag    orbit camera (pyvista default)
  shift-drag   pan
  scroll       zoom
  left-click   pick a node (when picking mode is on)

Sliders (left edge of window):
  speed        ticks per render frame, 0..60
  min level    hide nodes below this level (1..11)

Buttons (top-left):
  play/pause   green when playing, red when paused
  pick on/off  enables click-to-inspect a node
"""
from __future__ import annotations

import time
from dataclasses import replace
from pathlib import Path
from typing import Optional

import numpy as np

from world.config import WorldConfig, load_config
from world.physics import tick
from world.snapshot import save_snapshot, snapshot_filename
from world.state import World


# Same palette as the legacy preview, kept in sync deliberately.
COLOR_VIBR_EVEN = (0.29, 0.56, 0.89)
COLOR_VIBR_ODD = (0.91, 0.30, 0.24)
COLOR_ELECTRON = (0.95, 0.61, 0.07)
COLOR_ATOM = (1.0, 1.0, 1.0)

RADIUS_BY_LEVEL = {l: 1.0 + l * 0.5 for l in range(1, 33)}
RADIUS_BY_LEVEL[4] = 3.0  # atoms are visually distinct
COLOR_BY_LEVEL = {
    1: COLOR_ELECTRON,
    2: (0.85, 0.85, 0.90),
    3: (0.95, 0.92, 0.85),
    4: COLOR_ATOM,
}
# Level 5+: gradient from blue through green to red
for _l in range(5, 33):
    _t = (_l - 5) / 27.0
    COLOR_BY_LEVEL[_l] = (0.3 + 0.7 * _t, 0.9 - 0.5 * _t, 1.0 - 0.8 * _t)
LEVEL_NAMES = {1: "electron", 2: "pair", 3: "triad", 4: "atom"}
for _l in range(5, 33):
    LEVEL_NAMES[_l] = f"chain-{_l - 3}"  # chain-2, chain-3, ... chain-29


HELP_TEXT = (
    "space play/pause   s step   r reset   v vibr   n nodes\n"
    "o box   l labels   +/- speed   c camera   S snap   q quit"
)


class InteractiveViewer:
    """Single-window interactive simulator + renderer."""

    def __init__(self, config: WorldConfig, snapshot_dir: Optional[Path] = None):
        self.config = config
        self.world = World(config)
        self.snapshot_dir = snapshot_dir or Path("snapshots")
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

        # UI state
        self.playing = True
        self.speed = 1            # ticks per render frame
        self.min_level = 1        # filter
        self.show_vibrations = True
        self.show_nodes = True
        self.show_box = True
        self.show_labels = False
        self.picking_enabled = False
        self.selected_node: Optional[int] = None

        # Render bookkeeping
        self._pl = None
        self._vib_actor = None
        self._node_actor = None
        self._bridge_actor = None
        self._label_actor = None
        self._hud_actor = None
        self._info_actor = None
        self._help_actor = None
        self._box_actor = None
        self._last_render_t = time.time()
        self._frame_count = 0
        self._fps = 0.0
        self._step_once_requested = False

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def run(self) -> int:
        import pyvista as pv
        from world.gpu_viz import apply_plotter_gpu, configure_pyvista_gpu

        configure_pyvista_gpu(0, True)
        bx, by, bz = self.config.box_size
        pl = pv.Plotter(title="EQMOD — interactive substrate viewer", window_size=(1600, 1000))
        self._pl = pl
        pl.set_background("black")
        # Safe OpenGL — do not enable MSAA by default (AMD shader crashes)
        try:
            pl.disable_anti_aliasing()
        except Exception:
            pass

        # Static bounding box of the periodic substrate
        box = pv.Box(bounds=(0, bx, 0, by, 0, bz))
        self._box_actor = pl.add_mesh(box, style="wireframe", color=(0.3, 0.3, 0.35),
                                       line_width=1, name="box")

        # Initial geometry
        self._rebuild_vibrations()
        self._rebuild_nodes()
        self._rebuild_bridges()

        # HUD text actors
        self._hud_actor = pl.add_text("", position="upper_left",
                                      font_size=10, color="white", name="hud")
        self._info_actor = pl.add_text("", position="upper_right",
                                       font_size=10, color="yellow", name="info")
        self._help_actor = pl.add_text(HELP_TEXT, position="lower_left",
                                       font_size=8, color=(0.6, 0.6, 0.6), name="help")

        # Native widgets
        try:
            pl.add_slider_widget(
                self._on_speed_slider,
                rng=(0, 60), value=self.speed, title="speed (ticks/frame)",
                pointa=(0.025, 0.92), pointb=(0.225, 0.92),
                style="modern", fmt="%.0f",
            )
            pl.add_slider_widget(
                self._on_minlevel_slider,
                rng=(1, 11), value=self.min_level, title="min level",
                pointa=(0.025, 0.82), pointb=(0.225, 0.82),
                style="modern", fmt="%.0f",
            )
        except Exception as exc:
            print(f"[interactive] slider widgets unavailable: {exc}")

        try:
            pl.add_checkbox_button_widget(
                self._on_play_toggle, value=self.playing,
                position=(10, 10), size=30,
                color_on=(0.10, 0.70, 0.20), color_off=(0.80, 0.10, 0.10),
                border_size=2,
            )
            pl.add_checkbox_button_widget(
                self._on_pick_toggle, value=self.picking_enabled,
                position=(50, 10), size=30,
                color_on=(0.20, 0.50, 0.90), color_off=(0.40, 0.40, 0.45),
                border_size=2,
            )
        except Exception as exc:
            print(f"[interactive] button widgets unavailable: {exc}")

        # Key bindings
        pl.add_key_event("space", self._toggle_play)
        pl.add_key_event("s", self._step_once)
        pl.add_key_event("r", self._reset_world)
        pl.add_key_event("v", self._toggle_vibrations)
        pl.add_key_event("n", self._toggle_nodes)
        pl.add_key_event("o", self._toggle_box)
        pl.add_key_event("l", self._toggle_labels)
        pl.add_key_event("plus", self._speed_up)
        pl.add_key_event("minus", self._speed_down)
        pl.add_key_event("c", self._reset_camera)
        pl.add_key_event("S", self._save_snapshot)

        pl.camera_position = "iso"
        pl.show(interactive_update=True, auto_close=False)
        apply_plotter_gpu(pl)

        # Main loop — single thread, no race conditions
        try:
            while True:
                # Tick the world
                if self.playing or self._step_once_requested:
                    n = self.speed if self.playing else 1
                    for _ in range(max(1, n)):
                        tick(self.world, self.config.dt)
                    self._step_once_requested = False

                # Render
                self._rebuild_vibrations()
                self._rebuild_nodes()
                self._rebuild_bridges()
                self._update_labels()
                self._update_hud()

                pl.update()

                # Poll exit
                if not getattr(pl, "iren", None) or not pl.render_window:
                    break
                try:
                    rw = pl.render_window
                    if rw is None or rw.GetNeverRendered() and not pl.iren.initialized:
                        break
                except Exception:
                    pass

                # Frame pacing — cap at ~60 fps when idle
                self._tick_fps()
                if not self.playing and self.speed == 0:
                    time.sleep(0.03)
        except KeyboardInterrupt:
            pass
        finally:
            try:
                pl.close()
            except Exception:
                pass
        return 0

    # ------------------------------------------------------------------
    # Geometry rebuilds (cheap, per frame)
    # ------------------------------------------------------------------
    def _rebuild_vibrations(self):
        """Free vibrations as continuous layered field (hidden dimensions)."""
        pl = self._pl
        # remove previous field layers + legacy vib actor
        if self._vib_actor is not None:
            try:
                pl.remove_actor(self._vib_actor, render=False)
            except Exception:
                pass
            self._vib_actor = None
        for i in range(8):
            try:
                pl.remove_actor(f"field_layer_{i}", render=False)
            except Exception:
                pass
        try:
            pl.remove_actor("vib_backbone", render=False)
        except Exception:
            pass
        if not self.show_vibrations:
            return
        w = self.world
        try:
            from world.bet_live import build_vibration_field_layers
            layers = build_vibration_field_layers(w, n_bands=4)
        except Exception:
            return
        for i, (grid, col, opacity) in enumerate(layers):
            try:
                actor = pl.add_mesh(
                    grid,
                    color=tuple(float(c) for c in col),
                    opacity=opacity,
                    smooth_shading=False,
                    lighting=False,
                    name=f"field_layer_{i}",
                    show_edges=False,
                )
                if self._vib_actor is None:
                    self._vib_actor = actor
            except Exception:
                pass

    def _rebuild_nodes(self):
        import pyvista as pv
        pl = self._pl
        if self._node_actor is not None:
            try:
                pl.remove_actor(self._node_actor, render=False)
            except Exception:
                pass
            self._node_actor = None
        if not self.show_nodes:
            return

        w = self.world
        if w.k_count == 0:
            return

        # Vectorised: build one MultiBlock-style merged PolyData via glyphing.
        # Glyphing one sphere per node scales much better than the legacy
        # per-node add_mesh loop in preview.py.
        idx = np.where(w.k_alive[: w.k_count] & (w.k_level[: w.k_count] >= self.min_level))[0]
        if len(idx) == 0:
            return

        positions = w.k_pos[idx].copy()
        levels = w.k_level[idx].astype(np.int32)
        # Per-node radius and color
        radii = np.array([RADIUS_BY_LEVEL.get(int(l), 1.0) for l in levels])
        colors = np.array(
            [COLOR_BY_LEVEL.get(int(l), COLOR_ATOM) for l in levels]
        )

        pc = pv.PolyData(positions)
        pc["radius"] = radii
        pc["colors"] = (colors * 255).astype(np.uint8)
        pc["level"] = levels
        pc["index"] = idx.astype(np.int32)

        # Glyph: scale a unit sphere by per-point "radius"
        unit_sphere = pv.Sphere(radius=1.0, theta_resolution=32, phi_resolution=32)
        glyphs = pc.glyph(geom=unit_sphere, scale="radius", orient=False)
        # The glyph operation broadcasts point arrays; colors carry through.
        self._node_actor = pl.add_mesh(
            glyphs, scalars="colors", rgb=True, smooth_shading=False,
            lighting=False, name="nodes",
        )

        # Picking: bind picker to the original point cloud (not the glyph mesh)
        # so we get back node indices directly.
        if self.picking_enabled:
            try:
                pl.enable_point_picking(
                    callback=self._on_pick,
                    show_message=False,
                    use_picker=True,
                    pickable_window=False,
                    tolerance=0.025,
                    color="cyan",
                    point_size=14,
                )
            except Exception:
                pass

    def _rebuild_bridges(self):
        """Draw bridges as lines between connected atoms — shows membranes."""
        import pyvista as pv
        pl = self._pl
        if self._bridge_actor is not None:
            try:
                pl.remove_actor(self._bridge_actor, render=False)
            except Exception:
                pass
            self._bridge_actor = None

        w = self.world
        if not hasattr(w, 'b_count') or w.b_count == 0:
            return

        # Collect alive bridges as line segments
        pts = []
        lines = []
        n = 0
        for b in range(w.b_count):
            if not w.b_alive[b]:
                continue
            i, j = int(w.b_atom_i[b]), int(w.b_atom_j[b])
            if i >= w.k_count or j >= w.k_count:
                continue
            if not w.k_alive[i] or not w.k_alive[j]:
                continue
            # Skip bridges that wrap across the periodic boundary (visual clutter)
            box = np.asarray(w.config.box_size)
            d = w.k_pos[i] - w.k_pos[j]
            if np.any(np.abs(d) > box * 0.5):
                continue
            pts.append(w.k_pos[i]); pts.append(w.k_pos[j])
            lines.append([2, n, n + 1])
            n += 2

        if n == 0:
            return

        poly = pv.PolyData(np.array(pts), lines=np.hstack(lines))
        self._bridge_actor = pl.add_mesh(
            poly, color=(0.2, 1.0, 0.6), line_width=3,
            name="bridges",
        )

    def _update_labels(self):
        import pyvista as pv
        pl = self._pl
        if self._label_actor is not None:
            try:
                pl.remove_actor(self._label_actor, render=False)
            except Exception:
                pass
            self._label_actor = None
        if not self.show_labels:
            return
        w = self.world
        if w.k_count == 0:
            return
        idx = np.where(w.k_alive[: w.k_count] & (w.k_level[: w.k_count] >= self.min_level))[0]
        if len(idx) == 0:
            return
        # Cap labels to avoid font cost when N is huge
        if len(idx) > 200:
            idx = idx[:200]
        positions = w.k_pos[idx]
        labels = [f"{int(w.k_level[i])}" for i in idx]
        self._label_actor = pl.add_point_labels(
            positions, labels, font_size=10, text_color="cyan",
            point_size=0, shape=None, always_visible=True,
            name="labels",
        )

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------
    def _update_hud(self):
        w = self.world
        cfg = self.config
        n_v = int(w.s_alive.sum())
        levels = w.k_level[: w.k_count]
        alive = w.k_alive[: w.k_count]
        def count(L):
            return int(((levels == L) & alive).sum())
        n_e = count(1)
        n_p = count(2)
        n_t = count(3)
        n_a = count(4)
        n_m = int(((levels >= 5) & alive).sum())
        max_lvl = int(levels[alive].max()) if alive.any() else 0

        state = "PLAYING" if self.playing else "PAUSED"
        speed = self.speed
        hud = (
            f"EQMOD -- {state}   speed x{speed}   fps {self._fps:5.1f}\n"
            f"t = {w.t:8.3f} s    dt = {cfg.dt:.4f}    seed = {cfg.rng_seed}\n"
            f"vibr {n_v:5d}   e- {n_e:4d}   pair {n_p:3d}   triad {n_t:3d}   "
            f"atom {n_a:3d}   mol {n_m:3d}   MAX LEVEL {max_lvl}\n"
            f"box {cfg.box_size}   nodes_alive {int(alive.sum())}/{w.k_count}   "
            f"min_level={self.min_level}"
        )
        try:
            self._hud_actor.SetText(2, hud)  # 2 = upper-left in vtkCornerAnnotation
        except Exception:
            pass

        # Info pane: selected node
        info = ""
        if self.selected_node is not None and self.selected_node < w.k_count:
            i = self.selected_node
            if w.k_alive[i]:
                lvl = int(w.k_level[i])
                info = (
                    f"selected node #{i}\n"
                    f"  level {lvl} ({LEVEL_NAMES.get(lvl, '?')})\n"
                    f"  pos   ({w.k_pos[i,0]:.2f}, {w.k_pos[i,1]:.2f}, {w.k_pos[i,2]:.2f})\n"
                    f"  freq  {w.k_freq[i]:.2f}   pol {bool(w.k_pol[i])}\n"
                    f"  born  t={w.k_birth[i]:.3f}   age {w.t - w.k_birth[i]:.2f}s\n"
                    f"  pattern_id {int(w.k_pattern_id[i])}\n"
                    f"  charge {w.k_charge[i]:.3f}   strength {w.k_strength[i]:.3f}\n"
                    f"  eligibility {w.k_eligibility[i]:.3f}"
                )
            else:
                info = f"selected node #{i} (dead)"
        try:
            self._info_actor.SetText(3, info)  # 3 = upper-right
        except Exception:
            pass

    def _tick_fps(self):
        self._frame_count += 1
        now = time.time()
        dt = now - self._last_render_t
        if dt >= 0.5:
            self._fps = self._frame_count / dt
            self._frame_count = 0
            self._last_render_t = now

    # ------------------------------------------------------------------
    # Event callbacks
    # ------------------------------------------------------------------
    def _on_speed_slider(self, value):
        self.speed = int(round(value))

    def _on_minlevel_slider(self, value):
        self.min_level = int(round(value))

    def _on_play_toggle(self, value):
        self.playing = bool(value)

    def _on_pick_toggle(self, value):
        self.picking_enabled = bool(value)
        if not self.picking_enabled and self._pl is not None:
            try:
                self._pl.disable_picking()
            except Exception:
                pass

    def _toggle_play(self):
        self.playing = not self.playing

    def _step_once(self):
        if not self.playing:
            self._step_once_requested = True

    def _reset_world(self):
        self.world = World(self.config)
        self.selected_node = None

    def _toggle_vibrations(self):
        self.show_vibrations = not self.show_vibrations

    def _toggle_nodes(self):
        self.show_nodes = not self.show_nodes

    def _toggle_box(self):
        self.show_box = not self.show_box
        if self._box_actor is not None:
            try:
                self._box_actor.SetVisibility(self.show_box)
            except Exception:
                pass

    def _toggle_labels(self):
        self.show_labels = not self.show_labels

    def _speed_up(self):
        self.speed = min(60, self.speed + 1)

    def _speed_down(self):
        self.speed = max(0, self.speed - 1)

    def _reset_camera(self):
        if self._pl is not None:
            self._pl.camera_position = "iso"
            self._pl.reset_camera()

    def _save_snapshot(self):
        path = self.snapshot_dir / snapshot_filename(self.world.t)
        save_snapshot(self.world, path)
        print(f"[interactive] snapshot saved to {path}")

    def _on_pick(self, picked_point, picker=None):
        """Map a picked 3D point to the nearest live node index."""
        if picked_point is None:
            return
        w = self.world
        if w.k_count == 0:
            return
        alive_idx = np.where(w.k_alive[: w.k_count])[0]
        if len(alive_idx) == 0:
            return
        positions = w.k_pos[alive_idx]
        d2 = np.sum((positions - np.asarray(picked_point)) ** 2, axis=1)
        nearest = int(alive_idx[int(np.argmin(d2))])
        self.selected_node = nearest


def run_interactive(config_path: Optional[Path] = None,
                    seed: Optional[int] = None,
                    snapshot_dir: Optional[Path] = None) -> int:
    """CLI helper: load config, build viewer, run."""
    cfg = load_config(config_path)
    if seed is not None:
        cfg = replace(cfg, rng_seed=seed)
    viewer = InteractiveViewer(cfg, snapshot_dir=snapshot_dir)
    return viewer.run()
