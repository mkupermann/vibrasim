"""JEP-237 — close the DAG retrieval: detect trained edges by key->value BINDING ENERGY.

Same slot-binding store as JEP-236, but ACCEPT a slot retrieval only if the settled energy is a deep attractor
(<= 0.7 * median energy of the stored training patterns) -> rejects empty slots that a value-overlap threshold
could not. Closes JEP-236's empty-slot problem. Established (Hopfield energy as a stored-vs-spurious detector).

Pre-registered bars in docs/amendments/jep237_substrate_dag_energy_gate.md.
"""
import json
from collections import deque
from pathlib import Path
import numpy as np

from world.energy import EnergyNet
from world.understanding import UnderstandingEngine
from tools.run_jep232_relation_store import KEY, VAL, N
from tools.run_jep236_substrate_dag import edges_from, setup, patterns_for, MAXDEG

GATE = 0.7      # accept slot iff settled energy <= GATE * median(stored-pattern energies)


def store_gated(edges, code, slot, seed, train=True):
    net = EnergyNet(n_per_module=N, n_modules=1, seed=seed)
    pats = patterns_for(edges, code, slot)
    if train:
        for _ in range(140):
            net.train_epoch(pats, cue_frac=0.5, lr=0.02, relax_steps=12)
    e_med = float(np.median([net.energy(p) for p in pats])) if pats else 0.0
    return net, e_med


def parents_gated(net, child, code, slot, concepts, seed, e_cut):
    out = []
    for i in range(MAXDEG):
        net.state = np.random.default_rng(seed + i).choice([-1.0, 1.0], N)
        s = net.relax(np.arange(KEY), code[child] * slot[i], steps=40)
        if net.energy(s) > e_cut:                       # not a deep (trained) attractor -> empty slot, drop
            continue
        val = np.sign(s[KEY:KEY + VAL])
        sims = {c: float(val @ code[c]) for c in concepts}
        best = max(sims, key=sims.get)
        if best != child:
            out.append(best)
    return list(dict.fromkeys(out))


def ancestors_gated(net, x, code, slot, concepts, seed, e_cut, max_depth=8):
    anc, seen, q = set(), {x}, deque([(x, 0)])
    while q:
        cur, d = q.popleft()
        if d >= max_depth:
            continue
        for p in parents_gated(net, cur, code, slot, concepts, seed, e_cut):
            if p not in seen:
                seen.add(p); anc.add(p); q.append((p, d + 1))
    return anc


def battery(engine, concepts):
    qs = [(x, y, engine.is_a(x, y)) for x in concepts for y in concepts if x != y]
    pos = [q for q in qs if q[2]]; neg = [q for q in qs if not q[2]]
    rng = np.random.default_rng(0)
    neg = [neg[i] for i in rng.permutation(len(neg))[:max(len(pos), 4)]]
    return pos + neg


def gate_confusion(net, edges, code, slot, concepts, seed, e_cut):
    """0 false-accept / 0 false-reject check: for every (child, slot_i), is the gate decision == (slot trained?)."""
    by_child = {}
    for c, p in edges:
        by_child.setdefault(c, []).append(p)
    fa = fr = 0
    for child, pars in by_child.items():
        ndeg = len(pars[:MAXDEG])
        for i in range(MAXDEG):
            net.state = np.random.default_rng(seed + i).choice([-1.0, 1.0], N)
            s = net.relax(np.arange(KEY), code[child] * slot[i], steps=40)
            accepted = net.energy(s) <= e_cut
            trained = i < ndeg
            fa += (accepted and not trained)
            fr += (not accepted and trained)
    return fa, fr


def run_seed(seed):
    passage = ("A poodle is a dog. A poodle is a pet. A dog is a mammal. A mammal is an animal. "
               "A pet is a companion. A cat is a pet.")
    e = UnderstandingEngine(seed=seed); e.read(passage)
    edges = edges_from(e)
    code, slot, concepts = setup(edges, seed)
    net, e_med = store_gated(edges, code, slot, seed, train=True)
    ctl, _ = store_gated(edges, code, slot, seed, train=False)
    e_cut = GATE * e_med

    poodle = parents_gated(net, "poodle", code, slot, concepts, seed, e_cut)
    cat = parents_gated(net, "cat", code, slot, concepts, seed, e_cut)
    a = (set(poodle) == {"dog", "pet"}) and (cat == ["pet"])     # exact parent sets, no phantoms

    bat = battery(e, concepts)
    b = sum((y in ancestors_gated(net, x, code, slot, concepts, seed, e_cut)) == t for x, y, t in bat) / len(bat)
    c = sum((y in ancestors_gated(ctl, x, code, slot, concepts, seed, GATE * (e_med if e_med else 1)))
            == t for x, y, t in bat) / len(bat)
    fa, fr = gate_confusion(net, edges, code, slot, concepts, seed, e_cut)
    return {"a": bool(a), "b": b, "c": c, "poodle": sorted(poodle), "cat": cat,
            "e_med": round(e_med, 1), "e_cut": round(e_cut, 1), "false_accept": fa, "false_reject": fr}


if __name__ == "__main__":
    print("=== JEP-237: DAG retrieval via energy-gated slot-binding ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: poodle={r['poodle']} cat={r['cat']} | DAG match={r['b']:.2f} (control {r['c']:.2f}) | "
              f"gate cut={r['e_cut']} (med {r['e_med']}) false-accept={r['false_accept']} false-reject={r['false_reject']}",
              flush=True)

    J237a = all(R[s]['a'] for s in seeds)
    J237b = all(R[s]['b'] >= 0.90 for s in seeds)
    J237c = all(R[s]['c'] <= 0.60 for s in seeds)
    J237d = all(R[s]['false_accept'] == 0 and R[s]['false_reject'] == 0 for s in seeds)
    passed = J237a and J237b and J237c and J237d

    print("\n--- VERDICT ---", flush=True)
    print(f"J237a clean parent sets (no phantoms) : {J237a}", flush=True)
    print(f"J237b DAG closure matches symbolic    : {J237b}", flush=True)
    print(f"J237c above untrained control         : {J237c}", flush=True)
    print(f"J237d gate 0 false-accept/reject      : {J237d}", flush=True)
    verdict = ("PASS - the energy gate closes the DAG boundary: the substrate holds the engine's multi-parent "
               "taxonomy and reasons over it") if passed else "NULL/partial"
    print(f"\nJEP-237: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP237"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J237a": J237a, "J237b": J237b,
         "J237c": J237c, "J237d": J237d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
