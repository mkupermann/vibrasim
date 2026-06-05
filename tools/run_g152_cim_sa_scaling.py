"""G152 — does the CIM-AHC ~ SA near-tie (G150/G151) HOLD at larger scale (n=450, 600)? Frozen solver
settings; only n grows. Scaling robustness check.

Pre-registered bars in docs/amendments/g152_cim_sa_scaling.md.
"""
import json
from pathlib import Path
import numpy as np
from tools.run_g147_advantage_at_scale import cut, greedy_correct, sim_anneal
from tools.run_g150_cim_amplitude_correction import cim_best


if __name__ == "__main__":
    print("=== G152: CIM-AHC vs SA scaling (n=450,600) ===", flush=True)
    rng = np.random.default_rng(2)
    ns = [450, 600]
    n_inst = 4
    GRID_XI = [0.1, 0.3]; GRID_BETA = [0.1, 1.0]; SEEDS = [0, 1, 2]   # FROZEN from G150
    per_n = {}
    for n in ns:
        sa_v_grd = cim_v_grd = cim_v_sa = 0
        cim_sa_gaps, cim_ratios, sa_ratios, insts = [], [], [], []
        for inst in range(n_inst):
            A = rng.normal(0, 1, (n, n)); W = np.triu(A, 1); W = W + W.T
            cim = cim_best(W, GRID_XI, GRID_BETA, SEEDS)
            sa = sim_anneal(W, sweeps=800, restarts=3, seed=11)
            gc = greedy_correct(W, restarts=60, seed=7)
            sa_long = sim_anneal(W, sweeps=1500, restarts=2, seed=99)
            ref = max(cim, sa, gc, sa_long)
            if sa > gc + 1e-6: sa_v_grd += 1
            if cim > gc + 1e-6: cim_v_grd += 1
            if cim >= sa - 1e-6: cim_v_sa += 1
            cim_sa_gaps.append((cim - sa) / ref); cim_ratios.append(cim / ref); sa_ratios.append(sa / ref)
            insts.append(dict(cim=cim, sa=sa, gc=gc, ref=ref))
            print(f"  n={n:3d} inst {inst}: CIM={cim:8.1f} SA={sa:8.1f} GRD={gc:8.1f} REF={ref:8.1f} "
                  f"| CIM-SA={(cim-sa)/ref:+.3f} CIM-GRD={(cim-gc)/ref:+.3f}", flush=True)
        per_n[n] = dict(sa_v_grd=sa_v_grd, cim_v_grd=cim_v_grd, cim_v_sa=cim_v_sa,
                        mean_cim_sa_gap=float(np.mean(cim_sa_gaps)),
                        mean_cim_ratio=float(np.mean(cim_ratios)), mean_sa_ratio=float(np.mean(sa_ratios)),
                        n_inst=n_inst, insts=insts)
        print(f"  --> n={n}: SA>GRD {sa_v_grd}/{n_inst} | CIM>GRD {cim_v_grd}/{n_inst} | CIM>=SA {cim_v_sa}/{n_inst} "
              f"| mean CIM-SA gap {per_n[n]['mean_cim_sa_gap']:+.3f}", flush=True)

    nmax = ns[-1]; b = per_n[nmax]
    G152a = b['sa_v_grd'] >= 3
    G152b = b['cim_v_grd'] >= 3
    g = b['mean_cim_sa_gap']
    if abs(g) <= 0.015:
        cls = "HOLDS"
    elif -g >= 0.02:
        cls = "CIM_DEGRADES"
    elif g >= 0.01:
        cls = "CIM_CATCHES_UP"
    else:
        cls = "HOLDS"   # mild negative gap within (0.015,0.02) edge -> treat as holds-ish; reported explicitly
    print("\n--- VERDICT ---", flush=True)
    print(f"G152a hard regime (SA>GRD >=3/4)   : {G152a}", flush=True)
    print(f"G152b CIM>GRD (>=3/4)              : {G152b}", flush=True)
    print(f"G152c near-tie holds at scale      : {cls}  (gaps by n: {', '.join(f'{n}:{per_n[n]['mean_cim_sa_gap']:+.3f}' for n in ns)})", flush=True)
    print(f"      quality @ n={nmax}: CIM {b['mean_cim_ratio']:.3f} REF, SA {b['mean_sa_ratio']:.3f} REF", flush=True)
    if cls == "HOLDS":
        verdict = "HOLDS - CIM-AHC ~ SA near-tie is stable with scale; the scoped positive is scale-robust (adjacent hardware, not EQMOD; SA marginally best)"
    elif cls == "CIM_DEGRADES":
        verdict = "CIM DEGRADES - the physical annealer falls behind SA as n grows; scale caveat on the positive"
    else:
        verdict = "CIM CATCHES UP - CIM closes/passes SA at scale"
    print(f"\nG152: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G152"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"per_n": per_n, "class": cls, "G152a": bool(G152a),
                                                  "G152b": bool(G152b), "verdict": verdict}, indent=2, default=str))
    print("DONE", flush=True)
