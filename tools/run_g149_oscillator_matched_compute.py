"""G149 — is the oscillator's weakness (G148) a COMPUTE artifact or fundamental? Give it ~10x budget (same
dynamics/noise schedule, only more of it) and re-test vs correct greedy and SA.

Pre-registered bars in docs/amendments/g149_oscillator_matched_compute.md.
"""
import json
from pathlib import Path
import numpy as np
from tools.run_g147_advantage_at_scale import cut, osc_anneal, greedy_correct, sim_anneal


def osc_best(W, seeds, steps):
    return max(cut(W, osc_anneal(W, steps=steps, seed=sd)) for sd in range(seeds))


if __name__ == "__main__":
    print("=== G149: oscillator with ~10x compute (fairness check) ===", flush=True)
    rng = np.random.default_rng(2)
    ns = [200, 360]
    n_inst = 5
    per_n = {}
    for n in ns:
        ob_base, ob_big, sas, grds, refs = [], [], [], [], []
        big_v_grd = big_v_sa = 0
        big_grd_gaps = []
        for inst in range(n_inst):
            A = rng.normal(0, 1, (n, n)); W = np.triu(A, 1); W = W + W.T
            o_base = osc_best(W, seeds=5, steps=1500)
            o_big = osc_best(W, seeds=15, steps=5000)        # ~10x compute, same dynamics
            sa = sim_anneal(W, sweeps=1000, restarts=4, seed=11)
            gc = greedy_correct(W, restarts=60, seed=7)
            sa_long = sim_anneal(W, sweeps=3000, restarts=2, seed=99)
            ref = max(o_base, o_big, sa, gc, sa_long)
            ob_base.append(o_base); ob_big.append(o_big); sas.append(sa); grds.append(gc); refs.append(ref)
            if o_big > gc + 1e-6:
                big_v_grd += 1
            if o_big > sa + 1e-6:
                big_v_sa += 1
            big_grd_gaps.append((o_big - gc) / ref)
            print(f"  n={n:3d} inst {inst}: OSC_base={o_base:8.1f} OSC_big={o_big:8.1f} SA={sa:8.1f} "
                  f"GRD={gc:8.1f} REF={ref:8.1f} | big-GRD={(o_big-gc)/ref:+.3f} big-SA={(o_big-sa)/ref:+.3f}", flush=True)
        per_n[n] = dict(mean_base=float(np.mean(ob_base)), mean_big=float(np.mean(ob_big)),
                        mean_sa=float(np.mean(sas)), mean_grd=float(np.mean(grds)),
                        big_v_grd=big_v_grd, big_v_sa=big_v_sa,
                        mean_big_grd_gap=float(np.mean(big_grd_gaps)), n_inst=n_inst)
        print(f"  --> n={n}: OSC_big-vs-GRD wins {big_v_grd}/{n_inst} (gap {per_n[n]['mean_big_grd_gap']:+.3f}) "
              f"| OSC_big-vs-SA wins {big_v_sa}/{n_inst} | mean base={per_n[n]['mean_base']:.1f} "
              f"big={per_n[n]['mean_big']:.1f} sa={per_n[n]['mean_sa']:.1f}", flush=True)

    nmax = ns[-1]
    G149a = all(per_n[n]['mean_big'] >= per_n[n]['mean_base'] - 1e-6 for n in ns)
    big = per_n[nmax]
    if big['big_v_grd'] >= 4 and big['mean_big_grd_gap'] >= 0.01:
        cls = "SALVAGED"
    elif big['big_v_grd'] <= 3 and big['mean_big_grd_gap'] < 0.01:
        cls = "ROBUST_NEGATIVE"
    else:
        cls = "MIXED"

    print("\n--- VERDICT ---", flush=True)
    print(f"G149a more compute helps OSC (big>=base) : {G149a}", flush=True)
    print(f"G149b fairness verdict @ n={nmax}        : {cls}  "
          f"(OSC_big vs GRD wins {big['big_v_grd']}/{n_inst}, gap {big['mean_big_grd_gap']:+.3f})", flush=True)
    print(f"G149c OSC_big vs SA @ n={nmax}            : wins {big['big_v_sa']}/{n_inst} "
          f"(SA still ahead if low)", flush=True)
    if cls == "SALVAGED":
        verdict = ("SALVAGED - given fair (10x) compute the oscillator beats correct greedy on hard instances; "
                   "a scoped physical-annealing positive survives (still <= classical SA)")
    elif cls == "ROBUST_NEGATIVE":
        verdict = ("ROBUST-NEGATIVE - even at 10x compute the oscillator ties/loses to trivial correct greedy; "
                   "G148 stands, the substrate's computation niche is closed")
    else:
        verdict = "MIXED - inconclusive at this budget; report and consider further"
    print(f"\nG149: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G149_osc"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"per_n": per_n, "class": cls, "G149a": bool(G149a),
                                                  "verdict": verdict}, indent=2, default=str))
    print("DONE", flush=True)
