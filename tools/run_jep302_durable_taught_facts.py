"""JEP-302 — taught FACTS survive restart: sentence-teaching is durable on both the engine (replayed corpus) and
the substrate (bridged). Headless (no Tk). No transformer. Pre-registered bars in
docs/amendments/jep302_durable_taught_facts.md.
"""
import json, tempfile, itertools, subprocess, sys, os
from pathlib import Path
import numpy as np
from world.understanding import UnderstandingEngine
from world.substrate_memory import SubstrateMemory

# what Michael might teach by sentence, one at a time, in the GUI
SENTENCES = [
    "This is a poodle. A poodle is a dog.",
    "A dog is a mammal.",
    "A mammal is an animal.",
    "A dog can bark.",
    "A salmon is a fish.",
    "A fish is an animal.",
    "A heart is part of a dog.",
]


def gate_threshold(mem, seed):
    cal = [("c1", "isa", "k1"), ("c2", "isa", "k2"), ("c3", "isa", "k3")]
    for (c, r, p) in cal:
        if (c, r, p) not in mem.facts:
            pass
    taught = np.mean([mem.query(c, "isa")[1] for (c, _, _) in cal]) if any(
        f[0] in {"c1", "c2", "c3"} for f in mem.facts) else None
    rng = np.random.default_rng(seed + 321)
    untaught = np.mean([mem.query(f"none_{int(rng.integers(1e9))}", "isa")[1] for _ in range(32)])
    # fall back: use taught-edge sims directly if no calib facts
    if taught is None:
        ts = [mem.query(a, "isa")[1] for (a, r, b) in mem.facts if r == "isa"][:8]
        taught = np.mean(ts) if ts else 0.2
    return float((taught + untaught) / 2.0)


def climb_isa(mem, x, y, gate, max_hops=10):
    cur, seen = x, {x}
    for _ in range(max_hops):
        p, s = mem.query(cur, "isa")
        if p is None or s < gate or p in seen:
            return False
        if p == y:
            return True
        seen.add(p); cur = p
    return False


def run_seed(seed):
    # --- ORIGINAL teaching session (simulating the GUI sentence path) ---
    sm = SubstrateMemory(D=4096, tau=0.12, directed=True)
    eng0 = UnderstandingEngine(seed=seed)
    for s in SENTENCES:
        sm.learn_sentence(s, eng0)
    # add calib facts for the gate
    for (c, r, p) in [("c1", "isa", "k1"), ("c2", "isa", "k2"), ("c3", "isa", "k3")]:
        sm.add_fact(c, r, p)

    d = tempfile.mkdtemp(prefix=f"facts_{seed}_")
    sm.save(d)

    # --- RESTART: load fresh, rebuild engine from the durable corpus ---
    sm2 = SubstrateMemory.load(d)
    eng2 = sm2.rebuild_engine(seed=seed)
    gate = gate_threshold(sm2, seed)

    # question set: is-a multi-hop + has_property + negatives; ground truth = the ORIGINAL engine
    nodes = ["poodle", "dog", "mammal", "animal", "salmon", "fish", "bird"]
    isa_q = list(itertools.permutations(nodes, 2))
    prop_q = [(n, p) for n in nodes for p in ["bark", "swim", "fly"]]

    # J302a: rebuilt engine matches original engine
    a_isa = sum(eng2.is_a(a, b) == eng0.is_a(a, b) for (a, b) in isa_q) / len(isa_q)
    a_prop = sum(eng2.has_property(a, b) == eng0.has_property(a, b) for (a, b) in prop_q) / len(prop_q)
    j302a = (a_isa + a_prop) / 2

    # J302b: substrate store (engine discarded) answers is-a vs original engine
    b_isa = sum(climb_isa(sm2, a, b, gate) == eng0.is_a(a, b) for (a, b) in isa_q) / len(isa_q)

    demo = {"poodle_is_animal": eng2.is_a("poodle", "animal"),
            "poodle_can_bark": eng2.has_property("poodle", "bark"),
            "substrate_poodle_is_animal": climb_isa(sm2, "poodle", "animal", gate),
            "n_sentences": len(sm2.sentences)}
    return {"engine_match": round(j302a, 3), "substrate_isa": round(b_isa, 3), "demo": demo}


def regression(repo):
    r = subprocess.run([sys.executable, "tools/run_jep295_persistent_memory.py"], capture_output=True,
                       text=True, env={**os.environ, "PYTHONPATH": repo})
    return "JEP-295: PASS" in r.stdout


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-302: durable taught FACTS (sentence-teaching survives restart) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: rebuilt-engine match={r['engine_match']} | substrate is-a={r['substrate_isa']} | "
              f"demo={r['demo']}", flush=True)

    # J302c: GUI imports + headless sentence round-trip already exercised via SubstrateMemory above
    try:
        import importlib; importlib.import_module("tools.teach_gui"); j302c = True
    except Exception as ex:
        j302c = False; print("  teach_gui import:", ex, flush=True)
    reg = regression(repo)
    print(f"  GUI import: {j302c} | regression JEP-295: {'PASS' if reg else 'FAIL'}", flush=True)

    J302a = all(R[s]['engine_match'] >= 0.95 for s in seeds)
    J302b = all(R[s]['substrate_isa'] >= 0.90 for s in seeds)
    passed = J302a and J302b and j302c and reg
    print("\n--- VERDICT ---", flush=True)
    print(f"J302a rebuilt engine matches original (>=.95)  : {J302a}", flush=True)
    print(f"J302b substrate store answers is-a (>=.90)     : {J302b}", flush=True)
    print(f"J302c GUI wiring imports                        : {j302c}", flush=True)
    print(f"no-regression: JEP-295 persistence still PASS   : {reg}", flush=True)
    verdict = ("PASS - facts taught by sentence are durable: after restart the engine is rebuilt from the stored "
               "prose AND the substrate holds the bridged facts; both answer correctly") if passed else "NULL/partial"
    print(f"\nJEP-302: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP302"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "J302a": J302a,
                                                  "J302b": J302b, "J302c": j302c, "reg": reg,
                                                  "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
