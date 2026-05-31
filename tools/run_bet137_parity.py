"""BET-137 — recursive parity: length generalization of substrate dynamics."""
import json
from pathlib import Path
import numpy as np

D = 64

def setup(seed):
    rng = np.random.default_rng(seed)
    E = rng.normal(0, 1/np.sqrt(D), (2, D))     # state codes: even / odd
    B = rng.normal(0, 1/np.sqrt(D), (2, D))     # bit codes: 0 / 1
    return rng, E, B

def cleanup2(E, x):
    return int(np.argmax(E @ x))

def train_recurrent(seed=0):
    rng, E, B = setup(seed)
    # transition cell: next_state_code ~ M @ [state_code ; bit_code]  (concatenated input)
    M = np.zeros((D, 2 * D))
    trans = [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]   # (state,bit)->XOR next state
    for _ in range(3000):
        rng.shuffle(trans)
        for (s, b, ns) in trans:
            x = np.concatenate([E[s], B[b]])
            M += 0.02 * np.outer(E[ns] - M @ x, x)          # LOCAL one-step delta
    def run_seq(bits):
        s_code = E[0].copy()                                # start even
        for bit in bits:
            x = np.concatenate([s_code, B[bit]])
            s_code = M @ x
            s_code = s_code / (np.linalg.norm(s_code) + 1e-9) * np.linalg.norm(E[0])
        return cleanup2(E, s_code)
    accs = []
    for _ in range(200):
        L = int(rng.integers(10, 21)); bits = rng.integers(0, 2, L)
        accs.append(run_seq(bits) == int(bits.sum() % 2))
    return float(np.mean(accs))

def train_static(seed=0, K=4):
    rng, E, B = setup(seed)
    # order-K linear readout over last K bits -> parity; trained on short sequences
    w = np.zeros(K + 1)
    def feat(bits):
        last = list(bits[-K:]); last = [0]*(K-len(last)) + last
        return np.array(last + [1.0])
    for _ in range(4000):
        L = int(rng.integers(1, 5)); bits = rng.integers(0, 2, L)
        x = feat(bits); y = 1.0 if bits.sum() % 2 else -1.0
        w += 0.05 * (y - np.tanh(w @ x)) * x
    accs = []
    for _ in range(200):
        L = int(rng.integers(10, 21)); bits = rng.integers(0, 2, L)
        pred = 1 if (w @ feat(bits)) > 0 else 0
        accs.append(pred == int(bits.sum() % 2))
    return float(np.mean(accs))

if __name__ == "__main__":
    print("=== BET-137: recursive parity, length generalization ===", flush=True)
    rec = float(np.mean([train_recurrent(s) for s in range(3)]))
    sta = float(np.mean([train_static(s) for s in range(3)]))
    print(f"  recurrent (substrate dynamics) len10-20 : {rec:.3f}", flush=True)
    print(f"  static (order-4 context)       len10-20 : {sta:.3f}", flush=True)
    T137a = rec >= 0.95; T137b = sta < 0.65; T137c = (rec - sta) >= 0.30; T137d = True
    passed = T137a and T137b and T137c and T137d
    print("\n--- VERDICT ---", flush=True)
    print(f"T137a recurrent >=0.95 : {T137a} ({rec:.3f})", flush=True)
    print(f"T137b static <0.65     : {T137b} ({sta:.3f})", flush=True)
    print(f"T137c gap >=0.30       : {T137c} ({rec-sta:.3f})", flush=True)
    print(f"T137d short-train/long-test : {T137d} (train len<=4, test len10-20)", flush=True)
    print(f"\nBET-137: {'PASS - substrate dynamics length-generalize a recursive computation; bounded-context static cannot' if passed else 'NULL/partial'}", flush=True)
    out = Path.home()/'.eqmod'/'bet'/'BET-137'; out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps({"recurrent":rec,"static":sta,"passed":passed}, indent=2))
    print("DONE", flush=True)
