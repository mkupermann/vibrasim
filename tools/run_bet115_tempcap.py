"""BET-115 — temporal capacity: max number of length-4 sequences recallable vs N.
Confirms BET-114 was a capacity edge and gives a temporal-capacity law + plot.
Pre-registered bars in docs/amendments/bet_115_tempcap.md.
"""
import json
from pathlib import Path
import numpy as np
from world.energy import EnergyNet, make_patterns

L = 4


def max_sequences(npm, seed=0):
    """Largest S (length-L sequences) with min per-step recall overlap >= 0.90."""
    best = 0
    for S in [1, 2, 3, 4, 5, 6, 7, 8]:
        net = EnergyNet(n_per_module=npm, n_modules=2, p_in=0.6, p_cross=0.05,
                        beta=1.5, seed=seed)
        allp = make_patterns(net, n_patterns=S * L, seed=7)
        seqs = [allp[i * L:(i + 1) * L] for i in range(S)]
        for sq in seqs:
            net.train_sequence(sq, lr_T=0.06, lr_W=0.02, assoc_epochs=100)
        mn = 1.0
        for sq in seqs:
            rec = net.recall_sequence(sq[0], L)
            mn = min(mn, min(float(np.mean(np.sign(s) == np.sign(p)))
                             for s, p in zip(rec, sq)))
        if mn >= 0.90:
            best = S
        else:
            break
    return best


if __name__ == "__main__":
    print("=== BET-115: temporal capacity (max sequences vs N) ===", flush=True)
    Ns_npm = [(120, 60), (160, 80), (200, 100), (240, 120), (280, 140)]
    res = []
    for N, npm in Ns_npm:
        S = max_sequences(npm)
        res.append((N, S, S * L))
        print(f"N={N}: max sequences={S}  (patterns={S*L}, /N={S*L/N:.3f})", flush=True)

    Ss = [r[1] for r in res]
    T115a = all(S >= 2 for S in Ss)
    T115b = all(Ss[i] <= Ss[i + 1] for i in range(len(Ss) - 1))
    T115c = Ss[-1] >= 2 * Ss[0]
    passed = T115a and T115b and T115c

    print("\n--- VERDICT ---", flush=True)
    print(f"max-sequences per N: {[r[1] for r in res]}", flush=True)
    print(f"T115a stores>=2 at each N : {T115a}", flush=True)
    print(f"T115b monotonic           : {T115b}", flush=True)
    print(f"T115c largest>=2x smallest: {T115c}", flush=True)
    print(f"\nBET-115: {'PASS' if passed else 'NULL/FAIL'}", flush=True)

    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        Ns = [r[0] for r in res]; pats = [r[2] for r in res]
        fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
        ax[0].plot(Ns, Ss, 'o-', lw=2, color='#8e44ad'); ax[0].set_xlabel('N')
        ax[0].set_ylabel('max sequences (len 4, recall≥0.90)')
        ax[0].set_title('temporal capacity vs size'); ax[0].grid(alpha=0.3)
        ax[1].plot(Ns, pats, 's-', lw=2, color='#16a085', label='stored patterns')
        ax[1].plot(Ns, [0.1 * n for n in Ns], '--', color='gray', label='0.1·N (static cap)')
        ax[1].set_xlabel('N'); ax[1].set_ylabel('total stored patterns')
        ax[1].set_title('temporal store tracks static capacity'); ax[1].legend(); ax[1].grid(alpha=0.3)
        plt.tight_layout(); plt.savefig('bet115_tempcap.png', dpi=110)
        print("saved bet115_tempcap.png", flush=True)
    except Exception as e:
        print(f"(plot skipped: {e})", flush=True)

    out = Path.home() / '.eqmod' / 'bet' / 'BET-115'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'result.json').write_text(json.dumps(
        {"results": res, "T115a": T115a, "T115b": T115b, "T115c": T115c,
         "passed": passed}, indent=2))
    print("DONE", flush=True)
