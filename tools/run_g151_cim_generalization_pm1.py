"""G151 — does the G150 AHC-CIM finding GENERALIZE to the ±1 (Sherrington-Kirkpatrick) spin-glass family?
All solver settings FROZEN from G150; only the instance distribution changes (Gaussian -> +-1). Generalization
check, not threshold-chasing.

Pre-registered bars in docs/amendments/g151_cim_generalization_pm1.md.
"""
import json
from pathlib import Path
import numpy as np
from tools.run_g147_advantage_at_scale import cut, osc_anneal, greedy_correct, sim_anneal
from tools.run_g150_cim_amplitude_correction import cim_best


def pm1_instance(rng, n):
    A = rng.integers(0, 2, size=(n, n)) * 2 - 1   # +-1
    W = np.triu(A, 1).astype(np.float64)
    return W + W.T


if __name__ == "__main__":
    print("=== G151: does AHC-CIM (G150) generalize to +-1 / SK spin glass? ===", flush=True)
    rng = np.random.default_rng(2)
    ns = [200, 360]
    n_inst = 5
    GRID_XI = [0.1, 0.3]; GRID_BETA = [0.1, 1.0]; SEEDS = [0, 1, 2]   # FROZEN from G150
    per_n = {}
    for n in ns:
        sa_v_grd = cim_v_sa = cim_v_grd = cim_v_naive = 0
        cim_sa_gaps, insts = [], []
        for inst in range(n_inst):
            W = pm1_instance(rng, n)
            naive = max(cut(W, osc_anneal(W, seed=sd)) for sd in range(5))
            cim = cim_best(W, GRID_XI, GRID_BETA, SEEDS)
            sa = sim_anneal(W, sweeps=1000, restarts=4, seed=11)
            gc = greedy_correct(W, restarts=60, seed=7)
            sa_long = sim_anneal(W, sweeps=3000, restarts=2, seed=99)
            ref = max(naive, cim, sa, gc, sa_long)
            if sa > gc + 1e-6: sa_v_grd += 1
            if cim >= sa - 1e-6: cim_v_sa += 1
            if cim > gc + 1e-6: cim_v_grd += 1
            if cim >= naive - 1e-6: cim_v_naive += 1
            cim_sa_gaps.append((cim - sa) / ref)
            insts.append(dict(naive=naive, cim=cim, sa=sa, gc=gc, ref=ref))
            print(f"  n={n:3d} inst {inst}: naive={naive:8.1f} CIM={cim:8.1f} SA={sa:8.1f} GRD={gc:8.1f} "
                  f"REF={ref:8.1f} | CIM-SA={(cim-sa)/ref:+.3f} CIM-GRD={(cim-gc)/ref:+.3f}", flush=True)
        per_n[n] = dict(sa_v_grd=sa_v_grd, cim_v_sa=cim_v_sa, cim_v_grd=cim_v_grd, cim_v_naive=cim_v_naive,
                        mean_cim_sa_gap=float(np.mean(cim_sa_gaps)), n_inst=n_inst, insts=insts)
        print(f"  --> n={n}: SA>GRD {sa_v_grd}/{n_inst} | CIM>=SA {cim_v_sa}/{n_inst} "
              f"(gap {per_n[n]['mean_cim_sa_gap']:+.3f}) | CIM>GRD {cim_v_grd}/{n_inst} | "
              f"CIM>=naive {cim_v_naive}/{n_inst}", flush=True)

    nmax = ns[-1]; b = per_n[nmax]
    G151a = b['sa_v_grd'] >= 4
    G151c = b['cim_v_naive'] >= 3
    if b['cim_v_grd'] >= 4 and abs(b['mean_cim_sa_gap']) <= 0.01:
        cls = "GENERALIZES"
    elif b['cim_v_grd'] <= 3 or -b['mean_cim_sa_gap'] >= 0.02:
        cls = "FAMILY_SPECIFIC"
    else:
        cls = "PARTIAL"

    print("\n--- VERDICT ---", flush=True)
    print(f"G151a hard regime (SA>GRD >=4/5)      : {G151a}", flush=True)
    print(f"G151b generalizes to +-1             : {cls}  (CIM>GRD {b['cim_v_grd']}/5, CIM>=SA {b['cim_v_sa']}/5, mean CIM-SA {b['mean_cim_sa_gap']:+.3f})", flush=True)
    print(f"G151c AHC helps vs naive (>=3/5)      : {G151c}  (CIM>=naive {b['cim_v_naive']}/5)", flush=True)
    if cls == "GENERALIZES":
        verdict = "GENERALIZES - AHC-CIM beats local search & ~ties SA on +-1 too; the G150 scoped positive is robust across both canonical hard families (still adjacent hardware, not EQMOD; SA marginally best)"
    elif cls == "FAMILY_SPECIFIC":
        verdict = "FAMILY-SPECIFIC - the G150 result does not carry to +-1; the physical-annealer edge is ensemble-fragile"
    else:
        verdict = "PARTIAL - mixed on +-1; report as inconclusive"
    print(f"\nG151: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G151"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"per_n": per_n, "class": cls, "G151a": bool(G151a),
                                                  "G151c": bool(G151c), "verdict": verdict}, indent=2, default=str))
    print("DONE", flush=True)
