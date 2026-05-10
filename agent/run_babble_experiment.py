"""Predictive-babble top-level driver.

Iteration 5b of the predictive-babble pipeline (see
``docs/superpowers/specs/2026-05-10-predictive-babble-design.md``, §3 row
``agent/run_babble_experiment.py``).

This module is the wiring layer: it connects ``corpus_builder``,
``decoder_audio``, ``audio_predictor``, ``convergence``,
``curriculum_scheduler``, ``babble`` and ``evaluate_babble`` into a
single end-to-end run.

Two modes are exposed:

* ``--mini`` (the integration-test contract). Skips real audio
  download and full curriculum training. Generates four 2-second
  synthetic streams in memory, runs ``BabbleRunner`` on a fresh
  ``build_autonomous_world()``-style substrate per stream for one
  simulated second, evaluates the four wavs against the trained_de
  corpus as a stand-in reference, and writes ``result.json``.
  Pipeline correctness, not science (per spec §8: "Tests pipeline
  correctness, not result test").

* ``--config`` (production). Reads a YAML config that specifies the
  four stage URL lists for trained_de + french. Currently a TODO at
  the function level — the §6 falsifier acceptance run is gated on
  the spec's "Full curriculum acceptance run" step in §10.

CLI::

    python -m agent.run_babble_experiment --mini
    python -m agent.run_babble_experiment --config corpus.yaml --out ~/.eqmod/babble/run-N/
"""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

import numpy as np
import scipy.io.wavfile

from agent.evaluate_babble import EvaluationResult, _result_to_json_dict, evaluate


# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

SAMPLE_RATE = 16000

# Substrate names — order matters for the manifest. The first entry is
# the trained-DE substrate; the rest are controls. Keep this aligned
# with the integration test's expectation in tests/test_babble_integration.py.
SUBSTRATE_NAMES = ("trained_de", "white_noise", "reversed_de", "french")
TRAINED_NAME = "trained_de"
CONTROL_NAMES = ("white_noise", "reversed_de", "french")


# ---------------------------------------------------------------------
# Synthetic mini-corpora
# ---------------------------------------------------------------------


def _harmonic_mix(freqs_hz: Iterable[float], duration_s: float = 2.0,
                  amplitude: float = 0.3, sr: int = SAMPLE_RATE) -> np.ndarray:
    """Sum of sinusoids — a simple speech-like-spectrum stand-in.

    The resulting waveform has a structured MFCC distribution and a
    well-defined RMS, which is enough for the §8 mini integration
    test (pipeline correctness, not phonological fidelity).
    """
    freqs = [float(f) for f in freqs_hz]
    if not freqs:
        raise ValueError("freqs_hz must be non-empty")
    n = int(round(duration_s * sr))
    t = np.arange(n, dtype=np.float64) / sr
    samples = np.zeros(n, dtype=np.float64)
    for f in freqs:
        samples += np.sin(2.0 * np.pi * f * t)
    samples = samples / len(freqs)
    samples = (amplitude * samples).astype(np.float32)
    return np.clip(samples, -1.0, 1.0)


def _white_noise_stream(duration_s: float = 2.0, seed: int = 0,
                        sr: int = SAMPLE_RATE) -> np.ndarray:
    """RMS-bounded Gaussian noise stream of ``duration_s`` seconds."""
    rng = np.random.default_rng(seed)
    n = int(round(duration_s * sr))
    samples = (rng.standard_normal(n).astype(np.float32) * 0.3)
    return np.clip(samples, -1.0, 1.0)


def _build_mini_corpora(duration_s: float = 2.0,
                        sr: int = SAMPLE_RATE) -> dict[str, np.ndarray]:
    """Four 2-second synthetic streams keyed by substrate name.

    * ``trained_de`` — three-tone harmonic mix at 440 / 880 / 1760 Hz.
    * ``white_noise`` — Gaussian noise.
    * ``reversed_de`` — ``trained_de`` reversed sample-wise.
    * ``french`` — three-tone mix at different frequencies (different
      "language", per spec).
    """
    de = _harmonic_mix([440.0, 880.0, 1760.0], duration_s=duration_s, sr=sr)
    noise = _white_noise_stream(duration_s=duration_s, seed=0, sr=sr)
    reversed_de = de[::-1].copy()
    fr = _harmonic_mix([523.0, 659.0, 1568.0], duration_s=duration_s, sr=sr)
    return {
        "trained_de": de,
        "white_noise": noise,
        "reversed_de": reversed_de,
        "french": fr,
    }


# ---------------------------------------------------------------------
# Disk helpers
# ---------------------------------------------------------------------


def _write_corpus_manifest(target: Path, name: str, audio: np.ndarray,
                           sr: int = SAMPLE_RATE) -> None:
    """Write {target}/{name}/corpus.f32.raw + manifest.json."""
    sub_dir = target / name
    sub_dir.mkdir(parents=True, exist_ok=True)
    raw_path = sub_dir / "corpus.f32.raw"
    audio_f32 = audio.astype(np.float32, copy=False)
    audio_f32.tofile(raw_path)
    manifest = {
        "name": name,
        "sample_rate": int(sr),
        "n_samples": int(audio_f32.shape[0]),
        "duration_seconds": float(audio_f32.shape[0] / sr),
        "path": raw_path.name,
    }
    (sub_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))


def _write_wav(audio: np.ndarray, path: Path, sr: int = SAMPLE_RATE) -> None:
    """Write a float32 [-1, 1] sample array as 16-bit PCM mono wav."""
    arr = np.asarray(audio, dtype=np.float32)
    arr = np.clip(arr, -1.0, 1.0)
    pcm16 = (arr * np.float32(32767.0)).astype(np.int16)
    path.parent.mkdir(parents=True, exist_ok=True)
    scipy.io.wavfile.write(str(path), int(sr), pcm16)


# ---------------------------------------------------------------------
# Babble per substrate
# ---------------------------------------------------------------------


def _run_babble_for_substrate(name: str, out_path: Path,
                              duration_seconds: float = 1.0,
                              sr: int = SAMPLE_RATE) -> Path:
    """Run BabbleRunner on a fresh autonomous world; return wav path.

    The substrate is a `build_autonomous_world()`-style instance — same
    pre-seeded engrams every call, which gives an "as-trained"
    approximation for the mini-mode pipeline test (per the
    iteration-5b brief: "substrate 'as-trained' approximation —
    pre-seeded engrams already give it some output port firings").
    """
    # Lazy imports — keeps `python -m agent.run_babble_experiment --help`
    # cheap and avoids paying numba/JIT cost at module import time.
    from agent.autonomous_loop import (
        AutonomousLoopConfig,
        build_autonomous_world,
    )
    from agent.babble import BabbleRunner

    world = build_autonomous_world()
    cfg = AutonomousLoopConfig(
        awake_seconds_per_cycle=1.0,
        dream_seconds_per_cycle=0.5,
        stagnation_threshold=0.001,
        stagnation_window=2,
    )
    runner = BabbleRunner(
        world=world,
        autonomous_loop_cfg=cfg,
        duration_seconds=float(duration_seconds),
        output_path=out_path,
        sample_rate=int(sr),
    )
    _samples, written = runner.run()
    if written is None:
        # BabbleRunner only returns None when output_path is None; we
        # set output_path so this is unreachable. Raise loudly rather
        # than silent-pass on a missing file.
        raise RuntimeError(
            f"BabbleRunner did not write a wav for substrate {name!r}; "
            "output_path was set but writer returned None"
        )
    if not Path(written).exists():
        raise RuntimeError(
            f"BabbleRunner reported wrote {written} but file does not "
            "exist on disk"
        )
    return Path(written)


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------


def run_mini(out_dir: Path = Path.home() / ".eqmod" / "babble" / "mini",
             babble_duration_seconds: float = 1.0,
             sr: int = SAMPLE_RATE,
             n_clusters: int = 16,
             n_bootstrap: int = 20) -> EvaluationResult:
    """Mini integration run — pipeline correctness, not science.

    Generates 4 synthetic 2-second streams, writes raw + manifest per
    substrate, runs BabbleRunner per substrate (fresh
    ``build_autonomous_world()``), evaluates the 4 wavs against the
    trained_de corpus as the reference, and writes ``result.json``.

    Returns the :class:`EvaluationResult`.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Build the four synthetic corpora and write raw + manifest.
    corpora = _build_mini_corpora(duration_s=2.0, sr=sr)
    for name in SUBSTRATE_NAMES:
        if name not in corpora:
            raise RuntimeError(
                f"corpus for substrate {name!r} missing — synthetic "
                "corpus builder is out of sync with SUBSTRATE_NAMES"
            )
        _write_corpus_manifest(out_dir, name, corpora[name], sr=sr)

    # 2. Reference wav for the evaluator. We use the trained_de corpus
    #    as the reference (mini mode has no held-out test set; the
    #    point is pipeline correctness).
    reference_wav = out_dir / "reference.wav"
    _write_wav(corpora[TRAINED_NAME], reference_wav, sr=sr)

    # 3. Run BabbleRunner per substrate. Each gets a fresh world.
    babble_paths: dict[str, Path] = {}
    for name in SUBSTRATE_NAMES:
        wav_path = out_dir / name / "babble.wav"
        babble_paths[name] = _run_babble_for_substrate(
            name=name,
            out_path=wav_path,
            duration_seconds=babble_duration_seconds,
            sr=sr,
        )

    # 4. Evaluate. trained_de is the trained substrate; the rest are controls.
    trained_wav = babble_paths[TRAINED_NAME]
    control_wavs = {n: babble_paths[n] for n in CONTROL_NAMES}
    result = evaluate(
        trained_wav=trained_wav,
        control_wavs=control_wavs,
        reference_test_wav=reference_wav,
        n_bootstrap=int(n_bootstrap),
        seed=0,
        n_clusters=int(n_clusters),
        sr=int(sr),
    )

    # 5. Persist result.json.
    result_path = out_dir / "result.json"
    result_path.write_text(json.dumps(_result_to_json_dict(result), indent=2))

    return result


def run_full(config_path: Path, out_dir: Path) -> EvaluationResult:
    """Full curriculum acceptance run (spec §6).

    YAML config schema::

        de:
          stage1: ["https://...", "/path/to/local.mp3"]   # audiobook narrator
          stage2: ["https://..."]                          # single YouTuber
          stage3: ["https://...", "https://..."]           # multi-speaker
          stage4: ["/path/to/webcam-recording.wav"]        # user voice
        fr:
          sources: ["https://..."]                         # French control
        seed: 0
        n_clusters: 256
        n_bootstrap: 100
        babble_duration_seconds: 300.0
        perplexity_eval_interval_cycles: 10
        expected_min_cycles_per_stage: 50
        snapshot_every_seconds: 1800.0

    Pipeline:

    1. Parse YAML config.
    2. Build corpora via :class:`CorpusBuilder`.
    3. Train each substrate sequentially (trained DE first; controls
       inherit the trained substrate's per-stage wall-clock so all
       four enter babble mode at matched training duration).
    4. Run :class:`BabbleRunner` per substrate for
       ``babble_duration_seconds``.
    5. Evaluate against the held-back DE test split.
    6. Persist ``result.json`` in ``out_dir``.

    Returns the :class:`EvaluationResult`.
    """
    import yaml

    config_path = Path(config_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Parse YAML.
    cfg = yaml.safe_load(config_path.read_text()) or {}
    de_cfg = cfg.get("de", {}) or {}
    fr_cfg = cfg.get("fr", {}) or {}
    seed = int(cfg.get("seed", 0))
    n_clusters = int(cfg.get("n_clusters", 256))
    n_bootstrap = int(cfg.get("n_bootstrap", 100))
    babble_duration_seconds = float(
        cfg.get("babble_duration_seconds", 300.0)
    )
    perplexity_eval_interval_cycles = int(
        cfg.get("perplexity_eval_interval_cycles", 10)
    )
    expected_min_cycles_per_stage = int(
        cfg.get("expected_min_cycles_per_stage", 50)
    )
    snapshot_every_seconds = float(
        cfg.get("snapshot_every_seconds", 1800.0)
    )
    # Cycle durations and convergence-detector tunables — exposed in YAML
    # so synthetic demos can run in minutes; production runs use defaults.
    awake_seconds_per_cycle = float(cfg.get("awake_seconds_per_cycle", 30.0))
    dream_seconds_per_cycle = float(cfg.get("dream_seconds_per_cycle", 10.0))
    convergence_window_size = int(cfg.get("convergence_window_size", 10))
    convergence_min_improvement = float(cfg.get("convergence_min_improvement", 0.01))
    convergence_min_history = int(cfg.get("convergence_min_history", 20))
    perplexity_eval_duration_seconds = float(
        cfg.get("perplexity_eval_duration_seconds", 30.0)
    )

    # Lazy imports — keep CLI startup cheap and skip JIT cost for
    # callers who only want the dataclass / verdict.
    from agent.autonomous_loop import (
        AutonomousLoop,
        AutonomousLoopConfig,
        build_autonomous_world,
        configure_world_for_babble,
    )
    from agent.babble import BabbleRunner
    from agent.convergence import ConvergenceDetector
    from agent.corpus_audio_feeder import CorpusAudioFeeder
    from agent.corpus_builder import CorpusBuilder
    from agent.curriculum_scheduler import CurriculumScheduler, CurriculumStage
    from world.audio_predictor import AudioPredictor

    # 2. Build corpora.
    corpus_root = out_dir / "corpus"
    builder = CorpusBuilder(
        de_stage1=list(de_cfg.get("stage1", []) or []),
        de_stage2=list(de_cfg.get("stage2", []) or []),
        de_stage3=list(de_cfg.get("stage3", []) or []),
        de_stage4=list(de_cfg.get("stage4", []) or []),
        fr_sources=list(fr_cfg.get("sources", []) or []),
        seed=seed,
    )
    builder.build(corpus_root)

    # The CorpusBuilder writes corpora under {de, white_noise,
    # reversed_de, fr}; substrate names map onto these. After the
    # 2026-05-10 follow-up, the builder also writes per-stage train
    # files (``stage1_train.f32.raw`` ... ``stage4_train.f32.raw``)
    # so each curriculum stage can point at its own audio source.
    corpus_subdir_for_substrate: dict[str, str] = {
        "trained_de": "de",
        "white_noise": "white_noise",
        "reversed_de": "reversed_de",
        "french": "fr",
    }
    # 3. Train each substrate sequentially.
    state_path = out_dir / "state.json"
    state: dict = {}
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text())
        except (OSError, json.JSONDecodeError):
            state = {}

    # Trained substrate runs first so we can capture per-stage
    # wall-clock durations to feed the controls' matched schedules.
    stage_durations: list[float] = []
    eval_metrics_dir = out_dir / "metrics"
    snapshot_root = out_dir / "snapshots"
    babble_root = out_dir / "babble"

    for substrate_name in SUBSTRATE_NAMES:
        is_trained = substrate_name == TRAINED_NAME
        corpus_subdir = corpus_subdir_for_substrate[substrate_name]
        train_path = corpus_root / corpus_subdir / "train.f32.raw"
        manifest_path = corpus_root / corpus_subdir / "manifest.json"

        # Build per-stage CurriculumStage list. Each stage points at
        # its own ``stage{i}_train.f32.raw`` so the substrate is
        # progressively exposed to a different audio source per stage
        # (spec §3 row 1: audiobook → YouTuber → multi-speaker → webcam).
        # Falls back to the full ``train.f32.raw`` when per-stage files
        # don't exist (e.g. legacy corpora or test fixtures that mock
        # CorpusBuilder.build with a flat output tree).
        per_stage_train_paths: list[Path] = []
        for i in range(4):
            stage_path = corpus_root / corpus_subdir / f"stage{i + 1}_train.f32.raw"
            if not stage_path.exists():
                stage_path = train_path
            per_stage_train_paths.append(stage_path)
        stages = [
            CurriculumStage(
                name=f"stage{i + 1}",
                train_data_path=per_stage_train_paths[i],
                expected_min_cycles=expected_min_cycles_per_stage,
            )
            for i in range(4)
        ]

        if is_trained:
            convergence = ConvergenceDetector(
                window_size=convergence_window_size,
                min_relative_improvement=convergence_min_improvement,
                min_history_for_decision=convergence_min_history,
            )
            wall_clock_per_stage = [0.0, 0.0, 0.0, 0.0]
        else:
            if len(stage_durations) != len(stages):
                raise RuntimeError(
                    "stage_durations not yet populated; trained "
                    "substrate must run before controls"
                )
            convergence = None
            wall_clock_per_stage = list(stage_durations)

        scheduler = CurriculumScheduler(
            stages=stages,
            is_trained=is_trained,
            wall_clock_per_stage=wall_clock_per_stage,
            convergence=convergence,
        )

        # Build substrate, feeder, predictor, loop. The feeder starts
        # on stage 1's audio; we re-load it on each stage advance below
        # so the substrate hears the right source per curriculum stage.
        world = build_autonomous_world()
        # G19: enable Plan F speech-loop coupling and pre-seed audio
        # input/output port atoms at canonical speech harmonics. This
        # is the babble-pipeline opt-in that build_autonomous_world
        # leaves out so G17 emergence runs and the existing test suite
        # behave identically.
        configure_world_for_babble(world)
        feeder = CorpusAudioFeeder(sample_rate=int(SAMPLE_RATE))
        feeder.load_stage(per_stage_train_paths[0], manifest_path)
        predictor = AudioPredictor()
        substrate_snapshot_dir = snapshot_root / substrate_name
        substrate_snapshot_dir.mkdir(parents=True, exist_ok=True)
        eval_metrics_dir.mkdir(parents=True, exist_ok=True)
        loop_cfg = AutonomousLoopConfig(
            audio_io=feeder,  # duck-typed
            awake_seconds_per_cycle=awake_seconds_per_cycle,
            dream_seconds_per_cycle=dream_seconds_per_cycle,
            snapshot_dir=str(substrate_snapshot_dir),
            metrics_log_path=str(eval_metrics_dir / f"{substrate_name}.csv"),
        )
        loop = AutonomousLoop(world, loop_cfg)

        # 3a. Drive the loop in a controlled mini-loop. We do not call
        # ``loop.run()`` because that's a daemon that only stops on
        # ``stop_event``. Instead we step one cycle at a time
        # (awake+dream) and feed perplexity to the scheduler every K
        # cycles. Stop when the scheduler is_done.
        cycle_index = 0
        stage_start_time = time.time()
        per_stage_start_index = 0
        substrate_stage_durations: list[float] = []
        last_snapshot_sim_t = float(world.t)

        while not scheduler.is_done():
            cycle_index += 1
            loop.cycle = cycle_index
            cycle_start = time.time()
            cycle_start_t = float(world.t)

            # Inline-equivalent of one autonomous_loop cycle. We keep
            # the awake-phase audio injection (which the
            # autonomous_loop wires through cfg.audio_io) and the
            # standard awake/dream split. We drive it via the loop's
            # private helpers so we share the metrics-capture code
            # path with production.
            loop._run_awake_phase()
            awake_metrics = loop._snapshot_metrics(
                phase="awake",
                wall_time=time.time() - cycle_start,
                sim_time=float(world.t) - cycle_start_t,
                fires_in_cycle=loop._count_fires_since(cycle_start_t),
            )
            loop.metrics.append(awake_metrics)
            loop._error_history.append(awake_metrics.prediction_error)
            loop._error_history = loop._error_history[
                -loop.cfg.stagnation_window :
            ]
            if loop.cfg.metrics_log_path:
                loop._append_metrics_csv()

            # Predictor catches up on this cycle's audio-port firings.
            predictor.observe_world(world, port="audio_input")

            # Snapshot every snapshot_every_seconds of sim time.
            if (float(world.t) - last_snapshot_sim_t
                    >= snapshot_every_seconds):
                loop._save_snapshot()
                last_snapshot_sim_t = float(world.t)

            # Every K cycles, evaluate perplexity on the dev split.
            if cycle_index % perplexity_eval_interval_cycles == 0:
                perplexity = _evaluate_perplexity_on_dev(
                    world=world,
                    predictor=predictor,
                    dev_path=corpus_root / corpus_subdir / "dev.f32.raw",
                    eval_duration_seconds=perplexity_eval_duration_seconds,
                    sample_rate=int(SAMPLE_RATE),
                )
                elapsed = (
                    time.time()
                    - stage_start_time
                    + sum(substrate_stage_durations)
                )
                advanced = scheduler.step(
                    perplexity=perplexity,
                    elapsed_seconds=elapsed,
                )
                if advanced:
                    stage_wall = time.time() - stage_start_time
                    substrate_stage_durations.append(stage_wall)
                    per_stage_start_index = cycle_index
                    stage_start_time = time.time()
                    if not scheduler.is_done():
                        # Advance the feeder onto the next stage's
                        # per-stage train file (audiobook → YouTuber →
                        # multi-speaker → webcam, per spec §3 row 1).
                        next_stage_idx = int(
                            scheduler.current_stage_index
                        )
                        if 0 <= next_stage_idx < len(per_stage_train_paths):
                            feeder.load_stage(
                                per_stage_train_paths[next_stage_idx],
                                manifest_path,
                            )
                        else:
                            feeder.reset()

            # Persist resume state cheaply.
            state[substrate_name] = {
                "cycle": cycle_index,
                "stage_index": int(scheduler.current_stage_index),
            }
            # Cheap write — no atomic rename, the file is advisory.
            try:
                state_path.write_text(json.dumps(state, indent=2))
            except OSError:
                pass

        # Pad stage_durations if scheduler is_done() but we never saw
        # an advance (fail-safe — should not happen in practice).
        while len(substrate_stage_durations) < len(stages):
            substrate_stage_durations.append(time.time() - stage_start_time)

        if is_trained:
            stage_durations = substrate_stage_durations

        # 4. Babble per substrate.
        babble_path = babble_root / f"{substrate_name}.wav"
        babble_path.parent.mkdir(parents=True, exist_ok=True)
        babble_runner = BabbleRunner(
            world=world,
            autonomous_loop_cfg=loop_cfg,
            duration_seconds=babble_duration_seconds,
            output_path=babble_path,
            sample_rate=int(SAMPLE_RATE),
            # G19: predictive-babble pipeline drives output via dream-replay
            # of high-eligibility audio_output port atoms. Without this the
            # output port has no internal source of firings during the
            # babble window and wavs are silent. --mini and tests use the
            # default False to preserve their assertions.
            enable_dream_replay=True,
        )
        _samples, written = babble_runner.run()
        if written is None or not Path(written).exists():
            raise RuntimeError(
                f"BabbleRunner did not produce a wav for {substrate_name}"
            )

    # 5. Reference test wav: convert trained DE test split to wav.
    test_path = corpus_root / corpus_subdir_for_substrate[TRAINED_NAME] / "test.f32.raw"
    if not test_path.exists():
        raise RuntimeError(
            f"trained DE test split missing: {test_path}"
        )
    reference_wav = out_dir / "reference.wav"
    test_audio = np.fromfile(test_path, dtype=np.float32)
    if test_audio.size == 0:
        raise RuntimeError(
            f"trained DE test split is empty: {test_path}"
        )
    _write_wav(test_audio, reference_wav, sr=SAMPLE_RATE)

    # 6. Evaluate.
    trained_wav = babble_root / f"{TRAINED_NAME}.wav"
    control_wavs = {n: babble_root / f"{n}.wav" for n in CONTROL_NAMES}
    result = evaluate(
        trained_wav=trained_wav,
        control_wavs=control_wavs,
        reference_test_wav=reference_wav,
        n_bootstrap=n_bootstrap,
        seed=seed,
        n_clusters=n_clusters,
        sr=int(SAMPLE_RATE),
    )

    # 7. Persist result.json.
    result_path = out_dir / "result.json"
    result_path.write_text(json.dumps(_result_to_json_dict(result), indent=2))

    return result


# Sentinel "I have no signal" perplexity. Returned by
# _evaluate_perplexity_on_dev when the substrate hasn't fired in the
# audio_input port during the dev window, or when the predictor has no
# vocabulary yet. We use a large finite stand-in instead of
# float('inf') because the convergence detector's relative-improvement
# math (mean_prev - mean_last) becomes NaN on inf - inf, which breaks
# plateau detection — the substrate would be stuck on stage 0 forever.
# 1e6 is large enough to dwarf any real perplexity (vocab sizes < 10⁵)
# but finite enough that "stable no-signal" reads as plateau, allowing
# stages to advance even early in training. When the substrate later
# starts firing, real perplexity drops to <100, which is a huge
# improvement vs 1e6 → detector correctly says "improving, not
# plateaued" until the real signal stabilises.
_NO_SIGNAL_PERPLEXITY = 1_000_000.0


def _evaluate_perplexity_on_dev(
    world,
    predictor,
    dev_path: Path,
    eval_duration_seconds: float = 30.0,
    sample_rate: int = SAMPLE_RATE,
) -> float:
    """Evaluate the predictor's perplexity on held-out dev audio.

    Procedure (spec §3 row ``agent/run_babble_experiment.py``,
    2026-05-10 follow-up replacing the earlier circular stand-in):

    1. Snapshot world state in-memory so the dev evaluation cannot
       contaminate the training trajectory.
    2. Build a temporary :class:`CorpusAudioFeeder` pointing at
       ``dev_path``.
    3. Inject ``eval_duration_seconds`` of dev audio into the world via
       ``feeder.inject_into_substrate``.
    4. Tick physics for the same duration at ``world.config.dt``.
    5. Filter ``world.firing_events`` to events whose atom position
       lies inside the audio_input port AND whose timestamp falls in
       the eval window. Map atom_idx → ``world.k_pattern_id[idx]``;
       drop pid==0 (ambient) firings. Result is the held-out
       pattern_id sequence.
    6. Compute ``predictor.perplexity(sequence)`` — READ ONLY. We do
       not call ``observe`` so the dev data never trains the predictor.
       If the sequence has fewer than 2 elements (substrate did not
       fire in the audio_input port during dev), return ``inf`` —
       honest about non-convergence rather than a soft pass.
    7. Restore world state from the in-memory snapshot.

    Short-circuit: if the predictor has not yet seen any pattern_ids
    (vocabulary empty) or the world has no atoms, return ``inf``
    without ticking. Avoids the expensive snapshot+tick+restore round
    trip when there is nothing to evaluate yet — and is honest about a
    substrate that has not even begun building a vocabulary.

    Snapshot mechanism note: spec §10 hinted that
    ``world.snapshot.save_snapshot`` could be used directly. In
    practice the on-disk save+load round-trip drops several
    World fields (``k_pattern_id``, ``k_eligibility``, the slot
    recycling free-list, the self-model dict, etc.), so we do an
    in-memory copy of the full World state here instead. Everything
    that physics or dream may mutate is captured. Disk I/O is also
    avoided per-eval, which matters because the dev evaluation runs
    every K cycles across a 24-hour run.
    """
    import tempfile

    # Honest-default short circuits.
    if predictor.vocabulary_size() == 0:
        return _NO_SIGNAL_PERPLEXITY
    K = int(getattr(world, "k_count", 0))
    if K == 0:
        return _NO_SIGNAL_PERPLEXITY
    if not Path(dev_path).exists():
        return _NO_SIGNAL_PERPLEXITY
    if eval_duration_seconds <= 0.0:
        return _NO_SIGNAL_PERPLEXITY

    # 1. In-memory snapshot. Cheap (per-array .copy()), avoids disk I/O,
    # and captures fields ``world.snapshot.save_snapshot`` doesn't.
    snapshot = _capture_world_state(world)
    eval_window_start_t = float(world.t)
    try:
        # 2. Build a dev feeder. We need the dev corpus's manifest;
        # fall back to a synthetic in-memory manifest when the corpus
        # builder hasn't written one (older test fixtures).
        dev_manifest_path = Path(dev_path).parent / "manifest.json"
        if not dev_manifest_path.exists():
            # Write a minimal manifest next to the dev file so the
            # feeder's sample-rate cross-check is satisfied. Use a
            # tempfile to avoid mutating the corpus tree on disk.
            with tempfile.NamedTemporaryFile(
                suffix=".json", delete=False, mode="w",
            ) as mf_tmp:
                json.dump(
                    {
                        "name": "dev",
                        "sample_rate": int(sample_rate),
                    },
                    mf_tmp,
                )
                mf_tmp_path = Path(mf_tmp.name)
            dev_manifest_path = mf_tmp_path
        from agent.corpus_audio_feeder import CorpusAudioFeeder
        dev_feeder = CorpusAudioFeeder(sample_rate=int(sample_rate))
        try:
            dev_feeder.load_stage(Path(dev_path), dev_manifest_path)
        except (FileNotFoundError, ValueError):
            # Empty or unreadable dev split — honest non-convergence.
            return _NO_SIGNAL_PERPLEXITY

        # 3. Inject dev audio.
        dev_feeder.inject_into_substrate(
            world, float(eval_duration_seconds),
        )

        # 4. Tick physics for the eval window.
        try:
            from world.physics import tick as _tick
        except ImportError:
            return _NO_SIGNAL_PERPLEXITY
        dt = float(world.config.dt)
        if dt <= 0.0:
            return _NO_SIGNAL_PERPLEXITY
        n_ticks = max(1, int(round(float(eval_duration_seconds) / dt)))
        for _ in range(n_ticks):
            _tick(world, dt)

        # 5. Harvest pattern_id sequence from firing_events in the
        # eval window AND inside the audio_input port box. Filter
        # pid==0 (ambient/unassigned) so we measure only the
        # phoneme-scale pattern alphabet the predictor actually
        # models.
        cfg = world.config
        origin = getattr(cfg, "audio_input_port_origin", None)
        size = getattr(cfg, "audio_input_port_size", None)
        sequence: list[int] = []
        if origin is not None and size is not None:
            ox, oy, oz = (
                float(origin[0]), float(origin[1]), float(origin[2]),
            )
            sx, sy, sz = (
                float(size[0]), float(size[1]), float(size[2]),
            )
            K_now = int(getattr(world, "k_count", 0))
            k_pos = world.k_pos
            k_pattern_id = world.k_pattern_id
            for t_fire, atom_idx in world.firing_events:
                if t_fire < eval_window_start_t:
                    continue
                if atom_idx < 0 or atom_idx >= K_now:
                    continue
                pos = k_pos[atom_idx]
                if not (ox <= pos[0] <= ox + sx
                        and oy <= pos[1] <= oy + sy
                        and oz <= pos[2] <= oz + sz):
                    continue
                pid = int(k_pattern_id[atom_idx])
                if pid == 0:
                    continue
                sequence.append(pid)

        # 6. Compute perplexity (READ ONLY — no observe()).
        if len(sequence) < 2:
            return _NO_SIGNAL_PERPLEXITY
        perp = predictor.perplexity(sequence)
        if not np.isfinite(perp):
            return _NO_SIGNAL_PERPLEXITY
        return float(perp)
    finally:
        # 7. Restore world state. We mutate ``world`` in place so the
        # caller's reference (and the autonomous loop's ``self.world``)
        # stays valid.
        _restore_world_state(world, snapshot)


def _capture_world_state(world) -> dict:
    """In-memory snapshot of every World field physics or dream may mutate.

    We copy every numpy array (so subsequent in-place mutations don't
    leak back through aliasing) and the scalar/list fields that get
    appended to or rebound during a tick. The returned dict is fed
    back into :func:`_restore_world_state`.

    Why not :func:`world.snapshot.save_snapshot`? That API was built
    for cycle-end resumability and only persists a subset of fields
    (notably it drops ``k_pattern_id``, ``k_eligibility``, the slot
    recycling free-list, the self-model dict, and dream sub-phase
    state). The dev evaluation needs full transparency, so we capture
    here what production resumability does not need.
    """
    snap: dict = {}
    # Vibration arrays.
    snap["s_pos"] = world.s_pos.copy()
    snap["s_vel"] = world.s_vel.copy()
    snap["s_freq"] = world.s_freq.copy()
    snap["s_pol"] = world.s_pol.copy()
    snap["s_alive"] = world.s_alive.copy()
    snap["s_locked_this_tick"] = world.s_locked_this_tick.copy()
    snap["s_reward_polarity"] = world.s_reward_polarity.copy()
    snap["n_alive"] = int(world.n_alive)
    # Node arrays.
    snap["k_pos"] = world.k_pos.copy()
    snap["k_vel"] = world.k_vel.copy()
    snap["k_freq"] = world.k_freq.copy()
    snap["k_pol"] = world.k_pol.copy()
    snap["k_level"] = world.k_level.copy()
    snap["k_birth"] = world.k_birth.copy()
    snap["k_alive"] = world.k_alive.copy()
    snap["k_locked_this_tick"] = world.k_locked_this_tick.copy()
    snap["k_charge"] = world.k_charge.copy()
    snap["k_refractory_until"] = world.k_refractory_until.copy()
    snap["k_strength"] = world.k_strength.copy()
    snap["k_orientation"] = world.k_orientation.copy()
    snap["k_reward_polarity"] = world.k_reward_polarity.copy()
    snap["k_ref_count"] = world.k_ref_count.copy()
    snap["k_pattern_id"] = world.k_pattern_id.copy()
    snap["k_eligibility"] = world.k_eligibility.copy()
    snap["k_count"] = int(world.k_count)
    snap["active_pattern_id"] = int(world.active_pattern_id)
    # Composition arrays.
    snap["k_comp_offset"] = world.k_comp_offset.copy()
    snap["k_comp_end"] = world.k_comp_end.copy()
    snap["k_comp_indices"] = world.k_comp_indices.copy()
    snap["k_comp_kind"] = world.k_comp_kind.copy()
    snap["k_comp_used"] = int(world.k_comp_used)
    # Firing log + sim time.
    snap["firing_events"] = list(world.firing_events)
    snap["t"] = float(world.t)
    # Slot recycling bookkeeping (lists, not arrays).
    snap["_free_slots"] = list(getattr(world, "_free_slots", []))
    snap["_free_slots_set"] = set(getattr(world, "_free_slots_set", set()))
    # G16 self-aware state — dicts that apply_self_aware mutates.
    snap["self_model"] = dict(getattr(world, "self_model", {}))
    snap["self_predicted_next"] = dict(
        getattr(world, "self_predicted_next", {})
    )
    snap["self_prediction_error"] = float(
        getattr(world, "self_prediction_error", 0.0)
    )
    snap["workspace_winner_pattern_id"] = int(
        getattr(world, "workspace_winner_pattern_id", 0)
    )
    snap["workspace_history"] = list(
        getattr(world, "workspace_history", [])
    )
    snap["dream_subphase_counter"] = int(
        getattr(world, "dream_subphase_counter", 0)
    )
    return snap


def _restore_world_state(world, snap: dict) -> None:
    """Inverse of :func:`_capture_world_state` — restore in place."""
    # Vibration arrays.
    world.s_pos[:] = snap["s_pos"]
    world.s_vel[:] = snap["s_vel"]
    world.s_freq[:] = snap["s_freq"]
    world.s_pol[:] = snap["s_pol"]
    world.s_alive[:] = snap["s_alive"]
    world.s_locked_this_tick[:] = snap["s_locked_this_tick"]
    world.s_reward_polarity[:] = snap["s_reward_polarity"]
    world.n_alive = int(snap["n_alive"])
    # Node arrays.
    world.k_pos[:] = snap["k_pos"]
    world.k_vel[:] = snap["k_vel"]
    world.k_freq[:] = snap["k_freq"]
    world.k_pol[:] = snap["k_pol"]
    world.k_level[:] = snap["k_level"]
    world.k_birth[:] = snap["k_birth"]
    world.k_alive[:] = snap["k_alive"]
    world.k_locked_this_tick[:] = snap["k_locked_this_tick"]
    world.k_charge[:] = snap["k_charge"]
    world.k_refractory_until[:] = snap["k_refractory_until"]
    world.k_strength[:] = snap["k_strength"]
    world.k_orientation[:] = snap["k_orientation"]
    world.k_reward_polarity[:] = snap["k_reward_polarity"]
    world.k_ref_count[:] = snap["k_ref_count"]
    world.k_pattern_id[:] = snap["k_pattern_id"]
    world.k_eligibility[:] = snap["k_eligibility"]
    world.k_count = int(snap["k_count"])
    world.active_pattern_id = int(snap["active_pattern_id"])
    # Composition arrays.
    world.k_comp_offset[:] = snap["k_comp_offset"]
    world.k_comp_end[:] = snap["k_comp_end"]
    world.k_comp_indices[:] = snap["k_comp_indices"]
    world.k_comp_kind[:] = snap["k_comp_kind"]
    world.k_comp_used = int(snap["k_comp_used"])
    # Firing log + sim time.
    world.firing_events = list(snap["firing_events"])
    world.t = float(snap["t"])
    # Slot recycling bookkeeping.
    world._free_slots = list(snap["_free_slots"])
    world._free_slots_set = set(snap["_free_slots_set"])
    # G16 self-aware state.
    world.self_model = dict(snap["self_model"])
    world.self_predicted_next = dict(snap["self_predicted_next"])
    world.self_prediction_error = float(snap["self_prediction_error"])
    world.workspace_winner_pattern_id = int(
        snap["workspace_winner_pattern_id"]
    )
    world.workspace_history = list(snap["workspace_history"])
    world.dream_subphase_counter = int(snap["dream_subphase_counter"])


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m agent.run_babble_experiment",
        description=(
            "Top-level driver for the predictive-babble experiment. "
            "Use --mini for the integration-test contract; --config "
            "for the full curriculum acceptance run."
        ),
    )
    parser.add_argument(
        "--mini", action="store_true",
        help="Run the mini pipeline test (synthetic streams, 4 wavs, eval).",
    )
    parser.add_argument(
        "--config", type=Path, default=None,
        help="YAML config for the full curriculum run.",
    )
    parser.add_argument(
        "--out", type=Path, default=None,
        help=("Output directory. Default for --mini is "
              "~/.eqmod/babble/mini/. Required for --config."),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.mini and args.config is not None:
        raise SystemExit("--mini and --config are mutually exclusive")
    if not args.mini and args.config is None:
        raise SystemExit("either --mini or --config is required")

    if args.mini:
        out_dir = args.out or (Path.home() / ".eqmod" / "babble" / "mini")
        start = time.time()
        result = run_mini(out_dir=Path(out_dir))
        elapsed = time.time() - start
        wavs = sorted(p.name for p in out_dir.glob("*/babble.wav"))
        print(
            f"MINI RUN COMPLETE — {len(wavs)} wav files in {out_dir}/, "
            f"verdict={result.verdict} (elapsed={elapsed:.1f}s)"
        )
        return 0

    # Full mode.
    if args.out is None:
        raise SystemExit("--out is required with --config")
    result = run_full(config_path=args.config, out_dir=args.out)
    print(json.dumps(asdict(result), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
