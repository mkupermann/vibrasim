"""G79 — whole-substrate reservoir. Drive a full firing lattice (neuron_dynamics) with a random bit
stream injected into an input region; read a HIGH-DIM state = a 3x3x3 spatial grid of atom charge
(27 reservoir 'nodes'). Train a ridge readout on temporal XOR / memory with a HELD-OUT split.
Reads the substrate's actual recurrent activity (vs G78's tiny proto-cell interior).

Pre-registered bars in docs/amendments/g79_substrate_reservoir.md.
"""
import sys, json, time
import numpy as np
from pathlib import Path
from world.state import World
from world.physics import tick
from tools.run_bet098 import inject_tight
from tools.run_bet099 import make_cfg

WARMUP = 2000
N_BITS = 200
WIN = 8
NBINS = 3


def grid_state(w, box):
    K = w.k_count
    if K == 0:
        return np.zeros(NBINS ** 3)
    alive = w.k_alive[:K] & (w.k_level[:K] >= 4)
    pos = w.k_pos[:K][alive]; ch = w.k_charge[:K][alive]
    if len(pos) == 0:
        return np.zeros(NBINS ** 3)
    idx = np.clip(np.floor(pos / box * NBINS).astype(int), 0, NBINS - 1)
    flat = idx[:, 0] * NBINS * NBINS + idx[:, 1] * NBINS + idx[:, 2]
    state = np.zeros(NBINS ** 3)
    np.add.at(state, flat, ch + 1.0)   # +1 so presence (not just charge) registers
    return state


def collect(seed):
    cfg = make_cfg()
    object.__setattr__(cfg, 'rng_seed', seed)
    w = World(cfg); box = np.asarray(cfg.box_size)
    IN_X = box[0] * 0.2
    for _ in range(WARMUP):
        tick(w, cfg.dt)
    object.__setattr__(cfg, 'lambda_gen', 0.0)
    rng = np.random.default_rng(3000 + seed)
    bits = rng.integers(0, 2, N_BITS)
    states = []
    t0 = time.time()
    for t in range(N_BITS):
        for k in range(WIN):
            if bits[t]:
                inject_tight(w, cfg, box, IN_X, n=12)
            tick(w, cfg.dt)
        states.append(grid_state(w, box))
        if time.time() - t0 > 600:
            bits = bits[:len(states)]
            break
    return bits, np.array(states)


def evaluate(states, target, ntr):
    Xtr = np.hstack([states[:ntr], np.ones((ntr, 1))])
    Xte = np.hstack([states[ntr:], np.ones((len(states) - ntr, 1))])
    ytr = target[:ntr] - 0.5
    lam = 1.0
    wts = np.linalg.solve(Xtr.T @ Xtr + lam * np.eye(Xtr.shape[1]), Xtr.T @ ytr)
    pred = Xte @ wts
    yte = target[ntr:]
    acc = float(np.mean((pred > 0) == (yte > 0.5)))
    # balanced accuracy (robust to class imbalance)
    pos = yte > 0.5
    tpr = float(np.mean((pred[pos] > 0))) if pos.any() else 0.0
    tnr = float(np.mean((pred[~pos] <= 0))) if (~pos).any() else 0.0
    return acc, 0.5 * (tpr + tnr)


def run(seed):
    bits, states = collect(seed)
    n = len(bits)
    xor = np.array([bits[t] ^ bits[t - 1] for t in range(1, n)]).astype(float)
    mem = np.array([bits[t - 1] for t in range(1, n)]).astype(float)
    S = states[1:]
    ntr = int(0.7 * len(S))
    xa, xb = evaluate(S, xor, ntr)
    ma, mb = evaluate(S, mem, ntr)
    return dict(n=n, xor_acc=xa, xor_bal=xb, mem_acc=ma, mem_bal=mb)


if __name__ == "__main__":
    print("=== G79: whole-substrate reservoir (27-node grid state, held-out) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s} (n={R[s]['n']}): XOR balanced-acc={R[s]['xor_bal']:.2f} (raw {R[s]['xor_acc']:.2f}) "
              f"| memory balanced-acc={R[s]['mem_bal']:.2f}", flush=True)

    G79a = all(R[s]['xor_bal'] >= 0.65 for s in seeds)
    G79b = all(R[s]['mem_bal'] >= 0.65 for s in seeds)
    passed = G79a
    print("\n--- VERDICT ---", flush=True)
    print(f"G79a reservoir XOR balanced-acc >=0.65 (both) : {G79a}", flush=True)
    print(f"G79b fading memory >=0.65 (both)              : {G79b}", flush=True)
    verdict = ("PASS - whole-substrate reservoir solves held-out temporal XOR: a usable physics reservoir (deadlock-free computation)"
               if passed else "NULL - substrate reservoir does not generalize XOR above chance")
    print(f"\nG79: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G79"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
