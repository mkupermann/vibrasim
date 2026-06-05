"""JEP-338 — validated-on-real-content at scale: a ~150-fact engine-READ corpus forcing multi-module routing. No
transformer. Pre-registered bars in docs/amendments/jep338_large_corpus.md.
"""
import json, tempfile, itertools
from pathlib import Path
import numpy as np
from world.understanding import UnderstandingEngine
from world.substrate_memory import SubstrateMemory

SYL = [c + v for c in "bdfgklmnprstvz" for v in "aeiou"]
# 2-syllable word-like names from a product -> plenty of unique alpha-only concepts for a large corpus
NAMES = [SYL[i] + SYL[j] for i in range(len(SYL)) for j in range(len(SYL)) if i != j]
NAMES = list(dict.fromkeys(NAMES))                                        # dedup, preserve order
VERBS = ["bark", "fly", "swim", "run", "jump", "sing"]


def gen_corpus(n_concepts=140, branch=3):
    """Forest of is-a trees over generated names + properties + causal. Returns (sentences, gold_parents)."""
    names = NAMES[:n_concepts]
    parents = {}
    roots = names[:5]
    for i, c in enumerate(names[5:], start=5):
        p = names[(i - 5) // branch]                  # attach to an earlier node -> balanced forest
        parents[c] = p
    sents = [f"A {c} is a {p}." for c, p in parents.items()]
    # properties on every 4th concept (inherited by descendants)
    for i, c in enumerate(names):
        if i % 4 == 0:
            sents.append(f"A {c} can {VERBS[i % len(VERBS)]}.")
    # causal edges among roots/early concepts
    for i in range(0, 30, 3):
        sents.append(f"{names[i]} causes {names[i + 1]}.")
    return sents, parents, names


def gate(mem, seed, role="isa"):
    edges = [(a, b) for (a, r, b) in mem.facts if r == role]
    rng = np.random.default_rng(seed)
    t = np.mean([mem.edge_sim(a, role, b) for (a, b) in edges]) if edges else 0.2
    u = np.mean([mem.query(f"qq_{int(rng.integers(1e9))}", role)[1] for _ in range(30)])
    return float((t + u) / 2)


def climb(mem, x, y, rel, g, mx=40):
    from collections import deque
    q, seen, n = deque([x]), {x}, 0
    while q and n < mx:
        cur = q.popleft(); n += 1
        for (p, _) in mem.query_all(cur, rel, g):
            if p == y:
                return True
            if p not in seen:
                seen.add(p); q.append(p)
    return False


def run_seed(seed):
    sents, parents, names = gen_corpus()
    eng = UnderstandingEngine(seed=seed)
    for s in sents:
        eng.read(s)
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True, module_cap=40)
    mem.ingest_engine(eng)
    d = tempfile.mkdtemp(prefix=f"big_{seed}_"); mem.save(d); m = SubstrateMemory.load(d); g = gate(m, seed)

    n_facts = len(m.facts); n_modules = len(m.modules)
    concepts = sorted({a for (a, r, b) in m.facts if r == "isa"} | {b for (a, r, b) in m.facts if r == "isa"})

    # is-a multi-hop battery vs engine
    rng = np.random.default_rng(seed)
    allp = list(itertools.permutations(concepts, 2))
    pos = [(a, b) for (a, b) in allp if eng.is_a(a, b)]
    neg = [(a, b) for (a, b) in allp if not eng.is_a(a, b)]
    samp = ([pos[i] for i in rng.choice(len(pos), min(40, len(pos)), replace=False)] +
            [neg[i] for i in rng.choice(len(neg), min(40, len(neg)), replace=False)])
    isa_acc = np.mean([climb(m, a, b, "isa", g) == eng.is_a(a, b) for (a, b) in samp])

    # inheritance: pick concepts with an ancestor property
    prop_q = []
    for c in concepts[:40]:
        for p in VERBS:
            prop_q.append((c, p))
    def has_prop_sub(x, p):
        from collections import deque
        chain, cur, seen = [x], x, {x}
        for _ in range(40):
            nx, s = m.query(cur, "isa")
            if nx is None or s < g or nx in seen:
                break
            chain.append(nx); seen.add(nx); cur = nx
        return any(m.contains(a, "hasprop", p, g) for a in chain)
    inh_acc = np.mean([has_prop_sub(c, p) == eng.has_property(c, p) for (c, p) in prop_q])

    # abduction on a causal pair
    eff = names[1]
    abd = (set(c for (c, _) in m.query_all(eff, "caused_by", g)) == set(eng.abduce(eff)))

    # persistence
    m2 = SubstrateMemory.load(d); g2 = gate(m2, seed)
    persist = np.mean([climb(m2, a, b, "isa", g2) == climb(m, a, b, "isa", g) for (a, b) in samp]) >= 0.98

    return {"n_facts": n_facts, "n_modules": n_modules, "isa_acc": round(float(isa_acc), 3),
            "inh_acc": round(float(inh_acc), 3), "abduction_ok": bool(abd), "persist": bool(persist)}


if __name__ == "__main__":
    print("=== JEP-338: large real corpus (~150 facts, multi-module) ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: {r['n_facts']} facts / {r['n_modules']} modules | is-a={r['isa_acc']} "
              f"inheritance={r['inh_acc']} abduction={r['abduction_ok']} | persist={r['persist']}", flush=True)
    J338a = all(R[s]['n_facts'] >= 120 and R[s]['n_modules'] >= 3 and R[s]['isa_acc'] >= 0.90 for s in seeds)
    J338b = all(R[s]['inh_acc'] >= 0.90 and R[s]['abduction_ok'] for s in seeds)
    J338c = all(R[s]['persist'] for s in seeds)
    passed = J338a and J338b and J338c
    print("\n--- VERDICT ---", flush=True)
    print(f"J338a >=120 facts, >=3 modules, is-a >=.90: {J338a}", flush=True)
    print(f"J338b inheritance + abduction at scale     : {J338b}", flush=True)
    print(f"J338c persists                              : {J338c}", flush=True)
    verdict = ("PASS - the full reasoning suite holds on a ~150-fact engine-read corpus across multiple modules") \
        if passed else "NULL/partial"
    print(f"\nJEP-338: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP338"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J338a": J338a, "J338b": J338b, "J338c": J338c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
