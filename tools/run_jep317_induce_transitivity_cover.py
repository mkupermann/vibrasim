"""JEP-317 — induce transitivity from a COVER-only store via a few labeled examples, then infer over the cover with
the climb. Closes the JEP-316 scope gap. No transformer.
Pre-registered bars in docs/amendments/jep317_induce_transitivity_cover.md.
"""
import json, tempfile, itertools
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory

# transitive relations stored as COVER (chain only, NOT closure)
TRANS_COVER = {
    "ancestor_of": [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e")],
    "located_in": [("paris", "france"), ("france", "europe"), ("europe", "earth")],
    "bigger_than": [("elephant", "horse"), ("horse", "dog"), ("dog", "cat"), ("cat", "mouse")],
}
NON_TRANS = {
    "eats": [("cat", "fish"), ("fish", "algae"), ("cow", "grass")],     # cat eats fish, fish eats algae, NOT cat eats algae
    "likes": [("amy", "ben"), ("ben", "cam"), ("cam", "dan")],
    "parent_of": [("p1", "p2"), ("p2", "p3"), ("p3", "p4")],            # parent_of is NOT transitive (that's ancestor)
}
CALIB = [("z1", "located_in", "w1"), ("z2", "located_in", "w2"), ("z3", "located_in", "w3")]


def closure(edges):
    g = {}
    for a, b in edges:
        g.setdefault(a, set()).add(b)
    pairs = set()
    for n in list(g):
        seen, st = set(), list(g.get(n, []))
        while st:
            p = st.pop()
            if p in seen:
                continue
            seen.add(p); pairs.add((n, p)); st.extend(g.get(p, []))
    return pairs


def gate(mem, seed):
    t = np.mean([mem.query(c, "located_in")[1] for (c, _, _) in CALIB])
    rng = np.random.default_rng(seed + 321)
    u = np.mean([mem.query(f"n_{int(rng.integers(1e9))}", "located_in")[1] for _ in range(32)])
    return float((t + u) / 2)


def climb(mem, x, y, rel, g, mx=20):
    cur, seen = x, {x}
    for _ in range(mx):
        p, s = mem.query(cur, rel)
        if p is None or s < g or p in seen:
            return False
        if p == y:
            return True
        seen.add(p); cur = p
    return False


def build():
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for rel, ps in {**TRANS_COVER, **NON_TRANS}.items():
        for (a, b) in ps:
            mem.add_fact(a, rel, b)
    for (c, r, p) in CALIB:
        mem.add_fact(c, r, p)
    return mem


def run_seed(seed):
    mem = build()
    d = tempfile.mkdtemp(prefix=f"trc_{seed}_"); mem.save(d); mem2 = SubstrateMemory.load(d); g = gate(mem2, seed)

    GT_trans = {r: True for r in TRANS_COVER}; GT_trans.update({r: False for r in NON_TRANS})
    cover = {**TRANS_COVER, **NON_TRANS}
    # TRUE extension: transitive relation -> closure of cover; non-transitive -> direct edges ONLY (composed pairs
    # are FALSE). This is the fix: closure() is not the ground truth for a non-transitive relation.
    true_ext = {rel: (closure(ps) if GT_trans[rel] else set(ps)) for rel, ps in cover.items()}

    # K=3 labeled composed-pair (2-hop) examples per relation; label from the TRUE extension.
    flags = {}; labeled_used = {}
    for rel, ps in cover.items():
        twohop = sorted({(a, c) for (a, b) in ps for (b2, c) in ps if b == b2 and a != c})
        examples = [(pr, pr in true_ext[rel]) for pr in twohop[:3]]
        labeled_used[rel] = examples
        rate = np.mean([1.0 if lab else 0.0 for (_, lab) in examples]) if examples else 0.0
        flags[rel] = bool(rate >= 0.7)                  # transitive iff its composed pairs hold

    cls_acc = np.mean([flags[r] == GT_trans[r] for r in cover])

    # J317b: held-out composed queries (exclude labeled) answered by climb-if-flagged-else-direct, vs TRUE extension
    held_ok = []
    for rel, ps in cover.items():
        direct = set(ps)
        labeled_pairs = {pr for (pr, _) in labeled_used[rel]}
        nodes = sorted({x for e in ps for x in e})
        allpairs = [pr for pr in itertools.permutations(nodes, 2) if pr not in direct and pr not in labeled_pairs]
        for (a, b) in allpairs:
            pred = climb(mem2, a, b, rel, g) if flags[rel] else ((a, b) in direct)
            held_ok.append(pred == ((a, b) in true_ext[rel]))
    ans_acc = np.mean(held_ok) if held_ok else 1.0

    mem3 = SubstrateMemory.load(d)
    persist = all((climb(mem3, "a", "e", "ancestor_of", gate(mem3, seed)) == climb(mem2, "a", "e", "ancestor_of", g))
                  for _ in [0])
    return {"cls_acc": round(float(cls_acc), 3), "ans_acc": round(float(ans_acc), 3), "persist": bool(persist),
            "flags": flags, "demo_a_e": climb(mem2, "a", "e", "ancestor_of", g)}


if __name__ == "__main__":
    print("=== JEP-317: induce transitivity from a COVER + infer with the climb ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        print(f"  seed {s}: flag-classify acc={R[s]['cls_acc']} | held-out inference acc={R[s]['ans_acc']} | "
              f"persists={R[s]['persist']} | ancestor a->e (4-hop cover)={R[s]['demo_a_e']}", flush=True)
        print(f"           flags={R[s]['flags']}", flush=True)
    J317a = all(R[s]['cls_acc'] >= 0.90 for s in seeds)
    J317b = all(R[s]['ans_acc'] >= 0.90 for s in seeds)
    J317c = all(R[s]['persist'] for s in seeds)
    passed = J317a and J317b and J317c
    print("\n--- VERDICT ---", flush=True)
    print(f"J317a induce transitive flag from 3 examples (>=.90): {J317a}", flush=True)
    print(f"J317b held-out inference over the COVER (>=.90)      : {J317b}", flush=True)
    print(f"J317c persists                                       : {J317c}", flush=True)
    verdict = ("PASS - induces transitivity from a few labeled examples on a cover-only store, then the climb does "
               "genuine multi-hop inference (closes the JEP-316 gap)") if passed else "NULL/partial"
    print(f"\nJEP-317: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP317"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J317a": J317a, "J317b": J317b, "J317c": J317c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
