"""Post-hoc analysis of BET-081 checkpoint — three discriminating tests.

1. Trivial Baseline: k-means on raw Mel vectors vs L5-spike k-means
2. Temporal Order Test: shuffled Mel → same L5 patterns?
3. Weight Selectivity: are trained STDP weights selective or homogeneous?

Runs on saved checkpoint, no new training needed.
"""
import json
import pickle
import numpy as np
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def load_checkpoint(path):
    with open(path, 'rb') as f:
        return pickle.load(f)


def analyze_weight_selectivity(ckpt):
    """Test 3: Are STDP weights selective (few strong paths) or homogeneous?"""
    print("=" * 60)
    print("TEST 3: Weight Selectivity Analysis")
    print("=" * 60)

    results = {}
    for name in ['syn_in', 'syn_4_23', 'syn_23_5', 'syn_5_6', 'syn_6_4',
                  'syn_4r', 'syn_23r', 'syn_5r', 'syn_6r']:
        if name not in ckpt:
            continue
        w = ckpt[name]['w']
        if len(w) == 0:
            continue

        # Selectivity metrics
        mean_w = float(np.mean(w))
        std_w = float(np.std(w))
        cv = std_w / mean_w if mean_w > 1e-12 else 0.0  # coefficient of variation
        gini = _gini(w)
        # Fraction of weights near max (>80% of wmax)
        wmax = w.max()
        frac_strong = float(np.mean(w > 0.8 * wmax)) if wmax > 0 else 0.0
        frac_near_zero = float(np.mean(w < 0.1 * wmax)) if wmax > 0 else 0.0
        n_syn = len(w)

        results[name] = {
            'n_syn': n_syn, 'mean': mean_w, 'std': std_w,
            'cv': cv, 'gini': gini,
            'frac_strong': frac_strong, 'frac_near_zero': frac_near_zero,
            'max': float(wmax), 'min': float(w.min()),
        }

        print(f"\n  {name}: {n_syn:,} synapses")
        print(f"    mean={mean_w:.4f}, std={std_w:.4f}, CV={cv:.3f}")
        print(f"    Gini={gini:.3f} (0=homogeneous, 1=maximally selective)")
        print(f"    {frac_strong*100:.1f}% strong (>80% wmax), "
              f"{frac_near_zero*100:.1f}% near-zero (<10% wmax)")
        print(f"    range=[{w.min():.4f}, {wmax:.4f}]")

    # Verdict
    input_gini = results.get('syn_in', {}).get('gini', 0)
    ff_ginis = [results[k]['gini'] for k in ['syn_4_23', 'syn_23_5'] if k in results]
    avg_ff_gini = np.mean(ff_ginis) if ff_ginis else 0

    print(f"\n  VERDICT: Input Gini={input_gini:.3f}, FF avg Gini={avg_ff_gini:.3f}")
    if input_gini > 0.3 or avg_ff_gini > 0.3:
        print("  -> SELECTIVE: STDP has differentiated pathways")
    else:
        print("  -> HOMOGENEOUS: weights converged to similar values")

    return results


def analyze_trivial_baseline(mel_chunks, l5_patterns):
    """Test 1: Does k-means on raw Mel find the same structure as L5?"""
    print("=" * 60)
    print("TEST 1: Trivial Baseline (Mel k-means vs L5 k-means)")
    print("=" * 60)

    k = 10
    # Mel clustering
    km_mel = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels_mel = km_mel.fit_predict(mel_chunks)
    sil_mel = silhouette_score(mel_chunks, labels_mel) if len(set(labels_mel)) > 1 else -1

    # L5 clustering
    km_l5 = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels_l5 = km_l5.fit_predict(l5_patterns)
    sil_l5 = silhouette_score(l5_patterns, labels_l5) if len(set(labels_l5)) > 1 else -1

    # Agreement: how much do the two clusterings overlap?
    from sklearn.metrics import adjusted_rand_score
    ari = adjusted_rand_score(labels_mel, labels_l5)

    print(f"\n  Mel k-means silhouette:  {sil_mel:.4f}")
    print(f"  L5 k-means silhouette:   {sil_l5:.4f}")
    print(f"  Adjusted Rand Index:      {ari:.4f} (0=independent, 1=identical)")

    if ari > 0.3:
        print("  -> L5 clusters AGREE with Mel clusters: substrate mirrors input structure")
    elif sil_l5 > sil_mel + 0.05:
        print("  -> L5 finds BETTER structure than raw Mel: substrate adds value")
    else:
        print("  -> L5 clusters are INDEPENDENT of Mel: substrate structure is internal, "
              "not input-driven")

    return {'sil_mel': sil_mel, 'sil_l5': sil_l5, 'ari': ari}


def analyze_temporal_order(mel_chunks, l5_patterns):
    """Test 2: Shuffled temporal order → different L5 patterns?

    We can't re-run the network here, but we CAN check if L5 patterns
    correlate with the temporal position (chunk index) or with Mel content.
    If L5 patterns correlate with position but not content → temporal.
    If with content but not position → feature extraction.
    If neither → noise.
    """
    print("=" * 60)
    print("TEST 2: Temporal vs Content Analysis")
    print("=" * 60)

    n = len(mel_chunks)
    positions = np.arange(n).reshape(-1, 1).astype(float)

    # Correlation of L5 patterns with temporal position
    # Use first 3 PCA components of L5
    from sklearn.decomposition import PCA
    pca = PCA(n_components=min(3, l5_patterns.shape[1]))
    l5_pca = pca.fit_transform(l5_patterns)

    # Correlation L5-PC1 with position
    corr_pos = np.abs(np.corrcoef(l5_pca[:, 0], np.arange(n))[0, 1])

    # Correlation L5-PC1 with Mel-PC1
    mel_pca = PCA(n_components=1).fit_transform(mel_chunks)
    corr_mel = np.abs(np.corrcoef(l5_pca[:, 0], mel_pca[:, 0])[0, 1])

    # Also: mutual information proxy via cluster agreement
    # Bin position into 10 bins, check if L5 clusters align
    pos_labels = np.digitize(np.arange(n), np.linspace(0, n, 11)) - 1
    km = KMeans(n_clusters=10, n_init=10, random_state=42)
    l5_labels = km.fit_predict(l5_patterns)

    from sklearn.metrics import adjusted_rand_score
    ari_pos = adjusted_rand_score(pos_labels, l5_labels)

    print(f"\n  |corr(L5-PC1, position)|: {corr_pos:.4f}")
    print(f"  |corr(L5-PC1, Mel-PC1)|:  {corr_mel:.4f}")
    print(f"  ARI(L5 clusters, temporal bins): {ari_pos:.4f}")

    if corr_mel > corr_pos + 0.1:
        print("  -> Content-driven: L5 responds to acoustic features")
    elif corr_pos > corr_mel + 0.1:
        print("  -> Temporal-driven: L5 tracks time, not content")
    else:
        print("  -> Mixed or weak: no clear dominance")

    return {'corr_position': corr_pos, 'corr_mel': corr_mel, 'ari_temporal': ari_pos}


def _gini(arr):
    """Gini coefficient (0=perfect equality, 1=maximal inequality)."""
    arr = np.abs(np.sort(arr.flatten()))
    n = len(arr)
    if n == 0 or arr.sum() == 0:
        return 0.0
    index = np.arange(1, n + 1)
    return float((2 * np.sum(index * arr) / (n * np.sum(arr))) - (n + 1) / n)


def main():
    bet_dir = Path.home() / ".eqmod" / "bet" / "BET-081"

    # Load checkpoint
    ckpt_path = bet_dir / "checkpoints" / "checkpoint_h3.pkl"
    if not ckpt_path.exists():
        # Try latest
        ckpts = sorted((bet_dir / "checkpoints").glob("checkpoint_*.pkl"))
        ckpt_path = ckpts[-1] if ckpts else None
    if not ckpt_path:
        print("No checkpoint found")
        return

    print(f"Loading checkpoint: {ckpt_path.name}")
    ckpt = load_checkpoint(ckpt_path)

    # Load result for probe data
    result_path = bet_dir / "result.json"
    if result_path.exists():
        result = json.loads(result_path.read_text())
    else:
        result = None

    # --- Test 3: Weight selectivity (only needs checkpoint) ---
    weight_results = analyze_weight_selectivity(ckpt)

    # --- For Tests 1 & 2, we need probe L5 patterns + Mel vectors ---
    # Re-run probe on checkpoint to get per-chunk L5 patterns + Mel vectors
    print("\n" + "=" * 60)
    print("Running probe on checkpoint for Tests 1 & 2...")
    print("=" * 60)

    from world.flux.brian2_audio_cortex import (
        AudioCortexConfig, compute_mel_chunks, build_network)
    from agent.flux.encoder_free_training import load_corpus_waveform_from_manifest
    from brian2 import Hz, ms, mV, defaultclock, prefs
    import os

    prefs.codegen.target = os.environ.get('BRIAN2_BACKEND', 'numpy')
    defaultclock.dt = 1.0 * ms

    cc = AudioCortexConfig()
    manifest = Path.home() / ".eqmod" / "training" / "EN" / "manifest.json"
    audio = load_corpus_waveform_from_manifest(
        manifest, sample_rate_hz=16000, corpus_rms_target=0.25).astype(np.float32)
    mel = compute_mel_chunks(audio, cc)

    # Build network and restore weights from checkpoint
    net, comp = build_network(cc)
    inp = comp['input']
    mon = comp['mon_L5']

    # Restore neuron + synapse state
    from brian2 import volt
    from world.flux.brian2_checkpoint import restore_neuron_state, restore_synapse_state
    for name in ['L4_E', 'L23_E', 'L5_E', 'L6_E']:
        if name in ckpt:
            restore_neuron_state(comp[name], ckpt[name])

    for ckpt_name in ['syn_in', 'syn_4r', 'syn_23r', 'syn_4_23',
                       'syn_23_5', 'syn_5_6', 'syn_6_4']:
        if ckpt_name in ckpt and ckpt_name in comp.get('plastic_syn', {}):
            restore_synapse_state(comp['plastic_syn'][ckpt_name], ckpt[ckpt_name])

    # Probe: 500 chunks from middle of corpus
    n_probe = 500
    mid = len(mel) // 2
    probe_mels = mel[mid:mid + n_probe]
    chunk_dur = cc.chunk_duration_ms * ms

    print(f"Probing {n_probe} chunks...")
    l5_patterns = []
    for i, mel_vec in enumerate(probe_mels):
        c_before = np.array(mon.count).copy()
        inp.rates = (mel_vec * cc.input_rate_max_hz) * Hz
        net.run(chunk_dur)
        diff = (np.array(mon.count) - c_before).astype(np.float32)
        l5_patterns.append(diff)
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{n_probe}")

    l5_mat = np.array(l5_patterns)
    mel_mat = np.array(probe_mels)

    print(f"\nL5 matrix: {l5_mat.shape}, nonzero rows: {np.any(l5_mat > 0, axis=1).sum()}/{n_probe}")

    # --- Test 1: Trivial baseline ---
    baseline_results = analyze_trivial_baseline(mel_mat, l5_mat)

    # --- Test 2: Temporal vs content ---
    temporal_results = analyze_temporal_order(mel_mat, l5_mat)

    # --- Summary ---
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Weight selectivity: Input Gini={weight_results.get('syn_in',{}).get('gini',0):.3f}")
    print(f"Trivial baseline: ARI={baseline_results['ari']:.4f}, "
          f"Mel sil={baseline_results['sil_mel']:.4f}, L5 sil={baseline_results['sil_l5']:.4f}")
    print(f"Temporal: corr_pos={temporal_results['corr_position']:.4f}, "
          f"corr_mel={temporal_results['corr_mel']:.4f}")

    # Save
    analysis = {
        'weights': {k: {kk: float(vv) if isinstance(vv, (float, np.floating)) else vv
                        for kk, vv in v.items()}
                    for k, v in weight_results.items()},
        'baseline': {k: float(v) for k, v in baseline_results.items()},
        'temporal': {k: float(v) for k, v in temporal_results.items()},
    }
    out = bet_dir / "analysis_discriminating.json"
    out.write_text(json.dumps(analysis, indent=2))
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
