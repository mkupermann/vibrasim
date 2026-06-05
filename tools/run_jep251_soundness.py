"""JEP-251 — property-based SOUNDNESS of the substrate relational store at scale.

Across many random (single-parent tree) taxonomies within capacity, compare the energy-gated substrate is_a to the
symbolic transitive closure over ALL ordered pairs. Validates correctness broadly + classifies the residual error.
Established (property-based testing, transitive closure), named.

Pre-registered bars in docs/amendments/jep251_substrate_soundness.md.
"""
import json
from pathlib import Path
import numpy as np

from world.energy import EnergyNet
from tools.run_jep232_relation_store import KEY, VAL, N

N_TAX = 50
M = 12                      # concepts per taxonomy (<= ~18 edges within capacity)


def random_tree(M, rng):
    parent = {0: None}
    for c in range(1, M):
        parent[c] = int(rng.integers(0, c))      # parent chosen from earlier concepts -> a forest/tree
    return parent


def symbolic_isa(parent):
    anc = {c: set() for c in parent}
    for c in parent:
        p = parent[c]
        while p is not None:
            anc[c].add(p); p = parent[p]
    return anc


def build(parent, code, seed):
    edges = [(c, parent[c]) for c in parent if parent[c] is not None]
    net = EnergyNet(n_per_module=N, n_modules=1, seed=seed)
    pats = [np.concatenate([code[c], code[p]]) for c, p in edges]
    for _ in range(140):
        net.train_epoch(pats, cue_frac=0.5, lr=0.02, relax_steps=12)
    e_cut = 0.7 * float(np.median([net.energy(p) for p in pats])) if pats else -1
    return net, e_cut


def egate_chain(net, x, code, e_cut, seed, M, max_depth=10):
    reach, seen, cur = set(), {x}, x
    for d in range(max_depth):
        net.state = np.random.default_rng(seed + d).choice([-1.0, 1.0], N)
        s = net.relax(np.arange(KEY), code[cur], steps=40)
        if net.energy(s) > e_cut:
            break
        val = np.sign(s[KEY:KEY + VAL])
        nxt = int(np.argmax([val @ code[k] for k in range(M)]))
        if nxt in seen:
            break
        reach.add(nxt); seen.add(nxt); cur = nxt
    return reach


def run_seed(seed):
    rng = np.random.default_rng(seed)
    per_tax, sys_fp = [], 0
    total_ok = total = 0
    for t in range(N_TAX):
        parent = random_tree(M, rng)
        anc = symbolic_isa(parent)
        code = {c: rng.choice([-1.0, 1.0], KEY) for c in range(M)}
        net, e_cut = build(parent, code, seed * 1000 + t)
        reach = {x: egate_chain(net, x, code, e_cut, seed * 1000 + t, M) for x in range(M)}
        ok = tot = 0
        for x in range(M):
            for y in range(M):
                if x == y:
                    continue
                tot += 1
                sub = y in reach[x]; sym = y in anc[x]
                ok += (sub == sym)
                if sub and not sym:        # potential leak -> check if systematic (repeat with 5 re-inits)
                    reps = sum(y in egate_chain(net, x, code, e_cut, seed * 1000 + t + 9000 + r, M) for r in range(5))
                    if reps >= 4:
                        sys_fp += 1
        per_tax.append(ok / tot); total_ok += ok; total += tot
    per_tax = np.array(per_tax)
    return {"match": round(total_ok / total, 4), "sys_fp": int(sys_fp),
            "frac_perfect": round(float((per_tax >= 0.9999).mean()), 3), "mean_per_tax": round(float(per_tax.mean()), 4),
            "worst_tax": round(float(per_tax.min()), 3)}


if __name__ == "__main__":
    print(f"=== JEP-251: substrate-store soundness over {N_TAX} random taxonomies (M={M}) ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: match={r['match']} | systematic-FP={r['sys_fp']} | "
              f"frac-perfect-tax={r['frac_perfect']} mean-per-tax={r['mean_per_tax']} worst={r['worst_tax']}",
              flush=True)

    J251a = all(R[s]['match'] >= 0.98 for s in seeds)
    J251b = all(R[s]['sys_fp'] == 0 for s in seeds)
    J251c = all(R[s]['frac_perfect'] >= 0.90 for s in seeds)
    J251d = all(R[s]['mean_per_tax'] >= 0.97 for s in seeds)
    passed = J251a and J251b

    print("\n--- VERDICT ---", flush=True)
    print(f"J251a match >= 0.98 at scale       : {J251a}", flush=True)
    print(f"J251b 0 systematic false-positives : {J251b}", flush=True)
    print(f"J251c >=90% taxonomies perfect     : {J251c}", flush=True)
    print(f"J251d mean per-tax >= 0.97         : {J251d}", flush=True)
    verdict = ("PASS - the substrate relational store is SOUND at scale (matches the symbolic closure, no "
               "systematic leaks)") if passed else "NULL/partial"
    print(f"\nJEP-251: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP251"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J251a": J251a, "J251b": J251b,
         "J251c": J251c, "J251d": J251d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
