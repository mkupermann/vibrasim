"""BET-027 — T17 histogram-matching fidelity.

Intrinsic test: does the substrate's CELL WEIGHT DISTRIBUTION match the
TRAINING INPUT DISTRIBUTION? A well-tuned SOM should be a
vector-quantization of its training data.

T17 protocol:
  1. Train substrate on EN (10k ticks).
  2. Sample N=10000 EN sensor vectors from training data.
  3. Compute histogram-KL between substrate.w (3600 cells × 10 dims =
     36000 scalars) and training-input-feature-distribution (10000 × 10
     = 100000 scalars).
  4. Bar (LOCKED): KL < 0.5

  Negative control: same KL on WN-trained substrate vs EN-input
  distribution. Should be much larger.

Pre-data prediction: substrate captures training distribution faithfully.
KL(EN-trained-cells, EN-inputs) < 0.5. KL(WN-trained-cells, EN-inputs)
much larger (substrate trained elsewhere doesn't fit EN).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.som_replay import SOMReplayConfig, run
from world.flux.cognitive_map import encode_sensor
from world.flux.harder_bar_metrics import hist_kl_symmetric

N_TICKS = 10_000
N_SAMPLE_INPUTS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
TARGET_RMS = 0.25

T17_BAR_MAX = 0.5

OUT_DIR = Path.home() / ".eqmod/bet/BET-027"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _sample_features(audio, cfg, n_samples):
    features = np.zeros((n_samples, cfg.n_features), dtype=np.float64)
    n = min(n_samples, audio.size // cfg.samples_per_tick)
    for k in range(n):
        chunk = audio[k * cfg.samples_per_tick:(k + 1) * cfg.samples_per_tick]
        if chunk.size == 0:
            continue
        features[k] = encode_sensor(chunk, cfg)
    return features[:n]


@pytest.fixture(scope="module")
def substrates():
    cfg = SOMReplayConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
    )
    n_audio = N_TICKS * SAMPLES_PER_TICK
    n_sample = N_SAMPLE_INPUTS * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if n_audio + n_sample > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_train = full[:n_audio].astype(np.float64)
    eng_sample = full[n_audio:n_audio + n_sample].astype(np.float64)
    wn = _make_white_noise(n_audio, TARGET_RMS, WN_SEED)

    state_en = run(cfg, N_TICKS, eng_train)
    state_wn = run(cfg, N_TICKS, wn)
    en_features = _sample_features(eng_sample, cfg, N_SAMPLE_INPUTS)

    kl_en_cells_vs_en_inputs = hist_kl_symmetric(state_en["w"], en_features)
    kl_wn_cells_vs_en_inputs = hist_kl_symmetric(state_wn["w"], en_features)

    return {
        "kl_en_cells_vs_en_inputs": kl_en_cells_vs_en_inputs,
        "kl_wn_cells_vs_en_inputs": kl_wn_cells_vs_en_inputs,
        "discrimination_ratio": kl_wn_cells_vs_en_inputs / max(kl_en_cells_vs_en_inputs, 1e-9),
    }


def test_T17(substrates):
    en_kl = substrates["kl_en_cells_vs_en_inputs"]
    wn_kl = substrates["kl_wn_cells_vs_en_inputs"]
    t17_pass = en_kl < T17_BAR_MAX and wn_kl > en_kl
    if not t17_pass:
        pytest.fail(
            f"BET-027 NULL: T17 histogram fidelity.\n"
            f"  KL(EN-cells, EN-inputs) = {en_kl:.4f} (need < {T17_BAR_MAX})\n"
            f"  KL(WN-cells, EN-inputs) = {wn_kl:.4f}\n"
            f"  discrimination = {substrates['discrimination_ratio']:.4f}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    en_kl = substrates["kl_en_cells_vs_en_inputs"]
    wn_kl = substrates["kl_wn_cells_vs_en_inputs"]
    t17_pass = en_kl < T17_BAR_MAX and wn_kl > en_kl
    verdict = "passed" if t17_pass else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-027",
        "verdict": verdict,
        "hypothesis": "T17 histogram-matching fidelity. SOM cell weights should distribute like training inputs.",
        "thresholds": {"T17_kl_max": T17_BAR_MAX},
        "measurements": substrates,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))
