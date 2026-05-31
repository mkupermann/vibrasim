"""BET-116 — context-gated transitions: an episode tag disambiguates concurrent
sequences. Pre-registered bars in docs/amendments/bet_116_context.md.
"""
import json
from pathlib import Path
import numpy as np
from world.energy import EnergyNet

NPM, C, L = 60, 20, 4          # N=120; 20 context nodes; sequences of length 4


def build_sequences(net, S, use_ctx, rng):
    N = net.N
    cidx = np.arange(N - C, N)
    content = np.arange(0, N - C)
    seqs, tags = [], []
    for s in range(S):
        tag = rng.choice([-1.0, 1.0], C)
        pats = []
        for _ in range(L):
            p = rng.choice([-1.0, 1.0], N)
            if use_ctx:
                p[cidx] = tag        # episode tag on context nodes
            pats.append(p)
        seqs.append(pats); tags.append(tag)
    return seqs, tags, cidx, content


def train_and_recall(S, use_ctx, seed=0):
    net = EnergyNet(n_per_module=NPM, n_modules=2, p_in=0.6, p_cross=0.05,
                    beta=1.5, seed=seed)
    rng = np.random.default_rng(7)
    seqs, tags, cidx, content = build_sequences(net, S, use_ctx, rng)
    for sq in seqs:
        net.train_sequence(sq, lr_T=0.06, lr_W=0.02, assoc_epochs=100)

    min_content = 1.0
    for s, sq in enumerate(seqs):
        cval = tags[s] if use_ctx else None
        state = sq[0].copy()
        rec = [state.copy()]
        for _ in range(L - 1):
            nxt = np.tanh(net.beta * ((net.T * net.M) @ state))
            net.state = nxt
            if use_ctx:
                net.state[cidx] = cval
                net.relax(cidx, cval, 12)
            else:
                net.relax(None, None, 12)
            state = net.state.copy(); rec.append(state.copy())
        ov = [float(np.mean(np.sign(r[content]) == np.sign(p[content])))
              for r, p in zip(rec, sq)]
        min_content = min(min_content, min(ov))
    return min_content


if __name__ == "__main__":
    print("=== BET-116: context-gated transitions ===", flush=True)
    ctx3 = train_and_recall(3, use_ctx=True)
    noctx3 = train_and_recall(3, use_ctx=False)
    ctx5 = train_and_recall(5, use_ctx=True)
    print(f"S=3 with context : min content overlap {ctx3:.3f}", flush=True)
    print(f"S=3 no context   : min content overlap {noctx3:.3f}", flush=True)
    print(f"S=5 with context : min content overlap {ctx5:.3f}", flush=True)

    T116a = ctx3 >= 0.90
    T116b = noctx3 < 0.75
    T116c = ctx5 >= 0.85
    passed = T116a and T116b and T116c

    print("\n--- VERDICT ---", flush=True)
    print(f"T116a S=3 context (>=0.90)   : {T116a}", flush=True)
    print(f"T116b no-context fails (<0.75): {T116b}", flush=True)
    print(f"T116c S=5 context (>=0.85)   : {T116c}", flush=True)
    print(f"\nBET-116: {'PASS' if passed else 'NULL/FAIL'}", flush=True)
    if passed:
        print(">>> Context-gating fixes concurrent-sequence interference — "
              "episodic temporal memory.", flush=True)
    out = Path.home() / '.eqmod' / 'bet' / 'BET-116'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'result.json').write_text(json.dumps(
        {"ctx3": ctx3, "noctx3": noctx3, "ctx5": ctx5, "T116a": T116a,
         "T116b": T116b, "T116c": T116c, "passed": passed}, indent=2))
    print("DONE", flush=True)
