"""JEP-311 — a second transitive relation (located-in) + non-interference with is-a."""
import json, tempfile, itertools
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory

LOC = [("paris", "france"), ("france", "europe"), ("europe", "earth"),
       ("berlin", "germany"), ("germany", "europe"), ("tokyo", "japan"),
       ("japan", "asia"), ("asia", "earth"), ("cairo", "egypt"), ("egypt", "africa"), ("africa", "earth")]
ISA = [("poodle", "dog"), ("dog", "mammal"), ("mammal", "animal"), ("salmon", "fish"), ("fish", "animal")]
CALIB = [("z1", "located_in", "w1"), ("z2", "located_in", "w2"), ("z3", "located_in", "w3")]


def closure(edges):
    g = {}
    for a, b in edges:
        g.setdefault(a, set()).add(b)
    pairs = set()
    for n in g:
        seen, st = set(), list(g.get(n, []))
        while st:
            p = st.pop()
            if p in seen:
                continue
            seen.add(p); pairs.add((n, p)); st.extend(g.get(p, []))
    return pairs, g


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


def run_seed(seed):
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for a, b in LOC:
        mem.add_fact(a, "located_in", b)
    for a, b in ISA:
        mem.add_fact(a, "isa", b)
    for (c, r, p) in CALIB:
        mem.add_fact(c, r, p)
    d = tempfile.mkdtemp(); mem.save(d); mem2 = SubstrateMemory.load(d); g = gate(mem2, seed)

    loc_pairs, lg = closure(LOC)
    nodes = sorted({x for e in LOC for x in e})
    pos = sorted(loc_pairs); neg = [pr for pr in itertools.permutations(nodes, 2) if pr not in loc_pairs][:len(pos)]
    loc_acc = np.mean([climb(mem2, a, b, "located_in", g) == ((a, b) in loc_pairs) for (a, b) in pos + neg])

    isa_pairs, _ = closure(ISA)
    inodes = sorted({x for e in ISA for x in e})
    ipos = sorted(isa_pairs); ineg = [pr for pr in itertools.permutations(inodes, 2) if pr not in isa_pairs][:len(ipos)]
    isa_acc = np.mean([climb(mem2, a, b, "isa", g) == ((a, b) in isa_pairs) for (a, b) in ipos + ineg])

    mem3 = SubstrateMemory.load(d)
    persist = all(climb(mem3, a, b, "located_in", gate(mem3, seed)) == climb(mem2, a, b, "located_in", g)
                  for (a, b) in pos + neg)
    return {"loc_acc": round(float(loc_acc), 3), "isa_acc": round(float(isa_acc), 3), "persist": bool(persist),
            "demo_paris_earth": climb(mem2, "paris", "earth", "located_in", g)}


if __name__ == "__main__":
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        print(f"JEP311 seed {s}: located-in acc={R[s]['loc_acc']} is-a acc={R[s]['isa_acc']} "
              f"persists={R[s]['persist']} paris->earth={R[s]['demo_paris_earth']}", flush=True)
    J311a = all(R[s]['loc_acc'] >= 0.90 for s in seeds)
    J311b = all(R[s]['isa_acc'] >= 0.95 for s in seeds)
    J311c = all(R[s]['persist'] for s in seeds)
    passed = J311a and J311b and J311c
    print(f"JEP-311: {'PASS' if passed else 'NULL/partial'} (J311a={J311a} J311b={J311b} J311c={J311c})", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP311"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J311a": J311a, "J311b": J311b, "J311c": J311c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
