"""R-13 bridge-weight spectrum acceptance — pre-registered gate.

Pre-registered in ``.eqmod/autopilot/QUEUE.yaml::R-13``:

  ``test_bridge_spectrum_observable_constructs``     PASSES
  ``test_bridge_spectrum_zero_on_empty_substrate``    PASSES
  ``test_bridge_spectrum_differs_under_different_audio`` PASSES

The third gate runs two 50k-tick encoder-free substrates (one on
R-7 English audio Stage 1, one on matched-RMS white noise) and asserts
KL > 0.1 between their bridge-weight spectra. The KL threshold is locked;
the grid size for these short runs (30x15x8) is an implementation
choice and is documented in the R-13 LOGBOOK entry.

NULL is a valid outcome per autopilot charter — do not retune the 0.1
threshold or the grid/seed/duration parameters after seeing results.
"""
from __future__ import annotations

import numpy as np
import pytest

from agent.flux.bridge_spectrum import (
    DEFAULT_FREQ_RANGE_LOG_HZ,
    DEFAULT_N_FREQ_BINS,
    DEFAULT_N_WEIGHT_BINS,
    DEFAULT_WEIGHT_RANGE,
    bridge_spectrum_kl,
    bridge_weight_spectrum,
    load_english_stage1_segment,
    make_white_noise,
    n_populated_bins,
    run_short_encoder_free_substrate,
)
from world.flux.bridges import Bridges
from world.flux.structures import Nodes


# ---------- R-13 acceptance: spectrum constructs --------------------


def test_bridge_spectrum_observable_constructs():
    """Synthetic substrate with diverse (freq, weight) bridges →
    >= 32 of the 128 bins populated and histogram sums to 1.0.

    Construction: 8 freq levels × 16 weight levels = 128 unique
    (freq, weight) combos, one bridge each. Each should fall into its
    own (freq_bin, weight_bin) cell, so all 128 cells receive mass.
    The >=32 acceptance is the locked floor; this synthetic substrate
    exceeds it by 4x to guard against off-by-one binning issues.
    """
    nodes = Nodes(max_nodes=64)
    bridges = Bridges(max_bridges=256)

    freq_lo, freq_hi = DEFAULT_FREQ_RANGE_LOG_HZ
    weight_lo, weight_hi = DEFAULT_WEIGHT_RANGE
    # Place freqs strictly inside each bin (centre points).
    freq_centres = np.linspace(
        freq_lo + (freq_hi - freq_lo) / (2 * DEFAULT_N_FREQ_BINS),
        freq_hi - (freq_hi - freq_lo) / (2 * DEFAULT_N_FREQ_BINS),
        DEFAULT_N_FREQ_BINS,
    )
    weight_centres = np.linspace(
        weight_lo + (weight_hi - weight_lo) / (2 * DEFAULT_N_WEIGHT_BINS),
        weight_hi - (weight_hi - weight_lo) / (2 * DEFAULT_N_WEIGHT_BINS),
        DEFAULT_N_WEIGHT_BINS,
    )

    # One node per freq centre — every bridge in that freq's group
    # has both endpoints at this node, so the "mean" endpoint freq
    # is the node's freq exactly.
    node_slots = []
    for f in freq_centres:
        slot = nodes.add(pos=[0.0, 0.0, 0.0], energy=1.0, freq=float(f),
                         born_tick=0)
        assert slot >= 0
        node_slots.append(slot)

    for i, slot in enumerate(node_slots):
        for w in weight_centres:
            b = bridges.add(src=slot, dst=slot, weight=float(w), born_tick=0)
            assert b >= 0

    spectrum = bridge_weight_spectrum(nodes, bridges)
    assert spectrum.shape == (DEFAULT_N_FREQ_BINS, DEFAULT_N_WEIGHT_BINS)
    assert not np.isnan(spectrum).any(), "spectrum contains NaN"
    total = float(spectrum.sum())
    assert abs(total - 1.0) < 1e-9, (
        f"spectrum not normalised: sum={total}"
    )
    populated = n_populated_bins(spectrum)
    assert populated >= 32, (
        f"only {populated} bins populated; pre-registered floor is 32"
    )


# ---------- R-13 acceptance: empty substrate handled ----------------


def test_bridge_spectrum_zero_on_empty_substrate():
    """Zero-node substrate returns an all-zero array, not NaN/error."""
    nodes = Nodes(max_nodes=4)
    bridges = Bridges(max_bridges=4)
    assert nodes.n_alive() == 0
    assert bridges.n_alive() == 0

    spectrum = bridge_weight_spectrum(nodes, bridges)
    assert spectrum.shape == (DEFAULT_N_FREQ_BINS, DEFAULT_N_WEIGHT_BINS)
    assert not np.isnan(spectrum).any(), "spectrum must not contain NaN"
    assert float(spectrum.sum()) == 0.0, (
        "empty substrate must yield all-zero spectrum"
    )


# ---------- R-13 acceptance: audio vs white-noise KL > 0.1 ----------


@pytest.mark.slow
def test_bridge_spectrum_differs_under_different_audio():
    """50k-tick English-audio vs matched-RMS white-noise substrates:
    KL between their bridge-weight spectra must exceed 0.1.

    Locked parameters (pre-registered, no retuning):
    - n_ticks = 50_000
    - audio = R-7 Stage 1 English corpus, RMS-normalised to 0.25
    - white-noise = Gaussian, same RMS, fixed seed
    - KL threshold = 0.1 (nats)

    Grid size (30x15x8) and per-run RNG seed are implementation choices
    documented in the LOGBOOK; both runs use identical substrate config
    so the bridge-spectrum comparison is fair.
    """
    SR = 16_000
    SPT = 16
    N_TICKS = 50_000
    N_SAMPLES = N_TICKS * SPT
    TARGET_RMS = 0.25

    english = load_english_stage1_segment(N_SAMPLES, target_rms=TARGET_RMS)
    if english is None:
        pytest.skip(
            "R-7 English corpus manifest not available on this machine"
        )

    white = make_white_noise(N_SAMPLES, target_rms=TARGET_RMS, seed=9999)

    eng_rms = float(np.sqrt(np.mean(english * english)))
    white_rms = float(np.sqrt(np.mean(white * white)))
    assert abs(eng_rms - white_rms) / max(eng_rms, 1e-12) < 0.01, (
        f"RMS mismatch between English ({eng_rms:.4f}) and white-noise "
        f"({white_rms:.4f}) — both must be ~{TARGET_RMS} for a fair test"
    )

    nodes_eng, bridges_eng = run_short_encoder_free_substrate(
        waveform=english, n_ticks=N_TICKS, seed=4242,
    )
    nodes_wht, bridges_wht = run_short_encoder_free_substrate(
        waveform=white, n_ticks=N_TICKS, seed=4242,
    )

    spec_eng = bridge_weight_spectrum(nodes_eng, bridges_eng)
    spec_wht = bridge_weight_spectrum(nodes_wht, bridges_wht)

    # Both runs must have produced bridges or the comparison is moot.
    assert int(bridges_eng.alive.sum()) > 0, (
        "English-trained substrate produced no alive bridges — "
        "implementation regression or grid/duration mis-spec"
    )
    assert int(bridges_wht.alive.sum()) > 0, (
        "White-noise-trained substrate produced no alive bridges — "
        "implementation regression or grid/duration mis-spec"
    )

    kl = bridge_spectrum_kl(spec_eng, spec_wht)
    # Symmetric report for diagnostic clarity (we test the asymmetric
    # direction below — symmetric is informational).
    kl_rev = bridge_spectrum_kl(spec_wht, spec_eng)
    kl_sym = 0.5 * (kl + kl_rev)
    print(
        f"R-13 KL(eng||wht)={kl:.4f}  KL(wht||eng)={kl_rev:.4f}  "
        f"sym={kl_sym:.4f}  "
        f"bridges_eng={int(bridges_eng.alive.sum())} "
        f"bridges_wht={int(bridges_wht.alive.sum())}"
    )

    assert kl > 0.1, (
        f"bridge spectra do not distinguish English vs white noise: "
        f"KL(eng||wht)={kl:.4f} (threshold 0.1, sym={kl_sym:.4f}). "
        f"bridges_eng={int(bridges_eng.alive.sum())} "
        f"bridges_wht={int(bridges_wht.alive.sum())}. "
        f"Verdict: NULL per autopilot charter — no retuning."
    )
