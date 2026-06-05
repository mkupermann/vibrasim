"""JEP-323 — close the learning loop: materialize induced rules (composition, recursive closure) into the durable
store so the derived relation is directly queryable + persists + compounds. No transformer.
Pre-registered bars in docs/amendments/jep323_rule_materialization.md.
"""
import json, tempfile, itertools
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory

PARENT = [("g0", "g1"), ("g1", "g2"), ("g2", "g3"), ("g3", "g4"),
          ("g0", "h1"), ("h1", "h2"), ("g1", "k2")]
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


def gate(mem, seed, role="parent_of"):
    """Gate calibrated on the GIVEN relation's own edges (fan-out matters: a materialized closure key holds many
    values, so its per-value sim is lower than a single-valued parent edge -> calibrate per relation)."""
    edges = [(a, b) for (a, r, b) in mem.facts if r == role]
    rng = np.random.default_rng(seed + 321)
    samp = [edges[i] for i in rng.choice(len(edges), min(20, len(edges)), replace=False)] if edges else []
    t = np.mean([mem.edge_sim(a, role, b) for (a, b) in samp]) if samp else 0.2
    u = np.mean([mem.query(f"n_{int(rng.integers(1e9))}", role)[1] for _ in range(20)])
    return float((t + u) / 2)


def bfs_succ(mem, x, rel, g):
    from collections import deque
    q, seen, out = deque([x]), {x}, []
    while q:
        cur = q.popleft()
        for (p, _) in mem.query_all(cur, rel, g):
            if p not in seen:
                seen.add(p); out.append(p); q.append(p)
    return out


def build():
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for a, b in PARENT:
        mem.add_fact(a, "parent_of", b)
    for (c, r, p) in CALIB:
        mem.add_fact(c, r, p)
    return mem


def run_seed(seed):
    mem = build(); g = gate(mem, seed)
    nodes = sorted({x for e in PARENT for x in e})

    # --- materialize grandparent_of = parent o parent ---
    P = {(a, b) for (a, b) in PARENT}
    gp_true = {(a, c) for (a, x) in P for (x2, c) in P if x == x2 and a != c}
    # derive via store traversal (2-hop) and add
    for a in nodes:
        kids = [k for (k, _) in mem.query_all(a, "parent_of", g)]
        for k in kids:
            for gc in [(o) for (o, _) in mem.query_all(k, "parent_of", g)]:
                if gc != a:
                    mem.add_fact(a, "grandparent_of", gc)

    # --- materialize ancestor_of = closure(parent) ---
    for a in nodes:
        for anc in bfs_succ(mem, a, "parent_of", g):
            mem.add_fact(a, "ancestor_of", anc)

    d = tempfile.mkdtemp(prefix=f"mat_{seed}_"); mem.save(d); m = SubstrateMemory.load(d)
    g_par = gate(m, seed, "parent_of"); g_gp = gate(m, seed, "grandparent_of"); g_anc = gate(m, seed, "ancestor_of")

    # J323a: grandparent directly retrievable (single contains), no climb
    gp_ok = np.mean([m.contains(a, "grandparent_of", c, g_gp) for (a, c) in gp_true]) if gp_true else 1.0
    gp_false = max([1 if m.contains(a, "grandparent_of", c, g_gp) else 0
                    for (a, c) in itertools.permutations(nodes, 2) if (a, c) not in gp_true] + [0])

    # J323b: ancestor directly retrievable incl deep; non-ancestor not (relation-appropriate gate for high fan-out)
    anc_true = closure(PARENT)
    anc_ok = np.mean([m.contains(a, "ancestor_of", c, g_anc) for (a, c) in anc_true]) if anc_true else 1.0
    non_anc = [(a, c) for (a, c) in itertools.permutations(nodes, 2) if (a, c) not in anc_true]
    anc_false = np.mean([not m.contains(a, "ancestor_of", c, g_anc) for (a, c) in non_anc]) if non_anc else 1.0

    # J323c: compounds -- great-grandparent (g0->g3) via materialized grandparent(g0,g2) + parent(g2,g3)
    ggp = False
    for (a, gc) in [(o1, o2) for o1 in nodes for (o2, _) in m.query_all(o1, "grandparent_of", g_gp)]:
        for (ch, _) in m.query_all(gc, "parent_of", g_par):
            if (a, ch) == ("g0", "g3"):
                ggp = True
    return {"gp_acc": round(float(gp_ok), 3), "gp_no_false": (gp_false == 0),
            "anc_acc": round(float(anc_ok), 3), "anc_no_false": round(float(anc_false), 3),
            "compounds_ggp_g0_g4": bool(ggp), "n_facts": len(m.facts)}


if __name__ == "__main__":
    print("=== JEP-323: materialize induced rules into the durable store ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: grandparent direct={r['gp_acc']} (no-false={r['gp_no_false']}) | ancestor direct="
              f"{r['anc_acc']} (neg {r['anc_no_false']}) | compounds(g0->g4 great-grand)={r['compounds_ggp_g0_g4']} "
              f"| {r['n_facts']} facts", flush=True)
    J323a = all(R[s]['gp_acc'] >= 0.95 and R[s]['gp_no_false'] for s in seeds)
    J323b = all(R[s]['anc_acc'] >= 0.95 and R[s]['anc_no_false'] >= 0.95 for s in seeds)
    J323c = all(R[s]['compounds_ggp_g0_g4'] for s in seeds)
    passed = J323a and J323b and J323c
    print("\n--- VERDICT ---", flush=True)
    print(f"J323a grandparent materialized + direct (>=.95): {J323a}", flush=True)
    print(f"J323b ancestor closure materialized + direct    : {J323b}", flush=True)
    print(f"J323c compounds (uses materialized relation)     : {J323c}", flush=True)
    verdict = ("PASS - induced rules are materialized into the durable store: the derived relation becomes directly "
               "queryable, persists, and compounds into higher-order queries") if passed else "NULL/partial"
    print(f"\nJEP-323: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP323"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J323a": J323a, "J323b": J323b, "J323c": J323c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
