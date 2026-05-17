"""R-8 quick diagnostic — trained-only, 30_000 ticks, prints progress.

Runs the trained session at half the locked n_ticks_train_min so we get
observable substrate dynamics within wallclock budget. Outputs measured
numbers so the LOGBOOK can document mechanism even when the full
acceptance run times out under postflight's 30-min pytest cap.

Run: .venv/bin/python -u scripts/R8_diag.py
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from agent.flux.corpus_spectrum import compute_corpus_log_power_spectrum
from agent.flux.training_metric import corpus_alignment_index
from agent.flux.training_run import (
    Cochlea,
    cochlea_inject,
    step_resonators,
    TrainingRunConfig,
    load_corpus_waveform_from_manifest,
    make_corpus_waveform,
    make_control_waveform,
)
from world.flux import dynamics
from world.flux.audit import EnergyAuditor
from world.flux.bridges import Bridges
from world.flux.grid import Grid
from world.flux.quantum import Quanta
from world.flux.structures import Nodes


def run_session_instrumented(cfg, input_kind, n_ticks, snapshot_every=2000):
    """Run a session with periodic progress prints. Mirrors
    `run_training_session` but allows n_ticks < locked min (diagnostic).
    """
    sr = cfg.cochlea_cfg.sample_rate_hz
    samples_per_tick = cfg.cochlea_cfg.n_audio_samples_per_tick
    n_audio_total = n_ticks * samples_per_tick

    if input_kind == "train":
        waveform = make_corpus_waveform(cfg, n_samples=n_audio_total)
        seed = cfg.seed_train
    else:
        corpus_for_rms = load_corpus_waveform_from_manifest(
            cfg.manifest_path,
            stage_order=cfg.stage_order,
            sample_rate_hz=cfg.cochlea_cfg.sample_rate_hz,
        )
        rms_corpus = float(np.sqrt(np.mean(corpus_for_rms * corpus_for_rms)))
        waveform = make_control_waveform(
            cfg, n_samples=n_audio_total, target_rms=rms_corpus,
        )
        seed = cfg.seed_control

    rng = np.random.default_rng(seed)
    grid = Grid(dims=cfg.grid_dims, voxel_size=cfg.voxel_size,
                T_smoothing=0.1)
    quanta = Quanta(max_quanta=cfg.max_quanta)
    nodes = Nodes(max_nodes=cfg.max_nodes)
    bridges = Bridges(max_bridges=cfg.max_bridges)
    audit = EnergyAuditor(
        quanta=quanta, nodes=nodes, bridges=bridges, tol=cfg.audit_tol,
    )
    audit.record_initial()
    bank = Cochlea(cfg.cochlea_cfg)

    t_start = time.time()
    last_print = t_start
    for tick_idx in range(n_ticks):
        chunk = waveform[
            tick_idx * samples_per_tick
            : (tick_idx + 1) * samples_per_tick
        ]
        step_resonators(bank, samples=chunk)
        e_injected = cochlea_inject(
            quanta, grid, bank, cfg.cochlea_cfg, rng=rng,
        )
        audit.record_injection(e_injected)
        exported, binding_heat, decay_heat = dynamics.tick(
            quanta=quanta, grid=grid, dt=cfg.dt,
            injector=None, nodes=nodes,
            binding_cfg=cfg.binding_cfg,
            decay_cfg=cfg.decay_cfg,
            bridges=bridges,
            plasticity_cfg=cfg.plasticity_cfg,
            thermal_cfg=cfg.thermal_cfg,
            rng=rng, tick_index=tick_idx,
        )
        audit.record_export(exported)
        audit.record_binding_heat(binding_heat)
        audit.record_decay_heat(decay_heat)
        audit.step()

        if (tick_idx + 1) % snapshot_every == 0:
            now = time.time()
            n_q = int(quanta.alive.sum())
            n_n = int(nodes.alive.sum())
            n_b = int(bridges.alive.sum())
            print(f"  tick {tick_idx+1}/{n_ticks}: "
                  f"q={n_q} n={n_n} b={n_b} "
                  f"elapsed={now-t_start:.1f}s "
                  f"window={now-last_print:.1f}s",
                  flush=True)
            last_print = now
    return quanta, nodes, bridges, audit, time.time() - t_start


def main():
    n_ticks = 30_000
    cfg = TrainingRunConfig()
    print(f"R-8 diagnostic: n_ticks={n_ticks} (HALF of locked min "
          f"{cfg.n_ticks_train_min}). RMS=0.25 per-stage corpus normalisation.",
          flush=True)

    # Pre-compute corpus spectrum.
    print("loading corpus + computing reference spectrum ...", flush=True)
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
    print(f"  corpus: {corpus_wave.size/cfg.cochlea_cfg.sample_rate_hz:.0f}s, "
          f"RMS={corpus_rms:.4f}, top-bin={int(np.argmax(p_corpus))}, "
          f"wallclock={time.time()-t0:.1f}s",
          flush=True)
    # Release big corpus buffer; only spectrum is needed downstream.
    del corpus_wave

    out = {"config_n_ticks": n_ticks, "corpus_rms": corpus_rms}

    for kind in ("train", "control"):
        print(f"running {kind} session ({n_ticks} ticks) ...", flush=True)
        q, n, b, a, dt = run_session_instrumented(cfg, kind, n_ticks)
        n_q = int(q.alive.sum())
        n_n = int(n.alive.sum())
        n_b = int(b.alive.sum())
        alignment = corpus_alignment_index(
            b, n, p_corpus,
            n_freq_bins=cfg.n_freq_bins, freq_band_hz=cfg.freq_band_hz,
        )
        out[kind] = {
            "wallclock_seconds": dt,
            "ms_per_tick": dt / n_ticks * 1000.0,
            "n_alive_bridges": n_b,
            "n_alive_nodes": n_n,
            "n_alive_quanta": n_q,
            "corpus_alignment_index": float(alignment),
            "audit_residual": float(a.residual()),
        }
        print(f"  {kind} done: wallclock={dt:.1f}s, "
              f"alive b={n_b} n={n_n} q={n_q}, alignment={alignment:.4f}",
              flush=True)

    out["margin_at_30k"] = (
        out["train"]["corpus_alignment_index"]
        - out["control"]["corpus_alignment_index"]
    )
    out_path = Path("docs/flux/R8_diag_30k.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
