"""JEP-242 CAPSTONE — the FULL multi-relation Understanding Engine reasons through the substrate, from one passage.

read() a real multi-domain passage -> store ALL relation types (is-a, part-of, causal, comparison, temporal) in ONE
typed EnergyNet (subject (X) relation -> object) -> answer a Q&A battery across every relation type by substrate
retrieval/chaining (+ the part-of x is-a interaction), matching the symbolic engine. The substrate as a drop-in
relational backend for the whole engine. No transformer.

Pre-registered bars in docs/amendments/jep242_full_engine_on_substrate.md.
"""
import json
from pathlib import Path
import numpy as np

from world.energy import EnergyNet
from world.understanding import UnderstandingEngine
from tools.run_jep232_relation_store import KEY, VAL, N

SIM_STOP = 0.6 * KEY
RELS = ["isa", "partof", "causal", "bigger", "before"]


def collect_edges(e):
    edges = []   # (subject, relation, object)
    for c, ps in e.parents.items():
        for p in ps:
            edges.append((c, "isa", p))
    for pt, whs in getattr(e, "part_of_g", {}).items():
        for w in whs:
            edges.append((pt, "partof", w))
    for cz, eff in getattr(e, "causes", {}).items():
        for f in eff:
            edges.append((cz, "causal", f))
    for comp in ("bigger", "before"):
        for x, ys in getattr(e, "_orders", {}).get(comp, {}).items():
            for y in ys:
                edges.append((x, comp, y))
    return edges


def setup(edges, seed):
    concepts = sorted({x for s, _, o in edges for x in (s, o)})
    rng = np.random.default_rng(seed)
    code = {c: rng.choice([-1.0, 1.0], KEY) for c in concepts}
    rcode = {r: rng.choice([-1.0, 1.0], KEY) for r in RELS}
    return code, rcode, concepts


def build(edges, code, rcode, seed, train=True):
    net = EnergyNet(n_per_module=N, n_modules=1, seed=seed)
    if train:
        pats = [np.concatenate([code[s] * rcode[r], code[o]]) for s, r, o in edges]
        for _ in range(140):
            net.train_epoch(pats, cue_frac=0.5, lr=0.02, relax_steps=12)
    return net


def hop(net, subj, rel, code, rcode, concepts, seed):
    net.state = np.random.default_rng(seed).choice([-1.0, 1.0], N)
    s = net.relax(np.arange(KEY), code[subj] * rcode[rel], steps=40)
    val = np.sign(s[KEY:KEY + VAL])
    sims = {c: float(val @ code[c]) for c in concepts}
    best = max(sims, key=sims.get)
    return best, sims[best]


def chain(net, x, rel, code, rcode, concepts, seed, max_depth=8):
    reach, seen, cur = set(), {x}, x
    for d in range(max_depth):
        nxt, sim = hop(net, cur, rel, code, rcode, concepts, seed + d)
        if sim < SIM_STOP or nxt in seen:
            break
        reach.add(nxt); seen.add(nxt); cur = nxt
    return reach


def sub_query(net, kind, a, b, code, rcode, concepts, seed):
    """Answer a typed query through the substrate."""
    if kind == "isa":
        return b in chain(net, a, "isa", code, rcode, concepts, seed)
    if kind == "causal":
        return b in chain(net, a, "causal", code, rcode, concepts, seed)
    if kind in ("bigger", "before"):
        return b in chain(net, a, kind, code, rcode, concepts, seed)
    if kind == "partof":            # part-of x is-a UP interaction
        w, sim = hop(net, a, "partof", code, rcode, concepts, seed)
        if sim < SIM_STOP:
            return False
        return b == w or b in chain(net, w, "isa", code, rcode, concepts, seed)
    return False


def run_seed(seed):
    passage = ("A poodle is a dog. A dog is a mammal. A mammal is an animal. "
               "A heart is part of a dog. "
               "A virus causes a fever. A fever causes weakness. "
               "An elephant is bigger than a dog. A dog is bigger than a cat. "
               "The war happened before the treaty. The treaty happened before the peace.")
    e = UnderstandingEngine(seed=seed); e.read(passage)
    edges = collect_edges(e)
    code, rcode, concepts = setup(edges, seed)
    net = build(edges, code, rcode, seed, True)
    ctl = build(edges, code, rcode, seed, False)

    # ground-truth via the engine
    def truth(kind, a, b):
        if kind == "isa": return e.is_a(a, b)
        if kind == "partof": return e.part_of(a, b)
        if kind == "causal": return e.causes_effect(a, b)
        if kind in ("bigger", "before"): return e._order_holds(kind, a, b)
        return False

    battery = [
        ("isa", "poodle", "animal", ), ("isa", "poodle", "mammal"), ("isa", "poodle", "cat"),     # multi-hop + neg
        ("partof", "heart", "dog"), ("partof", "heart", "animal"), ("partof", "heart", "cat"),     # interaction + leak
        ("causal", "virus", "weakness"), ("causal", "virus", "fever"), ("causal", "fever", "virus"),
        ("bigger", "elephant", "cat"), ("bigger", "elephant", "dog"), ("bigger", "cat", "elephant"),
        ("before", "war", "peace"), ("before", "war", "treaty"), ("before", "peace", "war"),
    ]
    def score(n):
        ok = 0
        for kind, a, b in battery:
            ok += sub_query(n, kind, a, b, code, rcode, concepts, seed) == truth(kind, a, b)
        return ok / len(battery)

    a = score(net); d = score(ctl)
    # J242b: depth>=3 positives resolve through substrate in is-a, comparison, temporal
    deep = (sub_query(net, "isa", "poodle", "animal", code, rcode, concepts, seed)
            and sub_query(net, "bigger", "elephant", "cat", code, rcode, concepts, seed)
            and sub_query(net, "before", "war", "peace", code, rcode, concepts, seed))
    # J242c: interaction + leak
    inter = (sub_query(net, "partof", "heart", "animal", code, rcode, concepts, seed)
             and not sub_query(net, "partof", "heart", "cat", code, rcode, concepts, seed))
    return {"a": a, "d_ctl": d, "deep": bool(deep), "inter": bool(inter),
            "n_edges": len(edges), "n_q": len(battery)}


if __name__ == "__main__":
    print("=== JEP-242 CAPSTONE: full multi-relation engine through the substrate, from prose ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: battery match={r['a']:.2f} (control {r['d_ctl']:.2f}, {r['n_q']}q, {r['n_edges']} edges) "
              f"deep-multi-hop={r['deep']} interaction+leak={r['inter']}", flush=True)

    J242a = all(R[s]['a'] >= 0.90 for s in seeds)
    J242b = all(R[s]['deep'] for s in seeds)
    J242c = all(R[s]['inter'] for s in seeds)
    J242d = all(R[s]['d_ctl'] <= 0.60 for s in seeds)
    passed = J242a and J242b and J242c and J242d

    print("\n--- VERDICT ---", flush=True)
    print(f"J242a all relation types via substrate (>=.90): {J242a}", flush=True)
    print(f"J242b multi-hop in each type                  : {J242b}", flush=True)
    print(f"J242c interaction + leak guard                : {J242c}", flush=True)
    print(f"J242d above untrained control                 : {J242d}", flush=True)
    verdict = ("PASS - the FULL multi-relation Understanding Engine reasons through the substrate from real prose") \
        if passed else "NULL/partial"
    print(f"\nJEP-242: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP242"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J242a": J242a, "J242b": J242b,
         "J242c": J242c, "J242d": J242d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
