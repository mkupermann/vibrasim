"""BET-078 — T64 Brian2 checkpoint/resume roundtrip.

Phase B long-training infrastructure. Build a small Brian2 substrate,
train briefly, save state, build fresh network, load state, verify
synapse weights and neuron states match pre-checkpoint exactly.

T64 bars (LOCKED, all three must pass):
  T64a — synapse weights identical pre and post roundtrip (max diff < 1e-9)
  T64b — neuron v identical pre and post (max diff < 1e-9 volt)
  T64c — checkpoint file size < 10MB for 200-neuron substrate (reasonable)
"""
from __future__ import annotations

import json
import tempfile
import warnings
from pathlib import Path

import numpy as np
import pytest

warnings.filterwarnings('ignore')

T64A_MAX_W_DIFF = 1e-9
T64B_MAX_V_DIFF = 1e-9
T64C_MAX_FILE_MB = 10.0

OUT_DIR = Path.home() / ".eqmod/bet/BET-078"


def _build_substrate():
    """Build small Brian2 substrate matching BET-068 hierarchical shape."""
    from brian2 import (NeuronGroup, PoissonGroup, Synapses,
                        Hz, ms, mV, defaultclock, prefs)
    prefs.codegen.target = 'cython'
    defaultclock.dt = 1.0 * ms

    eqs_lif = '''
    dv/dt = (-(v - v_rest) + ge*(0*mV - v) + gi*(-80*mV - v)) / tau_m : volt (unless refractory)
    dge/dt = -ge / tau_e : 1
    dgi/dt = -gi / tau_i : 1
    '''
    neuron_ns = {'tau_m': 20 * ms, 'tau_e': 5 * ms, 'tau_i': 10 * ms,
                 'v_rest': -70 * mV, 'v_thresh': -54 * mV,
                 'v_reset': -75 * mV}
    tau_ref = 5 * ms

    input_group = PoissonGroup(10, rates=50 * Hz)
    L1 = NeuronGroup(100, eqs_lif, threshold='v > v_thresh',
                     reset='v = v_reset', refractory=tau_ref, method='euler',
                     namespace=neuron_ns)
    L1.v = -70 * mV
    L2 = NeuronGroup(50, eqs_lif, threshold='v > v_thresh',
                     reset='v = v_reset', refractory=tau_ref, method='euler',
                     namespace=neuron_ns)
    L2.v = -70 * mV

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
    syn_ns = {'taupre': 20 * ms, 'taupost': 20 * ms,
              'dApre_val': 0.01, 'dApost_val': -0.012, 'wmax': 2.0}

    syn_in_L1 = Synapses(input_group, L1, model=stdp_eqs, on_pre=on_pre,
                          on_post=on_post, namespace=syn_ns)
    syn_L1_L2 = Synapses(L1, L2, model=stdp_eqs, on_pre=on_pre,
                          on_post=on_post, namespace=syn_ns)

    return {
        'input': input_group, 'L1': L1, 'L2': L2,
        'syn_in_L1': syn_in_L1, 'syn_L1_L2': syn_L1_L2,
    }


def _build_substrate_with_connections(conn_in_L1, conn_L1_L2):
    """Build substrate with explicit connection indices."""
    s = _build_substrate()
    s['syn_in_L1'].connect(i=conn_in_L1[0], j=conn_in_L1[1])
    s['syn_L1_L2'].connect(i=conn_L1_L2[0], j=conn_L1_L2[1])
    return s


@pytest.fixture(scope="module")
def roundtrip_measurement():
    from brian2 import Network, ms
    from world.flux.brian2_checkpoint import (
        collect_neuron_state, collect_synapse_state,
        restore_neuron_state, restore_synapse_state,
        save_checkpoint, load_checkpoint,
    )

    # Build first substrate, with sparse random connections
    rng = np.random.default_rng(0)
    s1 = _build_substrate()
    s1['syn_in_L1'].connect(p=0.5)
    s1['syn_L1_L2'].connect(p=0.3)
    s1['syn_in_L1'].w = 'rand() * 1.0 + 0.5'
    s1['syn_L1_L2'].w = 'rand() * 0.4 + 0.3'

    net1 = Network(s1['input'], s1['L1'], s1['L2'], s1['syn_in_L1'], s1['syn_L1_L2'])
    # Train briefly
    net1.run(200 * ms)

    # Capture state
    state = {
        'L1': collect_neuron_state(s1['L1']),
        'L2': collect_neuron_state(s1['L2']),
        'syn_in_L1': collect_synapse_state(s1['syn_in_L1'], plastic=True),
        'syn_L1_L2': collect_synapse_state(s1['syn_L1_L2'], plastic=True),
    }

    # Pre-checkpoint signatures
    pre_w_in_L1 = np.asarray(s1['syn_in_L1'].w[:]).astype(float).copy()
    pre_w_L1_L2 = np.asarray(s1['syn_L1_L2'].w[:]).astype(float).copy()
    pre_v_L1 = np.asarray(s1['L1'].v[:]).astype(float).copy()
    pre_v_L2 = np.asarray(s1['L2'].v[:]).astype(float).copy()

    # Save to disk
    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp:
        ckpt_path = Path(tmp.name)
    save_checkpoint(state, ckpt_path)
    file_size_mb = ckpt_path.stat().st_size / (1024 * 1024)

    # Load + rebuild
    loaded = load_checkpoint(ckpt_path)
    conn_in_L1 = (loaded['syn_in_L1']['i'].astype(int),
                  loaded['syn_in_L1']['j'].astype(int))
    conn_L1_L2 = (loaded['syn_L1_L2']['i'].astype(int),
                  loaded['syn_L1_L2']['j'].astype(int))

    s2 = _build_substrate_with_connections(conn_in_L1, conn_L1_L2)
    restore_neuron_state(s2['L1'], loaded['L1'])
    restore_neuron_state(s2['L2'], loaded['L2'])
    restore_synapse_state(s2['syn_in_L1'], loaded['syn_in_L1'])
    restore_synapse_state(s2['syn_L1_L2'], loaded['syn_L1_L2'])

    # Post-checkpoint signatures
    post_w_in_L1 = np.asarray(s2['syn_in_L1'].w[:]).astype(float)
    post_w_L1_L2 = np.asarray(s2['syn_L1_L2'].w[:]).astype(float)
    post_v_L1 = np.asarray(s2['L1'].v[:]).astype(float)
    post_v_L2 = np.asarray(s2['L2'].v[:]).astype(float)

    max_w_diff = max(
        float(np.max(np.abs(pre_w_in_L1 - post_w_in_L1))),
        float(np.max(np.abs(pre_w_L1_L2 - post_w_L1_L2))),
    )
    max_v_diff = max(
        float(np.max(np.abs(pre_v_L1 - post_v_L1))),
        float(np.max(np.abs(pre_v_L2 - post_v_L2))),
    )

    ckpt_path.unlink(missing_ok=True)

    return dict(
        n_L1=100, n_L2=50,
        n_syn_in_L1=int(loaded['syn_in_L1']['N']),
        n_syn_L1_L2=int(loaded['syn_L1_L2']['N']),
        max_w_roundtrip_diff=max_w_diff,
        max_v_roundtrip_diff=max_v_diff,
        checkpoint_size_mb=file_size_mb,
    )


def _verdict(s):
    w_ok = s["max_w_roundtrip_diff"] < T64A_MAX_W_DIFF
    v_ok = s["max_v_roundtrip_diff"] < T64B_MAX_V_DIFF
    size_ok = s["checkpoint_size_mb"] < T64C_MAX_FILE_MB
    return {**s, "T64a_w_ok": w_ok, "T64b_v_ok": v_ok, "T64c_size_ok": size_ok,
            "T64_pass": w_ok and v_ok and size_ok}


def test_T64(roundtrip_measurement):
    m = _verdict(roundtrip_measurement)
    if not m["T64_pass"]:
        pytest.fail(
            f"BET-078 NULL T64 checkpoint/resume.\n"
            f"  n_syn input→L1: {m['n_syn_in_L1']}\n"
            f"  n_syn L1→L2: {m['n_syn_L1_L2']}\n"
            f"  max weight diff: {m['max_w_roundtrip_diff']:.2e} "
            f"(need < {T64A_MAX_W_DIFF:.0e})\n"
            f"  max v diff: {m['max_v_roundtrip_diff']:.2e} volt "
            f"(need < {T64B_MAX_V_DIFF:.0e})\n"
            f"  checkpoint size: {m['checkpoint_size_mb']:.2f} MB "
            f"(need < {T64C_MAX_FILE_MB} MB)\n"
        )


@pytest.fixture(scope="module", autouse=True)
def write_bet_result_at_end(roundtrip_measurement):
    yield
    m = _verdict(roundtrip_measurement)
    verdict = "passed" if m["T64_pass"] else "null"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "item_id": "BET-078",
        "verdict": verdict,
        "hypothesis": "T64 Brian2 checkpoint/resume roundtrip on 200-neuron hierarchical substrate. Bars: weight diff < 1e-9, v diff < 1e-9 volt, file < 10MB.",
        "thresholds": {
            "T64a_max_w_diff": T64A_MAX_W_DIFF,
            "T64b_max_v_diff": T64B_MAX_V_DIFF,
            "T64c_max_file_mb": T64C_MAX_FILE_MB,
        },
        "measurements": m,
        "schema_version": 1,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(payload, indent=2))
