"""BET-111 — capacity scaling. One job per network size N: sweep the number of
stored patterns, report Capacity(N) = max patterns with completion >= 0.90.

Usage: run_bet111_capacity.py <n_per_module>   (N = 2*n_per_module)
Pre-registered bars in docs/amendments/bet_111_capacity.md.
"""
import sys, json
from pathlib import Path
import numpy as np
from world.energy import EnergyNet, make_patterns

THRESH = 0.90
EPOCHS = 120
CUE = 0.4


def completion_at(n_per_module, n_patterns, seed=0):
    net = EnergyNet(n_per_module=n_per_module, n_modules=2, p_in=0.6,
                    p_cross=0.05, beta=1.5, seed=seed)
    pats = make_patterns(net, n_patterns=n_patterns, seed=7)
    for _ in range(EPOCHS):
        net.train_epoch(pats, cue_frac=CUE, lr=0.02, relax_steps=15)
    return net.recall_accuracy(pats, cue_frac=CUE, trials=40)


if __name__ == "__main__":
    npm = int(sys.argv[1])
    N = 2 * npm
    print(f"=== BET-111 capacity: N={N} ===", flush=True)
    capacity = 0
    # increasing pattern counts until completion drops below threshold
    for k in [2, 4, 6, 8, 10, 12, 16, 20, 26, 32, 40, 50]:
        acc = completion_at(npm, k)
        print(f"N={N}  patterns={k:3d}  completion={acc:.3f}", flush=True)
        if acc >= THRESH:
            capacity = k
        else:
            break
    print(f"\nCAPACITY N={N}: {capacity}  (ratio cap/N = {capacity/N:.3f})", flush=True)
    outdir = Path.home() / '.eqmod' / 'bet' / f'BET-111-N{N}'
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'result.json').write_text(json.dumps(
        {"N": N, "capacity": capacity, "ratio": capacity / N}, indent=2))
    print("DONE", flush=True)
