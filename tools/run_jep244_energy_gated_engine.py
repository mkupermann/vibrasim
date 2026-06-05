"""JEP-244 — robust FULL engine on the substrate via the ENERGY-GATED chain stop (the right fix for JEP-242/243).

Same typed multi-relation EnergyNet as JEP-242, but the chain-stop and the part-of hop use the JEP-237 ENERGY GATE
(continue only if settled energy <= 0.7*median stored-pattern energy) instead of SIM_STOP value-overlap -- so chains
stop at roots (untrained keys) and don't overrun into spurious nodes. Single-shot (the fix is the gate, not voting).

Pre-registered bars in docs/amendments/jep244_energy_gated_full_engine.md.
"""
import json
from pathlib import Path
import numpy as np

from world.understanding import UnderstandingEngine
from tools.run_jep232_relation_store import KEY, VAL, N
from tools.run_jep242_full_engine_substrate import collect_edges, setup

R242 = {42: 1.00, 7: 0.93}
PASSAGE = ("A poodle is a dog. A dog is a mammal. A mammal is an animal. "
           "A heart is part of a dog. "
           "A virus causes a fever. A fever causes weakness. "
           "An elephant is bigger than a dog. A dog is bigger than a cat. "
           "The war happened before the treaty. The treaty happened before the peace.")
BATTERY = [
    ("isa", "poodle", "animal"), ("isa", "poodle", "mammal"), ("isa", "poodle", "cat"),
    ("partof", "heart", "dog"), ("partof", "heart", "animal"), ("partof", "heart", "cat"),
    ("causal", "virus", "weakness"), ("causal", "virus", "fever"), ("causal", "fever", "virus"),
    ("bigger", "elephant", "cat"), ("bigger", "elephant", "dog"), ("bigger", "cat", "elephant"),
    ("before", "war", "peace"), ("before", "war", "treaty"), ("before", "peace", "war"),
]
from world.energy import EnergyNet


def build(edges, code, rcode, seed, train=True):
    net = EnergyNet(n_per_module=N, n_modules=1, seed=seed)
    pats = [np.concatenate([code[s] * rcode[r], code[o]]) for s, r, o in edges]
    if train:
        for _ in range(140):
            net.train_epoch(pats, cue_frac=0.5, lr=0.02, relax_steps=12)
    e_med = float(np.median([net.energy(p) for p in pats])) if pats else 0.0
    return net, 0.7 * e_med


def egate_hop(net, subj, rel, code, rcode, concepts, e_cut, seed):
    """Energy-gated hop: return (concept, True) if a trained edge (deep minimum), else (None, False)."""
    net.state = np.random.default_rng(seed).choice([-1.0, 1.0], N)
    s = net.relax(np.arange(KEY), code[subj] * rcode[rel], steps=40)
    if net.energy(s) > e_cut:          # shallow -> untrained key (root) -> stop
        return None
    val = np.sign(s[KEY:KEY + VAL])
    sims = {c: float(val @ code[c]) for c in concepts}
    return max(sims, key=sims.get)


def egate_chain(net, x, rel, code, rcode, concepts, e_cut, seed, max_depth=8):
    reach, seen, cur = set(), {x}, x
    for d in range(max_depth):
        nxt = egate_hop(net, cur, rel, code, rcode, concepts, e_cut, seed + d * 71)
        if nxt is None or nxt in seen:
            break
        reach.add(nxt); seen.add(nxt); cur = nxt
    return reach


def query(net, kind, a, b, code, rcode, concepts, e_cut, seed):
    if kind in ("isa", "causal", "bigger", "before"):
        return b in egate_chain(net, a, kind, code, rcode, concepts, e_cut, seed)
    if kind == "partof":
        w = egate_hop(net, a, "partof", code, rcode, concepts, e_cut, seed)
        if w is None:
            return False
        return b == w or b in egate_chain(net, w, "isa", code, rcode, concepts, e_cut, seed)
    return False


def run_seed(seed):
    e = UnderstandingEngine(seed=seed); e.read(PASSAGE)
    edges = collect_edges(e)
    code, rcode, concepts = setup(edges, seed)
    net, e_cut = build(edges, code, rcode, seed, True)
    ctl, ctl_cut = build(edges, code, rcode, seed, False)

    def truth(kind, a, b):
        if kind == "isa": return e.is_a(a, b)
        if kind == "partof": return e.part_of(a, b)
        if kind == "causal": return e.causes_effect(a, b)
        return e._order_holds(kind, a, b)

    match = sum(query(net, k, a, b, code, rcode, concepts, e_cut, seed) == truth(k, a, b)
                for k, a, b in BATTERY) / len(BATTERY)
    cmatch = sum(query(ctl, k, a, b, code, rcode, concepts, ctl_cut if ctl_cut else -1, seed) == truth(k, a, b)
                 for k, a, b in BATTERY) / len(BATTERY)
    inter = (query(net, "partof", "heart", "animal", code, rcode, concepts, e_cut, seed)
             and not query(net, "partof", "heart", "cat", code, rcode, concepts, e_cut, seed))
    # J244c: is-a chains do not overrun their roots (reached subset of symbolic ancestors)
    no_overrun = True
    for leaf in ("poodle", "dog", "mammal"):
        reached = egate_chain(net, leaf, "isa", code, rcode, concepts, e_cut, seed)
        sym = {y for y in concepts if e.is_a(leaf, y)}
        if not reached <= sym:
            no_overrun = False
    return {"match": match, "ctl": cmatch, "inter": bool(inter), "no_overrun": bool(no_overrun)}


if __name__ == "__main__":
    print("=== JEP-244: energy-gated full engine on substrate ===", flush=True)
    seeds = [42, 7]
    res = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = res[s]
        print(f"  seed {s}: battery match={r['match']:.2f} (control {r['ctl']:.2f}) interaction+leak={r['inter']} "
              f"chains-stop-at-roots={r['no_overrun']}  [JEP-242 SIM_STOP was {R242[s]:.2f}]", flush=True)

    J244a = all(res[s]['match'] == 1.00 for s in seeds)
    J244b = all(res[s]['inter'] for s in seeds)
    J244c = all(res[s]['no_overrun'] for s in seeds)
    J244d = all(res[s]['ctl'] <= 0.60 for s in seeds)
    passed = J244a and J244b and J244c and J244d

    print("\n--- VERDICT ---", flush=True)
    print(f"J244a battery 1.00 both seeds         : {J244a}", flush=True)
    print(f"J244b interaction + leak both seeds   : {J244b}", flush=True)
    print(f"J244c chains stop at roots (no overrun): {J244c}", flush=True)
    print(f"J244d control fails (<=0.60)          : {J244d}", flush=True)
    verdict = ("PASS - the energy-gated chain stop makes the full multi-relation engine run robustly on the "
               "substrate from prose (closes JEP-242/243 with the right fix)") if passed else "NULL/partial"
    print(f"\nJEP-244: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP244"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): res[s] for s in seeds}, "J244a": J244a, "J244b": J244b,
         "J244c": J244c, "J244d": J244d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
