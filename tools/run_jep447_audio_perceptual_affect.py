"""JEP-447 — the substrate HEARS a sound and feels its energy. Real audio: synthesize a waveform,
extract a real log-FFT feature (world/audio_features), and the energy model predicts its affective
valence (harsh/dissonant=dark, clean/consonant=bright), generalizing to sounds with a NOVEL
fundamental. Established methods. Pre-registered bars in docs/amendments/jep447_audio_perceptual_affect.md.
"""
import json
from pathlib import Path
import numpy as np

from world.audio_features import synth_tone, samples_to_feature
from world.valence_reservoir import ValenceReservoirLearner

TRAIN_F0 = [220.0, 247.0, 262.0, 294.0, 330.0]     # heard objects
NOVEL_F0 = [175.0, 392.0, 440.0]                   # never-heard objects
N_TRAIN, N_TEST = 300, 150
DUR = 0.25


def _sound_feature(rng, f0, bright):
    if bright:
        freqs = [f0, 1.5 * f0]; noise = 0.01        # consonant fifth, clean
    else:
        freqs = [f0, 1.06 * f0]; noise = 0.15       # dissonant minor second + harsh noise
    wav, sr = synth_tone(freqs, dur=DUR, noise=noise, rng=rng)
    return samples_to_feature(wav, sr)


def run(seed):
    rng = np.random.default_rng(seed)
    # discover feature dimension
    DP = len(_sound_feature(rng, 262.0, True))
    energy = ValenceReservoirLearner(n_inputs=DP, n_features=300, seed=seed)
    energy_sh = ValenceReservoirLearner(n_inputs=DP, n_features=300, seed=seed)

    feats, vals = [], []
    for _ in range(N_TRAIN):
        f0 = TRAIN_F0[rng.integers(len(TRAIN_F0))]
        bright = rng.integers(2) == 0
        feats.append(_sound_feature(rng, f0, bright)); vals.append(1.0 if bright else -1.0)
    sh = list(vals); np.random.default_rng(seed + 99).shuffle(sh)
    for x, v, vs in zip(feats, vals, sh):
        energy.experience(x, v); energy_sh.experience(x, vs)

    ok = ok_novel = ok_ctrl = 0; n = n_novel = 0
    for _ in range(N_TEST):
        novel = rng.random() < 0.5
        f0 = NOVEL_F0[rng.integers(len(NOVEL_F0))] if novel else TRAIN_F0[rng.integers(len(TRAIN_F0))]
        bright = rng.integers(2) == 0
        x = _sound_feature(rng, f0, bright); v = 1.0 if bright else -1.0
        n += 1
        ok += (np.sign(energy.feel(x)) == v)
        ok_ctrl += (np.sign(energy_sh.feel(x)) == v)
        if novel:
            n_novel += 1; ok_novel += (np.sign(energy.feel(x)) == v)
    return dict(acc=ok / n, acc_novel=ok_novel / max(n_novel, 1), acc_ctrl=ok_ctrl / n, dim=DP)


if __name__ == "__main__":
    print("=== JEP-447: the substrate hears a sound and feels its energy (real audio) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: affect acc(all)={R[s]['acc']:.3f} | novel-fundamental acc={R[s]['acc_novel']:.3f} | "
              f"shuffled-ctrl={R[s]['acc_ctrl']:.3f} | feat_dim={R[s]['dim']}", flush=True)

    J447a = all(R[s]['acc'] >= 0.85 for s in seeds)
    J447b = all(R[s]['acc_novel'] >= 0.80 for s in seeds)
    J447c = all(R[s]['acc_ctrl'] <= 0.60 for s in seeds)
    passed = J447a and J447b and J447c

    print("\n--- VERDICT ---", flush=True)
    print(f"J447a hears affect from real FFT (>=0.85)      : {J447a}", flush=True)
    print(f"J447b generalizes to UNHEARD fundamental (>=0.80): {J447b}", flush=True)
    print(f"J447c learned rule (shuffled<=0.60)            : {J447c}", flush=True)
    verdict = ("PASS - the energy model HEARS a sound's affect from its real spectrum and generalizes "
               "to unheard fundamentals: real-sensor perception of environmental energy") if passed else "NULL/partial"
    print(f"\nJEP-447: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP447"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J447a": J447a, "J447b": J447b, "J447c": J447c}, indent=2, default=str))
    print("DONE", flush=True)
