"""BET-113 — sequence prediction (predictive world-model step). Train A->B->C..,
recall the whole sequence from the start. --demo plays it as live 3D snapshots.

  python tools/run_bet113_sequence.py            # verdict
  python tools/run_bet113_sequence.py --demo     # play the sequence in 3D (viewer)

Pre-registered bars in docs/amendments/bet_113_sequence.md.
"""
import sys, json, time, os
import numpy as np
from pathlib import Path
from world.energy import EnergyNet, make_patterns

STATE_DIR = Path.home() / '.eqmod' / 'energy'
STATE_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = STATE_DIR / 'state.npz'


def overlaps(rec, seq):
    return [float(np.mean(np.sign(s) == np.sign(p))) for s, p in zip(rec, seq)]


def train_net(L, seed=0):
    net = EnergyNet(n_per_module=40, n_modules=2, p_in=0.6, p_cross=0.05,
                    beta=1.5, seed=seed)
    seq = make_patterns(net, n_patterns=L, seed=7)
    net.train_sequence(seq, lr_T=0.06, lr_W=0.02, assoc_epochs=120)
    return net, seq


def write_snapshot(net, phase, step, acc):
    tmp = STATE_DIR / 'state.tmp.npz'
    np.savez(tmp, pos=net.pos, state=net.state.astype(np.float32),
             module=net.module, W=(net.W * net.M).astype(np.float32),
             phase=np.array(phase), epoch=np.array(step),
             pattern_id=np.array(step), acc=np.array(acc, dtype=np.float32),
             energy=np.array(net.energy(), dtype=np.float32), n_patterns=np.array(5))
    for _ in range(20):
        try:
            os.replace(tmp, STATE_FILE); return
        except PermissionError:
            time.sleep(0.04)


def verdict():
    print("=== BET-113: sequence prediction (predictive world-model) ===", flush=True)
    net, seq = train_net(5)
    rec = net.recall_sequence(seq[0], length=5)
    ov = overlaps(rec, seq)
    print("L=5 per-step overlap:", [round(x, 3) for x in ov], flush=True)
    # one-step predictions
    step_ok = []
    for t in range(len(seq) - 1):
        net.state = seq[t].astype(float)
        nxt = net.predict_step(seq[t].astype(float))
        step_ok.append(float(np.mean(np.sign(nxt) == np.sign(seq[t + 1]))))
    # control: no transitions
    net.T[:] = 0
    ovc = overlaps(net.recall_sequence(seq[0], 5), seq)
    # longer sequence
    net8, seq8 = train_net(8, seed=1)
    ov8 = overlaps(net8.recall_sequence(seq8[0], 8), seq8)

    T113a = min(step_ok) >= 0.90
    T113b = min(ov) >= 0.90
    T113c = max(ovc[1:]) < 0.70
    T113d = min(ov8) >= 0.85
    passed = T113a and T113b and T113c and T113d

    print("\n--- VERDICT ---", flush=True)
    print(f"one-step preds min={min(step_ok):.3f}  full-seq min={min(ov):.3f}  "
          f"control steps>0 max={max(ovc[1:]):.3f}  L8 min={min(ov8):.3f}", flush=True)
    print(f"T113a one-step (>=0.90)        : {T113a}", flush=True)
    print(f"T113b full-sequence (>=0.90)   : {T113b}", flush=True)
    print(f"T113c control fails (<0.70)    : {T113c}", flush=True)
    print(f"T113d longer L=8 (>=0.85)      : {T113d}", flush=True)
    print(f"\nBET-113: {'PASS' if passed else 'NULL/FAIL'}", flush=True)
    if passed:
        print(">>> Predictive world-model primitive: self-supervised next-state "
              "prediction + sequence recall. No transformer.", flush=True)
    out = Path.home() / '.eqmod' / 'bet' / 'BET-113'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'result.json').write_text(json.dumps(
        {"seq5": ov, "one_step": step_ok, "control": ovc, "seq8": ov8,
         "T113a": T113a, "T113b": T113b, "T113c": T113c, "T113d": T113d,
         "passed": passed}, indent=2))
    print("DONE", flush=True)


def demo():
    print("=== BET-113 DEMO — playing the recalled sequence in 3D ===", flush=True)
    print(f"snapshots -> {STATE_FILE}  (start: python tools/viz3d_energy.py)", flush=True)
    net, seq = train_net(5)
    s = np.sign(seq[0]).astype(float)
    step = 0
    try:
        while True:
            for t in range(len(seq)):
                # show the clean stored pattern t (the recalled state)
                net.state = s.copy()
                acc = float(np.mean(np.sign(s) == np.sign(seq[t])))
                write_snapshot(net, f"sequence step {t} (A..E)", t, acc)
                print(f"step {t}: overlap {acc:.2f}", flush=True)
                time.sleep(1.1)
                s = net.predict_step(s)        # predict the next state
            s = np.sign(seq[0]).astype(float)  # loop the sequence
            step += 1
    except KeyboardInterrupt:
        print("\n[demo stopped]", flush=True)


if __name__ == "__main__":
    demo() if "--demo" in sys.argv else verdict()
