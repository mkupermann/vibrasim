"""BET-057 — T41 Spiking Neural Network emergent selectivity.

PARADIGM SHIFT iteration. Tests brain-faithful substrate (LIF spiking
neurons + STDP) for EMERGENT property: do hidden neurons develop
SELECTIVE responses to specific audio patterns purely from STDP
learning?

If yes: emergent feature-detection, qualitatively different from
SOM/N-gram which we explicitly designed for it.
If no: SNN-STDP needs different parameters or longer training to
develop selectivity at this audio scale.

T41 protocol:
  1. Train SNN with STDP on 1000 EN chunks (~50s simulation per chunk
     at 50ms each = 50000ms = 50s sim time for the whole training).
  2. Test response: present 200 fresh EN chunks, measure hidden-neuron
     spike counts per chunk.
  3. Variance of spike-rates across chunks = selectivity index.
  4. Compare to random-init (same protocol, untrained substrate).

T41 bar (LOCKED):
  trained_variance > 2 * fresh_variance
  AND active_neurons > 5 (substrate isn't dead)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.snn_stdp import SNNConfig, initialise, run, measure_hidden_response, step

N_TICKS_TRAIN = 1_000
N_TICKS_TEST = 200
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
TARGET_RMS = 0.25

T41_VARIANCE_RATIO_MIN = 2.0
T41_MIN_ACTIVE_NEURONS = 5

OUT_DIR = Path.home() / ".eqmod/bet/BET-057"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


@pytest.fixture(scope="module")
def substrates():
    cfg = SNNConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
    )
    n_audio = (N_TICKS_TRAIN + N_TICKS_TEST) * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if n_audio > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    train = full[:N_TICKS_TRAIN * SAMPLES_PER_TICK].astype(np.float64)
    test = full[N_TICKS_TRAIN * SAMPLES_PER_TICK:
                (N_TICKS_TRAIN + N_TICKS_TEST) * SAMPLES_PER_TICK].astype(np.float64)

    # Trained substrate
    state_trained = run(cfg, N_TICKS_TRAIN, train)
    # Reset spike rates for measurement
    state_trained["spike_rates_hidden"] = np.zeros(cfg.n_hidden, dtype=np.int64)
    # Measure response on test chunks
    test_chunks = [test[k * SAMPLES_PER_TICK:(k + 1) * SAMPLES_PER_TICK] for k in range(N_TICKS_TEST)]
    responses_trained = measure_hidden_response(state_trained, test_chunks, cfg)

    # Fresh (untrained) substrate
    state_fresh = initialise(cfg)
    responses_fresh = measure_hidden_response(state_fresh, test_chunks, cfg)

    # Per-neuron variance across chunks (selectivity index)
    var_per_neuron_trained = responses_trained.var(axis=0)
    var_per_neuron_fresh = responses_fresh.var(axis=0)
    mean_var_trained = float(var_per_neuron_trained.mean())
    mean_var_fresh = float(var_per_neuron_fresh.mean())

    # Active neurons = neurons that fired at least once on test
    active_trained = int((responses_trained.sum(axis=0) > 0).sum())
    active_fresh = int((responses_fresh.sum(axis=0) > 0).sum())

    return dict(
        n_hidden=cfg.n_hidden, n_input=cfg.n_input,
        total_spikes_trained_train=state_trained["total_hidden_spikes"],
        active_neurons_trained=active_trained,
        active_neurons_fresh=active_fresh,
        mean_response_trained=float(responses_trained.mean()),
        mean_response_fresh=float(responses_fresh.mean()),
        variance_per_neuron_trained=mean_var_trained,
        variance_per_neuron_fresh=mean_var_fresh,
        variance_ratio=mean_var_trained / max(mean_var_fresh, 1e-9),
    )


def _verdict(s):
    var_ok = s["variance_ratio"] > T41_VARIANCE_RATIO_MIN
    active_ok = s["active_neurons_trained"] >= T41_MIN_ACTIVE_NEURONS
    return {**s, "T41_variance_ratio_ok": var_ok,
            "T41_active_ok": active_ok,
            "T41_pass": var_ok and active_ok}


def test_T41(substrates):
    m = _verdict(substrates)
    if not m["T41_pass"]:
        pytest.fail(
            f"BET-057 NULL T41 SNN emergence.\n"
            f"  active_trained: {m['active_neurons_trained']}/{m['n_hidden']} "
            f"(need >= {T41_MIN_ACTIVE_NEURONS}) pass={m['T41_active_ok']}\n"
            f"  active_fresh:   {m['active_neurons_fresh']}\n"
            f"  variance_trained: {m['variance_per_neuron_trained']:.4f}\n"
            f"  variance_fresh:   {m['variance_per_neuron_fresh']:.4f}\n"
            f"  ratio: {m['variance_ratio']:.4f} "
            f"(need > {T41_VARIANCE_RATIO_MIN}) pass={m['T41_variance_ratio_ok']}\n"
            f"  total_spikes_during_training: {m['total_spikes_trained_train']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T41_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-057",
        "verdict": verdict,
        "hypothesis": "T41 SNN-STDP substrate develops EMERGENT selective hidden-neuron responses via spike-timing learning. Brain-faithful paradigm (LIF + STDP, no backprop, no SOM). Bar: trained variance > 2*fresh AND active neurons >= 5.",
        "thresholds": {"T41_variance_ratio_min": T41_VARIANCE_RATIO_MIN,
                       "T41_min_active": T41_MIN_ACTIVE_NEURONS},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))
