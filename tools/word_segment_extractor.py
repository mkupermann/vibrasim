"""Energy-based word-segment extractor for EN audio corpus.

Pre-LLM-compatible: uses only raw acoustic features (RMS energy, FFT
magnitude), no pretrained models, no transcription.

Pipeline:
  1. Load WAV file at 16kHz
  2. Compute frame-wise RMS energy (10ms hop)
  3. VAD: voiced = RMS > silence_threshold (adaptive)
  4. Find contiguous voiced segments separated by ≥50ms silence
  5. Filter: keep segments with duration ∈ [80ms, 500ms] (single-word candidates)
  6. Extract FFT-magnitude signature per segment (16 log-bands)
  7. Save segments + metadata to disk

Output (per WAV file):
  <out_dir>/segments/<base>_<seg_idx>.wav  — extracted segment audio
  <out_dir>/index.json                     — per-segment metadata (start, dur, fft_sig, file_hash)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


SAMPLE_RATE_HZ = 16000
FRAME_HOP_MS = 10
FRAME_LEN_MS = 25
SILENCE_THRESHOLD_PERCENTILE = 30   # bottom 30% of frame energies = silence
MIN_VOICED_DURATION_MS = 80
MAX_VOICED_DURATION_MS = 500
MIN_GAP_MS = 50
FFT_BANDS = 16


def _load_wav_16k(path: Path) -> np.ndarray:
    """Load a WAV at 16kHz mono. Uses wave module (stdlib) to avoid deps."""
    import wave
    with wave.open(str(path), 'rb') as wf:
        n_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)
    if sample_width == 2:
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif sample_width == 4:
        x = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        raise RuntimeError(f"unsupported sample_width {sample_width}")
    if n_channels > 1:
        x = x.reshape(-1, n_channels).mean(axis=1)
    if framerate != SAMPLE_RATE_HZ:
        # simple linear resample
        new_n = int(len(x) * SAMPLE_RATE_HZ / framerate)
        idx = np.linspace(0, len(x) - 1, new_n).astype(int)
        x = x[idx]
    return x


def _frame_rms(audio: np.ndarray) -> np.ndarray:
    hop = int(SAMPLE_RATE_HZ * FRAME_HOP_MS / 1000)
    win = int(SAMPLE_RATE_HZ * FRAME_LEN_MS / 1000)
    n_frames = (len(audio) - win) // hop + 1
    rms = np.empty(n_frames, dtype=np.float32)
    for i in range(n_frames):
        s = i * hop
        rms[i] = float(np.sqrt(np.mean(audio[s:s+win] ** 2)))
    return rms


def _find_voiced_segments(rms: np.ndarray, threshold: float) -> list[tuple[int, int]]:
    """Return list of (start_frame, end_frame) for voiced segments."""
    voiced = rms > threshold
    segments = []
    start = None
    for i, v in enumerate(voiced):
        if v and start is None:
            start = i
        elif not v and start is not None:
            segments.append((start, i))
            start = None
    if start is not None:
        segments.append((start, len(voiced)))
    return segments


def _merge_close_segments(segments: list[tuple[int, int]],
                          min_gap_frames: int) -> list[tuple[int, int]]:
    """Merge segments separated by less than min_gap_frames."""
    if not segments:
        return []
    merged = [segments[0]]
    for s, e in segments[1:]:
        if s - merged[-1][1] < min_gap_frames:
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))
    return merged


def _fft_signature(audio: np.ndarray, n_bands: int = FFT_BANDS) -> np.ndarray:
    mag = np.abs(np.fft.rfft(audio))
    if mag.size <= n_bands:
        return mag
    edges = np.linspace(0, mag.size, n_bands + 1, dtype=int)
    bands = np.array([
        float(np.mean(mag[edges[i]:edges[i+1]])) for i in range(n_bands)
    ])
    # log + normalize
    bands = np.log1p(bands)
    if bands.max() > 0:
        bands = bands / bands.max()
    return bands.astype(np.float32)


def _save_wav(audio: np.ndarray, path: Path):
    import wave
    path.parent.mkdir(parents=True, exist_ok=True)
    x16 = np.clip(audio * 32767, -32768, 32767).astype(np.int16)
    with wave.open(str(path), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE_HZ)
        wf.writeframes(x16.tobytes())


def process_wav(wav_path: Path, out_dir: Path) -> list[dict]:
    audio = _load_wav_16k(wav_path)
    rms = _frame_rms(audio)
    threshold = float(np.percentile(rms, SILENCE_THRESHOLD_PERCENTILE))
    raw_segments = _find_voiced_segments(rms, threshold)
    min_gap_frames = max(1, MIN_GAP_MS // FRAME_HOP_MS)
    merged = _merge_close_segments(raw_segments, min_gap_frames)

    hop = int(SAMPLE_RATE_HZ * FRAME_HOP_MS / 1000)
    min_voiced_frames = MIN_VOICED_DURATION_MS // FRAME_HOP_MS
    max_voiced_frames = MAX_VOICED_DURATION_MS // FRAME_HOP_MS

    base = wav_path.stem
    segments_dir = out_dir / "segments"

    results = []
    for seg_idx, (sf, ef) in enumerate(merged):
        duration_frames = ef - sf
        if duration_frames < min_voiced_frames or duration_frames > max_voiced_frames:
            continue
        start_sample = sf * hop
        end_sample = ef * hop
        seg_audio = audio[start_sample:end_sample]
        if seg_audio.size == 0:
            continue
        sig = _fft_signature(seg_audio)
        rms_value = float(np.sqrt(np.mean(seg_audio ** 2)))
        seg_path = segments_dir / f"{base}_seg{seg_idx:05d}.wav"
        _save_wav(seg_audio, seg_path)
        results.append({
            "source_file": str(wav_path),
            "source_base": base,
            "seg_idx": seg_idx,
            "start_seconds": start_sample / SAMPLE_RATE_HZ,
            "duration_seconds": (end_sample - start_sample) / SAMPLE_RATE_HZ,
            "rms": rms_value,
            "fft_signature": sig.tolist(),
            "segment_path": str(seg_path),
            "label": None,
        })
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, type=Path,
                    help="Path to EN training manifest")
    ap.add_argument("--out_dir", required=True, type=Path,
                    help="Output directory (segments + index.json)")
    ap.add_argument("--max_files", type=int, default=None,
                    help="Process at most this many source files")
    args = ap.parse_args()

    manifest = json.loads(args.manifest.read_text())
    files = []
    for stage_key, stage in manifest.get("stages", {}).items():
        for f in stage.get("files", []):
            files.append(Path(f["path"]))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    all_segments = []
    for i, wav_path in enumerate(files):
        if args.max_files and i >= args.max_files:
            break
        if not wav_path.exists():
            print(f"  skip missing: {wav_path}", file=sys.stderr)
            continue
        print(f"[{i+1}/{len(files)}] {wav_path.name}", file=sys.stderr, flush=True)
        try:
            segs = process_wav(wav_path, args.out_dir)
            all_segments.extend(segs)
            print(f"    {len(segs)} candidate segments", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"    ERROR {e}", file=sys.stderr)

    index_path = args.out_dir / "index.json"
    index_path.write_text(json.dumps({
        "n_segments": len(all_segments),
        "min_voiced_ms": MIN_VOICED_DURATION_MS,
        "max_voiced_ms": MAX_VOICED_DURATION_MS,
        "fft_bands": FFT_BANDS,
        "silence_threshold_percentile": SILENCE_THRESHOLD_PERCENTILE,
        "segments": all_segments,
    }, indent=2))
    print(f"\nWrote {len(all_segments)} segments to {args.out_dir}", file=sys.stderr)
    print(f"Index: {index_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
