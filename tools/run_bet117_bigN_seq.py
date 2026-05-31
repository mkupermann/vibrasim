"""BET-117 — multiple sequences at large N: capacity vs mechanism."""
import json
from pathlib import Path
import numpy as np
from world.energy import EnergyNet

L = 4


def run(npm, S, use_ctx=True, C=30, seed=0):
    net = EnergyNet(n_per_module=npm, n_modules=2, p_in=0.5, p_cross=0.04,
                    beta=1.5, seed=seed)
    N = net.N; rng = np.random.default_rng(7)
    cidx = np.arange(N - C, N); content = np.arange(0, N - C)
    seqs, tags = [], []
    for s in range(S):
        tag = rng.choice([-1.0, 1.0], C)
        pats = []
        for _ in range(L):
            p = rng.choice([-1.0, 1.0], N)
            if use_ctx:
                p[cidx] = tag
            pats.append(p)
        seqs.append(pats); tags.append(tag)
    for sq in seqs:
        net.train_sequence(sq, lr_T=0.06, lr_W=0.02, assoc_epochs=100)
    mn = 1.0
    for s, sq in enumerate(seqs):
        state = sq[0].copy(); rec = [state.copy()]
        for _ in range(L - 1):
            state = np.tanh(net.beta * ((net.T * net.M) @ state))
            net.state = state
            if use_ctx:
                net.state[cidx] = tags[s]; net.relax(cidx, tags[s], 12)
            else:
                net.relax(None, None, 12)
            state = net.state.copy(); rec.append(state.copy())
        ov = [float(np.mean(np.sign(r[content]) == np.sign(p[content])))
              for r, p in zip(rec, sq)]
        mn = min(mn, min(ov))
    return mn


if __name__ == "__main__":
    print("=== BET-117: multi-sequence at large N (capacity vs mechanism) ===", flush=True)
    r3 = run(150, 3)        # N=300
    r5 = run(200, 5)        # N=400
    print(f"S=3 @ N=300: min content overlap {r3:.3f}", flush=True)
    print(f"S=5 @ N=400: min content overlap {r5:.3f}", flush=True)
    T117a = r3 >= 0.90; T117b = r5 >= 0.85
    passed = T117a and T117b
    print("\n--- VERDICT ---", flush=True)
    print(f"T117a S=3@N300 (>=0.90): {T117a}", flush=True)
    print(f"T117b S=5@N400 (>=0.85): {T117b}", flush=True)
    print(f"\nBET-117: {'PASS (capacity was the limit)' if passed else 'NULL (mechanism is the wall)'}", flush=True)
    out = Path.home()/'.eqmod'/'bet'/'BET-117'; out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps({"r3":r3,"r5":r5,"T117a":T117a,"T117b":T117b,"passed":passed},indent=2))
    print("DONE", flush=True)
