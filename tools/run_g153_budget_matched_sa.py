"""G153 — resolve the one open caveat in the G150-G152 positive: was the n=600 'CIM>SA' a budget artifact?
Give SA a GENEROUS (numba-accelerated) budget at n=450,600 and see whether it re-takes the lead vs the
frozen-grid CIM. Fairness control (like G149), not fishing.

Pre-registered bars in docs/amendments/g153_budget_matched_sa.md.
"""
import json
from pathlib import Path
import numpy as np
from numba import njit
from tools.run_g147_advantage_at_scale import cut, greedy_correct, sim_anneal
from tools.run_g150_cim_amplitude_correction import cim_best


@njit(cache=True)
def _sa_numba(W, sweeps, restarts, T0, T1, seed):
    n = W.shape[0]
    np.random.seed(seed)
    best = -1e18
    ratio = T1 / T0
    for r in range(restarts):
        s = np.where(np.random.random(n) < 0.5, -1.0, 1.0)
        h = W @ s
        for sw in range(sweeps):
            T = T0 * ratio ** (sw / sweeps)
            order = np.random.permutation(n)
            for k in range(n):
                i = order[k]
                dcut = s[i] * h[i]
                if dcut > 0.0 or np.random.random() < np.exp(dcut / T):
                    c = -2.0 * s[i]
                    for j in range(n):
                        h[j] += c * W[j, i]
                    s[i] = -s[i]
        # cut = 0.25 * sum W_ij (1 - s_i s_j) = 0.25*(sumW - s^T W s)
        e = 0.0
        for i in range(n):
            e += s[i] * h[i]
        cutv = 0.25 * (W.sum() - e)
        if cutv > best:
            best = cutv
    return best


def sa_generous(W, seed=11):
    return float(_sa_numba(W.astype(np.float64), 4000, 8, 4.0, 0.01, seed))


if __name__ == "__main__":
    print("=== G153: budget-matched (generous, numba) SA vs frozen-grid CIM ===", flush=True)
    rng = np.random.default_rng(2)
    ns = [450, 600]
    n_inst = 4
    GRID_XI = [0.1, 0.3]; GRID_BETA = [0.1, 1.0]; SEEDS = [0, 1, 2]
    # warm up numba on a tiny instance so JIT time isn't counted as a hang
    _ = sa_generous(np.zeros((4, 4)))
    per_n = {}
    for n in ns:
        sagen_v_cim = cim_v_sagen = sagen_v_samod = 0
        gaps, insts = [], []
        for inst in range(n_inst):
            A = rng.normal(0, 1, (n, n)); W = np.triu(A, 1); W = W + W.T
            cim = cim_best(W, GRID_XI, GRID_BETA, SEEDS)
            sa_mod = sim_anneal(W, sweeps=800, restarts=3, seed=11)   # G152 modest SA
            sa_gen = sa_generous(W, seed=11)                          # generous numba SA
            gc = greedy_correct(W, restarts=60, seed=7)
            ref = max(cim, sa_gen, sa_mod, gc)
            if sa_gen > cim + 1e-6: sagen_v_cim += 1
            if cim >= sa_gen - 1e-6: cim_v_sagen += 1
            if sa_gen > sa_mod + 1e-6: sagen_v_samod += 1
            gaps.append((sa_gen - cim) / ref)
            insts.append(dict(cim=cim, sa_gen=sa_gen, sa_mod=sa_mod, gc=gc, ref=ref))
            print(f"  n={n:3d} inst {inst}: CIM={cim:8.1f} SA_gen={sa_gen:8.1f} SA_mod={sa_mod:8.1f} "
                  f"GRD={gc:8.1f} | SAgen-CIM={(sa_gen-cim)/ref:+.3f}", flush=True)
        per_n[n] = dict(sagen_v_cim=sagen_v_cim, cim_v_sagen=cim_v_sagen, sagen_v_samod=sagen_v_samod,
                        mean_sagen_cim_gap=float(np.mean(gaps)), n_inst=n_inst, insts=insts)
        print(f"  --> n={n}: SA_gen>CIM {sagen_v_cim}/{n_inst} | CIM>=SA_gen {cim_v_sagen}/{n_inst} | "
              f"SA_gen>SA_mod {sagen_v_samod}/{n_inst} | mean SAgen-CIM {per_n[n]['mean_sagen_cim_gap']:+.3f}", flush=True)

    nmax = ns[-1]; b = per_n[nmax]
    G153a = b['sagen_v_samod'] >= 3
    g = b['mean_sagen_cim_gap']
    if b['sagen_v_cim'] >= 3 and g >= 0.005:
        cls = "SA_BEST_AT_MATCH"
    elif b['cim_v_sagen'] >= 2 and abs(g) <= 0.005:
        cls = "CIM_GENUINELY_COMPETITIVE"
    else:
        cls = "MIXED"
    print("\n--- VERDICT ---", flush=True)
    print(f"G153a generous SA helps (>=3/4)      : {G153a}  (SA_gen>SA_mod {b['sagen_v_samod']}/4)", flush=True)
    print(f"G153b budget-matched resolution       : {cls}  (SA_gen>CIM {b['sagen_v_cim']}/4, mean SAgen-CIM {g:+.3f})", flush=True)
    if cls == "SA_BEST_AT_MATCH":
        verdict = "SA BEST AT MATCH - the n=600 'CIM>SA' was a budget artifact; with a generous budget SA re-takes the lead. Confirms the G152 caveat; SA is marginally best at matched budget."
    elif cls == "CIM_GENUINELY_COMPETITIVE":
        verdict = "CIM GENUINELY COMPETITIVE - CIM holds even vs a generous SA; the near-tie is real, not a budget fluke."
    else:
        verdict = "MIXED - budget-matched CIM vs SA inconclusive."
    print(f"\nG153: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G153"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"per_n": per_n, "class": cls, "G153a": bool(G153a),
                                                  "verdict": verdict}, indent=2, default=str))
    print("DONE", flush=True)
