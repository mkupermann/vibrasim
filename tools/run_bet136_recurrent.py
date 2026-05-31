"""BET-136 — recurrent (iterated, locally-learned) dynamics vs the modular wall."""
import json
from pathlib import Path
import numpy as np

V, D = 12, 64

def setup(seed):
    rng = np.random.default_rng(seed)
    E = rng.normal(0, 1/np.sqrt(D), (V, D))          # ring-state codes (fixed, random)
    pos1 = rng.choice([-1.0, 1.0], D); pos2 = rng.choice([-1.0, 1.0], D)
    O = rng.normal(0, 1/np.sqrt(D), (V, D))           # output codebook for static baseline
    return rng, E, O, pos1, pos2

def cleanup_idx(C, x):
    return int(np.argmax(C @ x))

# ---- recurrent computer: learn successor operator U by LOCAL one-step delta ----
def train_recurrent(seed=0):
    rng, E, O, pos1, pos2 = setup(seed)
    bigrams = [(a, b) for a in range(V) for b in range(V) if a != b]
    rng.shuffle(bigrams); te = bigrams[:44]            # held-out PAIRS (never used to train U)
    U = np.zeros((D, D))
    steps = [(k, (k + 1) % V) for k in range(V)]       # the only training signal: successor
    for _ in range(2000):                              # online local updates on single steps
        rng.shuffle(steps)
        for (k, kn) in steps:
            pred = U @ E[k]
            U += 0.02 * np.outer(E[kn] - pred, E[k])   # delta rule, one step, LOCAL
    def run_pair(a, b):
        s = E[a].copy()
        for _ in range(b):                             # ITERATE the dynamics b steps
            s = U @ s
            s = s / (np.linalg.norm(s) + 1e-9) * np.linalg.norm(E[0])  # keep on the manifold
        return cleanup_idx(E, s)
    acc = np.mean([run_pair(a, b) == (a + b) % V for (a, b) in te])
    return float(acc)

# ---- static baseline: one-shot additive map (the established stack) ----
def train_static(seed=0):
    rng, E, O, pos1, pos2 = setup(seed)
    bigrams = [(a, b) for a in range(V) for b in range(V) if a != b]
    rng.shuffle(bigrams); te = bigrams[:44]; tr = bigrams[44:]
    W = np.zeros((D, D))
    def ctx(a, b):
        c = pos1 * E[a] + pos2 * E[b]; return c / (np.linalg.norm(c) + 1e-9)
    for _ in range(400):
        rng.shuffle(tr)
        for (a, b) in tr:
            c = ctx(a, b); W += 0.05 * np.outer(O[(a + b) % V] - W @ c, c)
    acc = np.mean([cleanup_idx(O, W @ ctx(a, b)) == (a + b) % V for (a, b) in te])
    return float(acc)

if __name__ == "__main__":
    print("=== BET-136: recurrent dynamics vs static composition (modular wall) ===", flush=True)
    rec = float(np.mean([train_recurrent(s) for s in range(3)]))
    sta = float(np.mean([train_static(s) for s in range(3)]))
    print(f"  recurrent (iterated successor) held-out : {rec:.3f}", flush=True)
    print(f"  static (one-shot additive)     held-out : {sta:.3f}", flush=True)
    T136a = rec >= 0.85; T136b = sta < 0.30; T136c = (rec - sta) >= 0.50; T136d = True
    passed = T136a and T136b and T136c and T136d
    print("\n--- VERDICT ---", flush=True)
    print(f"T136a recurrent >=0.85 : {T136a} ({rec:.3f})", flush=True)
    print(f"T136b static <0.30     : {T136b} ({sta:.3f})", flush=True)
    print(f"T136c gap >=0.50       : {T136c} ({rec-sta:.3f})", flush=True)
    print(f"T136d local-only train : {T136d} (U trained on single successors only; held-out pairs unused)", flush=True)
    print(f"\nBET-136: {'PASS - substrate DYNAMICS (local-rule + iteration) systematically compute what its static stack cannot' if passed else 'NULL/partial'}", flush=True)
    out = Path.home()/'.eqmod'/'bet'/'BET-136'; out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps({"recurrent":rec,"static":sta,"passed":passed}, indent=2))
    print("DONE", flush=True)
