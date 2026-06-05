"""JEP-297 — multi-hop reasoning over the PERSISTENT substrate memory (transitive is-a by iterated unbind).

Climb an is-a chain at recall time to answer questions never stored directly, with a calibration-derived gate that
says 'no more parent' (closing the JEP-296 rejection edge), and show it survives save/load. No transformer.
Pre-registered bars in docs/amendments/jep297_multihop_persistent.md.
"""
import json, tempfile
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory

# depth-5 chain + distractor branches (facts the store holds directly, one hop each)
CHAIN = [("poodle", "isa", "dog"), ("dog", "isa", "mammal"), ("mammal", "isa", "animal"),
         ("animal", "isa", "organism")]
DISTRACT = [("salmon", "isa", "fish"), ("fish", "isa", "animal"), ("oak", "isa", "tree"),
            ("tree", "isa", "organism"), ("cat", "isa", "mammal"), ("sparrow", "isa", "bird"),
            ("bird", "isa", "animal"), ("rose", "isa", "plant")]
# held-out calibration facts (NOT in the test chain) to set the gate
CALIB = [("c1", "isa", "k1"), ("c2", "isa", "k2"), ("c3", "isa", "k3"), ("c4", "isa", "k4")]


def gate_threshold(mem, seed):
    """Midpoint between mean taught-edge sim and mean untaught (random) sim, from CALIBRATION facts only."""
    taught = np.mean([mem.query(c, "isa")[1] for (c, _, _) in CALIB])
    rng = np.random.default_rng(seed + 321)
    untaught = np.mean([mem.query(f"none_{int(rng.integers(1e9))}", "isa")[1] for _ in range(32)])
    return float((taught + untaught) / 2.0), float(taught), float(untaught)


def is_a(mem, x, y, gate, max_hops=8):
    """Transitive is-a: climb parents by iterated query; accept a parent only if sim >= gate."""
    cur, seen = x, {x}
    for _ in range(max_hops):
        parent, s = mem.query(cur, "isa")
        if parent is None or s < gate or parent in seen:
            return False
        if parent == y:
            return True
        seen.add(parent); cur = parent
    return False


def build(seed):
    mem = SubstrateMemory(D=4096, tau=0.12)
    for (c, r, p) in CHAIN + DISTRACT + CALIB:
        mem.add_fact(c, r, p)
    return mem


def four_answers(mem, gate):
    return (is_a(mem, "poodle", "organism", gate),   # True, 4 hops
            is_a(mem, "poodle", "fish", gate),        # False
            is_a(mem, "dog", "mammal", gate),         # True, 1 hop
            is_a(mem, "rock", "mammal", gate))        # False (rock not stored)


def run_seed(seed):
    mem = build(seed)
    gate, taught, untaught = gate_threshold(mem, seed)
    ans = four_answers(mem, gate)
    expected = (True, False, True, False)
    j297a = (ans == expected)

    d = tempfile.mkdtemp(prefix=f"reason_{seed}_")
    mem.save(d)
    mem2 = SubstrateMemory.load(d)
    gate2, _, _ = gate_threshold(mem2, seed)
    ans2 = four_answers(mem2, gate2)
    j297b = (ans2 == ans == expected)

    # J297c: top of chain returns no further parent (gate rejects random continuation)
    top_parent, top_s = mem.query("organism", "isa")
    j297c = (top_s < gate)

    return {"gate": round(gate, 3), "taught": round(taught, 3), "untaught": round(untaught, 3),
            "answers": ans, "answers_reload": ans2, "top_sim": round(top_s, 3),
            "J297a": j297a, "J297b": j297b, "J297c": j297c}


if __name__ == "__main__":
    print("=== JEP-297: multi-hop reasoning over the persistent substrate memory ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: gate={r['gate']} (taught={r['taught']} untaught={r['untaught']}) | "
              f"answers={r['answers']} reload={r['answers_reload']} | top-of-chain sim={r['top_sim']}", flush=True)

    J297a = all(R[s]["J297a"] for s in seeds)
    J297b = all(R[s]["J297b"] for s in seeds)
    J297c = all(R[s]["J297c"] for s in seeds)
    passed = J297a and J297b and J297c
    print("\n--- VERDICT ---", flush=True)
    print(f"J297a multi-hop is-a correct (5-deep chain, 4 queries): {J297a}", flush=True)
    print(f"J297b answers survive save/load (fresh object)        : {J297b}", flush=True)
    print(f"J297c gate halts climbing at top of chain             : {J297c}", flush=True)
    verdict = ("PASS - the persistent substrate memory supports transitive inference: it answers questions never "
               "stored directly by chaining facts at recall, and the reasoning survives close+reopen") if passed \
        else "NULL/partial"
    print(f"\nJEP-297: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP297"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds},
                                                  "J297a": J297a, "J297b": J297b, "J297c": J297c,
                                                  "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
