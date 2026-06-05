"""JEP-446 — perceptual affect: the energy model predicts the valence of a PERCEPT from its
perceptual feature vector (the same kind active_learner grounds symbols from), and generalizes to
a NOVEL, unrecognized object — affect grounded in perception, not identity. Established methods.
Pre-registered bars in docs/amendments/jep446_perceptual_affect.md.
"""
import json
from pathlib import Path
import numpy as np

from world.active_learner import ActiveLearner
from world.valence_reservoir import ValenceReservoirLearner

DP = 64
NOISE_R = 0.5
N_TRAIN, N_TEST = 300, 150


def _unit(v):
    return v / (np.linalg.norm(v) + 1e-9)


def _make_world(seed):
    rng = np.random.default_rng(seed)
    protos = {f"S{i}": _unit(rng.standard_normal(DP)) for i in range(6)}   # S0..S4 trained, S5 novel
    sharp = _unit(rng.standard_normal(DP))                                  # the affect-bearing direction
    return rng, protos, sharp


def _percept(rng, proto, sharp):
    sign = 1.0 if rng.integers(2) == 0 else -1.0     # +1 smooth/bright, -1 sharp/dark
    sig = proto + 0.8 * sign * sharp
    sig = _unit(sig)
    nz = rng.standard_normal(DP); nz = nz * (NOISE_R / (np.linalg.norm(nz) + 1e-9))
    x = _unit(sig + nz)
    return x, sign


def run(seed, shuffle=False):
    rng, protos, sharp = _make_world(seed)
    al = ActiveLearner()
    energy = ValenceReservoirLearner(n_inputs=DP, n_features=300, seed=seed)
    energy_sh = ValenceReservoirLearner(n_inputs=DP, n_features=300, seed=seed)

    train_syms = [f"S{i}" for i in range(5)]
    vals = []
    samples = []
    for _ in range(N_TRAIN):
        sym = train_syms[rng.integers(5)]
        x, v = _percept(rng, protos[sym], sharp)
        al.teach("vision", sym, x)
        samples.append((x, v))
        vals.append(v)
    sh = list(vals); np.random.default_rng(seed + 99).shuffle(sh)
    for (x, v), vs in zip(samples, sh):
        energy.experience(x, v)
        energy_sh.experience(x, vs)

    # test: trained-symbol percepts + NOVEL-symbol (S5) percepts
    ok = ok_novel = ok_ctrl = 0
    n_all = n_novel = 0
    conf_trained, conf_novel = [], []
    for _ in range(N_TEST):
        novel = rng.random() < 0.5
        sym = "S5" if novel else train_syms[rng.integers(5)]
        x, v = _percept(rng, protos[sym], sharp)
        n_all += 1
        ok += (np.sign(energy.feel(x)) == v)
        ok_ctrl += (np.sign(energy_sh.feel(x)) == v)
        _, conf = al.guess("vision", x)          # (symbol, confidence)
        if novel:
            n_novel += 1
            ok_novel += (np.sign(energy.feel(x)) == v)
            conf_novel.append(conf)
        else:
            conf_trained.append(conf)
    return dict(acc=ok / n_all, acc_novel=ok_novel / max(n_novel, 1), acc_ctrl=ok_ctrl / n_all,
                conf_trained=float(np.mean(conf_trained)) if conf_trained else 0.0,
                conf_novel=float(np.mean(conf_novel)) if conf_novel else 0.0)


if __name__ == "__main__":
    print("=== JEP-446: perceptual affect (energy grounded in perception, not identity) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: affect acc(all)={R[s]['acc']:.3f} | novel-object acc={R[s]['acc_novel']:.3f} | "
              f"shuffled-ctrl={R[s]['acc_ctrl']:.3f} | conf trained={R[s]['conf_trained']:.2f} novel={R[s]['conf_novel']:.2f}",
              flush=True)

    J446a = all(R[s]['acc'] >= 0.85 for s in seeds)
    J446b = all(R[s]['acc_novel'] >= 0.80 and R[s]['conf_novel'] < R[s]['conf_trained'] for s in seeds)
    J446c = all(R[s]['acc_ctrl'] <= 0.60 for s in seeds)
    passed = J446a and J446b and J446c

    print("\n--- VERDICT ---", flush=True)
    print(f"J446a perceptual affect generalizes (>=0.85)        : {J446a}", flush=True)
    print(f"J446b affect transfers to NOVEL object (>=0.80, conf lower): {J446b}", flush=True)
    print(f"J446c learned rule (shuffled<=0.60)                 : {J446c}", flush=True)
    verdict = ("PASS - the energy model perceives affect from perceptual features and generalizes to "
               "UNRECOGNIZED objects: energy grounded in perception, independent of identity") if passed else "NULL/partial"
    print(f"\nJEP-446: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP446"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J446a": J446a, "J446b": J446b, "J446c": J446c}, indent=2, default=str))
    print("DONE", flush=True)
