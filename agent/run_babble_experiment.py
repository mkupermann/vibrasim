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


def run_full(config_path: Path, out_dir: Path) -> EvaluationResult:  # pragma: no cover - production path
    """Full curriculum acceptance run (spec §6).

    TODO(iteration-6+): wire CorpusBuilder + AutonomousLoop +
    CurriculumScheduler + ConvergenceDetector + BabbleRunner +
    evaluator. The mini-mode contract is the only path the
    iteration-5b acceptance test gates on; full mode is for the
    "Full curriculum acceptance run" step in §10 of the spec, which
    runs after iteration-5b lands.

    The expected wiring is:

    1. ``CorpusBuilder.build(out_dir / 'corpus')`` to produce four
       16 kHz mono float32 corpora with 80/10/10 splits.
    2. For each substrate (one trained + three controls): build a
       fresh autonomous world, attach an AudioIO to its train split,
       run AutonomousLoop with audio_io set, drive
       CurriculumScheduler+ConvergenceDetector through the four
       stages, until all four reach babble mode.
    3. Run BabbleRunner for 5 minutes per substrate.
    4. Run evaluate() with n_clusters=256 and n_bootstrap=100 against
       the held-back test split.
    5. Write the report to ``out_dir / 'result.json'``.
    """
    raise NotImplementedError(
        "Full curriculum mode lands in iteration-6. "
        "The iteration-5b contract is gated on --mini only."
    )


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
