"""JEP-232 — does the SUBSTRATE carry the Understanding Engine's relational knowledge?

Store is-a facts (child -> parent) as key->value attractors in world.energy.EnergyNet (a modular Hopfield/
contrastive-Hebbian EBM) and retrieve the parent from a child cue THROUGH energy relaxation. Answers "where is
the substrate in the chain?" for relational knowledge. Established associative key-value memory, named as such.

Pre-registered bars in docs/amendments/jep232_substrate_relation_store.md.
"""
import json
from pathlib import Path
import numpy as np

from world.energy import EnergyNet

KEY, VAL, N = 40, 40, 80           # single dense module: KEY = [0:40], VALUE = [40:80]
EPOCHS = 120


def codes(n_concepts, seed):
    rng = np.random.default_rng(seed)
    return [rng.choice([-1.0, 1.0], KEY) for _ in range(n_concepts)]


def store(facts, code, seed, train=True):
    """facts: list of (child, parent) concept-index pairs. Returns a trained EnergyNet."""
    net = EnergyNet(n_per_module=N, n_modules=1, seed=seed)
    patterns = [np.concatenate([code[c], code[p]]) for c, p in facts]
    if train:
        for _ in range(EPOCHS):
            net.train_epoch(patterns, cue_frac=0.5, lr=0.02, relax_steps=12)
    return net


def retrieve(net, child_code, code, key_frac=1.0, seed=0):
    """Clamp (a fraction of) the KEY slot to child_code, relax the VALUE slot free, read the nearest concept."""
    rng = np.random.default_rng(seed)
    key_units = np.arange(KEY)
    if key_frac < 1.0:
        keep = rng.random(KEY) < key_frac
        key_units = key_units[keep]
        clamp_val = child_code[keep]
    else:
        clamp_val = child_code
    net.state = rng.choice([-1.0, 1.0], N)
    s = net.relax(key_units, clamp_val, steps=40)
    val = np.sign(s[KEY:KEY + VAL])
    sims = [float(val @ code[k]) for k in range(len(code))]
    return int(np.argmax(sims))


def recall_rate(facts, code, net, key_frac=1.0, seed=0):
    """Fraction of facts whose CHILD cue retrieves the correct PARENT (argmax excludes the child's own code)."""
    ok = 0
    for c, p in facts:
        sims_child = code[c]
        net.state = np.random.default_rng(seed + c).choice([-1.0, 1.0], N)
        key_units = np.arange(KEY)
        kf = key_frac
        if kf < 1.0:
            keep = np.random.default_rng(seed + 100 + c).random(KEY) < kf
            key_units = key_units[keep]; clamp = sims_child[keep]
        else:
            clamp = sims_child
        s = net.relax(key_units, clamp, steps=40)
        val = np.sign(s[KEY:KEY + VAL])
        sims = np.array([val @ code[k] for k in range(len(code))])
        sims[c] = -np.inf                      # exclude the child's own code (risk (i) guard)
        if int(np.argmax(sims)) == p:
            ok += 1
    return ok / len(facts)


def make_facts(K, n_concepts):
    # a chain c0->c1->c2->... so every child has a distinct parent; K facts over K+1 concepts
    return [(i, i + 1) for i in range(K)]


def run_seed(seed):
    out = {}
    for K in (4, 12):
        nc = K + 1
        code = codes(nc, seed)
        facts = make_facts(K, nc)
        net = store(facts, code, seed, train=True)
        out[f"K{K}_full"] = recall_rate(facts, code, net, key_frac=1.0, seed=seed)
        out[f"K{K}_partial"] = recall_rate(facts, code, net, key_frac=0.6, seed=seed)
        ctl = store(facts, code, seed, train=False)
        out[f"K{K}_control"] = recall_rate(facts, code, ctl, key_frac=1.0, seed=seed)
    return out


if __name__ == "__main__":
    print("=== JEP-232: does the substrate carry the Understanding Engine's relations? ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: K=4 recall={r['K4_full']:.2f} partial(60%)={r['K4_partial']:.2f} "
              f"control={r['K4_control']:.2f} | K=12 recall={r['K12_full']:.2f} control={r['K12_control']:.2f}",
              flush=True)

    J232a = all(R[s]['K4_full'] >= 0.85 for s in seeds)
    J232b = all(R[s]['K4_control'] <= 0.40 for s in seeds)
    J232c = all(R[s]['K4_partial'] >= 0.70 for s in seeds)
    J232d = all(R[s]['K12_full'] < R[s]['K4_full'] for s in seeds)
    passed = J232a and J232b and J232c and J232d

    print("\n--- VERDICT ---", flush=True)
    print(f"J232a substrate carries relations (K=4 >=0.85): {J232a}", flush=True)
    print(f"J232b above untrained control (<=0.40)        : {J232b}", flush=True)
    print(f"J232c partial-cue CAM (60% key >=0.70)        : {J232c}", flush=True)
    print(f"J232d bounded capacity (K12 < K4)             : {J232d}", flush=True)
    verdict = ("PASS - the energy-based SUBSTRATE carries the Understanding Engine's is-a relations as "
               "content-addressable attractors with bounded capacity") if passed else "NULL/partial"
    print(f"\nJEP-232: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP232"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J232a": J232a, "J232b": J232b,
         "J232c": J232c, "J232d": J232d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
