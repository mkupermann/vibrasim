"""G140 — the recommended physical-computing paradigm also does ASSOCIATIVE MEMORY (Hopfield/oscillator
relaxation): store patterns as couplings, present a NOISY cue, relax, recover the pattern. Ties the user's
memory + compute threads into one useful no-LLM physical primitive. Established (Hopfield network), named
as such; numpy reference (hardware = the same coupled-oscillator relaxation as the Ising machine).
"""
import numpy as np


def store(patterns):
    n = patterns.shape[1]
    W = np.zeros((n, n))
    for p in patterns:
        W += np.outer(p, p)
    np.fill_diagonal(W, 0)
    return W / len(patterns)


def recall(W, cue, steps=30):
    s = cue.copy()
    for _ in range(steps):
        order = np.random.default_rng(0).permutation(len(s))
        for i in order:
            s[i] = 1 if W[i] @ s >= 0 else -1
    return s


if __name__ == "__main__":
    print("=== G140: oscillator/Hopfield ASSOCIATIVE MEMORY (recall from noisy cue) ===", flush=True)
    rng = np.random.default_rng(1)
    n = 64
    accs = []
    for K in [3, 5, 8]:                          # number of stored patterns (capacity ~0.14n ≈ 9)
        pats = rng.choice([-1, 1], (K, n))
        W = store(pats)
        for flip in [0.05, 0.15, 0.25]:          # cue noise (fraction of bits flipped)
            ok = 0
            for p in pats:
                cue = p.copy()
                idx = rng.choice(n, int(flip * n), replace=False); cue[idx] *= -1
                out = recall(W, cue)
                ok += int(np.mean(out == p) > 0.99)   # exact recovery
            acc = ok / K
            accs.append((K, flip, acc))
            print(f"  K={K} patterns, cue-noise={flip:.0%}: exact recall = {acc:.2f}", flush=True)
    easy = np.mean([a for K, f, a in accs if K <= 5 and f <= 0.15])
    print("\n--- VERDICT ---", flush=True)
    print(f"  recall (<=5 patterns, <=15% noise) mean = {easy:.2f}", flush=True)
    if easy >= 0.9:
        print("G140: PASS - the physical-computing paradigm does CONTENT-ADDRESSABLE recall (Hopfield relaxation): recovers stored patterns from noisy cues. Combined with G138/G139 (optimization), one oscillator substrate gives no-LLM memory AND compute.", flush=True)
    else:
        print("G140: PARTIAL - recall works but below 0.9 in the easy regime (capacity/tuning)", flush=True)
    print("DONE", flush=True)
