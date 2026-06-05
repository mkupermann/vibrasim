"""JEP-329 — temporal/event reasoning over the durable store (before/after, what happened first). Bridges the
engine's before-DAG. No transformer. Pre-registered bars in docs/amendments/jep329_temporal_reasoning.md.
"""
import json, tempfile, itertools
from pathlib import Path
import numpy as np
from world.understanding import UnderstandingEngine
from world.substrate_memory import SubstrateMemory

CORPUS = ("The protest happened before the election. The election happened before the war. "
          "The war happened before the treaty. The treaty happened before the peace. "
          "The drought happened before the famine. The famine happened before the migration.")
CALIB = [("z1", "before", "w1"), ("z2", "before", "w2"), ("z3", "before", "w3")]


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
    edges = [(a, b) for (a, r, b) in mem.facts if r == "before"]
    rng = np.random.default_rng(seed)
    t = np.mean([mem.edge_sim(a, "before", b) for (a, b) in edges]) if edges else 0.2
    u = np.mean([mem.query(f"n_{int(rng.integers(1e9))}", "before")[1] for _ in range(30)])
    return float((t + u) / 2)


def happened_before(mem, x, y, g, mx=30):
    from collections import deque
    q, seen, n = deque([x]), {x}, 0
    while q and n < mx:
        cur = q.popleft(); n += 1
        for (p, _) in mem.query_all(cur, "before", g):
            if p == y:
                return True
            if p not in seen:
                seen.add(p); q.append(p)
    return False


def what_first(mem, events, g):
    firsts = [e for e in events if not any(happened_before(mem, d, e, g) for d in events if d != e)]
    return firsts


def run_seed(seed):
    eng = UnderstandingEngine(seed=seed); eng.read(CORPUS)
    before = {a: set(b) for a, b in dict(eng._orders.get("before", {})).items()}
    edges = [(a, b) for a, bs in before.items() for b in bs]
    events = sorted({x for e in edges for x in e})

    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for a, b in edges:
        mem.add_fact(a, "before", b)
    for (c, r, p) in CALIB:
        mem.add_fact(c, r, p)
    d = tempfile.mkdtemp(prefix=f"tmp_{seed}_"); mem.save(d); m = SubstrateMemory.load(d); g = gate(m, seed)

    cl = closure(edges)
    pos = sorted(cl)
    neg = [pr for pr in itertools.permutations(events, 2) if pr not in cl][:len(pos)]
    acc = np.mean([happened_before(m, a, b, g) == ((a, b) in cl) for (a, b) in pos + neg])

    firsts = set(what_first(m, events, g))
    # ground-truth firsts: events with no predecessor in closure
    gt_first = {e for e in events if not any((d, e) in cl for d in events)}
    first_ok = (firsts == gt_first)

    m3 = SubstrateMemory.load(d)
    persist = (set(what_first(m3, events, gate(m3, seed))) == firsts)
    return {"before_acc": round(float(acc), 3), "firsts": sorted(firsts), "gt_first": sorted(gt_first),
            "first_ok": bool(first_ok), "persist": bool(persist),
            "demo": {"protest_before_peace": happened_before(m, "protest", "peace", g),
                     "peace_before_protest": happened_before(m, "peace", "protest", g)}}


if __name__ == "__main__":
    print("=== JEP-329: temporal/event reasoning over the durable store ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: happened-before acc={r['before_acc']} | firsts={r['firsts']} (gt {r['gt_first']}) "
              f"first_ok={r['first_ok']} persists={r['persist']} | demo={r['demo']}", flush=True)
    J329a = all(R[s]['before_acc'] >= 0.90 for s in seeds)
    J329b = all(R[s]['first_ok'] for s in seeds)
    J329c = all(R[s]['persist'] for s in seeds)
    passed = J329a and J329b and J329c
    print("\n--- VERDICT ---", flush=True)
    print(f"J329a happened-before transitive+asymmetric (>=.90): {J329a}", flush=True)
    print(f"J329b what-happened-first correct                  : {J329b}", flush=True)
    print(f"J329c persists                                      : {J329c}", flush=True)
    verdict = ("PASS - the durable store answers temporal ordering (before/after, transitive + asymmetric) and "
               "'what happened first', bridged from the engine") if passed else "NULL/partial"
    print(f"\nJEP-329: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP329"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J329a": J329a, "J329b": J329b, "J329c": J329c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
