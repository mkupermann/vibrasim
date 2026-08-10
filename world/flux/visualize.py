"""Flux substrate visualization — single consolidated module.

Replaces the four parallel 2026-08-09/10 iterations (visualize / visualize_highend /
visualize_simple / visualize_live). Design constraints, from hard-won macOS lessons
(see LOGBOOK 2026-08-10):

  - PyVista/VTK must stay on the MAIN thread. No threading, no busy-wait loops.
    The simulation loop calls `update()` / `save_frame()` inline.
  - `off_screen` is passed to the Plotter constructor (not set afterward).
  - PyVista 0.48 API only: no raytrace=True, no multi_samples, no hide_grid(),
    text positions restricted to the corner/edge set.
  - Geometry sizes derive from the grid box, not absolute units — the historic
    "giant sphere" frame came from radius-3.0 spheres in an 80x40x10 box.
  - One actor per layer (glyphs / tubes), never one mesh per particle: the
    per-quantum pv.Sphere loop cost ~40 s per frame at n=1000.

Usage (inline from the simulation loop, main thread):

    viz = FluxVisualizer(quanta, grid, nodes, bridges)      # off-screen default
    viz.update(t=world_time)
    viz.save_frame("frames/frame_0001.png")
    viz.close()
"""
from __future__ import annotations

import numpy as np
from typing import TYPE_CHECKING

try:
    import pyvista as pv
    PV_AVAILABLE = True
except ImportError:
    PV_AVAILABLE = False

if TYPE_CHECKING:
    from world.flux.quantum import Quanta
    from world.flux.grid import Grid
    from world.flux.structures import Nodes
    from world.flux.bridges import Bridges


class FluxVisualizer:
    """Off-screen (default) or live single-window renderer for the Flux substrate.

    Layers:
      quanta  — shaded points (render_points_as_spheres), color by energy
      nodes   — sphere glyphs, gold, radius scaled to the box diagonal
      bridges — one combined tube mesh, magenta
    """

    def __init__(
        self,
        quanta: "Quanta",
        grid: "Grid",
        nodes: "Nodes | None" = None,
        bridges: "Bridges | None" = None,
        window_size: tuple[int, int] = (1400, 900),
        off_screen: bool = True,
        background_color: str = "black",
        orbit_deg_per_update: float = 0.6,
    ):
        if not PV_AVAILABLE:
            raise ImportError(
                "PyVista is required for visualization: pip install pyvista"
            )

        self.quanta = quanta
        self.grid = grid
        self.nodes = nodes
        self.bridges = bridges
        self.orbit_deg_per_update = orbit_deg_per_update

        # All geometry sizes are fractions of the box diagonal.
        box = np.array(grid.dims, dtype=np.float64) * grid.voxel_size
        self._box = box
        diag = float(np.linalg.norm(box))
        self._node_radius = 0.006 * diag
        self._bridge_radius = 0.0018 * diag

        self.plotter = pv.Plotter(window_size=window_size, off_screen=off_screen)
        self.plotter.set_background(background_color)

        light = pv.Light(
            position=tuple(box * 2.0),
            focal_point=tuple(box * 0.5),
            color="white",
            intensity=1.3,
        )
        self.plotter.add_light(light)

        # Box outline so scale stays readable even with few structures.
        outline = pv.Box(bounds=(0, box[0], 0, box[1], 0, box[2]))
        self.plotter.add_mesh(
            outline.extract_all_edges(), color="gray", opacity=0.25,
            line_width=1, name="box",
        )

        self.metrics = {"t": 0.0, "quanta": 0, "nodes": 0, "bridges": 0,
                        "energy": 0.0, "dream_events": 0, "self_aware_events": 0}
        self._camera_initialized = False
        self.update()

    def update(self, t: float = 0.0, dream_events: int = 0,
               self_aware_events: int = 0) -> None:
        """Rebuild the three layers from current state. Main thread only."""
        q, nodes, bridges = self.quanta, self.nodes, self.bridges

        self.metrics.update(
            t=t,
            quanta=q.n_alive(),
            nodes=nodes.n_alive() if nodes is not None else 0,
            bridges=bridges.n_alive() if bridges is not None else 0,
            energy=q.total_energy(),
            dream_events=dream_events,
            self_aware_events=self_aware_events,
        )

        # Quanta: one point cloud, shaded as spheres, colored by energy.
        alive = q.alive
        if alive.any():
            cloud = pv.PolyData(np.asarray(q.pos[alive], dtype=np.float64))
            cloud["energy"] = np.asarray(q.energy[alive], dtype=np.float64)
            self.plotter.add_mesh(
                cloud, name="quanta",
                render_points_as_spheres=True, point_size=6.0,
                scalars="energy", cmap="cool", show_scalar_bar=False,
                opacity=0.85,
            )
        else:
            self.plotter.remove_actor("quanta")

        # Nodes: sphere glyphs on one PolyData — a single actor.
        if nodes is not None and nodes.n_alive() > 0:
            npos = np.asarray(nodes.pos[nodes.alive], dtype=np.float64)
            pts = pv.PolyData(npos)
            glyphs = pts.glyph(
                geom=pv.Sphere(radius=self._node_radius,
                               theta_resolution=16, phi_resolution=16),
                scale=False, orient=False,
            )
            self.plotter.add_mesh(
                glyphs, name="nodes", color="gold",
                specular=0.8, specular_power=40, diffuse=0.6, ambient=0.25,
                smooth_shading=True,
            )
        else:
            self.plotter.remove_actor("nodes")

        # Bridges: all segments in ONE PolyData, one tube filter pass.
        if (bridges is not None and nodes is not None
                and bridges.n_alive() > 0):
            bmask = bridges.alive
            src_pos = np.asarray(nodes.pos[bridges.src[bmask]], dtype=np.float64)
            dst_pos = np.asarray(nodes.pos[bridges.dst[bmask]], dtype=np.float64)
            n_seg = len(src_pos)
            points = np.empty((2 * n_seg, 3), dtype=np.float64)
            points[0::2] = src_pos
            points[1::2] = dst_pos
            lines = np.empty((n_seg, 3), dtype=np.int64)
            lines[:, 0] = 2
            lines[:, 1] = np.arange(0, 2 * n_seg, 2)
            lines[:, 2] = np.arange(1, 2 * n_seg, 2)
            seg = pv.PolyData(points, lines=lines.ravel())
            tubes = seg.tube(radius=self._bridge_radius, n_sides=8)
            self.plotter.add_mesh(
                tubes, name="bridges", color="magenta",
                opacity=0.7, smooth_shading=True,
            )
        else:
            self.plotter.remove_actor("bridges")

        m = self.metrics
        text = (f"t = {m['t']:8.2f} s\n"
                f"quanta  {m['quanta']:6d}   energy {m['energy']:10.1f}\n"
                f"nodes   {m['nodes']:6d}   bridges {m['bridges']:6d}\n"
                f"dream   {m['dream_events']:6d}   self-aware {m['self_aware_events']:4d}")
        self.plotter.add_text(text, position="upper_left", font_size=11,
                              color="white", name="metrics", font="courier")

        if not self._camera_initialized:
            self.plotter.reset_camera()
            self.plotter.camera.azimuth = 30
            self.plotter.camera.elevation = 15
            self.plotter.camera.zoom(1.2)
            self._camera_initialized = True
        elif self.orbit_deg_per_update:
            self.plotter.camera.azimuth += self.orbit_deg_per_update

        self.plotter.render()

    def save_frame(self, filename: str) -> None:
        self.plotter.screenshot(filename)

    # Alias kept for callers written against the 08-09/10 iterations.
    def screenshot(self, filename: str) -> None:
        self.plotter.screenshot(filename)

    def show(self) -> None:
        """Open the interactive window (live mode; requires off_screen=False)."""
        self.plotter.show(auto_close=False)

    def close(self) -> None:
        self.plotter.close()


# Backwards-compatible name used by world/run.py --visualize.
SimpleFluxVisualizer = FluxVisualizer
