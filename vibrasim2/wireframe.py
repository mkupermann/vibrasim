"""Simple real-time wireframe view over unmodified simulation frames.

The renderer is deliberately dumb: it draws only particles, bonds and field
paths supplied by the simulation.  It does not interpolate bonds, infer
surfaces or turn sparse geometry into organisms.
"""
from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable

import numpy as np


class BondState(str, Enum):
    STABLE = "stable"
    FORMING = "forming"
    BREAKING = "breaking"


BOND_COLORS = {
    BondState.STABLE: (120, 220, 235),
    BondState.FORMING: (80, 230, 140),
    BondState.BREAKING: (245, 145, 65),
}


@dataclass(frozen=True)
class WireframeFrame:
    positions: np.ndarray
    bonds: np.ndarray
    bond_states: tuple[BondState, ...]
    field_lines: tuple[np.ndarray, ...] = ()

    def __post_init__(self) -> None:
        positions = np.asarray(self.positions, dtype=float)
        bonds = np.asarray(self.bonds, dtype=np.int32)
        if positions.ndim != 2 or positions.shape[1:] != (3,):
            raise ValueError("positions must have shape (n, 3)")
        if bonds.size == 0:
            bonds = np.empty((0, 2), dtype=np.int32)
        if bonds.ndim != 2 or bonds.shape[1:] != (2,):
            raise ValueError("bonds must have shape (m, 2)")
        if len(self.bond_states) != len(bonds):
            raise ValueError("one bond state is required for each bond")
        if bonds.size and (int(bonds.min()) < 0 or int(bonds.max()) >= len(positions)):
            raise ValueError("bond endpoint is outside the particle array")
        field_lines = tuple(np.asarray(line, dtype=float) for line in self.field_lines)
        if any(line.ndim != 2 or line.shape[1:] != (3,) or len(line) < 2
               for line in field_lines):
            raise ValueError("field lines must each have shape (n>=2, 3)")
        object.__setattr__(self, "positions", positions.copy())
        object.__setattr__(self, "bonds", bonds.copy())
        object.__setattr__(self, "field_lines", tuple(line.copy() for line in field_lines))


@dataclass(frozen=True)
class WireframeGeometry:
    particle_points: np.ndarray
    bond_segments: np.ndarray
    bond_states: tuple[BondState, ...]
    bond_colors: np.ndarray
    field_lines: tuple[np.ndarray, ...]


@dataclass
class RenderCadence:
    """Throttle simulation-frame acquisition without throttling UI events."""

    frame_interval: float = 2.0
    next_due: float | None = None

    def frame_due(self, now: float, playing: bool, step_requested: bool) -> bool:
        if step_requested:
            self.next_due = now + self.frame_interval
            return True
        if not playing:
            return False
        if self.next_due is None or now >= self.next_due:
            self.next_due = now + self.frame_interval
            return True
        return False


def build_geometry(frame: WireframeFrame) -> WireframeGeometry:
    """Map a frame to render arrays without inventing or smoothing geometry."""
    segments = frame.positions[frame.bonds] if len(frame.bonds) else np.empty((0, 2, 3))
    colors = np.asarray([BOND_COLORS[state] for state in frame.bond_states], dtype=np.uint8)
    if not len(colors):
        colors = np.empty((0, 3), dtype=np.uint8)
    return WireframeGeometry(
        particle_points=frame.positions.copy(),
        bond_segments=segments.copy(),
        bond_states=frame.bond_states,
        bond_colors=colors,
        field_lines=tuple(line.copy() for line in frame.field_lines),
    )


def _line_mesh(segments: np.ndarray, colors: np.ndarray):
    import pyvista as pv

    points = segments.reshape(-1, 3)
    lines = np.column_stack(
        (np.full(len(segments), 2, dtype=np.int64),
         np.arange(0, 2 * len(segments), 2),
         np.arange(1, 2 * len(segments), 2))
    ).ravel()
    mesh = pv.PolyData(points, lines=lines)
    mesh.cell_data["state_rgb"] = colors
    return mesh


def _path_mesh(paths: tuple[np.ndarray, ...]):
    import pyvista as pv

    if not paths:
        return pv.PolyData()
    points = np.concatenate(paths)
    cells = []
    offset = 0
    for path in paths:
        cells.extend((len(path), *(offset + np.arange(len(path)))))
        offset += len(path)
    return pv.PolyData(points, lines=np.asarray(cells, dtype=np.int64))


def _add_frame_actors(plotter, frame: WireframeFrame, *, render: bool = False) -> None:
    import pyvista as pv

    geometry = build_geometry(frame)
    if len(geometry.particle_points):
        plotter.add_mesh(
            pv.PolyData(geometry.particle_points), style="points",
            color=(0.85, 0.88, 0.92), point_size=5,
            render_points_as_spheres=False, lighting=False,
            name="particles", render=render,
        )
    if len(geometry.bond_segments):
        plotter.add_mesh(
            _line_mesh(geometry.bond_segments, geometry.bond_colors),
            scalars="state_rgb", rgb=True, line_width=2, lighting=False,
            name="bonds", render=render,
        )
    if geometry.field_lines:
        plotter.add_mesh(
            _path_mesh(geometry.field_lines), color=(0.32, 0.42, 0.95),
            opacity=0.45, line_width=1, lighting=False,
            name="field", render=render,
        )


class WireframeViewer:
    """Single-threaded PyVista viewer for a stream of real simulation frames."""

    def __init__(
        self,
        next_frame: Callable[[], WireframeFrame],
        bounds: tuple[float, float, float, float, float, float],
        frame_interval: float = 2.0,
    ) -> None:
        self.next_frame = next_frame
        self.bounds = bounds
        self.cadence = RenderCadence(frame_interval=frame_interval)
        self.playing = True
        self.step_requested = False
        self._plotter = None

    def run(self) -> int:
        import pyvista as pv

        try:
            pl = pv.Plotter(title="Vibrasim II — wireframe", window_size=(1400, 900))
            self._plotter = pl
            pl.set_background("black")
            try:
                pl.disable_anti_aliasing()
            except Exception:
                pass
            # The cage is the simulation domain supplied by the caller, not an
            # inferred organism or interpolated experimental structure.
            pl.add_mesh(
                pv.Box(bounds=self.bounds), style="wireframe",
                color=(0.25, 0.28, 0.32), line_width=1, lighting=False,
                name="bounds",
            )
            pl.add_key_event("space", self._toggle_play)
            pl.add_key_event("s", self._step)
            pl.add_key_event("c", lambda: pl.view_isometric())
            pl.camera_position = "iso"
            self._draw(self.next_frame())
            self.cadence.frame_due(time.perf_counter(), playing=True,
                                   step_requested=False)
            pl.show(interactive_update=True, auto_close=False)
            while self._window_open(pl):
                now = time.perf_counter()
                if self.cadence.frame_due(now, self.playing, self.step_requested):
                    self._draw(self.next_frame())
                    self.step_requested = False
                pl.update()
                time.sleep(1.0 / 60.0)
        except KeyboardInterrupt:
            pass
        finally:
            if self._plotter is not None:
                self._plotter.close()
        return 0

    @staticmethod
    def _window_open(plotter) -> bool:
        if not getattr(plotter, "iren", None):
            return False
        render_window = getattr(plotter, "render_window", None)
        if render_window is None:
            return False
        try:
            return not (render_window.GetNeverRendered()
                        and not plotter.iren.initialized)
        except (AttributeError, RuntimeError):
            return False

    def _draw(self, frame: WireframeFrame) -> None:
        pl = self._plotter
        for name in ("particles", "bonds", "field"):
            try:
                pl.remove_actor(name, render=False)
            except Exception:
                pass
        _add_frame_actors(pl, frame)

    def _toggle_play(self) -> None:
        self.playing = not self.playing

    def _step(self) -> None:
        if not self.playing:
            self.step_requested = True


def _demo_source() -> Callable[[], WireframeFrame]:
    """Visual smoke source only; never use its frames as experimental data."""
    phase = 0.0
    angles = np.linspace(0.0, 2.0 * np.pi, 32, endpoint=False)

    def next_frame() -> WireframeFrame:
        nonlocal phase
        phase += 0.04
        radius = 12.0 + 0.6 * np.sin(3.0 * angles + phase)
        positions = np.column_stack(
            (radius * np.cos(angles), radius * np.sin(angles),
             1.5 * np.sin(2.0 * angles - phase))
        )
        bonds = np.column_stack((np.arange(32), np.roll(np.arange(32), -1)))
        states = tuple(
            BondState.FORMING if (i + int(phase * 4)) % 17 == 0 else
            BondState.BREAKING if (i + int(phase * 3)) % 23 == 0 else
            BondState.STABLE for i in range(32)
        )
        paths = tuple(
            np.column_stack((np.linspace(-28, 28, 80),
                             np.full(80, y),
                             2.0 * np.sin(np.linspace(-3, 3, 80) + phase + y / 8)))
            for y in (-18.0, -9.0, 0.0, 9.0, 18.0)
        )
        return WireframeFrame(positions, bonds, states, paths)

    return next_frame


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="run a visual smoke demo")
    args = parser.parse_args(argv)
    if not args.demo:
        parser.error("a simulation frame source is required; use --demo for the visual smoke")
    return WireframeViewer(_demo_source(), (-30, 30, -25, 25, -20, 20)).run()


if __name__ == "__main__":
    raise SystemExit(main())
