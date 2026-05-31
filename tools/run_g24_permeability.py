"""G24 — selective membrane permeability: control (transparent) vs frequency-gated rule.

Physics-faithful: vibration motion replicates world.physics.move_vibrations exactly
(inertial + periodic wrap). The ONLY addition under test is a local 8%-gated reflection
at shell atoms. Self-contained so it runs instantly on this machine.
"""
import json
from pathlib import Path
import numpy as np

BOX = np.array([28.0, 28.0, 28.0])
CENTRE = BOX / 2.0
R_SHELL = 6.0
R_CHANNEL = 1.2          # interaction band around the shell surface
F_MEM = 100.0            # membrane atom frequency
N_SHELL = 42             # Fibonacci-sphere atoms
N_PER_BAND = 300
STEPS = 4000
DT = 0.02
SPEED = 8.0


def fibonacci_sphere(n, radius, centre):
    i = np.arange(n) + 0.5
    phi = np.arccos(1 - 2 * i / n)
    theta = np.pi * (1 + 5 ** 0.5) * i
    x = np.cos(theta) * np.sin(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(phi)
    return centre + radius * np.stack([x, y, z], axis=1)


def compatible(f, f_mem, tol=0.08):
    """8%-family compatibility: |f/f_mem - 1| within tol (and harmonics off)."""
    return abs(f / f_mem - 1.0) <= tol


def seed_vibrations(rng, n, f_value):
    # start OUTSIDE the shell, moving roughly inward
    dirs = rng.normal(size=(n, 3))
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    start_r = R_SHELL + rng.uniform(2.0, 6.0, n)[:, None]
    pos = CENTRE + dirs * start_r
    pos %= BOX
    vel = -dirs * SPEED                      # aimed inward
    freq = np.full(n, f_value)
    return pos, vel, freq


def run(rule_on, seed=0):
    rng = np.random.default_rng(seed)
    shell = fibonacci_sphere(N_SHELL, R_SHELL, CENTRE)
    # two bands
    pos_c, vel_c, f_c = seed_vibrations(rng, N_PER_BAND, F_MEM * 1.0)        # compatible
    pos_i, vel_i, f_i = seed_vibrations(rng, N_PER_BAND, F_MEM * 1000.0)     # incompatible
    pos = np.vstack([pos_c, pos_i]); vel = np.vstack([vel_c, vel_i])
    freq = np.concatenate([f_c, f_i])
    band = np.concatenate([np.zeros(N_PER_BAND), np.ones(N_PER_BAND)])       # 0=compat,1=incompat

    for _ in range(STEPS):
        prev = pos.copy()
        pos = (pos + vel * DT) % BOX                                         # == move_vibrations
        if rule_on:
            # frequency-gated reflection at the shell surface (G24)
            # vector from centre (minimum-image)
            d = pos - CENTRE
            d -= BOX * np.round(d / BOX)
            r = np.linalg.norm(d, axis=1)
            dprev = prev - CENTRE
            dprev -= BOX * np.round(dprev / BOX)
            rprev = np.linalg.norm(dprev, axis=1)
            # crossing the shell surface this step?
            crossed = ((rprev - R_SHELL) * (r - R_SHELL) < 0) & (np.abs(r - R_SHELL) < R_CHANNEL + SPEED * DT)
            for k in np.where(crossed)[0]:
                if compatible(freq[k], F_MEM):
                    continue                                                # compatible passes
                # reflect radial velocity component (specular bounce off the shell)
                n_hat = d[k] / (r[k] + 1e-9)
                vr = np.dot(vel[k], n_hat)
                vel[k] = vel[k] - 2 * vr * n_hat
                pos[k] = prev[k]                                            # don't penetrate this step

    # interior fraction per band
    d = pos - CENTRE
    d -= BOX * np.round(d / BOX)
    inside = np.linalg.norm(d, axis=1) < R_SHELL
    frac_c = float(inside[band == 0].mean())
    frac_i = float(inside[band == 1].mean())
    return frac_c, frac_i


if __name__ == "__main__":
    print("=== G24: selective membrane permeability (control vs rule) ===", flush=True)
    off_c, off_i = np.mean([run(False, s) for s in range(3)], axis=0)
    on_c, on_i = np.mean([run(True, s) for s in range(3)], axis=0)
    print(f"  control (rule OFF): interior compatible={off_c:.3f}  incompatible={off_i:.3f}", flush=True)
    print(f"  G24     (rule ON):  interior compatible={on_c:.3f}  incompatible={on_i:.3f}", flush=True)

    G24a = abs(off_c - off_i) < 0.12
    G24b = on_i < 0.20
    G24c = (on_c - on_i) >= 0.40
    G24d = G24a
    passed = G24a and G24b and G24c and G24d
    print("\n--- VERDICT ---", flush=True)
    print(f"G24a control non-selective (<0.12) : {G24a} (|{off_c-off_i:+.3f}|)", flush=True)
    print(f"G24b rule contains incompatible(<0.20): {G24b} ({on_i:.3f})", flush=True)
    print(f"G24c rule selective (gap>=0.40)    : {G24c} ({on_c-on_i:+.3f})", flush=True)
    print(f"G24d selectivity only with rule    : {G24d}", flush=True)
    verdict = ("PASS - current substrate is non-selectively permeable; a single local "
               "8%-gated reflection rule produces selective permeability") if passed else "NULL/partial"
    print(f"\nG24: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G24"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"off_c": off_c, "off_i": off_i, "on_c": on_c, "on_i": on_i, "passed": passed}, indent=2))
    print("DONE", flush=True)
