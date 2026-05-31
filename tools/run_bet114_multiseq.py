"""BET-114 — multiple temporal sequences without interference.
Pre-registered bars in docs/amendments/bet_114_multiseq.md.
"""
import json
from pathlib import Path
import numpy as np
from world.energy import EnergyNet, make_patterns

S, L, NPM = 3, 4, 60   # 3 sequences x length 4 = 12 patterns; N=120


def build(seed=0):
    net = EnergyNet(n_per_module=NPM, n_modules=2, p_in=0.6, p_cross=0.05,
                    beta=1.5, seed=seed)
    allp = make_patterns(net, n_patterns=S * L, seed=7)
    seqs = [allp[i * L:(i + 1) * L] for i in range(S)]
    for sq in seqs:
        net.train_sequence(sq, lr_T=0.06, lr_W=0.02, assoc_epochs=120)
    return net, seqs, allp


if __name__ == "__main__":
    print("=== BET-114: multiple sequences without interference ===", flush=True)
    net, seqs, allp = build()

    min_ov = 1.0
    own = tot = 0
    for si, sq in enumerate(seqs):
        rec = net.recall_sequence(sq[0], L)
        ov = [float(np.mean(np.sign(s) == np.sign(p))) for s, p in zip(rec, sq)]
        min_ov = min(min_ov, min(ov))
        # cross-talk: nearest stored pattern of each recalled state in its own seq?
        for s in rec:
            overlaps = [np.mean(np.sign(s) == np.sign(p)) for p in allp]
            nearest = int(np.argmax(overlaps))
            if si * L <= nearest < (si + 1) * L:
                own += 1
            tot += 1
        print(f"sequence {si}: per-step overlap {[round(x,3) for x in ov]}", flush=True)

    # control: shuffled transitions
    rng = np.random.default_rng(99)
    ctrl, cseqs, _ = build(seed=0)
    ctrl.T = rng.permutation(ctrl.T.flatten()).reshape(ctrl.T.shape)
    cmin = 1.0
    for sq in cseqs:
        rec = ctrl.recall_sequence(sq[0], L)
        cmin = min(cmin, min(float(np.mean(np.sign(s) == np.sign(p)))
                             for s, p in zip(rec[1:], sq[1:])))

    T114a = min_ov >= 0.90
    T114b = own >= 10           # of S*L = 12 steps
    T114c = cmin < 0.70
    passed = T114a and T114b and T114c

    print("\n--- VERDICT ---", flush=True)
    print(f"min per-step overlap={min_ov:.3f}  own-sequence={own}/{tot}  "
          f"control min={cmin:.3f}", flush=True)
    print(f"T114a all sequences (>=0.90)  : {T114a}", flush=True)
    print(f"T114b no cross-talk (>=10/12) : {T114b}", flush=True)
    print(f"T114c control fails (<0.70)   : {T114c}", flush=True)
    print(f"\nBET-114: {'PASS' if passed else 'NULL/FAIL'}", flush=True)

    out = Path.home() / '.eqmod' / 'bet' / 'BET-114'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'result.json').write_text(json.dumps(
        {"min_overlap": min_ov, "own": own, "total": tot, "control_min": cmin,
         "T114a": T114a, "T114b": T114b, "T114c": T114c, "passed": passed},
        indent=2))
    print("DONE", flush=True)
