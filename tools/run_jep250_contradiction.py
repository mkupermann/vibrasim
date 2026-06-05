"""JEP-250 — contradiction as energy FRUSTRATION: can the substrate natively flag an inconsistent fact?

Contradicted key X is trained toward BOTH code[Y] and -code[Y] (the negation); the shared key is pulled to opposite
attractors -> Ising frustration -> shallower (higher) energy + ambiguous retrieval. Tests whether energy/confidence
natively flag inconsistency. Established (Ising frustration, Hopfield mixed states), named.

Pre-registered bars in docs/amendments/jep250_contradiction_frustration.md.
"""
import json
from pathlib import Path
import numpy as np

from world.energy import EnergyNet
from tools.run_jep232_relation_store import KEY, VAL, N, codes


def run_seed(seed, n_each=4):
    # concepts: keys 0..2*ne-1 (each its own), values share a pool; build consistent + contradicted facts
    n_keys = 2 * n_each
    code = codes(n_keys + n_each + 1, seed)            # keys + value targets
    consistent = [(k, n_keys + (k % n_each)) for k in range(n_each)]               # X_k -> Y_k
    contradicted = [(n_each + k, n_keys + (k % n_each)) for k in range(n_each)]     # X'_k -> Y_k AND -> not Y_k

    pats = []
    for x, y in consistent:
        pats.append(np.concatenate([code[x], code[y]]))
    for x, y in contradicted:
        pats.append(np.concatenate([code[x], code[y]]))
        pats.append(np.concatenate([code[x], -code[y]]))      # the negation: same key, opposite value

    net = EnergyNet(n_per_module=N, n_modules=1, seed=seed)
    for _ in range(140):
        net.train_epoch(pats, cue_frac=0.5, lr=0.02, relax_steps=12)

    def probe(x, y):
        net.state = np.random.default_rng(seed + x).choice([-1.0, 1.0], N)
        s = net.relax(np.arange(KEY), code[x], steps=40)
        val = np.sign(s[KEY:KEY + VAL])
        conf = abs(float(val @ code[y])) / KEY            # clean +Y or -Y -> ~1; frustrated mush -> ~0
        recalled = int(np.argmax([np.sign(s[KEY:KEY + VAL]) @ code[c] for c in range(len(code))]))
        return net.energy(s), conf, recalled

    cons_E, cons_conf, cons_ok = [], [], []
    for x, y in consistent:
        E, conf, rec = probe(x, y); cons_E.append(E); cons_conf.append(conf); cons_ok.append(rec == y)
    con_E, con_conf = [], []
    for x, y in contradicted:
        E, conf, rec = probe(x, y); con_E.append(E); con_conf.append(conf)

    cons_E, con_E = np.array(cons_E), np.array(con_E)
    cut = (cons_E.mean() + con_E.mean()) / 2
    acc = (sum(e < cut for e in cons_E) + sum(e >= cut for e in con_E)) / (len(cons_E) + len(con_E))
    return {"mean_E_consistent": round(float(cons_E.mean()), 1), "mean_E_contradicted": round(float(con_E.mean()), 1),
            "mean_conf_consistent": round(float(np.mean(cons_conf)), 2),
            "mean_conf_contradicted": round(float(np.mean(con_conf)), 2),
            "cut": round(float(cut), 1), "sep_acc": round(float(acc), 2), "all_consistent_recalled": bool(all(cons_ok))}


if __name__ == "__main__":
    print("=== JEP-250: contradiction as energy frustration ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: energy consistent={r['mean_E_consistent']} contradicted={r['mean_E_contradicted']} | "
              f"confidence consistent={r['mean_conf_consistent']} contradicted={r['mean_conf_contradicted']} | "
              f"sep-acc={r['sep_acc']} all-consistent-recalled={r['all_consistent_recalled']}", flush=True)

    J250a = all(R[s]['mean_E_contradicted'] > R[s]['mean_E_consistent'] + 0.20 * abs(R[s]['mean_E_consistent'])
                for s in seeds)
    J250b = all(R[s]['mean_conf_consistent'] - R[s]['mean_conf_contradicted'] >= 0.30 for s in seeds)
    J250c = all(R[s]['sep_acc'] >= 0.85 for s in seeds)
    J250d = all(R[s]['all_consistent_recalled'] for s in seeds)
    passed = J250a and J250b and J250c

    print("\n--- VERDICT ---", flush=True)
    print(f"J250a contradiction raises energy (>=20%)  : {J250a}", flush=True)
    print(f"J250b contradiction lowers confidence (>=.30): {J250b}", flush=True)
    print(f"J250c energy threshold separates (>=.85)   : {J250c}", flush=True)
    print(f"J250d consistent facts still recalled      : {J250d}", flush=True)
    verdict = ("PASS - the substrate NATIVELY flags a contradiction by energy frustration (shallower, ambiguous "
               "minimum, energy-separable from consistent facts)") if passed else "NULL/partial"
    print(f"\nJEP-250: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP250"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J250a": J250a, "J250b": J250b,
         "J250c": J250c, "J250d": J250d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
