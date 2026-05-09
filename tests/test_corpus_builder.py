"""Unit tests for ``agent/corpus_builder.py``.

Tests use synthetic audio (sine waves, noise mixes) written to ``tmp_path``
as 16-bit PCM .wav files. ffmpeg on PATH is required (matches production)
but no network calls are made — yt-dlp is mocked where needed.
"""
from __future__ import annotations

import json
import shutil
import wave
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from agent import corpus_builder
from agent.corpus_builder import (
    CorpusBuilder,
    SAMPLE_RATE,
    _extract_audio_ffmpeg,
    _make_white_noise,
    _reverse,
    _rms,
    _split_80_10_10,
)


# ---------------------------------------------------------------------------
# fixtures + helpers
# ---------------------------------------------------------------------------


pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None,
    reason="ffmpeg required on PATH for corpus builder tests",
)


def _write_wav_int16(path: Path, samples: np.ndarray, sr: int, channels: int) -> None:
    """Write ``samples`` as a PCM-int16 wav file readable by ffmpeg.

    For stereo, ``samples`` must be shape (n_frames, 2) and is written
    interleaved.
    """
    if channels == 1:
        flat = samples.astype(np.int16, copy=False)
    else:
        assert samples.ndim == 2 and samples.shape[1] == channels
        flat = samples.astype(np.int16, copy=False).reshape(-1)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(flat.tobytes())


def _sine(freq_hz: float, duration_s: float, sr: int, amp: float = 0.5) -> np.ndarray:
    n = int(round(duration_s * sr))
    t = np.arange(n) / sr
    return (amp * np.sin(2 * np.pi * freq_hz * t)).astype(np.float32)


def _make_de_wav(tmp_path: Path, duration_s: float = 1.0) -> Path:
    """Make a stereo 44.1 kHz int16 wav: distinct freqs L/R so ffmpeg downmix
    has nontrivial content."""
    sr = 44100
    n = int(round(duration_s * sr))
    t = np.arange(n) / sr
    left = (0.4 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)
    right = (0.4 * np.sin(2 * np.pi * 660.0 * t)).astype(np.float32)
    stereo = np.stack([left, right], axis=1)
    int16 = (stereo * 32000).astype(np.int16)
    path = tmp_path / "de.wav"
    _write_wav_int16(path, int16, sr, channels=2)
    return path


def _make_fr_wav(tmp_path: Path, duration_s: float = 1.0) -> Path:
    """A different sine so we can verify FR != DE in tests if needed."""
    sr = 22050
    n = int(round(duration_s * sr))
    t = np.arange(n) / sr
    mono = (0.3 * np.sin(2 * np.pi * 880.0 * t)).astype(np.float32)
    int16 = (mono * 32000).astype(np.int16)
    path = tmp_path / "fr.wav"
    _write_wav_int16(path, int16, sr, channels=1)
    return path


def _builder_with_paths(de_path: Path, fr_path: Path,
                       cache_dir: Path) -> CorpusBuilder:
    """Default-shaped builder using one source per DE stage + one FR source."""
    return CorpusBuilder(
        de_stage1=[str(de_path)],
        de_stage2=[str(de_path)],
        de_stage3=[str(de_path)],
        de_stage4=[str(de_path)],
        fr_sources=[str(fr_path)],
        cache_dir=cache_dir,
        seed=42,
    )


# ---------------------------------------------------------------------------
# 1. Normalisation: 44.1 kHz stereo int16 → 16 kHz mono float32, range [-1, 1]
# ---------------------------------------------------------------------------


def test_normalisation_to_16khz_mono_float32(tmp_path):
    de_path = _make_de_wav(tmp_path, duration_s=1.0)

    audio = _extract_audio_ffmpeg(de_path, sample_rate=SAMPLE_RATE)

    if audio.size == 0:
        pytest.fail("ffmpeg returned 0 samples — normalisation produced no audio")
    if audio.dtype != np.float32:
        pytest.fail(f"expected float32 output, got {audio.dtype}")
    if audio.ndim != 1:
        pytest.fail(f"expected mono (1-D) output, got shape {audio.shape}")
    # 1 s of audio at 16 kHz ⇒ ~16000 samples (allow small ffmpeg framing slack).
    expected = SAMPLE_RATE
    if not (expected - 200 <= audio.size <= expected + 200):
        pytest.fail(
            f"expected ~{expected} samples for 1 s @ 16 kHz; got {audio.size}"
        )
    # Range [-1, 1] post-normalisation.
    if float(audio.max()) > 1.0 + 1e-6 or float(audio.min()) < -1.0 - 1e-6:
        pytest.fail(
            f"audio out of [-1, 1]: min={audio.min()} max={audio.max()}"
        )


# ---------------------------------------------------------------------------
# 2. Equal duration across all four streams
# ---------------------------------------------------------------------------


def test_equal_duration_across_streams(tmp_path):
    de_path = _make_de_wav(tmp_path, duration_s=1.0)
    fr_path = _make_fr_wav(tmp_path, duration_s=0.5)  # shorter on purpose
    cache_dir = tmp_path / "cache"
    out_dir = tmp_path / "out"

    builder = _builder_with_paths(de_path, fr_path, cache_dir)
    manifests = builder.build(out_dir)

    if len(manifests) != 4:
        pytest.fail(f"expected 4 corpora; got {sorted(manifests)}")

    n_de = sum(s["n_samples"] for s in manifests["de"]["splits"].values())
    if n_de == 0:
        pytest.fail("DE corpus has 0 samples; equal-duration check is meaningless")

    for name in ("white_noise", "reversed_de", "fr"):
        n_other = sum(s["n_samples"] for s in manifests[name]["splits"].values())
        # Spec allows ±1 sample tolerance.
        if abs(n_other - n_de) > 1:
            pytest.fail(
                f"{name} has {n_other} samples but DE has {n_de} "
                f"(>1 sample drift)"
            )


# ---------------------------------------------------------------------------
# 3. Time reversal preserves the power spectrum (per spec §8, within 1%)
# ---------------------------------------------------------------------------


def test_time_reversal_preserves_power_spectrum(tmp_path):
    rng = np.random.default_rng(0)
    # Mix of two sines + noise so the power spectrum is nontrivial.
    sr = SAMPLE_RATE
    t = np.arange(2 * sr) / sr
    audio = (
        0.4 * np.sin(2 * np.pi * 440.0 * t)
        + 0.2 * np.sin(2 * np.pi * 1320.0 * t)
        + 0.05 * rng.standard_normal(t.shape[0])
    ).astype(np.float32)

    reversed_audio = _reverse(audio)
    if reversed_audio.shape != audio.shape:
        pytest.fail("reversed audio length differs from input")

    # |FFT|^2 — magnitude squared. Reversal should leave |FFT| unchanged
    # (only the phase flips), so power spectra match within FP noise.
    P0 = np.abs(np.fft.rfft(audio.astype(np.float64))) ** 2
    P1 = np.abs(np.fft.rfft(reversed_audio.astype(np.float64))) ** 2

    denom = np.maximum(P0, 1e-12)
    rel_err = np.abs(P0 - P1) / denom
    # Spec: within 1% bin-by-bin. Median is the robust check; allow a tiny
    # tail of FP-noise outliers (10%).
    if float(np.median(rel_err)) > 0.01:
        pytest.fail(f"reversal changed median power-spectrum bin by "
                    f"{float(np.median(rel_err)):.4%} (>1%)")
    if float(np.quantile(rel_err, 0.9)) > 0.01:
        pytest.fail(f"reversal changed 90th-pct power-spectrum bin by "
                    f"{float(np.quantile(rel_err, 0.9)):.4%} (>1%)")


# ---------------------------------------------------------------------------
# 4. White-noise control RMS-matched to trained corpus (within 5%)
# ---------------------------------------------------------------------------


def test_white_noise_rms_matched():
    rng = np.random.default_rng(123)
    # Trained-corpus stand-in: a chirp with known RMS.
    sr = SAMPLE_RATE
    t = np.arange(3 * sr) / sr
    de = (0.3 * np.sin(2 * np.pi * (200.0 + 50.0 * t) * t)).astype(np.float32)
    target_rms = _rms(de)
    if target_rms <= 0.0:
        pytest.fail("synthetic DE RMS is 0 — fixture broken")

    noise = _make_white_noise(de.shape[0], target_rms, rng)
    if noise.shape[0] != de.shape[0]:
        pytest.fail(
            f"noise length {noise.shape[0]} != DE length {de.shape[0]}"
        )
    noise_rms = _rms(noise)
    if noise_rms <= 0.0:
        pytest.fail("white-noise RMS is 0; matching failed")

    rel = abs(noise_rms - target_rms) / target_rms
    if rel > 0.05:
        pytest.fail(
            f"white-noise RMS {noise_rms:.6f} differs from target "
            f"{target_rms:.6f} by {rel:.2%} (>5%)"
        )


# ---------------------------------------------------------------------------
# 5. 80/10/10 split: contiguous, sums to total
# ---------------------------------------------------------------------------


def test_split_80_10_10():
    n = 1000
    audio = np.arange(n, dtype=np.float32)  # [0, 1, 2, ..., n-1]

    train, dev, test = _split_80_10_10(audio)

    total = train.shape[0] + dev.shape[0] + test.shape[0]
    if total != n:
        pytest.fail(f"sizes sum to {total}, expected {n}")

    # Contiguous: identity values come straight from the input.
    if not np.array_equal(train, audio[:800]):
        pytest.fail("train split is not contiguous slice [0:800)")
    if not np.array_equal(dev, audio[800:900]):
        pytest.fail("dev split is not contiguous slice [800:900)")
    if not np.array_equal(test, audio[900:]):
        pytest.fail("test split is not contiguous slice [900:)")
    if train.shape[0] != 800 or dev.shape[0] != 100 or test.shape[0] != 100:
        pytest.fail(
            f"split sizes wrong: {train.shape[0]}/{dev.shape[0]}/{test.shape[0]}, "
            f"expected 800/100/100"
        )


# ---------------------------------------------------------------------------
# 6. manifest.json: sample_rate, duration, n_samples; values match files
# ---------------------------------------------------------------------------


def test_manifest_json_correct(tmp_path):
    de_path = _make_de_wav(tmp_path, duration_s=1.0)
    fr_path = _make_fr_wav(tmp_path, duration_s=1.0)
    cache_dir = tmp_path / "cache"
    out_dir = tmp_path / "out"

    builder = _builder_with_paths(de_path, fr_path, cache_dir)
    builder.build(out_dir)

    for name in corpus_builder.CORPUS_NAMES:
        manifest_path = out_dir / name / "manifest.json"
        if not manifest_path.is_file():
            pytest.fail(f"manifest.json missing for corpus {name}")
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("sample_rate") != SAMPLE_RATE:
            pytest.fail(
                f"{name}: sample_rate={manifest.get('sample_rate')} != {SAMPLE_RATE}"
            )
        for split_name in ("train", "dev", "test"):
            split = manifest["splits"].get(split_name)
            if split is None:
                pytest.fail(f"{name}: split '{split_name}' missing from manifest")
            raw_path = out_dir / name / split["path"]
            if not raw_path.is_file():
                pytest.fail(f"{name}: raw file missing at {raw_path}")
            # File size in bytes / 4 (float32) must equal n_samples.
            n_from_file = raw_path.stat().st_size // 4
            if n_from_file != split["n_samples"]:
                pytest.fail(
                    f"{name}/{split_name}: file has {n_from_file} samples, "
                    f"manifest says {split['n_samples']}"
                )
            expected_duration = split["n_samples"] / SAMPLE_RATE
            if abs(split["duration_seconds"] - expected_duration) > 1e-6:
                pytest.fail(
                    f"{name}/{split_name}: duration_seconds inconsistent "
                    f"with n_samples/sample_rate"
                )


# ---------------------------------------------------------------------------
# 7. Local path input does NOT invoke yt-dlp
# ---------------------------------------------------------------------------


def test_local_path_input_skips_download(tmp_path):
    de_path = _make_de_wav(tmp_path, duration_s=0.5)
    fr_path = _make_fr_wav(tmp_path, duration_s=0.5)
    cache_dir = tmp_path / "cache"
    out_dir = tmp_path / "out"

    builder = _builder_with_paths(de_path, fr_path, cache_dir)

    # Patch the module-level download helper. If any local path is mistaken
    # for a URL, the patched callable will be invoked and the test fails.
    with patch.object(corpus_builder, "_download_url",
                      side_effect=AssertionError("yt-dlp must not be invoked for local paths")) as mock_dl:
        builder.build(out_dir)
        if mock_dl.called:
            pytest.fail(
                f"_download_url was called {mock_dl.call_count} times for "
                f"local-path inputs"
            )
