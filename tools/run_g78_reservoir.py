"""G78 — substrate reservoir, done PROPERLY. A long random bit stream drives the proto-cell; the
reservoir STATE is read in 8 spatial octants (high-dim). Target = temporal XOR (bit[t] XOR bit[t-1]),
which needs short memory + nonlinearity. Ridge readout trained on the FIRST portion, evaluated on a
HELD-OUT tail. #samples >> #features and train/test split => no overfitting (the G77 flaw fixed).

Controls: (b) linear readout on the raw bits {bit[t],bit[t-1]} can't solve XOR (sanity it needs
nonlinearity); (c) reservoir predicting bit[t-1] (linear memory task) confirms fading memory.

Pre-registered bars in docs/amendments/g78_reservoir_proper.md.
"""
import sys, json
from dataclasses import replace
from pathlib import Path
import numpy as np
from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg, membrane_geom
from tools.run_g59_rejection import inject_rate

SETTLE = 250
PRECLEAR = 60
N_BITS = 150
WIN = 12          # ticks per bit
BURST = 8
TRAIN_FRAC = 0.7


def octant_state(w, centre, radius, f_mem, c_lo, c_hi, box):
    alive = w.s_alive[: w.s_pos.shape[0]]
    if not alive.any():
        return np.zeros(8)
    pos = w.s_pos[alive]; freq = w.s_freq[alive]
    ratio = np.abs(freq - f_mem) / np.maximum(np.minimum(freq, f_mem), 1e-12)
    incompat = ~((ratio >= c_lo) & (ratio <= c_hi))
    d = pos - centre; d -= box * np.round(d / box)
    r = np.linalg.norm(d, axis=1)
    inside = (r < 0.6 * radius) & incompat
    if not inside.any():
        return np.zeros(8)
    di = d[inside]
    oct_id = (di[:, 0] > 0).astype(int) + 2 * (di[:, 1] > 0).astype(int) + 4 * (di[:, 2] > 0).astype(int)
    return np.bincount(oct_id, minlength=8).astype(float)


def collect(seed):
    c = cfg(seed); w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    geom = membrane_geom(w)
    if geom is None:
        return None
    centre, radius, f_mem, _ = geom
    c_lo, c_hi = c.freq_ratio - c.freq_tolerance, c.freq_ratio + c.freq_tolerance
    box = np.asarray(c.box_size, dtype=np.float64)
    w.config = replace(c, membrane_channel_k=1.0, membrane_channel_mode='atom', membrane_channel_recompute=20)
    for _ in range(PRECLEAR):
        tick(w, c.dt)
    rng = np.random.default_rng(2000 + seed)
    bits = rng.integers(0, 2, N_BITS)
    states = []
    for t in range(N_BITS):
        for k in range(WIN):
            if bits[t]:
                inject_rate(w, centre, radius, f_mem, box, rng, BURST)
            tick(w, c.dt)
        states.append(octant_state(w, centre, radius, f_mem, c_lo, c_hi, box))
    return bits, np.array(states)


def evaluate(states, target, n_train):
    Xtr = np.hstack([states[:n_train], np.ones((n_train, 1))])
    Xte = np.hstack([states[n_train:], np.ones((len(states) - n_train, 1))])
    ytr = target[:n_train] - 0.5
    lam = 1.0
    wts = np.linalg.solve(Xtr.T @ Xtr + lam * np.eye(Xtr.shape[1]), Xtr.T @ ytr)
    pred = Xte @ wts
    acc = float(np.mean((pred > 0) == (target[n_train:] > 0.5)))
    return acc


def run(seed):
    bits, states = collect(seed)
    n = len(bits)
    n_train = int(TRAIN_FRAC * n)
    # targets aligned for t>=1 (need bit[t-1])
    xor = np.array([bits[t] ^ bits[t - 1] for t in range(1, n)])
    prev = np.array([bits[t - 1] for t in range(1, n)])
    S = states[1:]
    ntr = int(TRAIN_FRAC * len(S))
    res_xor = evaluate(S, xor.astype(float), ntr)
    res_mem = evaluate(S, prev.astype(float), ntr)
    # control: linear readout on raw bits {bit[t], bit[t-1]} -> XOR
    rawX = np.array([[bits[t], bits[t - 1]] for t in range(1, n)], dtype=float)
    lin_xor = evaluate(rawX, xor.astype(float), ntr)
    return dict(res_xor=res_xor, res_mem=res_mem, lin_xor=lin_xor)


if __name__ == "__main__":
    print("=== G78: substrate reservoir (held-out temporal XOR) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: reservoir XOR test-acc={R[s]['res_xor']:.2f} | memory(bit[t-1]) test-acc={R[s]['res_mem']:.2f} "
              f"| linear-on-raw-bits XOR={R[s]['lin_xor']:.2f}", flush=True)

    G78a = all(R[s]['res_xor'] >= 0.70 for s in seeds)
    G78b = all(R[s]['lin_xor'] <= 0.65 for s in seeds)
    passed = G78a and G78b
    print("\n--- VERDICT ---", flush=True)
    print(f"G78a reservoir solves XOR on HELD-OUT (>=0.70, both) : {G78a}", flush=True)
    print(f"G78b linear-on-raw-bits can't (<=0.65, both)        : {G78b}", flush=True)
    print(f"  (memory control bit[t-1] test-acc: {[round(R[s]['res_mem'],2) for s in seeds]})", flush=True)
    verdict = ("PASS - genuine RESERVOIR: substrate dynamics make temporal XOR linearly readable on held-out data (learning without writable memory)"
               if passed else "NULL - reservoir does not generalize XOR above chance")
    print(f"\nG78: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G78"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
