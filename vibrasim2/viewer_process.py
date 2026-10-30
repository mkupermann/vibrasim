"""Process-isolated, observer-only viewer control and lifecycle helpers."""
from __future__ import annotations

import multiprocessing
import time
from dataclasses import dataclass, replace
from pathlib import Path
from queue import Empty
from typing import Any

from vibrasim2.observation import EdgeKind, ObservationEnvelope, ObservationStatus
from vibrasim2.observation_transport import LatestOnlyPublisher


@dataclass(frozen=True)
class ViewerProcessConfig:
    grid_shape: tuple[int, int] = (32, 32)
    display_scale: float = 4.0
    camera_position: tuple[float, float, float] = (48.0, -48.0, 32.0)
    camera_focal_point: tuple[float, float, float] = (15.5, 15.5, 0.0)
    draw_interval_seconds: float = 0.1
    shutdown_timeout_seconds: float = 2.0


def viewer_config_for_registered_p0() -> ViewerProcessConfig:
    return ViewerProcessConfig()


@dataclass
class ViewerController:
    frozen: bool = False
    displayed: ObservationEnvelope | None = None
    pending: ObservationEnvelope | None = None
    stream_kind: str = "live"
    recorded_verdict: str | None = None

    def __post_init__(self) -> None:
        if self.stream_kind not in {"live", "replay"}:
            raise ValueError("stream_kind must be live or replay")
        if self.recorded_verdict not in {None, "PASS", "NULL", "INCONCLUSIVE", "FAIL"}:
            raise ValueError("recorded_verdict is invalid")

    def accept(self, envelope: ObservationEnvelope) -> None:
        if not isinstance(envelope, ObservationEnvelope):
            raise TypeError("viewer accepts ObservationEnvelope only")
        self.pending = envelope

    def drain(self, frame_queue: Any) -> int:
        """Accept every available envelope, retaining only the newest one."""
        count = 0
        while True:
            try:
                envelope = frame_queue.get_nowait()
            except Empty:
                return count
            except (EOFError, OSError, ValueError):
                return count
            self.accept(envelope)
            count += 1

    def set_frozen(self, frozen: bool) -> None:
        self.frozen = bool(frozen)

    def next_drawable(self) -> ObservationEnvelope | None:
        if self.frozen or self.pending is None:
            return None
        self.displayed, self.pending = self.pending, None
        return self.displayed

    def hud(self, now_ns: int | None = None) -> str:
        envelope = self.pending or self.displayed
        if envelope is None:
            return "RAW SIMULATION STATE — OBSERVATION ONLY\nNO FRAME — S=4"
        if now_ns is None:
            now_ns = time.monotonic_ns()
        age_seconds = max(0.0, (now_ns - envelope.emitted_monotonic_ns) / 1_000_000_000)
        parts = envelope.run_id.lower().split("-")
        experiment = parts[1].upper() if len(parts) > 1 and parts[0] == "v2" else "UNSPECIFIED"
        lines = (
            f"VIBRASIM II · {experiment} · {self.stream_kind.upper()}",
            "RAW SIMULATION STATE — OBSERVATION ONLY",
            f"run={envelope.run_id} stage={envelope.stage} arm={envelope.arm}",
            f"source={envelope.source_centre} tick={envelope.tick} time={envelope.simulation_time:g}",
            f"age={age_seconds:.3f}s S=4",
        )
        if EdgeKind.MATERIAL_ONLY_CONTROL in envelope.frame.edge_kinds:
            lines += ("NON-RECIPROCAL SENSITIVITY CONTROL",)
        if self.recorded_verdict is not None and envelope.status is ObservationStatus.COMPLETE:
            footer = f"VERDICT: {self.recorded_verdict}"
        elif envelope.status is ObservationStatus.COMPLETE:
            footer = "VERDICT RECORDED IN result.json"
        else:
            footer = "VERDICT PENDING"
        return "\n".join((*lines, footer))


def viewer_process_main(frame_queue: Any, stop_event: Any, config: ViewerProcessConfig) -> None:
    from vibrasim2.wireframe import WireframeViewer

    WireframeViewer(frame_queue, stop_event, config).run()


@dataclass
class ViewerHandle:
    process: multiprocessing.Process | None
    queue: Any | None
    stop_event: Any | None
    publisher: LatestOnlyPublisher | None
    config: ViewerProcessConfig
    shutdown_started: bool = False


def append_view_event_best_effort(output_dir, event: dict[str, object]) -> None:
    """Append bounded non-scientific observer diagnostics, never raising."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "view-events.jsonl"
        import json

        lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
        lines.append(json.dumps(event, sort_keys=True, separators=(",", ":")))
        lines = lines[-256:]
        while sum(len(line.encode("utf-8")) + 1 for line in lines) > 64 * 1024 and lines:
            lines.pop(0)
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    except Exception:
        return None


def start_viewer(output_dir, config: ViewerProcessConfig) -> ViewerHandle:
    try:
        context = multiprocessing.get_context("spawn")
        frame_queue = context.Queue(maxsize=1)
        stop_event = context.Event()
        process = context.Process(target=viewer_process_main, args=(frame_queue, stop_event, config))
        process.start()
        return ViewerHandle(process, frame_queue, stop_event, LatestOnlyPublisher(frame_queue), config)
    except Exception as exc:
        append_view_event_best_effort(output_dir, {"event": "viewer_start_failed", "error": type(exc).__name__})
        return ViewerHandle(None, None, None, None, config)


def shutdown_viewer(handle: ViewerHandle) -> None:
    if handle.shutdown_started:
        return
    handle.shutdown_started = True
    process = handle.process
    queue = handle.queue
    try:
        if handle.stop_event is not None:
            try:
                handle.stop_event.set()
            except Exception:
                pass
        if process is not None:
            try:
                process.join(handle.config.shutdown_timeout_seconds)
            except Exception:
                pass
            try:
                alive = process.is_alive()
            except Exception:
                alive = False
            if alive:
                try:
                    process.terminate()
                except Exception:
                    pass
                try:
                    process.join(handle.config.shutdown_timeout_seconds)
                except Exception:
                    pass
    finally:
        if queue is not None:
            try:
                queue.cancel_join_thread()
            except Exception:
                pass
            try:
                queue.close()
            except Exception:
                pass


class P0ObservationSink:
    """Project persisted snapshots and publish only copied observer envelopes."""

    def __init__(self, handle: ViewerHandle, output_dir: Path, run_id: str) -> None:
        self.handle = handle
        self.output_dir = Path(output_dir)
        self.run_id = run_id
        self.last_envelope: ObservationEnvelope | None = None
        self._sequence = 0
        self._closed = False

    def after_snapshot_persisted(self, stage: str, cell: Any, snapshot: Any, cell_dir: Path) -> None:
        if self._closed:
            return
        try:
            from vibrasim2.p0.observation import (
                ObservationMetadata,
                ObservationProjectionConfig,
                ProjectionTopology,
                project_p0_observation,
            )
            from vibrasim2.p0.types import P0Config

            self._sequence += 1
            envelope = project_p0_observation(
                snapshot,
                ProjectionTopology.from_registered(P0Config.registered(), cell),
                ObservationMetadata(
                    run_id=self.run_id,
                    stage=stage,
                    arm=cell.arm_label,
                    source_centre=cell.source_centre,
                    sequence=self._sequence,
                    emitted_monotonic_ns=time.monotonic_ns(),
                    status=ObservationStatus.RUNNING,
                ),
                ObservationProjectionConfig(display_scale=4.0),
            )
            if self.handle.publisher is None:
                append_view_event_best_effort(self.output_dir, {"event": "viewer_disabled"})
                return
            outcome = self.handle.publisher.publish(envelope)
            if outcome.published:
                self.last_envelope = envelope
            else:
                append_view_event_best_effort(
                    self.output_dir,
                    {"event": "frame_dropped", "tick": envelope.tick},
                )
        except Exception as exc:
            append_view_event_best_effort(
                self.output_dir,
                {"event": "projection_failed", "error": type(exc).__name__},
            )

    def close(self, result_recorded: bool) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            if result_recorded and self.last_envelope is not None and self.handle.publisher is not None:
                complete = replace(
                    self.last_envelope,
                    sequence=self.last_envelope.sequence + 1,
                    emitted_monotonic_ns=time.monotonic_ns(),
                    status=ObservationStatus.COMPLETE,
                )
                outcome = self.handle.publisher.publish(complete)
                if not outcome.published:
                    append_view_event_best_effort(
                        self.output_dir, {"event": "complete_frame_dropped"}
                    )
        except Exception as exc:
            append_view_event_best_effort(
                self.output_dir,
                {"event": "complete_publish_failed", "error": type(exc).__name__},
            )
        finally:
            try:
                shutdown_viewer(self.handle)
            except Exception as exc:
                append_view_event_best_effort(
                    self.output_dir,
                    {"event": "viewer_shutdown_failed", "error": type(exc).__name__},
                )


def make_registered_observer_factory(output_dir: Path):
    config = viewer_config_for_registered_p0()

    def factory(run_id: str) -> P0ObservationSink:
        handle = start_viewer(Path(output_dir), config)
        return P0ObservationSink(handle, Path(output_dir), run_id)

    return factory


def _read_json(path: Path) -> dict[str, Any]:
    import json

    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _ordered_cell_dirs(root: Path) -> tuple[Path, list[Path], dict[str, Any]]:
    if (root / "snapshots" / "manifest.jsonl").is_file():
        return root.parent, [root], _read_json(root / "cell.json")
    manifest = _read_json(root / "run.json")
    order = manifest.get("cell_slugs", manifest.get("cell_order", manifest.get("cells")))
    if not isinstance(order, list) or not order or not all(isinstance(item, (str, dict)) for item in order):
        raise ValueError("run.json must contain an ordered cell list")
    names = [item if isinstance(item, str) else item.get("slug", item.get("path")) for item in order]
    if any(not isinstance(name, str) or not name for name in names) or len(set(names)) != len(names):
        raise ValueError("run.json cell order is invalid")
    actual = {
        child.name: child for child in root.iterdir()
        if child.is_dir() and (child / "cell.json").is_file()
    }
    if set(names) != set(actual):
        raise ValueError("run.json cell order does not match cell directories")
    return root, [actual[name] for name in names], manifest


def _fallback_snapshots(cell_dir: Path):
    import json
    from types import SimpleNamespace
    import numpy as np

    manifest = cell_dir / "snapshots" / "manifest.jsonl"
    with manifest.open(encoding="utf-8") as stream:
        entries = [json.loads(line) for line in stream if line.strip()]
    for entry in entries:
        with np.load(cell_dir / "snapshots" / entry["file"], allow_pickle=False) as data:
            state = SimpleNamespace(u=data["u"], p=data["p"], q=data["q"], r=data["r"])
        yield SimpleNamespace(
            tick=int(entry["tick"]),
            simulation_time=float(entry["simulation_time"]),
            state=state,
        )


def _iter_cell_snapshots(cell_dir: Path):
    try:
        from vibrasim2.p0.artifacts import iter_snapshots
    except (ImportError, AttributeError):
        yield from _fallback_snapshots(cell_dir)
    else:
        yield from iter_snapshots(cell_dir)


def _topology_from_cell(cell_data: dict[str, Any], run_data: dict[str, Any]):
    import numpy as np
    from vibrasim2.observation import EdgeKind
    from vibrasim2.p0.observation import ProjectionTopology

    config = cell_data.get("config", {})
    grid_shape = tuple(config.get("grid_shape", cell_data.get("grid_shape", run_data.get("grid_shape", (32, 32)))))
    sites = cell_data.get("coupling_sites", cell_data.get("sites"))
    edges = cell_data.get("supplied_edges", cell_data.get("matter_edges", []))
    mode = cell_data.get("mode", "full")
    mode = getattr(mode, "value", mode)
    if isinstance(mode, dict):
        mode = mode.get("value", "full")
    if mode == "no_bonds":
        edges = []
    if mode in {"full", "no_bonds"}:
        vertical = EdgeKind.RECIPROCAL_COUPLING
    elif mode == "decoupled":
        vertical = None
    elif mode == "broken_pair":
        vertical = EdgeKind.MATERIAL_ONLY_CONTROL
    else:
        raise ValueError(f"unknown replay mode: {mode}")
    return ProjectionTopology(tuple(grid_shape), np.asarray(sites, dtype=np.int64), np.asarray(edges, dtype=np.int64).reshape((-1, 2)), vertical)


def _result_is_valid(root: Path) -> bool:
    result_path = root / "result.json"
    if not result_path.is_file():
        return False
    try:
        result = _read_json(result_path)
        expected = result.get("scientific_digest")
        if not isinstance(expected, str) or not expected:
            return False
        from vibrasim2.p0.artifacts import scientific_digest

        return scientific_digest(root) == expected
    except Exception:
        return False


def replay_verdict(path: Path) -> str | None:
    """Return a verdict only from a scientifically valid replay root."""
    root, _, _ = _ordered_cell_dirs(Path(path))
    if not _result_is_valid(root):
        return None
    value = _read_json(root / "result.json").get("verdict")
    return value if value in {"PASS", "NULL", "INCONCLUSIVE", "FAIL"} else None


def iter_replay_envelopes(path: Path, *, result_valid: bool | None = None):
    """Yield observation envelopes from persisted snapshots, never simulating."""
    import time as _time
    root, cell_dirs, run_data = _ordered_cell_dirs(Path(path))
    run_id = str(run_data.get("run_id", "replay"))
    if run_data.get("observation_schema_version", 1) != 1:
        raise ValueError("replay requires observation schema version 1")
    display_scale = float(run_data.get("display_scale", 4.0))
    if display_scale != 4.0:
        raise ValueError("replay requires the registered display scale S=4")
    sequence = 0
    last_envelope = None
    complete = _result_is_valid(root) if result_valid is None else bool(result_valid)
    for cell_dir in cell_dirs:
        cell_data = run_data if cell_dir == Path(path) and (Path(path) / "cell.json").is_file() else _read_json(cell_dir / "cell.json")
        topology = _topology_from_cell(cell_data, run_data)
        source = tuple(cell_data.get("source_centre", run_data.get("source_centre", (0, 0))))
        stage = str(cell_data.get("stage", "A"))
        mode = str(cell_data.get("mode", "replay"))
        topology_name = str(cell_data.get("topology", ""))
        arm = str(cell_data.get("arm", cell_data.get("arm_label", "")))
        if not arm:
            arm = (
                topology_name if mode == "full" and topology_name
                else f"{topology_name}:broken_pair"
                if mode == "broken_pair" and topology_name
                else mode
            )
        for snapshot in _iter_cell_snapshots(cell_dir):
            sequence += 1
            from vibrasim2.p0.observation import ObservationMetadata, ObservationProjectionConfig, project_p0_observation

            envelope = project_p0_observation(
                snapshot,
                topology,
                ObservationMetadata(
                    run_id=run_id, stage=stage, arm=arm, source_centre=source,
                    sequence=sequence, emitted_monotonic_ns=_time.monotonic_ns(),
                    status=ObservationStatus.RUNNING,
                ),
                ObservationProjectionConfig(display_scale=4.0),
            )
            if last_envelope is not None:
                yield last_envelope
            last_envelope = envelope
    if last_envelope is not None:
        if complete:
            last_envelope = replace(
                last_envelope,
                status=ObservationStatus.COMPLETE,
                emitted_monotonic_ns=_time.monotonic_ns(),
            )
        yield last_envelope
