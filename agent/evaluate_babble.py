"""Acceptance evaluator for the predictive-babble pipeline.

Iteration 5a of the predictive-babble pipeline (see
``docs/superpowers/specs/2026-05-10-predictive-babble-design.md``, §3 row
``agent/evaluate_babble.py`` and §6 acceptance criterion).

Pipeline (per spec §6):

1. Extract MFCC frames from each substrate's babble wav at 10 ms hop.
2. Fit a k-means codebook (256 clusters) on the held-back German *test
   split* MFCC frames. The codebook defines the histogram bins.
3. For each substrate (trained + 3 controls), build a normalised
   histogram of its MFCC frames against the codebook, compute KL
   divergence against the test-split's own histogram (with Laplace
   smoothing on q to avoid log(0)), and bootstrap that estimate 100
   times by resampling MFCC frames with replacement.
4. Compute the falsifier verdict:

   * **PASS**  trained's mean KL is lower than every control's mean KL
                by ≥ 2 standard deviations.
   * **FAIL**  trained is statistically indistinguishable (z ≤ 0)
                from the white-noise control.
   * **NULL**  otherwise — the verdict carries the list of controls
                for which the evidence is inconclusive.

Design notes (no silent-pass paths — cf. §4 last bullet of the spec):

* Every substrate must yield ≥ 1 MFCC frame; otherwise we raise loudly.
  An empty histogram or NaN KL would silently look "great" against
  controls and trip the F3b silent-pass class of bugs.
* The reference distribution ``q`` is Laplace-smoothed before
  ``log(p/q)`` so a bin with zero reference probability cannot push
  KL to ``inf`` and pretend everything passed.
* ``EvaluationResult`` is JSON-serialisable: every numpy scalar is
  converted to a Python ``float`` / ``int`` / ``str`` in the dataclass.
* The CLI (``python -m agent.evaluate_babble``) writes the result to a
  caller-specified JSON path. The CLI is thin and delegates to the
  pure-function API.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from math import sqrt
from pathlib import Path
from typing import Literal

import librosa
import numpy as np
import scipy.io.wavfile
from sklearn.cluster import KMeans


# ----------------------------------------------------------------------
# Public dataclass


VerdictT = Literal["PASS", "FAIL", "NULL"]


@dataclass
class EvaluationResult:
    """Outcome of the §6 falsifier evaluation.

    Attributes
    ----------
    verdict
        ``"PASS"``, ``"FAIL"``, or ``"NULL"``.
    null_against
        Names of controls against which the evidence is inconclusive.
        Empty for ``"PASS"``. May or may not be empty for ``"FAIL"``.
    trained_kl_mean, trained_kl_std
        Bootstrap mean and std of the trained substrate's KL.
    control_kl
        ``{control_name: (mean, std)}`` for each control.
    z_scores
        ``{control_name: z}`` where higher-positive ``z`` means trained
        beats the control more decisively (trained's KL is lower).
    n_frames_per_substrate
        ``{substrate_name: n_mfcc_frames}`` — useful for debugging
        short or silent wavs.
    n_bootstrap
        Number of bootstrap iterations used.
    """

    verdict: VerdictT
    null_against: list[str]
    trained_kl_mean: float
    trained_kl_std: float
    control_kl: dict[str, tuple[float, float]]
    z_scores: dict[str, float]
    n_frames_per_substrate: dict[str, int]
    n_bootstrap: int = 100


# ----------------------------------------------------------------------
# Step 1: MFCC extraction


def extract_mfcc(
    wav_path: Path,
    sr: int = 16000,
    n_mfcc: int = 20,
    hop_length: int = 160,
) -> np.ndarray:
    """Read a wav and return its MFCC frame matrix ``[n_frames, n_mfcc]``.

    Uses :func:`librosa.feature.mfcc` with the spec's parameters
    (``sr=16000``, ``n_mfcc=20``, ``hop_length=160`` -- 10 ms hop).
    The wav is decoded via :mod:`scipy.io.wavfile` (stable, no codec
    surprises) and converted to mono float32 in ``[-1, 1]``.
    """
    p = Path(wav_path)
    if not p.exists():
        raise FileNotFoundError(f"wav not found: {p}")

    file_sr, data = scipy.io.wavfile.read(str(p))
    if file_sr != sr:
        raise ValueError(
            f"wav sample rate is {file_sr}, expected {sr}; "
            f"resample upstream rather than silently reinterpreting"
        )

    # Convert to mono float32 in [-1, 1] regardless of source dtype.
    if data.ndim > 1:
        data = np.mean(data, axis=1)
    data = data.astype(np.float64, copy=False)
    if np.issubdtype(data.dtype, np.integer):
        # Already cast to float64 above; keep guard in case dtype shifts.
        max_abs = float(np.iinfo(np.int16).max)
        data = data / max_abs
    else:
        peak = float(np.max(np.abs(data))) if data.size else 0.0
        if peak > 1.0 + 1e-3:
            # int-stored-as-float (e.g. int16 cast); scale by int16 max.
            data = data / 32768.0
    audio = data.astype(np.float32, copy=False)

    if audio.size == 0:
        raise ValueError(f"wav has zero samples: {p}")

    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=sr,
        n_mfcc=n_mfcc,
        hop_length=hop_length,
    )
    # librosa returns ``(n_mfcc, n_frames)``; transpose for downstream.
    return np.asarray(mfcc.T, dtype=np.float64)


# ----------------------------------------------------------------------
# Step 2: codebook fit


def fit_codebook(
    reference_mfcc: np.ndarray,
    n_clusters: int = 256,
    seed: int = 0,
) -> KMeans:
    """Fit a k-means codebook on reference MFCC frames.

    The reference is the held-back German *test split* MFCC frames.
    ``n_init`` is set explicitly to silence sklearn 1.4+'s
    FutureWarning and ensure deterministic behaviour given ``seed``.
    """
    if reference_mfcc.ndim != 2:
        raise ValueError(
            f"reference_mfcc must be 2-D [n_frames, n_mfcc]; "
            f"got shape {reference_mfcc.shape}"
        )
    if reference_mfcc.shape[0] < n_clusters:
        raise ValueError(
            f"reference has {reference_mfcc.shape[0]} frames but "
            f"n_clusters={n_clusters}; need at least one frame per cluster"
        )
    km = KMeans(
        n_clusters=int(n_clusters),
        n_init=10,
        random_state=int(seed),
    )
    km.fit(reference_mfcc)
    return km


# ----------------------------------------------------------------------
# Step 3: histogram


def quantise_to_histogram(
    mfcc: np.ndarray,
    codebook: KMeans,
) -> np.ndarray:
    """Assign each MFCC frame to its nearest centroid; return normalised counts.

    Returns a length-``n_clusters`` probability vector that sums to 1.
    """
    if mfcc.ndim != 2:
        raise ValueError(
            f"mfcc must be 2-D [n_frames, n_mfcc]; got shape {mfcc.shape}"
        )
    if mfcc.shape[0] == 0:
        raise ValueError("cannot histogram zero MFCC frames")

    n_clusters = int(codebook.n_clusters)
    labels = codebook.predict(mfcc)
    counts = np.bincount(labels, minlength=n_clusters).astype(np.float64)
    total = float(counts.sum())
    if total <= 0.0:
        # Defensive: sklearn.predict always returns valid labels, so
        # this is unreachable in practice. Raise rather than produce
        # NaN -- a NaN distribution downstream would silent-pass.
        raise RuntimeError("histogram total is zero; cannot normalise")
    return counts / total


# ----------------------------------------------------------------------
# Step 4: KL divergence


def kl_divergence(
    p: np.ndarray,
    q: np.ndarray,
    smoothing: float = 1e-9,
) -> float:
    """``KL(p || q)`` with Laplace smoothing on ``q``.

    Smoothing: ``q' = (q + smoothing) / sum(q + smoothing)``. Bins where
    ``p[i] == 0`` contribute zero (we follow the convention
    ``0 * log(0/q) = 0`` from information theory). This makes the
    estimator robust against unseen bins in ``p``; bins with ``q'[i]
    == 0`` are mathematically impossible after smoothing because
    ``smoothing > 0``.
    """
    if p.shape != q.shape:
        raise ValueError(
            f"p.shape={p.shape} != q.shape={q.shape}; "
            "distributions must match"
        )
    if smoothing <= 0.0:
        raise ValueError("smoothing must be positive")

    p_arr = np.asarray(p, dtype=np.float64)
    q_arr = np.asarray(q, dtype=np.float64)
    q_smooth = q_arr + smoothing
    q_smooth = q_smooth / q_smooth.sum()

    nonzero = p_arr > 0.0
    if not np.any(nonzero):
        # All-zero p is not a valid distribution; return 0 (defensive).
        return 0.0
    p_nz = p_arr[nonzero]
    q_nz = q_smooth[nonzero]
    kl = float(np.sum(p_nz * np.log(p_nz / q_nz)))
    if not np.isfinite(kl):
        raise FloatingPointError(
            f"KL divergence is non-finite ({kl}); check smoothing"
        )
    return kl


# ----------------------------------------------------------------------
# Step 5: bootstrap


def bootstrap_kl(
    mfcc: np.ndarray,
    codebook: KMeans,
    reference_q: np.ndarray,
    n_bootstrap: int = 100,
    seed: int = 0,
) -> tuple[float, float]:
    """Bootstrap KL between this substrate's MFCC distribution and ``reference_q``.

    Resamples MFCC frames with replacement ``n_bootstrap`` times. Each
    resample size equals the original frame count. Returns
    ``(mean_kl, std_kl)``.
    """
    if mfcc.ndim != 2:
        raise ValueError(
            f"mfcc must be 2-D [n_frames, n_mfcc]; got shape {mfcc.shape}"
        )
    n = mfcc.shape[0]
    if n == 0:
        raise ValueError("cannot bootstrap on zero MFCC frames")
    if n_bootstrap <= 0:
        raise ValueError("n_bootstrap must be positive")
    if reference_q.shape[0] != int(codebook.n_clusters):
        raise ValueError(
            f"reference_q has length {reference_q.shape[0]} but "
            f"codebook has {codebook.n_clusters} clusters"
        )

    rng = np.random.default_rng(int(seed))
    kls = np.empty(n_bootstrap, dtype=np.float64)
    for i in range(int(n_bootstrap)):
        idx = rng.integers(low=0, high=n, size=n)
        resample = mfcc[idx]
        p = quantise_to_histogram(resample, codebook)
        kls[i] = kl_divergence(p, reference_q)

    mean_kl = float(np.mean(kls))
    # ddof=1 sample std; if n_bootstrap == 1 fall back to 0.0 to avoid
    # division by zero (callers should not run with 1 iteration).
    std_kl = float(np.std(kls, ddof=1)) if n_bootstrap > 1 else 0.0
    return mean_kl, std_kl


# ----------------------------------------------------------------------
# Step 6: top-level evaluation


@dataclass
class _SubstrateStat:
    name: str
    mean: float
    std: float
    n_frames: int


def _z_score(trained: _SubstrateStat, control: _SubstrateStat) -> float:
    """Z-score for trained-beats-control: positive means trained < control."""
    denom = sqrt(trained.std ** 2 + control.std ** 2)
    if denom <= 0.0:
        # Identical-variance edge case (e.g. trained == control on
        # synthetic input). Return 0 to mark as inconclusive rather
        # than dividing by zero.
        return 0.0
    return float((control.mean - trained.mean) / denom)


def evaluate(
    trained_wav: Path,
    control_wavs: dict[str, Path],
    reference_test_wav: Path,
    n_bootstrap: int = 100,
    seed: int = 0,
    n_clusters: int = 256,
    sr: int = 16000,
    n_mfcc: int = 20,
    hop_length: int = 160,
) -> EvaluationResult:
    """Run the §6 falsifier and return an :class:`EvaluationResult`.

    Parameters
    ----------
    trained_wav
        Path to the trained substrate's babble wav.
    control_wavs
        Mapping ``{control_name: wav_path}``. The acceptance run uses
        ``{"white_noise": ..., "reversed_de": ..., "french": ...}`` but
        any names are accepted; the verdict logic only treats
        ``"white_noise"`` specially (FAIL if trained ≈ white_noise).
    reference_test_wav
        Path to the held-back German *test split* (concatenated to a
        single wav). Its MFCC frames define the codebook AND the
        reference distribution ``q``.
    n_bootstrap
        Number of bootstrap iterations per substrate (default 100 from
        the spec).
    seed
        Reproducibility seed for both the bootstrap RNG and KMeans.
    n_clusters
        Codebook size. Production runs use 256 (per §6); tests pass a
        smaller value (e.g. 16) for speed.
    sr, n_mfcc, hop_length
        MFCC parameters. Defaults match the spec.
    """
    if not control_wavs:
        raise ValueError("at least one control is required")

    # 1. Reference MFCC + codebook + reference distribution.
    ref_mfcc = extract_mfcc(
        reference_test_wav, sr=sr, n_mfcc=n_mfcc, hop_length=hop_length,
    )
    codebook = fit_codebook(ref_mfcc, n_clusters=n_clusters, seed=seed)
    reference_q = quantise_to_histogram(ref_mfcc, codebook)

    # 2. Trained substrate.
    trained_mfcc = extract_mfcc(
        trained_wav, sr=sr, n_mfcc=n_mfcc, hop_length=hop_length,
    )
    t_mean, t_std = bootstrap_kl(
        trained_mfcc, codebook, reference_q,
        n_bootstrap=n_bootstrap, seed=seed,
    )
    trained_stat = _SubstrateStat(
        name="trained", mean=t_mean, std=t_std,
        n_frames=int(trained_mfcc.shape[0]),
    )

    # 3. Each control.
    control_stats: dict[str, _SubstrateStat] = {}
    control_kl: dict[str, tuple[float, float]] = {}
    for control_name, wav_path in control_wavs.items():
        c_mfcc = extract_mfcc(
            wav_path, sr=sr, n_mfcc=n_mfcc, hop_length=hop_length,
        )
        # Each control gets its own deterministic bootstrap seed
        # (offset from the global seed) so the seeds are reproducible
        # but not identical to trained's.
        offset = (abs(hash(control_name)) % 10_000) + 1
        c_mean, c_std = bootstrap_kl(
            c_mfcc, codebook, reference_q,
            n_bootstrap=n_bootstrap, seed=int(seed) + offset,
        )
        control_stats[control_name] = _SubstrateStat(
            name=control_name, mean=c_mean, std=c_std,
            n_frames=int(c_mfcc.shape[0]),
        )
        control_kl[control_name] = (c_mean, c_std)

    # 4. Z-scores per control.
    z_scores: dict[str, float] = {}
    for name, stat in control_stats.items():
        z_scores[name] = _z_score(trained_stat, stat)

    # 5. Verdict logic per §6.
    null_against: list[str] = []
    verdict: VerdictT
    # FAIL has priority: trained statistically indistinguishable from
    # white-noise control means trained learnt nothing audio-distributional.
    z_white_noise = z_scores.get("white_noise", None)
    is_fail = z_white_noise is not None and z_white_noise <= 0.0
    if is_fail:
        verdict = "FAIL"
        for name, z in z_scores.items():
            if z < 2.0:
                null_against.append(name)
    else:
        # PASS iff every control has z >= 2 AND trained's mean is lower
        # than every control's mean (the latter is implied by z >= 2 with
        # non-negative stds, but enforce it explicitly for clarity).
        all_pass = True
        for name, z in z_scores.items():
            stat = control_stats[name]
            if z < 2.0 or trained_stat.mean >= stat.mean:
                all_pass = False
                null_against.append(name)
        verdict = "PASS" if all_pass else "NULL"

    n_frames_per_substrate = {"trained": trained_stat.n_frames}
    n_frames_per_substrate.update(
        {name: stat.n_frames for name, stat in control_stats.items()}
    )

    return EvaluationResult(
        verdict=verdict,
        null_against=null_against,
        trained_kl_mean=float(trained_stat.mean),
        trained_kl_std=float(trained_stat.std),
        control_kl={k: (float(v[0]), float(v[1])) for k, v in control_kl.items()},
        z_scores={k: float(v) for k, v in z_scores.items()},
        n_frames_per_substrate=n_frames_per_substrate,
        n_bootstrap=int(n_bootstrap),
    )


# ----------------------------------------------------------------------
# JSON helpers


def _result_to_json_dict(result: EvaluationResult) -> dict:
    """Convert ``EvaluationResult`` to a JSON-serialisable dict.

    Tuples are serialised as 2-element lists; numpy scalars in
    user-supplied paths have already been coerced to Python floats by
    :func:`evaluate`.
    """
    raw = asdict(result)
    raw["control_kl"] = {
        k: [float(v[0]), float(v[1])] for k, v in result.control_kl.items()
    }
    return raw


# ----------------------------------------------------------------------
# CLI


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m agent.evaluate_babble",
        description=(
            "Run the §6 falsifier on a trained babble wav vs three "
            "control wavs against a held-back German test-split wav."
        ),
    )
    parser.add_argument("--trained", type=Path, required=True)
    parser.add_argument("--white-noise", type=Path, required=True)
    parser.add_argument("--reversed-de", type=Path, required=True)
    parser.add_argument("--french", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--n-bootstrap", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--n-clusters", type=int, default=256)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    result = evaluate(
        trained_wav=args.trained,
        control_wavs={
            "white_noise": args.white_noise,
            "reversed_de": args.reversed_de,
            "french": args.french,
        },
        reference_test_wav=args.reference,
        n_bootstrap=args.n_bootstrap,
        seed=args.seed,
        n_clusters=args.n_clusters,
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(_result_to_json_dict(result), indent=2))


if __name__ == "__main__":
    main()
