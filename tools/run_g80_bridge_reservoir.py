"""G80 — bridge-strength reservoir. Read the BRIDGE-STRENGTH state (high-dim AND slow): bridges
integrate co-firing history; a leak makes them a FADING memory (avoids saturation). State = bridge
strengths binned into a 3x3x3 grid (27 nodes). The genuine high-dim-with-memory reservoir candidate
the G79 analysis pointed to. Held-out temporal XOR + memory, balanced accuracy.

Pre-registered bars in docs/amendments/g80_bridge_reservoir.md.
"""
import sys, json, time
import numpy as np
from pathlib import Path
from world.state import World
from world.physics import tick
from tools.run_bet098 import inject_tight
from tools.run_bet099 import make_cfg

WARMUP = 1500
N_BITS = 200
WIN = 8
NBINS = 3


def bridge_grid(w, box):
    state = np.zeros(NBINS ** 3)
    B = w.b_count
    for b in range(B):
        if not w.b_alive[b]:
            continue
        i, j = int(w.b_atom_i[b]), int(w.b_atom_j[b])
        if i >= w.k_count or j >= w.k_count or not w.k_alive[i] or not w.k_alive[j]:
            continue
        mid = 0.5 * (w.k_pos[i] + w.k_pos[j])
        idx = np.clip((mid / box * NBINS).astype(int), 0, NBINS - 1)
        state[idx[0] * NBINS * NBINS + idx[1] * NBINS + idx[2]] += w.b_strength[b]
    return state


def collect(seed):
    cfg = make_cfg()
    object.__setattr__(cfg, 'rng_seed', seed)
    object.__setattr__(cfg, 'bridge_leak_rate', 0.1)   # fading memory; no consolidation
    w = World(cfg); box = np.asarray(cfg.box_size)
    IN_X = box[0] * 0.2
    for _ in range(WARMUP):
        tick(w, cfg.dt)
    object.__setattr__(cfg, 'lambda_gen', 0.0)
    rng = np.random.default_rng(4000 + seed)
    bits = rng.integers(0, 2, N_BITS)
    states = []
    t0 = time.time()
    for t in range(N_BITS):
        for k in range(WIN):
            if bits[t]:
                inject_tight(w, cfg, box, IN_X, n=12)
            tick(w, cfg.dt)
        states.append(bridge_grid(w, box))
        if time.time() - t0 > 600:
            bits = bits[:len(states)]
            break
    return bits, np.array(states)


def evaluate(states, target, ntr):
    Xtr = np.hstack([states[:ntr], np.ones((ntr, 1))])
    Xte = np.hstack([states[ntr:], np.ones((len(states) - ntr, 1))])
    wts = np.linalg.solve(Xtr.T @ Xtr + 1.0 * np.eye(Xtr.shape[1]), Xtr.T @ (target[:ntr] - 0.5))
    pred = Xte @ wts; yte = target[ntr:]
    pos = yte > 0.5
    tpr = float(np.mean(pred[pos] > 0)) if pos.any() else 0.0
    tnr = float(np.mean(pred[~pos] <= 0)) if (~pos).any() else 0.0
    return 0.5 * (tpr + tnr)


def run(seed):
    bits, states = collect(seed)
    n = len(bits)
    xor = np.array([bits[t] ^ bits[t - 1] for t in range(1, n)]).astype(float)
    mem = np.array([bits[t - 1] for t in range(1, n)]).astype(float)
    S = states[1:]; ntr = int(0.7 * len(S))
    return dict(n=n, xor_bal=evaluate(S, xor, ntr), mem_bal=evaluate(S, mem, ntr))


if __name__ == "__main__":
    print("=== G80: bridge-strength reservoir (high-dim + fading memory) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s} (n={R[s]['n']}): XOR balanced-acc={R[s]['xor_bal']:.2f} | memory balanced-acc={R[s]['mem_bal']:.2f}", flush=True)

    G80a = all(R[s]['xor_bal'] >= 0.65 for s in seeds)
    G80b = all(R[s]['mem_bal'] >= 0.65 for s in seeds)
    passed = G80a
    print("\n--- VERDICT ---", flush=True)
    print(f"G80a bridge reservoir XOR >=0.65 (both) : {G80a}", flush=True)
    print(f"G80b fading memory >=0.65 (both)        : {G80b}", flush=True)
    verdict = ("PASS - bridge-strength reservoir solves held-out XOR: the physics substrate IS a usable reservoir (deadlock-free learning)"
               if passed else "NULL - bridge reservoir does not generalize XOR above chance")
    print(f"\nG80: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G80"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
