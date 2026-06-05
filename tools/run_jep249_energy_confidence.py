"""JEP-249 — energy as graded CONFIDENCE: does fact support (restatement count) modulate energy?

Edges restated s in {1,2,3,5,8} times; measure whether energy(concat(X,Y)) decreases monotonically with support
-> graded, frequency-calibrated confidence the binary symbolic engine lacks. Established (Hebbian frequency effects,
EBM energy = log-plausibility), named.

Pre-registered bars in docs/amendments/jep249_energy_confidence.md.
"""
import json
from pathlib import Path
import numpy as np

from world.energy import EnergyNet
from tools.run_jep232_relation_store import KEY, VAL, N, codes


def spearman(x, y):
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    rx = rx - rx.mean(); ry = ry - ry.mean()
    d = np.sqrt((rx**2).sum() * (ry**2).sum())
    return float((rx * ry).sum() / d) if d > 0 else 0.0


SUPPORTS = [1, 2, 3, 5, 8]


def run_seed(seed):
    n = len(SUPPORTS) + 1
    code = codes(n, seed)
    facts = [(i, i + 1) for i in range(len(SUPPORTS))]      # one edge per support level
    # training pattern list: edge i appears SUPPORTS[i] times
    pats = []
    for i, (c, p) in enumerate(facts):
        pats += [np.concatenate([code[c], code[p]])] * SUPPORTS[i]
    net = EnergyNet(n_per_module=N, n_modules=1, seed=seed)
    for _ in range(140):
        net.train_epoch(pats, cue_frac=0.5, lr=0.02, relax_steps=12)

    energies, recalled = [], []
    for (c, p) in facts:
        energies.append(net.energy(np.concatenate([code[c], code[p]])))
        net.state = np.random.default_rng(seed + c).choice([-1.0, 1.0], N)
        s = net.relax(np.arange(KEY), code[c], steps=40)
        val = np.sign(s[KEY:KEY + VAL])
        sims = np.array([val @ code[k] for k in range(n)]); sims[c] = -np.inf
        recalled.append(int(np.argmax(sims)) == p)
    energies = np.array(energies)
    rho = spearman(np.array(SUPPORTS, float), -energies)        # more support -> lower energy
    # expected: energy non-increasing as support rises; count inversions (a later, higher-support edge with HIGHER energy)
    inversions = int(sum(energies[i + 1] > energies[i] + 1e-6 for i in range(len(energies) - 1)))
    margin = (energies[0] - energies[-1]) / max(abs(energies[0]), 1e-9)   # s=8 vs s=1, fraction of s=1 magnitude
    return {"energies": [round(float(e), 1) for e in energies], "spearman": round(rho, 2),
            "margin_frac": round(float(margin), 3), "all_recalled": bool(all(recalled)), "inversions": int(inversions)}


if __name__ == "__main__":
    print("=== JEP-249: energy as graded confidence (support -> attractor depth) ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: support {SUPPORTS} -> energy {r['energies']} | spearman(support,-E)={r['spearman']} "
              f"margin(s1->s8)={r['margin_frac']} all-recalled={r['all_recalled']} inversions={r['inversions']}",
              flush=True)

    J249a = all(R[s]['spearman'] >= 0.80 for s in seeds)
    J249b = all(R[s]['margin_frac'] >= 0.10 for s in seeds)
    J249c = all(R[s]['all_recalled'] for s in seeds)
    J249d = all(R[s]['inversions'] <= 1 for s in seeds)
    passed = J249a and J249b and J249c

    print("\n--- VERDICT ---", flush=True)
    print(f"J249a support lowers energy (spearman>=.80): {J249a}", flush=True)
    print(f"J249b distinguishable extremes (>=10%)     : {J249b}", flush=True)
    print(f"J249c all facts still recalled (true)      : {J249c}", flush=True)
    print(f"J249d monotone (<=1 inversion)             : {J249d}", flush=True)
    verdict = ("PASS - the substrate gives GRADED confidence: a fact's energy encodes its support, a calibrated "
               "signal the binary symbolic engine lacks") if passed else "NULL/partial"
    print(f"\nJEP-249: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP249"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J249a": J249a, "J249b": J249b,
         "J249c": J249c, "J249d": J249d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
