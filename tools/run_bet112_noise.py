"""BET-112 — noise robustness / error-correcting recall. Flip a fraction f of a
stored pattern's bits, relax freely, measure recovered overlap. Plot recovery vs f.

Pre-registered bars in docs/amendments/bet_112_noise.md.
"""
import json
from pathlib import Path
import numpy as np
from world.energy import EnergyNet, make_patterns


def recovery_curve(net, pats, levels, trials=40, rng=None):
    rng = rng or np.random.default_rng(11)
    out = {}
    for f in levels:
        accs = []
        for _ in range(trials):
            p = pats[rng.integers(len(pats))]
            noisy = p.copy()
            flip = rng.random(net.N) < f
            noisy[flip] *= -1
            net.state = noisy.astype(float)
            net.relax(None, None, 30)
            accs.append(float(np.mean(np.sign(net.state) == np.sign(p))))
        out[f] = float(np.mean(accs))
    return out


if __name__ == "__main__":
    print("=== BET-112: noise robustness (error-correcting recall) ===", flush=True)
    net = EnergyNet(n_per_module=40, n_modules=2, p_in=0.6, p_cross=0.05,
                    beta=1.5, seed=0)
    pats = make_patterns(net, n_patterns=6, seed=7)
    for _ in range(250):
        net.train_epoch(pats, cue_frac=0.4, lr=0.02, relax_steps=20)

    levels = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
    rec = recovery_curve(net, pats, levels)
    for f in levels:
        print(f"  noise f={f:.2f}  recovered overlap={rec[f]:.3f}", flush=True)

    # shuffled-weight control
    rng = np.random.default_rng(99)
    ctrl = EnergyNet(n_per_module=40, n_modules=2, p_in=0.6, p_cross=0.05,
                     beta=1.5, seed=0)
    flat = rng.permutation(net.W.flatten()).reshape(net.W.shape)
    ctrl.W = 0.5 * (flat + flat.T)
    crec = recovery_curve(ctrl, pats, [0.10], rng=np.random.default_rng(5))[0.10]

    T112a = rec[0.10] >= 0.95
    T112b = all(rec[f] >= 0.90 for f in levels if f <= 0.20)
    T112c = crec < 0.75
    vals = [rec[f] for f in levels]
    T112d = all(vals[i] >= vals[i + 1] - 0.03 for i in range(len(vals) - 1))
    passed = T112a and T112b and T112c and T112d

    print("\n--- VERDICT ---", flush=True)
    print(f"recovery@0.10={rec[0.10]:.3f}  @0.20={rec[0.20]:.3f}  "
          f"control@0.10={crec:.3f}", flush=True)
    print(f"T112a corrects light noise (@0.10>=0.95) : {T112a}", flush=True)
    print(f"T112b basin (f<=0.20 -> >=0.90)          : {T112b}", flush=True)
    print(f"T112c control fails (@0.10<0.75)         : {T112c}", flush=True)
    print(f"T112d graceful (monotone)                : {T112d}", flush=True)
    print(f"\nBET-112: {'PASS' if passed else 'NULL/FAIL'}", flush=True)

    # plot
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        plt.figure(figsize=(8, 5.2))
        plt.plot(levels, [rec[f] for f in levels], 'o-', lw=2, color='#27ae60',
                 label='trained (error-correcting recall)')
        plt.axhline(crec, ls=':', color='gray', label=f'control @0.10 = {crec:.2f}')
        plt.axhline(0.90, ls='--', color='lightgray')
        plt.xlabel('input corruption (fraction of bits flipped)')
        plt.ylabel('recovered overlap with true pattern')
        plt.title('EQMOD-2 energy memory — error-correcting recall (BET-112)')
        plt.ylim(0.45, 1.02); plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
        plt.savefig('bet112_noise.png', dpi=110)
        print("saved bet112_noise.png", flush=True)
    except Exception as e:
        print(f"(plot skipped: {e})", flush=True)

    outdir = Path.home() / '.eqmod' / 'bet' / 'BET-112'
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'result.json').write_text(json.dumps(
        {"recovery": rec, "control_010": crec, "T112a": T112a, "T112b": T112b,
         "T112c": T112c, "T112d": T112d, "passed": passed}, indent=2))
    print("DONE", flush=True)
