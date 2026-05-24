"""BET-075 — T59 Brian2 100K neurons sparse 0.5%, scaling milestone.

After BET-074 PASS (10K + 5% sparse + 2.1× speedup), push to 100K.
Memory budget: 100K × 100K × 0.5% = 5×10^7 synapses ≈ 4GB synapse state.

T59 bars (LOCKED):
  T59a — substrate completes without OOM/crash
  T59b — cython wall < 300s for 100ms sim (substrate runs faster than
         3000× sim-time; viable for any long-training scenario)
"""
from __future__ import annotations

import json
import subprocess
import sys
import warnings
from pathlib import Path

import pytest

warnings.filterwarnings('ignore')

N_NEURONS = 100000
N_INPUT = 200
SIM_DURATION_MS = 100.0
INPUT_SPARSE_P = 0.02   # 2% — 400K input synapses
REC_SPARSE_P = 0.005    # 0.5% — 5×10^7 recurrent synapses

T59B_CYTHON_WALL_MAX = 300.0

OUT_DIR = Path.home() / ".eqmod/bet/BET-075"

RUNNER_SCRIPT = r"""
import time, sys, json, resource
target = sys.argv[1]
n_neurons = int(sys.argv[2])
n_input = int(sys.argv[3])
sim_duration_ms = float(sys.argv[4])
input_sparse_p = float(sys.argv[5])
rec_sparse_p = float(sys.argv[6])

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

t_build0 = time.perf_counter()
syn_in = Synapses(input_group, neurons, model=stdp_eqs, on_pre=on_pre, on_post=on_post,
                  namespace={'taupre': 20 * ms, 'taupost': 20 * ms,
                             'dApre_val': 0.01, 'dApost_val': -0.012, 'wmax': 2.0})
syn_in.connect(p=input_sparse_p)
syn_in.w = 'rand() * 1.5 + 0.5'

syn_rec = Synapses(neurons, neurons, model=stdp_eqs, on_pre=on_pre, on_post=on_post,
                   namespace={'taupre': 20 * ms, 'taupost': 20 * ms,
                              'dApre_val': 0.005, 'dApost_val': -0.006, 'wmax': 1.0})
syn_rec.connect(p=rec_sparse_p)
syn_rec.w = 'rand() * 0.5 + 0.1'
build_seconds = time.perf_counter() - t_build0

mon = SpikeMonitor(neurons)
net = Network(input_group, neurons, syn_in, syn_rec, mon)

t_warm = time.perf_counter()
net.run(5 * ms)
warm_seconds = time.perf_counter() - t_warm

t0 = time.perf_counter()
net.run(sim_duration_ms * ms)
wall_seconds = time.perf_counter() - t0

n_spikes = int(len(mon.i))
n_synapses_in = int(len(syn_in))
n_synapses_rec = int(len(syn_rec))

# Memory peak in bytes (Mac returns bytes; Linux returns KB — we're on Mac)
mem_peak_bytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

out = {"wall_seconds": wall_seconds, "warm_seconds": warm_seconds,
       "build_seconds": build_seconds,
       "n_spikes": n_spikes, "target": target,
       "n_synapses_in": n_synapses_in, "n_synapses_rec": n_synapses_rec,
       "mem_peak_gb": mem_peak_bytes / 1e9}
print("RESULT_JSON=" + json.dumps(out))
"""


def _run_target(target):
    proc = subprocess.run(
        [sys.executable, "-c", RUNNER_SCRIPT, target,
         str(N_NEURONS), str(N_INPUT), str(SIM_DURATION_MS),
         str(INPUT_SPARSE_P), str(REC_SPARSE_P)],
        capture_output=True, text=True, timeout=1500,
    )
    for line in proc.stdout.splitlines():
        if line.startswith("RESULT_JSON="):
            return json.loads(line[len("RESULT_JSON="):])
    raise RuntimeError(
        f"target {target} failed:\nSTDOUT:{proc.stdout[-2000:]}\nSTDERR:{proc.stderr[-2000:]}"
    )


@pytest.fixture(scope="module")
def measurement():
    cython_result = _run_target('cython')
    return {
        "n_neurons": N_NEURONS,
        "n_input": N_INPUT,
        "input_sparse_p": INPUT_SPARSE_P,
        "rec_sparse_p": REC_SPARSE_P,
        "sim_duration_ms": SIM_DURATION_MS,
        "n_synapses_in": cython_result["n_synapses_in"],
        "n_synapses_rec": cython_result["n_synapses_rec"],
        "n_synapses_total": cython_result["n_synapses_in"] + cython_result["n_synapses_rec"],
        "cython_build_seconds": cython_result["build_seconds"],
        "cython_warm_seconds": cython_result["warm_seconds"],
        "cython_wall_seconds": cython_result["wall_seconds"],
        "cython_total_spikes": cython_result["n_spikes"],
        "mem_peak_gb": cython_result["mem_peak_gb"],
        "realtime_factor": cython_result["wall_seconds"] / (SIM_DURATION_MS / 1000),
    }


def _verdict(s):
    completed = True  # if we got here, we completed
    fast_enough = s["cython_wall_seconds"] < T59B_CYTHON_WALL_MAX
    return {**s, "T59a_completed_ok": completed,
            "T59b_realtime_ok": fast_enough,
            "T59_pass": completed and fast_enough}


def test_T59(measurement):
    m = _verdict(measurement)
    if not m["T59_pass"]:
        pytest.fail(
            f"BET-075 NULL T59 100K-neuron scaling.\n"
            f"  n_neurons: {m['n_neurons']}, total synapses: {m['n_synapses_total']:,}\n"
            f"  memory peak: {m['mem_peak_gb']:.2f} GB\n"
            f"  build wall: {m['cython_build_seconds']:.2f}s\n"
            f"  cython warm-up: {m['cython_warm_seconds']:.2f}s\n"
            f"  cython sim wall: {m['cython_wall_seconds']:.2f}s "
            f"({m['realtime_factor']:.1f}x real-time, need < {T59B_CYTHON_WALL_MAX/(SIM_DURATION_MS/1000):.0f}x)\n"
            f"  total spikes: {m['cython_total_spikes']:,}\n"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(measurement):
    yield
    m = _verdict(measurement)
    verdict = "passed" if m["T59_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-075",
        "verdict": verdict,
        "hypothesis": "T59 100K neurons sparse (2% input + 0.5% recurrent) ~5e7 synapses. Bars: substrate runs without OOM AND cython wall < 300s for 100ms sim (< 3000x real-time).",
        "thresholds": {"T59b_cython_wall_max": T59B_CYTHON_WALL_MAX},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))
