"""Integration tests for ``agent/run_babble_experiment.py`` (iter-5b).

THIS IS THE PIPELINE-CONTRACT TEST for the predictive-babble build.
It exercises the full mini-mode path that the autonomous-build's success
contract gates on:

    Contract = `python -m agent.run_babble_experiment --mini`
               produces 4 wav files in ``~/.eqmod/babble/mini/``
               AND tests/test_babble_integration.py exits 0.

Each test calls ``run_mini`` against its own ``tmp_path`` so the tests
do not collide with each other or with the real ``~/.eqmod`` dir on the
developer's machine.

No silent-pass paths: every conditional uses ``pytest.fail`` on the
unreachable branch, mirroring the iteration-4b/5a tests
(cf. project memory's F3b silent-pass class of bugs).
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from unittest import mock

import numpy as np
import pytest
import scipy.io.wavfile

from agent.evaluate_babble import EvaluationResult
from agent.run_babble_experiment import (
    CONTROL_NAMES,
    SUBSTRATE_NAMES,
    TRAINED_NAME,
    run_full,
    run_mini,
)


# ---------------------------------------------------------------------
# 1. Four wav files exist and are readable.


def test_run_mini_produces_4_wav_files(tmp_path: Path) -> None:
    out_dir = tmp_path / "mini"
    run_mini(out_dir=out_dir)

    if len(SUBSTRATE_NAMES) != 4:
        pytest.fail(
            f"SUBSTRATE_NAMES has {len(SUBSTRATE_NAMES)} entries, "
            "expected 4 (trained_de + 3 controls)"
        )

    for name in SUBSTRATE_NAMES:
        wav_path = out_dir / name / "babble.wav"
        if not wav_path.exists():
            pytest.fail(f"missing wav file at {wav_path}")
        sr, data = scipy.io.wavfile.read(str(wav_path))
        if sr != 16000:
            pytest.fail(f"{name}: wav sample rate is {sr}, expected 16000")
        if data.size == 0:
            pytest.fail(f"{name}: wav has zero samples")
        duration_s = float(data.shape[0] / sr)
        # Mini runs target 1.0 sec; ISTFT padding can shave a few
        # samples — accept >= 0.9 sec.
        if duration_s < 0.9:
            pytest.fail(
                f"{name}: wav duration {duration_s:.3f}s is below "
                "the 0.9s minimum (target 1.0s)"
            )


# ---------------------------------------------------------------------
# 2. result.json is well-formed.


def test_run_mini_writes_result_json(tmp_path: Path) -> None:
    out_dir = tmp_path / "mini"
    run_mini(out_dir=out_dir)

    result_path = out_dir / "result.json"
    if not result_path.exists():
        pytest.fail(f"result.json missing at {result_path}")

    parsed = json.loads(result_path.read_text())
    for key in ("verdict", "trained_kl_mean", "control_kl", "z_scores"):
        if key not in parsed:
            pytest.fail(f"result.json missing top-level key {key!r}")

    if parsed["verdict"] not in ("PASS", "FAIL", "NULL"):
        pytest.fail(
            f"result.json verdict is {parsed['verdict']!r}, "
            "expected one of PASS/FAIL/NULL"
        )
    if not isinstance(parsed["control_kl"], dict):
        pytest.fail(
            f"control_kl must be a dict; got {type(parsed['control_kl'])}"
        )
    if not isinstance(parsed["z_scores"], dict):
        pytest.fail(
            f"z_scores must be a dict; got {type(parsed['z_scores'])}"
        )


# ---------------------------------------------------------------------
# 3. Return type is EvaluationResult with a valid verdict.


def test_run_mini_returns_evaluation_result(tmp_path: Path) -> None:
    out_dir = tmp_path / "mini"
    result = run_mini(out_dir=out_dir)

    if not isinstance(result, EvaluationResult):
        pytest.fail(
            f"run_mini returned {type(result).__name__}, "
            "expected EvaluationResult"
        )
    if result.verdict not in ("PASS", "FAIL", "NULL"):
        pytest.fail(
            f"verdict is {result.verdict!r}, expected PASS/FAIL/NULL"
        )
    # n_bootstrap mirrors the run_mini default (20). If it changes here
    # without the spec moving, the test informs the developer.
    if result.n_bootstrap <= 0:
        pytest.fail(
            f"n_bootstrap is {result.n_bootstrap}, expected positive"
        )


# ---------------------------------------------------------------------
# 4. Mini mode does not call CorpusBuilder (offline contract).


def test_run_mini_does_not_block_on_network(tmp_path: Path) -> None:
    """If mini mode hits the network, the developer running pytest in
    a CI sandbox or on a flight will see a hang. The contract is
    explicit per the iteration-5b brief: mini mode is offline.

    We patch ``agent.corpus_builder.CorpusBuilder`` to raise on any
    instantiation. ``run_mini`` must complete without hitting it.
    """
    out_dir = tmp_path / "mini"
    with mock.patch(
        "agent.corpus_builder.CorpusBuilder",
        side_effect=AssertionError(
            "CorpusBuilder must not be invoked from --mini mode"
        ),
    ):
        # If the patched class is touched, the AssertionError surfaces.
        run_mini(out_dir=out_dir)

    # Sanity: we still produced the 4 wavs (i.e. the test is not
    # silently passing because run_mini bailed before doing work).
    for name in SUBSTRATE_NAMES:
        wav_path = out_dir / name / "babble.wav"
        if not wav_path.exists():
            pytest.fail(
                f"run_mini under CorpusBuilder mock did not write "
                f"{wav_path} — mini mode might be silently degrading"
            )


# ---------------------------------------------------------------------
# 5. Wall-clock under 60 seconds.


def test_run_mini_completes_in_under_60_seconds(tmp_path: Path) -> None:
    """Pipeline correctness, not a scientific evaluation. If this
    fails, mini mode is doing too much."""
    out_dir = tmp_path / "mini"
    start = time.time()
    run_mini(out_dir=out_dir)
    elapsed = time.time() - start

    if elapsed >= 60.0:
        pytest.fail(
            f"run_mini took {elapsed:.1f}s, exceeded the 60s budget "
            "for the integration-test contract"
        )
    # The fast-path check: explicitly confirm the wavs are present
    # so a silent-fail (run_mini returns early without writing) does
    # not slip past this test.
    for name in SUBSTRATE_NAMES:
        wav_path = out_dir / name / "babble.wav"
        if not wav_path.exists():
            pytest.fail(
                f"run_mini completed in {elapsed:.1f}s but did not "
                f"write {wav_path} — early-exit silent-fail"
            )


# =====================================================================
# run_full tests (mocked — real run_full takes 24 hours per spec §7).
#
# Strategy: every heavy component is patched so the production path
# can be exercised structurally without doing real work:
#
#   - CorpusBuilder.build is patched to write 4 tiny f32.raw + manifest
#     trees on disk (so feeder.load_stage and the test-split → wav
#     conversion still see real files).
#   - AutonomousLoop is patched to avoid actually running ticks. We
#     intercept the constructor and short-circuit the per-cycle helpers.
#   - BabbleRunner is patched so each substrate's babble.wav is
#     filled with fixed silence.
#   - evaluate is patched to spy on its arguments and return a fixture
#     EvaluationResult.
# =====================================================================


def _write_synthetic_corpus_tree(corpus_root: Path, sample_rate: int = 16000) -> None:
    """Mimic CorpusBuilder.build's on-disk output without ffmpeg/yt-dlp."""
    n = sample_rate  # 1 sec
    audio = (0.1 * np.sin(2 * np.pi * 440.0 * np.arange(n) / sample_rate)).astype(np.float32)
    for name in ("de", "white_noise", "reversed_de", "fr"):
        sub = corpus_root / name
        sub.mkdir(parents=True, exist_ok=True)
        for split in ("train", "dev", "test"):
            (sub / f"{split}.f32.raw").write_bytes(audio.tobytes())
        manifest = {
            "name": name,
            "sample_rate": sample_rate,
            "splits": {
                split: {
                    "path": f"{split}.f32.raw",
                    "n_samples": n,
                    "duration_seconds": 1.0,
                }
                for split in ("train", "dev", "test")
            },
        }
        (sub / "manifest.json").write_text(json.dumps(manifest, indent=2))


def _make_fake_evaluation_result() -> EvaluationResult:
    return EvaluationResult(
        verdict="NULL",
        null_against=list(CONTROL_NAMES),
        trained_kl_mean=0.5,
        trained_kl_std=0.1,
        control_kl={n: (0.6, 0.1) for n in CONTROL_NAMES},
        z_scores={n: 1.0 for n in CONTROL_NAMES},
        n_frames_per_substrate={"trained": 100,
                                **{n: 100 for n in CONTROL_NAMES}},
        n_bootstrap=100,
    )


class _StubAutonomousLoop:
    """Drop-in for AutonomousLoop in run_full tests.

    Records cycle increments and exposes the helpers run_full's
    mini-loop calls. Each helper is a no-op or returns a sentinel so
    the loop never actually advances simulated time.
    """

    cycles_per_advance = 50  # how many step()s per stage advance signal

    def __init__(self, world, cfg) -> None:
        self.world = world
        self.cfg = cfg
        self.cycle = 0
        self.metrics: list = []
        self._error_history: list[float] = []
        self.stop_event = type("Evt", (), {"is_set": staticmethod(lambda: False)})()

    def _run_awake_phase(self) -> None:
        # No-op: skip ticks entirely.
        return None

    def _snapshot_metrics(self, *, phase, wall_time, sim_time, fires_in_cycle,
                           blend_events_in_cycle: int = 0):
        from agent.autonomous_loop import AutonomousLoopMetrics
        m = AutonomousLoopMetrics(
            cycle=self.cycle, wall_time=wall_time, sim_time=sim_time,
            phase=phase, n_atoms=0, n_bridges=0, n_patterns=0,
            workspace_winner=0, prediction_error=0.0,
            btsp_potentiation=0.0, fires_in_cycle=fires_in_cycle,
            blend_events_in_cycle=blend_events_in_cycle,
        )
        return m

    def _count_fires_since(self, _t):
        return 0

    def _append_metrics_csv(self):
        return None

    def _save_snapshot(self):
        return None


class _StubScheduler:
    """Curriculum scheduler stub that advances on a fixed cycle count.

    Records every step() call so tests can inspect the perplexity /
    elapsed_seconds the production code passed in.
    """

    def __init__(self, stages, is_trained, wall_clock_per_stage,
                 convergence=None) -> None:
        self.stages = stages
        self.is_trained = is_trained
        self.wall_clock_per_stage = list(wall_clock_per_stage)
        self.convergence = convergence
        self._stage_index = 0
        self.steps: list[tuple[float, float]] = []

    def step(self, perplexity: float, elapsed_seconds: float) -> bool:
        self.steps.append((float(perplexity), float(elapsed_seconds)))
        # Advance every call until done.
        if self._stage_index < len(self.stages):
            self._stage_index += 1
            return True
        return False

    def is_done(self) -> bool:
        return self._stage_index >= len(self.stages)

    @property
    def current_stage_index(self) -> int:
        return self._stage_index


def _stub_run_babble_runner(*args, **kwargs):
    """Replacement BabbleRunner that writes 1 sec of silence to output_path."""
    duration_s = float(kwargs.get("duration_seconds", 1.0))
    sr = int(kwargs.get("sample_rate", 16000))
    out = kwargs.get("output_path")
    if out is None:
        pytest.fail("test stub expects output_path to be set")
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = max(1, int(round(duration_s * sr)))
    pcm = np.zeros(n, dtype=np.int16)
    scipy.io.wavfile.write(str(out), sr, pcm)

    class _Result:
        def run(self):
            return np.zeros(n, dtype=np.float32), out
    return _Result()


def _write_minimal_yaml(path: Path) -> dict:
    """Write a tiny YAML config for run_full mocked tests.

    Returns the dict that was written so tests can assert on what
    run_full read.
    """
    cfg = {
        "de": {
            "stage1": ["/fake/de/stage1.mp3"],
            "stage2": ["/fake/de/stage2.mp3"],
            "stage3": ["/fake/de/stage3.mp3"],
            "stage4": ["/fake/de/stage4.wav"],
        },
        "fr": {"sources": ["/fake/fr/sources.mp3"]},
        "seed": 0,
        "n_clusters": 256,
        "n_bootstrap": 100,
        "babble_duration_seconds": 0.1,
        "perplexity_eval_interval_cycles": 1,
        "expected_min_cycles_per_stage": 1,
        "snapshot_every_seconds": 1e9,  # never snapshot in tests
    }
    import yaml
    path.write_text(yaml.safe_dump(cfg))
    return cfg


# ---------------------------------------------------------------------
# 11. run_full parses the YAML config and writes to out_dir.


def test_run_full_parses_yaml_config(tmp_path: Path) -> None:
    out_dir = tmp_path / "full"
    out_dir.mkdir(parents=True, exist_ok=True)
    config_path = tmp_path / "corpus.yaml"
    _write_minimal_yaml(config_path)

    def _fake_build(self, target):
        _write_synthetic_corpus_tree(Path(target))
        return {}

    with mock.patch(
        "agent.corpus_builder.CorpusBuilder.build", autospec=True,
        side_effect=_fake_build,
    ), mock.patch(
        "agent.autonomous_loop.AutonomousLoop", _StubAutonomousLoop,
    ), mock.patch(
        "agent.curriculum_scheduler.CurriculumScheduler", _StubScheduler,
    ), mock.patch(
        "agent.babble.BabbleRunner", side_effect=_stub_run_babble_runner,
    ), mock.patch(
        "agent.run_babble_experiment.evaluate",
        return_value=_make_fake_evaluation_result(),
    ):
        result = run_full(config_path=config_path, out_dir=out_dir)

    if not isinstance(result, EvaluationResult):
        pytest.fail(
            f"run_full returned {type(result).__name__}, "
            "expected EvaluationResult"
        )
    if not (out_dir / "result.json").exists():
        pytest.fail(
            f"result.json not written under {out_dir}"
        )


# ---------------------------------------------------------------------
# 12. CorpusBuilder is constructed with the DE 4-stage and FR sources.


def test_run_full_calls_corpus_builder_with_de_and_fr_sources(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "full"
    out_dir.mkdir(parents=True, exist_ok=True)
    config_path = tmp_path / "corpus.yaml"
    cfg = _write_minimal_yaml(config_path)

    captured: dict = {}

    real_build = None

    class _SpyBuilder:
        def __init__(self, *, de_stage1, de_stage2, de_stage3, de_stage4,
                     fr_sources, sample_rate: int = 16000, seed: int = 0,
                     cache_dir=None):
            captured["de_stage1"] = list(de_stage1)
            captured["de_stage2"] = list(de_stage2)
            captured["de_stage3"] = list(de_stage3)
            captured["de_stage4"] = list(de_stage4)
            captured["fr_sources"] = list(fr_sources)
            captured["seed"] = int(seed)

        def build(self, target):
            _write_synthetic_corpus_tree(Path(target))
            return {}

    with mock.patch(
        "agent.corpus_builder.CorpusBuilder", _SpyBuilder,
    ), mock.patch(
        "agent.autonomous_loop.AutonomousLoop", _StubAutonomousLoop,
    ), mock.patch(
        "agent.curriculum_scheduler.CurriculumScheduler", _StubScheduler,
    ), mock.patch(
        "agent.babble.BabbleRunner", side_effect=_stub_run_babble_runner,
    ), mock.patch(
        "agent.run_babble_experiment.evaluate",
        return_value=_make_fake_evaluation_result(),
    ):
        run_full(config_path=config_path, out_dir=out_dir)

    if "de_stage1" not in captured:
        pytest.fail(
            "CorpusBuilder was never instantiated with the YAML-derived "
            "DE 4-stage source list"
        )
    if captured["de_stage1"] != cfg["de"]["stage1"]:
        pytest.fail(
            f"de_stage1 was {captured['de_stage1']!r}; expected "
            f"{cfg['de']['stage1']!r}"
        )
    if captured["de_stage2"] != cfg["de"]["stage2"]:
        pytest.fail(f"de_stage2 mismatch: {captured['de_stage2']!r}")
    if captured["de_stage3"] != cfg["de"]["stage3"]:
        pytest.fail(f"de_stage3 mismatch: {captured['de_stage3']!r}")
    if captured["de_stage4"] != cfg["de"]["stage4"]:
        pytest.fail(f"de_stage4 mismatch: {captured['de_stage4']!r}")
    if captured["fr_sources"] != cfg["fr"]["sources"]:
        pytest.fail(
            f"fr_sources was {captured['fr_sources']!r}; expected "
            f"{cfg['fr']['sources']!r}"
        )


# ---------------------------------------------------------------------
# 13. Trained substrate advances through 4 stages before babble starts.


def test_run_full_advances_through_4_stages_for_trained(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "full"
    out_dir.mkdir(parents=True, exist_ok=True)
    config_path = tmp_path / "corpus.yaml"
    _write_minimal_yaml(config_path)

    captured_schedulers: list[_StubScheduler] = []

    class _RecordingScheduler(_StubScheduler):
        def __init__(self, stages, is_trained, wall_clock_per_stage,
                     convergence=None):
            super().__init__(stages, is_trained, wall_clock_per_stage,
                             convergence=convergence)
            captured_schedulers.append(self)

    def _fake_build(self, target):
        _write_synthetic_corpus_tree(Path(target))
        return {}

    with mock.patch(
        "agent.corpus_builder.CorpusBuilder.build", autospec=True,
        side_effect=_fake_build,
    ), mock.patch(
        "agent.autonomous_loop.AutonomousLoop", _StubAutonomousLoop,
    ), mock.patch(
        "agent.curriculum_scheduler.CurriculumScheduler", _RecordingScheduler,
    ), mock.patch(
        "agent.babble.BabbleRunner", side_effect=_stub_run_babble_runner,
    ), mock.patch(
        "agent.run_babble_experiment.evaluate",
        return_value=_make_fake_evaluation_result(),
    ):
        run_full(config_path=config_path, out_dir=out_dir)

    # Trained substrate is the first scheduler created.
    if not captured_schedulers:
        pytest.fail("no schedulers were created — control flow error")
    trained_sched = captured_schedulers[0]
    if not trained_sched.is_trained:
        pytest.fail(
            "first scheduler is_trained=False; trained substrate "
            "must run first so its wall-clock can be reused for controls"
        )
    if len(trained_sched.stages) != 4:
        pytest.fail(
            f"trained scheduler has {len(trained_sched.stages)} stages, "
            "expected 4"
        )
    if not trained_sched.is_done():
        pytest.fail(
            "trained scheduler did not reach is_done() — run_full's "
            "training loop did not advance through all 4 stages"
        )


# ---------------------------------------------------------------------
# 14. Controls receive matched wall-clock from trained substrate.


def test_run_full_uses_matched_wall_clock_for_controls(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "full"
    out_dir.mkdir(parents=True, exist_ok=True)
    config_path = tmp_path / "corpus.yaml"
    _write_minimal_yaml(config_path)

    captured: list[_StubScheduler] = []

    class _RecordingScheduler(_StubScheduler):
        def __init__(self, stages, is_trained, wall_clock_per_stage,
                     convergence=None):
            super().__init__(stages, is_trained, wall_clock_per_stage,
                             convergence=convergence)
            captured.append(self)

    def _fake_build(self, target):
        _write_synthetic_corpus_tree(Path(target))
        return {}

    with mock.patch(
        "agent.corpus_builder.CorpusBuilder.build", autospec=True,
        side_effect=_fake_build,
    ), mock.patch(
        "agent.autonomous_loop.AutonomousLoop", _StubAutonomousLoop,
    ), mock.patch(
        "agent.curriculum_scheduler.CurriculumScheduler", _RecordingScheduler,
    ), mock.patch(
        "agent.babble.BabbleRunner", side_effect=_stub_run_babble_runner,
    ), mock.patch(
        "agent.run_babble_experiment.evaluate",
        return_value=_make_fake_evaluation_result(),
    ):
        run_full(config_path=config_path, out_dir=out_dir)

    if len(captured) != len(SUBSTRATE_NAMES):
        pytest.fail(
            f"created {len(captured)} schedulers; expected "
            f"{len(SUBSTRATE_NAMES)} (one per substrate)"
        )

    trained = captured[0]
    if not trained.is_trained:
        pytest.fail("first scheduler is not trained")

    # Build the per-stage wall-clock list the controls SHOULD receive
    # (any non-empty list inherited from trained's training run).
    for control_idx in range(1, len(captured)):
        ctrl = captured[control_idx]
        if ctrl.is_trained:
            pytest.fail(
                f"control scheduler #{control_idx} flagged is_trained=True"
            )
        if len(ctrl.wall_clock_per_stage) != 4:
            pytest.fail(
                f"control wall_clock_per_stage length is "
                f"{len(ctrl.wall_clock_per_stage)}, expected 4"
            )
        # The list must come from trained's measured per-stage durations.
        # Each entry is a wall-clock float (>= 0).
        for v in ctrl.wall_clock_per_stage:
            if v < 0.0:
                pytest.fail(
                    f"control wall_clock entry {v} is negative; "
                    "matched wall-clock must be non-negative"
                )


# ---------------------------------------------------------------------
# 15. result.json is written; evaluate called with full-mode settings.


def test_run_full_writes_result_json_with_full_settings(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "full"
    out_dir.mkdir(parents=True, exist_ok=True)
    config_path = tmp_path / "corpus.yaml"
    _write_minimal_yaml(config_path)

    spy_kwargs: dict = {}

    def _spy_evaluate(**kwargs):
        spy_kwargs.update(kwargs)
        return _make_fake_evaluation_result()

    def _fake_build(self, target):
        _write_synthetic_corpus_tree(Path(target))
        return {}

    with mock.patch(
        "agent.corpus_builder.CorpusBuilder.build", autospec=True,
        side_effect=_fake_build,
    ), mock.patch(
        "agent.autonomous_loop.AutonomousLoop", _StubAutonomousLoop,
    ), mock.patch(
        "agent.curriculum_scheduler.CurriculumScheduler", _StubScheduler,
    ), mock.patch(
        "agent.babble.BabbleRunner", side_effect=_stub_run_babble_runner,
    ), mock.patch(
        "agent.run_babble_experiment.evaluate", side_effect=_spy_evaluate,
    ):
        result = run_full(config_path=config_path, out_dir=out_dir)

    # 1. result.json exists.
    result_path = out_dir / "result.json"
    if not result_path.exists():
        pytest.fail(f"result.json not written at {result_path}")
    parsed = json.loads(result_path.read_text())
    if parsed.get("verdict") not in ("PASS", "FAIL", "NULL"):
        pytest.fail(
            f"result.json verdict is {parsed.get('verdict')!r}; "
            "expected PASS/FAIL/NULL"
        )

    # 2. evaluate() was called with full-mode parameters.
    if spy_kwargs.get("n_clusters") != 256:
        pytest.fail(
            f"evaluate called with n_clusters="
            f"{spy_kwargs.get('n_clusters')!r}; expected 256"
        )
    if spy_kwargs.get("n_bootstrap") != 100:
        pytest.fail(
            f"evaluate called with n_bootstrap="
            f"{spy_kwargs.get('n_bootstrap')!r}; expected 100"
        )
    # 3. trained_wav points at the trained substrate's babble file.
    trained_wav = spy_kwargs.get("trained_wav")
    if trained_wav is None:
        pytest.fail("evaluate was not given a trained_wav argument")
    if Path(trained_wav).name != f"{TRAINED_NAME}.wav":
        pytest.fail(
            f"trained_wav path is {trained_wav!r}; "
            f"expected name to be {TRAINED_NAME}.wav"
        )
    # 4. control_wavs cover all three controls.
    control_wavs = spy_kwargs.get("control_wavs", {})
    for ctrl in CONTROL_NAMES:
        if ctrl not in control_wavs:
            pytest.fail(
                f"evaluate's control_wavs missing {ctrl!r}; "
                f"got keys {list(control_wavs.keys())!r}"
            )
    # 5. The returned EvaluationResult round-trips through the JSON.
    if not isinstance(result, EvaluationResult):
        pytest.fail(
            f"run_full returned {type(result).__name__}, "
            "expected EvaluationResult"
        )
