"""G105 — transmission over DISTANCE vs co-located readout (honesty check on the channel claim).
Symbol = which of K channels along Y. Inject at the LEFT edge (x=4) with +x velocity; propagate D ticks;
decode from the Y-binned grid of the FAR region (x>16). Compare to a co-located full-box readout.
If far-end decode works, "transmission" is justified; if only co-located works, correct the wording.
Bars pre-registered in docs/amendments/g105_transmission_distance.md.
"""
import sys, json, time
from dataclasses import replace
import numpy as np
from pathlib import Path
from world.state import World
from world.physics import tick
from tools.run_bet093 import cull_free_vibrations
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
N_SYM = 240
K = 4
NBINS = 8
YSPAN = (8.0, 22.0)
X0 = 4.0
VX = 6.0
PROP = 6
FARX = 16.0


def inject_moving(w, cfg, box, x0, cy, n, vx, sigma=1.0):
    rng = w.rng
    free = np.where(~w.s_alive[:cfg.n_vibrations_max])[0]
    k = min(n, len(free))
    if k == 0:
        return
    sl = free[:k]
    w.s_pos[sl] = np.column_stack([
        rng.normal(x0, sigma, k) % box[0],
        rng.normal(cy, sigma, k) % box[1],
        rng.normal(box[2] / 2, sigma, k) % box[2]])
    w.s_vel[sl] = np.tile([vx, 0.0, 0.0], (k, 1))
    w.s_freq[sl] = w._sample_frequencies(k)
    w.s_pol[sl] = rng.random(k) < 0.5
    w.s_alive[sl] = True
    w.n_alive = max(w.n_alive, int(sl.max()) + 1)


def ygrid(w, box, xmin=None):
    n = w.s_pos.shape[0]
    alive = w.s_alive[:n]
    mask = alive if xmin is None else (alive & (w.s_pos[:n, 0] > xmin))
    y = w.s_pos[:n, 1][mask]
    if len(y) == 0:
        return np.zeros(NBINS)
    idx = np.clip((y / box[1] * NBINS).astype(int), 0, NBINS - 1)
    return np.bincount(idx, minlength=NBINS).astype(float)


def collect(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    box = np.asarray(c.box_size)
    chan_y = np.linspace(YSPAN[0], YSPAN[1], K)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    cull_free_vibrations(w, keep_frac=0.0)
    rng = np.random.default_rng(10500 + seed)
    msg = rng.integers(0, K, N_SYM)
    far, both = [], []
    t0 = time.time()
    for s in msg:
        inject_moving(w, c, box, X0, chan_y[s], n=14, vx=VX)
        for _ in range(PROP):
            tick(w, c.dt)
        far.append(ygrid(w, box, xmin=FARX))     # only vibrations that propagated downstream
        both.append(ygrid(w, box, xmin=None))    # co-located full-box readout (control)
        cull_free_vibrations(w, keep_frac=0.0)
        if time.time() - t0 > 200:
            msg = msg[:len(far)]
            break
    return msg, np.array(far), np.array(both)


def decode(states, labels, ntr):
    Xtr = np.hstack([states[:ntr], np.ones((ntr, 1))])
    Xte = np.hstack([states[ntr:], np.ones((len(states) - ntr, 1))])
    W = np.zeros((Xtr.shape[1], K))
    for k in range(K):
        yk = (labels[:ntr] == k).astype(float) - (1.0 / K)
        W[:, k] = np.linalg.solve(Xtr.T @ Xtr + 1.0 * np.eye(Xtr.shape[1]), Xtr.T @ yk)
    pred = (Xte @ W).argmax(axis=1)
    return float(np.mean(pred == labels[ntr:]))


def run(seed):
    msg, far, both = collect(seed)
    n = len(msg)
    ntr = int(0.7 * n)
    return dict(n=n, far=decode(far, msg, ntr), colocated=decode(both, msg, ntr))


if __name__ == "__main__":
    print("=== G105: transmission over distance (far-end x>16) vs co-located readout ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: far(x>16)={R[s]['far']:.2f} | co-located={R[s]['colocated']:.2f} (chance=0.25, n={R[s]['n']})", flush=True)
    G105a = all(R[s]['far'] >= 0.85 for s in seeds)
    G105b = all(R[s]['colocated'] >= 0.85 for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"G105a transmission over distance (far >=0.85 both): {G105a}", flush=True)
    print(f"G105b co-located sanity (>=0.85 both)             : {G105b}", flush=True)
    if G105a:
        print("G105: PASS - genuine transmission over distance; 'transmission' language justified", flush=True)
    elif G105b:
        print("G105: PARTIAL - symbol is encoded but does NOT survive propagation to the far end; the channel is CO-LOCATED readout, not transmission over distance -> correct the wording", flush=True)
    else:
        print("G105: NULL - neither far nor co-located decodes (setup issue)", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G105"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds},
                                                  "G105a": G105a, "G105b": G105b}, indent=2, default=str))
    print("DONE", flush=True)
