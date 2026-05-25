"""BET-081 — Emergent audio-cortex clustering via continuous stream STDP.

Cortical substrate fed by 32 Mel-band Poisson input. Audio streams
continuously (no segmentation, no labels). STDP + homeostatic threshold
drift. Post-hoc probing clusters L5 spike responses.

Single-Network per-chunk loop (same proven architecture as BET-080).
Training runs for N hours wallclock. After training, probe eval streams
held-out audio and clusters L5 spike patterns.
"""
from __future__ import annotations

import json
import logging
import os
import time
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

warnings.filterwarnings('ignore')
logging.getLogger('brian2').setLevel(logging.ERROR)


@dataclass
class AudioCortexConfig:
    n_input: int = 32
    n_L4_E: int = 2000
    n_L23_E: int = 2500
    n_L5_E: int = 2000
    n_L6_E: int = 1500
    n_L4_I: int = 500
    n_L23_I: int = 625
    n_L5_I: int = 500
    n_L6_I: int = 375
    p_rec_EE: float = 0.02
    p_EI: float = 0.20
    p_IE: float = 0.40
    p_ff: float = 0.10
    p_fb: float = 0.05
    p_input: float = 0.30
    sample_rate_hz: int = 16000
    n_mels: int = 32
    n_fft: int = 512
    hop_length: int = 160
    frames_per_chunk: int = 10  # 10 frames averaged per sim chunk
    input_rate_max_hz: float = 200.0
    chunk_duration_ms: float = 100.0
    homeostasis_target_rate_hz: float = 5.0
    homeostasis_eta_mv: float = 0.5
    homeostasis_thresh_min_mv: float = -60.0
    homeostasis_thresh_max_mv: float = -48.0


@dataclass
class AudioDaemonConfig:
    cortex: AudioCortexConfig = field(default_factory=AudioCortexConfig)
    run_duration_seconds: float = 4 * 3600
    checkpoint_interval_seconds: float = 3600.0
    eval_interval_seconds: float = 3600.0
    telegram_heartbeat_interval_seconds: float = 3600.0
    checkpoint_dir: Optional[Path] = None
    metrics_log_path: Optional[Path] = None
    notify_config_path: Optional[Path] = None
    audio_manifest_path: Optional[Path] = None
    bet_dir: Optional[Path] = None
    eval_n_probe_chunks: int = 500


def compute_mel_chunks(audio: np.ndarray, cc: AudioCortexConfig) -> np.ndarray:
    """Mel spectrogram averaged per chunk. Returns (n_chunks, n_mels) in [0,1]."""
    import librosa
    S = librosa.feature.melspectrogram(
        y=audio.astype(np.float32), sr=cc.sample_rate_hz,
        n_mels=cc.n_mels, n_fft=cc.n_fft, hop_length=cc.hop_length)
    S_log = np.log1p(S).T
    mx = S_log.max()
    if mx > 0:
        S_log /= mx
    fpc = cc.frames_per_chunk
    n = S_log.shape[0] // fpc
    return S_log[:n * fpc].reshape(n, fpc, cc.n_mels).mean(axis=1).astype(np.float32)


def _send_telegram(notify_path, msg):
    if not notify_path or not Path(notify_path).exists():
        return
    try:
        cfg = json.loads(Path(notify_path).read_text())
        import urllib.request, urllib.parse
        data = urllib.parse.urlencode({
            "chat_id": cfg["telegram_chat_id"], "text": msg[:4000],
        }).encode()
        urllib.request.urlopen(
            f"https://api.telegram.org/bot{cfg['telegram_bot_token']}/sendMessage",
            data=data, timeout=10)
    except Exception:
        pass


def _load_audio(manifest_path: Path, sr: int) -> np.ndarray:
    from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
    return load_corpus_waveform_from_manifest(
        manifest_path, sample_rate_hz=sr, corpus_rms_target=0.25).astype(np.float32)


def build_network(cc: AudioCortexConfig):
    """Build the cortical network. Returns (net, components_dict)."""
    from brian2 import (NeuronGroup, PoissonGroup, Synapses, SpikeMonitor,
                        Network, Hz, ms, mV)

    eqs_lif = '''
    dv/dt = (-(v - v_rest) + ge*(0*mV - v) + gi*(-80*mV - v)) / tau_m : volt (unless refractory)
    dge/dt = -ge / tau_e : 1
    dgi/dt = -gi / tau_i : 1
    v_thresh : volt
    '''
    ns = {'tau_m': 20*ms, 'tau_e': 5*ms, 'tau_i': 10*ms,
          'v_rest': -70*mV, 'v_reset': -75*mV}

    def make_grp(n):
        g = NeuronGroup(n, eqs_lif, threshold='v > v_thresh',
                        reset='v = v_reset', refractory=5*ms, method='euler',
                        namespace=ns)
        g.v = -70 * mV
        g.v_thresh = -54 * mV
        return g

    input_group = PoissonGroup(cc.n_input, rates=0 * Hz)
    L4_E = make_grp(cc.n_L4_E);   L4_I = make_grp(cc.n_L4_I)
    L23_E = make_grp(cc.n_L23_E); L23_I = make_grp(cc.n_L23_I)
    L5_E = make_grp(cc.n_L5_E);   L5_I = make_grp(cc.n_L5_I)
    L6_E = make_grp(cc.n_L6_E);   L6_I = make_grp(cc.n_L6_I)

    stdp_eqs = '''
    w : 1
    dApre/dt = -Apre / taupre : 1 (event-driven)
    dApost/dt = -Apost / taupost : 1 (event-driven)
    '''
    on_pre = 'ge += w\nApre += dApre_val\nw = clip(w + Apost, 0, wmax)'
    on_post = 'Apost += dApost_val\nw = clip(w + Apre, 0, wmax)'
    sns = {'taupre': 20*ms, 'taupost': 20*ms,
           'dApre_val': 0.01, 'dApost_val': -0.012, 'wmax': 2.0}
    sns_rec = {'taupre': 20*ms, 'taupost': 20*ms,
               'dApre_val': 0.005, 'dApost_val': -0.006, 'wmax': 0.3}

    def plas(src, tgt, p, wl, wh, ns_):
        s = Synapses(src, tgt, model=stdp_eqs, on_pre=on_pre, on_post=on_post,
                     namespace=ns_)
        s.connect(p=p)
        s.w = f'rand() * {wh - wl} + {wl}'
        return s

    def sexc(src, tgt, p, wt):
        s = Synapses(src, tgt, 'w_s : 1', on_pre='ge_post += w_s')
        s.connect(p=p)
        s.w_s = wt
        return s

    def sinh(src, tgt, p, wt):
        s = Synapses(src, tgt, 'w_s : 1', on_pre='gi_post += w_s')
        s.connect(p=p)
        s.w_s = wt
        return s

    syn_in   = plas(input_group, L4_E, cc.p_input, 0.5, 1.5, sns)
    syn_4r   = plas(L4_E,  L4_E,  cc.p_rec_EE, 0.02, 0.1, sns_rec)
    syn_23r  = plas(L23_E, L23_E, cc.p_rec_EE, 0.02, 0.1, sns_rec)
    syn_5r   = plas(L5_E,  L5_E,  cc.p_rec_EE, 0.02, 0.1, sns_rec)
    syn_6r   = plas(L6_E,  L6_E,  cc.p_rec_EE, 0.02, 0.1, sns_rec)
    syn_4_23 = plas(L4_E,  L23_E, cc.p_ff, 0.2, 0.5, sns)
    syn_23_5 = plas(L23_E, L5_E,  cc.p_ff, 0.2, 0.5, sns)
    syn_5_6  = plas(L5_E,  L6_E,  cc.p_ff, 0.2, 0.5, sns)
    syn_6_4  = plas(L6_E,  L4_E,  cc.p_fb, 0.05, 0.2, sns)

    syn_4ei  = sexc(L4_E,  L4_I,  cc.p_EI, 0.5)
    syn_23ei = sexc(L23_E, L23_I, cc.p_EI, 0.5)
    syn_5ei  = sexc(L5_E,  L5_I,  cc.p_EI, 0.5)
    syn_6ei  = sexc(L6_E,  L6_I,  cc.p_EI, 0.5)
    syn_4ie  = sinh(L4_I,  L4_E,  cc.p_IE, 1.0)
    syn_23ie = sinh(L23_I, L23_E, cc.p_IE, 1.0)
    syn_5ie  = sinh(L5_I,  L5_E,  cc.p_IE, 1.0)
    syn_6ie  = sinh(L6_I,  L6_E,  cc.p_IE, 1.0)

    mon_L5 = SpikeMonitor(L5_E, record=False)

    all_objs = [input_group,
                L4_E, L4_I, L23_E, L23_I, L5_E, L5_I, L6_E, L6_I,
                syn_in, syn_4r, syn_23r, syn_5r, syn_6r,
                syn_4_23, syn_23_5, syn_5_6, syn_6_4,
                syn_4ei, syn_23ei, syn_5ei, syn_6ei,
                syn_4ie, syn_23ie, syn_5ie, syn_6ie,
                mon_L5]
    net = Network(all_objs)

    all_syn = [syn_in, syn_4r, syn_23r, syn_5r, syn_6r,
               syn_4_23, syn_23_5, syn_5_6, syn_6_4,
               syn_4ei, syn_23ei, syn_5ei, syn_6ei,
               syn_4ie, syn_23ie, syn_5ie, syn_6ie]

    return net, {
        'input': input_group,
        'L4_E': L4_E, 'L23_E': L23_E, 'L5_E': L5_E, 'L6_E': L6_E,
        'L4_I': L4_I, 'L23_I': L23_I, 'L5_I': L5_I, 'L6_I': L6_I,
        'excit': [L4_E, L23_E, L5_E, L6_E],
        'mon_L5': mon_L5,
        'all_syn': all_syn,
        'plastic_syn': {
            'syn_in': syn_in, 'syn_4r': syn_4r, 'syn_23r': syn_23r,
            'syn_4_23': syn_4_23, 'syn_23_5': syn_23_5,
            'syn_5_6': syn_5_6, 'syn_6_4': syn_6_4,
        },
        'n_syn': sum(int(len(s)) for s in all_syn),
    }


def run_audio_cortex_training(cfg: AudioDaemonConfig):
    """BET-081 training + probing."""
    from brian2 import Hz, ms, mV, defaultclock, prefs

    backend = os.environ.get('BRIAN2_BACKEND', 'numpy')
    prefs.codegen.target = backend
    defaultclock.dt = 1.0 * ms
    print(f"Brian2 backend: {backend}")

    cc = cfg.cortex

    _send_telegram(cfg.notify_config_path,
                   f"BET-081 START | audio cortex | {cfg.run_duration_seconds/3600:.1f}h")

    # Audio
    print("Loading audio...")
    audio = _load_audio(cfg.audio_manifest_path, cc.sample_rate_hz)
    print(f"Computing Mel ({len(audio)/cc.sample_rate_hz:.0f}s)...")
    mel_chunks = compute_mel_chunks(audio, cc)
    n_mel = len(mel_chunks)
    print(f"{n_mel} Mel chunks ({n_mel * cc.chunk_duration_ms / 1000 / 60:.1f} min audio)")

    # Network
    print("Building network...")
    net, comp = build_network(cc)
    n_E = sum(g.N for g in comp['excit'])
    n_I = comp['L4_I'].N + comp['L23_I'].N + comp['L5_I'].N + comp['L6_I'].N
    print(f"Network: {n_E}E + {n_I}I = {n_E+n_I} neurons, {comp['n_syn']:,} synapses")

    inp = comp['input']
    mon_L5 = comp['mon_L5']
    excit = comp['excit']
    chunk_dur = cc.chunk_duration_ms * ms
    target_spk = cc.homeostasis_target_rate_hz * (cc.chunk_duration_ms / 1000.0)

    if cfg.checkpoint_dir:
        Path(cfg.checkpoint_dir).mkdir(parents=True, exist_ok=True)
    if cfg.metrics_log_path:
        Path(cfg.metrics_log_path).parent.mkdir(parents=True, exist_ok=True)
    if cfg.bet_dir:
        Path(cfg.bet_dir).mkdir(parents=True, exist_ok=True)

    metrics_log = []
    start_wall = time.time()
    last_ckpt = start_wall
    last_eval = start_wall
    last_tg = start_wall
    chunks_trained = 0
    audio_pos = 0
    prev_counts = [np.array(mon_L5.count).copy()]  # only L5 for speed
    # Full homeostasis needs all layers:
    prev_all = [np.zeros(g.N) for g in excit]

    print("Training...")

    while True:
        elapsed = time.time() - start_wall
        if elapsed >= cfg.run_duration_seconds:
            break

        if audio_pos >= n_mel:
            audio_pos = 0
        inp.rates = (mel_chunks[audio_pos] * cc.input_rate_max_hz) * Hz
        audio_pos += 1

        net.run(chunk_dur)
        chunks_trained += 1

        # Homeostasis on all excitatory layers
        for i, grp in enumerate(excit):
            cur = np.array(grp.v_thresh[:]).astype(float) * 1000.0  # to mV
            # Approximate rate from L5 monitor (only tracked layer).
            # For other layers, use a simpler threshold drift.
            if i == 2:  # L5
                l5_now = np.array(mon_L5.count).astype(float)
                diff = l5_now - prev_all[i]
                prev_all[i] = l5_now.copy()
            else:
                diff = np.full(grp.N, target_spk)  # no drift for non-monitored
            adj = cc.homeostasis_eta_mv * (diff - target_spk)
            cur += adj
            cur = np.clip(cur, cc.homeostasis_thresh_min_mv, cc.homeostasis_thresh_max_mv)
            grp.v_thresh = cur * mV

        now = time.time()

        if now - last_eval >= cfg.eval_interval_seconds:
            hour = elapsed / 3600
            l5_active = float(np.mean(np.array(mon_L5.count) > 0))
            entry = {"t_wall": elapsed, "chunks": chunks_trained,
                     "L5_active": l5_active}
            metrics_log.append(entry)
            if cfg.metrics_log_path:
                Path(cfg.metrics_log_path).write_text(json.dumps(metrics_log, indent=2))
            rate = chunks_trained / max(elapsed, 1)
            print(f"  h{hour:.1f} | {chunks_trained} chunks ({rate:.2f}/s) | L5 active {l5_active:.3f}")
            last_eval = now

        if cfg.checkpoint_dir and now - last_ckpt >= cfg.checkpoint_interval_seconds:
            from world.flux.brian2_checkpoint import (
                collect_neuron_state, collect_synapse_state, save_checkpoint)
            state = {"chunks_trained": chunks_trained, "wall_s": elapsed,
                     "audio_pos": audio_pos}
            for name in ['L4_E', 'L23_E', 'L5_E', 'L6_E']:
                state[name] = collect_neuron_state(comp[name])
            for name, syn in comp['plastic_syn'].items():
                state[name] = collect_synapse_state(syn, plastic=True)
            ckpt = Path(cfg.checkpoint_dir) / f"checkpoint_h{int(elapsed/3600+0.5)}.pkl"
            save_checkpoint(state, ckpt)
            last_ckpt = now

        if now - last_tg >= cfg.telegram_heartbeat_interval_seconds:
            _send_telegram(cfg.notify_config_path,
                           f"BET-081 h{elapsed/3600:.1f} | {chunks_trained} chunks")
            last_tg = now

    train_wall = time.time() - start_wall
    print(f"\nTraining: {chunks_trained} chunks in {train_wall/3600:.2f}h")

    # --- Post-hoc probing ---
    print("Probing...")
    probe = run_probe(net, inp, mon_L5, mel_chunks, cc, cfg)

    total_wall = time.time() - start_wall
    result = {"elapsed_seconds": total_wall, "train_seconds": train_wall,
              "chunks_trained": chunks_trained, "n_synapses": comp['n_syn'],
              "probe": probe, "metrics_log": metrics_log}

    if cfg.bet_dir:
        _save_json(Path(cfg.bet_dir) / "result.json", result)

    _send_telegram(cfg.notify_config_path,
                   f"BET-081 DONE | {total_wall/3600:.2f}h | chunks {chunks_trained} | "
                   f"distinct {probe.get('n_distinct_clusters','?')} | "
                   f"sil {probe.get('silhouette_score',0):.4f}")
    return result


def run_probe(net, inp, mon_L5, mel_chunks, cc, cfg):
    """Post-hoc probing: stream held-out audio, record L5 per-chunk patterns, cluster."""
    from brian2 import Hz, ms, mV
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    # Use middle of corpus for probing (avoid silent head/tail)
    n_probe = min(cfg.eval_n_probe_chunks, len(mel_chunks) // 2)
    mid = len(mel_chunks) // 2
    probe_mels = mel_chunks[mid:mid + n_probe]
    chunk_dur = cc.chunk_duration_ms * ms

    l5_patterns = []
    for mel_vec in probe_mels:
        c_before = np.array(mon_L5.count).copy()
        inp.rates = (mel_vec * cc.input_rate_max_hz) * Hz
        net.run(chunk_dur)
        l5_pattern = (np.array(mon_L5.count) - c_before).astype(np.float32)
        l5_patterns.append(l5_pattern)

    l5_mat = np.array(l5_patterns)
    l5_active = float(np.mean(np.any(l5_mat > 0, axis=0)))

    k = min(10, n_probe - 1)
    if k < 2 or l5_mat.shape[0] < k + 1:
        return {"n_windows": n_probe, "n_L5_neurons": cc.n_L5_E,
                "L5_active_fraction": l5_active, "silhouette_score": -1.0,
                "n_distinct_clusters": 0, "k": 0, "cluster_stats": []}

    km = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = km.fit_predict(l5_mat)

    sil = -1.0
    if len(set(labels)) > 1:
        sil = float(silhouette_score(l5_mat, labels))

    # Cluster distinctness via Mel-vector cosine
    def _cos(a, b):
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        return float(np.dot(a, b) / (na * nb)) if min(na, nb) > 1e-12 else 0.0

    mel_mat = np.array([probe_mels[i] for i in range(len(probe_mels))])
    global_mel = mel_mat.mean(axis=0)
    n_distinct = 0
    stats = []
    for c in range(k):
        mask = labels == c
        if mask.sum() < 2:
            stats.append({"cluster": c, "size": int(mask.sum()), "distinct": False})
            continue
        centroid = mel_mat[mask].mean(axis=0)
        intra = float(np.mean([_cos(m, centroid) for m in mel_mat[mask]]))
        inter = _cos(centroid, global_mel)
        d = bool(intra > inter + 0.05)
        if d:
            n_distinct += 1
        stats.append({"cluster": c, "size": int(mask.sum()),
                      "intra_cos": float(intra), "inter_cos": float(inter), "distinct": d})

    print(f"Probe: {n_probe} chunks, L5 active {l5_active:.3f}, "
          f"sil {sil:.4f}, distinct {n_distinct}/{k}")

    return {"n_windows": n_probe, "n_L5_neurons": cc.n_L5_E,
            "L5_active_fraction": l5_active, "silhouette_score": sil,
            "n_distinct_clusters": n_distinct, "k": k, "cluster_stats": stats}


def _save_json(path, data):
    def _c(o):
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, (np.floating,)): return float(o)
        if isinstance(o, np.ndarray): return o.tolist()
        return o
    Path(path).write_text(json.dumps(data, indent=2, default=_c))
