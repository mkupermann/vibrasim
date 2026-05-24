"""BET-046 — ART substrate self-allocation test.

T30 — substrate decides its own capacity. ART allocates new category
cells when input doesn't match existing categories (vigilance threshold).
Tests genuine "selbstständig" property unavailable in fixed-grid SOMs.

Pre-data prediction:
  - Allocations grow non-linearly: many early, fewer later as categories
    stabilize.
  - EN training produces FEWER cells than WN training (EN is more
    structured, repeats categories).
  - Cell count saturates well below max_cells.

T30 bar (LOCKED):
  - Substrate allocates at least 20 cells after 10k training chunks
    (substrate IS adapting, not just allocating one cell)
  - Substrate allocates fewer than max_cells (vigilance is meaningful)
  - n_cells_EN < n_cells_WN (EN more structured)

If all 3: ART substrate demonstrates self-determined capacity allocation
that's class-sensitive.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.art_substrate import ARTConfig, run

N_TICKS = 10_000
SAMPLES_PER_TICK = 16
FFT_BANDS = 8
N_FEATURES = 2 + FFT_BANDS
WN_SEED = 9999
TARGET_RMS = 0.25

T30_MIN_CELLS = 20

OUT_DIR = Path.home() / ".eqmod/bet/BET-046"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


@pytest.fixture(scope="module")
def substrates():
    cfg = ARTConfig(
        samples_per_tick=SAMPLES_PER_TICK, fft_bands=FFT_BANDS,
        n_features=N_FEATURES,
    )
    n_audio = N_TICKS * SAMPLES_PER_TICK

    full = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    if n_audio > full.shape[0]:
        raise RuntimeError("R-7 corpus too short")
    eng_train = full[:n_audio].astype(np.float64)
    wn_train = _make_wn(n_audio, TARGET_RMS, WN_SEED)

    state_en = run(cfg, N_TICKS, eng_train)
    state_wn = run(cfg, N_TICKS, wn_train)

    return dict(
        cfg=cfg,
        n_cells_en=state_en["weights"].shape[0],
        n_resonances_en=state_en["n_resonances"],
        n_allocations_en=state_en["n_allocations"],
        n_cells_wn=state_wn["weights"].shape[0],
        n_resonances_wn=state_wn["n_resonances"],
        n_allocations_wn=state_wn["n_allocations"],
        max_cells=cfg.max_cells,
        vigilance=cfg.vigilance,
    )


def _verdict(s):
    en_grew = s["n_cells_en"] >= T30_MIN_CELLS
    not_saturated = s["n_cells_en"] < s["max_cells"] and s["n_cells_wn"] < s["max_cells"]
    en_less_than_wn = s["n_cells_en"] < s["n_cells_wn"]
    pass_ = en_grew and not_saturated and en_less_than_wn
    return {
        **s,
        "T30_en_grew_to_at_least_20": en_grew,
        "T30_not_saturated_to_max": not_saturated,
        "T30_en_less_than_wn": en_less_than_wn,
        "T30_pass": pass_,
    }


def test_T30(substrates):
    m = _verdict(substrates)
    if not m["T30_pass"]:
        pytest.fail(
            f"BET-046 NULL T30 ART substrate.\n"
            f"  n_cells (EN): {m['n_cells_en']} (need >= {T30_MIN_CELLS})\n"
            f"  n_cells (WN): {m['n_cells_wn']}\n"
            f"  max_cells: {m['max_cells']}\n"
            f"  resonances EN: {m['n_resonances_en']}, allocations EN: {m['n_allocations_en']}\n"
            f"  EN<WN check: {m['T30_en_less_than_wn']}"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(substrates):
    yield
    m = _verdict(substrates)
    verdict = "passed" if m["T30_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-046",
        "verdict": verdict,
        "hypothesis": "T30 ART self-allocating substrate (Grossberg 1987). Substrate decides own capacity via vigilance threshold. Bar: at least 20 cells on EN, not saturated, EN less cells than WN (EN more structured).",
        "thresholds": {"T30_min_cells": T30_MIN_CELLS, "T30_vigilance": substrates["vigilance"]},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))
