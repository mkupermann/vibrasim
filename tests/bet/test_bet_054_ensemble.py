"""BET-054 — T38 substrate ensemble (3 substrates majority vote).

Tests if ensemble of independent substrates (different seeds) improves
3-class classification over single substrate (BET-050 88.6%).

T38 bar (LOCKED): ensemble balanced accuracy > single-substrate
balanced (>0.886).
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
N_TEST_PER_CLASS = 1_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
WN_TEST_SEED = 8888
PINK_SEED = 7777
PINK_TEST_SEED = 6666
TARGET_RMS = 0.25
GRID_DIMS = (10, 10, 1)
ENSEMBLE_SEEDS = (0, 42, 1337)

T38_ENSEMBLE_MIN = 0.886
T38_IMPROVEMENT_MIN = 0.0  # ensemble must be >= single

OUT_DIR = Path.home() / ".eqmod/bet/BET-054"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _make_pink(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    white = rng.standard_normal(n)
    fft = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n)
    freqs[0] = 1.0
    fft_pink = fft / np.sqrt(freqs)
    pink = np.fft.irfft(fft_pink, n=n)
    rms = np.sqrt(np.mean(pink * pink))
    if rms > 0:
        pink = pink / rms * target_rms
    return pink.astype(np.float64)


def _copy_state(state):
    return {
        "w": state["w"].copy(), "N": state["N"].copy(),
        "ii": state["ii"], "jj": state["jj"], "kk": state["kk"],
        "buffer": state["buffer"].copy(), "buffer_head": state["buffer_head"],
        "buffer_fill": state["buffer_fill"], "global_tick": state["global_tick"],
    }


def _bmu_index(state, sensor):
    diff = state["w"] - sensor
    return int(np.argmin(np.einsum("ijkl,ijkl->ijk", diff, diff)))


def _count_visits(state, audio, cfg, n_cells, n_chunks):
    counts = np.zeros(n_cells, dtype=np.int64)
    for k in range(n_chunks):
        chunk = audio[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK]
        if chunk.size == 0:
            continue
        counts[_bmu_index(state, encode_sensor(chunk, cfg))] += 1
    return counts


def _train_substrate(seed, eng, wn, pink, n_per, cfg, n_cells, n_chunks_per_class):
    cfg_seeded = SOMReplayConfig(
        samples_per_tick=cfg.samples_per_tick, fft_bands=cfg.fft_bands,
        n_features=cfg.n_features, grid_dims=cfg.grid_dims, rng_seed=seed,
    )
    state = run(cfg_seeded, N_TICKS_PER_CLASS, eng)
    cell_en = _count_visits(state, eng, cfg_seeded, n_cells, n_chunks_per_class)
    state = run(cfg_seeded, N_TICKS_PER_CLASS, wn, state=_copy_state(state))
    cell_wn = _count_visits(state, wn, cfg_seeded, n_cells, n_chunks_per_class)
    state = run(cfg_seeded, N_TICKS_PER_CLASS, pink, state=_copy_state(state))
    cell_pink = _count_visits(state, pink, cfg_seeded, n_cells, n_chunks_per_class)
    cell_labels = np.stack([cell_en, cell_wn, cell_pink], axis=1).argmax(axis=1)
    return state, cell_labels


def _predict(state, cell_labels, sensor):
    return int(cell_labels[_bmu_index(state, sensor)])


def _ensemble_classify(states_with_labels, audio, cfg, true_class):
    n = audio.size // cfg.samples_per_tick
    correct = 0
    total = 0
    for k in range(n):
        chunk = audio[k * cfg.samples_per_tick:(k + 1) * cfg.samples_per_tick]
        if chunk.size == 0:
            continue
        sensor = encode_sensor(chunk, cfg)
        # Majority vote
        votes = [_predict(state, labels, sensor) for state, labels in states_with_labels]
        # Most common vote (ties broken by first)
        counts = np.bincount(votes, minlength=3)
        pred = int(np.argmax(counts))
        if pred == true_class:
            correct += 1
        total += 1
    return correct / max(total, 1)


def _single_classify(state, cell_labels, audio, cfg, true_class):
    return _ensemble_classify([(state, cell_labels)], audio, cfg, true_class)


@pytest.fixture(scope="module")
def substrates():
    cfg = SOMReplayConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES, grid_dims=GRID_DIMS,
    )
    n_per = N_TICKS_PER_CLASS * SAMPLES_PER_TICK
    n_test = N_TEST_PER_CLASS * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if n_per + n_test > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_train = full[:n_per].astype(np.float64)
    eng_test = full[n_per:n_per + n_test].astype(np.float64)
    wn_train = _make_wn(n_per, TARGET_RMS, WN_SEED)
    wn_test = _make_wn(n_test, TARGET_RMS, WN_TEST_SEED)
    pink_train = _make_pink(n_per, TARGET_RMS, PINK_SEED)
    pink_test = _make_pink(n_test, TARGET_RMS, PINK_TEST_SEED)

    Lx, Ly, Lz = GRID_DIMS
    n_cells = Lx * Ly * Lz
    n_chunks_per_class = n_per // SAMPLES_PER_TICK

    # Train 3 substrates with different seeds
    substrates_list = []
    for seed in ENSEMBLE_SEEDS:
        state, cell_labels = _train_substrate(
            seed, eng_train, wn_train, pink_train, n_per, cfg, n_cells, n_chunks_per_class)
        substrates_list.append((state, cell_labels))

    # Single-substrate baseline (use first seed)
    single_acc_en = _single_classify(*substrates_list[0], eng_test, cfg, 0)
    single_acc_wn = _single_classify(*substrates_list[0], wn_test, cfg, 1)
    single_acc_pink = _single_classify(*substrates_list[0], pink_test, cfg, 2)
    single_bal = (single_acc_en + single_acc_wn + single_acc_pink) / 3

    # Ensemble
    ens_acc_en = _ensemble_classify(substrates_list, eng_test, cfg, 0)
    ens_acc_wn = _ensemble_classify(substrates_list, wn_test, cfg, 1)
    ens_acc_pink = _ensemble_classify(substrates_list, pink_test, cfg, 2)
    ens_bal = (ens_acc_en + ens_acc_wn + ens_acc_pink) / 3

    return dict(
        n_substrates=len(ENSEMBLE_SEEDS),
        seeds=list(ENSEMBLE_SEEDS),
        single_balanced=single_bal,
        ensemble_balanced=ens_bal,
        improvement=ens_bal - single_bal,
        single_per_class={"en": single_acc_en, "wn": single_acc_wn, "pink": single_acc_pink},
        ensemble_per_class={"en": ens_acc_en, "wn": ens_acc_wn, "pink": ens_acc_pink},
    )


def _verdict(s):
    pass_ = (s["ensemble_balanced"] > T38_ENSEMBLE_MIN
             and s["improvement"] >= T38_IMPROVEMENT_MIN)
    return {**s, "T38_pass": pass_}


def test_T38(substrates):
    m = _verdict(substrates)
    if not m["T38_pass"]:
        pytest.fail(
            f"BET-054 NULL T38 ensemble.\n"
            f"  single substrate: {m['single_balanced']:.4f}\n"
            f"  ensemble (3 substrates): {m['ensemble_balanced']:.4f}\n"
            f"  improvement: {m['improvement']:+.4f} (need >= 0)\n"
            f"  ensemble >= {T38_ENSEMBLE_MIN}? {m['ensemble_balanced'] > T38_ENSEMBLE_MIN}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T38_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-054",
        "verdict": verdict,
        "hypothesis": "T38 substrate ensemble. 3 SOM+replay substrates with different seeds, majority vote. Tests if ensemble improves over single substrate.",
        "thresholds": {"T38_ensemble_min": T38_ENSEMBLE_MIN, "T38_improvement_min": T38_IMPROVEMENT_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))
