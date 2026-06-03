"""G145 — is there ANY regime where the physical paradigm genuinely BEATS standard methods? Test the one
place energy-based machines should win: HARD frustrated instances (spin-glass MAX-CUT, random +/- weights)
where greedy gets trapped in local minima. Oscillator-Ising WITH noise-annealing (escapes traps) vs
multi-restart greedy. If the physical machine finds better cuts on hard instances -> a real advantage.
If it ties even here -> 'decorative' is universal. Established methods, named as such."""
import numpy as np


def cut(W, s):
    return 0.25 * float(np.sum(W * (1 - np.outer(s, s))))


def osc_anneal(W, steps=1500, dt=0.03, seed=0):
    n = W.shape[0]; rng = np.random.default_rng(seed)
    th = rng.uniform(0, 2 * np.pi, n)
    for t in range(steps):
        frac = t / steps
        noise = (1.0 - frac) * rng.normal(0, 1.2, n)          # annealed thermal noise -> escapes local minima
        diff = th[:, None] - th[None, :]
        dth = np.sum(W * np.sin(diff), axis=1) - np.sin(2 * th) * frac + noise
        th = (th + dt * dth) % (2 * np.pi)
    return np.where(np.cos(th) >= 0, 1, -1)


def greedy_multi(W, restarts=20, seed=0):
    n = W.shape[0]; rng = np.random.default_rng(seed); best = -1e9
    for _ in range(restarts):
        s = rng.choice([-1, 1], n)
        improved = True
        while improved:
            improved = False
            for i in rng.permutation(n):
                s[i] *= -1; new = cut(W, s)
                if new > cut(W, s * np.where(np.arange(n) == i, -1, 1)):  # compare to pre-flip
                    pass
                s[i] *= -1
                # proper local move:
                gain = 2 * s[i] * (W[i] @ s)
                if gain < 0:
                    s[i] *= -1; improved = True
        best = max(best, cut(W, s))
    return best


if __name__ == "__main__":
    print("=== G145: HARD frustrated MAX-CUT — oscillator-anneal vs multi-restart greedy ===", flush=True)
    rng = np.random.default_rng(2)
    owins = gwins = ties = 0; oadv = []
    for trial in range(8):
        n = 30
        A = rng.normal(0, 1, (n, n)); W = np.triu(A, 1); W = W + W.T   # spin-glass: signed weights (frustrated)
        og = max(cut(W, osc_anneal(W, seed=s)) for s in range(5))
        gg = greedy_multi(W, restarts=25, seed=7)
        oadv.append(og - gg)
        if og > gg + 1e-6: owins += 1
        elif gg > og + 1e-6: gwins += 1
        else: ties += 1
        print(f"  trial {trial}: oscillator={og:.1f}  greedy={gg:.1f}  (osc-greedy={og-gg:+.1f})", flush=True)
    madv = float(np.mean(oadv))
    print("\n--- VERDICT ---", flush=True)
    print(f"  oscillator wins {owins}, greedy wins {gwins}, ties {ties} | mean osc-greedy = {madv:+.2f}", flush=True)
    if madv >= 1.0 and owins >= 5:
        print("G145: PASS - on HARD frustrated instances the oscillator-anneal machine BEATS multi-restart greedy -> a GENUINE physical-computing advantage exists (escapes local minima)", flush=True)
    elif madv <= -1.0:
        print("G145: NULL - oscillator WORSE than greedy on hard instances", flush=True)
    else:
        print("G145: NULL(tie) - oscillator ~ multi-restart greedy even on hard instances; no decisive physical advantage -> 'decorative/no-edge' holds even here", flush=True)
    print("DONE", flush=True)
