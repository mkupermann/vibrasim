"""BET-040 — T24 multi-class generation.

Substrate trained sequentially on EN+WN with replay. Cells classified
as EN-cells or WN-cells by which class visited them more during training.
Bigram built on combined token stream. Generation tested for compositional
output.

Tests substrate's ability to represent + generate TWO classes
simultaneously after sequential training. Builds on T8 (catastrophic-
forgetting resistance) + T22 (autonomous generation).

T24 bar (LOCKED):
  EN-cell fraction in generated sequence within [0.25, 0.75]
  AND substrate has both class-types as cells (not all EN or all WN)

If passes: substrate maintains compositional class memory; can generate
both classes via bigram conditioning.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_replay import SOMReplayConfig, run, initialise
from world.flux.cognitive_map import encode_sensor

N_TICKS_PER_CLASS = 5_000
N_GENERATE = 1_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
GEN_SEED = 7777
TARGET_RMS = 0.25
GRID_DIMS = (10, 10, 1)

T24_EN_FRACTION_MIN = 0.25
T24_EN_FRACTION_MAX = 0.75

OUT_DIR = Path.home() / ".eqmod/bet/BET-040"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _quantize_with_class(state, audio, cfg, class_label):
    """Returns (tokens, classes) parallel arrays."""
    n = audio.size // cfg.samples_per_tick
    tokens = np.zeros(n, dtype=np.int64)
    classes = np.full(n, class_label, dtype=np.int64)
    for k in range(n):
        chunk = audio[k * cfg.samples_per_tick:(k + 1) * cfg.samples_per_tick]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        diff = state["w"] - sensor
        tokens[k] = int(np.argmin(np.einsum("ijkl,ijkl->ijk", diff, diff)))
    return tokens, classes


def _copy_state(state):
    return {
        "w": state["w"].copy(), "N": state["N"].copy(),
        "ii": state["ii"], "jj": state["jj"], "kk": state["kk"],
        "buffer": state["buffer"].copy(), "buffer_head": state["buffer_head"],
        "buffer_fill": state["buffer_fill"], "global_tick": state["global_tick"],
    }


def _bigram(tokens, n_cells, alpha=0.01):
    B = np.zeros((n_cells, n_cells), dtype=np.float64)
    for t in range(tokens.size - 1):
        B[tokens[t], tokens[t + 1]] += 1
    B += alpha
    return B / B.sum(axis=1, keepdims=True)


def _generate(P, n_tokens, n_cells, seed):
    rng = np.random.default_rng(seed)
    tokens = np.zeros(n_tokens, dtype=np.int64)
    tokens[0] = rng.integers(0, n_cells)
    for t in range(1, n_tokens):
        tokens[t] = rng.choice(n_cells, p=P[tokens[t - 1]])
    return tokens


@pytest.fixture(scope="module")
def substrates():
    cfg = SOMReplayConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES, grid_dims=GRID_DIMS,
    )
    n_per_class = N_TICKS_PER_CLASS * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if n_per_class > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng = full[:n_per_class].astype(np.float64)
    wn = _make_wn(n_per_class, TARGET_RMS, WN_SEED)

    Lx, Ly, Lz = GRID_DIMS
    n_cells = Lx * Ly * Lz

    # Sequential training: EN first, then WN. Replay protects EN.
    state = run(cfg, N_TICKS_PER_CLASS, eng)
    en_tokens, en_classes = _quantize_with_class(state, eng, cfg, class_label=0)

    state_after_en = _copy_state(state)
    state = run(cfg, N_TICKS_PER_CLASS, wn, state=state)
    wn_tokens, wn_classes = _quantize_with_class(state, wn, cfg, class_label=1)

    # Combined token stream + class labels
    combined_tokens = np.concatenate([en_tokens, wn_tokens])
    combined_classes = np.concatenate([en_classes, wn_classes])

    # Classify each cell by which class visited it more
    cell_en_visits = np.zeros(n_cells, dtype=np.int64)
    cell_wn_visits = np.zeros(n_cells, dtype=np.int64)
    for t, c in zip(combined_tokens, combined_classes):
        if c == 0:
            cell_en_visits[t] += 1
        else:
            cell_wn_visits[t] += 1
    cell_class = np.where(cell_en_visits > cell_wn_visits, 0, 1)

    n_en_cells = int((cell_class == 0).sum())
    n_wn_cells = int((cell_class == 1).sum())

    P_bi = _bigram(combined_tokens, n_cells)
    gen_tokens = _generate(P_bi, N_GENERATE, n_cells, GEN_SEED)

    gen_en_fraction = float(np.mean(cell_class[gen_tokens] == 0))
    gen_wn_fraction = float(np.mean(cell_class[gen_tokens] == 1))

    return dict(
        n_cells=n_cells,
        n_per_class_train=N_TICKS_PER_CLASS,
        n_combined_tokens=int(combined_tokens.size),
        n_unique_combined=int(np.unique(combined_tokens).size),
        n_en_cells=n_en_cells, n_wn_cells=n_wn_cells,
        en_cell_fraction=n_en_cells / n_cells,
        wn_cell_fraction=n_wn_cells / n_cells,
        gen_en_fraction=gen_en_fraction,
        gen_wn_fraction=gen_wn_fraction,
        gen_n_tokens=int(gen_tokens.size),
    )


def test_T24(substrates):
    s = substrates
    has_both = s["n_en_cells"] > 0 and s["n_wn_cells"] > 0
    balanced = T24_EN_FRACTION_MIN <= s["gen_en_fraction"] <= T24_EN_FRACTION_MAX
    if not (has_both and balanced):
        pytest.fail(
            f"BET-040 NULL T24 multi-class generation.\n"
            f"  EN-cells: {s['n_en_cells']}/{s['n_cells']} = {s['en_cell_fraction']:.4f}\n"
            f"  WN-cells: {s['n_wn_cells']}/{s['n_cells']} = {s['wn_cell_fraction']:.4f}\n"
            f"  has_both_class_cells: {has_both}\n"
            f"  generated EN fraction: {s['gen_en_fraction']:.4f}\n"
            f"  bar: [{T24_EN_FRACTION_MIN}, {T24_EN_FRACTION_MAX}] balanced={balanced}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    s = substrates
    has_both = s["n_en_cells"] > 0 and s["n_wn_cells"] > 0
    balanced = T24_EN_FRACTION_MIN <= s["gen_en_fraction"] <= T24_EN_FRACTION_MAX
    pass_ = has_both and balanced
    verdict = "passed" if pass_ else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-040",
        "verdict": verdict,
        "hypothesis": "T24 multi-class generation. Substrate trained sequentially EN+WN with replay; cells classified by majority-visit. Generated bigram-sample contains BOTH class-types in balanced fraction (substrate has compositional class memory).",
        "thresholds": {
            "T24_en_fraction_min": T24_EN_FRACTION_MIN,
            "T24_en_fraction_max": T24_EN_FRACTION_MAX,
        },
        "measurements": {**s, "T24_pass": pass_},
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))
