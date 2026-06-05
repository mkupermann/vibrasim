"""JEP-243 — robust FULL engine on the substrate: per-hop AGGREGATION (JEP-241 cure) for composed queries.

Same typed multi-relation EnergyNet as JEP-242, but every hop is an aggregated hop: R gated independent retrievals,
majority-vote the winner (SIM_STOP preserved per retrieval so chains still stop at roots). Tests whether aggregation
closes the JEP-242 composed-query robustness gap across both seeds. Established (ensemble voting + CAM).

Pre-registered bars in docs/amendments/jep243_robust_full_engine_substrate.md.
"""
import json
from collections import Counter
from pathlib import Path
import numpy as np

from world.understanding import UnderstandingEngine
from tools.run_jep232_relation_store import KEY, VAL, N
from tools.run_jep242_full_engine_substrate import collect_edges, setup, build, SIM_STOP

R = 5
PASSAGE = ("A poodle is a dog. A dog is a mammal. A mammal is an animal. "
           "A heart is part of a dog. "
           "A virus causes a fever. A fever causes weakness. "
           "An elephant is bigger than a dog. A dog is bigger than a cat. "
           "The war happened before the treaty. The treaty happened before the peace.")


def agg_hop(net, subj, rel, code, rcode, concepts, seed):
    """R independent gated retrievals; majority-vote among those clearing SIM_STOP. Returns (winner|None, ok)."""
    cands = []
    for i in range(R):
        net.state = np.random.default_rng(seed + i * 17).choice([-1.0, 1.0], N)
        s = net.relax(np.arange(KEY), code[subj] * rcode[rel], steps=40)
        val = np.sign(s[KEY:KEY + VAL])
        sims = {c: float(val @ code[c]) for c in concepts}
        best = max(sims, key=sims.get)
        if sims[best] >= SIM_STOP:
            cands.append(best)
    if not cands:
        return None
    return Counter(cands).most_common(1)[0][0]


def agg_chain(net, x, rel, code, rcode, concepts, seed, max_depth=8):
    reach, seen, cur = set(), {x}, x
    for d in range(max_depth):
        nxt = agg_hop(net, cur, rel, code, rcode, concepts, seed + d * 101)
        if nxt is None or nxt in seen:
            break
        reach.add(nxt); seen.add(nxt); cur = nxt
    return reach


def query(net, kind, a, b, code, rcode, concepts, seed):
    if kind in ("isa", "causal", "bigger", "before"):
        return b in agg_chain(net, a, kind, code, rcode, concepts, seed)
    if kind == "partof":
        w = agg_hop(net, a, "partof", code, rcode, concepts, seed)
        if w is None:
            return False
        return b == w or b in agg_chain(net, w, "isa", code, rcode, concepts, seed)
    return False


BATTERY = [
    ("isa", "poodle", "animal"), ("isa", "poodle", "mammal"), ("isa", "poodle", "cat"),
    ("partof", "heart", "dog"), ("partof", "heart", "animal"), ("partof", "heart", "cat"),
    ("causal", "virus", "weakness"), ("causal", "virus", "fever"), ("causal", "fever", "virus"),
    ("bigger", "elephant", "cat"), ("bigger", "elephant", "dog"), ("bigger", "cat", "elephant"),
    ("before", "war", "peace"), ("before", "war", "treaty"), ("before", "peace", "war"),
]


def run_seed(seed):
    e = UnderstandingEngine(seed=seed); e.read(PASSAGE)
    edges = collect_edges(e)
    code, rcode, concepts = setup(edges, seed)
    net = build(edges, code, rcode, seed, True)
    ctl = build(edges, code, rcode, seed, False)

    def truth(kind, a, b):
        if kind == "isa": return e.is_a(a, b)
        if kind == "partof": return e.part_of(a, b)
        if kind == "causal": return e.causes_effect(a, b)
        return e._order_holds(kind, a, b)

    def score(n):
        return sum(query(n, k, a, b, code, rcode, concepts, seed) == truth(k, a, b)
                   for k, a, b in BATTERY) / len(BATTERY)

    a = score(net); d = score(ctl)
    inter = (query(net, "partof", "heart", "animal", code, rcode, concepts, seed)
             and not query(net, "partof", "heart", "cat", code, rcode, concepts, seed))
    return {"match": a, "ctl": d, "inter": bool(inter), "n_edges": len(edges)}


if __name__ == "__main__":
    print("=== JEP-243: robust full engine on substrate (per-hop aggregation) ===", flush=True)
    seeds = [42, 7]
    R242 = {42: 1.00, 7: 0.93}        # JEP-242 single-retrieval battery match (for the no-regression bar)
    res = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = res[s]
        print(f"  seed {s}: aggregated battery match={r['match']:.2f} (control {r['ctl']:.2f}, {r['n_edges']} edges) "
              f"interaction+leak={r['inter']}  [JEP-242 single-shot was {R242[s]:.2f}]", flush=True)

    J243a = all(res[s]['match'] == 1.00 for s in seeds)
    J243b = all(res[s]['inter'] for s in seeds)
    J243c = all(res[s]['match'] >= R242[s] for s in seeds)
    J243d = all(res[s]['ctl'] <= 0.60 for s in seeds)
    passed = J243a and J243b and J243c and J243d

    print("\n--- VERDICT ---", flush=True)
    print(f"J243a battery 1.00 both seeds      : {J243a}", flush=True)
    print(f"J243b interaction holds both seeds : {J243b}", flush=True)
    print(f"J243c no regression vs single-shot : {J243c}", flush=True)
    print(f"J243d control fails (<=0.60)       : {J243d}", flush=True)
    verdict = ("PASS - per-hop aggregation makes the full multi-relation engine robust on the substrate "
               "(closes the JEP-242 gap)") if passed else "NULL/partial"
    print(f"\nJEP-243: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP243"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): res[s] for s in seeds}, "J243a": J243a, "J243b": J243b,
         "J243c": J243c, "J243d": J243d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
