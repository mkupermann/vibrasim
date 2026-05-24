"""BET-074 — T58 Brian2 cython speedup at 10K neurons sparse 5%.

BET-073 found that at 1K neurons numpy is already near-optimal (cython
0.91x). Hypothesis: cython speedup appears at larger scale where
numerical compute dominates Python loop overhead.

T58 bars (LOCKED, both must pass):
  T58a — cython wall < 0.75x numpy wall (cython gives speedup at 10K)
  T58b — cython wall < 30s for 250ms-sim (substrate runs faster than
         12x real-time, i.e. wall-clock budget realistic for long training)
"""
from __future__ import annotations

import json
import subprocess
import sys
import warnings
from pathlib import Path

import pytest

warnings.filterwarnings('ignore')

N_NEURONS = 10000
N_INPUT = 200
SIM_DURATION_MS = 250.0
SPARSE_P = 0.05  # 5% connectivity

T58A_SPEEDUP_RATIO_MAX = 0.75
T58B_CYTHON_WALL_MAX = 30.0

OUT_DIR = Path.home() / ".eqmod/bet/BET-074"

RUNNER_SCRIPT = r"""
import time, sys, json
target = sys.argv[1]
n_neurons = int(sys.argv[2])
n_input = int(sys.argv[3])
sim_duration_ms = float(sys.argv[4])
sparse_p = float(sys.argv[5])

import numpy as np
import warnings
warnings.filterwarnings('ignore')
from brian2 import (NeuronGroup, PoissonGroup, Synapses, SpikeMonitor,
                    Network, Hz, ms, mV, defaultclock, prefs)
prefs.codegen.target = target
defaultclock.dt = 1.0 * ms

eqs_lif = '''
dv/dt = (-(v - v_rest) + ge*(0*mV - v) + gi*(-80*mV - v)) / tau_m : volt (unless refractory)
dge/dt = -ge / tau_e : 1
dgi/dt = -gi / tau_i : 1
'''
tau_m = 20 * ms; tau_e = 5 * ms; tau_i = 10 * ms
v_rest = -70 * mV; v_thresh = -54 * mV; v_reset = -75 * mV; tau_ref = 5 * ms

rng = np.random.default_rng(42)
rates_hz = rng.uniform(20, 80, n_input)
input_group = PoissonGroup(n_input, rates=rates_hz * Hz)
neurons = NeuronGroup(n_neurons, eqs_lif, threshold='v > v_thresh',
                      reset='v = v_reset', refractory=tau_ref, method='euler')
neurons.v = v_rest

stdp_eqs = '''
w : 1
dApre/dt = -Apre / taupre : 1 (event-driven)
dApost/dt = -Apost / taupost : 1 (event-driven)
'''
on_pre = '''
ge += w
Apre += dApre_val
w = clip(w + Apost, 0, wmax)
'''
on_post = '''
Apost += dApost_val
w = clip(w + Apre, 0, wmax)
'''

# input → neurons (5% sparse)
syn_in = Synapses(input_group, neurons, model=stdp_eqs, on_pre=on_pre, on_post=on_post,
                  namespace={'taupre': 20 * ms, 'taupost': 20 * ms,
                             'dApre_val': 0.01, 'dApost_val': -0.012, 'wmax': 2.0})
syn_in.connect(p=sparse_p)
syn_in.w = 'rand() * 1.5 + 0.5'

# recurrent within neurons (5% sparse) — cortical-style
syn_rec = Synapses(neurons, neurons, model=stdp_eqs, on_pre=on_pre, on_post=on_post,
                   namespace={'taupre': 20 * ms, 'taupost': 20 * ms,
                              'dApre_val': 0.005, 'dApost_val': -0.006, 'wmax': 1.0})
syn_rec.connect(p=sparse_p)
syn_rec.w = 'rand() * 0.5 + 0.1'

mon = SpikeMonitor(neurons)
net = Network(input_group, neurons, syn_in, syn_rec, mon)

# Warm-up to compile codegen, not counted
t_warm = time.perf_counter()
net.run(10 * ms)
warm_seconds = time.perf_counter() - t_warm

t0 = time.perf_counter()
net.run(sim_duration_ms * ms)
wall_seconds = time.perf_counter() - t0

n_spikes = int(len(mon.i))
n_synapses_in = int(len(syn_in))
n_synapses_rec = int(len(syn_rec))

out = {"wall_seconds": wall_seconds, "warm_seconds": warm_seconds,
       "n_spikes": n_spikes, "target": target,
       "n_synapses_in": n_synapses_in, "n_synapses_rec": n_synapses_rec}
print("RESULT_JSON=" + json.dumps(out))
"""


def _run_target(target):
    proc = subprocess.run(
        [sys.executable, "-c", RUNNER_SCRIPT, target,
         str(N_NEURONS), str(N_INPUT), str(SIM_DURATION_MS), str(SPARSE_P)],
        capture_output=True, text=True, timeout=600,
    )
    for line in proc.stdout.splitlines():
        if line.startswith("RESULT_JSON="):
            return json.loads(line[len("RESULT_JSON="):])
    raise RuntimeError(
        f"target {target} failed:\nSTDOUT:{proc.stdout[-2000:]}\nSTDERR:{proc.stderr[-2000:]}"
    )


@pytest.fixture(scope="module")
def speedup_measurement():
    numpy_result = _run_target('numpy')
    cython_result = _run_target('cython')

    numpy_wall = numpy_result["wall_seconds"]
    cython_wall = cython_result["wall_seconds"]
    speedup_ratio = cython_wall / numpy_wall if numpy_wall > 0 else float('inf')

    return {
        "n_neurons": N_NEURONS,
        "n_input": N_INPUT,
        "n_synapses_in": numpy_result["n_synapses_in"],
        "n_synapses_rec": numpy_result["n_synapses_rec"],
        "sparse_p": SPARSE_P,
        "sim_duration_ms": SIM_DURATION_MS,
        "numpy_wall_seconds": numpy_wall,
        "cython_wall_seconds": cython_wall,
        "cython_warm_seconds": cython_result["warm_seconds"],
        "speedup_ratio_cython_over_numpy": speedup_ratio,
        "speedup_factor_x": (numpy_wall / cython_wall) if cython_wall > 0 else float('inf'),
        "numpy_total_spikes": numpy_result["n_spikes"],
        "cython_total_spikes": cython_result["n_spikes"],
    }


def _verdict(s):
    a = s["speedup_ratio_cython_over_numpy"] < T58A_SPEEDUP_RATIO_MAX
    b = s["cython_wall_seconds"] < T58B_CYTHON_WALL_MAX
    return {**s, "T58a_speedup_ok": a, "T58b_realtime_ok": b,
            "T58_pass": a and b}


def test_T58(speedup_measurement):
    m = _verdict(speedup_measurement)
    if not m["T58_pass"]:
        pytest.fail(
            f"BET-074 NULL T58 10K-neuron benchmark.\n"
            f"  n_neurons: {m['n_neurons']}\n"
            f"  synapses: {m['n_synapses_in']} input + {m['n_synapses_rec']} recurrent\n"
            f"  numpy wall: {m['numpy_wall_seconds']:.2f}s ({m['numpy_total_spikes']} spikes)\n"
            f"  cython wall: {m['cython_wall_seconds']:.2f}s ({m['cython_total_spikes']} spikes)\n"
            f"  speedup factor: {m['speedup_factor_x']:.2f}x (need > 1.33x; ratio < {T58A_SPEEDUP_RATIO_MAX})\n"
            f"  cython warm-up cost: {m['cython_warm_seconds']:.2f}s\n"
            f"  cython realtime factor: {m['cython_wall_seconds']/(m['sim_duration_ms']/1000):.2f}x sim-time\n"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(speedup_measurement):
    yield
    m = _verdict(speedup_measurement)
    verdict = "passed" if m["T58_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-074",
        "verdict": verdict,
        "hypothesis": "T58 Brian2 cython at 10K neurons sparse 5%. Bars: cython < 0.75x numpy AND wall < 30s for 250ms sim.",
        "thresholds": {
            "T58a_speedup_ratio_max": T58A_SPEEDUP_RATIO_MAX,
            "T58b_cython_wall_max": T58B_CYTHON_WALL_MAX,
        },
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))
