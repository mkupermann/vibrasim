"""JEP-248 — the EBM query mode: rank fact plausibility by ENERGY (not retrieval).

Clamp a full candidate fact concat(X_code, Y_code) and read net.energy (low = plausible). Does energy separate
TRUE direct edges from FALSE pairs? Do TRANSITIVE (unstored) edges score low (generalize) or high (memory boundary)?
Established (EBM energy-as-plausibility, Hopfield energy landscape), named.

Pre-registered bars in docs/amendments/jep248_energy_query.md.
"""
import json
from pathlib import Path
import numpy as np

from tools.run_jep232_relation_store import KEY, VAL, N, codes, store, make_facts


def auc(pos, neg):
    """P(a random pos has LOWER energy than a random neg) -- pos=direct-true, neg=false."""
    pos, neg = np.asarray(pos), np.asarray(neg)
    wins = sum((p < n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def run_seed(seed, K=12):
    code = codes(K + 1, seed)
    facts = make_facts(K, K + 1)              # direct edges (i,i+1)
    net = store(facts, code, seed, train=True)

    def E(x, y):
        return net.energy(np.concatenate([code[x], code[y]]))

    direct = [E(i, i + 1) for i in range(K)]
    # FALSE = pairs that are NOT ancestors (y <= x in the chain): never a true is-a edge
    false = [E(x, y) for x in range(K + 1) for y in range(K + 1) if y <= x][:40]
    transitive = [E(i, j) for i in range(K + 1) for j in range(i + 2, K + 1)]

    a_auc = auc(direct, false)
    cut = (np.mean(direct) + np.mean(false)) / 2
    acc = (sum(d < cut for d in direct) + sum(f >= cut for f in false)) / (len(direct) + len(false))
    md, mf, mt = float(np.mean(direct)), float(np.mean(false)), float(np.mean(transitive))
    trans_on_false_side = mt >= md + 0.5 * (mf - md)
    no_fp_transitive = all(t >= cut for t in transitive)        # no transitive pair is called 'true' by the cut
    return {"auc": float(a_auc), "acc": float(acc), "mean_direct": round(md, 1), "mean_false": round(mf, 1),
            "mean_transitive": round(mt, 1), "cut": round(float(cut), 1),
            "trans_on_false_side": bool(trans_on_false_side), "no_fp_transitive": bool(no_fp_transitive)}


if __name__ == "__main__":
    print("=== JEP-248: EBM energy-query mode (fact plausibility by energy) ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: AUC(direct<false)={r['auc']:.2f} acc={r['acc']:.2f} | mean energy direct={r['mean_direct']} "
              f"false={r['mean_false']} transitive={r['mean_transitive']} (cut {r['cut']}) | "
              f"transitive on false-side={r['trans_on_false_side']} no-FP-transitive={r['no_fp_transitive']}", flush=True)

    J248a = all(R[s]['auc'] >= 0.90 for s in seeds)
    J248b = all(R[s]['acc'] >= 0.85 for s in seeds)
    J248c = all(R[s]['trans_on_false_side'] for s in seeds)
    J248d = all(R[s]['no_fp_transitive'] for s in seeds)
    passed = J248a and J248b and J248c

    print("\n--- VERDICT ---", flush=True)
    print(f"J248a energy separates direct-true/false (AUC>=.90): {J248a}", flush=True)
    print(f"J248b threshold classifies direct facts (>=.85)    : {J248b}", flush=True)
    print(f"J248c transitive NOT low-energy (memory boundary)  : {J248c}", flush=True)
    print(f"J248d cut admits only direct stored edges          : {J248d}", flush=True)
    verdict = ("PASS - the substrate supports an EBM energy-query for DIRECT fact plausibility; it does NOT "
               "generalize to transitive edges (only chaining does) -- the JEP-245 boundary from the energy side") \
        if passed else "NULL/partial"
    print(f"\nJEP-248: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP248"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J248a": J248a, "J248b": J248b,
         "J248c": J248c, "J248d": J248d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
