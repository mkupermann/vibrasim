"""BET-041 — T25 conditional generation steerable by prompt.

After BET-040 PASS (multi-class generation), test if substrate's
generation can be STEERED by a prompt: given starting token from
EN-cells, generated continuation should be EN-biased. Given starting
token from WN-cells, continuation should be WN-biased.

This tests INPUT→OUTPUT communication: substrate responds to a prompt
with class-appropriate output. Core property of usable communication.

T25 bar (LOCKED):
  EN-prompted continuation: > 50% EN-cells in next 100 tokens
  WN-prompted continuation: > 50% WN-cells in next 100 tokens
  Both must satisfy.

If passes: substrate is bigram-steerable; the prompt biases output
class. Real prompt-response capability at substrate level.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_replay import SOMReplayConfig, run
from world.flux.cognitive_map import encode_sensor

N_TICKS_PER_CLASS = 5_000
N_CONTINUE = 100
N_TRIALS = 100
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
GEN_SEED = 9001
TARGET_RMS = 0.25
GRID_DIMS = (10, 10, 1)

T25_FRACTION_MIN = 0.5

OUT_DIR = Path.home() / ".eqmod/bet/BET-041"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _quantize_with_class(state, audio, cfg, class_label):
    n = audio.size // cfg.samples_per_tick
    tokens = np.zeros(n, dtype=np.int64)
    for k in range(n):
        chunk = audio[k * cfg.samples_per_tick:(k + 1) * cfg.samples_per_tick]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        diff = state["w"] - sensor
        tokens[k] = int(np.argmin(np.einsum("ijkl,ijkl->ijk", diff, diff)))
    return tokens


def _bigram(tokens, n_cells, alpha=0.01):
    B = np.zeros((n_cells, n_cells), dtype=np.float64)
    for t in range(tokens.size - 1):
        B[tokens[t], tokens[t + 1]] += 1
    B += alpha
    return B / B.sum(axis=1, keepdims=True)


def _generate_from(P, start_token, n_continue, n_cells, seed):
    rng = np.random.default_rng(seed)
    tokens = np.zeros(n_continue, dtype=np.int64)
    tokens[0] = start_token
    for t in range(1, n_continue):
        tokens[t] = rng.choice(n_cells, p=P[tokens[t - 1]])
    return tokens


@pytest.fixture(scope="module")
def substrates():
    cfg = SOMReplayConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES, grid_dims=GRID_DIMS,
    )
    n_per = N_TICKS_PER_CLASS * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if n_per > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng = full[:n_per].astype(np.float64)
    wn = _make_wn(n_per, TARGET_RMS, WN_SEED)

    Lx, Ly, Lz = GRID_DIMS
    n_cells = Lx * Ly * Lz

    state = run(cfg, N_TICKS_PER_CLASS, eng)
    en_tokens = _quantize_with_class(state, eng, cfg, 0)
    state = run(cfg, N_TICKS_PER_CLASS, wn, state={
        "w": state["w"].copy(), "N": state["N"].copy(),
        "ii": state["ii"], "jj": state["jj"], "kk": state["kk"],
        "buffer": state["buffer"].copy(), "buffer_head": state["buffer_head"],
        "buffer_fill": state["buffer_fill"], "global_tick": state["global_tick"],
    })
    wn_tokens = _quantize_with_class(state, wn, cfg, 1)

    combined = np.concatenate([en_tokens, wn_tokens])
    combined_classes = np.concatenate([
        np.zeros(en_tokens.size, dtype=np.int64),
        np.ones(wn_tokens.size, dtype=np.int64),
    ])

    cell_en_visits = np.zeros(n_cells, dtype=np.int64)
    cell_wn_visits = np.zeros(n_cells, dtype=np.int64)
    for t, c in zip(combined, combined_classes):
        if c == 0:
            cell_en_visits[t] += 1
        else:
            cell_wn_visits[t] += 1
    cell_class = np.where(cell_en_visits > cell_wn_visits, 0, 1)

    P_bi = _bigram(combined, n_cells)

    # EN-typical prompts: cells most-visited by EN
    en_cells_sorted = np.argsort(-cell_en_visits)
    wn_cells_sorted = np.argsort(-cell_wn_visits)

    en_prompts = en_cells_sorted[:N_TRIALS]
    wn_prompts = wn_cells_sorted[:N_TRIALS]

    # Run N_TRIALS continuations from each prompt
    en_continuation_en_fractions = []
    wn_continuation_wn_fractions = []
    for i in range(N_TRIALS):
        en_cont = _generate_from(P_bi, int(en_prompts[i]), N_CONTINUE, n_cells, GEN_SEED + i)
        wn_cont = _generate_from(P_bi, int(wn_prompts[i]), N_CONTINUE, n_cells, GEN_SEED + 1000 + i)
        en_continuation_en_fractions.append(float(np.mean(cell_class[en_cont] == 0)))
        wn_continuation_wn_fractions.append(float(np.mean(cell_class[wn_cont] == 1)))

    mean_en_fraction_when_en_prompted = float(np.mean(en_continuation_en_fractions))
    mean_wn_fraction_when_wn_prompted = float(np.mean(wn_continuation_wn_fractions))

    return dict(
        n_cells=n_cells,
        n_en_cells=int((cell_class == 0).sum()),
        n_wn_cells=int((cell_class == 1).sum()),
        n_trials=N_TRIALS, n_continue=N_CONTINUE,
        mean_en_fraction_when_en_prompted=mean_en_fraction_when_en_prompted,
        mean_wn_fraction_when_wn_prompted=mean_wn_fraction_when_wn_prompted,
    )


def test_T25(substrates):
    s = substrates
    en_pass = s["mean_en_fraction_when_en_prompted"] > T25_FRACTION_MIN
    wn_pass = s["mean_wn_fraction_when_wn_prompted"] > T25_FRACTION_MIN
    if not (en_pass and wn_pass):
        pytest.fail(
            f"BET-041 NULL T25 conditional generation.\n"
            f"  EN-prompted EN-fraction: {s['mean_en_fraction_when_en_prompted']:.4f} "
            f"(need > {T25_FRACTION_MIN}) pass={en_pass}\n"
            f"  WN-prompted WN-fraction: {s['mean_wn_fraction_when_wn_prompted']:.4f} "
            f"(need > {T25_FRACTION_MIN}) pass={wn_pass}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    s = substrates
    en_pass = s["mean_en_fraction_when_en_prompted"] > T25_FRACTION_MIN
    wn_pass = s["mean_wn_fraction_when_wn_prompted"] > T25_FRACTION_MIN
    pass_ = en_pass and wn_pass
    verdict = "passed" if pass_ else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-041",
        "verdict": verdict,
        "hypothesis": "T25 conditional generation. Substrate prompted with class-typical token continues bigram generation; continuation should be class-biased (>50%).",
        "thresholds": {"T25_class_fraction_min": T25_FRACTION_MIN},
        "measurements": {**s, "T25_en_pass": en_pass, "T25_wn_pass": wn_pass, "T25_pass": pass_},
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))
