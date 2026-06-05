"""JEP-331 — deductive generation: the durable brain states new TRUE facts it was never directly told (forward-
chaining + verbalization). No transformer. Pre-registered bars in docs/amendments/jep331_deductive_generation.md.
"""
import json, tempfile
from pathlib import Path
import numpy as np
from world.understanding import UnderstandingEngine
from world.substrate_memory import SubstrateMemory

# directly-told facts (the ENGINE reads these; the substrate is bridged from it)
TOLD = ("A poodle is a dog. A beagle is a dog. A dog is a mammal. A mammal is an animal. "
        "A dog can bark. A mammal can breathe. A salmon is a fish. A fish is an animal.")
LEGS = [("dog", "4"), ("salmon", "0")]                  # numeric attrs added directly to the substrate
CALIB = [("z1", "isa", "w1"), ("z2", "isa", "w2"), ("z3", "isa", "w3")]


def gate(mem, seed, role="isa"):
    edges = [(a, b) for (a, r, b) in mem.facts if r == role]
    rng = np.random.default_rng(seed)
    t = np.mean([mem.edge_sim(a, role, b) for (a, b) in edges]) if edges else 0.2
    u = np.mean([mem.query(f"n_{int(rng.integers(1e9))}", role)[1] for _ in range(30)])
    return float((t + u) / 2)


def ancestors(mem, x, g, mx=20):
    out, cur, seen = [x], x, {x}
    for _ in range(mx):
        p, s = mem.query(cur, "isa")
        if p is None or s < g or p in seen:
            break
        out.append(p); seen.add(p); cur = p
    return out


def generate(mem, eng, g):
    """Forward-chain + verbalize. Returns list of (sentence, (s,r,o)) for derived, novel, entailed facts."""
    isa_direct = {(a, b) for (a, r, b) in mem.facts if r == "isa"}
    prop_direct = {(a, b) for (a, r, b) in mem.facts if r == "hasprop"}
    legs_direct = {(a, b) for (a, r, b) in mem.facts if r == "has_legs"}
    entities = sorted({a for (a, r, b) in mem.facts if r in ("isa", "hasprop", "has_legs")})
    out = []
    for x in entities:
        anc = ancestors(mem, x, g)
        # inherited is-a (skip the direct parent edge)
        for a in anc[1:]:
            if (x, a) not in isa_direct:
                out.append((f"A {x} is a{'n' if a[0] in 'aeiou' else ''} {a}.", (x, "isa", a)))
        # inherited properties (from any ancestor, not directly on x)
        for a in anc:
            for (s_, o_) in prop_direct:
                if s_ == a and (x, o_) not in prop_direct and a != x:
                    out.append((f"A {x} can {o_}.", (x, "hasprop", o_)))
        # inherited numeric legs (nearest ancestor with has_legs, if not direct on x)
        for a in anc:
            hit = [(s_, o_) for (s_, o_) in legs_direct if s_ == a]
            if hit and (x, hit[0][1]) not in legs_direct and a != x:
                out.append((f"A {x} has {hit[0][1]} legs.", (x, "has_legs", hit[0][1])))
                break
    # de-dup
    seen, uniq = set(), []
    for sent, fact in out:
        if fact not in seen:
            seen.add(fact); uniq.append((sent, fact))
    return uniq


def closure_isa(isa):
    g = {}
    for a, b in isa:
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


def run_seed(seed):
    eng = UnderstandingEngine(seed=seed); eng.read(TOLD)
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True); mem.ingest_engine(eng)
    for a, n in LEGS:
        mem.add_fact(a, "has_legs", n)
    for (c, r, p) in CALIB:
        mem.add_fact(c, r, p)
    d = tempfile.mkdtemp(prefix=f"gen_{seed}_"); mem.save(d); m = SubstrateMemory.load(d); g = gate(m, seed)

    gen = generate(m, eng, g)

    # ground truth for soundness
    isa_direct = {(a, b) for (a, r, b) in m.facts if r == "isa"}
    isa_clo = closure_isa(isa_direct)
    prop_direct = {(a, b) for (a, r, b) in m.facts if r == "hasprop"}
    legs_direct = {(a, b) for (a, r, b) in m.facts if r == "has_legs"}

    def entailed(fact):
        x, r, o = fact
        if r == "isa":
            return (x, o) in isa_clo
        anc = [x] + [a for a in ancestors(m, x, g)]
        if r == "hasprop":
            return any((a, o) in prop_direct for a in anc)
        if r == "has_legs":
            return any((a, o) in legs_direct for a in anc)
        return False

    direct_facts = isa_direct | {(a, b) for (a, b) in prop_direct} | {(a, b) for (a, b) in legs_direct}
    sound = np.mean([entailed(f) for (_, f) in gen]) if gen else 1.0
    novel = np.mean([(f[0], f[2]) not in direct_facts for (_, f) in gen]) if gen else 0.0

    # round-trip: re-read generated sentences into a FRESH engine, recover is-a entailments
    eng2 = UnderstandingEngine(seed=seed)
    for (sent, _) in gen:
        eng2.read(sent)
    rt = [f for (_, f) in gen if f[1] == "isa"]
    rt_ok = np.mean([eng2.is_a(x, o) for (x, _, o) in rt]) if rt else 1.0

    return {"n_generated": len(gen), "soundness": round(float(sound), 3), "novelty": round(float(novel), 3),
            "roundtrip": round(float(rt_ok), 3),
            "samples": [s for (s, _) in gen[:6]]}


if __name__ == "__main__":
    print("=== JEP-331: deductive generation (state new TRUE facts never told) ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: generated={r['n_generated']} | soundness={r['soundness']} novelty={r['novelty']} "
              f"roundtrip={r['roundtrip']}", flush=True)
        for samp in R[s]["samples"]:
            print(f"      > {samp}", flush=True)
    J331a = all(R[s]['soundness'] >= 1.0 for s in seeds)
    J331b = all(R[s]['novelty'] >= 0.50 for s in seeds)
    J331c = all(R[s]['roundtrip'] >= 0.90 for s in seeds)
    passed = J331a and J331b and J331c
    print("\n--- VERDICT ---", flush=True)
    print(f"J331a soundness (every generated stmt TRUE = 1.0): {J331a}", flush=True)
    print(f"J331b novelty (>=50% never told)                 : {J331b}", flush=True)
    print(f"J331c well-formed round-trip (>=.90)             : {J331c}", flush=True)
    verdict = ("PASS - the durable brain GENERATES new true English statements entailed by what it knows, never "
               "directly told, and the engine re-parses them") if passed else "NULL/partial"
    print(f"\nJEP-331: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP331"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J331a": J331a, "J331b": J331b, "J331c": J331c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
