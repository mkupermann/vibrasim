"""G106 — does CHARGE transport a symbol across distance along the bridge graph?
Deposit charge into left-edge atoms at one of K y-positions, propagate along bridges (PROP ticks), decode
the far-edge (x>20) atom-charge pattern by y. Co-located whole-box readout is the control. Decisive test
of whether the substrate transmits over distance via charge (vs only co-located readout, G105).
Bars pre-registered in docs/amendments/g106_charge_transport.md.
"""
import sys, json, time
from dataclasses import replace
import numpy as np
from pathlib import Path
from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
N_SYM = 200
K = 4
NBINS = 8
YSPAN = (8.0, 22.0)
QDEP = 5.0
PROP = 10
LEFTX = 10.0
FARX = 20.0


def deposit(w, cy, q=QDEP, leftx=LEFTX, band=2.5):
    K_ = w.k_count
    if K_ == 0:
        return
    al = w.k_alive[:K_]
    x = w.k_pos[:K_, 0]
    y = w.k_pos[:K_, 1]
    sel = al & (x < leftx) & (np.abs(y - cy) < band)
    w.k_charge[:K_][sel] += q


def chargegrid_y(w, box, xmin=None):
    K_ = w.k_count
    if K_ == 0:
        return np.zeros(NBINS)
    al = w.k_alive[:K_]
    mask = al if xmin is None else (al & (w.k_pos[:K_, 0] > xmin))
    y = w.k_pos[:K_, 1][mask]
    q = w.k_charge[:K_][mask]
    if len(y) == 0:
        return np.zeros(NBINS)
    idx = np.clip((y / box[1] * NBINS).astype(int), 0, NBINS - 1)
    g = np.zeros(NBINS)
    np.add.at(g, idx, np.abs(q))
    return g


def collect(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    box = np.asarray(c.box_size)
    chan_y = np.linspace(YSPAN[0], YSPAN[1], K)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)   # keep lattice; just stop new vibrations
    rng = np.random.default_rng(10600 + seed)
    msg = rng.integers(0, K, N_SYM)
    far, both = [], []
    t0 = time.time()
    for s in msg:
        w.k_charge[:w.k_count] = 0.0
        deposit(w, chan_y[s])
        for _ in range(PROP):
            tick(w, c.dt)
        far.append(chargegrid_y(w, box, xmin=FARX))
        both.append(chargegrid_y(w, box, xmin=None))
        if time.time() - t0 > 200:
            msg = msg[:len(far)]
            break
    return msg, np.array(far), np.array(both)


def decode(states, labels, ntr):
    if states.std() == 0:
        return 0.0
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
    return dict(n=n, far=decode(far, msg, ntr), colocated=decode(both, msg, ntr),
                far_energy=float(far.sum()))


if __name__ == "__main__":
    print("=== G106: charge transport across distance (far x>20) vs co-located ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: far(x>20)={R[s]['far']:.2f} | co-located={R[s]['colocated']:.2f} "
              f"(chance=0.25, n={R[s]['n']}, far_charge_energy={R[s]['far_energy']:.1f})", flush=True)
    G106a = all(R[s]['far'] >= 0.85 for s in seeds)
    G106b = all(R[s]['colocated'] >= 0.85 for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"G106a charge transport (far >=0.85 both): {G106a}", flush=True)
    print(f"G106b co-located sanity (>=0.85 both)   : {G106b}", flush=True)
    if G106a:
        print("G106: PASS - charge transports a symbol across distance via the bridge graph; scoped 'transmission' is justified", flush=True)
    elif G106b:
        print("G106: PARTIAL - charge deposited distinguishably but does NOT transport to the far end; substrate is LOCAL-ONLY on both channels (vibration G105 + charge G106) -> co-located codec is final", flush=True)
    else:
        print("G106: NULL - charge not even co-located decodable (setup issue)", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G106"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds},
                                                  "G106a": G106a, "G106b": G106b}, indent=2, default=str))
    print("DONE", flush=True)
