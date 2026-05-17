"""R-7 corpus build — fetch primary_urls from corpus.training-EN.yaml,
resample each to 16 kHz mono WAV, compute sha256, write manifest.json,
and update the YAML's per-stage 'files:' list.

CLI:
    .venv/bin/python -m agent.flux.training_corpus_build \\
        --yaml corpus.training-EN.yaml \\
        --out  ~/.eqmod/training/EN

R-7 pre-registered acceptance (QUEUE.yaml):
    tests/flux/test_training_corpus_valid.py PASSES
    tests/flux/test_training_corpus_manifest.py PASSES

Module is pure-Python + ffmpeg + requests + soundfile + numpy + yaml. No
LLM, no learned model, no STFT learning — see CLAUDE.md hard constraints.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Iterable

import numpy as np
import requests
import soundfile as sf
import yaml


SAMPLE_RATE_HZ = 16_000
CHANNELS = 1
DOWNLOAD_TIMEOUT_S = 600  # per file
DOWNLOAD_RETRY = 3
USER_AGENT = "eqmod-research/1.0 (https://github.com/mkupermann/EQMOD)"

REQUIRED_STAGES = ("stage1", "stage2", "stage4_substitute")


def _have_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_basename(url: str) -> str:
    name = url.rstrip("/").rsplit("/", 1)[-1]
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name or "asset"


def _download(url: str, dest: Path, *, timeout: int = DOWNLOAD_TIMEOUT_S) -> None:
    """Stream-download `url` to `dest`. Atomic via .part rename."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    headers = {"User-Agent": USER_AGENT}
    last_err: Exception | None = None
    for attempt in range(1, DOWNLOAD_RETRY + 1):
        try:
            with requests.get(url, headers=headers, timeout=timeout, stream=True) as r:
                r.raise_for_status()
                total = 0
                with tmp.open("wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                            total += len(chunk)
                if total == 0:
                    raise RuntimeError(f"empty body from {url}")
            tmp.replace(dest)
            return
        except Exception as exc:  # network / 5xx / 4xx
            last_err = exc
            print(f"  attempt {attempt}/{DOWNLOAD_RETRY} failed: {exc}", file=sys.stderr)
            tmp.unlink(missing_ok=True)
            if attempt < DOWNLOAD_RETRY:
                time.sleep(2 * attempt)
    raise RuntimeError(f"download failed after {DOWNLOAD_RETRY} attempts: {url}") from last_err


def _ffmpeg_to_wav_16k_mono(src: Path, dest: Path) -> None:
    """Decode src (any ffmpeg-supported format) → 16 kHz mono WAV PCM 16-bit."""
    if not _have_ffmpeg():
        raise RuntimeError("ffmpeg is required on PATH for audio normalisation")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(src),
        "-vn",
        "-ac", str(CHANNELS),
        "-ar", str(SAMPLE_RATE_HZ),
        "-c:a", "pcm_s16le",
        "-f", "wav",
        "-loglevel", "error",
        str(tmp),
    ]
    subprocess.run(cmd, check=True, timeout=DOWNLOAD_TIMEOUT_S)
    if tmp.stat().st_size == 0:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"ffmpeg produced empty WAV for {src}")
    tmp.replace(dest)


def _wav_duration_seconds(path: Path) -> float:
    info = sf.info(str(path))
    if info.samplerate != SAMPLE_RATE_HZ:
        raise RuntimeError(
            f"{path}: post-ffmpeg sample_rate={info.samplerate}, expected {SAMPLE_RATE_HZ}"
        )
    if info.channels != CHANNELS:
        raise RuntimeError(
            f"{path}: post-ffmpeg channels={info.channels}, expected {CHANNELS}"
        )
    return float(info.frames) / float(info.samplerate)


def _fetch_one(url: str, stage_out: Path, *, cache_dir: Path) -> dict:
    """Fetch a single URL → 16 kHz mono WAV. Returns a manifest entry dict."""
    raw_name = _safe_basename(url)
    raw_path = cache_dir / raw_name
    if raw_path.exists() and raw_path.stat().st_size > 0:
        print(f"  cached raw: {raw_path.name} ({raw_path.stat().st_size // 1024} KB)")
    else:
        print(f"  fetching: {url}")
        _download(url, raw_path)
        print(f"    -> {raw_path.name} ({raw_path.stat().st_size // 1024} KB)")

    wav_name = Path(raw_name).stem + ".wav"
    wav_path = stage_out / wav_name
    if wav_path.exists() and wav_path.stat().st_size > 0:
        print(f"  cached wav: {wav_path.name}")
    else:
        print(f"  ffmpeg → {wav_path.name}")
        _ffmpeg_to_wav_16k_mono(raw_path, wav_path)

    duration = _wav_duration_seconds(wav_path)
    sha = _sha256(wav_path)
    print(f"    duration={duration:.1f}s  sha256={sha[:12]}...")
    return {
        "path": str(wav_path),
        "source_url": url,
        "duration_seconds": duration,
        "sha256": sha,
        "size_bytes": int(wav_path.stat().st_size),
    }


def build_corpus(yaml_path: Path, out_root: Path) -> dict:
    """Read yaml_path, fetch primary_urls per required stage, normalise,
    write WAVs under out_root/<stage>/, mutate the YAML's 'files:' list,
    and write out_root/manifest.json. Returns the manifest dict.
    """
    data = yaml.safe_load(yaml_path.read_text())
    if not isinstance(data, dict):
        raise RuntimeError(f"{yaml_path} did not parse as a YAML mapping")
    if data.get("language") != "en":
        raise RuntimeError(f"{yaml_path} language must be 'en'")
    if data.get("sample_rate_hz") != SAMPLE_RATE_HZ:
        raise RuntimeError(f"{yaml_path} sample_rate_hz must be {SAMPLE_RATE_HZ}")
    if data.get("channels") != CHANNELS:
        raise RuntimeError(f"{yaml_path} channels must be {CHANNELS}")

    out_root = Path(out_root).expanduser()
    out_root.mkdir(parents=True, exist_ok=True)
    cache_dir = out_root / "_raw_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict = {
        "language": "en",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "stages": {},
    }

    stages = data.get("stages") or {}
    for stage_key in REQUIRED_STAGES:
        stage = stages.get(stage_key)
        if not isinstance(stage, dict):
            raise RuntimeError(f"{yaml_path}: missing stage {stage_key}")
        urls: list[str] = list(stage.get("primary_urls") or [])
        if not urls:
            raise RuntimeError(f"{yaml_path}: {stage_key} has no primary_urls")
        stage_out = out_root / stage_key
        stage_out.mkdir(parents=True, exist_ok=True)
        print(f"\n=== {stage_key} ({len(urls)} urls) ===")
        entries: list[dict] = []
        for url in urls:
            entry = _fetch_one(url, stage_out, cache_dir=cache_dir)
            entries.append(entry)
        total = sum(e["duration_seconds"] for e in entries)
        min_dur = int(stage.get("duration_seconds_min") or 0)
        if total < min_dur:
            raise RuntimeError(
                f"{stage_key} total duration {total:.1f}s < required {min_dur}s — "
                f"fetch produced insufficient audio"
            )
        manifest["stages"][stage_key] = {
            "source_class": stage.get("source_class"),
            "licence": stage.get("licence"),
            "duration_seconds": total,
            "duration_seconds_min": min_dur,
            "files": entries,
        }
        # mutate YAML 'files' list in-memory
        stages[stage_key]["files"] = [
            {"path": e["path"], "source_url": e["source_url"],
             "duration_seconds": e["duration_seconds"], "sha256": e["sha256"]}
            for e in entries
        ]

    # Persist updated YAML
    data["stages"] = stages
    with yaml_path.open("w") as f:
        yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)
    print(f"\nupdated YAML: {yaml_path}")

    # Persist manifest.json
    manifest_path = out_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"wrote manifest: {manifest_path}")
    return manifest


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent.flux.training_corpus_build")
    parser.add_argument("--yaml", required=True, type=Path,
                        help="corpus.training-EN.yaml")
    parser.add_argument("--out", required=True, type=Path,
                        help="output root (e.g. ~/.eqmod/training/EN)")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not args.yaml.exists():
        print(f"YAML not found: {args.yaml}", file=sys.stderr)
        return 2

    manifest = build_corpus(args.yaml, args.out)
    print("\n--- summary ---")
    for k, v in manifest["stages"].items():
        n = len(v["files"])
        print(f"  {k}: {n} files, {v['duration_seconds']:.0f}s "
              f"(min {v['duration_seconds_min']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
