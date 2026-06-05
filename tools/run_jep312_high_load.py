"""JEP-312 — high-load ceiling: push routing past JEP-307's ~900 facts to find the true ceiling."""
import json
from pathlib import Path
import numpy as np
import tools.run_jep306_integrated_scale as S


def edge_gate(mem, seed):
    edges = [(a, b) for (a, r, b) in mem.facts if r == "isa"]
    rng = np.random.default_rng(seed)
    samp = [edges[i] for i in rng.choice(len(edges), min(40, len(edges)), replace=False)] if edges else []
    t = np.mean([mem.query(a, "isa")[1] for (a, b) in samp]) if samp else 0.2
    u = np.mean([mem.query(f"none_{int(rng.integers(1e9))}", "isa")[1] for _ in range(40)])
    return float((t + u) / 2)


def run_at(n, seed):
    parent, props, not_props, concepts = S.build_graph(n, 3, seed)
    mem = S.build_store(parent, props, not_props)
    g = edge_gate(mem, seed)
    isa, prop = S.score(mem, parent, props, not_props, concepts, seed, g)
    return len(mem.facts), len(mem.modules), float(isa), float(prop)


if __name__ == "__main__":
    seeds = [0, 7]; Ns = [500, 1000, 2000, 4000]
    curve = {s: {} for s in seeds}
    for s in seeds:
        for n in Ns:
            nf, nm, isa, prop = run_at(n, s)
            integ = round((isa + prop) / 2, 3)
            curve[s][n] = {"facts": nf, "modules": nm, "isa": round(isa, 3), "prop": round(prop, 3), "integrated": integ}
            print(f"JEP312 seed {s} N~{n}: facts={nf} modules={nm} is-a={round(isa,3)} prop={round(prop,3)} "
                  f"integrated={integ}", flush=True)
    J312a = all(curve[s][2000]["integrated"] >= 0.90 for s in seeds)
    nstar = {}
    for s in seeds:
        below = [n for n in Ns if curve[s][n]["integrated"] < 0.90]
        nstar[s] = below[0] if below else f">{Ns[-1]}"
    print(f"JEP-312: {'PASS' if J312a else 'NULL/partial'} | integrated>=.90 to N=2000={J312a} | N*(<.90)={nstar}",
          flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP312"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"curve": curve, "J312a": J312a,
                                                  "nstar": {str(k): str(v) for k, v in nstar.items()},
                                                  "passed": J312a}, default=str))
    print("DONE", flush=True)
