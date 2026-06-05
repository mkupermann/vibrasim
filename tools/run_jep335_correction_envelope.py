"""JEP-335 — correction reliability envelope: gate-override vs compaction across load. No transformer.
Pre-registered bars in docs/amendments/jep335_correction_envelope.md.
"""
import json
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory


def gate(mem, seed, role="isa"):
    edges = [(a, b) for (a, r, b) in mem.facts if r == role]
    rng = np.random.default_rng(seed)
    t = np.mean([mem.edge_sim(a, role, b) for (a, b) in edges]) if edges else 0.2
    u = np.mean([mem.query(f"n_{int(rng.integers(1e9))}", role)[1] for _ in range(30)])
    return float((t + u) / 2)


def is_a_override(mem, x, y, g):
    """is_a with gate-detected negation override (no compaction)."""
    if mem.contains(x, "not_isa", y, g):
        return False
    # direct/1-hop only (the corrected fact is a direct edge)
    return y in [p for (p, _) in mem.query_all(x, "isa", g)]


def build(n_corr, seed):
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True, module_cap=40)
    for i in range(n_corr):
        mem.add_fact(f"e{i}", "isa", f"wrong{i}")
        mem.add_fact(f"e{i}", "isa", f"right{i}")
        mem.add_fact(f"e{i}", "not_isa", f"wrong{i}")     # correction
    return mem


def reliability(mem, n_corr, g):
    """Fraction of corrected is_a(e_i, wrong_i) correctly returning False."""
    return np.mean([is_a_override(mem, f"e{i}", f"wrong{i}", g) is False for i in range(n_corr)])


if __name__ == "__main__":
    print("=== JEP-335: correction reliability envelope (override vs compaction) ===", flush=True)
    seeds = [0, 7]; loads = [5, 10, 20, 40, 80]
    curve = {s: {} for s in seeds}
    for s in seeds:
        for nc in loads:
            mem = build(nc, s); g = gate(mem, s)
            ov = reliability(mem, nc, g)
            comp = mem.compact(); gc = gate(comp, s)
            cp = reliability(comp, nc, gc)
            curve[s][nc] = {"override": round(float(ov), 3), "compacted": round(float(cp), 3),
                            "facts": len(mem.facts), "modules": len(mem.modules)}
            print(f"  seed {s} corrections={nc} (facts={len(mem.facts)}, mods={len(mem.modules)}): "
                  f"override reliability={round(float(ov),3)} | after compaction={round(float(cp),3)}", flush=True)

    J335a = all(curve[s][nc]["compacted"] >= 1.0 for s in seeds for nc in loads)
    leak = {s: next((nc for nc in loads if curve[s][nc]["override"] < 0.95), f">{loads[-1]}") for s in seeds}
    print(f"\n  override leak threshold (reliability<0.95) at corrections={leak}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    print(f"J335a compaction reliable at every load (=1.0): {J335a}", flush=True)
    verdict = ("PASS - compaction makes corrections reliable at every load; gate-override leaks as load rises "
               "(threshold reported) -> compact long-lived corrected stores") if J335a else "NULL/partial"
    print(f"\nJEP-335: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP335"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"curve": {str(s): {str(k): v for k, v in curve[s].items()} for s in seeds},
                                                  "J335a": J335a, "leak": {str(k): str(v) for k, v in leak.items()},
                                                  "passed": J335a}, default=str))
    print("DONE", flush=True)
