"""BET-073 — T57 Brian2 cython codegen speedup vs numpy.

First step in Mac-scaling sequence. Measure speedup of Brian2 cython
codegen target vs numpy on identical 1000-neuron substrate. Runs each
target in isolated subprocess for clean Brian2 state.

T57 bar (LOCKED): cython wall < 0.5x numpy wall (≥2× speedup minimum).
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import warnings
from pathlib import Path

import pytest

warnings.filterwarnings('ignore')

N_NEURONS = 1000
N_INPUT = 50
SIM_DURATION_MS = 1000.0
T57_SPEEDUP_RATIO_MAX = 0.5

OUT_DIR = Path.home() / ".eqmod/bet/BET-073"

RUNNER_SCRIPT = r"""
import time, sys, json
target = sys.argv[1]
n_neurons = int(sys.argv[2])
n_input = int(sys.argv[3])
sim_duration_ms = float(sys.argv[4])

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
syn = Synapses(input_group, neurons, model=stdp_eqs, on_pre=on_pre, on_post=on_post,
               namespace={'taupre': 20 * ms, 'taupost': 20 * ms,
                          'dApre_val': 0.01, 'dApost_val': -0.012, 'wmax': 2.0})
syn.connect(p=0.2)
syn.w = 'rand() * 1.5 + 0.5'

mon = SpikeMonitor(neurons)
net = Network(input_group, neurons, syn, mon)

# Warm up codegen with tiny run, then measure
t_warm = time.perf_counter()
net.run(10 * ms)
warm_seconds = time.perf_counter() - t_warm

t0 = time.perf_counter()
net.run(sim_duration_ms * ms)
wall_seconds = time.perf_counter() - t0

n_spikes = int(len(mon.i))
out = {"wall_seconds": wall_seconds, "warm_seconds": warm_seconds,
       "n_spikes": n_spikes, "target": target}
print("RESULT_JSON=" + json.dumps(out))
"""


def _run_target(target):
    proc = subprocess.run(
        [sys.executable, "-c", RUNNER_SCRIPT, target,
         str(N_NEURONS), str(N_INPUT), str(SIM_DURATION_MS)],
        capture_output=True, text=True, timeout=300,
    )
    for line in proc.stdout.splitlines():
        if line.startswith("RESULT_JSON="):
            return json.loads(line[len("RESULT_JSON="):])
    raise RuntimeError(f"target {target} failed:\nSTDOUT:{proc.stdout[-2000:]}\nSTDERR:{proc.stderr[-2000:]}")


@pytest.fixture(scope="module")
def speedup_measurement():
    numpy_result = _run_target('numpy')
    cython_result = _run_target('cython')

    numpy_wall = numpy_result["wall_seconds"]
    cython_wall = cython_result["wall_seconds"]
    speedup_ratio = cython_wall / numpy_wall if numpy_wall > 0 else float('inf')
    return {
        "n_neurons": N_NEURONS,
        "sim_duration_ms": SIM_DURATION_MS,
        "numpy_wall_seconds": numpy_wall,
        "numpy_warm_seconds": numpy_result["warm_seconds"],
        "cython_wall_seconds": cython_wall,
        "cython_warm_seconds": cython_result["warm_seconds"],
        "speedup_ratio_cython_over_numpy": speedup_ratio,
        "speedup_factor_x": (numpy_wall / cython_wall) if cython_wall > 0 else float('inf'),
        "numpy_total_spikes": numpy_result["n_spikes"],
        "cython_total_spikes": cython_result["n_spikes"],
    }


def _verdict(s):
    return {**s, "T57_pass": s["speedup_ratio_cython_over_numpy"] < T57_SPEEDUP_RATIO_MAX}


def test_T57(speedup_measurement):
    m = _verdict(speedup_measurement)
    if not m["T57_pass"]:
        pytest.fail(
            f"BET-073 NULL T57 Brian2 cython speedup.\n"
            f"  n_neurons: {m['n_neurons']}\n"
            f"  numpy wall: {m['numpy_wall_seconds']:.2f}s ({m['numpy_total_spikes']} spikes)\n"
            f"  cython wall: {m['cython_wall_seconds']:.2f}s ({m['cython_total_spikes']} spikes)\n"
            f"  speedup factor: {m['speedup_factor_x']:.2f}x (need > 2x; ratio < {T57_SPEEDUP_RATIO_MAX})\n"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(speedup_measurement):
    yield
    m = _verdict(speedup_measurement)
    verdict = "passed" if m["T57_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-073",
        "verdict": verdict,
        "hypothesis": "T57 Brian2 cython codegen speedup vs numpy. First step in Mac-scaling sequence toward 1M neurons. Bar: cython wall < 0.5x numpy wall.",
        "thresholds": {"T57_speedup_ratio_max": T57_SPEEDUP_RATIO_MAX},
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))
