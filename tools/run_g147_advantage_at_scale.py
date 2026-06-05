"""G147 — does annealing open a REAL gap over a correct, strong multi-restart greedy at scale? The decisive,
final test of whether the oscillator/Ising/annealing paradigm has ANY genuine computational edge.

Pre-registered bars in docs/amendments/g147_advantage_at_scale.md.
"""
import json
from pathlib import Path
import numpy as np


def cut(W, s):
    return 0.25 * float(np.sum(W * (1 - np.outer(s, s))))


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


def greedy_correct(W, restarts=60, seed=7):
    """Sign-correct multi-restart greedy with incremental field h = W@s (O(n) per flip)."""
    n = W.shape[0]; rng = np.random.default_rng(seed); best = -1e9
    for _ in range(restarts):
        s = rng.choice([-1, 1], n).astype(np.float64)
        h = W @ s
        improved = True
        while improved:
            improved = False
            for i in rng.permutation(n):
                dcut = s[i] * h[i]                  # change in cut from flipping i
                if dcut > 1e-12:
                    h += (-2.0 * s[i]) * W[:, i]     # field update for flip
                    s[i] = -s[i]; improved = True
        best = max(best, cut(W, s))
    return best


def sim_anneal(W, sweeps=1000, restarts=4, T0=4.0, T1=0.01, seed=0):
    """Proper Metropolis SA with incremental field h = W@s."""
    n = W.shape[0]; rng = np.random.default_rng(seed); best = -1e9
    ratio = (T1 / T0)
    for r in range(restarts):
        s = rng.choice([-1, 1], n).astype(np.float64)
        h = W @ s
        for sw in range(sweeps):
            T = T0 * ratio ** (sw / sweeps)
            for i in rng.permutation(n):
                dcut = s[i] * h[i]
                if dcut > 0 or rng.random() < np.exp(dcut / T):
                    h += (-2.0 * s[i]) * W[:, i]
                    s[i] = -s[i]
        best = max(best, cut(W, s))
    return best


if __name__ == "__main__":
    print("=== G147: does annealing beat CORRECT strong greedy at scale? ===", flush=True)
    rng = np.random.default_rng(2)
    ns = [30, 60, 100, 150]
    n_inst = 6
    per_n = {}
    for n in ns:
        gaps, anneal_ratios, grd_ratios, anneal_wins = [], [], [], 0
        for inst in range(n_inst):
            A = rng.normal(0, 1, (n, n)); W = np.triu(A, 1); W = W + W.T
            og = max(cut(W, osc_anneal(W, seed=sd)) for sd in range(5))
            sa = sim_anneal(W, sweeps=1000, restarts=4, seed=11)
            gc = greedy_correct(W, restarts=60, seed=7)
            sa_long = sim_anneal(W, sweeps=8000, restarts=2, seed=99)
            ref = max(og, sa, gc, sa_long)
            anneal = max(og, sa)
            ar, gr = anneal / ref, gc / ref
            gaps.append(ar - gr); anneal_ratios.append(ar); grd_ratios.append(gr)
            if anneal > gc + 1e-6:
                anneal_wins += 1
            print(f"  n={n:3d} inst {inst}: OSC={og:8.1f} SA={sa:8.1f} GRD={gc:8.1f} REF={ref:8.1f} "
                  f"| anneal_r={ar:.3f} grd_r={gr:.3f} gap={ar-gr:+.3f}", flush=True)
        per_n[n] = dict(mean_gap=float(np.mean(gaps)), mean_anneal=float(np.mean(anneal_ratios)),
                        mean_grd=float(np.mean(grd_ratios)), anneal_wins=anneal_wins, n_inst=n_inst)
        print(f"  --> n={n}: mean gap={per_n[n]['mean_gap']:+.3f}, anneal_r={per_n[n]['mean_anneal']:.3f}, "
              f"grd_r={per_n[n]['mean_grd']:.3f}, anneal wins {anneal_wins}/{n_inst}", flush=True)

    nmax = ns[-1]
    G147a = per_n[30]['mean_grd'] >= 0.99
    G147c = all(per_n[n]['mean_anneal'] >= 0.97 for n in ns)
    big_gap = per_n[nmax]['mean_gap'] >= 0.02 and per_n[nmax]['anneal_wins'] >= 5
    any_gap = any(per_n[n]['mean_gap'] >= 0.02 for n in ns)
    gaps_seq = [per_n[n]['mean_gap'] for n in ns]
    monotone_growing = all(gaps_seq[i + 1] >= gaps_seq[i] - 1e-9 for i in range(len(gaps_seq) - 1)) and gaps_seq[-1] > 0.005
    if big_gap:
        cls = "ADVANTAGE"
    elif not any_gap:
        cls = "NO_ADVANTAGE"
    elif monotone_growing:
        cls = "EMERGING"
    else:
        cls = "NO_ADVANTAGE"

    print("\n--- VERDICT ---", flush=True)
    print(f"G147a small-n greedy optimal (>=0.99) : {G147a}  (n=30 grd_r={per_n[30]['mean_grd']:.3f})", flush=True)
    print(f"G147b gap classification              : {cls}  (gaps by n: "
          f"{', '.join(f'{n}:{per_n[n]['mean_gap']:+.3f}' for n in ns)})", flush=True)
    print(f"G147c annealers work at scale (>=0.97): {G147c}", flush=True)
    if cls == "ADVANTAGE" and G147c:
        verdict = "PASS/ADVANTAGE - annealing genuinely out-solves strong correct greedy on hard (large) instances; G145's claim RESTORED on a correct baseline"
    elif cls == "NO_ADVANTAGE":
        verdict = "NULL/NO_ADVANTAGE - correct multi-restart greedy tracks annealing up to n=150; the programme shows NO demonstrated computational advantage anywhere"
    else:
        verdict = "PARTIAL/EMERGING - a sub-threshold gap is opening with n; scale further before concluding"
    print(f"\nG147: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G147"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"per_n": per_n, "class": cls, "G147a": bool(G147a),
                                                  "G147c": bool(G147c), "verdict": verdict}, indent=2, default=str))
    print("DONE", flush=True)
