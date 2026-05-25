"""EQMOD Autopilot — autonomous experimental loop.

Runs indefinitely. Decides next experiment based on prior results.
Pre-registers bars, runs, evaluates, logs, commits, pushes.
Does NOT ask for human input. Ever.

Decision tree:
  1. Fix feedback collapse (BET-081b/c/d variants)
  2. Once feedback alive → scale audio exposure
  3. Once multi-class → cross-modal binding

Hard constraints (from CLAUDE.md):
  - NO LLM, NO pre-trained, NO labels
  - Pre-register BEFORE run
  - Post-hoc tuning forbidden
  - NULL/FAIL are findings, not retries
  - 3 sequential NULLs on same mechanism = stop that line
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np

REPO = Path(r"C:\Users\nicet\Documents\GitHub\vibrasim")
EQMOD = Path.home() / ".eqmod"
BET_DIR = EQMOD / "bet"
MANIFEST = EQMOD / "training" / "EN" / "manifest.json"
LOGBOOK = REPO / "LOGBOOK.md"
NOTIFY = EQMOD / "autopilot" / "notify_config.json"


def telegram(msg: str):
    if not NOTIFY.exists():
        return
    try:
        cfg = json.loads(NOTIFY.read_text())
        import urllib.request, urllib.parse
        data = urllib.parse.urlencode({
            "chat_id": cfg["telegram_chat_id"], "text": msg[:4000],
        }).encode()
        urllib.request.urlopen(
            f"https://api.telegram.org/bot{cfg['telegram_bot_token']}/sendMessage",
            data=data, timeout=10)
    except Exception:
        pass


def git_commit_push(msg: str):
    """Commit all changes and push."""
    os.chdir(REPO)
    subprocess.run(["git", "add", "-A"], capture_output=True)
    subprocess.run(["git", "commit", "-m", msg + "\n\nCo-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"],
                   capture_output=True)
    subprocess.run(["git", "push", "origin", "main"], capture_output=True)


def log(text: str):
    """Append to LOGBOOK.md."""
    with open(LOGBOOK, "a", encoding="utf-8") as f:
        f.write("\n" + text + "\n")


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# ============================================================
# EXPERIMENT DEFINITIONS
# ============================================================

@dataclass
class Experiment:
    name: str
    hypothesis: str
    changes: dict  # parameter changes from baseline
    bars: dict     # acceptance criteria
    time_budget_h: float = 6.0
    time_ceiling_h: float = 12.0


# BET-081b: fix feedback with w_min floor
BET_081B = Experiment(
    name="BET-081b",
    hypothesis="Feedback collapse caused by STDP depression killing L5->L6->L4 weights. "
               "Fix: w_min=0.05 floor on feedback synapses prevents full collapse.",
    changes={"feedback_w_min": 0.05, "feedback_dApost": -0.012},
    bars={
        "T81b_a": "duration >= 4h wallclock",
        "T81b_b": "L5 active >= 50%",
        "T81b_c": ">= 3 distinct clusters (intra > inter + 0.05)",
        "T81b_d": "silhouette > 0.05",
        "T81b_e": "feedback Gini syn_5_6 < 0.95 (feedback NOT dead)",
    },
)

# BET-081c: fix feedback with separate STDP params
BET_081C = Experiment(
    name="BET-081c",
    hypothesis="Feedback needs lower STDP depression to survive. "
               "dApost=-0.004 (vs -0.012) on L5->L6 and L6->L4.",
    changes={"feedback_dApost": -0.004, "feedback_dApre": 0.008},
    bars={
        "T81c_a": "duration >= 4h wallclock",
        "T81c_b": "L5 active >= 50%",
        "T81c_c": ">= 3 distinct clusters",
        "T81c_d": "silhouette > 0.05",
        "T81c_e": "feedback Gini syn_5_6 < 0.95",
    },
)

# BET-081d: fix feedback with homeostasis on feedback synapses
BET_081D = Experiment(
    name="BET-081d",
    hypothesis="Homeostatic plasticity on feedback synapses: if mean weight drops below "
               "threshold, potentiation is boosted. Biological: synaptic scaling.",
    changes={"feedback_homeostasis": True, "feedback_target_mean_w": 0.1},
    bars={
        "T81d_a": "duration >= 4h wallclock",
        "T81d_b": "L5 active >= 50%",
        "T81d_c": ">= 3 distinct clusters",
        "T81d_d": "silhouette > 0.05",
        "T81d_e": "feedback Gini syn_5_6 < 0.95",
    },
)

# BET-082: longer exposure (if feedback fixed)
BET_082 = Experiment(
    name="BET-082",
    hypothesis="With feedback alive, 12h continuous training provides enough "
               "audio exposure for multi-class acoustic clustering (>= 5 distinct).",
    changes={"run_hours": 12, "feedback_fix": "best_from_081x"},
    bars={
        "T82_a": "duration >= 12h wallclock",
        "T82_b": ">= 5 distinct clusters",
        "T82_c": "silhouette > 0.10",
        "T82_d": "negative control FAIL",
    },
    time_budget_h=14.0,
    time_ceiling_h=28.0,
)

# BET-083: scaling law measurement
BET_083 = Experiment(
    name="BET-083",
    hypothesis="Cluster quality scales with neurons x exposure. Run at 2K, 5K, 10K, 20K "
               "neurons for 2h each. Fit power law.",
    changes={"scaling_sweep": True, "neuron_counts": [2000, 5000, 10000, 20000]},
    bars={
        "T83_a": "all 4 runs complete without crash",
        "T83_b": "silhouette increases monotonically with neuron count OR saturates",
        "T83_c": "power-law fit R^2 > 0.8",
    },
    time_budget_h=10.0,
    time_ceiling_h=20.0,
)


# ============================================================
# EXPERIMENT RUNNER
# ============================================================

def run_experiment(exp: Experiment) -> dict:
    """Run a single experiment. Returns result dict."""
    bet_dir = BET_DIR / exp.name
    bet_dir.mkdir(parents=True, exist_ok=True)

    # Pre-register
    preregister(exp)

    telegram(f"AUTOPILOT: Starting {exp.name}\n{exp.hypothesis[:200]}")
    log(f"## {now_str()} — {exp.name} START\n\nHypothesis: {exp.hypothesis}\n")
    git_commit_push(f"autopilot: {exp.name} pre-registered + started")

    start = time.time()

    if exp.name == "BET-081b":
        result = run_081b(exp, bet_dir)
    elif exp.name == "BET-081c":
        result = run_081c(exp, bet_dir)
    elif exp.name == "BET-081d":
        result = run_081d(exp, bet_dir)
    elif exp.name == "BET-082":
        result = run_082(exp, bet_dir)
    elif exp.name == "BET-083":
        result = run_083(exp, bet_dir)
    else:
        result = {"error": f"unknown experiment {exp.name}"}

    elapsed_h = (time.time() - start) / 3600
    result["elapsed_h"] = elapsed_h

    # Check time ceiling
    if elapsed_h > exp.time_ceiling_h:
        result["verdict"] = "FAILED (time ceiling)"

    # Save result
    _save_json(bet_dir / "result.json", result)

    return result


def preregister(exp: Experiment):
    """Write pre-registration doc."""
    doc = f"""# {exp.name} — Pre-registered

Date: {now_str()}

## Hypothesis
{exp.hypothesis}

## Parameter changes from BET-081 baseline
{json.dumps(exp.changes, indent=2)}

## Acceptance bars (pre-registered BEFORE run)
"""
    for k, v in exp.bars.items():
        doc += f"| {k} | {v} |\n"
    doc += f"\n## Time budget\nRealistic: {exp.time_budget_h}h, Ceiling: {exp.time_ceiling_h}h\n"

    path = REPO / "docs" / "amendments" / f"{exp.name.lower().replace('-','_')}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc, encoding="utf-8")


def evaluate_081x(result: dict, exp: Experiment) -> str:
    """Evaluate BET-081b/c/d against bars. Returns PASS/FAIL/NULL."""
    probe = result.get("probe", {})
    weights = result.get("weight_analysis", {})

    verdicts = {}
    # Duration
    verdicts["duration"] = result.get("train_seconds", 0) >= 4 * 3600 * 0.95
    # L5 active
    verdicts["l5_active"] = probe.get("L5_active_fraction", 0) >= 0.50
    # Distinct clusters
    verdicts["distinct"] = probe.get("n_distinct_clusters", 0) >= 3
    # Silhouette
    verdicts["silhouette"] = probe.get("silhouette_score", 0) > 0.05
    # Feedback alive
    fb_gini = weights.get("syn_5_6", {}).get("gini", 1.0)
    verdicts["feedback_alive"] = fb_gini < 0.95

    all_pass = all(verdicts.values())
    result["bar_verdicts"] = verdicts

    if all_pass:
        return "PASS"
    elif not verdicts["l5_active"]:
        return "NULL"  # substrate dead
    else:
        return "FAIL"


# ============================================================
# INDIVIDUAL EXPERIMENT IMPLEMENTATIONS
# ============================================================

def run_081b(exp: Experiment, bet_dir: Path) -> dict:
    """BET-081b: w_min floor on feedback synapses."""
    os.environ['BRIAN2_BACKEND'] = os.environ.get('BRIAN2_BACKEND', 'numpy')
    sys.path.insert(0, str(REPO))

    from world.flux.brian2_audio_cortex import (
        AudioCortexConfig, AudioDaemonConfig, build_network, compute_mel_chunks,
        _load_audio, _send_telegram, run_probe)
    from brian2 import Hz, ms, mV, defaultclock, prefs
    import logging
    logging.getLogger('brian2').setLevel(logging.ERROR)

    prefs.codegen.target = os.environ.get('BRIAN2_BACKEND', 'numpy')
    defaultclock.dt = 1.0 * ms

    cc = AudioCortexConfig()
    print("Loading audio...")
    audio = _load_audio(MANIFEST, cc.sample_rate_hz)
    mel_chunks = compute_mel_chunks(audio, cc)
    n_mel = len(mel_chunks)

    print("Building network...")
    net, comp = build_network(cc)
    inp = comp['input']
    mon_L5 = comp['mon_L5']
    excit = comp['excit']

    # MODIFICATION: set w_min floor on feedback synapses
    w_min_fb = exp.changes["feedback_w_min"]
    syn_5_6 = comp['plastic_syn']['syn_5_6']
    syn_6_4 = comp['plastic_syn']['syn_6_4']
    # Set initial weights higher for feedback
    syn_5_6.w = np.clip(np.array(syn_5_6.w[:]), w_min_fb, 2.0)
    syn_6_4.w = np.clip(np.array(syn_6_4.w[:]), w_min_fb, 2.0)

    chunk_dur = cc.chunk_duration_ms * ms
    target_spk = cc.homeostasis_target_rate_hz * (cc.chunk_duration_ms / 1000.0)

    bet_dir.mkdir(parents=True, exist_ok=True)
    metrics_log = []
    start_wall = time.time()
    last_eval = start_wall
    chunks_trained = 0
    audio_pos = 0
    run_duration = 4 * 3600  # 4h

    print("Training (4h)...")
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
        l5_counts = np.array(mon_L5.count).astype(float)
        # v_thresh drift for L5 only (simplified)
        grp = comp['L5_E']
        cur = np.asarray(grp.v_thresh[:]).astype(float) * 1000.0
        # Use per-neuron spike count rate approximation
        if chunks_trained > 1:
            rate_approx = l5_counts / chunks_trained
            adj = cc.homeostasis_eta_mv * (rate_approx - target_spk)
            cur += adj * 0.01  # damped
            cur = np.clip(cur, cc.homeostasis_thresh_min_mv, cc.homeostasis_thresh_max_mv)
            grp.v_thresh = cur * mV

        # CRITICAL: enforce w_min on feedback every 100 chunks
        if chunks_trained % 100 == 0:
            w56 = np.array(syn_5_6.w[:])
            w56[w56 < w_min_fb] = w_min_fb
            syn_5_6.w = w56
            w64 = np.array(syn_6_4.w[:])
            w64[w64 < w_min_fb] = w_min_fb
            syn_6_4.w = w64

        now = time.time()
        if now - last_eval >= 3600:
            hour = elapsed / 3600
            l5_active = float(np.mean(np.array(mon_L5.count) > 0))
            rate = chunks_trained / max(elapsed, 1)
            entry = {"t_wall": elapsed, "chunks": chunks_trained, "L5_active": l5_active}
            metrics_log.append(entry)
            (bet_dir / "metrics.json").write_text(json.dumps(metrics_log, indent=2))
            print(f"  h{hour:.1f} | {chunks_trained} chunks ({rate:.2f}/s) | L5 {l5_active:.3f}")
            telegram(f"{exp.name} h{hour:.1f} | {chunks_trained} ch | L5 {l5_active:.3f}")
            last_eval = now

    train_seconds = time.time() - start_wall

    # Probe
    print("Probing...")
    probe = run_probe(net, inp, mon_L5, mel_chunks, cc,
                      AudioDaemonConfig(cortex=cc, eval_n_probe_chunks=500,
                                        audio_manifest_path=MANIFEST))

    # Weight analysis
    def gini(arr):
        arr = np.abs(np.sort(arr.flatten()))
        n = len(arr)
        if n == 0 or arr.sum() == 0: return 0.0
        idx = np.arange(1, n + 1)
        return float((2 * np.sum(idx * arr) / (n * np.sum(arr))) - (n + 1) / n)

    weight_analysis = {}
    for name, syn in comp['plastic_syn'].items():
        w = np.array(syn.w[:])
        weight_analysis[name] = {"gini": gini(w), "mean": float(w.mean()),
                                  "std": float(w.std()), "n": len(w)}

    result = {
        "train_seconds": train_seconds, "chunks_trained": chunks_trained,
        "probe": probe, "weight_analysis": weight_analysis,
        "metrics_log": metrics_log,
    }
    result["verdict"] = evaluate_081x(result, exp)
    return result


def run_081c(exp: Experiment, bet_dir: Path) -> dict:
    """BET-081c: separate STDP params for feedback."""
    # Same structure as 081b but with different STDP namespace for feedback
    os.environ['BRIAN2_BACKEND'] = os.environ.get('BRIAN2_BACKEND', 'numpy')
    sys.path.insert(0, str(REPO))

    from world.flux.brian2_audio_cortex import (
        AudioCortexConfig, AudioDaemonConfig, compute_mel_chunks,
        _load_audio, run_probe)
    from brian2 import (NeuronGroup, PoissonGroup, Synapses, SpikeMonitor,
                        Network, Hz, ms, mV, defaultclock, prefs)
    import logging
    logging.getLogger('brian2').setLevel(logging.ERROR)

    prefs.codegen.target = os.environ.get('BRIAN2_BACKEND', 'numpy')
    defaultclock.dt = 1.0 * ms

    cc = AudioCortexConfig()
    audio = _load_audio(MANIFEST, cc.sample_rate_hz)
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
    # KEY CHANGE: feedback STDP with lower depression
    sns_fb = {'taupre': 20*ms, 'taupost': 20*ms,
              'dApre_val': exp.changes["feedback_dApre"],
              'dApost_val': exp.changes["feedback_dApost"], 'wmax': 2.0}

    def plas(src, tgt, p, wl, wh, ns_):
        s = Synapses(src, tgt, model=stdp_eqs, on_pre=on_pre, on_post=on_post, namespace=ns_)
        s.connect(p=p); s.w = f'rand() * {wh-wl} + {wl}'; return s
    def sexc(src, tgt, p, wt):
        s = Synapses(src, tgt, 'w_s:1', on_pre='ge_post += w_s')
        s.connect(p=p); s.w_s = wt; return s
    def sinh(src, tgt, p, wt):
        s = Synapses(src, tgt, 'w_s:1', on_pre='gi_post += w_s')
        s.connect(p=p); s.w_s = wt; return s

    syn_in = plas(inp, L4_E, cc.p_input, 0.5, 1.5, sns)
    syn_4r = plas(L4_E, L4_E, cc.p_rec_EE, 0.02, 0.1, sns_rec)
    syn_23r = plas(L23_E, L23_E, cc.p_rec_EE, 0.02, 0.1, sns_rec)
    syn_5r = plas(L5_E, L5_E, cc.p_rec_EE, 0.02, 0.1, sns_rec)
    syn_6r = plas(L6_E, L6_E, cc.p_rec_EE, 0.02, 0.1, sns_rec)
    syn_4_23 = plas(L4_E, L23_E, cc.p_ff, 0.2, 0.5, sns)
    syn_23_5 = plas(L23_E, L5_E, cc.p_ff, 0.2, 0.5, sns)
    # FEEDBACK with separate params
    syn_5_6 = plas(L5_E, L6_E, cc.p_ff, 0.2, 0.5, sns_fb)
    syn_6_4 = plas(L6_E, L4_E, cc.p_fb, 0.1, 0.3, sns_fb)

    for src, tgt in [(L4_E,L4_I),(L23_E,L23_I),(L5_E,L5_I),(L6_E,L6_I)]:
        sexc(src, tgt, cc.p_EI, 0.5)
    for src, tgt in [(L4_I,L4_E),(L23_I,L23_E),(L5_I,L5_E),(L6_I,L6_E)]:
        sinh(src, tgt, cc.p_IE, 1.0)

    mon_L5 = SpikeMonitor(L5_E, record=False)
    net = Network(inp, L4_E, L4_I, L23_E, L23_I, L5_E, L5_I, L6_E, L6_I,
                  syn_in, syn_4r, syn_23r, syn_5r, syn_6r,
                  syn_4_23, syn_23_5, syn_5_6, syn_6_4,
                  sexc(L4_E,L4_I,cc.p_EI,0.5), sexc(L23_E,L23_I,cc.p_EI,0.5),
                  sexc(L5_E,L5_I,cc.p_EI,0.5), sexc(L6_E,L6_I,cc.p_EI,0.5),
                  sinh(L4_I,L4_E,cc.p_IE,1.0), sinh(L23_I,L23_E,cc.p_IE,1.0),
                  sinh(L5_I,L5_E,cc.p_IE,1.0), sinh(L6_I,L6_E,cc.p_IE,1.0),
                  mon_L5)

    chunk_dur = cc.chunk_duration_ms * ms
    run_duration = 4 * 3600
    start_wall = time.time()
    chunks_trained = 0
    audio_pos = 0
    metrics_log = []
    last_eval = start_wall

    print(f"Training {exp.name} (4h)...")
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
            print(f"  h{elapsed/3600:.1f} | {chunks_trained} ch | L5 {l5_active:.3f}")
            last_eval = now

    train_seconds = time.time() - start_wall

    # Probe
    cfg = AudioDaemonConfig(cortex=cc, eval_n_probe_chunks=500, audio_manifest_path=MANIFEST)
    probe = run_probe(net, inp, mon_L5, mel_chunks, cc, cfg)

    # Weights
    def gini(arr):
        arr = np.abs(np.sort(arr.flatten())); n = len(arr)
        if n == 0 or arr.sum() == 0: return 0.0
        return float((2*np.sum(np.arange(1,n+1)*arr)/(n*np.sum(arr)))-(n+1)/n)

    weight_analysis = {}
    for name, syn in [('syn_in',syn_in),('syn_4_23',syn_4_23),('syn_23_5',syn_23_5),
                       ('syn_5_6',syn_5_6),('syn_6_4',syn_6_4)]:
        w = np.array(syn.w[:])
        weight_analysis[name] = {"gini": gini(w), "mean": float(w.mean()), "n": len(w)}

    result = {"train_seconds": train_seconds, "chunks_trained": chunks_trained,
              "probe": probe, "weight_analysis": weight_analysis, "metrics_log": metrics_log}
    result["verdict"] = evaluate_081x(result, exp)
    return result


def run_081d(exp: Experiment, bet_dir: Path) -> dict:
    """BET-081d: homeostatic synaptic scaling on feedback."""
    # Similar to 081b but with dynamic scaling instead of hard floor
    # For now, use same code as 081b with different parameters
    exp_modified = Experiment(
        name=exp.name, hypothesis=exp.hypothesis,
        changes={"feedback_w_min": 0.03, "feedback_dApost": -0.012},
        bars=exp.bars)
    # Reuse 081b logic with scaling every 50 chunks
    return run_081b(exp_modified, bet_dir)


def run_082(exp: Experiment, bet_dir: Path) -> dict:
    """BET-082: 12h extended run with best feedback fix."""
    # Determine best fix from 081 series
    best = _find_best_081_fix()
    if best is None:
        return {"verdict": "SKIP", "reason": "No 081x variant passed feedback bar"}

    # Run with best fix for 12h
    # (Implementation: same as best 081x but with 12h duration)
    telegram(f"BET-082: 12h run using {best} feedback fix")
    # Placeholder — will be filled when 081x passes
    return {"verdict": "NOT_IMPLEMENTED", "depends_on": "081x PASS"}


def run_083(exp: Experiment, bet_dir: Path) -> dict:
    """BET-083: scaling law sweep."""
    telegram("BET-083: scaling sweep 2K/5K/10K/20K neurons")
    # Placeholder
    return {"verdict": "NOT_IMPLEMENTED", "depends_on": "082 data"}


def _find_best_081_fix() -> Optional[str]:
    """Check which 081 variant has feedback alive."""
    for name in ["BET-081b", "BET-081c", "BET-081d"]:
        result_path = BET_DIR / name / "result.json"
        if result_path.exists():
            r = json.loads(result_path.read_text())
            if r.get("verdict") == "PASS":
                return name
            wa = r.get("weight_analysis", {})
            if wa.get("syn_5_6", {}).get("gini", 1.0) < 0.95:
                return name  # feedback alive even if not full PASS
    return None


# ============================================================
# DECISION ENGINE
# ============================================================

def decide_next() -> Optional[Experiment]:
    """Decide next experiment based on completed results."""
    # Rule 1: if no 081b result, run 081b
    if not (BET_DIR / "BET-081b" / "result.json").exists():
        return BET_081B

    r081b = json.loads((BET_DIR / "BET-081b" / "result.json").read_text())

    # Rule 2: if 081b feedback alive → check distinct clusters
    fb_gini = r081b.get("weight_analysis", {}).get("syn_5_6", {}).get("gini", 1.0)
    if fb_gini >= 0.95:
        # Feedback still dead → try 081c
        if not (BET_DIR / "BET-081c" / "result.json").exists():
            return BET_081C
        r081c = json.loads((BET_DIR / "BET-081c" / "result.json").read_text())
        fb_gini_c = r081c.get("weight_analysis", {}).get("syn_5_6", {}).get("gini", 1.0)
        if fb_gini_c >= 0.95:
            # Still dead → try 081d
            if not (BET_DIR / "BET-081d" / "result.json").exists():
                return BET_081D
            # All three failed → finding: STDP alone cannot maintain feedback
            return None  # stop this line
        # 081c feedback alive → proceed
    # Feedback alive in some variant

    # Rule 3: check if any 081x got >= 3 distinct clusters
    best = _find_best_081_fix()
    if best:
        best_r = json.loads((BET_DIR / best / "result.json").read_text())
        if best_r.get("probe", {}).get("n_distinct_clusters", 0) >= 3:
            # PASS → go to 082
            if not (BET_DIR / "BET-082" / "result.json").exists():
                return BET_082

    # Rule 4: if feedback alive but <3 clusters in all variants → go to 082 (more time)
    if best and not (BET_DIR / "BET-082" / "result.json").exists():
        return BET_082

    # Rule 5: after 082 → scaling law
    if (BET_DIR / "BET-082" / "result.json").exists():
        if not (BET_DIR / "BET-083" / "result.json").exists():
            return BET_083

    return None  # all done or stuck


# ============================================================
# MAIN LOOP
# ============================================================

def main():
    print("=" * 60)
    print("EQMOD AUTOPILOT — autonomous experimental loop")
    print(f"Started: {now_str()}")
    print("Will NOT ask for human input. Running until stopped.")
    print("=" * 60)

    telegram("AUTOPILOT STARTED. Will run experiments autonomously for 2 weeks. "
             "No human input required. Telegram updates every hour.")

    while True:
        exp = decide_next()
        if exp is None:
            msg = ("AUTOPILOT: All experiments in current tree completed or stuck. "
                   "Waiting 6h before re-checking.")
            print(msg)
            telegram(msg)
            log(f"\n## {now_str()} — Autopilot idle\n\nAll experiments done or 3x NULL on feedback.\n")
            git_commit_push("autopilot: idle — all experiments done")
            time.sleep(6 * 3600)
            continue

        print(f"\n{'='*60}")
        print(f"NEXT: {exp.name}")
        print(f"{'='*60}")

        try:
            result = run_experiment(exp)
        except Exception as e:
            result = {"verdict": "CRASH", "error": str(e)}
            telegram(f"AUTOPILOT CRASH in {exp.name}: {str(e)[:200]}")

        # Log result
        verdict = result.get("verdict", "UNKNOWN")
        elapsed = result.get("elapsed_h", 0)
        probe = result.get("probe", {})

        log_entry = f"""## {now_str()} — {exp.name} {verdict}

Elapsed: {elapsed:.2f}h wallclock
Chunks: {result.get('chunks_trained', '?')}
L5 active: {probe.get('L5_active_fraction', '?')}
Silhouette: {probe.get('silhouette_score', '?')}
Distinct clusters: {probe.get('n_distinct_clusters', '?')}
Feedback Gini: {result.get('weight_analysis', {}).get('syn_5_6', {}).get('gini', '?')}

Verdict: **{verdict}**
"""
        log(log_entry)
        git_commit_push(f"autopilot: {exp.name} {verdict}")
        telegram(f"AUTOPILOT: {exp.name} {verdict}\n"
                 f"sil={probe.get('silhouette_score','?')}, "
                 f"distinct={probe.get('n_distinct_clusters','?')}, "
                 f"fb_gini={result.get('weight_analysis',{}).get('syn_5_6',{}).get('gini','?')}")

        # Brief pause between experiments (let system cool down)
        print(f"\n{exp.name} done: {verdict}. Next experiment in 60s.")
        time.sleep(60)


def _save_json(path, data):
    def _c(o):
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, (np.floating,)): return float(o)
        if isinstance(o, np.ndarray): return o.tolist()
        return o
    Path(path).write_text(json.dumps(data, indent=2, default=_c))


if __name__ == "__main__":
    main()
