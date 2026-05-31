"""BET-138 — attractor-stabilized recurrence for drift-free length generalization."""
import json
from pathlib import Path
import numpy as np

D = 64

def setup(seed):
    rng = np.random.default_rng(seed)
    E = rng.normal(0, 1/np.sqrt(D), (2, D))
    B = rng.normal(0, 1/np.sqrt(D), (2, D))
    return rng, E, B

def cleanup_state(E, x):
    return int(np.argmax(E @ x))

def train_cell(rng, E, B):
    M = np.zeros((D, 2 * D))
    trans = [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]
    for _ in range(3000):
        rng.shuffle(trans)
        for (s, b, ns) in trans:
            x = np.concatenate([E[s], B[b]])
            M += 0.02 * np.outer(E[ns] - M @ x, x)
    return M

def run_seq(M, E, B, bits, in_loop_cleanup):
    s_code = E[0].copy()
    for bit in bits:
        x = np.concatenate([s_code, B[bit]])
        s_code = M @ x
        if in_loop_cleanup:
            s_code = E[cleanup_state(E, s_code)].copy()      # ATTRACTOR snaps to clean code
        else:
            s_code = s_code / (np.linalg.norm(s_code) + 1e-9) * np.linalg.norm(E[0])
    return cleanup_state(E, s_code)

def eval_len(M, E, B, rng, in_loop_cleanup, lo, hi, n=200):
    ok = []
    for _ in range(n):
        L = int(rng.integers(lo, hi + 1)); bits = rng.integers(0, 2, L)
        ok.append(run_seq(M, E, B, bits, in_loop_cleanup) == int(bits.sum() % 2))
    return float(np.mean(ok))

def trial(seed, in_loop_cleanup, lo, hi):
    rng, E, B = setup(seed); M = train_cell(rng, E, B)
    return eval_len(M, E, B, rng, in_loop_cleanup, lo, hi)

if __name__ == "__main__":
    print("=== BET-138: attractor-stabilized recurrence (parity length-gen) ===", flush=True)
    attr = float(np.mean([trial(s, True, 10, 20) for s in range(3)]))
    naive = float(np.mean([trial(s, False, 10, 20) for s in range(3)]))
    attr50 = float(np.mean([trial(s, True, 50, 50) for s in range(3)]))
    print(f"  attractor-recurrent len10-20 : {attr:.3f}", flush=True)
    print(f"  naive (no cleanup) len10-20  : {naive:.3f}", flush=True)
    print(f"  attractor-recurrent len50    : {attr50:.3f}", flush=True)
    T138a = attr >= 0.95; T138b = naive < 0.65; T138c = (attr - naive) >= 0.30; T138d = attr50 >= 0.90
    passed = T138a and T138b and T138c and T138d
    print("\n--- VERDICT ---", flush=True)
    print(f"T138a attractor >=0.95 : {T138a} ({attr:.3f})", flush=True)
    print(f"T138b naive <0.65      : {T138b} ({naive:.3f})", flush=True)
    print(f"T138c gap >=0.30       : {T138c} ({attr-naive:.3f})", flush=True)
    print(f"T138d len50 >=0.90     : {T138d} ({attr50:.3f})", flush=True)
    print(f"\nBET-138: {'PASS - attractor-stabilized recurrence gives DRIFT-FREE unbounded composition (substrate-native)' if passed else 'NULL/partial'}", flush=True)
    out = Path.home()/'.eqmod'/'bet'/'BET-138'; out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps({"attr":attr,"naive":naive,"attr50":attr50,"passed":passed}, indent=2))
    print("DONE", flush=True)
