"""BET-005 — Diagnostic instrumentation. NULL-by-design.

Per LOGBOOK 2026-05-23 scientific-rigor commitment. Locates WHERE in
the cognitive_map substrate the EN/WN content variance is lost.
Four instrumentation locations; result.json category="diagnostic";
does not consume a bet iteration slot.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
from world.flux.cognitive_map import (
    MapConfig, encode_sensor, initialise, position_hash,
)

N_TICKS = 10_000
SAMPLES_PER_TICK = 16
WN_SEED = 9999
TARGET_RMS = 0.25
N_BINS = 32

OUT_DIR = Path.home() / ".eqmod/bet/BET-005"
POSTMORTEM_DIR = Path.home() / ".eqmod/bet/postmortems"
MANIFEST_PATH = Path.home() / ".eqmod/training/EN/manifest.json"


def _make_white_noise(n: int, target_rms: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def _hist_kl(a: np.ndarray, b: np.ndarray, n_bins: int = N_BINS) -> float:
    a = a.ravel(); b = b.ravel()
    lo = min(a.min(), b.min()); hi = max(a.max(), b.max())
    if hi - lo < 1e-12:
        return 0.0
    edges = np.linspace(lo, hi, n_bins + 1)
    ha, _ = np.histogram(a, bins=edges)
    hb, _ = np.histogram(b, bins=edges)
    pa = (ha + 1.0) / (ha.sum() + n_bins)
    pb = (hb + 1.0) / (hb.sum() + n_bins)
    return 0.5 * (float(np.sum(pa * np.log(pa / pb))) + float(np.sum(pb * np.log(pb / pa))))


def _instrumented_run(cfg: MapConfig, audio: np.ndarray) -> dict:
    state = initialise(cfg)
    Lx, Ly, Lz = cfg.grid_dims
    sensors = np.empty((N_TICKS, cfg.n_features), dtype=np.float64)
    cell_hits = np.zeros((Lx, Ly, Lz), dtype=np.int64)
    for tick in range(N_TICKS):
        i0 = tick * SAMPLES_PER_TICK
        chunk = audio[i0:i0 + SAMPLES_PER_TICK]
        if chunk.size == 0:
            sensors[tick] = 0.0
            continue
        sensor = encode_sensor(chunk, cfg)
        sample_index = tick * SAMPLES_PER_TICK + (chunk.size - 1)
        sample_value = float(chunk[-1])
        x, y, z = position_hash(sample_index, sample_value, cfg)
        sensors[tick] = sensor
        cell_hits[x, y, z] += 1
        mu = state["mu"]; Lambda = state["Lambda"]; N = state["N"]
        e = sensor - mu[x, y, z]
        N[x, y, z] += 1
        mu[x, y, z] += e / float(N[x, y, z])
        Lambda[x, y, z] += cfg.alpha_precision_gain * (e * e)
    return {"state": state, "sensors": sensors, "cell_hits": cell_hits}


def _diagnose() -> dict:
    cfg = MapConfig()
    n_audio = N_TICKS * SAMPLES_PER_TICK
    full_eng = load_corpus_waveform_from_manifest(
        MANIFEST_PATH, sample_rate_hz=16000, corpus_rms_target=TARGET_RMS,
    )
    eng = full_eng[:n_audio].astype(np.float64)
    wn = _make_white_noise(n_audio, TARGET_RMS, WN_SEED)

    run_eng = _instrumented_run(cfg, eng)
    run_wn = _instrumented_run(cfg, wn)

    # Location 1: sensor distributions
    sensors_eng = run_eng["sensors"].ravel()
    sensors_wn = run_wn["sensors"].ravel()
    loc1_sensor_kl = _hist_kl(sensors_eng, sensors_wn)
    cos_per_tick = []
    for t in range(N_TICKS):
        a = run_eng["sensors"][t]; b = run_wn["sensors"][t]
        d = np.linalg.norm(a) * np.linalg.norm(b)
        cos_per_tick.append(float(np.dot(a, b) / (d + 1e-12)))
    loc1_mean_per_tick_cosine = float(np.mean(cos_per_tick))

    # Location 2: cell-hit histograms
    eng_hits = run_eng["cell_hits"].ravel().astype(np.float64)
    wn_hits = run_wn["cell_hits"].ravel().astype(np.float64)
    loc2_cell_visit_kl = _hist_kl(eng_hits, wn_hits)
    eng_only = float(np.mean((run_eng["cell_hits"] > 0) & (run_wn["cell_hits"] == 0)))
    wn_only = float(np.mean((run_wn["cell_hits"] > 0) & (run_eng["cell_hits"] == 0)))
    both = float(np.mean((run_eng["cell_hits"] > 0) & (run_wn["cell_hits"] > 0)))
    cells_hit_eng = int(np.sum(run_eng["cell_hits"] > 0))
    cells_hit_wn = int(np.sum(run_wn["cell_hits"] > 0))

    # Location 3: per-cell mu cosine over intersection
    mu_eng = run_eng["state"]["mu"]
    mu_wn = run_wn["state"]["mu"]
    both_mask = (run_eng["cell_hits"] > 0) & (run_wn["cell_hits"] > 0)
    coords = np.argwhere(both_mask)
    if coords.size > 0:
        per_cell_cos = []
        for (x, y, z) in coords:
            a = mu_eng[x, y, z]; b = mu_wn[x, y, z]
            d = np.linalg.norm(a) * np.linalg.norm(b)
            per_cell_cos.append(float(np.dot(a, b) / (d + 1e-12)))
        loc3_mean_per_cell_cosine = float(np.mean(per_cell_cos))
        loc3_min_per_cell_cosine = float(np.min(per_cell_cos))
        loc3_n_intersection_cells = int(len(per_cell_cos))
    else:
        loc3_mean_per_cell_cosine = float("nan")
        loc3_min_per_cell_cosine = float("nan")
        loc3_n_intersection_cells = 0

    # Location 4: per-cell L2 vs aggregate hist-KL
    if coords.size > 0:
        per_cell_l2 = []
        for (x, y, z) in coords:
            per_cell_l2.append(float(np.linalg.norm(mu_eng[x, y, z] - mu_wn[x, y, z])))
        loc4_mean_per_cell_l2 = float(np.mean(per_cell_l2))
        loc4_max_per_cell_l2 = float(np.max(per_cell_l2))
    else:
        loc4_mean_per_cell_l2 = 0.0
        loc4_max_per_cell_l2 = 0.0
    loc4_aggregate_hist_kl = _hist_kl(mu_eng, mu_wn)

    return {
        "loc1_sensor_distribution_kl": loc1_sensor_kl,
        "loc1_mean_per_tick_cosine": loc1_mean_per_tick_cosine,
        "loc2_cell_visit_kl": loc2_cell_visit_kl,
        "loc2_eng_only_cells_frac": eng_only,
        "loc2_wn_only_cells_frac": wn_only,
        "loc2_both_cells_frac": both,
        "loc2_cells_hit_eng": cells_hit_eng,
        "loc2_cells_hit_wn": cells_hit_wn,
        "loc3_mean_per_cell_cosine": loc3_mean_per_cell_cosine,
        "loc3_min_per_cell_cosine": loc3_min_per_cell_cosine,
        "loc3_n_intersection_cells": loc3_n_intersection_cells,
        "loc4_mean_per_cell_l2_divergence": loc4_mean_per_cell_l2,
        "loc4_max_per_cell_l2_divergence": loc4_max_per_cell_l2,
        "loc4_aggregate_histogram_kl": loc4_aggregate_hist_kl,
    }


def _diagnose_root_cause(m: dict) -> tuple[str, str]:
    A = m["loc1_sensor_distribution_kl"] < 0.05 and m["loc1_mean_per_tick_cosine"] > 0.9
    B = m["loc2_cell_visit_kl"] < 0.05 and m["loc2_both_cells_frac"] > 0.5
    c3 = m["loc3_mean_per_cell_cosine"]
    C = (not np.isnan(c3)) and c3 > 0.9
    D = m["loc4_mean_per_cell_l2_divergence"] > 0.3 and m["loc4_aggregate_histogram_kl"] < 0.05

    causes = []
    if A: causes.append("A (encoder produces statistically indistinguishable vectors)")
    if B: causes.append("B (position_hash distributes equally across EN/WN)")
    if C: causes.append("C (per-cell averaging converges to same values)")
    if D: causes.append("D (T2 measurement metric strips per-cell variance — analog R-22b)")

    if not causes:
        label = "no-single-locus"
        paragraph = (
            "None of the four pre-registered locus criteria fired strongly. "
            "Failure is likely a combination of weak effects below each criterion's threshold."
        )
    else:
        label = " + ".join(causes)
        paragraph = f"Dominant failure locus: {label}."
    return label, paragraph


def _write_postmortem(label: str, paragraph: str, m: dict) -> None:
    POSTMORTEM_DIR.mkdir(parents=True, exist_ok=True)
    md = (
        f"# BET-005 — Diagnostic Instrumentation Postmortem\n\n"
        f"**Run date**: 2026-05-23\n"
        f"**Dominant failure locus**: {label}\n\n"
        f"## Findings\n\n{paragraph}\n\n"
        f"## Full measurements\n\n```json\n"
        + json.dumps(m, indent=2, default=str) +
        f"\n```\n\n## Implied design for BET-006 (pre-registered ablation)\n\n"
        f"The ablation grid varies the factor identified by the dominant locus, "
        f"with all other factors fixed at the BET-002 baseline.\n"
    )
    (POSTMORTEM_DIR / "BET-005.md").write_text(md)


def _write_result_json(measurements: dict, label: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-005",
        "category": "diagnostic",
        "verdict": "null",
        "measurements": measurements,
        "dominant_failure_locus": label,
        "hypothesis": "Diagnostic only — locate where EN/WN signal disappears",
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2, default=str))


def test_diagnostic_runs_to_completion():
    m = _diagnose()
    label, paragraph = _diagnose_root_cause(m)
    _write_postmortem(label, paragraph, m)
    _write_result_json(m, label)
    assert (OUT_DIR / "result.json").exists()
    assert (POSTMORTEM_DIR / "BET-005.md").exists()
