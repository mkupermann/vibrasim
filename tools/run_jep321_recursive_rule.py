"""JEP-321 — induce a RECURSIVE rule: ancestor = transitive closure of parent; apply by climbing the base. No
transformer. Pre-registered bars in docs/amendments/jep321_recursive_rule.md.
"""
import json, tempfile, itertools
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory

# a deeper family tree so ancestor has >=4-hop pairs
PARENT = [("g0", "g1"), ("g1", "g2"), ("g2", "g3"), ("g3", "g4"), ("g4", "g5"),     # a 5-deep line
          ("g0", "h1"), ("h1", "h2"), ("h2", "h3"),                                  # a side branch
          ("g1", "k2"), ("k2", "k3")]
SIBS = [("g1", "h1"), ("g2", "k2")]                                                  # distractor base (symmetric)
CALIB = [("z1", "parent_of", "w1"), ("z2", "parent_of", "w2"), ("z3", "parent_of", "w3")]


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
    t = np.mean([mem.query(c, "parent_of")[1] for (c, _, _) in CALIB])
    rng = np.random.default_rng(seed + 321)
    u = np.mean([mem.query(f"n_{int(rng.integers(1e9))}", "parent_of")[1] for _ in range(32)])
    return float((t + u) / 2)


def climb(mem, x, y, rel, g, mx=60):
    """BFS over ALL successors (query_all) -- a branching tree needs set-valued retrieval, not a single path."""
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


def build():
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for a, b in PARENT:
        mem.add_fact(a, "parent_of", b)
    for a, b in SIBS:
        mem.add_fact(a, "sibling_of", b); mem.add_fact(b, "sibling_of", a)
    for (c, r, p) in CALIB:
        mem.add_fact(c, r, p)
    return mem


def induce_base(mem, examples, bases, g):
    """Return the base relation whose closure (gated climb) covers the examples (>=0.8), else None."""
    best, bestsc = None, 0.0
    for B in bases:
        sc = np.mean([1.0 if climb(mem, a, c, B, g) else 0.0 for (a, c) in examples]) if examples else 0.0
        if sc > bestsc:
            best, bestsc = B, sc
    return (best if bestsc >= 0.8 else None), bestsc


def run_seed(seed):
    mem = build(); d = tempfile.mkdtemp(prefix=f"rec_{seed}_"); mem.save(d); m = SubstrateMemory.load(d)
    g = gate(m, seed); bases = ["parent_of", "sibling_of"]

    anc = sorted(closure(PARENT))
    labeled = anc[:3]; held = anc[3:]
    base_for_anc, sc = induce_base(m, labeled, bases, g)
    induce_ok = (base_for_anc == "parent_of")

    # held-out (incl deep) + negatives
    nodes = sorted({x for e in PARENT for x in e})
    negs = [pr for pr in itertools.permutations(nodes, 2) if pr not in set(anc)][:len(held)]
    ans = [climb(m, a, c, base_for_anc, g) == ((a, c) in set(anc)) for (a, c) in held + negs] if base_for_anc else []
    ans_acc = float(np.mean(ans)) if ans else 0.0

    # negative target: scrambled pairs -> no base
    rng = np.random.default_rng(seed)
    scram = [(f"q{int(rng.integers(100))}", f"r{int(rng.integers(100))}") for _ in range(5)]
    neg_base, _ = induce_base(m, scram, bases, g)
    no_false = (neg_base is None)

    m3 = SubstrateMemory.load(d)
    persist = (induce_base(m3, labeled, bases, gate(m3, seed))[0] == base_for_anc)
    deepest = max((len_path for (a, c) in held if (len_path := _depth(a, c, PARENT))), default=0)
    return {"induce_ok": bool(induce_ok), "base": base_for_anc, "ans_acc": round(ans_acc, 3),
            "no_false": bool(no_false), "persist": bool(persist), "max_held_depth": deepest,
            "demo_g0_g5": climb(m, "g0", "g5", base_for_anc or "parent_of", g)}


def _depth(a, c, edges):
    g = {}
    for x, y in edges:
        g.setdefault(x, []).append(y)
    from collections import deque
    q = deque([(a, 0)])
    while q:
        n, dpt = q.popleft()
        if n == c:
            return dpt
        for nb in g.get(n, []):
            q.append((nb, dpt + 1))
    return 0


if __name__ == "__main__":
    print("=== JEP-321: induce RECURSIVE rule (ancestor = closure of parent) ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: induce_ok={r['induce_ok']} base={r['base']} | held-out acc={r['ans_acc']} "
              f"(max depth {r['max_held_depth']}) | no-false={r['no_false']} persists={r['persist']} "
              f"| g0->g5 (5-hop)={r['demo_g0_g5']}", flush=True)
    J321a = all(R[s]['induce_ok'] and R[s]['no_false'] for s in seeds)
    J321b = all(R[s]['ans_acc'] >= 0.90 for s in seeds)
    J321c = all(R[s]['persist'] for s in seeds)
    passed = J321a and J321b and J321c
    print("\n--- VERDICT ---", flush=True)
    print(f"J321a induce recursive base + reject scramble: {J321a}", flush=True)
    print(f"J321b apply held-out incl deep (>=.90)        : {J321b}", flush=True)
    print(f"J321c persists                                 : {J321c}", flush=True)
    verdict = ("PASS - the substrate induces that a relation is the transitive CLOSURE of a base (a recursive rule) "
               "and answers held-out deep queries by climbing the base") if passed else "NULL/partial"
    print(f"\nJEP-321: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP321"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J321a": J321a, "J321b": J321b, "J321c": J321c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
