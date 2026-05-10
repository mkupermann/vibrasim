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

    # Lazy imports — keep CLI startup cheap and skip JIT cost for
    # callers who only want the dataclass / verdict.
    from agent.autonomous_loop import (
        AutonomousLoop,
        AutonomousLoopConfig,
        build_autonomous_world,
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
    # reversed_de, fr}; substrate names map onto these.
    # MVP simplification (acknowledged in the spec §10 — per-stage
    # outputs are a future CorpusBuilder extension): each stage in the
    # CurriculumScheduler points at the same per-substrate train
    # split. The scheduler still drives advancement via convergence;
    # the feeder loops on the same file across stages until then.
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

        # Build per-stage CurriculumStage list. All four stages point
        # at the same train file for now; advancement is the
        # scheduler's responsibility.
        stages = [
            CurriculumStage(
                name=f"stage{i + 1}",
                train_data_path=train_path,
                expected_min_cycles=expected_min_cycles_per_stage,
            )
            for i in range(4)
        ]

        if is_trained:
            convergence = ConvergenceDetector()
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

        # Build substrate, feeder, predictor, loop.
        world = build_autonomous_world()
        feeder = CorpusAudioFeeder(sample_rate=int(SAMPLE_RATE))
        feeder.load_stage(train_path, manifest_path)
        predictor = AudioPredictor()
        substrate_snapshot_dir = snapshot_root / substrate_name
        substrate_snapshot_dir.mkdir(parents=True, exist_ok=True)
        eval_metrics_dir.mkdir(parents=True, exist_ok=True)
        loop_cfg = AutonomousLoopConfig(
            audio_io=feeder,  # duck-typed
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
                    predictor=predictor,
                    dev_path=corpus_root / corpus_subdir / "dev.f32.raw",
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
                        # Reload the same train file (MVP: per-stage
                        # files would differ in a future iteration).
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


def _evaluate_perplexity_on_dev(predictor, dev_path: Path) -> float:
    """Compute perplexity over the dev-split pattern_id sequence.

    The audio_predictor's ``perplexity`` method takes a sequence of
    pattern_ids; in this simplified MVP we approximate by walking the
    predictor's vocabulary across the existing ``_history`` -- see
    the predictor's docstring for context. Returns a positive float;
    if the predictor has no observed transitions yet we return a
    large sentinel (10x current vocab size) so ``ConvergenceDetector``
    sees a strictly-decreasing series early on.
    """
    # The dev_path is the f32.raw of the dev split. Encoding the dev
    # split through the predictor is a future hardening step (it
    # requires a separate substrate forward-pass to elicit its
    # pattern_id sequence). For MVP, we report the predictor's
    # internal perplexity over the most recent observed sequence.
    vocab_size = max(1, predictor.vocabulary_size())
    # Synthetic 'recent observations' — read the last few pattern_ids
    # from _last_seen_pid only. If we have at least one transition
    # recorded we can compute perplexity over a degenerate two-element
    # sequence; otherwise fall back to vocab_size as a baseline.
    if not predictor._counts:
        return float(10 * vocab_size)
    # Pick a chain through the most-frequent transitions to estimate
    # the model's confidence on its own data — a stand-in for the
    # full dev forward-pass.
    sample = list(predictor._counts.keys())[:max(2, vocab_size)]
    if len(sample) < 2:
        sample = sample + sample  # degenerate two-element sequence
    perp = predictor.perplexity(sample)
    if not np.isfinite(perp):
        return float(vocab_size)
    return float(perp)


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
