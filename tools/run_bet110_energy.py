"""BET-110 — energy-based self-supervised pattern completion (EQMOD-2).

Default: train self-supervised, evaluate the pre-registered bars, print the
verdict, write result.json. Writes a live snapshot for the 3D viewer throughout.

  python tools/run_bet110_energy.py            # verdict run (fast)
  python tools/run_bet110_energy.py --demo     # slow, watchable: stream snapshots
                                                # for tools/viz3d_energy.py

Pre-registered bars in docs/amendments/bet_110_energy_completion.md.
"""
import sys, os, json, time
import numpy as np
from pathlib import Path
from world.energy import EnergyNet, make_patterns

STATE_DIR = Path.home() / '.eqmod' / 'energy'
STATE_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = STATE_DIR / 'state.npz'

N_PATTERNS = 6
CUE_FRAC = 0.4
EPOCHS = 300
SEED = 0


def write_snapshot(net, phase, epoch, pattern_id, acc):
    """Atomically write the current state for the 3D viewer (1-2 s polling)."""
    tmp = STATE_DIR / 'state.tmp.npz'   # np.savez requires a .npz-ending name
    np.savez(tmp, pos=net.pos, state=net.state.astype(np.float32),
             module=net.module, W=(net.W * net.M).astype(np.float32),
             phase=np.array(phase), epoch=np.array(epoch),
             pattern_id=np.array(pattern_id), acc=np.array(acc, dtype=np.float32),
             energy=np.array(net.energy(), dtype=np.float32),
             n_patterns=np.array(N_PATTERNS))
    # Windows: os.replace fails if a reader (the viewer) holds the file open —
    # retry briefly instead of crashing the producer.
    for _ in range(20):
        try:
            os.replace(tmp, STATE_FILE)
            return
        except PermissionError:
            time.sleep(0.04)


def content_addressable(net, patterns, cue_frac, rng):
    """For each pattern i: cue it, relax, check masked-unit overlap argmax == i."""
    right = 0
    for i, p in enumerate(patterns):
        net.state = rng.choice([-1.0, 1.0], net.N)
        cue = rng.random(net.N) < cue_frac
        ci = np.where(cue)[0]
        masked = np.where(~cue)[0]
        s = net.relax(ci, p[ci], 30)
        if len(masked) == 0:
            right += 1; continue
        overlaps = [np.mean(np.sign(s[masked]) == np.sign(q[masked])) for q in patterns]
        if int(np.argmax(overlaps)) == i:
            right += 1
    return right


def verdict_run():
    print("=== BET-110: energy-based self-supervised pattern completion ===", flush=True)
    net = EnergyNet(n_per_module=40, n_modules=2, p_in=0.6, p_cross=0.05,
                    beta=1.5, seed=SEED)
    pats = make_patterns(net, n_patterns=N_PATTERNS, seed=7)
    base = net.recall_accuracy(pats, cue_frac=CUE_FRAC, trials=30)
    print(f"untrained completion: {base:.3f}", flush=True)

    for ep in range(1, EPOCHS + 1):
        net.train_epoch(pats, cue_frac=CUE_FRAC, lr=0.02, relax_steps=20)
        if ep % 30 == 0:
            a = net.recall_accuracy(pats, cue_frac=CUE_FRAC, trials=30)
            write_snapshot(net, f"train", ep, -1, a)
            print(f"epoch {ep:3d}: completion {a:.3f}", flush=True)

    trained = net.recall_accuracy(pats, cue_frac=CUE_FRAC, trials=60)
    # shuffled-weight control (same magnitudes, scrambled structure)
    rng = np.random.default_rng(99)
    ctrl = EnergyNet(n_per_module=40, n_modules=2, p_in=0.6, p_cross=0.05,
                     beta=1.5, seed=SEED)
    flat = rng.permutation(net.W.flatten()).reshape(net.W.shape)
    ctrl.W = 0.5 * (flat + flat.T)
    control = ctrl.recall_accuracy(pats, cue_frac=CUE_FRAC, trials=60)
    ca = content_addressable(net, pats, CUE_FRAC, np.random.default_rng(3))

    T110a = True  # zero labels by construction (only masked completion of the patterns)
    T110b = trained >= 0.90
    T110c = control < 0.65
    T110d = ca >= N_PATTERNS - 1
    passed = T110a and T110b and T110c and T110d

    print("\n--- VERDICT ---", flush=True)
    print(f"trained completion={trained:.3f}  control={control:.3f}  "
          f"content-addr={ca}/{N_PATTERNS}", flush=True)
    print(f"T110a self-supervised (no labels) : {T110a}", flush=True)
    print(f"T110b learning (>=0.90)           : {T110b}", flush=True)
    print(f"T110c control fails (<0.65)        : {T110c}", flush=True)
    print(f"T110d content-addressable (>={N_PATTERNS-1}/{N_PATTERNS}) : {T110d}", flush=True)
    print(f"\nBET-110: {'PASS' if passed else 'NULL/FAIL'}", flush=True)
    if passed:
        print(">>> First genuine learning in EQMOD: geometric, energy-based, "
              "self-supervised, content-addressable. No transformer.", flush=True)
    out = STATE_DIR / 'result.json'
    out.write_text(json.dumps({"trained": trained, "control": control,
                               "content_addr": ca, "n_patterns": N_PATTERNS,
                               "T110a": T110a, "T110b": T110b, "T110c": T110c,
                               "T110d": T110d, "passed": passed}, indent=2))
    write_snapshot(net, "done", EPOCHS, -1, trained)
    print("DONE", flush=True)
    return passed


def demo_run():
    """Slow, watchable: interleave training and recalls, streaming snapshots so
    tools/viz3d_energy.py shows the net relaxing into attractors and weights
    growing. Runs until Ctrl+C."""
    print("=== BET-110 DEMO — streaming snapshots for the 3D viewer ===", flush=True)
    print(f"snapshots -> {STATE_FILE}   (start: python tools/viz3d_energy.py)", flush=True)
    net = EnergyNet(n_per_module=40, n_modules=2, p_in=0.6, p_cross=0.05,
                    beta=1.5, seed=SEED)
    pats = make_patterns(net, n_patterns=N_PATTERNS, seed=7)
    rng = np.random.default_rng(5)
    ep = 0
    try:
        while True:
            # a few training epochs
            for _ in range(5):
                net.train_epoch(pats, cue_frac=CUE_FRAC, lr=0.02, relax_steps=20)
                ep += 1
            acc = net.recall_accuracy(pats, cue_frac=CUE_FRAC, trials=20)
            write_snapshot(net, "train", ep, -1, acc)
            print(f"epoch {ep}: completion {acc:.3f}", flush=True)
            time.sleep(0.8)
            # a recall: cue a pattern, stream the relaxation settling into a valley
            i = rng.integers(N_PATTERNS); p = pats[i]
            net.state = rng.choice([-1.0, 1.0], net.N)
            cue = rng.random(net.N) < CUE_FRAC; ci = np.where(cue)[0]
            frames = []
            net.relax(ci, p[ci], 30, record=frames)
            for k, fr in enumerate(frames[::2]):
                net.state = fr
                write_snapshot(net, f"recall p{i}", ep, int(i),
                               float(np.mean(np.sign(fr) == np.sign(p))))
                time.sleep(0.15)
            time.sleep(0.8)
    except KeyboardInterrupt:
        print("\n[demo stopped]", flush=True)


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo_run()
    else:
        verdict_run()
