"""JEP-330 — numeric attribute reasoning with inheritance (how many legs? more than?). No transformer.
Pre-registered bars in docs/amendments/jep330_numeric_attributes.md.
"""
import json, tempfile
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory

ISA = [("poodle", "dog"), ("dog", "mammal"), ("mammal", "animal"),
       ("sparrow", "bird"), ("bird", "animal"), ("tripod_dog", "dog"), ("spider", "arachnid")]
LEGS = [("dog", "4"), ("bird", "2"), ("arachnid", "8"), ("tripod_dog", "3")]   # tripod overrides dog's 4
CALIB = [("z1", "isa", "w1"), ("z2", "isa", "w2"), ("z3", "isa", "w3")]


def gate(mem, seed, role="isa"):
    edges = [(a, b) for (a, r, b) in mem.facts if r == role]
    rng = np.random.default_rng(seed)
    t = np.mean([mem.edge_sim(a, role, b) for (a, b) in edges]) if edges else 0.2
    u = np.mean([mem.query(f"n_{int(rng.integers(1e9))}", role)[1] for _ in range(30)])
    return float((t + u) / 2)


def ancestors(mem, x, g, mx=20):
    out, cur, seen = [x], x, {x}
    for _ in range(mx):
        p, s = mem.query(cur, "isa")
        if p is None or s < g or p in seen:
            break
        out.append(p); seen.add(p); cur = p
    return out


def how_many(mem, x, g):
    for a in ancestors(mem, x, g):              # most specific first -> first value wins (override)
        v, s = mem.query(a, "has_legs")
        if v is not None and s >= g:
            return int(v)
    return None


def build():
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for a, b in ISA:
        mem.add_fact(a, "isa", b)
    for a, n in LEGS:
        mem.add_fact(a, "has_legs", n)
    for (c, r, p) in CALIB:
        mem.add_fact(c, r, p)
    return mem


def run_seed(seed):
    mem = build(); d = tempfile.mkdtemp(prefix=f"num_{seed}_"); mem.save(d)
    m = SubstrateMemory.load(d); g = gate(m, seed)

    gt = {"poodle": 4, "dog": 4, "sparrow": 2, "bird": 2, "spider": 8, "tripod_dog": 3}
    qm = {x: how_many(m, x, g) for x in gt}
    hm_acc = np.mean([qm[x] == gt[x] for x in gt])

    comps = [("dog", "bird", 1), ("bird", "spider", -1), ("poodle", "tripod_dog", 1), ("sparrow", "dog", -1)]
    def cmp(x, y):
        a, b = how_many(m, x, g), how_many(m, y, g)
        return 0 if a == b else (1 if a > b else -1)
    cmp_acc = np.mean([cmp(x, y) == sign for (x, y, sign) in comps])

    m3 = SubstrateMemory.load(d); g3 = gate(m3, seed)
    persist = all(how_many(m3, x, g3) == qm[x] for x in gt)
    return {"how_many_acc": round(float(hm_acc), 3), "compare_acc": round(float(cmp_acc), 3),
            "persist": bool(persist), "demo": {x: qm[x] for x in ["poodle", "sparrow", "tripod_dog", "spider"]}}


if __name__ == "__main__":
    print("=== JEP-330: numeric attribute reasoning with inheritance ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: how-many acc={r['how_many_acc']} | compare acc={r['compare_acc']} | "
              f"persists={r['persist']} | demo={r['demo']}", flush=True)
    J330a = all(R[s]['how_many_acc'] >= 0.95 for s in seeds)
    J330b = all(R[s]['compare_acc'] >= 0.95 for s in seeds)
    J330c = all(R[s]['persist'] for s in seeds)
    passed = J330a and J330b and J330c
    print("\n--- VERDICT ---", flush=True)
    print(f"J330a inherited quantity incl override (>=.95): {J330a}", flush=True)
    print(f"J330b numeric comparison (>=.95)              : {J330b}", flush=True)
    print(f"J330c persists                                 : {J330c}", flush=True)
    verdict = ("PASS - the durable store answers numeric attribute questions with is-a inheritance + override, and "
               "numeric comparison") if passed else "NULL/partial"
    print(f"\nJEP-330: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP330"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J330a": J330a, "J330b": J330b, "J330c": J330c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
