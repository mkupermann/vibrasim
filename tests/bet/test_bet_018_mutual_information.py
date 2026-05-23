"""BET-018 — T12 mutual information between query class and BMU cell.

Pre-registered LOGBOOK 2026-05-24 00:08. Intrinsic substrate-routing
test: no reference vectors, no magnitude bias, no positivity artifacts.

Protocol: train SOM+replay on EN (10k ticks). Present 1000 EN + 1000
WN queries. For each, record BMU cell index. Compute MI between
(query class, BMU cell index).

T12 bar (LOCKED):
  trained_MI > 0.5 bits
  fresh_MI < 0.1 bits
  Both must pass.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_replay import SOMReplayConfig, initialise, run
from world.flux.cognitive_map import encode_sensor

N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
TARGET_RMS = 0.25
N_QUERIES_PER_CLASS = 1000

T12_TRAINED_MIN = 0.5  # bits
T12_FRESH_MAX = 0.1    # bits

OUT_DIR = Path.home() / ".eqmod/bet/BET-018"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n_samples, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n_samples)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _retrieve_bmu_index(state, sensor):
    """Return BMU as flat cell index 0..(Lx*Ly*Lz-1)."""
    diff = state["w"] - sensor
    dist_sq = np.einsum("ijkl,ijkl->ijk", diff, diff)
    return int(np.argmin(dist_sq))


def _gather_bmu_indices(state, audio, cfg, n_queries):
    """For each of n_queries chunks, return its BMU index."""
    n = min(n_queries, audio.size // cfg.samples_per_tick)
    bmu_indices = np.zeros(n, dtype=np.int64)
    for k in range(n):
        i0 = k * cfg.samples_per_tick
        i1 = i0 + cfg.samples_per_tick
        chunk = audio[i0:i1]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        bmu_indices[k] = _retrieve_bmu_index(state, sensor)
    return bmu_indices


def _mutual_information(class_labels: np.ndarray, bmu_indices: np.ndarray, n_cells: int) -> float:
    """Plug-in MI estimator with Laplace smoothing. Returns bits."""
    n = class_labels.size
    classes = np.unique(class_labels)
    n_classes = classes.size
    # Joint distribution
    joint = np.zeros((n_classes, n_cells), dtype=np.float64)
    for ci, c in enumerate(classes):
        mask = class_labels == c
        cells_for_class = bmu_indices[mask]
        for b in cells_for_class:
            joint[ci, b] += 1.0
    # Laplace smoothing
    joint += 1.0
    total = joint.sum()
    joint /= total
    p_class = joint.sum(axis=1, keepdims=True)
    p_cell = joint.sum(axis=0, keepdims=True)
    # MI = sum p(c,b) * log2(p(c,b) / (p(c) * p(b)))
    safe_joint = np.where(joint > 0, joint, 1.0)
    log_ratio = np.log2(safe_joint / (p_class * p_cell + 1e-30) + 1e-30)
    mi = float((joint * log_ratio).sum())
    return mi


@pytest.fixture(scope="module")
def substrates():
    cfg = SOMReplayConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
    )
    n_audio = N_TICKS * SAMPLES_PER_TICK
    n_query = N_QUERIES_PER_CLASS * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if n_audio + n_query > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_train = full[:n_audio].astype(np.float64)
    eng_queries = full[n_audio:n_audio + n_query].astype(np.float64)
    wn_train = _make_white_noise(n_audio, TARGET_RMS, WN_SEED)
    wn_queries = _make_white_noise(n_query, TARGET_RMS, WN_SEED + 1)

    Lx, Ly, Lz = cfg.grid_dims
    n_cells = Lx * Ly * Lz  # 3600

    # Trained substrate
    state_trained = run(cfg, N_TICKS, eng_train)
    bmu_eng_trained = _gather_bmu_indices(state_trained, eng_queries, cfg, N_QUERIES_PER_CLASS)
    bmu_wn_trained = _gather_bmu_indices(state_trained, wn_queries, cfg, N_QUERIES_PER_CLASS)

    classes_trained = np.concatenate([
        np.zeros(bmu_eng_trained.size, dtype=np.int64),
        np.ones(bmu_wn_trained.size, dtype=np.int64),
    ])
    bmu_all_trained = np.concatenate([bmu_eng_trained, bmu_wn_trained])
    mi_trained = _mutual_information(classes_trained, bmu_all_trained, n_cells)

    # Fresh (no training) substrate
    state_fresh = initialise(cfg)
    bmu_eng_fresh = _gather_bmu_indices(state_fresh, eng_queries, cfg, N_QUERIES_PER_CLASS)
    bmu_wn_fresh = _gather_bmu_indices(state_fresh, wn_queries, cfg, N_QUERIES_PER_CLASS)
    classes_fresh = np.concatenate([
        np.zeros(bmu_eng_fresh.size, dtype=np.int64),
        np.ones(bmu_wn_fresh.size, dtype=np.int64),
    ])
    bmu_all_fresh = np.concatenate([bmu_eng_fresh, bmu_wn_fresh])
    mi_fresh = _mutual_information(classes_fresh, bmu_all_fresh, n_cells)

    return dict(
        cfg=cfg, n_cells=n_cells,
        mi_trained=mi_trained, mi_fresh=mi_fresh,
        n_unique_bmus_trained_eng=int(np.unique(bmu_eng_trained).size),
        n_unique_bmus_trained_wn=int(np.unique(bmu_wn_trained).size),
        n_unique_bmus_fresh_eng=int(np.unique(bmu_eng_fresh).size),
        n_unique_bmus_fresh_wn=int(np.unique(bmu_wn_fresh).size),
    )


def _verdict(sub):
    trained_pass = sub["mi_trained"] > T12_TRAINED_MIN
    fresh_pass = sub["mi_fresh"] < T12_FRESH_MAX
    return {
        "T12_mi_trained_bits": sub["mi_trained"],
        "T12_mi_trained_threshold_min": T12_TRAINED_MIN,
        "T12_mi_trained_pass": trained_pass,
        "T12_mi_fresh_bits": sub["mi_fresh"],
        "T12_mi_fresh_threshold_max": T12_FRESH_MAX,
        "T12_mi_fresh_pass": fresh_pass,
        "n_cells_total": sub["n_cells"],
        "n_unique_bmus_trained_eng": sub["n_unique_bmus_trained_eng"],
        "n_unique_bmus_trained_wn": sub["n_unique_bmus_trained_wn"],
        "n_unique_bmus_fresh_eng": sub["n_unique_bmus_fresh_eng"],
        "n_unique_bmus_fresh_wn": sub["n_unique_bmus_fresh_wn"],
        "T12_pass": trained_pass and fresh_pass,
    }


def test_T12_mutual_information(substrates):
    m = _verdict(substrates)
    if not m["T12_pass"]:
        pytest.fail(
            f"BET-018 NULL: T12 mutual information.\n"
            f"  trained substrate MI: {m['T12_mi_trained_bits']:.4f} bits "
            f"(need > {T12_TRAINED_MIN}) pass={m['T12_mi_trained_pass']}\n"
            f"  fresh substrate MI:   {m['T12_mi_fresh_bits']:.4f} bits "
            f"(need < {T12_FRESH_MAX}) pass={m['T12_mi_fresh_pass']}\n"
            f"  unique BMUs trained: EN={m['n_unique_bmus_trained_eng']}, WN={m['n_unique_bmus_trained_wn']}\n"
            f"  unique BMUs fresh:   EN={m['n_unique_bmus_fresh_eng']}, WN={m['n_unique_bmus_fresh_wn']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T12_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-018",
        "verdict": verdict,
        "hypothesis": "T12 mutual information: BMU cell index carries substantial info about query class (EN vs WN) after training. Intrinsic substrate-routing metric — no reference vectors, no magnitude bias.",
        "thresholds": {
            "T12_trained_min_bits": T12_TRAINED_MIN,
            "T12_fresh_max_bits": T12_FRESH_MAX,
        },
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))
