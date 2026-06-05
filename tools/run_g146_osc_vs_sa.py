"""G146 — validate G145 (oscillator-Ising, the programme's lone positive claim) against the PROPER peer:
simulated annealing, plus a sign-audited greedy. Same 8 hard frustrated MAX-CUT instances as G145.

Pre-registered bars in docs/amendments/g146_oscillator_vs_simulated_annealing.md.
"""
import numpy as np


def cut(W, s):
    return 0.25 * float(np.sum(W * (1 - np.outer(s, s))))


# --- OSC: oscillator-anneal, G145 verbatim --------------------------------------------------------
def osc_anneal(W, steps=1500, dt=0.03, seed=0):
    n = W.shape[0]; rng = np.random.default_rng(seed)
    th = rng.uniform(0, 2 * np.pi, n)
    for t in range(steps):
        frac = t / steps
        noise = (1.0 - frac) * rng.normal(0, 1.2, n)
        diff = th[:, None] - th[None, :]
        dth = np.sum(W * np.sin(diff), axis=1) - np.sin(2 * th) * frac + noise
        th = (th + dt * dth) % (2 * np.pi)
    return np.where(np.cos(th) >= 0, 1, -1)


# --- GRD145: G145's greedy verbatim (reproduce) ---------------------------------------------------
def greedy_g145(W, restarts=25, seed=7):
    n = W.shape[0]; rng = np.random.default_rng(seed); best = -1e9
    for _ in range(restarts):
        s = rng.choice([-1, 1], n)
        improved = True
        while improved:
            improved = False
            for i in rng.permutation(n):
                gain = 2 * s[i] * (W[i] @ s)
                if gain < 0:
                    s[i] *= -1; improved = True
        best = max(best, cut(W, s))
    return best


# --- GRD: sign-audited greedy (flip iff it INCREASES the cut) -------------------------------------
def greedy_correct(W, restarts=25, seed=7):
    n = W.shape[0]; rng = np.random.default_rng(seed); best = -1e9
    for _ in range(restarts):
        s = rng.choice([-1, 1], n)
        improved = True
        while improved:
            improved = False
            for i in rng.permutation(n):
                dcut = s[i] * (W[i] @ s)   # change in cut from flipping i
                if dcut > 1e-12:
                    s[i] *= -1; improved = True
        best = max(best, cut(W, s))
    return best


# --- SA: proper Metropolis simulated annealing, geometric cooling ---------------------------------
def sim_anneal(W, sweeps=2000, restarts=5, T0=4.0, T1=0.01, seed=0):
    n = W.shape[0]; rng = np.random.default_rng(seed); best = -1e9
    ratio = (T1 / T0)
    for r in range(restarts):
        s = rng.choice([-1, 1], n).astype(np.int64)
        for sw in range(sweeps):
            T = T0 * ratio ** (sw / sweeps)
            for i in rng.permutation(n):
                dcut = s[i] * float(W[i] @ s)        # change in cut from flipping i
                if dcut > 0 or rng.random() < np.exp(dcut / T):
                    s[i] *= -1
        best = max(best, cut(W, s))
    return best


if __name__ == "__main__":
    print("=== G146: oscillator-Ising vs PROPER simulated annealing (validate G145) ===", flush=True)
    rng = np.random.default_rng(2)   # same instance stream as G145
    rows = []
    osc_v_grd145 = osc_ge_sa = sa_gt_osc = 0
    d_osc_sa, d_grd = [], []
    grd145_cuts, grd_cuts = [], []
    osc_ratio, sa_ratio = [], []
    for trial in range(8):
        n = 30
        A = rng.normal(0, 1, (n, n)); W = np.triu(A, 1); W = W + W.T
        og = max(cut(W, osc_anneal(W, seed=s)) for s in range(5))
        sa = sim_anneal(W, sweeps=2000, restarts=5, seed=11)
        g145 = greedy_g145(W, restarts=25, seed=7)
        gc = greedy_correct(W, restarts=25, seed=7)
        sa_long = sim_anneal(W, sweeps=10000, restarts=3, seed=99)
        ref = max(og, sa, gc, g145, sa_long)
        rows.append((trial, og, sa, g145, gc, ref))
        if og > g145 + 1e-6: osc_v_grd145 += 1
        if og >= sa - 1e-6: osc_ge_sa += 1
        if sa > og + 1e-6: sa_gt_osc += 1
        d_osc_sa.append(og - sa); d_grd.append(g145)
        grd145_cuts.append(g145); grd_cuts.append(gc)
        osc_ratio.append(og / ref if ref > 0 else 0.0)
        sa_ratio.append(sa / ref if ref > 0 else 0.0)
        print(f"  trial {trial}: OSC={og:7.1f}  SA={sa:7.1f}  GRD145={g145:7.1f}  GRD(fixed)={gc:7.1f}  "
              f"REF={ref:7.1f}  | OSC-SA={og-sa:+6.1f}", flush=True)

    mean_ref = float(np.mean([r[5] for r in rows]))
    eps = 0.02 * abs(mean_ref)
    m_osc_sa = float(np.mean(d_osc_sa))
    G146a = osc_v_grd145 >= 5
    grd_buggy = (float(np.mean(grd145_cuts)) < 0 <= float(np.mean(grd_cuts)))
    # G146c classification
    if osc_ge_sa >= 4 and m_osc_sa >= -eps:
        cls = "COMPETITIVE"
    elif sa_gt_osc >= 6 and -m_osc_sa >= eps:
        cls = "SUBOPTIMAL"
    else:
        cls = "INCONCLUSIVE"
    G146d = (float(np.mean(osc_ratio)) >= 0.95) and (float(np.mean(sa_ratio)) >= 0.95)

    print("\n--- VERDICT ---", flush=True)
    print(f"G146a reproduce G145 (OSC>GRD145 >=5/8) : {G146a}  ({osc_v_grd145}/8)", flush=True)
    print(f"G146b greedy audit                      : GRD145 mean={np.mean(grd145_cuts):.1f}, "
          f"GRD(fixed) mean={np.mean(grd_cuts):.1f} -> buggy={grd_buggy}", flush=True)
    print(f"G146c OSC vs SA                          : {cls}  "
          f"(OSC>=SA on {osc_ge_sa}/8, SA>OSC on {sa_gt_osc}/8, mean OSC-SA={m_osc_sa:+.2f}, eps={eps:.2f})", flush=True)
    print(f"G146d absolute quality (>=0.95 REF)      : {G146d}  "
          f"(OSC {np.mean(osc_ratio):.3f}, SA {np.mean(sa_ratio):.3f})", flush=True)

    if G146a and cls == "COMPETITIVE" and G146d:
        verdict = "PASS - oscillator-Ising is competitive with proper SA; G145's positive claim is VALIDATED"
    elif cls == "SUBOPTIMAL":
        verdict = "TEMPERED/NULL - textbook SA beats the oscillator machine; the programme's lone positive claim is WEAKENED"
    else:
        verdict = "PARTIAL/INCONCLUSIVE - OSC vs SA not decisive at this budget"
    if grd_buggy:
        verdict += " | NOTE: G145's greedy baseline was sign-buggy (minimizing cut) -> the '8/8 vs greedy' framing was unfair"
    print(f"\nG146: {verdict}", flush=True)

    import json
    from pathlib import Path
    out = Path.home() / ".eqmod" / "bet" / "G146"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": rows, "G146a": bool(G146a), "grd_buggy": bool(grd_buggy), "class": cls,
         "G146d": bool(G146d), "mean_osc_sa": m_osc_sa, "eps": eps, "mean_ref": mean_ref,
         "osc_ge_sa": osc_ge_sa, "sa_gt_osc": sa_gt_osc, "verdict": verdict}, indent=2, default=str))
    print("DONE", flush=True)
