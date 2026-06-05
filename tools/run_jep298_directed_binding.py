"""JEP-298 — directed edges via permutation-protected binding -> transitive is-a works (fixes JEP-297 NULL).

Same depth-5 chain JEP-297 failed, now with SubstrateMemory(directed=True). Verifies multi-hop is-a, that a node
no longer retrieves its children (directionality), persistence, and no regression of the symmetric path. No
transformer. Pre-registered bars in docs/amendments/jep298_directed_binding.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory

CHAIN = [("poodle", "isa", "dog"), ("dog", "isa", "mammal"), ("mammal", "isa", "animal"),
         ("animal", "isa", "organism")]
DISTRACT = [("salmon", "isa", "fish"), ("fish", "isa", "animal"), ("oak", "isa", "tree"),
            ("tree", "isa", "organism"), ("cat", "isa", "mammal"), ("sparrow", "isa", "bird"),
            ("bird", "isa", "animal"), ("rose", "isa", "plant")]
CALIB = [("c1", "isa", "k1"), ("c2", "isa", "k2"), ("c3", "isa", "k3"), ("c4", "isa", "k4")]


def gate_threshold(mem, seed):
    taught = np.mean([mem.query(c, "isa")[1] for (c, _, _) in CALIB])
    rng = np.random.default_rng(seed + 321)
    untaught = np.mean([mem.query(f"none_{int(rng.integers(1e9))}", "isa")[1] for _ in range(32)])
    return float((taught + untaught) / 2.0), float(taught), float(untaught)


def is_a(mem, x, y, gate, max_hops=8):
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
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for (c, r, p) in CHAIN + DISTRACT + CALIB:
        mem.add_fact(c, r, p)
    return mem


def four(mem, gate):
    return (is_a(mem, "poodle", "organism", gate), is_a(mem, "poodle", "fish", gate),
            is_a(mem, "dog", "mammal", gate), is_a(mem, "rock", "mammal", gate))


def run_seed(seed):
    mem = build(seed)
    gate, taught, untaught = gate_threshold(mem, seed)
    ans = four(mem, gate)
    expected = (True, False, True, False)
    J298a = (ans == expected)

    # directionality: organism (top) has no parent -> below gate; poodle forward still clean
    org_parent, org_s = mem.query("organism", "isa")
    pood = mem.query("poodle", "isa")
    J298b = (org_s < gate) and (pood[0] == "dog")

    d = tempfile.mkdtemp(prefix=f"dir_{seed}_")
    mem.save(d)
    mem2 = SubstrateMemory.load(d)
    gate2, _, _ = gate_threshold(mem2, seed)
    ans2 = four(mem2, gate2)
    J298c = (ans2 == expected)

    return {"gate": round(gate, 3), "taught": round(taught, 3), "untaught": round(untaught, 3),
            "answers": ans, "answers_reload": ans2, "organism_sim": round(org_s, 3), "poodle_q": pood[0],
            "J298a": J298a, "J298b": J298b, "J298c": J298c}


def regression_jep296(repo):
    """Symmetric multi-module store still works (directed defaults False)."""
    out = subprocess.run([sys.executable, "tools/run_jep296_unbounded_growth.py"],
                         capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    return "JEP-296: PASS" in out.stdout


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-298: directed binding -> multi-hop inference ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: gate={r['gate']} | answers={r['answers']} reload={r['answers_reload']} | "
              f"query(organism,isa) sim={r['organism_sim']} (rejected) | query(poodle,isa)={r['poodle_q']}", flush=True)
    reg = regression_jep296(repo)
    print(f"  JEP-296 regression (symmetric multi-module): {'PASS' if reg else 'FAIL'}", flush=True)

    J298a = all(R[s]["J298a"] for s in seeds)
    J298b = all(R[s]["J298b"] for s in seeds)
    J298c = all(R[s]["J298c"] for s in seeds)
    passed = J298a and J298b and J298c and reg
    print("\n--- VERDICT ---", flush=True)
    print(f"J298a multi-hop is-a correct (the set JEP-297 failed): {J298a}", flush=True)
    print(f"J298b directionality: node doesn't retrieve children : {J298b}", flush=True)
    print(f"J298c answers survive save/load                      : {J298c}", flush=True)
    print(f"no-regression: JEP-296 symmetric path still PASS     : {reg}", flush=True)
    verdict = ("PASS - permutation-protected directed binding gives one-way is-a edges; the substrate now does "
               "transitive multi-hop inference over its persistent memory") if passed else "NULL/partial"
    print(f"\nJEP-298: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP298"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "reg": reg,
                                                  "J298a": J298a, "J298b": J298b, "J298c": J298c,
                                                  "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
