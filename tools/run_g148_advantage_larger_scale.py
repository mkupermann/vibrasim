"""G148 — does the emerging annealing gap (G147) CROSS the 0.02 threshold at larger scale? Same solvers as
G147, n in {200,280,360}, classification ordering FIXED.

Pre-registered bars in docs/amendments/g148_advantage_larger_scale.md.
"""
import json
from pathlib import Path
import numpy as np
from tools.run_g147_advantage_at_scale import cut, osc_anneal, greedy_correct, sim_anneal


if __name__ == "__main__":
    print("=== G148: annealing vs correct strong greedy at LARGER scale ===", flush=True)
    rng = np.random.default_rng(2)
    ns = [200, 280, 360]
    n_inst = 5
    per_n = {}
    for n in ns:
        gaps, anneal_ratios, grd_ratios, anneal_wins = [], [], [], 0
        osc_v_grd = sa_v_grd = sa_v_osc = 0           # SEPARATED: physical oscillator vs classical SA
        osc_grd_gaps, sa_grd_gaps, insts = [], [], []
        for inst in range(n_inst):
            A = rng.normal(0, 1, (n, n)); W = np.triu(A, 1); W = W + W.T
            og = max(cut(W, osc_anneal(W, seed=sd)) for sd in range(5))
            sa = sim_anneal(W, sweeps=1000, restarts=4, seed=11)
            gc = greedy_correct(W, restarts=60, seed=7)
            sa_long = sim_anneal(W, sweeps=3000, restarts=2, seed=99)
            ref = max(og, sa, gc, sa_long)
            anneal = max(og, sa)
            ar, gr = anneal / ref, gc / ref
            gaps.append(ar - gr); anneal_ratios.append(ar); grd_ratios.append(gr)
            if anneal > gc + 1e-6:
                anneal_wins += 1
            if og > gc + 1e-6:
                osc_v_grd += 1
            if sa > gc + 1e-6:
                sa_v_grd += 1
            if sa > og + 1e-6:
                sa_v_osc += 1
            osc_grd_gaps.append((og - gc) / ref); sa_grd_gaps.append((sa - gc) / ref)
            insts.append(dict(og=og, sa=sa, gc=gc, ref=ref))
            print(f"  n={n:3d} inst {inst}: OSC={og:9.1f} SA={sa:9.1f} GRD={gc:9.1f} REF={ref:9.1f} "
                  f"| anneal_r={ar:.3f} grd_r={gr:.3f} gap={ar-gr:+.3f} "
                  f"| OSC-GRD={(og-gc)/ref:+.3f} SA-GRD={(sa-gc)/ref:+.3f}", flush=True)
        per_n[n] = dict(mean_gap=float(np.mean(gaps)), mean_anneal=float(np.mean(anneal_ratios)),
                        mean_grd=float(np.mean(grd_ratios)), anneal_wins=anneal_wins, n_inst=n_inst,
                        osc_v_grd=osc_v_grd, sa_v_grd=sa_v_grd, sa_v_osc=sa_v_osc,
                        mean_osc_grd_gap=float(np.mean(osc_grd_gaps)), mean_sa_grd_gap=float(np.mean(sa_grd_gaps)),
                        insts=insts)
        print(f"  --> n={n}: mean gap={per_n[n]['mean_gap']:+.3f} | OSC-vs-GRD wins {osc_v_grd}/{n_inst} "
              f"(gap {per_n[n]['mean_osc_grd_gap']:+.3f}) | SA-vs-GRD wins {sa_v_grd}/{n_inst} "
              f"(gap {per_n[n]['mean_sa_grd_gap']:+.3f}) | SA-vs-OSC wins {sa_v_osc}/{n_inst}", flush=True)

    nmax = ns[-1]
    gmax = per_n[nmax]['mean_gap']
    wins_max = per_n[nmax]['anneal_wins']
    # FIXED ordering: advantage first, then plateau, then emerging-still
    if gmax >= 0.02 and wins_max >= 4:
        cls = "ADVANTAGE"
    elif gmax < 0.01:
        cls = "NO_ADVANTAGE"
    else:
        cls = "EMERGING_STILL"

    print("\n--- VERDICT ---", flush=True)
    print(f"  gaps by n: {', '.join(f'{n}:{per_n[n]['mean_gap']:+.3f}(w{per_n[n]['anneal_wins']}/{n_inst})' for n in ns)}", flush=True)
    print(f"  largest n={nmax}: mean gap={gmax:+.3f}, anneal wins {wins_max}/{n_inst}", flush=True)
    if cls == "ADVANTAGE":
        verdict = ("PASS/ADVANTAGE - annealing out-solves strong correct greedy on hard large instances; "
                   "G145's claim RESTORED against a correct baseline. The real niche: annealing for hard combinatorial optimization.")
    elif cls == "NO_ADVANTAGE":
        verdict = "NULL/NO_ADVANTAGE - gap plateaued below 0.01; correct greedy matches annealing even at n=360. Final retraction."
    else:
        verdict = f"PARTIAL/EMERGING_STILL - gap real and growing but in (0.01,0.02) at n={nmax}; pre-register larger n."
    print(f"\nG148: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G148"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"per_n": per_n, "class": cls, "verdict": verdict}, indent=2, default=str))
    print("DONE", flush=True)
