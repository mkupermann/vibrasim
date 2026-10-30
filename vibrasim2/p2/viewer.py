"""Process-isolated live viewer adapter for persisted P2 snapshots."""

from __future__ import annotations

import time
from dataclasses import replace
from pathlib import Path

from vibrasim2.observation import ObservationEnvelope, ObservationStatus
from vibrasim2.p0.observation import ObservationMetadata, ObservationProjectionConfig
from vibrasim2.viewer_process import (
    ViewerHandle,
    append_view_event_best_effort,
    shutdown_viewer,
    start_viewer,
    viewer_config_for_registered_p0,
)

from .observation import project_p2_observation
from .types import P2Config


class P2ObservationSink:
    def __init__(self, handle: ViewerHandle, output_dir: Path, run_id: str) -> None:
        self.handle = handle
        self.output_dir = Path(output_dir)
        self.run_id = run_id
        self.last_envelope: ObservationEnvelope | None = None
        self.sequence = 0
        self.closed = False

    def after_snapshot_persisted(self, stage, cell, snapshot, cell_dir) -> None:
        if self.closed:
            return
        try:
            self.sequence += 1
            envelope = project_p2_observation(
                snapshot,
                cell,
                P2Config.registered(),
                ObservationMetadata(
                    self.run_id,
                    stage,
                    cell.arm.value,
                    cell.source_centre,
                    self.sequence,
                    time.monotonic_ns(),
                    ObservationStatus.RUNNING,
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
                    {"event": "frame_dropped", "cell": cell.slug, "tick": snapshot.tick},
                )
        except Exception as exc:
            append_view_event_best_effort(
                self.output_dir,
                {"event": "projection_failed", "error": type(exc).__name__},
            )

    def close(self, result_recorded: bool) -> None:
        if self.closed:
            return
        self.closed = True
        if result_recorded and self.last_envelope is not None and self.handle.publisher is not None:
            try:
                self.handle.publisher.publish(
                    replace(
                        self.last_envelope,
                        sequence=self.last_envelope.sequence + 1,
                        emitted_monotonic_ns=time.monotonic_ns(),
                        status=ObservationStatus.COMPLETE,
                    )
                )
                # Keep the last real frame visible. The owning CLI process stays
                # alive until the user closes the window or a later run replaces it.
                return
            except Exception:
                pass
        shutdown_viewer(self.handle)


def make_p2_observer_factory(output_dir: Path):
    def factory(run_id: str) -> P2ObservationSink:
        handle = start_viewer(Path(output_dir), viewer_config_for_registered_p0())
        return P2ObservationSink(handle, Path(output_dir), run_id)

    return factory
