"""Corpus builder for the predictive-babble pipeline.

Pipeline (per spec §3, row `agent/corpus_builder.py`, plus the
2026-05-10 follow-up that added per-stage outputs so the curriculum
actually exposes the trained substrate to a different audio source per
stage):

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
     * time-reversed-DE — reversed sample-wise (per stage)
     * French — built from a separate French source list, same pipeline.

5. Split each of the four corpora 80 / 10 / 10 train / dev / test. The
   train split is built CONTIGUOUSLY *within each stage* and the
   per-stage 80% chunks are concatenated to form the full ``train``
   file. dev and test follow the same pattern. Per-stage train files
   are also written so the curriculum scheduler can advance the feeder
   onto a different audio source per stage.
6. Write outputs::

     {out_dir}/{name}/train.f32.raw          # concatenated 80% chunks
     {out_dir}/{name}/dev.f32.raw            # concatenated 10% chunks
     {out_dir}/{name}/test.f32.raw           # concatenated 10% chunks
     {out_dir}/{name}/stage1_train.f32.raw   # stage 1 80% chunk
     {out_dir}/{name}/stage2_train.f32.raw   # stage 2 80% chunk
     {out_dir}/{name}/stage3_train.f32.raw   # stage 3 80% chunk
     {out_dir}/{name}/stage4_train.f32.raw   # stage 4 80% chunk
     {out_dir}/{name}/manifest.json          # sample_rate, splits + per-stage metadata

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


def _split_per_stage(stage_arrays: list[np.ndarray]) -> tuple[
    list[np.ndarray], list[np.ndarray], list[np.ndarray]
]:
    """Apply ``_split_80_10_10`` to each stage independently.

    Returns three parallel lists ``(stage_trains, stage_devs, stage_tests)``
    so callers can both write per-stage files and concatenate to form
    the full splits without re-splitting the catenation.
    """
    stage_trains: list[np.ndarray] = []
    stage_devs: list[np.ndarray] = []
    stage_tests: list[np.ndarray] = []
    for stage_audio in stage_arrays:
        train, dev, test = _split_80_10_10(stage_audio)
        stage_trains.append(train)
        stage_devs.append(dev)
        stage_tests.append(test)
    return stage_trains, stage_devs, stage_tests


def _concat_or_empty(arrays: list[np.ndarray]) -> np.ndarray:
    """Concatenate non-empty arrays; return zero-length f32 if all empty."""
    arrays = [a for a in arrays if a.size > 0]
    if not arrays:
        return np.zeros(0, dtype=np.float32)
    return np.concatenate(arrays).astype(np.float32, copy=False)


def _split_into_chunks(
    audio: np.ndarray, lengths: list[int],
) -> list[np.ndarray]:
    """Carve ``audio`` into contiguous chunks of the requested lengths.

    The total of ``lengths`` must equal ``audio.size`` exactly. If a
    rounding mismatch sneaks in we adjust the final chunk by ±1 sample
    so the invariant ``sum(out_lengths) == audio.size`` always holds.
    """
    total = int(audio.size)
    target = int(sum(lengths))
    # Round-tripped lengths can drift by ±1 vs the source after
    # arithmetic in the caller; absorb that drift in the last chunk so
    # the invariant holds exactly without throwing.
    if target != total and lengths:
        lengths = list(lengths)
        lengths[-1] += (total - target)
    chunks: list[np.ndarray] = []
    cursor = 0
    for L in lengths:
        L_int = max(0, int(L))
        end = cursor + L_int
        chunks.append(audio[cursor:end].astype(np.float32, copy=False))
        cursor = end
    return chunks


def _write_split(
    name: str,
    audio: np.ndarray,
    out_dir: Path,
    sample_rate: int = SAMPLE_RATE,
    *,
    stage_trains: list[np.ndarray] | None = None,
    stage_devs: list[np.ndarray] | None = None,
    stage_tests: list[np.ndarray] | None = None,
    fr_per_stage_note: str | None = None,
) -> dict:
    """Write train/dev/test + per-stage train files + manifest.

    The full ``train.f32.raw`` is the concatenation of per-stage 80%
    chunks; ``dev.f32.raw`` and ``test.f32.raw`` are the corresponding
    10% chunk concatenations. When ``stage_trains`` is supplied (the
    new code path), per-stage files are also written and the manifest
    grows a ``stages`` array describing each stage's n_samples and
    duration_seconds.

    ``stage_trains`` is the source of truth for the full train file
    when supplied — passing it preserves the per-stage structure across
    the concatenation, which would otherwise be invisible to the
    caller.
    """
    target = out_dir / name
    target.mkdir(parents=True, exist_ok=True)

    # Build the full splits. If per-stage chunks are supplied use them
    # to preserve the contiguous-within-stage invariant; otherwise fall
    # back to a global 80/10/10 split for backwards compatibility.
    if stage_trains is not None and stage_devs is not None and stage_tests is not None:
        train = _concat_or_empty(stage_trains)
        dev = _concat_or_empty(stage_devs)
        test = _concat_or_empty(stage_tests)
    else:
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

    # Per-stage train files + manifest entries.
    if stage_trains is not None:
        stages_meta: list[dict] = []
        for i, stage_train in enumerate(stage_trains, start=1):
            stage_name = f"stage{i}"
            file_name = f"{stage_name}_train.f32.raw"
            stage_train_f32 = stage_train.astype(np.float32, copy=False)
            stage_train_f32.tofile(target / file_name)
            stages_meta.append({
                "name": stage_name,
                "path": file_name,
                "n_samples": int(stage_train_f32.shape[0]),
                "duration_seconds": float(stage_train_f32.shape[0] / sample_rate),
            })
        manifest["stages"] = stages_meta

    if fr_per_stage_note is not None:
        manifest["per_stage_note"] = fr_per_stage_note

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

    def build_trained_de_per_stage(self) -> list[np.ndarray]:
        """Ingest each DE stage independently.

        Returns a list of four numpy arrays, one per curriculum stage.
        Empty stages produce zero-length arrays — callers must filter
        if they want to enforce non-emptiness.
        """
        stages = [
            self.de_stage1,
            self.de_stage2,
            self.de_stage3,
            self.de_stage4,
        ]
        return [
            _ingest_sources(stage, self.cache_dir, self.sample_rate)
            for stage in stages
        ]

    def build_trained_de(self) -> np.ndarray:
        """Concatenate the four stages of trained-DE audio."""
        chunks = self.build_trained_de_per_stage()
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

        Per-stage outputs (the 2026-05-10 follow-up):

        * Trained DE: each stage is ingested independently, split 80/10/10
          *within that stage* (contiguously), and the per-stage 80% chunk
          is written as ``stage{i}_train.f32.raw``. The full ``train``
          file is the concatenation of those per-stage chunks.
        * White-noise control: the per-stage train files match the DE
          per-stage train durations exactly (sample-for-sample), so the
          curriculum scheduler can advance at matched wall-clock.
        * Reversed-DE control: each stage is reversed independently
          (``stage{i}_train`` of reversed_de is ``reverse(stage{i}_train`` of
          trained DE), so the temporal structure of each stage's reversal
          maps back onto the same stage in the curriculum.
        * French control: per-stage FR sourcing is not realistic without a
          richer YAML (FR is a single flat list in the spec). For v1 we
          divide the FR audio into four contiguous chunks of durations
          matching the trained DE per-stage train durations. The manifest
          records this explicitly via ``per_stage_note``.
        """
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        # 1. Ingest DE per-stage.
        de_stages = self.build_trained_de_per_stage()
        de = _concat_or_empty(de_stages)
        n = de.shape[0]
        if n == 0:
            raise RuntimeError(
                "Trained-DE corpus is empty; check that DE source lists "
                "resolved to readable audio."
            )

        # 2. Per-stage 80/10/10 splits for the trained corpus. Each
        # stage's per-stage train file is the 80% slice of *that*
        # stage's audio, contiguous within the stage — preserves
        # prosodic continuity within the stage as the spec demands.
        de_stage_trains, de_stage_devs, de_stage_tests = (
            _split_per_stage(de_stages)
        )
        per_stage_train_lengths = [int(a.size) for a in de_stage_trains]

        # 3. RMS-matched white noise — generated with the *trained
        # corpus's* per-stage train durations so per-stage files match
        # sample-for-sample. The full white-noise stream stays the same
        # global length as DE for backwards compat with consumers that
        # only use the full ``train.f32.raw``.
        rng = np.random.default_rng(self.seed)
        target_rms = _rms(de)
        white = _make_white_noise(n, target_rms, rng)
        # Independent per-stage RNG draws (deterministic on self.seed)
        # ensure each per-stage white-noise file is itself white noise,
        # not just a slice of the global stream — slicing would still
        # be valid noise but the per-stage structure would be invisible.
        white_stage_trains: list[np.ndarray] = []
        white_stage_devs: list[np.ndarray] = []
        white_stage_tests: list[np.ndarray] = []
        for i, _train in enumerate(de_stage_trains):
            stage_n = int(de_stages[i].size)
            stage_rms_target = (
                _rms(de_stages[i]) if de_stages[i].size > 0 else target_rms
            )
            stage_rng = np.random.default_rng(self.seed + 1 + i)
            stage_noise = _make_white_noise(
                stage_n, stage_rms_target, stage_rng,
            )
            wt, wd, ws = _split_80_10_10(stage_noise)
            white_stage_trains.append(wt)
            white_stage_devs.append(wd)
            white_stage_tests.append(ws)

        # 4. Reversed-DE per stage. The spec is explicit:
        # reversed_de/stage{i}_train.f32.raw == reverse(de/stage{i}_train.f32.raw)
        # i.e. the stage's *train* slice reversed. We also reverse the
        # dev and test slices per stage so dev/test of the reversed
        # control still come from the right stage's audio.
        rev_stage_trains: list[np.ndarray] = [
            _reverse(t) for t in de_stage_trains
        ]
        rev_stage_devs: list[np.ndarray] = [
            _reverse(d) for d in de_stage_devs
        ]
        rev_stage_tests: list[np.ndarray] = [
            _reverse(t) for t in de_stage_tests
        ]
        # The full reversed_de stream is *not* simply reverse(de) any more
        # — it is the concatenation of the per-stage reversals (so the
        # full file's substring structure aligns with the per-stage files).
        reversed_de = _concat_or_empty(
            rev_stage_trains + rev_stage_devs + rev_stage_tests
        )
        # Defensive: total length must still equal n.
        if reversed_de.size != n:
            # Fall back to the global reversal so the equal-duration
            # invariant holds; per-stage reversals are still written.
            reversed_de = _reverse(de)

        # 5. French per stage — spec note: per-stage FR sourcing not
        # realistic without a richer YAML. For v1 we split FR into four
        # contiguous chunks matching trained DE per-stage durations.
        fr = self.build_french(n)
        # Per-stage FR chunks: cut to match trained DE per-stage total
        # duration (train + dev + test). Within each per-stage FR chunk,
        # apply 80/10/10 contiguous split.
        per_stage_fr_total_lengths = [int(a.size) for a in de_stages]
        fr_stage_chunks = _split_into_chunks(fr, per_stage_fr_total_lengths)
        fr_stage_trains: list[np.ndarray] = []
        fr_stage_devs: list[np.ndarray] = []
        fr_stage_tests: list[np.ndarray] = []
        for chunk in fr_stage_chunks:
            ft, fd, fs = _split_80_10_10(chunk)
            fr_stage_trains.append(ft)
            fr_stage_devs.append(fd)
            fr_stage_tests.append(fs)

        # Defensive: every full stream must equal n samples exactly.
        for label, arr in [
            ("white_noise", white),
            ("reversed_de", reversed_de),
            ("fr", fr),
        ]:
            if arr.shape[0] != n:
                raise RuntimeError(
                    f"control '{label}' has length {arr.shape[0]} != "
                    f"trained-DE length {n}; equal-duration invariant broken."
                )

        manifests: dict[str, dict] = {}
        manifests["de"] = _write_split(
            "de", de, out_dir, self.sample_rate,
            stage_trains=de_stage_trains,
            stage_devs=de_stage_devs,
            stage_tests=de_stage_tests,
        )
        manifests["white_noise"] = _write_split(
            "white_noise", white, out_dir, self.sample_rate,
            stage_trains=white_stage_trains,
            stage_devs=white_stage_devs,
            stage_tests=white_stage_tests,
        )
        manifests["reversed_de"] = _write_split(
            "reversed_de", reversed_de, out_dir, self.sample_rate,
            stage_trains=rev_stage_trains,
            stage_devs=rev_stage_devs,
            stage_tests=rev_stage_tests,
        )
        manifests["fr"] = _write_split(
            "fr", fr, out_dir, self.sample_rate,
            stage_trains=fr_stage_trains,
            stage_devs=fr_stage_devs,
            stage_tests=fr_stage_tests,
            fr_per_stage_note=(
                "FR per-stage chunks are contiguous slices of the flat "
                "fr.sources list, sized to match trained DE per-stage "
                "total durations. Per-stage FR sourcing would need a "
                "richer YAML schema (fr.stage1..stage4)."
            ),
        )

        # Cross-substrate per-stage train length invariant: white_noise,
        # reversed_de and fr per-stage train lengths must match DE's
        # within ±1 sample (rounding tolerance from arithmetic above).
        for name, stage_trains in [
            ("white_noise", white_stage_trains),
            ("reversed_de", rev_stage_trains),
            ("fr", fr_stage_trains),
        ]:
            for i, target_len in enumerate(per_stage_train_lengths):
                got = int(stage_trains[i].size)
                if abs(got - target_len) > 1:
                    raise RuntimeError(
                        f"control '{name}' stage{i + 1} train length "
                        f"{got} != trained DE stage{i + 1} train length "
                        f"{target_len} (>1 sample drift)"
                    )
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
