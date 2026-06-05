"""JEP-238 — the relation-INTERACTION matrix through the substrate (part-of x is-a UP, with leak guard).

Compose two substrate retrievals: retrieve a part's WHOLE from a part-of store, chain the whole's is-a ancestors
from an is-a store, and answer 'is the part part-of <super>?' for supers up the is-a chain -- reproducing the
engine's signature interaction ('a dog's heart is part of an animal' but NOT 'part of a cat'). No transformer.

Pre-registered bars in docs/amendments/jep238_substrate_interaction.md.
"""
import json
from pathlib import Path
import numpy as np

from world.energy import EnergyNet
from world.understanding import UnderstandingEngine
from tools.run_jep232_relation_store import KEY, VAL, N

SIM_STOP = 0.6 * KEY


def make_store(edges, code, seed, train=True):
    net = EnergyNet(n_per_module=N, n_modules=1, seed=seed)
    if train:
        pats = [np.concatenate([code[a], code[b]]) for a, b in edges]
        for _ in range(120):
            net.train_epoch(pats, cue_frac=0.5, lr=0.02, relax_steps=12)
    return net


def hop(net, x, code, concepts, seed):
    net.state = np.random.default_rng(seed).choice([-1.0, 1.0], N)
    s = net.relax(np.arange(KEY), code[x], steps=40)
    val = np.sign(s[KEY:KEY + VAL])
    sims = {c: float(val @ code[c]) for c in concepts}
    best = max(sims, key=sims.get)
    return (best, sims[best])


def isa_ancestors(net, x, code, concepts, seed, max_depth=8):
    anc, seen, cur = set(), {x}, x
    for d in range(max_depth):
        nxt, sim = hop(net, cur, code, concepts, seed + d)
        if sim < SIM_STOP or nxt in seen:
            break
        anc.add(nxt); seen.add(nxt); cur = nxt
    return anc


def part_of_super(part, sup, partnet, isanet, code, concepts, seed):
    """part-of x is-a UP: the part's whole, then up the whole's is-a chain."""
    w, sim = hop(partnet, part, code, concepts, seed)
    if sim < SIM_STOP:
        return False
    supers = {w} | isa_ancestors(isanet, w, code, concepts, seed)
    return sup in supers


def run_seed(seed):
    passage = ("A heart is part of a dog. A dog is a canine. A canine is a mammal. A mammal is an animal. "
               "A cat is a feline. A feline is a mammal.")
    e = UnderstandingEngine(seed=seed); e.read(passage)
    isa_edges = [(c, p) for c, ps in e.parents.items() for p in ps]
    part_edges = [(pt, wh) for pt, whs in getattr(e, "part_of_g", {}).items() for wh in whs]
    concepts = sorted({x for ed in isa_edges + part_edges for x in ed})
    code = {c: np.random.default_rng(hash((seed, c)) % (2**32)).choice([-1.0, 1.0], KEY) for c in concepts}
    isanet = make_store(isa_edges, code, seed, True)
    partnet = make_store(part_edges, code, seed, True)
    isactl = make_store(isa_edges, code, seed, False)
    partctl = make_store(part_edges, code, seed, False)

    def sub(part, sup, pn, inet):
        return part_of_super(part, sup, pn, inet, code, concepts, seed)

    a = sub("heart", "animal", partnet, isanet) and sub("heart", "mammal", partnet, isanet)
    b = not sub("heart", "cat", partnet, isanet) and not sub("heart", "feline", partnet, isanet)

    # battery: for the part 'heart', every concept as a candidate super; ground truth = engine's part_of
    bat = [(s_, e.part_of("heart", s_)) for s_ in concepts if s_ != "heart"]
    match = sum(sub("heart", s_, partnet, isanet) == truth for s_, truth in bat) / len(bat)
    ctl = sum(sub("heart", s_, partctl, isactl) == truth for s_, truth in bat) / len(bat)
    return {"a": bool(a), "b": bool(b), "c": match, "d_ctl": ctl, "n_q": len(bat),
            "isa_edges": len(isa_edges), "part_edges": len(part_edges)}


if __name__ == "__main__":
    print("=== JEP-238: part-of x is-a interaction through the substrate ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: UP(heart->animal&mammal)={r['a']} leak-guard(NOT cat/feline)={r['b']} | "
              f"battery match={r['c']:.2f} (control {r['d_ctl']:.2f}, {r['n_q']}q, "
              f"{r['isa_edges']} is-a + {r['part_edges']} part-of edges)", flush=True)

    J238a = all(R[s]['a'] for s in seeds)
    J238b = all(R[s]['b'] for s in seeds)
    J238c = all(R[s]['c'] >= 0.90 for s in seeds)
    J238d = all(R[s]['d_ctl'] <= 0.60 for s in seeds)
    passed = J238a and J238b and J238c and J238d

    print("\n--- VERDICT ---", flush=True)
    print(f"J238a UP interaction holds          : {J238a}", flush=True)
    print(f"J238b leak guard holds              : {J238b}", flush=True)
    print(f"J238c battery match (>=0.90)        : {J238c}", flush=True)
    print(f"J238d above untrained control       : {J238d}", flush=True)
    verdict = ("PASS - the engine's part-of x is-a interaction (incl leak guard) runs through the substrate") \
        if passed else "NULL/partial"
    print(f"\nJEP-238: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP238"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J238a": J238a, "J238b": J238b,
         "J238c": J238c, "J238d": J238d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
