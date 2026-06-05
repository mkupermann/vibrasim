"""JEP-236 — close the DAG boundary: multi-parent taxonomies in the substrate via SLOT-BINDING.

Store each is-a edge (child -> parent_i) under a distinct key child_code (X) slot_i_code; recover ALL parents by
querying the slots; BFS the multi-parent ancestor set. Closes JEP-235's single-parent limitation. Established VSA
slot-binding + Hopfield CAM, named as such.

Pre-registered bars in docs/amendments/jep236_substrate_dag.md.
"""
import json
from collections import deque
from pathlib import Path
import numpy as np

from world.energy import EnergyNet
from world.understanding import UnderstandingEngine
from tools.run_jep232_relation_store import KEY, VAL, N

MAXDEG = 3
SIM_STOP = 0.6 * KEY


def edges_from(engine):
    return [(c, p) for c, pars in engine.parents.items() for p in pars]


def setup(edges, seed):
    rng = np.random.default_rng(seed)
    concepts = sorted({c for e in edges for c in e})
    code = {c: rng.choice([-1.0, 1.0], KEY) for c in concepts}
    slot = [rng.choice([-1.0, 1.0], KEY) for _ in range(MAXDEG)]
    return code, slot, concepts


def patterns_for(edges, code, slot):
    by_child = {}
    for c, p in edges:
        by_child.setdefault(c, []).append(p)
    pats = []
    for c, pars in by_child.items():
        for i, p in enumerate(pars[:MAXDEG]):
            pats.append(np.concatenate([code[c] * slot[i], code[p]]))   # key = child (X) slot_i
    return pats


def store(edges, code, slot, seed, train=True):
    net = EnergyNet(n_per_module=N, n_modules=1, seed=seed)
    if train:
        pats = patterns_for(edges, code, slot)
        for _ in range(140):
            net.train_epoch(pats, cue_frac=0.5, lr=0.02, relax_steps=12)
    return net


def parents_substrate(net, child, code, slot, concepts, seed):
    """Query each slot; keep retrievals clearing the confidence threshold."""
    out = []
    for i in range(MAXDEG):
        net.state = np.random.default_rng(seed + i).choice([-1.0, 1.0], N)
        s = net.relax(np.arange(KEY), code[child] * slot[i], steps=40)
        val = np.sign(s[KEY:KEY + VAL])
        sims = {c: float(val @ code[c]) for c in concepts}
        best = max(sims, key=sims.get)
        if sims[best] >= SIM_STOP and best != child:
            out.append(best)
    return list(dict.fromkeys(out))                 # dedupe, preserve order


def ancestors_dag(net, x, code, slot, concepts, seed, max_depth=8):
    anc, seen, q = set(), {x}, deque([(x, 0)])
    while q:
        cur, d = q.popleft()
        if d >= max_depth:
            continue
        for p in parents_substrate(net, cur, code, slot, concepts, seed):
            if p not in seen:
                seen.add(p); anc.add(p); q.append((p, d + 1))
    return anc


def battery(engine, concepts):
    qs = [(x, y, engine.is_a(x, y)) for x in concepts for y in concepts if x != y]
    pos = [q for q in qs if q[2]]
    neg = [q for q in qs if not q[2]]
    rng = np.random.default_rng(0)
    neg = [neg[i] for i in rng.permutation(len(neg))[:max(len(pos), 4)]]
    return pos + neg


def run_seed(seed):
    # multi-parent taxonomy FROM PROSE: poodle has TWO parents (dog, pet); a deeper chain above dog
    passage = ("A poodle is a dog. A poodle is a pet. A dog is a mammal. A mammal is an animal. "
               "A pet is a companion. A cat is a pet.")
    e = UnderstandingEngine(seed=seed); e.read(passage)
    edges = edges_from(e)
    code, slot, concepts = setup(edges, seed)
    net = store(edges, code, slot, seed, train=True)
    ctl = store(edges, code, slot, seed, train=False)

    both = set(parents_substrate(net, "poodle", code, slot, concepts, seed))
    a = {"dog", "pet"} <= both

    bat = battery(e, concepts)
    def match(n):
        ok = sum((y in ancestors_dag(n, x, code, slot, concepts, seed)) == truth for x, y, truth in bat)
        return ok / len(bat)
    b = match(net); c = match(ctl)

    # in-rung counter-check (i): a single-parent node returns EXACTLY one parent (no spurious slot)
    cat_parents = parents_substrate(net, "cat", code, slot, concepts, seed)
    single_clean = (cat_parents == ["pet"])
    return {"a": bool(a), "b": b, "c": c, "n_edges": len(edges), "n_q": len(bat),
            "poodle_parents": sorted(both), "cat_parents": cat_parents, "single_clean": bool(single_clean)}


if __name__ == "__main__":
    print("=== JEP-236: multi-parent DAG taxonomy in the substrate via slot-binding ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: poodle parents={r['poodle_parents']} (both? {r['a']}) | DAG match={r['b']:.2f} "
              f"(control {r['c']:.2f}, {r['n_q']}q, {r['n_edges']} edges) | cat parents={r['cat_parents']} "
              f"single-clean={r['single_clean']}", flush=True)

    J236a = all(R[s]['a'] for s in seeds)
    J236b = all(R[s]['b'] >= 0.90 for s in seeds)
    J236c = all(R[s]['c'] <= 0.60 for s in seeds)
    J236d = all(R[s]['single_clean'] for s in seeds)      # capacity/cleanliness: single-parent stays single
    passed = J236a and J236b and J236c and J236d

    print("\n--- VERDICT ---", flush=True)
    print(f"J236a multi-parent recovered (both)   : {J236a}", flush=True)
    print(f"J236b DAG closure matches symbolic    : {J236b}", flush=True)
    print(f"J236c above untrained control         : {J236c}", flush=True)
    print(f"J236d single-parent stays clean       : {J236d}", flush=True)
    verdict = ("PASS - the substrate now holds the engine's multi-parent DAG taxonomy and reasons over it "
               "(slot-binding closes the JEP-235 boundary)") if passed else "NULL/partial"
    print(f"\nJEP-236: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP236"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J236a": J236a, "J236b": J236b,
         "J236c": J236c, "J236d": J236d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
