"""Corpus builder for the predictive-babble pipeline.

Pipeline (per spec §3, row `agent/corpus_builder.py`):

1. Accept four input source lists for the trained-DE substrate (one per
   curriculum stage): audiobooks, single YouTuber, multi-speaker podcasts,
   webcam recording. Each list element is either a URL (downloaded via
   yt-dlp) or a local path (used as-is).
2. Extract audio with ffmpeg, normalised to 16 kHz mono float32 PCM, in the
   range [-1, 1]. Same ffmpeg invocation as
   ``agent.youtube_feeder.YouTubeFeeder._extract_audio``.
3. Concatenate per-stage audio into one numpy array per stage; the trained
   DE corpus is the concatenation of all four stages.
4. Build three control streams of equal total duration to the trained DE
   corpus:

     * white-noise — RMS-matched
     * time-reversed-DE — reversed sample-wise
     * French — built from a separate French source list, same pipeline.

5. Split each of the four corpora 80 / 10 / 10 train / dev / test.
   Splits are CONTIGUOUS (no shuffling) — preserves prosodic continuity
   within each split as the spec demands.
6. Write outputs::

     {out_dir}/{name}/train.f32.raw
     {out_dir}/{name}/dev.f32.raw
     {out_dir}/{name}/test.f32.raw
     {out_dir}/{name}/manifest.json   # sample_rate, duration_seconds, n_samples per split

CLI::

    python -m agent.corpus_builder --config corpus.yaml --out ~/.eqmod/babble/corpus/

The YAML config has shape::

    de:
      stage1: [url-or-path, ...]
      stage2: [url-or-path, ...]
      stage3: [url-or-path, ...]
      stage4: [path-to-webcam-recording]
    fr:
      sources: [url-or-path, ...]
    seed: 0
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

import numpy as np

SAMPLE_RATE = 16000
"""Target sample rate for every output stream (Hz)."""

CORPUS_NAMES = ("de", "white_noise", "reversed_de", "fr")


# ---------------------------------------------------------------------------
# Helpers (module level so tests can monkey-patch them)
# ---------------------------------------------------------------------------


def _have_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def _looks_like_url(s: str) -> bool:
    s = s.strip().lower()
    return s.startswith(("http://", "https://", "www.", "youtu.be/", "youtube.com/"))


def _download_url(url: str, cache_dir: Path) -> Path:
    """Download ``url`` via yt-dlp (lazy import) and return the local path.

    Used only when the source is a URL — local paths bypass this entirely.
    """
    import yt_dlp  # lazy: tests with only local files never import yt-dlp

    cache_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(cache_dir / "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = Path(info["requested_downloads"][0]["filepath"])
    return path


def _extract_audio_ffmpeg(src_path: Path, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Run ffmpeg to produce 16 kHz mono float32 PCM as a numpy array.

    Mirrors ``agent.youtube_feeder.YouTubeFeeder._extract_audio`` (-ac 1
    -ar 16000 -f f32le). Output values are in the range produced by
    ffmpeg's f32le encoding, i.e. roughly [-1, 1] for non-clipping
    sources.
    """
    if not _have_ffmpeg():
        raise RuntimeError(
            "ffmpeg is required on PATH for audio extraction. "
            "macOS: brew install ffmpeg. Linux: apt install ffmpeg."
        )
    with tempfile.NamedTemporaryFile(suffix=".f32.raw", delete=False) as tmp:
        out_path = Path(tmp.name)
    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(src_path),
            "-ac", "1",
            "-ar", str(sample_rate),
            "-f", "f32le",
            "-loglevel", "error",
            str(out_path),
        ]
        subprocess.run(cmd, check=True)
        data = np.fromfile(out_path, dtype=np.float32)
    finally:
        try:
            out_path.unlink()
        except FileNotFoundError:
            pass
    if data.size == 0:
        raise RuntimeError(f"ffmpeg produced empty audio from {src_path}")
    # Defensive clip — ffmpeg can occasionally emit slightly out-of-range
    # samples on lossy decode boundaries.
    return np.clip(data, -1.0, 1.0).astype(np.float32, copy=False)


def _resolve_source(source: str, cache_dir: Path) -> Path:
    """Return a local file path for ``source``: download if URL, else cast."""
    if _looks_like_url(source):
        return _download_url(source, cache_dir)
    p = Path(source)
    if not p.exists():
        raise FileNotFoundError(f"source not found: {source}")
    return p


def _ingest_sources(sources: Iterable[str], cache_dir: Path,
                    sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Resolve each source to a local file, run ffmpeg, concatenate."""
    chunks: list[np.ndarray] = []
    for src in sources:
        local = _resolve_source(src, cache_dir)
        chunks.append(_extract_audio_ffmpeg(local, sample_rate))
    if not chunks:
        return np.zeros(0, dtype=np.float32)
    return np.concatenate(chunks).astype(np.float32, copy=False)


# ---------------------------------------------------------------------------
# Stream builders (control corpora)
# ---------------------------------------------------------------------------


def _rms(x: np.ndarray) -> float:
    if x.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(x, dtype=np.float64))))


def _make_white_noise(n: int, target_rms: float, rng: np.random.Generator) -> np.ndarray:
    """RMS-matched standard-normal noise of length ``n``."""
    if n <= 0:
        return np.zeros(0, dtype=np.float32)
    raw = rng.standard_normal(n).astype(np.float32)
    raw_rms = _rms(raw)
    if raw_rms == 0.0:
        return raw
    scaled = raw * (target_rms / raw_rms)
    # Numerical safety against rare tail draws clipping the [-1, 1] window.
    scaled = np.clip(scaled, -1.0, 1.0)
    return scaled.astype(np.float32, copy=False)


def _reverse(audio: np.ndarray) -> np.ndarray:
    return audio[::-1].copy()


def _split_80_10_10(audio: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Contiguous 80/10/10 split. Sum-of-sizes == len(audio)."""
    n = audio.shape[0]
    n_train = (n * 80) // 100
    n_dev = (n * 10) // 100
    # Test gets the remainder so sizes always sum to n exactly.
    train = audio[:n_train]
    dev = audio[n_train:n_train + n_dev]
    test = audio[n_train + n_dev:]
    return train, dev, test


def _write_split(name: str, audio: np.ndarray, out_dir: Path,
                 sample_rate: int = SAMPLE_RATE) -> dict:
    """Write train/dev/test + manifest. Return the manifest dict."""
    target = out_dir / name
    target.mkdir(parents=True, exist_ok=True)
    train, dev, test = _split_80_10_10(audio)
    splits = {"train": train, "dev": dev, "test": test}
    manifest: dict = {
        "name": name,
        "sample_rate": sample_rate,
        "splits": {},
    }
    for split_name, arr in splits.items():
        path = target / f"{split_name}.f32.raw"
        arr_f32 = arr.astype(np.float32, copy=False)
        arr_f32.tofile(path)
        manifest["splits"][split_name] = {
            "path": path.name,
            "n_samples": int(arr_f32.shape[0]),
            "duration_seconds": float(arr_f32.shape[0] / sample_rate),
        }
    manifest_path = target / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return manifest


# ---------------------------------------------------------------------------
# Public class
# ---------------------------------------------------------------------------


@dataclass
class CorpusBuilder:
    """Build the four-corpus dataset for the predictive-babble experiment.

    Attributes
    ----------
    de_stage1, de_stage2, de_stage3, de_stage4 :
        Source lists per curriculum stage. Each element is either a URL
        (downloaded via yt-dlp) or a local file path.
    fr_sources :
        French source list — single bucket, same total duration as DE.
    sample_rate :
        Target sample rate. Defaults to 16 kHz per spec.
    seed :
        Seed for the white-noise RNG. Reproducible across runs.
    cache_dir :
        Where yt-dlp drops downloaded media. Defaults to a tempdir.
    """

    de_stage1: list[str] = field(default_factory=list)
    de_stage2: list[str] = field(default_factory=list)
    de_stage3: list[str] = field(default_factory=list)
    de_stage4: list[str] = field(default_factory=list)
    fr_sources: list[str] = field(default_factory=list)
    sample_rate: int = SAMPLE_RATE
    seed: int = 0
    cache_dir: Optional[Path] = None

    def __post_init__(self) -> None:
        if self.cache_dir is None:
            self.cache_dir = Path(tempfile.gettempdir()) / "eqmod-corpus-cache"
        self.cache_dir = Path(self.cache_dir)

    # ---- ingestion ------------------------------------------------------

    def build_trained_de(self) -> np.ndarray:
        """Concatenate the four stages of trained-DE audio."""
        stages = [
            self.de_stage1,
            self.de_stage2,
            self.de_stage3,
            self.de_stage4,
        ]
        chunks = [
            _ingest_sources(stage, self.cache_dir, self.sample_rate)
            for stage in stages
        ]
        if all(c.size == 0 for c in chunks):
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(chunks).astype(np.float32, copy=False)

    def build_french(self, n_samples: int) -> np.ndarray:
        """Build the French control. Truncate or pad-by-repeat to ``n_samples``."""
        fr = _ingest_sources(self.fr_sources, self.cache_dir, self.sample_rate)
        if n_samples <= 0:
            return np.zeros(0, dtype=np.float32)
        if fr.size == 0:
            raise RuntimeError(
                "French sources produced empty audio; cannot build FR control."
            )
        if fr.size >= n_samples:
            return fr[:n_samples].astype(np.float32, copy=False)
        # Shorter than the DE corpus: tile, then trim. The control needs to
        # match duration exactly so KL-divergence is comparable.
        reps = int(np.ceil(n_samples / fr.size))
        tiled = np.tile(fr, reps)[:n_samples]
        return tiled.astype(np.float32, copy=False)

    # ---- top-level ------------------------------------------------------

    def build(self, out_dir: Path) -> dict[str, dict]:
        """Build all four corpora and write splits + manifests under ``out_dir``.

        Returns a dict of ``{corpus_name: manifest_dict}``.
        """
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        de = self.build_trained_de()
        n = de.shape[0]
        if n == 0:
            raise RuntimeError(
                "Trained-DE corpus is empty; check that DE source lists "
                "resolved to readable audio."
            )

        rng = np.random.default_rng(self.seed)
        target_rms = _rms(de)
        white = _make_white_noise(n, target_rms, rng)
        reversed_de = _reverse(de)
        fr = self.build_french(n)

        # Defensive: every corpus must equal n samples exactly.
        for label, arr in [("white_noise", white), ("reversed_de", reversed_de), ("fr", fr)]:
            if arr.shape[0] != n:
                raise RuntimeError(
                    f"control '{label}' has length {arr.shape[0]} != "
                    f"trained-DE length {n}; equal-duration invariant broken."
                )

        manifests: dict[str, dict] = {}
        for name, arr in [
            ("de", de),
            ("white_noise", white),
            ("reversed_de", reversed_de),
            ("fr", fr),
        ]:
            manifests[name] = _write_split(name, arr, out_dir, self.sample_rate)
        return manifests


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _load_yaml_config(path: Path) -> dict:
    """Load YAML config without taking on a hard PyYAML dependency.

    Falls back to a minimal parser only if PyYAML isn't available — the
    expected runtime install ships PyYAML transitively. For tests we
    construct the builder directly, so the fallback is rarely hit.
    """
    text = path.read_text()
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text) or {}
    except ImportError as exc:  # pragma: no cover — env-dependent
        raise RuntimeError(
            "PyYAML is required for --config. Install with: uv pip install pyyaml"
        ) from exc


def _builder_from_config(cfg: dict) -> CorpusBuilder:
    de = cfg.get("de", {}) or {}
    fr = cfg.get("fr", {}) or {}
    return CorpusBuilder(
        de_stage1=list(de.get("stage1", []) or []),
        de_stage2=list(de.get("stage2", []) or []),
        de_stage3=list(de.get("stage3", []) or []),
        de_stage4=list(de.get("stage4", []) or []),
        fr_sources=list(fr.get("sources", []) or []),
        seed=int(cfg.get("seed", 0)),
    )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="agent.corpus_builder")
    parser.add_argument("--config", required=True, type=Path,
                        help="YAML config with de.stage{1,2,3,4} and fr.sources lists.")
    parser.add_argument("--out", required=True, type=Path,
                        help="Output directory for the four corpora.")
    args = parser.parse_args(argv)

    cfg = _load_yaml_config(args.config)
    builder = _builder_from_config(cfg)
    manifests = builder.build(args.out)
    print(json.dumps({name: m["splits"] for name, m in manifests.items()}, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
