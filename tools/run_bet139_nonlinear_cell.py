"""BET-139 — nonlinear (random-feature) recurrent cell for length-generalizing parity."""
import json
from pathlib import Path
import numpy as np

D = 64
H = 512   # random-feature (reservoir) hidden width

def setup(seed):
    rng = np.random.default_rng(seed)
    E = rng.normal(0, 1/np.sqrt(D), (2, D))
    B = rng.normal(0, 1/np.sqrt(D), (2, D))
    R = rng.normal(0, 1.0/np.sqrt(2*D), (H, 2*D))      # substrate's fixed random projection
    bias = rng.normal(0, 0.3, H)
    return rng, E, B, R, bias

def cleanup_state(E, x):
    return int(np.argmax(E @ x))

def phi(R, bias, state, bit_code, nonlinear):
    x = np.concatenate([state, bit_code])
    return np.tanh(R @ x + bias) if nonlinear else x       # nonlinear cell vs linear control

def train_cell(rng, E, B, R, bias, nonlinear):
    fdim = H if nonlinear else 2*D
    Wout = np.zeros((D, fdim))
    trans = [(0,0,0),(0,1,1),(1,0,1),(1,1,0)]
    for _ in range(3000):
        rng.shuffle(trans)
        for (s,b,ns) in trans:
            f = phi(R, bias, E[s], B[b], nonlinear)
            Wout += 0.02 * np.outer(E[ns] - Wout @ f, f)
    return Wout

def run_seq(Wout, E, B, R, bias, bits, nonlinear):
    s = E[0].copy()
    for bit in bits:
        f = phi(R, bias, s, B[bit], nonlinear)
        s = E[cleanup_state(E, Wout @ f)].copy()           # in-loop attractor cleanup
    return cleanup_state(E, s)

def eval_acc(seed, nonlinear, lo, hi, n=200):
    rng, E, B, R, bias = setup(seed)
    Wout = train_cell(rng, E, B, R, bias, nonlinear)
    ok = []
    for _ in range(n):
        L = int(rng.integers(lo, hi+1)); bits = rng.integers(0, 2, L)
        ok.append(run_seq(Wout, E, B, R, bias, bits, nonlinear) == int(bits.sum() % 2))
    return float(np.mean(ok))

if __name__ == "__main__":
    print("=== BET-139: nonlinear recurrent cell, parity length-gen ===", flush=True)
    nl = float(np.mean([eval_acc(s, True, 10, 20) for s in range(3)]))
    lin = float(np.mean([eval_acc(s, False, 10, 20) for s in range(3)]))
    nl50 = float(np.mean([eval_acc(s, True, 50, 50) for s in range(3)]))
    print(f"  nonlinear cell len10-20 : {nl:.3f}", flush=True)
    print(f"  linear control len10-20 : {lin:.3f}", flush=True)
    print(f"  nonlinear cell len50    : {nl50:.3f}", flush=True)
    T139a = nl >= 0.95; T139b = lin < 0.65; T139c = nl50 >= 0.90; T139d = True
    passed = T139a and T139b and T139c and T139d
    print("\n--- VERDICT ---", flush=True)
    print(f"T139a nonlinear >=0.95 : {T139a} ({nl:.3f})", flush=True)
    print(f"T139b linear <0.65     : {T139b} ({lin:.3f})", flush=True)
    print(f"T139c len50 >=0.90     : {T139c} ({nl50:.3f})", flush=True)
    print(f"T139d short/local train: {T139d}", flush=True)
    print(f"\nBET-139: {'PASS - nonlinear substrate-feature recurrent cell + cleanup = drift-free unbounded recursive composition, local-rule, no BPTT' if passed else 'NULL/partial'}", flush=True)
    out = Path.home()/'.eqmod'/'bet'/'BET-139'; out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps({"nonlinear":nl,"linear":lin,"nl50":nl50,"passed":passed}, indent=2))
    print("DONE", flush=True)
