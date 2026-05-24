"""BET-070 — T54 Brian2 SNN temporal sequence sensitivity.

Stufe 3 des Proof. Test if Brian2 SNN+STDP develops temporal-sequence
detectors. Present audio chunks in patterns:
  Class 0: regular repeating (EN-EN-EN-...)
  Class 1: alternating (EN-WN-EN-WN-...)

Both classes use SAME chunks (EN and WN samples). The only difference
is TEMPORAL ORDER. If substrate develops different L2 firing patterns
for the two sequence-types, it captures temporal structure beyond
per-chunk features.

T54 bar (LOCKED):
  L2 prototype classification accuracy on sequence-class > 0.65
  (need temporal context to beat chance, NOT chunk-level features).
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pytest

warnings.filterwarnings('ignore')

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.brian2_hierarchical import Brian2HierarchicalConfig, train_and_collect_patterns

N_SEQUENCES_PER_CLASS = 50
SEQUENCE_LENGTH = 4
N_TEST_PER_CLASS = 20
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
TARGET_RMS = 0.25

T54_ACCURACY_MIN = 0.65

OUT_DIR = Path.home() / ".eqmod/bet/BET-070"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _build_sequence_audio(en_pool, wn_pool, sequence_type, length, rng):
    """Build audio sequence:
      sequence_type 0 = repeating (EN-EN-EN-EN or WN-WN-WN-WN)
      sequence_type 1 = alternating (EN-WN-EN-WN or WN-EN-WN-EN)
    Returns concatenated audio.
    """
    chunks = []
    if sequence_type == 0:  # repeating
        # Pick one class randomly, repeat it
        class_chunks = en_pool if rng.random() < 0.5 else wn_pool
        for i in range(length):
            idx = rng.integers(0, len(class_chunks))
            chunks.append(class_chunks[idx])
    else:  # alternating
        start_en = rng.random() < 0.5
        for i in range(length):
            pool = en_pool if (start_en == (i % 2 == 0)) else wn_pool
            idx = rng.integers(0, len(pool))
            chunks.append(pool[idx])
    return np.concatenate(chunks)


@pytest.fixture(scope="module")
def substrates():
    class _Cfg:
        n_features = N_FEATURES
        fft_bands = FFT_BANDS
        samples_per_tick = SAMPLES_PER_TICK
    encoder_cfg = _Cfg()

    n_pool = 100 * SAMPLES_PER_TICK
    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    en_audio = full[:n_pool].astype(np.float64)
    wn_audio = _make_wn(n_pool, TARGET_RMS, WN_SEED)

    en_pool = [en_audio[k*SAMPLES_PER_TICK:(k+1)*SAMPLES_PER_TICK] for k in range(100)]
    wn_pool = [wn_audio[k*SAMPLES_PER_TICK:(k+1)*SAMPLES_PER_TICK] for k in range(100)]

    # Build train/test sequences
    train_dict = {0: [], 1: []}
    test_dict = {0: [], 1: []}
    rng = np.random.default_rng(42)
    for _ in range(N_SEQUENCES_PER_CLASS):
        train_dict[0].append(_build_sequence_audio(en_pool, wn_pool, 0, SEQUENCE_LENGTH, rng))
        train_dict[1].append(_build_sequence_audio(en_pool, wn_pool, 1, SEQUENCE_LENGTH, rng))
    for _ in range(N_TEST_PER_CLASS):
        test_dict[0].append(_build_sequence_audio(en_pool, wn_pool, 0, SEQUENCE_LENGTH, rng))
        test_dict[1].append(_build_sequence_audio(en_pool, wn_pool, 1, SEQUENCE_LENGTH, rng))

    # Use hierarchical substrate. Chunk duration = single SAMPLES_PER_TICK * sequence_length
    # Each "sequence" = SEQUENCE_LENGTH chunks concatenated
    cfg = Brian2HierarchicalConfig(chunk_duration_ms=200.0)  # longer for sequence
    result = train_and_collect_patterns(
        train_dict, test_dict, encoder_cfg,
        N_SEQUENCES_PER_CLASS, N_TEST_PER_CLASS, cfg,
    )

    L2_rep = result["L2_patterns_by_class"][0]
    L2_alt = result["L2_patterns_by_class"][1]

    proto_rep = L2_rep.mean(axis=0)
    proto_alt = L2_alt.mean(axis=0)
    correct = 0
    total = 0
    for p in L2_rep:
        d_rep = float(np.linalg.norm(p - proto_rep))
        d_alt = float(np.linalg.norm(p - proto_alt))
        if d_rep < d_alt: correct += 1
        total += 1
    for p in L2_alt:
        d_rep = float(np.linalg.norm(p - proto_rep))
        d_alt = float(np.linalg.norm(p - proto_alt))
        if d_alt < d_rep: correct += 1
        total += 1
    accuracy = correct / max(total, 1)

    return dict(
        sequence_length=SEQUENCE_LENGTH,
        n_train_sequences_per_class=N_SEQUENCES_PER_CLASS,
        L2_prototype_accuracy_sequence=accuracy,
        L2_mean_response_repeating=float(L2_rep.mean()),
        L2_mean_response_alternating=float(L2_alt.mean()),
        total_L1_spikes=result["total_L1_spikes"],
        total_L2_spikes=result["total_L2_spikes"],
    )


def _verdict(s):
    return {**s, "T54_pass": s["L2_prototype_accuracy_sequence"] > T54_ACCURACY_MIN}


def test_T54(substrates):
    m = _verdict(substrates)
    if not m["T54_pass"]:
        pytest.fail(
            f"BET-070 NULL T54 temporal sequence.\n"
            f"  sequence length: {m['sequence_length']}\n"
            f"  L2 prototype acc on sequence-type: {m['L2_prototype_accuracy_sequence']:.4f} "
            f"(need > {T54_ACCURACY_MIN})\n"
            f"  L2 mean response repeating: {m['L2_mean_response_repeating']:.4f}\n"
            f"  L2 mean response alternating: {m['L2_mean_response_alternating']:.4f}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T54_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-070",
        "verdict": verdict,
        "hypothesis": "T54 Brian2 SNN temporal sequence sensitivity. Same chunks, different temporal order: repeating vs alternating sequences. Tests if substrate captures sequence-level structure beyond per-chunk features. Bar: prototype acc > 0.65.",
        "thresholds": {"T54_accuracy_min": T54_ACCURACY_MIN},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))
