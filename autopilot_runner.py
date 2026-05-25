"""Subprocess runner for individual BET experiments.

Called by autopilot.py as a fresh Python process to avoid Brian2 import
issues in long-running processes.

Usage: python autopilot_runner.py BET-081b /path/to/bet/dir
"""
import json
import os
import sys
import time
import warnings

warnings.filterwarnings('ignore')

import numpy as np
from pathlib import Path

REPO = Path(r"C:\Users\nicet\Documents\GitHub\vibrasim")
MANIFEST = Path.home() / ".eqmod" / "training" / "EN" / "manifest.json"


def gini(arr):
    arr = np.abs(np.sort(arr.flatten()))
    n = len(arr)
    if n == 0 or arr.sum() == 0: return 0.0
    idx = np.arange(1, n + 1)
    return float((2 * np.sum(idx * arr) / (n * np.sum(arr))) - (n + 1) / n)


def run_081b(bet_dir: Path, feedback_w_min: float = 0.05) -> dict:
    from brian2 import Hz, ms, mV, defaultclock, prefs
    from world.flux.brian2_audio_cortex import (
        AudioCortexConfig, AudioDaemonConfig, build_network,
        compute_mel_chunks, run_probe)
    from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest

    prefs.codegen.target = os.environ.get('BRIAN2_BACKEND', 'numpy')
    defaultclock.dt = 1.0 * ms

    cc = AudioCortexConfig()
    print("Loading audio...", flush=True)
    audio = load_corpus_waveform_from_manifest(
        MANIFEST, sample_rate_hz=cc.sample_rate_hz,
        corpus_rms_target=0.25).astype(np.float32)
    mel_chunks = compute_mel_chunks(audio, cc)
    n_mel = len(mel_chunks)

    print("Building network...", flush=True)
    net, comp = build_network(cc)
    inp = comp['input']
    mon_L5 = comp['mon_L5']

    # Apply w_min floor on feedback synapses
    syn_5_6 = comp['plastic_syn']['syn_5_6']
    syn_6_4 = comp['plastic_syn']['syn_6_4']
    w56 = np.array(syn_5_6.w[:])
    w56[w56 < feedback_w_min] = feedback_w_min
    syn_5_6.w = w56
    w64 = np.array(syn_6_4.w[:])
    w64[w64 < feedback_w_min] = feedback_w_min
    syn_6_4.w = w64

    n_E = sum(g.N for g in comp['excit'])
    n_I = comp['L4_I'].N + comp['L23_I'].N + comp['L5_I'].N + comp['L6_I'].N
    print(f"Network: {n_E}E + {n_I}I, {comp['n_syn']:,} synapses", flush=True)

    chunk_dur = cc.chunk_duration_ms * ms
    target_spk = cc.homeostasis_target_rate_hz * (cc.chunk_duration_ms / 1000.0)
    run_duration = 4 * 3600
    metrics_log = []
    start_wall = time.time()
    last_eval = start_wall
    chunks_trained = 0
    audio_pos = 0

    print(f"Training 4h...", flush=True)
    while True:
        elapsed = time.time() - start_wall
        if elapsed >= run_duration:
            break

        if audio_pos >= n_mel:
            audio_pos = 0
        inp.rates = (mel_chunks[audio_pos] * cc.input_rate_max_hz) * Hz
        audio_pos += 1
        net.run(chunk_dur)
        chunks_trained += 1

        # Homeostasis on L5
        if chunks_trained > 1 and chunks_trained % 10 == 0:
            grp = comp['L5_E']
            l5_counts = np.array(mon_L5.count).astype(float)
            rate_approx = l5_counts / chunks_trained
            adj = cc.homeostasis_eta_mv * (rate_approx - target_spk) * 0.01
            cur = np.asarray(grp.v_thresh[:]).astype(float) * 1000.0
            cur += adj
            cur = np.clip(cur, cc.homeostasis_thresh_min_mv, cc.homeostasis_thresh_max_mv)
            grp.v_thresh = cur * mV

        # Enforce w_min on feedback every 100 chunks
        if chunks_trained % 100 == 0:
            for syn in [syn_5_6, syn_6_4]:
                w = np.array(syn.w[:])
                w[w < feedback_w_min] = feedback_w_min
                syn.w = w

        now = time.time()
        if now - last_eval >= 3600:
            l5_active = float(np.mean(np.array(mon_L5.count) > 0))
            rate = chunks_trained / max(elapsed, 1)
            entry = {"t": elapsed, "ch": chunks_trained, "l5": l5_active}
            metrics_log.append(entry)
            (bet_dir / "metrics.json").write_text(json.dumps(metrics_log, indent=2))
            print(f"  h{elapsed/3600:.1f} | {chunks_trained} ch ({rate:.2f}/s) | L5 {l5_active:.3f}", flush=True)
            last_eval = now

    train_seconds = time.time() - start_wall
    print(f"Training done: {chunks_trained} chunks in {train_seconds/3600:.2f}h", flush=True)

    # Probe
    print("Probing...", flush=True)
    cfg = AudioDaemonConfig(cortex=cc, eval_n_probe_chunks=500, audio_manifest_path=MANIFEST)
    probe = run_probe(net, inp, mon_L5, mel_chunks, cc, cfg)

    # Weight analysis
    weight_analysis = {}
    for name, syn in comp['plastic_syn'].items():
        w = np.array(syn.w[:])
        weight_analysis[name] = {"gini": gini(w), "mean": float(w.mean()), "n": len(w)}

    result = {
        "train_seconds": train_seconds, "chunks_trained": chunks_trained,
        "probe": probe, "weight_analysis": weight_analysis,
        "metrics_log": metrics_log,
    }

    # Evaluate bars
    fb_gini = weight_analysis.get("syn_5_6", {}).get("gini", 1.0)
    distinct = probe.get("n_distinct_clusters", 0)
    sil = probe.get("silhouette_score", 0)
    l5_act = probe.get("L5_active_fraction", 0)

    verdicts = {
        "duration": train_seconds >= 4 * 3600 * 0.95,
        "l5_active": l5_act >= 0.50,
        "distinct": distinct >= 3,
        "silhouette": sil > 0.05,
        "feedback_alive": fb_gini < 0.95,
    }
    result["bar_verdicts"] = verdicts
    result["verdict"] = "PASS" if all(verdicts.values()) else "FAIL"

    print(f"Verdict: {result['verdict']}", flush=True)
    print(f"  L5 active: {l5_act:.3f}, sil: {sil:.4f}, distinct: {distinct}, fb_gini: {fb_gini:.3f}", flush=True)

    return result


def run_081c(bet_dir: Path) -> dict:
    """081c: separate STDP params. TODO: implement when 081b is done."""
    return {"verdict": "NOT_IMPLEMENTED"}


def run_081d(bet_dir: Path) -> dict:
    """081d: homeostatic scaling. Reuse 081b with lower w_min."""
    return run_081b(bet_dir, feedback_w_min=0.03)


def _save_json(path, data):
    def _c(o):
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, (np.floating,)): return float(o)
        if isinstance(o, np.ndarray): return o.tolist()
        return o
    Path(path).write_text(json.dumps(data, indent=2, default=_c))


if __name__ == "__main__":
    name = sys.argv[1]
    bet_dir = Path(sys.argv[2])
    bet_dir.mkdir(parents=True, exist_ok=True)

    print(f"Runner: {name} -> {bet_dir}", flush=True)

    if name == "BET-081b":
        result = run_081b(bet_dir)
    elif name == "BET-081c":
        result = run_081c(bet_dir)
    elif name == "BET-081d":
        result = run_081d(bet_dir)
    else:
        result = {"verdict": "UNKNOWN", "error": f"unknown experiment {name}"}

    _save_json(bet_dir / "result.json", result)
    print(f"Result saved to {bet_dir / 'result.json'}", flush=True)
