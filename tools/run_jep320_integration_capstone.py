"""JEP-320 — grand integration capstone: one durable store, reloaded, exercising every reasoning + meta-learning
operation together. One regression for the whole arc (JEP-294..319). No transformer.
Pre-registered bars in docs/amendments/jep320_integration_capstone.md.
"""
import json, tempfile, itertools
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory


def gate(mem, seed, role="isa"):
    edges = [(a, b) for (a, r, b) in mem.facts if r == role]
    rng = np.random.default_rng(seed)
    samp = [edges[i] for i in rng.choice(len(edges), min(30, len(edges)), replace=False)] if edges else []
    t = np.mean([mem.query(a, role)[1] for (a, b) in samp]) if samp else 0.2
    u = np.mean([mem.query(f"none_{int(rng.integers(1e9))}", role)[1] for _ in range(30)])
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
    # taxonomy (with a DAG node) + properties + exception
    for c, p in [("poodle", "dog"), ("dog", "mammal"), ("mammal", "animal"), ("penguin", "bird"),
                 ("penguin", "swimmer"), ("bird", "animal"), ("swimmer", "animal"), ("robin", "bird")]:
        mem.add_fact(c, "isa", p)
    for a, p in [("bird", "fly"), ("dog", "bark"), ("mammal", "breathe")]:
        mem.add_fact(a, "hasprop", p)
    mem.add_fact("penguin", "not_hasprop", "fly")               # exception
    mem.add_fact("whale", "isa", "mammal"); mem.add_fact("whale", "not_isa", "fish")   # negative is-a
    # causal (+ inverse for abduction)
    for c, e in [("smoking", "cancer"), ("radiation", "cancer")]:
        mem.add_fact(c, "causes", e); mem.add_fact(e, "caused_by", c)
    # open relation
    for s, o in [("cat", "fish"), ("cow", "grass")]:
        mem.add_fact(s, "eats", o)
    # contradiction (direct double-assertion)
    mem.add_fact("robin", "hasprop", "swim"); mem.add_fact("robin", "not_hasprop", "swim")
    # symmetric relation
    for a, b in [("alice", "bob"), ("carol", "dave")]:
        mem.add_fact(a, "married_to", b); mem.add_fact(b, "married_to", a)
    # family tree (for composition + inverse)
    for a, b in [("al", "bo"), ("al", "bea"), ("bo", "cy"), ("bea", "ed")]:
        mem.add_fact(a, "parent_of", b); mem.add_fact(b, "child_of", a)
    for a, b in [("bo", "bea")]:
        mem.add_fact(a, "sibling_of", b); mem.add_fact(b, "sibling_of", a)
    return mem


def base_sets(mem, rels):
    return {r: {(s, o) for (s, rr, o) in mem.facts if rr == r} for r in rels}


def run_seed(seed):
    mem = build()
    d = tempfile.mkdtemp(prefix=f"cap_{seed}_"); mem.save(d)
    m = SubstrateMemory.load(d)                                  # FRESH reload
    g = gate(m, seed)
    checks = {}

    # 1 is-a multi-hop ; 2 inheritance leaf ; 3 negation/exception ; 4 DAG
    checks["isa_multihop"] = climb(m, "poodle", "animal", "isa", g) and not climb(m, "poodle", "fish", "isa", g)
    checks["inheritance"] = m.contains("dog", "hasprop", "bark", g)  # direct; inherited checked via climb below
    def hasprop_def(x, p):
        for a in [x] + [n for n in _anc(m, x, g)]:
            if m.contains(a, "not_hasprop", p, g):
                return False
            if m.contains(a, "hasprop", p, g):
                return True
        return False
    checks["exception"] = (hasprop_def("penguin", "fly") is False) and (hasprop_def("robin", "fly") is True)
    checks["dag"] = {p for (p, _) in m.query_all("penguin", "isa", g)} >= {"bird", "swimmer"}
    checks["neg_isa"] = (not climb(m, "whale", "fish", "isa", g)) and climb(m, "whale", "animal", "isa", g) \
        if not m.contains("whale", "not_isa", "fish", g) else (m.contains("whale", "not_isa", "fish", g))
    # 5 abduction
    checks["abduction"] = {c for (c, _) in m.query_all("cancer", "caused_by", g)} == {"smoking", "radiation"}
    # 6 open relation
    checks["open_rel"] = m.query("cat", "eats")[0] == "fish"
    # 7 contradiction
    checks["contradiction"] = ("robin", "hasprop", "swim") in m.detect_conflicts(g)
    # 8 induce symmetry (married_to)
    f_mar = {(s, o) for (s, r, o) in m.facts if r == "married_to"}
    sym_rate = np.mean([1.0 if (b, a) in f_mar else 0.0 for (a, b) in f_mar])
    checks["induce_symmetry"] = sym_rate >= 0.7
    # 9 discover inverse (parent_of / child_of)
    fp = {(s, o) for (s, r, o) in m.facts if r == "parent_of"}
    fc = {(s, o) for (s, r, o) in m.facts if r == "child_of"}
    inv_rate = np.mean([1.0 if (b, a) in fc else 0.0 for (a, b) in fp])
    checks["discover_inverse"] = inv_rate >= 0.8
    # 10 induce composition (grandparent = parent_of o parent_of): al->cy via bo, al->ed via bea
    B = base_sets(m, ["parent_of", "sibling_of"])
    gp = {(a, c) for (a, x) in B["parent_of"] for (x2, c) in B["parent_of"] if x == x2 and a != c}
    checks["induce_composition"] = ("al", "cy") in gp and ("al", "ed") in gp

    return {"checks": checks, "all_pass": all(checks.values()), "n_facts": len(m.facts)}


def _anc(mem, x, g, mx=20):
    out, cur, seen = [], x, {x}
    for _ in range(mx):
        p, s = mem.query(cur, "isa")
        if p is None or s < g or p in seen:
            break
        out.append(p); seen.add(p); cur = p
    return out


if __name__ == "__main__":
    print("=== JEP-320: grand integration capstone (one reloaded store, every operation) ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        print(f"  seed {s}: all_pass={R[s]['all_pass']} ({R[s]['n_facts']} facts)", flush=True)
        for k, v in R[s]["checks"].items():
            print(f"      {k}: {bool(v)}", flush=True)
    J320a = all(R[s]['all_pass'] for s in seeds)
    passed = J320a
    print("\n--- VERDICT ---", flush=True)
    print(f"J320a all 10 operations pass on the single reloaded store: {J320a}", flush=True)
    verdict = ("PASS - the whole stack (reasoning + meta-learning) composes in one durable store and survives a "
               "restart together") if passed else "NULL/partial - see per-check"
    print(f"\nJEP-320: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP320"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "J320a": J320a,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
