"""JEP-308 — abductive 'why?' reasoning in the durable substrate via stored inverse causal edges. abduce(effect)
= reverse causal lookup, matching the engine. No transformer. Pre-registered bars in
docs/amendments/jep308_abduction.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
import numpy as np
from world.understanding import UnderstandingEngine
from world.substrate_memory import SubstrateMemory

CORPUS = (
    "Smoking causes cancer. Radiation causes cancer. Asbestos causes cancer. A virus causes infection. "
    "Bacteria causes infection. Stress causes headache. Poor diet causes headache. Dehydration causes headache. "
    "A storm causes flooding. Heavy rain causes flooding."
)
CALIB = [("z1", "caused_by", "w1"), ("z2", "caused_by", "w2"), ("z3", "caused_by", "w3")]


def gate_threshold(mem, seed):
    taught = np.mean([mem.query(c, "caused_by")[1] for (c, _, _) in CALIB])
    rng = np.random.default_rng(seed + 321)
    untaught = np.mean([mem.query(f"none_{int(rng.integers(1e9))}", "caused_by")[1] for _ in range(32)])
    return float((taught + untaught) / 2.0)


def build(eng):
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for cause, effs in dict(eng.causes).items():
        for eff in effs:
            mem.add_fact(cause, "causes", eff)          # forward
            mem.add_fact(eff, "caused_by", cause)       # inverse (enables abduction)
    for (c, r, p) in CALIB:
        mem.add_fact(c, r, p)
    return mem


def sub_abduce(mem, effect, gate):
    return {c for (c, _) in mem.query_all(effect, "caused_by", gate)}


def run_seed(seed):
    eng = UnderstandingEngine(seed=seed)
    eng.read(CORPUS)
    effects = sorted({e for effs in dict(eng.causes).values() for e in effs})
    causes = sorted(dict(eng.causes).keys())

    mem = build(eng)
    d = tempfile.mkdtemp(prefix=f"abd_{seed}_")
    mem.save(d)
    mem2 = SubstrateMemory.load(d)
    gate = gate_threshold(mem2, seed)

    # J308a: abduced set == engine set (restrict to real cause vocabulary)
    exact = []
    for e in effects:
        sub = {c for c in sub_abduce(mem2, e, gate) if c in causes}
        eng_set = set(eng.abduce(e))
        exact.append(1.0 if sub == eng_set else 0.0)
    set_acc = float(np.mean(exact))

    # J308b: non-effect -> empty; forward causal intact
    non_eff = {c for c in sub_abduce(mem2, "sunburn", gate) if c in causes}
    fwd_ok = all(mem2.contains(cause, "causes", eff, gate)
                 for cause, effs in dict(eng.causes).items() for eff in effs)
    nofalse = (non_eff == set(eng.abduce("sunburn"))) and fwd_ok

    # J308c: persists
    mem3 = SubstrateMemory.load(d); gate3 = gate_threshold(mem3, seed)
    persist = all(sub_abduce(mem3, e, gate3) == sub_abduce(mem2, e, gate) for e in effects)

    demo = {e: sorted(c for c in sub_abduce(mem2, e, gate) if c in causes) for e in effects}
    return {"set_acc": round(set_acc, 3), "nofalse_ok": bool(nofalse), "persist_ok": bool(persist),
            "n_effects": len(effects), "demo": demo}


def regression(repo):
    r = subprocess.run([sys.executable, "tools/run_jep307_module_routing.py"], capture_output=True, text=True,
                       env={**os.environ, "PYTHONPATH": repo})
    return "JEP-307: PASS" in r.stdout


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-308: abductive 'why?' reasoning in the durable substrate ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: abduce-set acc={r['set_acc']} ({r['n_effects']} effects) | no-false={r['nofalse_ok']} "
              f"| persists={r['persist_ok']}", flush=True)
        print(f"           demo={r['demo']}", flush=True)
    reg = regression(repo)
    print(f"  regression JEP-307: {'PASS' if reg else 'FAIL'}", flush=True)

    J308a = all(R[s]['set_acc'] >= 0.95 for s in seeds)
    J308b = all(R[s]['nofalse_ok'] for s in seeds)
    J308c = all(R[s]['persist_ok'] for s in seeds)
    passed = J308a and J308b and J308c and reg
    print("\n--- VERDICT ---", flush=True)
    print(f"J308a abduction matches engine (>=.95): {J308a}", flush=True)
    print(f"J308b no hallucinated cause + forward intact: {J308b}", flush=True)
    print(f"J308c persists across reload                : {J308c}", flush=True)
    print(f"no-regression: JEP-307 still PASS           : {reg}", flush=True)
    verdict = ("PASS - the substrate abduces causes (reverse 'why?' lookup) via stored inverse edges, matching the "
               "engine over the persistent store, multi-cause included") if passed else "NULL/partial"
    print(f"\nJEP-308: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP308"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "reg": reg,
                                                  "J308a": J308a, "J308b": J308b, "J308c": J308c,
                                                  "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
