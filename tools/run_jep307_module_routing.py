"""JEP-307 — module-aware routing fixes multi-hop reasoning at scale (the JEP-306 NULL). Re-runs the scale sweep
with routing + an edge-calibrated gate, and checks no-regression on directed/DAG/negation. No transformer.

Pre-registered bars in docs/amendments/jep307_module_routing.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
import numpy as np
import tools.run_jep306_integrated_scale as S
from world.substrate_memory import SubstrateMemory


def edge_gate(mem, seed):
    edges = [(a, b) for (a, r, b) in mem.facts if r == "isa"]
    rng = np.random.default_rng(seed)
    samp = [edges[i] for i in rng.choice(len(edges), min(40, len(edges)), replace=False)] if edges else []
    taught = np.mean([mem.query(a, "isa")[1] for (a, b) in samp]) if samp else 0.2
    untaught = np.mean([mem.query(f"none_{int(rng.integers(1e9))}", "isa")[1] for _ in range(40)])
    return float((taught + untaught) / 2.0)


def run_at(n, seed):
    parent, props, not_props, concepts = S.build_graph(n, 3, seed)
    mem = S.build_store(parent, props, not_props)        # uses SubstrateMemory (now with routing)
    gate = edge_gate(mem, seed)
    isa, prop = S.score(mem, parent, props, not_props, concepts, seed, gate)
    return mem, parent, props, not_props, concepts, gate, float(isa), float(prop)


def regression(repo):
    outs = {}
    for name, script in [("298", "run_jep298_directed_binding"), ("303", "run_jep303_dag_taxonomies"),
                         ("305", "run_jep305_negation_exceptions")]:
        r = subprocess.run([sys.executable, f"tools/{script}.py"], capture_output=True, text=True,
                           env={**os.environ, "PYTHONPATH": repo})
        outs[name] = f"JEP-{name}: PASS" in r.stdout
    return outs


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-307: module-aware routing -> multi-hop at scale ===", flush=True)
    seeds = [0, 7]
    Ns = [50, 100, 200, 400, 800]
    curve = {s: {} for s in seeds}
    for s in seeds:
        for n in Ns:
            mem, parent, props, not_props, concepts, gate, isa, prop = run_at(n, s)
            curve[s][n] = {"n_facts": len(mem.facts), "modules": len(mem.modules),
                           "isa": round(isa, 3), "prop": round(prop, 3), "integrated": round((isa + prop) / 2, 3)}
            print(f"  seed {s} N~{n}: facts={len(mem.facts)} modules={len(mem.modules)} | is-a={round(isa,3)} "
                  f"prop={round(prop,3)} integrated={round((isa+prop)/2,3)}", flush=True)

    # persistence at N=200
    persist = {}
    for s in seeds:
        mem, parent, props, not_props, concepts, gate, isa0, prop0 = run_at(200, s)
        d = tempfile.mkdtemp(prefix=f"route_{s}_"); mem.save(d)
        mem2 = SubstrateMemory.load(d); g2 = edge_gate(mem2, s)
        isa1, prop1 = S.score(mem2, parent, props, not_props, concepts, s, g2)
        persist[s] = abs((isa0 + prop0) / 2 - (isa1 + prop1) / 2) <= 0.01

    reg = regression(repo)
    print(f"  regression: {reg}", flush=True)

    J307a = all(curve[s][200]["integrated"] >= 0.90 and curve[s][800]["isa"] >= 0.85 for s in seeds)
    J307c = all(persist[s] for s in seeds) and all(reg.values())
    passed = J307a and J307c
    print("\n--- VERDICT ---", flush=True)
    print(f"J307a integrated>=.90 @N=200 AND is-a>=.85 @N=800: {J307a}", flush=True)
    print(f"J307c persists (+/-.01) + no regression (298/303/305): {J307c}", flush=True)
    verdict = ("PASS - module-aware routing removes cross-module hijacking; multi-hop chains now scale with growth "
               "where JEP-306 collapsed") if passed else "NULL/partial - see curve"
    print(f"\nJEP-307: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP307"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"curve": curve, "persist": persist, "reg": reg,
                                                  "J307a": J307a, "J307c": J307c, "passed": passed},
                                                 indent=2, default=str))
    print("DONE", flush=True)
