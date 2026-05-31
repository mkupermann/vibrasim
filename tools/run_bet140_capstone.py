"""BET-140 — capstone: substrate-native unbounded recursive composition (parity)."""
import json
from pathlib import Path
import numpy as np

D = 64
H = 512

def setup(seed):
    rng = np.random.default_rng(seed)
    E = rng.normal(0, 1/np.sqrt(D), (2, D))
    B = rng.normal(0, 1/np.sqrt(D), (2, D))
    R = rng.normal(0, 1.0/np.sqrt(2*D), (H, 2*D))
    bias = rng.normal(0, 0.3, H)
    return rng, E, B, R, bias

def cleanup_state(E, x):
    return int(np.argmax(E @ x))

def feats(R, bias, state, bit_code, nonlinear):
    x = np.concatenate([state, bit_code])
    return np.tanh(R @ x + bias) if nonlinear else x

def train_lsq(E, B, R, bias, nonlinear, lam=1e-4):
    trans = [(0,0,0),(0,1,1),(1,0,1),(1,1,0)]
    X = np.array([feats(R, bias, E[s], B[b], nonlinear) for (s,b,_) in trans])
    Y = np.array([E[ns] for (_,_,ns) in trans])
    A = X.T @ X + lam*np.eye(X.shape[1])
    return (np.linalg.solve(A, X.T @ Y)).T          # ridge LSQ = the online-RLS fixed point

def run_seq(Wout, E, B, R, bias, bits, nonlinear):
    s = E[0].copy()
    for bit in bits:
        s = E[cleanup_state(E, Wout @ feats(R, bias, s, B[bit], nonlinear))].copy()
    return cleanup_state(E, s)

def acc_at(seed, nonlinear, lo, hi, n=300):
    rng, E, B, R, bias = setup(seed)
    Wout = train_lsq(E, B, R, bias, nonlinear)
    ok = []
    for _ in range(n):
        L = int(rng.integers(lo, hi+1)); bits = rng.integers(0, 2, L)
        ok.append(run_seq(Wout, E, B, R, bias, bits, nonlinear) == int(bits.sum() % 2))
    return float(np.mean(ok))

if __name__ == "__main__":
    print("=== BET-140: capstone — unbounded recursive composition ===", flush=True)
    a = float(np.mean([acc_at(s, True, 10, 20) for s in range(3)]))
    a50 = float(np.mean([acc_at(s, True, 50, 50) for s in range(3)]))
    a100 = float(np.mean([acc_at(s, True, 100, 100) for s in range(3)]))
    lin = float(np.mean([acc_at(s, False, 10, 20) for s in range(3)]))
    print(f"  nonlinear len10-20 : {a:.3f}", flush=True)
    print(f"  nonlinear len50    : {a50:.3f}", flush=True)
    print(f"  nonlinear len100   : {a100:.3f}", flush=True)
    print(f"  linear  len10-20   : {lin:.3f}", flush=True)
    T140a = a >= 0.98; T140b = a50 >= 0.95; T140c = a100 >= 0.90; T140d = lin < 0.70
    passed = T140a and T140b and T140c and T140d
    print("\n--- VERDICT ---", flush=True)
    print(f"T140a len10-20 >=0.98 : {T140a} ({a:.3f})", flush=True)
    print(f"T140b len50 >=0.95    : {T140b} ({a50:.3f})", flush=True)
    print(f"T140c len100 >=0.90   : {T140c} ({a100:.3f})", flush=True)
    print(f"T140d linear <0.70    : {T140d} ({lin:.3f})", flush=True)
    print(f"\nBET-140: {'PASS - substrate-native unbounded recursive composition (nonlinear features + RLS readout + attractor cleanup), local-only, no BPTT, no transformer' if passed else 'NULL/partial'}", flush=True)
    out = Path.home()/'.eqmod'/'bet'/'BET-140'; out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps({"a":a,"a50":a50,"a100":a100,"lin":lin,"passed":passed}, indent=2))
    print("DONE", flush=True)
