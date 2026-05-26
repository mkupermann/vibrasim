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
    """081c: separate STDP params for feedback (lower depression)."""
    from brian2 import (NeuronGroup, PoissonGroup, Synapses, SpikeMonitor,
                        Network, Hz, ms, mV, defaultclock, prefs)
    from world.flux.brian2_audio_cortex import (
        AudioCortexConfig, AudioDaemonConfig, compute_mel_chunks, run_probe)
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

    # Build network with CUSTOM feedback STDP
    ns = {'tau_m': 20*ms, 'tau_e': 5*ms, 'tau_i': 10*ms,
          'v_rest': -70*mV, 'v_reset': -75*mV}

    def make_grp(n):
        g = NeuronGroup(n, '''
            dv/dt = (-(v - v_rest) + ge*(0*mV - v) + gi*(-80*mV - v)) / tau_m : volt (unless refractory)
            dge/dt = -ge / tau_e : 1
            dgi/dt = -gi / tau_i : 1
            v_thresh : volt''',
            threshold='v > v_thresh', reset='v = v_reset',
            refractory=5*ms, method='euler', namespace=ns)
        g.v = -70*mV; g.v_thresh = -54*mV
        return g

    inp = PoissonGroup(cc.n_input, rates=0*Hz)
    L4_E = make_grp(cc.n_L4_E); L4_I = make_grp(cc.n_L4_I)
    L23_E = make_grp(cc.n_L23_E); L23_I = make_grp(cc.n_L23_I)
    L5_E = make_grp(cc.n_L5_E); L5_I = make_grp(cc.n_L5_I)
    L6_E = make_grp(cc.n_L6_E); L6_I = make_grp(cc.n_L6_I)

    stdp_eqs = 'w : 1\ndApre/dt = -Apre / taupre : 1 (event-driven)\ndApost/dt = -Apost / taupost : 1 (event-driven)'
    on_pre = 'ge += w\nApre += dApre_val\nw = clip(w + Apost, 0, wmax)'
    on_post = 'Apost += dApost_val\nw = clip(w + Apre, 0, wmax)'

    sns = {'taupre': 20*ms, 'taupost': 20*ms, 'dApre_val': 0.01, 'dApost_val': -0.012, 'wmax': 2.0}
    sns_rec = {'taupre': 20*ms, 'taupost': 20*ms, 'dApre_val': 0.005, 'dApost_val': -0.006, 'wmax': 0.3}
    # KEY: lower depression on feedback
    sns_fb = {'taupre': 20*ms, 'taupost': 20*ms, 'dApre_val': 0.008, 'dApost_val': -0.004, 'wmax': 2.0}

    def plas(src, tgt, p, wl, wh, ns_):
        s = Synapses(src, tgt, model=stdp_eqs, on_pre=on_pre, on_post=on_post, namespace=ns_)
        s.connect(p=p); s.w = f'rand() * {wh-wl} + {wl}'; return s
    def sexc(src, tgt, p, wt):
        s = Synapses(src, tgt, 'w_s:1', on_pre='ge_post += w_s'); s.connect(p=p); s.w_s = wt; return s
    def sinh_(src, tgt, p, wt):
        s = Synapses(src, tgt, 'w_s:1', on_pre='gi_post += w_s'); s.connect(p=p); s.w_s = wt; return s

    print("Building network...", flush=True)
    syn_in = plas(inp, L4_E, cc.p_input, 0.5, 1.5, sns)
    syn_4r = plas(L4_E, L4_E, cc.p_rec_EE, 0.02, 0.1, sns_rec)
    syn_23r = plas(L23_E, L23_E, cc.p_rec_EE, 0.02, 0.1, sns_rec)
    syn_5r = plas(L5_E, L5_E, cc.p_rec_EE, 0.02, 0.1, sns_rec)
    syn_6r = plas(L6_E, L6_E, cc.p_rec_EE, 0.02, 0.1, sns_rec)
    syn_4_23 = plas(L4_E, L23_E, cc.p_ff, 0.2, 0.5, sns)
    syn_23_5 = plas(L23_E, L5_E, cc.p_ff, 0.2, 0.5, sns)
    syn_5_6 = plas(L5_E, L6_E, cc.p_ff, 0.2, 0.5, sns_fb)
    syn_6_4 = plas(L6_E, L4_E, cc.p_fb, 0.1, 0.3, sns_fb)

    ei_syn = []
    for src, tgt in [(L4_E,L4_I),(L23_E,L23_I),(L5_E,L5_I),(L6_E,L6_I)]:
        ei_syn.append(sexc(src, tgt, cc.p_EI, 0.5))
    for src, tgt in [(L4_I,L4_E),(L23_I,L23_E),(L5_I,L5_E),(L6_I,L6_E)]:
        ei_syn.append(sinh_(src, tgt, cc.p_IE, 1.0))

    mon_L5 = SpikeMonitor(L5_E, record=False)
    net = Network(inp, L4_E, L4_I, L23_E, L23_I, L5_E, L5_I, L6_E, L6_I,
                  syn_in, syn_4r, syn_23r, syn_5r, syn_6r,
                  syn_4_23, syn_23_5, syn_5_6, syn_6_4,
                  *ei_syn, mon_L5)

    n_syn = sum(int(len(s)) for s in [syn_in, syn_4r, syn_23r, syn_5r, syn_6r,
                                       syn_4_23, syn_23_5, syn_5_6, syn_6_4] + ei_syn)
    print(f"Network: {n_syn:,} synapses", flush=True)

    chunk_dur = cc.chunk_duration_ms * ms
    run_duration = 4 * 3600
    start_wall = time.time()
    last_eval = start_wall
    chunks_trained = 0
    audio_pos = 0
    metrics_log = []

    print("Training 4h...", flush=True)
    while time.time() - start_wall < run_duration:
        if audio_pos >= n_mel: audio_pos = 0
        inp.rates = (mel_chunks[audio_pos] * cc.input_rate_max_hz) * Hz
        audio_pos += 1
        net.run(chunk_dur)
        chunks_trained += 1

        now = time.time()
        if now - last_eval >= 3600:
            elapsed = now - start_wall
            l5_active = float(np.mean(np.array(mon_L5.count) > 0))
            metrics_log.append({"t": elapsed, "ch": chunks_trained, "l5": l5_active})
            (bet_dir / "metrics.json").write_text(json.dumps(metrics_log, indent=2))
            print(f"  h{elapsed/3600:.1f} | {chunks_trained} ch | L5 {l5_active:.3f}", flush=True)
            last_eval = now

    train_seconds = time.time() - start_wall
    print(f"Training done: {chunks_trained} chunks in {train_seconds/3600:.2f}h", flush=True)

    print("Probing...", flush=True)
    cfg = AudioDaemonConfig(cortex=cc, eval_n_probe_chunks=500, audio_manifest_path=MANIFEST)
    probe = run_probe(net, inp, mon_L5, mel_chunks, cc, cfg)

    weight_analysis = {}
    for name, syn in [('syn_in',syn_in),('syn_4_23',syn_4_23),('syn_23_5',syn_23_5),
                       ('syn_5_6',syn_5_6),('syn_6_4',syn_6_4)]:
        w = np.array(syn.w[:])
        weight_analysis[name] = {"gini": gini(w), "mean": float(w.mean()), "n": len(w)}

    result = {"train_seconds": train_seconds, "chunks_trained": chunks_trained,
              "probe": probe, "weight_analysis": weight_analysis, "metrics_log": metrics_log}

    fb_g = weight_analysis.get("syn_5_6", {}).get("gini", 1.0)
    distinct = probe.get("n_distinct_clusters", 0)
    sil = probe.get("silhouette_score", 0)
    l5_act = probe.get("L5_active_fraction", 0)
    verdicts = {"duration": train_seconds >= 4*3600*0.95, "l5_active": l5_act >= 0.5,
                "distinct": distinct >= 3, "silhouette": sil > 0.05, "feedback_alive": fb_g < 0.95}
    result["bar_verdicts"] = verdicts
    result["verdict"] = "PASS" if all(verdicts.values()) else "FAIL"

    print(f"Verdict: {result['verdict']}", flush=True)
    print(f"  L5={l5_act:.3f}, sil={sil:.4f}, distinct={distinct}, fb_gini={fb_g:.3f}", flush=True)
    return result


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
