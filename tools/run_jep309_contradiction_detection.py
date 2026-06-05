"""JEP-309 — contradiction detection in the durable substrate, distinguished from defeasible exceptions. Generated
ground truth (engine resolves conflicts silently). No transformer. Pre-registered bars in
docs/amendments/jep309_contradiction_detection.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory

CALIB = [("z1", "isa", "w1"), ("z2", "isa", "w2"), ("z3", "isa", "w3")]


def gate_threshold(mem, seed):
    taught = np.mean([mem.query(c, "isa")[1] for (c, _, _) in CALIB])
    rng = np.random.default_rng(seed + 321)
    untaught = np.mean([mem.query(f"none_{int(rng.integers(1e9))}", "isa")[1] for _ in range(32)])
    return float((taught + untaught) / 2.0)


def build(seed):
    """Consistent taxonomy + properties + EXCEPTIONS (must NOT flag) + injected CONTRADICTIONS (must flag)."""
    rng = np.random.default_rng(seed)
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    # consistent taxonomy
    isa = [("poodle", "dog"), ("dog", "mammal"), ("mammal", "animal"), ("robin", "bird"),
           ("bird", "animal"), ("penguin", "bird"), ("salmon", "fish"), ("fish", "animal")]
    for c, p in isa:
        mem.add_fact(c, "isa", p)
    # consistent properties (some inherited)
    for a, p in [("bird", "fly"), ("dog", "bark"), ("fish", "swim"), ("mammal", "breathe")]:
        mem.add_fact(a, "hasprop", p)
    # EXCEPTIONS (consistent, defeasible): inherits a prop but has explicit negative on the SPECIFIC node
    exceptions = [("penguin", "fly")]                 # penguin inherits fly from bird, but cannot fly
    for x, p in exceptions:
        mem.add_fact(x, "not_hasprop", p)             # NOT a direct hasprop on penguin -> exception, not conflict
    # INJECTED CONTRADICTIONS (must be flagged): direct double-assertion on the SAME node
    contradictions = [("robin", "prop", "swim"), ("dog", "prop", "growl")]
    for (x, _, p) in contradictions:
        mem.add_fact(x, "hasprop", p); mem.add_fact(x, "not_hasprop", p)
    isa_contra = [("salmon", "isa", "bird")]          # salmon is a bird AND not a bird (direct)
    for (x, _, y) in isa_contra:
        mem.add_fact(x, "isa", y); mem.add_fact(x, "not_isa", y)
    for (c, r, p) in CALIB:
        mem.add_fact(c, r, p)
    truth = {(x, "hasprop", p) for (x, _, p) in contradictions} | {(x, "isa", y) for (x, _, y) in isa_contra}
    return mem, truth, set(exceptions)


def run_seed(seed):
    mem, truth, exceptions = build(seed)
    d = tempfile.mkdtemp(prefix=f"conf_{seed}_")
    mem.save(d)
    mem2 = SubstrateMemory.load(d)
    gate = gate_threshold(mem2, seed)

    flagged = set(mem2.detect_conflicts(gate))
    tp = len(flagged & truth); fp = len(flagged - truth); fn = len(truth - flagged)
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0

    # J309b: exceptions must NOT be flagged
    exc_flagged = any((x, "hasprop", p) in flagged or (x, "not_hasprop", p) in flagged for (x, p) in exceptions)

    # J309c: persists (re-load again)
    mem3 = SubstrateMemory.load(d); gate3 = gate_threshold(mem3, seed)
    persist = set(mem3.detect_conflicts(gate3)) == flagged

    return {"precision": round(precision, 3), "recall": round(recall, 3), "n_flagged": len(flagged),
            "n_truth": len(truth), "exception_flagged": bool(exc_flagged), "persist_ok": bool(persist),
            "flagged": sorted(flagged)}


def regression(repo):
    r = subprocess.run([sys.executable, "tools/run_jep305_negation_exceptions.py"], capture_output=True, text=True,
                       env={**os.environ, "PYTHONPATH": repo})
    return "JEP-305: PASS" in r.stdout


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-309: contradiction detection (vs defeasible exceptions) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: precision={r['precision']} recall={r['recall']} ({r['n_flagged']}/{r['n_truth']}) | "
              f"exception-flagged={r['exception_flagged']} | persists={r['persist_ok']}", flush=True)
        print(f"           flagged={r['flagged']}", flush=True)
    reg = regression(repo)
    print(f"  regression JEP-305: {'PASS' if reg else 'FAIL'}", flush=True)

    J309a = all(R[s]['precision'] >= 0.95 and R[s]['recall'] >= 0.95 for s in seeds)
    J309b = all(not R[s]['exception_flagged'] for s in seeds)
    J309c = all(R[s]['persist_ok'] for s in seeds)
    passed = J309a and J309b and J309c and reg
    print("\n--- VERDICT ---", flush=True)
    print(f"J309a exact contradiction detection (P=R=1): {J309a}", flush=True)
    print(f"J309b exception NOT flagged as contradiction: {J309b}", flush=True)
    print(f"J309c persists across reload                 : {J309c}", flush=True)
    print(f"no-regression: JEP-305 still PASS            : {reg}", flush=True)
    verdict = ("PASS - the substrate flags genuine contradictions (direct double-assertion) while leaving "
               "defeasible exceptions alone, durably") if passed else "NULL/partial"
    print(f"\nJEP-309: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP309"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "reg": reg,
                                                  "J309a": J309a, "J309b": J309b, "J309c": J309c,
                                                  "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
