"""Brian2 cortical substrate long-training daemon — Phase B.

Runs the BET-077c-balanced cortical 25K substrate continuously for
multi-hour periods. Checkpoints state every hour, sends Telegram
heartbeat, captures eval metrics at each hour boundary.

Design constraints:
  - SpikeMonitor(record=False) so spike-event buffer doesn't grow
  - Only mon.count read (per-neuron counters)
  - Audio streamed in chunks from corpus manifest, looped
  - Homeostatic threshold drift between chunks
  - Atomic checkpoints via tmp+rename
"""
from __future__ import annotations

import json
import os
import time
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

warnings.filterwarnings('ignore')


@dataclass
class DaemonConfig:
    run_duration_seconds: float
    chunk_duration_ms: float = 100.0
    checkpoint_interval_seconds: float = 3600.0  # hourly
    eval_interval_seconds: float = 3600.0        # hourly
    telegram_heartbeat_interval_seconds: float = 3600.0
    target_firing_rate_hz: float = 5.0
    homeostasis_eta_mv: float = 1.0
    homeostasis_thresh_min_mv: float = -60.0
    homeostasis_thresh_max_mv: float = -48.0
    checkpoint_dir: Optional[Path] = None
    metrics_log_path: Optional[Path] = None
    notify_config_path: Optional[Path] = None
    audio_manifest_path: Optional[Path] = None
    eval_n_chunks_per_class: int = 30
    samples_per_tick: int = 16
    fft_bands: int = 8


def _send_telegram(notify_path, msg):
    if not notify_path or not Path(notify_path).exists():
        return
    try:
        cfg = json.loads(Path(notify_path).read_text())
        token = cfg["telegram_bot_token"]
        chat = cfg["telegram_chat_id"]
        import urllib.request
        import urllib.parse
        data = urllib.parse.urlencode({
            "chat_id": chat,
            "text": msg[:4000],
        }).encode()
        urllib.request.urlopen(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data, timeout=10,
        )
    except Exception as e:
        # Daemon never dies because of telegram
        pass


def _make_wn(n, target_rms, seed):
    rng = np.random.default_rng(seed)
    s = rng.standard_normal(n)
    return (s / np.sqrt(np.mean(s * s)) * target_rms).astype(np.float64)


def run_long_training(daemon_cfg: DaemonConfig):
    """Main daemon loop. Returns final metrics dict."""
    from brian2 import (NeuronGroup, PoissonGroup, Synapses, SpikeMonitor,
                        Network, Hz, ms, mV, defaultclock, prefs)
    from world.flux.brian2_cortical import Brian2CorticalConfig
    from world.flux.cognitive_map import encode_sensor
    from world.flux.harder_bar_metrics import hist_kl_symmetric
    from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest

    prefs.codegen.target = 'cython'
    defaultclock.dt = 1.0 * ms

    # Cortical substrate parameters (BET-077c balanced)
    cfg = Brian2CorticalConfig(
        chunk_duration_ms=daemon_cfg.chunk_duration_ms,
        p_rec_EE=0.02,
        p_IE=0.40,
        homeostasis_enabled=True,
        homeostasis_target_rate_hz=daemon_cfg.target_firing_rate_hz,
        homeostasis_eta_mv=daemon_cfg.homeostasis_eta_mv,
    )

    class _EncoderCfg:
        n_features = 2 + daemon_cfg.fft_bands
        fft_bands = daemon_cfg.fft_bands
        samples_per_tick = daemon_cfg.samples_per_tick
    encoder_cfg = _EncoderCfg()

    _send_telegram(daemon_cfg.notify_config_path,
                   f"EQMOD daemon START | cortical 25K | {daemon_cfg.run_duration_seconds/3600:.1f}h")

    # Build substrate (same shape as BET-077c)
    eqs_lif = '''
    dv/dt = (-(v - v_rest) + ge*(0*mV - v) + gi*(-80*mV - v)) / tau_m : volt (unless refractory)
    dge/dt = -ge / tau_e : 1
    dgi/dt = -gi / tau_i : 1
    v_thresh : volt
    '''
    neuron_ns = {'tau_m': 20*ms, 'tau_e': 5*ms, 'tau_i': 10*ms,
                 'v_rest': -70*mV, 'v_reset': -75*mV}
    tau_ref = 5*ms
    v_thresh_init = -54*mV

    def make_grp(n):
        ng = NeuronGroup(n, eqs_lif, threshold='v > v_thresh',
                         reset='v = v_reset', refractory=tau_ref, method='euler',
                         namespace=neuron_ns)
        ng.v = -70*mV
        ng.v_thresh = v_thresh_init
        return ng

    input_group = PoissonGroup(cfg.n_input, rates=0*Hz)
    L4_E = make_grp(cfg.n_L4_E);  L4_I = make_grp(cfg.n_L4_I)
    L23_E = make_grp(cfg.n_L23_E); L23_I = make_grp(cfg.n_L23_I)
    L5_E = make_grp(cfg.n_L5_E);  L5_I = make_grp(cfg.n_L5_I)
    L6_E = make_grp(cfg.n_L6_E);  L6_I = make_grp(cfg.n_L6_I)

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
    stdp_ns = {'taupre': 20*ms, 'taupost': 20*ms,
               'dApre_val': 0.01, 'dApost_val': -0.012, 'wmax': 2.0}
    stdp_ns_rec = {'taupre': 20*ms, 'taupost': 20*ms,
                   'dApre_val': 0.005, 'dApost_val': -0.006, 'wmax': 0.3}

    def plastic(src, tgt, p, w_lo, w_hi, ns):
        s = Synapses(src, tgt, model=stdp_eqs, on_pre=on_pre, on_post=on_post,
                     namespace=ns)
        s.connect(p=p)
        s.w = f'rand() * {w_hi - w_lo} + {w_lo}'
        return s

    def stx(src, tgt, p, w):
        s = Synapses(src, tgt, 'w : 1', on_pre='ge_post += w')
        s.connect(p=p)
        s.w = w
        return s

    def stinh(src, tgt, p, w):
        s = Synapses(src, tgt, 'w : 1', on_pre='gi_post += w')
        s.connect(p=p)
        s.w = w
        return s

    syn_in_L4 = plastic(input_group, L4_E, cfg.p_input, 0.5, 1.5, stdp_ns)
    syn_L4_rec  = plastic(L4_E,  L4_E,  cfg.p_rec_EE, 0.02, 0.1, stdp_ns_rec)
    syn_L23_rec = plastic(L23_E, L23_E, cfg.p_rec_EE, 0.02, 0.1, stdp_ns_rec)
    syn_L5_rec  = plastic(L5_E,  L5_E,  cfg.p_rec_EE, 0.02, 0.1, stdp_ns_rec)
    syn_L6_rec  = plastic(L6_E,  L6_E,  cfg.p_rec_EE, 0.02, 0.1, stdp_ns_rec)
    syn_L4_L23 = plastic(L4_E,  L23_E, cfg.p_ff, 0.2, 0.5, stdp_ns)
    syn_L23_L5 = plastic(L23_E, L5_E,  cfg.p_ff, 0.2, 0.5, stdp_ns)
    syn_L5_L6  = plastic(L5_E,  L6_E,  cfg.p_ff, 0.2, 0.5, stdp_ns)
    syn_L6_L4  = plastic(L6_E,  L4_E,  cfg.p_fb, 0.05, 0.2, stdp_ns)

    syn_L4_EI  = stx(L4_E,  L4_I,  cfg.p_EI, 0.5)
    syn_L23_EI = stx(L23_E, L23_I, cfg.p_EI, 0.5)
    syn_L5_EI  = stx(L5_E,  L5_I,  cfg.p_EI, 0.5)
    syn_L6_EI  = stx(L6_E,  L6_I,  cfg.p_EI, 0.5)
    syn_L4_IE  = stinh(L4_I,  L4_E,  cfg.p_IE, 1.0)
    syn_L23_IE = stinh(L23_I, L23_E, cfg.p_IE, 1.0)
    syn_L5_IE  = stinh(L5_I,  L5_E,  cfg.p_IE, 1.0)
    syn_L6_IE  = stinh(L6_I,  L6_E,  cfg.p_IE, 1.0)

    # record=False keeps the spike-event buffer empty; mon.count still works
    mon_L4  = SpikeMonitor(L4_E,  record=False)
    mon_L23 = SpikeMonitor(L23_E, record=False)
    mon_L5  = SpikeMonitor(L5_E,  record=False)
    mon_L6  = SpikeMonitor(L6_E,  record=False)

    all_syn = [syn_in_L4,
               syn_L4_rec, syn_L23_rec, syn_L5_rec, syn_L6_rec,
               syn_L4_L23, syn_L23_L5, syn_L5_L6, syn_L6_L4,
               syn_L4_EI, syn_L23_EI, syn_L5_EI, syn_L6_EI,
               syn_L4_IE, syn_L23_IE, syn_L5_IE, syn_L6_IE]
    net = Network(input_group, L4_E, L4_I, L23_E, L23_I, L5_E, L5_I, L6_E, L6_I,
                  *all_syn,
                  mon_L4, mon_L23, mon_L5, mon_L6)

    # Pre-load audio corpus once into memory
    full_audio = load_corpus_waveform_from_manifest(
        daemon_cfg.audio_manifest_path,
        sample_rate_hz=16000, corpus_rms_target=0.25,
    ).astype(np.float64)
    wn_pool = _make_wn(len(full_audio), 0.25, seed=9999)

    chunk_samples = daemon_cfg.samples_per_tick
    n_audio_chunks = len(full_audio) // chunk_samples
    n_wn_chunks = len(wn_pool) // chunk_samples

    chunk_dur = daemon_cfg.chunk_duration_ms * ms
    target_spikes_per_chunk = daemon_cfg.target_firing_rate_hz * (daemon_cfg.chunk_duration_ms / 1000.0)
    excit_groups = [L4_E, L23_E, L5_E, L6_E]
    excit_monitors = [mon_L4, mon_L23, mon_L5, mon_L6]
    excit_names = ['L4', 'L23', 'L5', 'L6']
    n_excit = [cfg.n_L4_E, cfg.n_L23_E, cfg.n_L5_E, cfg.n_L6_E]

    metrics_log = []
    if daemon_cfg.metrics_log_path:
        Path(daemon_cfg.metrics_log_path).parent.mkdir(parents=True, exist_ok=True)
    if daemon_cfg.checkpoint_dir:
        Path(daemon_cfg.checkpoint_dir).mkdir(parents=True, exist_ok=True)

    def _eval_substrate():
        """Quick eval: present eval_n_chunks_per_class audio + WN, measure
        prototype accuracy at each layer."""
        rng = np.random.default_rng(int(time.time()) % 2**31)
        L4_p = {0: [], 1: []}; L23_p = {0: [], 1: []}
        L5_p = {0: [], 1: []}; L6_p = {0: [], 1: []}
        for _ in range(daemon_cfg.eval_n_chunks_per_class):
            for class_label in (0, 1):
                if class_label == 0:
                    idx = rng.integers(0, n_audio_chunks)
                    chunk = full_audio[idx*chunk_samples:(idx+1)*chunk_samples]
                else:
                    idx = rng.integers(0, n_wn_chunks)
                    chunk = wn_pool[idx*chunk_samples:(idx+1)*chunk_samples]
                features = encode_sensor(chunk, encoder_cfg)
                rates = np.clip(features[:cfg.n_input], 0, 1) * cfg.input_rate_max_hz
                input_group.rates = rates * Hz
                c = [np.array(m.count).copy() for m in excit_monitors]
                net.run(chunk_dur)
                for layer_i, m in enumerate(excit_monitors):
                    diff = np.array(m.count) - c[layer_i]
                    if layer_i == 0: L4_p[class_label].append(diff)
                    elif layer_i == 1: L23_p[class_label].append(diff)
                    elif layer_i == 2: L5_p[class_label].append(diff)
                    else: L6_p[class_label].append(diff)

        def proto_acc(p):
            p0 = np.array(p[0]); p1 = np.array(p[1])
            if len(p0) == 0 or len(p1) == 0: return 0.5
            proto0 = p0.mean(0); proto1 = p1.mean(0)
            correct = 0; total = 0
            for q in p0:
                if np.linalg.norm(q-proto0) < np.linalg.norm(q-proto1): correct += 1
                total += 1
            for q in p1:
                if np.linalg.norm(q-proto1) < np.linalg.norm(q-proto0): correct += 1
                total += 1
            return correct / max(total, 1)

        def kl(p):
            p0 = np.array(p[0]).astype(np.float64); p1 = np.array(p[1]).astype(np.float64)
            if len(p0) == 0 or len(p1) == 0: return 0.0
            return hist_kl_symmetric(p0, p1)

        return {
            'L4_acc': proto_acc(L4_p), 'L23_acc': proto_acc(L23_p),
            'L5_acc': proto_acc(L5_p), 'L6_acc': proto_acc(L6_p),
            'L4_kl':  kl(L4_p),  'L23_kl': kl(L23_p),
            'L5_kl':  kl(L5_p),  'L6_kl':  kl(L6_p),
        }

    # Training loop
    start_wall = time.time()
    last_checkpoint_wall = start_wall
    last_eval_wall = start_wall
    last_telegram_wall = start_wall
    chunks_trained = 0
    prev_spike_counts = [np.array(m.count).copy() for m in excit_monitors]
    rng = np.random.default_rng(42)

    pre_eval = _eval_substrate()
    metrics_log.append({"t_seconds": 0, "kind": "pre_eval", **pre_eval})
    if daemon_cfg.metrics_log_path:
        Path(daemon_cfg.metrics_log_path).write_text(json.dumps(metrics_log, indent=2))

    while True:
        elapsed = time.time() - start_wall
        if elapsed >= daemon_cfg.run_duration_seconds:
            break

        # Pick random chunk, random class (50/50)
        if rng.random() < 0.5:
            idx = rng.integers(0, n_audio_chunks)
            chunk = full_audio[idx*chunk_samples:(idx+1)*chunk_samples]
        else:
            idx = rng.integers(0, n_wn_chunks)
            chunk = wn_pool[idx*chunk_samples:(idx+1)*chunk_samples]

        features = encode_sensor(chunk, encoder_cfg)
        rates = np.clip(features[:cfg.n_input], 0, 1) * cfg.input_rate_max_hz
        input_group.rates = rates * Hz
        net.run(chunk_dur)
        chunks_trained += 1

        # Homeostasis update
        for grp, mon, prev in zip(excit_groups, excit_monitors, prev_spike_counts):
            cur = np.array(mon.count)
            diff = cur - prev
            adj_mv = daemon_cfg.homeostasis_eta_mv * (diff - target_spikes_per_chunk)
            new_thresh_mv = (np.asarray(grp.v_thresh[:]).astype(float) * 1000.0 + adj_mv)
            new_thresh_mv = np.clip(new_thresh_mv,
                                    daemon_cfg.homeostasis_thresh_min_mv,
                                    daemon_cfg.homeostasis_thresh_max_mv)
            grp.v_thresh = new_thresh_mv * mV
        prev_spike_counts = [np.array(m.count).copy() for m in excit_monitors]

        wall_now = time.time()

        # Hourly eval
        if wall_now - last_eval_wall >= daemon_cfg.eval_interval_seconds:
            eval_metrics = _eval_substrate()
            hour_marker = int((wall_now - start_wall) / 3600 + 0.5)
            entry = {"t_seconds": wall_now - start_wall,
                     "hour_marker": hour_marker,
                     "chunks_trained": chunks_trained,
                     "kind": "hourly_eval", **eval_metrics}
            metrics_log.append(entry)
            if daemon_cfg.metrics_log_path:
                Path(daemon_cfg.metrics_log_path).write_text(json.dumps(metrics_log, indent=2))
            last_eval_wall = wall_now

        # Hourly checkpoint
        if (daemon_cfg.checkpoint_dir and
            wall_now - last_checkpoint_wall >= daemon_cfg.checkpoint_interval_seconds):
            from world.flux.brian2_checkpoint import (
                collect_neuron_state, collect_synapse_state, save_checkpoint)
            state = {
                "chunks_trained": chunks_trained,
                "elapsed_seconds": wall_now - start_wall,
            }
            for name, grp in [('L4_E', L4_E), ('L23_E', L23_E),
                              ('L5_E', L5_E), ('L6_E', L6_E)]:
                state[name] = collect_neuron_state(grp)
            for name, syn in [('syn_in_L4', syn_in_L4),
                              ('syn_L4_rec', syn_L4_rec),
                              ('syn_L23_rec', syn_L23_rec),
                              ('syn_L4_L23', syn_L4_L23),
                              ('syn_L23_L5', syn_L23_L5),
                              ('syn_L5_L6', syn_L5_L6),
                              ('syn_L6_L4', syn_L6_L4)]:
                state[name] = collect_synapse_state(syn, plastic=True)
            ckpt = Path(daemon_cfg.checkpoint_dir) / f"checkpoint_h{int(elapsed/3600+0.5)}.pkl"
            save_checkpoint(state, ckpt)
            last_checkpoint_wall = wall_now

        # Hourly Telegram
        if wall_now - last_telegram_wall >= daemon_cfg.telegram_heartbeat_interval_seconds:
            hour = (wall_now - start_wall) / 3600
            last_metrics = next((m for m in reversed(metrics_log) if m.get('kind') == 'hourly_eval'),
                                pre_eval)
            msg = (f"EQMOD daemon h{hour:.1f}/{daemon_cfg.run_duration_seconds/3600:.1f} | "
                   f"chunks {chunks_trained} | L5 acc {last_metrics.get('L5_acc', '?'):.3f} "
                   f"L6 KL {last_metrics.get('L6_kl', '?'):.3e}")
            _send_telegram(daemon_cfg.notify_config_path, msg)
            last_telegram_wall = wall_now

    # Final eval
    final_eval = _eval_substrate()
    final_wall = time.time() - start_wall
    metrics_log.append({"t_seconds": final_wall, "kind": "final_eval",
                        "chunks_trained": chunks_trained, **final_eval})
    if daemon_cfg.metrics_log_path:
        Path(daemon_cfg.metrics_log_path).write_text(json.dumps(metrics_log, indent=2))

    # Final telegram
    _send_telegram(daemon_cfg.notify_config_path,
                   f"EQMOD daemon DONE | {final_wall/3600:.2f}h | chunks {chunks_trained} | "
                   f"L5 acc {final_eval['L5_acc']:.3f} L6 KL {final_eval['L6_kl']:.3e}")

    return {
        "elapsed_seconds": final_wall,
        "chunks_trained": chunks_trained,
        "pre_eval": pre_eval,
        "final_eval": final_eval,
        "metrics_log": metrics_log,
        "checkpoint_dir": str(daemon_cfg.checkpoint_dir) if daemon_cfg.checkpoint_dir else None,
        "metrics_log_path": str(daemon_cfg.metrics_log_path) if daemon_cfg.metrics_log_path else None,
    }
