import numpy as np

from vibrasim2.observation import (
    EdgeKind,
    ObservationEnvelope,
    ObservationStatus,
    WireframeFrame,
)
from vibrasim2.viewer_process import (
    ViewerController,
    viewer_config_for_registered_p0,
)


def envelopes_at_ticks(*ticks: int, kind: EdgeKind = EdgeKind.MATTER) -> tuple[ObservationEnvelope, ...]:
    frame = WireframeFrame(
        positions=np.array(((0.0, 0.0, 0.0), (1.0, 0.0, 0.5))),
        edges=np.array(((0, 1),), dtype=np.int32),
        edge_states=("supplied",),
        edge_kinds=(kind,),
    )
    return tuple(
        ObservationEnvelope(
            schema_version=1, run_id="r1", stage="A", arm="cycle",
            source_centre=(4, 16), tick=tick, simulation_time=tick * 0.05,
            sequence=sequence, emitted_monotonic_ns=2_000_000_000,
            status=ObservationStatus.RUNNING, display_scale=4.0, frame=frame,
        )
        for sequence, tick in enumerate(ticks, start=1)
    )


def test_freeze_holds_display_while_pending_advances():
    controller = ViewerController()
    first, second, third = envelopes_at_ticks(10, 20, 30)
    controller.accept(first)
    assert controller.next_drawable() == first
    controller.set_frozen(True)
    controller.accept(second)
    controller.accept(third)
    assert controller.next_drawable() is None
    controller.set_frozen(False)
    assert controller.next_drawable() == third


def test_hud_is_neutral_and_reports_frame_age():
    controller = ViewerController()
    controller.accept(envelopes_at_ticks(10)[0])
    hud = controller.hud(now_ns=2_100_000_000)
    assert "RAW SIMULATION STATE" in hud
    assert "OBSERVATION ONLY" in hud
    assert "VERDICT PENDING" in hud
    assert "S=4" in hud
    assert "PASS" not in hud and "NULL" not in hud
    assert "age=0.100s" in hud


def test_complete_changes_only_the_neutral_footer():
    controller = ViewerController()
    running = envelopes_at_ticks(10)[0]
    controller.accept(running)
    running_hud = controller.hud(now_ns=2_000_000_000)
    complete = ObservationEnvelope(
        **{**running.__dict__, "status": ObservationStatus.COMPLETE}
    )
    controller.accept(complete)
    complete_hud = controller.hud(now_ns=2_000_000_000)
    assert running_hud.replace("VERDICT PENDING", "VERDICT RECORDED IN result.json") == complete_hud


def test_broken_pair_hud_labels_nonreciprocal_sensitivity_control():
    controller = ViewerController()
    controller.accept(envelopes_at_ticks(10, kind=EdgeKind.MATERIAL_ONLY_CONTROL)[0])
    hud = controller.hud(now_ns=2_000_000_000)
    assert "NON-RECIPROCAL SENSITIVITY CONTROL" in hud
    assert "HAMILTONIAN" not in hud
    assert "RECIPROCAL COUPLING" not in hud


def test_controller_exposes_no_simulation_callback():
    controller = ViewerController()
    for name in ("step", "play", "pause"):
        assert not hasattr(controller, name)
    assert not any(callable(value) for name, value in vars(controller).items() if name != "pending")


class DrainQueue:
    def __init__(self, items):
        self.items = list(items)
        self.calls = 0

    def get_nowait(self):
        from queue import Empty

        self.calls += 1
        if not self.items:
            raise Empty
        return self.items.pop(0)


def test_draw_cadence_never_limits_queue_polling():
    controller = ViewerController()
    queue = DrainQueue(list(envelopes_at_ticks(10, 20, 30)))
    assert controller.drain(queue) == 3
    assert queue.calls == 4
    assert controller.pending.tick == 30


def test_unfreeze_draws_only_the_newest_envelope():
    controller = ViewerController(frozen=True)
    for envelope in envelopes_at_ticks(10, 20, 30):
        controller.accept(envelope)
    controller.set_frozen(False)
    assert controller.next_drawable().tick == 30


def test_registered_viewer_config_is_fixed():
    config = viewer_config_for_registered_p0()
    assert config.grid_shape == (32, 32)
    assert config.display_scale == 4.0
    assert config.camera_position == (48.0, -48.0, 32.0)
    assert config.camera_focal_point == (15.5, 15.5, 0.0)
    assert config.draw_interval_seconds == 0.1
    assert config.shutdown_timeout_seconds == 2.0


def test_viewer_process_main_delegates_only_to_the_renderer(monkeypatch):
    calls = []

    class FakeViewer:
        def __init__(self, frame_queue, stop_event, config):
            calls.append((frame_queue, stop_event, config))

        def run(self):
            calls.append("run")

    monkeypatch.setattr("vibrasim2.wireframe.WireframeViewer", FakeViewer)
    from vibrasim2.viewer_process import viewer_process_main

    queue, stop_event, config = object(), object(), viewer_config_for_registered_p0()
    viewer_process_main(queue, stop_event, config)
    assert calls == [(queue, stop_event, config), "run"]


def test_renderer_has_no_simulation_step_binding():
    from pathlib import Path

    source = (Path(__file__).resolve().parents[1] / "vibrasim2" / "wireframe.py").read_text()
    assert 'add_key_event("s"' not in source
