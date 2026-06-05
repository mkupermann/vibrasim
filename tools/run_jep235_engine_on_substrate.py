"""JEP-235 CAPSTONE — the Understanding Engine reasons through the substrate, end-to-end from prose.

read() a passage -> store the extracted is-a taxonomy as key->value attractors in world.energy.EnergyNet ->
answer 'is X a Y?' by chaining retrievals THROUGH energy relaxation (collect the ancestor set), compared to the
engine's symbolic is_a (ground truth). Plus the honest multi-parent/DAG boundary test.

Pre-registered bars in docs/amendments/jep235_engine_on_substrate.md.
"""
import json
from pathlib import Path
import numpy as np

from world.energy import EnergyNet
from world.understanding import UnderstandingEngine
from tools.run_jep232_relation_store import KEY, VAL, N

SIM_STOP = 0.6 * KEY                       # retrieval overlap below this = no stored parent (a root); stop the walk


def edges_from(engine):
    """is-a edges (child -> parent) from the engine's symbolic taxonomy."""
    out = []
    for child, pars in engine.parents.items():
        for p in pars:
            out.append((child, p))
    return out


def encode(edges, seed):
    concepts = sorted({c for e in edges for c in e})
    rng = np.random.default_rng(seed)
    code = {c: rng.choice([-1.0, 1.0], KEY) for c in concepts}
    return code, concepts


def store(edges, code, seed, train=True):
    patterns = [np.concatenate([code[c], code[p]]) for c, p in edges]
    net = EnergyNet(n_per_module=N, n_modules=1, seed=seed)
    if train:
        for _ in range(120):
            net.train_epoch(patterns, cue_frac=0.5, lr=0.02, relax_steps=12)
    return net


def step(net, key_bits, code, concepts, seed):
    """One substrate hop: clamp key, relax, return (nearest_concept, overlap) or (None, low) if below threshold."""
    net.state = np.random.default_rng(seed).choice([-1.0, 1.0], N)
    s = net.relax(np.arange(KEY), key_bits, steps=40)
    val = np.sign(s[KEY:KEY + VAL])
    sims = {c: float(val @ code[c]) for c in concepts}
    best = max(sims, key=sims.get)
    return (best, sims[best])


def ancestors_substrate(net, x, code, concepts, seed, max_depth=8):
    """Walk parents through the substrate from x; stop at a root (low overlap), a cycle, or max_depth."""
    anc, seen, cur = set(), {x}, x
    for d in range(max_depth):
        nxt, sim = step(net, code[cur], code, concepts, seed + d)
        if sim < SIM_STOP or nxt in seen:        # root reached (no stored parent) or cycle -> stop
            break
        anc.add(nxt); seen.add(nxt); cur = nxt
    return anc


def battery(engine, concepts):
    """Mixed is_a queries (positives across depths + negatives) with symbolic ground truth."""
    qs = []
    cs = list(concepts)
    for x in cs:
        for y in cs:
            if x != y:
                qs.append((x, y, engine.is_a(x, y)))
    # keep all positives + a matched number of negatives for a balanced battery
    pos = [q for q in qs if q[2]]
    neg = [q for q in qs if not q[2]]
    rng = np.random.default_rng(0)
    neg = [neg[i] for i in rng.permutation(len(neg))[:max(len(pos), 4)]]
    return pos + neg


def run_seed(seed):
    # TREE taxonomy read FROM PROSE (single parent each), depth >= 3
    tree_passage = ("A poodle is a dog. A dog is a canine. A canine is a mammal. A mammal is an animal. "
                    "An animal is an organism. A cat is a feline. A feline is a mammal.")
    e = UnderstandingEngine(seed=seed); e.read(tree_passage)
    edges = edges_from(e)
    code, concepts = encode(edges, seed)
    net = store(edges, code, seed, train=True)
    ctl = store(edges, code, seed, train=False)

    bat = battery(e, concepts)
    def match(n):
        ok = 0
        for x, y, truth in bat:
            got = y in ancestors_substrate(n, x, code, concepts, seed)
            ok += (got == truth)
        return ok / len(bat)
    a = match(net); c = match(ctl)
    # depth-3 positive resolves through substrate (from prose)
    deep = ("poodle", "organism")
    deep_ok = deep[1] in ancestors_substrate(net, deep[0], code, concepts, seed) and e.is_a(*deep)

    # MULTI-PARENT (DAG) boundary: a node with two parents
    e2 = UnderstandingEngine(seed=seed); e2.read("A poodle is a dog. A poodle is a pet.")
    edges2 = edges_from(e2)
    code2, concepts2 = encode(edges2, seed)
    net2 = store(edges2, code2, seed, train=True)
    rec = {p for (ch, p) in edges2 if ch == "poodle"}      # symbolic: {dog, pet}
    got_parent, _ = step(net2, code2["poodle"], code2, concepts2, seed)
    sub_dog = "dog" in ancestors_substrate(net2, "poodle", code2, concepts2, seed)
    sub_pet = "pet" in ancestors_substrate(net2, "poodle", code2, concepts2, seed)
    dag_loses_one = (sub_dog != sub_pet)                   # exactly one parent recovered (the predicted limitation)

    return {"a": a, "c": c, "deep_ok": bool(deep_ok), "n_edges": len(edges), "n_q": len(bat),
            "dag_parents_symbolic": sorted(rec), "dag_recovered": got_parent, "dag_loses_one": bool(dag_loses_one)}


if __name__ == "__main__":
    print("=== JEP-235 CAPSTONE: the Understanding Engine reasons through the substrate, from prose ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: tree match={r['a']:.2f} (control {r['c']:.2f}, {r['n_q']} queries, {r['n_edges']} edges) "
              f"deep poodle->organism={r['deep_ok']} | DAG: symbolic {r['dag_parents_symbolic']} -> substrate recovered "
              f"'{r['dag_recovered']}', loses one={r['dag_loses_one']}", flush=True)

    J235a = all(R[s]['a'] >= 0.90 for s in seeds)
    J235b = all(R[s]['deep_ok'] for s in seeds)
    J235c = all(R[s]['c'] <= 0.60 for s in seeds)
    J235d = all(R[s]['dag_loses_one'] for s in seeds)
    passed = J235a and J235b and J235c and J235d

    print("\n--- VERDICT ---", flush=True)
    print(f"J235a engine reasons through substrate (tree match >=0.90): {J235a}", flush=True)
    print(f"J235b end-to-end depth-3 from prose                       : {J235b}", flush=True)
    print(f"J235c above untrained control (<=0.60)                    : {J235c}", flush=True)
    print(f"J235d DAG boundary as predicted (multi-parent loses one)  : {J235d}", flush=True)
    verdict = ("PASS - the engine's is-a reasoning runs through the substrate end-to-end from prose; the "
               "multi-parent/DAG limitation is exactly as predicted") if passed else "NULL/partial"
    print(f"\nJEP-235: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP235"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J235a": J235a, "J235b": J235b,
         "J235c": J235c, "J235d": J235d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
