"""JEP-303 — DAG taxonomies: set-valued parent retrieval + DAG BFS is-a over the persistent store, matching the
engine. Closes the pattern doc's last named limitation (single-best-parent climb). No transformer.

Pre-registered bars in docs/amendments/jep303_dag_taxonomies.md.
"""
import json, tempfile, itertools, subprocess, sys, os
from pathlib import Path
import numpy as np
from world.understanding import UnderstandingEngine
from world.substrate_memory import SubstrateMemory

# a taxonomy with several MULTI-PARENT (DAG) nodes
CORPUS = (
    "A penguin is a bird. A penguin is a swimmer. A bird is an animal. A swimmer is an animal. "
    "A platypus is a mammal. A platypus is an egglayer. A mammal is an animal. An egglayer is a vertebrate. "
    "A vertebrate is an animal. A bat is a mammal. A bat is a flyer. A flyer is an animal. "
    "A robin is a bird. A salmon is a swimmer."
)
CALIB = [("c1", "isa", "k1"), ("c2", "isa", "k2"), ("c3", "isa", "k3")]


def gate_threshold(mem, seed):
    taught = np.mean([mem.query(c, "isa")[1] for (c, _, _) in CALIB])
    rng = np.random.default_rng(seed + 321)
    untaught = np.mean([mem.query(f"none_{int(rng.integers(1e9))}", "isa")[1] for _ in range(32)])
    return float((taught + untaught) / 2.0)


def dag_is_a(mem, x, y, gate, max_nodes=60):
    """BFS over ALL parents (set-valued) — handles multi-parent DAGs."""
    from collections import deque
    q, seen = deque([x]), {x}
    n = 0
    while q and n < max_nodes:
        cur = q.popleft(); n += 1
        for (p, _) in mem.query_all(cur, "isa", gate):
            if p == y:
                return True
            if p not in seen:
                seen.add(p); q.append(p)
    return False


def build(eng, seed):
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for c, ps in eng.parents.items():
        for p in ps:
            mem.add_fact(c, "isa", p)
    for (c, r, p) in CALIB:
        mem.add_fact(c, r, p)
    return mem


def run_seed(seed):
    eng = UnderstandingEngine(seed=seed)
    eng.read(CORPUS)
    parents = {k: set(v) for k, v in eng.parents.items()}
    nodes = sorted(set(parents) | {p for v in parents.values() for p in v})

    mem = build(eng, seed)
    d = tempfile.mkdtemp(prefix=f"dag_{seed}_")
    mem.save(d)
    mem2 = SubstrateMemory.load(d)
    gate = gate_threshold(mem2, seed)

    # J303a: exact direct-parent SET recovery per node
    exact = []
    for c, ps in parents.items():
        got = {p for (p, _) in mem2.query_all(c, "isa", gate)}
        # restrict to the real value vocabulary (ignore calib)
        got = {g for g in got if g in nodes}
        exact.append(1.0 if got == ps else 0.0)
    set_acc = float(np.mean(exact))
    multi = {c: ps for c, ps in parents.items() if len(ps) > 1}

    # J303b: DAG multi-hop is-a vs engine, balanced
    rng = np.random.default_rng(seed)
    allpairs = list(itertools.permutations(nodes, 2))
    pos = [(a, b) for (a, b) in allpairs if eng.is_a(a, b)]
    neg = [(a, b) for (a, b) in allpairs if not eng.is_a(a, b)]
    k = min(len(pos), len(neg))
    sel = pos[:k] + [neg[i] for i in rng.choice(len(neg), k, replace=False)]
    isa_acc = float(np.mean([dag_is_a(mem2, a, b, gate) == eng.is_a(a, b) for (a, b) in sel]))

    # J303c: persists
    mem3 = SubstrateMemory.load(d); gate3 = gate_threshold(mem3, seed)
    persist = all(dag_is_a(mem3, a, b, gate3) == dag_is_a(mem2, a, b, gate) for (a, b) in sel)

    demo = {"penguin_parents": sorted(p for (p, _) in mem2.query_all("penguin", "isa", gate) if p in nodes),
            "penguin_is_animal": dag_is_a(mem2, "penguin", "animal", gate),
            "platypus_is_animal": dag_is_a(mem2, "platypus", "animal", gate)}
    return {"set_acc": round(set_acc, 3), "isa_acc": round(isa_acc, 3), "persist_ok": bool(persist),
            "n_multi": len(multi), "demo": demo}


def regression(repo):
    r298 = subprocess.run([sys.executable, "tools/run_jep298_directed_binding.py"], capture_output=True,
                          text=True, env={**os.environ, "PYTHONPATH": repo})
    r301 = subprocess.run([sys.executable, "tools/run_jep301_substrate_inheritance.py"], capture_output=True,
                          text=True, env={**os.environ, "PYTHONPATH": repo})
    return ("JEP-298: PASS" in r298.stdout), ("JEP-301: PASS" in r301.stdout)


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-303: DAG taxonomies (set-valued parents) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: parent-set acc={r['set_acc']} ({r['n_multi']} multi-parent nodes) | DAG is-a acc="
              f"{r['isa_acc']} | persists={r['persist_ok']} | demo={r['demo']}", flush=True)
    reg298, reg301 = regression(repo)
    print(f"  regression: JEP-298={'PASS' if reg298 else 'FAIL'} JEP-301={'PASS' if reg301 else 'FAIL'}", flush=True)

    J303a = all(R[s]['set_acc'] >= 0.95 for s in seeds)
    J303b = all(R[s]['isa_acc'] >= 0.90 for s in seeds)
    J303c = all(R[s]['persist_ok'] for s in seeds)
    passed = J303a and J303b and J303c and reg298 and reg301
    print("\n--- VERDICT ---", flush=True)
    print(f"J303a exact direct-parent SET recovery (>=.95): {J303a}", flush=True)
    print(f"J303b DAG multi-hop is-a matches engine (>=.90): {J303b}", flush=True)
    print(f"J303c persists across reload                   : {J303c}", flush=True)
    print(f"no-regression: JEP-298 & JEP-301 still PASS     : {reg298 and reg301}", flush=True)
    verdict = ("PASS - set-valued retrieval + DAG BFS let the substrate handle multi-parent taxonomies, matching "
               "the engine over the persistent store") if passed else "NULL/partial"
    print(f"\nJEP-303: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP303"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "reg298": reg298,
                                                  "reg301": reg301, "J303a": J303a, "J303b": J303b, "J303c": J303c,
                                                  "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
