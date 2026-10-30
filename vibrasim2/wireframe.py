"""Simple real-time wireframe view over supplied observation frames.

The renderer is deliberately dumb: it draws only particles, edges and field
paths supplied by the observation process. It does not infer structure.
"""
from __future__ import annotations

import argparse
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from queue import Empty, Full, Queue
from typing import Callable, Iterable

import numpy as np

from vibrasim2.observation import EdgeKind, EdgeState, WireframeFrame


@dataclass(frozen=True)
class WireframeGeometry:
    particle_points: np.ndarray
    particle_values: np.ndarray
    edge_segments: np.ndarray
    edge_states: tuple[EdgeState, ...]
    edge_colors: np.ndarray
    edge_kinds: tuple[EdgeKind, ...]
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
    segments = frame.positions[frame.edges] if len(frame.edges) else np.empty((0, 2, 3))
    colors = np.asarray([EDGE_COLORS[state] for state in frame.edge_states], dtype=np.uint8)
    if not len(colors):
        colors = np.empty((0, 3), dtype=np.uint8)
    return WireframeGeometry(
        particle_points=frame.positions.copy(),
        particle_values=frame.particle_values.copy(),
        edge_segments=segments.copy(),
        edge_states=frame.edge_states,
        edge_colors=colors,
        edge_kinds=frame.edge_kinds,
        field_lines=tuple(line.copy() for line in frame.field_lines),
    )


EDGE_COLORS = {
    EdgeState.SUPPLIED: (150, 170, 185),
    EdgeState.AVAILABLE: (70, 78, 88),
    EdgeState.LIVE: (255, 154, 46),
}


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
        particles = pv.PolyData(geometry.particle_points)
        if len(geometry.particle_values):
            particles.point_data["reservoir"] = geometry.particle_values
            plotter.add_mesh(
                particles, style="points", scalars="reservoir", cmap="plasma",
                clim=(0.0, 1.0), point_size=6, show_scalar_bar=False,
                render_points_as_spheres=False, lighting=False,
                name="particles", render=render,
            )
        else:
            plotter.add_mesh(
                particles, style="points", color=(0.85, 0.88, 0.92), point_size=5,
                render_points_as_spheres=False, lighting=False,
                name="particles", render=render,
            )
    if len(geometry.edge_segments):
        plotter.add_mesh(
            _line_mesh(geometry.edge_segments, geometry.edge_colors),
            scalars="state_rgb", rgb=True, line_width=2, lighting=False,
            name="edges", render=render,
        )
    if geometry.field_lines:
        plotter.add_mesh(
            _path_mesh(geometry.field_lines), color=(0.32, 0.42, 0.95),
            opacity=0.45, line_width=1, lighting=False,
            name="field", render=render,
        )


class WireframeViewer:
    """Single-threaded PyVista viewer for copied observation envelopes."""

    def __init__(
        self,
        frame_queue,
        stop_event,
        config,
        *,
        demo: bool = False,
        stream_kind: str = "live",
        recorded_verdict: str | None = None,
    ) -> None:
        from vibrasim2.viewer_process import ViewerController

        self.frame_queue = frame_queue
        self.stop_event = stop_event
        self.config = config
        self.controller = ViewerController(
            stream_kind=stream_kind, recorded_verdict=recorded_verdict
        )
        self.cadence = RenderCadence(frame_interval=config.draw_interval_seconds)
        self.demo = demo
        rows, columns = config.grid_shape
        self.bounds = (0.0, float(rows), 0.0, float(columns), -64.0, 64.0)
        self._plotter = None

    def run(self) -> int:
        import pyvista as pv

        try:
            pl = pv.Plotter(title="Vibrasim II — wireframe", window_size=(1400, 900))
            self._plotter = pl
            pl.set_background("black")
            pl.camera_position = self.config.camera_position
            try:
                pl.camera.focal_point = self.config.camera_focal_point
            except (AttributeError, RuntimeError):
                pass
            if self.demo:
                pl.add_text(
                    "ENGINEERING SMOKE — NOT SIMULATION DATA",
                    name="engineering-smoke", position="upper_left", color="white",
                )
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
            pl.add_key_event("space", self._toggle_freeze)
            pl.add_key_event("c", lambda: setattr(pl, "camera_position", self.config.camera_position))
            pl.show(interactive_update=True, auto_close=False)
            while self._window_open(pl):
                self._poll_and_draw(time.perf_counter())
                pl.update()
                if self.stop_event is not None and self.stop_event.is_set():
                    self._final_drain(pl)
                    break
                time.sleep(1.0 / 60.0)
        except KeyboardInterrupt:
            pass
        finally:
            if self._plotter is not None:
                self._plotter.close()
        return 0

    def _poll_and_draw(self, now: float) -> None:
        self.controller.drain(self.frame_queue)
        if self.cadence.frame_due(now, playing=True, step_requested=False):
            frame = self.controller.next_drawable()
            if frame is not None:
                self._draw(frame)

    def _final_drain(self, plotter) -> None:
        deadline = time.perf_counter() + 0.25
        while time.perf_counter() < deadline:
            count = self.controller.drain(self.frame_queue)
            frame = self.controller.next_drawable()
            if frame is not None:
                self._draw(frame)
            plotter.update()
            if count == 0:
                break

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

    def _draw(self, envelope) -> None:
        pl = self._plotter
        for name in ("particles", "edges", "field", "observation-hud"):
            try:
                pl.remove_actor(name, render=False)
            except Exception:
                pass
        _add_frame_actors(pl, envelope.frame)
        pl.add_text(
            self.controller.hud(), name="observation-hud", position="lower_left",
            color="white",
        )

    def _toggle_freeze(self) -> None:
        self.controller.set_frozen(not self.controller.frozen)


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
        edges = np.column_stack((np.arange(32), np.roll(np.arange(32), -1)))
        states = (EdgeState.SUPPLIED,) * len(edges)
        kinds = (EdgeKind.MATTER,) * len(edges)
        paths = tuple(
            np.column_stack((np.linspace(-28, 28, 80),
                             np.full(80, y),
                             2.0 * np.sin(np.linspace(-3, 3, 80) + phase + y / 8)))
            for y in (-18.0, -9.0, 0.0, 9.0, 18.0)
        )
        return WireframeFrame(positions, edges, states, kinds, paths)

    return next_frame


def _put_latest(frame_queue: Queue, frame) -> None:
    """Keep the transport bounded while preferring the newest observation."""
    try:
        frame_queue.put_nowait(frame)
    except Full:
        try:
            frame_queue.get_nowait()
            frame_queue.put_nowait(frame)
        except (Empty, Full):
            pass


def iter_replay_cycles(
    path: Path,
    *,
    loop: bool,
    stop_event=None,
    source_factory=None,
):
    """Replay persisted evidence once or repeatedly without altering frames."""
    if source_factory is None:
        from vibrasim2.viewer_process import iter_replay_envelopes

        source_factory = iter_replay_envelopes
    while True:
        yielded = False
        for envelope in source_factory(path):
            yielded = True
            yield envelope
            if stop_event is not None and stop_event.is_set():
                return
        if not loop or not yielded or (stop_event is not None and stop_event.is_set()):
            return


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sources = parser.add_mutually_exclusive_group(required=True)
    sources.add_argument("--demo", action="store_true", help="run a visual smoke demo")
    sources.add_argument(
        "--replay", type=Path,
        help="replay persisted observation snapshots without running dynamics",
    )
    parser.add_argument(
        "--loop", action="store_true",
        help="repeat a persisted replay until its window is closed",
    )
    args = parser.parse_args(argv)
    from vibrasim2.viewer_process import viewer_config_for_registered_p0

    if args.replay is not None and not args.replay.exists():
        parser.error(f"replay path does not exist: {args.replay}")
    if args.loop and args.replay is None:
        parser.error("--loop requires --replay")

    frame_queue = Queue(maxsize=1)
    stop_event = threading.Event()
    recorded_verdict = None
    replay_source_factory = None
    if args.replay is not None:
        from vibrasim2.viewer_process import iter_replay_envelopes, replay_verdict

        recorded_verdict = replay_verdict(args.replay)
        result_valid = recorded_verdict is not None

        def replay_source_factory(path):
            return iter_replay_envelopes(path, result_valid=result_valid)

    def produce() -> None:
        if args.demo:
            source = _demo_source()
            while not stop_event.is_set():
                _put_latest(frame_queue, source())
                stop_event.wait(0.1)
            return

        try:
            for envelope in iter_replay_cycles(
                args.replay,
                loop=args.loop,
                stop_event=stop_event,
                source_factory=replay_source_factory,
            ):
                if stop_event.is_set():
                    break
                _put_latest(frame_queue, envelope)
                # Yield to the renderer without manufacturing simulation time.
                time.sleep(0.01)
        finally:
            stop_event.set()

    producer = threading.Thread(target=produce, daemon=True)
    producer.start()
    try:
        return WireframeViewer(
            frame_queue,
            stop_event,
            viewer_config_for_registered_p0(),
            demo=args.demo,
            stream_kind="replay" if args.replay is not None else "live",
            recorded_verdict=recorded_verdict,
        ).run()
    finally:
        stop_event.set()
        producer.join(timeout=0.5)


if __name__ == "__main__":
    raise SystemExit(main())
