"""PyVista 3D live preview. Polls the world state at low frame rate. Read-only."""
from __future__ import annotations
import threading
import numpy as np

COLOR_VIBR_EVEN = (0.29, 0.56, 0.89)
COLOR_VIBR_ODD = (0.91, 0.30, 0.24)
COLOR_ELECTRON = (0.95, 0.61, 0.07)
COLOR_ATOM = (1.0, 1.0, 1.0)


class LivePreview:
    """Non-blocking PyVista viewer that polls a World instance. Run in a thread."""

    def __init__(self, world):
        self.world = world
        self._stop = threading.Event()
        self._plotter = None
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self._stop.set()
        self.thread.join(timeout=5.0)

    def _run(self):
        """Main loop — runs in background thread."""
        import time
        try:
            import pyvista as pv
        except ImportError:
            print("[preview] pyvista not available — preview disabled")
            return

        try:
            pl = pv.Plotter(title="World of Vibrations — live preview", off_screen=False)
            self._plotter = pl
        except Exception as exc:
            print(f"[preview] Could not open PyVista window: {exc}")
            return

        pl.show(interactive_update=True, auto_close=False)

        while not self._stop.is_set():
            pl.clear()
            self._add_geometry(pl)
            pl.update()
            time.sleep(0.1)  # 10 fps preview

        pl.close()

    def _add_geometry(self, pl):
        import pyvista as pv
        w = self.world

        # Vibrations as point cloud
        if w.n_alive > 0:
            alive_mask = w.s_alive
            pts = w.s_pos[alive_mask].copy()
            if len(pts) > 0:
                cloud = pv.PolyData(pts)
                # Per-point colors as RGB array (0-255 for pyvista scalars)
                pol = w.s_pol[alive_mask]
                colors = np.where(
                    pol[:, None],
                    np.array(COLOR_VIBR_EVEN),
                    np.array(COLOR_VIBR_ODD),
                )
                cloud["colors"] = (colors * 255).astype(np.uint8)
                pl.add_mesh(cloud, scalars="colors", rgb=True,
                            style="points", point_size=4, render_points_as_spheres=True)

        # Nodes as spheres sized by level
        for i in range(w.k_count):
            if not w.k_alive[i]:
                continue
            level = int(w.k_level[i])
            radius = {1: 1.0, 2: 1.5, 3: 2.0, 4: 3.0}.get(level, 1.0)
            color = COLOR_ELECTRON if level == 1 else COLOR_ATOM
            sphere = pv.Sphere(radius=radius, center=w.k_pos[i].tolist())
            pl.add_mesh(sphere, color=color, smooth_shading=True)
