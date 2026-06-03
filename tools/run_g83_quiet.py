"""G83 — QUIET substrate test of the root hypothesis. After settling a lattice, CULL the free-
vibration background (and lambda_gen=0) so the substrate is quiet but still has atoms (binding
nonlinearity). Then run spatial-XOR trials. If a quiet background makes the input REGISTER (sanity
passes) where the active substrate (G81/G82) drowned it, the homogeneous-activity ROOT is confirmed
— and a quiet substrate may unlock computation.

Pre-registered bars in docs/amendments/g83_quiet.md.
"""
import sys, json, time
from dataclasses import replace
import numpy as np
from pathlib import Path
from world.state import World
from world.physics import tick
from tools.run_bet098 import inject_tight
from tools.run_bet093 import cull_free_vibrations
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
N_TRIAL = 240
WIN = 8
NBINS = 3
AX, BX = 8.0, 14.0


def vib_grid(w, box):
    n = w.s_pos.shape[0]
    alive = w.s_alive[:n]
    pos = w.s_pos[:n][alive]
    if len(pos) == 0:
        return np.zeros(NBINS ** 3)
    idx = np.clip((pos / box * NBINS).astype(int), 0, NBINS - 1)
    flat = idx[:, 0] * NBINS * NBINS + idx[:, 1] * NBINS + idx[:, 2]
    return np.bincount(flat, minlength=NBINS ** 3).astype(float)


def collect(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c); box = np.asarray(c.box_size)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    cull_free_vibrations(w, keep_frac=0.0)        # QUIET the background
    rng = np.random.default_rng(7000 + seed)
    inputs = rng.integers(0, 2, (N_TRIAL, 2))
    states = []
    t0 = time.time()
    for t in range(N_TRIAL):
        a, b = inputs[t]
        for k in range(WIN):
            if a:
                inject_tight(w, c, box, AX, n=14)
            if b:
                inject_tight(w, c, box, BX, n=14)
            tick(w, c.dt)
        states.append(vib_grid(w, box))
        cull_free_vibrations(w, keep_frac=0.0)    # re-quiet between trials (clear residual)
        if time.time() - t0 > 600:
            inputs = inputs[:len(states)]; break
    return inputs, np.array(states)


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
    inp, states = collect(seed)
    n = len(inp); ntr = int(0.7 * n)
    xor = (inp[:, 0] ^ inp[:, 1]).astype(float)
    a_lab = inp[:, 0].astype(float)
    return dict(n=n, xor_bal=evaluate(states, xor, ntr), a_bal=evaluate(states, a_lab, ntr))


if __name__ == "__main__":
    print("=== G83: QUIET substrate — does input register + spatial XOR? ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s} (n={R[s]['n']}): single-input(A) acc={R[s]['a_bal']:.2f} | spatial XOR={R[s]['xor_bal']:.2f}", flush=True)

    sanity = all(R[s]['a_bal'] >= 0.70 for s in seeds)
    G83a = all(R[s]['xor_bal'] >= 0.65 for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"sanity: quiet substrate -> input REGISTERS (>=0.70 both) : {sanity}", flush=True)
    print(f"G83a quiet substrate spatial XOR (>=0.65 both)           : {G83a}", flush=True)
    if G83a:
        verdict = "PASS - quiet substrate computes spatial XOR (root confirmed AND computation unlocked)"
    elif sanity:
        verdict = "PARTIAL - root CONFIRMED (quiet substrate registers input where active one drowned it) but XOR still not linearly readable (no nonlinear interaction)"
    else:
        verdict = "NULL - even a quiet substrate doesn't register input (root is elsewhere)"
    print(f"\nG83: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G83"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds},
                                                  "sanity": sanity, "passed": G83a}, indent=2, default=str))
    print("DONE", flush=True)
