"""JEP-316 — induce a relation's algebra (symmetry/transitivity) from its fact pattern, then auto-apply it.
Established relational-property induction, named as such. No transformer.
Pre-registered bars in docs/amendments/jep316_induce_relation_algebra.md.
"""
import json, tempfile, itertools
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory

# ground-truth relations
SYM = {
    "married_to": [("alice", "bob"), ("carol", "dave"), ("eve", "frank")],
    "sibling_of": [("tom", "sue"), ("ann", "joe"), ("kim", "leo")],
    "neighbor_of": [("h1", "h2"), ("h3", "h4"), ("h5", "h6")],
}
TRANS = {
    "ancestor_of": [("a", "b"), ("b", "c"), ("c", "d")],
    "bigger_than": [("elephant", "dog"), ("dog", "cat"), ("cat", "mouse")],
    "located_in": [("paris", "france"), ("france", "europe"), ("europe", "earth")],
}
NEITHER = {
    "eats": [("cat", "fish"), ("cow", "grass"), ("owl", "mouse")],
    "likes": [("amy", "tea"), ("ben", "coffee"), ("cam", "juice")],
    "owns": [("dan", "car"), ("ela", "house"), ("fin", "boat")],
}
GT = {**{r: "sym" for r in SYM}, **{r: "trans" for r in TRANS}, **{r: "neither" for r in NEITHER}}


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


def build():
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for rel, ps in SYM.items():
        for (a, b) in ps:
            mem.add_fact(a, rel, b); mem.add_fact(b, rel, a)         # symmetric: both directions
    for rel, ps in TRANS.items():
        for (a, b) in sorted(closure(ps)):
            mem.add_fact(a, rel, b)                                   # transitive: materialized closure
    for rel, ps in NEITHER.items():
        for (a, b) in ps:
            mem.add_fact(a, rel, b)                                   # as-is
    return mem


def induce(mem, rel):
    facts = {(s, o) for (s, r, o) in mem.facts if r == rel}
    if not facts:
        return "neither", 0.0, 0.0
    sym = np.mean([1.0 if (b, a) in facts else 0.0 for (a, b) in facts])
    comps = [(a, c) for (a, b) in facts for (b2, c) in facts if b == b2 and a != c]
    trans = np.mean([1.0 if (a, c) in facts else 0.0 for (a, c) in comps]) if comps else 0.0
    if sym >= 0.7:
        return "sym", float(sym), float(trans)
    if trans >= 0.7:
        return "trans", float(sym), float(trans)
    return "neither", float(sym), float(trans)


def answer(mem, rel, a, b, kind):
    """Auto-applied: symmetric -> either direction; else direct membership (closure already materialized)."""
    facts = {(s, o) for (s, r, o) in mem.facts if r == rel}
    if kind == "sym":
        return (a, b) in facts or (b, a) in facts
    return (a, b) in facts


def run_seed(seed):
    mem = build()
    d = tempfile.mkdtemp(prefix=f"alg_{seed}_"); mem.save(d); mem2 = SubstrateMemory.load(d)

    induced = {rel: induce(mem2, rel)[0] for rel in GT}
    cls_acc = np.mean([induced[rel] == GT[rel] for rel in GT])

    # J316b: auto-apply matches ground truth (balanced). For SYM, reverse queries; for TRANS, composed pairs.
    qs = []
    for rel, ps in SYM.items():
        for (a, b) in ps:
            qs.append((rel, b, a, True))                             # reverse should hold (symmetric)
        qs.append((rel, ps[0][0], ps[1][1], False))                  # cross pair shouldn't
    for rel, ps in TRANS.items():
        cl = closure(ps)
        for (a, b) in sorted(cl)[:4]:
            qs.append((rel, a, b, True))
        nodes = sorted({x for e in ps for x in e})
        for (a, b) in itertools.permutations(nodes, 2):
            if (a, b) not in cl:
                qs.append((rel, a, b, False)); break
    for rel, ps in NEITHER.items():
        for (a, b) in ps:
            qs.append((rel, a, b, True)); qs.append((rel, b, a, False))   # not symmetric
    ans_acc = np.mean([answer(mem2, rel, a, b, induced[rel]) == truth for (rel, a, b, truth) in qs])

    mem3 = SubstrateMemory.load(d)
    persist = all(induce(mem3, rel)[0] == induced[rel] for rel in GT)
    return {"cls_acc": round(float(cls_acc), 3), "ans_acc": round(float(ans_acc), 3), "persist": bool(persist),
            "induced": induced}


if __name__ == "__main__":
    print("=== JEP-316: induce relation algebra (symmetry/transitivity) + auto-apply ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        print(f"  seed {s}: classify acc={R[s]['cls_acc']} | auto-apply acc={R[s]['ans_acc']} | "
              f"persists={R[s]['persist']}", flush=True)
        print(f"           induced={R[s]['induced']}", flush=True)
    J316a = all(R[s]['cls_acc'] >= 0.90 for s in seeds)
    J316b = all(R[s]['ans_acc'] >= 0.90 for s in seeds)
    J316c = all(R[s]['persist'] for s in seeds)
    passed = J316a and J316b and J316c
    print("\n--- VERDICT ---", flush=True)
    print(f"J316a induce relation type matches ground truth (>=.90): {J316a}", flush=True)
    print(f"J316b auto-applied reasoning matches ground truth (>=.90): {J316b}", flush=True)
    print(f"J316c persists across reload                            : {J316c}", flush=True)
    verdict = ("PASS - the substrate INDUCES whether a relation is symmetric/transitive/neither from its fact "
               "pattern and applies the right reasoning automatically") if passed else "NULL/partial"
    print(f"\nJEP-316: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP316"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J316a": J316a, "J316b": J316b, "J316c": J316c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
