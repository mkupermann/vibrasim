"""BET-047 — Hopfield attractor-based pattern completion.

Stores SOM cell weights as Hopfield attractor patterns. Tests pattern
completion from partial cues: given 5 of 10 feature dims, Hopfield
should converge to nearest stored pattern.

Compare to BET-016 (SOM-BMU-with-partial-distance): Hopfield gives
DYNAMIC attractor convergence vs SOM gives nearest-neighbor lookup.
Different mechanism.

T31 bar (LOCKED):
  Mean Pearson correlation between Hopfield-recalled hidden dims and
  true hidden dims:
    Positive (trained on EN cells, query EN partial): > 0.6
    Negative (trained on WN cells, query EN partial): < 0.4
    Difference (positive - negative): > 0.3
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_replay import SOMReplayConfig, run as som_run
from world.flux.hopfield import HopfieldConfig, initialise as hop_init, store_patterns, recall
from world.flux.cognitive_map import encode_sensor

N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
N_HIDDEN = 5
WN_SEED = 9999
ZERO_SEED = 33333
TARGET_RMS = 0.25
N_HOLDOUT = 1000
GRID_DIMS = (10, 10, 1)

T31_POS_MIN = 0.6
T31_NEG_MAX = 0.4
T31_DIFF_MIN = 0.3

OUT_DIR = Path.home() / ".eqmod/bet/BET-047"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _partial_mask(cfg, seed):
    rng = np.random.default_rng(seed)
    perm = rng.permutation(cfg.n_features)
    known_mask = np.zeros(cfg.n_features, dtype=bool)
    known_mask[perm[:cfg.n_features - N_HIDDEN]] = True
    return known_mask


def _pearson(a, b):
    a_c = a - a.mean()
    b_c = b - b.mean()
    denom = np.linalg.norm(a_c) * np.linalg.norm(b_c) + 1e-12
    return float(np.dot(a_c, b_c) / denom) if denom > 0 else 0.0


def _evaluate_hopfield(hop_state, eng_held_audio, som_cfg, hop_cfg, n_holdout):
    n_chunks = min(n_holdout, eng_held_audio.size // som_cfg.samples_per_tick)
    pearsons = []
    for k in range(n_chunks):
        chunk = eng_held_audio[k * som_cfg.samples_per_tick:(k + 1) * som_cfg.samples_per_tick]
        if chunk.size == 0:
            continue
        full = encode_sensor(chunk, som_cfg)
        known = _partial_mask(som_cfg, ZERO_SEED + k)
        cue = np.where(known, full, 0.0)
        recalled = recall(hop_state, cue, known, hop_cfg)
        hidden = ~known
        if hidden.sum() < 2:
            continue
        r = _pearson(full[hidden], recalled[hidden])
        pearsons.append(r)
    arr = np.array(pearsons) if pearsons else np.array([0.0])
    return float(arr.mean())


@pytest.fixture(scope="module")
def substrates():
    som_cfg = SOMReplayConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES, grid_dims=GRID_DIMS,
    )
    hop_cfg = HopfieldConfig(n_features=N_FEATURES)
    n_audio = N_TICKS * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if 2 * n_audio > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_train = full[:n_audio].astype(np.float64)
    eng_held = full[n_audio:2 * n_audio].astype(np.float64)
    wn = _make_wn(n_audio, TARGET_RMS, WN_SEED)

    # Build SOMs to get cell-weight patterns
    state_en = som_run(som_cfg, N_TICKS, eng_train)
    state_wn = som_run(som_cfg, N_TICKS, wn)

    Lx, Ly, Lz = GRID_DIMS
    n_cells = Lx * Ly * Lz

    # Hopfield trained on EN cells
    hop_en = hop_init(hop_cfg)
    en_patterns = state_en["w"].reshape(n_cells, N_FEATURES)
    store_patterns(hop_en, en_patterns)

    # Hopfield trained on WN cells
    hop_wn = hop_init(hop_cfg)
    wn_patterns = state_wn["w"].reshape(n_cells, N_FEATURES)
    store_patterns(hop_wn, wn_patterns)

    pos_pearson = _evaluate_hopfield(hop_en, eng_held, som_cfg, hop_cfg, N_HOLDOUT)
    neg_pearson = _evaluate_hopfield(hop_wn, eng_held, som_cfg, hop_cfg, N_HOLDOUT)

    return dict(
        n_cells=n_cells,
        n_patterns_stored=n_cells,
        pos_pearson_hidden=pos_pearson,
        neg_pearson_hidden=neg_pearson,
        diff=pos_pearson - neg_pearson,
    )


def _verdict(s):
    pos_ok = s["pos_pearson_hidden"] > T31_POS_MIN
    neg_ok = s["neg_pearson_hidden"] < T31_NEG_MAX
    diff_ok = s["diff"] > T31_DIFF_MIN
    return {
        **s,
        "T31_pos_pass": pos_ok,
        "T31_neg_pass": neg_ok,
        "T31_diff_pass": diff_ok,
        "T31_pass": pos_ok and neg_ok and diff_ok,
    }


def test_T31(substrates):
    m = _verdict(substrates)
    if not m["T31_pass"]:
        pytest.fail(
            f"BET-047 NULL T31 Hopfield pattern completion.\n"
            f"  positive (trained EN, query EN partial): {m['pos_pearson_hidden']:.4f} "
            f"(need > {T31_POS_MIN}) pass={m['T31_pos_pass']}\n"
            f"  negative (trained WN, query EN partial): {m['neg_pearson_hidden']:.4f} "
            f"(need < {T31_NEG_MAX}) pass={m['T31_neg_pass']}\n"
            f"  diff: {m['diff']:.4f} (need > {T31_DIFF_MIN}) pass={m['T31_diff_pass']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T31_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-047",
        "verdict": verdict,
        "hypothesis": "T31 Hopfield attractor-based pattern completion. Stores SOM cell-weights as attractors; partial-cue recall converges to nearest stored pattern via dynamics. Compares to BET-016 nearest-neighbor SOM recall.",
        "thresholds": {
            "T31_pos_min": T31_POS_MIN, "T31_neg_max": T31_NEG_MAX,
            "T31_diff_min": T31_DIFF_MIN,
        },
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))
