"""G77 — substrate as a RESERVOIR: temporal XOR. Encode 2 input bits as presence/absence of
foreign-influx bursts in two time windows; read the interior concentration trajectory as features;
fit a LINEAR readout to the XOR label. XOR is not linearly separable in the inputs, so success
requires the substrate's NONLINEAR dynamics (G74) to build a separable representation. This is the
reservoir-computing test: computation from fixed nonlinear dynamics + a trained linear readout,
NEEDING NO writable internal memory (sidesteps the write=leak deadlock).

Pre-registered bars in docs/amendments/g77_reservoir_xor.md.
"""
import sys, json
from dataclasses import replace
from pathlib import Path
import numpy as np
from world.state import World
from world.physics import tick
from tools.run_g43_protocell import cfg, membrane_geom
from tools.run_g44_recovery import interior_incompat_conc
from tools.run_g59_rejection import inject_rate

SETTLE = 250
PRECLEAR = 60
W1 = (0, 30)      # input window for bit 1
W2 = (45, 75)     # input window for bit 2
READOUT = range(75, 160)   # sample the trajectory after both inputs
SAMPLE_EVERY = 7
BURST = 8


def run_pattern(seed, b1, b2):
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
    rng = np.random.default_rng(1500 + seed)
    feats = []
    for t in range(160):
        drive = (b1 if W1[0] <= t < W1[1] else 0) + (b2 if W2[0] <= t < W2[1] else 0)
        if drive:
            inject_rate(w, centre, radius, f_mem, box, rng, BURST)
        tick(w, c.dt)
        if t in READOUT and (t % SAMPLE_EVERY == 0):
            feats.append(interior_incompat_conc(w, centre, radius, f_mem, c_lo, c_hi, box))
    return np.array(feats)


def solve_xor(seed):
    patterns = [(0, 0), (0, 1), (1, 0), (1, 1)]
    labels = np.array([0, 1, 1, 0], dtype=float)        # XOR
    X = np.array([run_pattern(seed, b1, b2) for b1, b2 in patterns])
    # augment with bias; least-squares linear readout to labels; check sign separation
    Xb = np.hstack([X, np.ones((4, 1))])
    wts, *_ = np.linalg.lstsq(Xb, labels - 0.5, rcond=None)  # center labels around 0
    pred = Xb @ wts
    correct = int(np.all((pred > 0) == (labels > 0.5)))
    margin = float(np.min(np.abs(pred)))
    # control: is XOR linearly separable from the raw INPUTS alone? (should be NO)
    Ii = np.array([[b1, b2, 1.0] for b1, b2 in patterns])
    wi, *_ = np.linalg.lstsq(Ii, labels - 0.5, rcond=None)
    pin = Ii @ wi
    input_correct = int(np.all((pin > 0) == (labels > 0.5)))
    return dict(reservoir_correct=correct, margin=margin, input_correct=input_correct,
                preds=[round(float(p), 3) for p in pred])


if __name__ == "__main__":
    print("=== G77: substrate reservoir — temporal XOR via linear readout ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = solve_xor(s)
        print(f"  seed {s}: reservoir_solves_XOR={bool(R[s]['reservoir_correct'])} margin={R[s]['margin']:.3f} "
              f"| raw-input-solves-XOR={bool(R[s]['input_correct'])} | preds={R[s]['preds']}", flush=True)

    G77a = all(R[s]['reservoir_correct'] for s in seeds)
    G77b = all(not R[s]['input_correct'] for s in seeds)   # XOR NOT solvable from inputs alone (sanity)
    passed = G77a and G77b
    print("\n--- VERDICT ---", flush=True)
    print(f"G77a reservoir readout solves XOR (both seeds) : {G77a}", flush=True)
    print(f"G77b XOR NOT linearly separable from inputs    : {G77b}", flush=True)
    verdict = ("PASS - the substrate's nonlinear dynamics make XOR linearly readable: a usable RESERVOIR (learning without writable memory)"
               if passed else "NULL - reservoir readout cannot solve XOR")
    print(f"\nG77: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G77"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
