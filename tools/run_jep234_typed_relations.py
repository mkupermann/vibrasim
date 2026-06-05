"""JEP-234 — can the substrate be a TYPED relational store (multiple relation types, no crosstalk)?

Bind the relation type into the key via a Hadamard (element-wise +-1) product subject (X) relation = a VSA-bound
key unique to the (subject, relation) pair; VALUE = object. Store mixed relation types in one EnergyNet; query by
(subject, relation). Established VSA role-binding + Hopfield key->value memory, named as such.

Pre-registered bars in docs/amendments/jep234_substrate_typed_relations.md.
"""
import json
from pathlib import Path
import numpy as np

from world.energy import EnergyNet
from tools.run_jep232_relation_store import KEY, VAL, N, store

RELS = ["is_a", "part_of", "causal"]


def setup(seed):
    """Return (concept_codes, relation_codes, facts). facts: list of (subj, rel, obj) index/name tuples."""
    rng = np.random.default_rng(seed)
    n_concepts = 24                            # 12 facts x (subject, object) over distinct concept pairs
    ccode = [rng.choice([-1.0, 1.0], KEY) for _ in range(n_concepts)]
    rcode = {r: rng.choice([-1.0, 1.0], KEY) for r in RELS}
    # 4 facts per relation type over distinct concept pairs (12 typed facts)
    facts = []
    c = 0
    for r in RELS:
        for _ in range(4):
            facts.append((c, r, c + 1)); c += 2
    return ccode, rcode, facts


def key_of(subj, rel, ccode, rcode):
    return ccode[subj] * rcode[rel]            # Hadamard bind: unique key for the (subject, relation) pair


def decode(val_bits, ccode):
    sims = np.array([np.sign(val_bits) @ ccode[k] for k in range(len(ccode))])
    return int(np.argmax(sims))


def build(facts, ccode, rcode, seed, train=True):
    patterns = [np.concatenate([key_of(s, r, ccode, rcode), ccode[o]]) for s, r, o in facts]
    net = EnergyNet(n_per_module=N, n_modules=1, seed=seed)
    if train:
        for _ in range(120):
            net.train_epoch(patterns, cue_frac=0.5, lr=0.02, relax_steps=12)
    return net


def retrieve(net, subj, rel, ccode, rcode, seed):
    net.state = np.random.default_rng(seed + subj).choice([-1.0, 1.0], N)
    s = net.relax(np.arange(KEY), key_of(subj, rel, ccode, rcode), steps=40)
    return decode(s[KEY:KEY + VAL], ccode)


def run_seed(seed):
    ccode, rcode, facts = setup(seed)
    net = build(facts, ccode, rcode, seed, train=True)
    ctl = build(facts, ccode, rcode, seed, train=False)

    # J234a: typed retrieval; J234d: per-type
    per_type = {r: [] for r in RELS}
    ok = 0
    for s, r, o in facts:
        hit = retrieve(net, s, r, ccode, rcode, seed) == o
        ok += hit; per_type[r].append(hit)
    a = ok / len(facts)
    d = {r: float(np.mean(v)) for r, v in per_type.items()}

    # J234b: wrong-relation discrimination — query each stored subject with a DIFFERENT relation; how often the
    # correct (original) object still comes back (should be ~chance, i.e. the binding discriminates)
    wrong = 0; ntot = 0
    for s, r, o in facts:
        for r2 in RELS:
            if r2 == r:
                continue
            ntot += 1
            if retrieve(net, s, r2, ccode, rcode, seed) == o:
                wrong += 1
    b = wrong / max(ntot, 1)

    # J234c: untrained control
    cok = sum(retrieve(ctl, s, r, ccode, rcode, seed) == o for s, r, o in facts) / len(facts)
    return {"a": a, "b": b, "c": cok, "d": d}


if __name__ == "__main__":
    print("=== JEP-234: typed relational store in the substrate ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: typed recall={r['a']:.2f} wrong-rel hit={r['b']:.2f} control={r['c']:.2f} | "
              f"per-type {{ {', '.join(f'{k}={v:.2f}' for k, v in r['d'].items())} }}", flush=True)

    J234a = all(R[s]['a'] >= 0.85 for s in seeds)
    J234b = all(R[s]['b'] < 0.20 for s in seeds)
    J234c = all(R[s]['c'] <= 0.40 for s in seeds)
    J234d = all(all(v >= 0.85 for v in R[s]['d'].values()) for s in seeds)
    passed = J234a and J234b and J234c and J234d

    print("\n--- VERDICT ---", flush=True)
    print(f"J234a typed retrieval (>=0.85)        : {J234a}", flush=True)
    print(f"J234b relation discriminates (<0.20)  : {J234b}", flush=True)
    print(f"J234c control fails (<=0.40)          : {J234c}", flush=True)
    print(f"J234d all types served (>=0.85)       : {J234d}", flush=True)
    verdict = ("PASS - the substrate is a TYPED relational store: multiple relation types, binding discriminates, "
               "no type starved") if passed else "NULL/partial"
    print(f"\nJEP-234: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP234"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J234a": J234a, "J234b": J234b,
         "J234c": J234c, "J234d": J234d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
