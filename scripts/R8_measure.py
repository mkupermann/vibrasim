"""R-8 measurement driver — runs both trained + control sessions at the
pre-registered n_ticks_train_min=60_000, captures alignment numbers, and
writes a JSON report. Not a test; the tests are the locked acceptance.

Run: .venv/bin/python scripts/R8_measure.py
Output: docs/flux/R8_measurement.json
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from agent.flux.corpus_spectrum import compute_corpus_log_power_spectrum
from agent.flux.training_metric import corpus_alignment_index
from agent.flux.training_run import (
    TrainingRunConfig,
    load_corpus_waveform_from_manifest,
    run_training_session,
)


def main():
    cfg = TrainingRunConfig()
    print(f"R-8 measurement: n_ticks_train={cfg.n_ticks_train}, "
          f"alignment_thresh_train={cfg.alignment_thresh_train}, "
          f"alignment_thresh_control={cfg.alignment_thresh_control}, "
          f"margin_min={cfg.margin_min}, "
          f"n_bridges_min_alive_train={cfg.n_bridges_min_alive_train}, "
          f"n_bridges_min_alive_control={cfg.n_bridges_min_alive_control}")

    # Pre-compute corpus spectrum once (cache).
    print("loading corpus + computing reference spectrum ...")
    t0 = time.time()
    corpus_wave = load_corpus_waveform_from_manifest(
        cfg.manifest_path,
        stage_order=cfg.stage_order,
        sample_rate_hz=cfg.cochlea_cfg.sample_rate_hz,
    )
    p_corpus = compute_corpus_log_power_spectrum(
        corpus_wave,
        sample_rate_hz=cfg.cochlea_cfg.sample_rate_hz,
        n_freq_bins=cfg.n_freq_bins,
        freq_band_hz=cfg.freq_band_hz,
    )
    corpus_rms = float(np.sqrt(np.mean(corpus_wave * corpus_wave)))
    print(f"  corpus loaded: {corpus_wave.size} samples, "
          f"RMS={corpus_rms:.4f}, spectrum top bin={int(np.argmax(p_corpus))}, "
          f"corpus prep wallclock={time.time()-t0:.1f}s")

    results = {
        "config": {
            "n_ticks_train": cfg.n_ticks_train,
            "alignment_thresh_train": cfg.alignment_thresh_train,
            "alignment_thresh_control": cfg.alignment_thresh_control,
            "margin_min": cfg.margin_min,
            "n_bridges_min_alive_train": cfg.n_bridges_min_alive_train,
            "n_bridges_min_alive_control": cfg.n_bridges_min_alive_control,
            "seed_train": cfg.seed_train,
            "seed_control": cfg.seed_control,
            "n_freq_bins": cfg.n_freq_bins,
            "corpus_rms": corpus_rms,
        },
    }

    for kind in ("train", "control"):
        print(f"running {kind} session ({cfg.n_ticks_train} ticks) ...")
        t0 = time.time()
        r = run_training_session(cfg, input_kind=kind)
        dt = time.time() - t0
        n_alive_bridges = int(r.bridges.alive.sum())
        n_alive_nodes = int(r.nodes.alive.sum())
        n_alive_quanta = int(r.quanta.alive.sum())
        alignment = corpus_alignment_index(
            r.bridges, r.nodes, p_corpus,
            n_freq_bins=cfg.n_freq_bins,
            freq_band_hz=cfg.freq_band_hz,
        )
        audit_residual = float(r.audit.residual())
        results[kind] = {
            "wallclock_seconds": dt,
            "ms_per_tick": dt / cfg.n_ticks_train * 1000.0,
            "n_alive_bridges": n_alive_bridges,
            "n_alive_nodes": n_alive_nodes,
            "n_alive_quanta": n_alive_quanta,
            "corpus_alignment_index": float(alignment),
            "audit_residual": audit_residual,
            "waveform_rms": float(r.waveform_rms),
        }
        print(f"  {kind} done: wallclock={dt:.1f}s ({dt/cfg.n_ticks_train*1000:.2f}ms/tick), "
              f"alive bridges={n_alive_bridges}, nodes={n_alive_nodes}, "
              f"quanta={n_alive_quanta}, alignment={alignment:.4f}, "
              f"audit_residual={audit_residual:.3e}")

    margin = results["train"]["corpus_alignment_index"] - results["control"]["corpus_alignment_index"]
    results["margin"] = margin

    # Verdict logic mirroring the test assertions:
    failures = []
    if results["train"]["n_alive_bridges"] < cfg.n_bridges_min_alive_train:
        failures.append(
            f"trained n_bridges={results['train']['n_alive_bridges']} < "
            f"{cfg.n_bridges_min_alive_train}"
        )
    if results["train"]["corpus_alignment_index"] < cfg.alignment_thresh_train:
        failures.append(
            f"trained alignment={results['train']['corpus_alignment_index']:.4f} < "
            f"{cfg.alignment_thresh_train}"
        )
    if results["control"]["n_alive_bridges"] < cfg.n_bridges_min_alive_control:
        failures.append(
            f"control n_bridges={results['control']['n_alive_bridges']} < "
            f"{cfg.n_bridges_min_alive_control}"
        )
    if results["control"]["corpus_alignment_index"] >= cfg.alignment_thresh_control:
        failures.append(
            f"control alignment={results['control']['corpus_alignment_index']:.4f} >= "
            f"{cfg.alignment_thresh_control}"
        )
    if margin < cfg.margin_min:
        failures.append(f"margin={margin:.4f} < {cfg.margin_min}")
    results["verdict"] = "PASS" if not failures else "NULL"
    results["failures"] = failures

    print(f"margin train-control={margin:.4f}, verdict={results['verdict']}")
    if failures:
        for f in failures:
            print(f"  - {f}")

    out_path = Path("docs/flux/R8_measurement.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
