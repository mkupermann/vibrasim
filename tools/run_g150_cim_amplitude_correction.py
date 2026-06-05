"""G150 — does the textbook CIM amplitude-heterogeneity correction (AHC; Leleu/Yamamoto 2019) close the
oscillator<->SA gap that G146-G149 found for the naive phase-only oscillator? Established method, named as
such. Same hard instances as G148.

Pre-registered bars in docs/amendments/g150_cim_amplitude_correction.md.
"""
import json
from pathlib import Path
import numpy as np
from tools.run_g147_advantage_at_scale import cut, osc_anneal, greedy_correct, sim_anneal


def cim_ahc(W, xi, beta, seed, steps=1500, dt=0.05, p_max=2.0, a=1.0):
    """Amplitude-heterogeneity-corrected CIM (Leleu 2019). Minimizes Ising energy with J=-W/sqrt(n);
    for MAX-CUT that maximizes the cut. Returns a {+-1} spin vector."""
    n = W.shape[0]
    rng = np.random.default_rng(seed)
    J = -W / np.sqrt(n)
    x = 0.01 * rng.standard_normal(n)
    e = np.ones(n)
    for t in range(steps):
        p = p_max * (t / steps)
        mvm = J @ x
        x = x + dt * ((p - 1.0 - x * x) * x + xi * e * mvm)
        e = e + dt * (-beta * (x * x - a) * e)
        np.clip(x, -3.0, 3.0, out=x)
        np.clip(e, 0.0, 10.0, out=e)
    s = np.where(x >= 0, 1, -1)
    return s


def cim_best(W, grid_xi, grid_beta, seeds):
    best = -1e9
    for xi in grid_xi:
        for beta in grid_beta:
            for sd in seeds:
                best = max(best, cut(W, cim_ahc(W, xi, beta, seed=sd)))
    return best


if __name__ == "__main__":
    print("=== G150: CIM amplitude-heterogeneity correction (AHC) vs SA ===", flush=True)
    rng = np.random.default_rng(2)
    ns = [200, 360]
    n_inst = 5
    GRID_XI = [0.1, 0.3]; GRID_BETA = [0.1, 1.0]; SEEDS = [0, 1, 2]   # PRE-REGISTERED, frozen
    per_n = {}
    for n in ns:
        sa_v_grd = cim_v_sa = cim_v_grd = cim_v_naive = 0
        cim_sa_gaps, insts = [], []
        for inst in range(n_inst):
            A = rng.normal(0, 1, (n, n)); W = np.triu(A, 1); W = W + W.T
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
    G150a = b['sa_v_grd'] >= 4
    G150c = b['cim_v_naive'] >= 3
    if b['cim_v_sa'] >= 4 and b['mean_cim_sa_gap'] >= -0.01:
        cls = "CLOSED"
    elif (b['n_inst'] - b['cim_v_sa']) >= 4 and -b['mean_cim_sa_gap'] >= 0.01:
        cls = "NOT_CLOSED"
    else:
        cls = "PARTIAL"

    print("\n--- VERDICT ---", flush=True)
    print(f"G150a hard regime (SA>GRD >=4/5)      : {G150a}", flush=True)
    print(f"G150b AHC closes gap to SA            : {cls}  (CIM>=SA {b['cim_v_sa']}/5, mean CIM-SA {b['mean_cim_sa_gap']:+.3f})", flush=True)
    print(f"G150c AHC helps vs naive (>=3/5)      : {G150c}  (CIM>=naive {b['cim_v_naive']}/5)", flush=True)
    print(f"      (CIM vs correct greedy @ n={nmax}: {b['cim_v_grd']}/5)", flush=True)
    if cls == "CLOSED":
        verdict = "CLOSED - the AHC-corrected CIM is competitive with classical SA; the oscillator paradigm is rehabilitated (G145's weakness was naive dynamics)"
    elif cls == "NOT_CLOSED":
        verdict = "NOT-CLOSED - even the textbook AHC-corrected oscillator stays behind classical SA; the weakness is paradigm-deep (strengthens G148/G149)"
    else:
        verdict = "PARTIAL - AHC-CIM mixed vs SA; report as inconclusive"
    print(f"\nG150: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G150"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"per_n": per_n, "class": cls, "G150a": bool(G150a),
                                                  "G150c": bool(G150c), "verdict": verdict,
                                                  "grid": {"xi": GRID_XI, "beta": GRID_BETA, "seeds": SEEDS}},
                                                 indent=2, default=str))
    print("DONE", flush=True)
