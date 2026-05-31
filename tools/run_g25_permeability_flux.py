"""G25 — selective permeability measured as inward crossing FLUX (corrects G24's metric)."""
import json
from pathlib import Path
import numpy as np

BOX = np.array([28.0, 28.0, 28.0])
CENTRE = BOX / 2.0
R_SHELL = 6.0
R_CHANNEL = 1.2
F_MEM = 100.0
N_PER_BAND = 300
STEPS = 4000
DT = 0.02
SPEED = 8.0


def compatible(f, f_mem, tol=0.08):
    return abs(f / f_mem - 1.0) <= tol


def seed(rng, n, f_value):
    dirs = rng.normal(size=(n, 3)); dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    start_r = (R_SHELL + rng.uniform(2.0, 6.0, n))[:, None]
    pos = (CENTRE + dirs * start_r) % BOX
    vel = -dirs * SPEED
    return pos, vel, np.full(n, f_value)


def radial(pos):
    d = pos - CENTRE
    d -= BOX * np.round(d / BOX)
    return np.linalg.norm(d, axis=1), d


def run(rule_on, seed_v=0):
    rng = np.random.default_rng(seed_v)
    pc, vc, fc = seed(rng, N_PER_BAND, F_MEM)
    pi, vi, fi = seed(rng, N_PER_BAND, F_MEM * 1000.0)
    pos = np.vstack([pc, pi]); vel = np.vstack([vc, vi])
    freq = np.concatenate([fc, fi])
    band = np.concatenate([np.zeros(N_PER_BAND), np.ones(N_PER_BAND)])
    ever_in = np.zeros(2 * N_PER_BAND, dtype=bool)     # made >=1 inward crossing

    r_prev, _ = radial(pos)
    for _ in range(STEPS):
        prev = pos.copy()
        pos = (pos + vel * DT) % BOX
        r, d = radial(pos)
        if rule_on:
            crossed = ((r_prev - R_SHELL) * (r - R_SHELL) < 0) & (np.abs(r - R_SHELL) < R_CHANNEL + SPEED * DT)
            for k in np.where(crossed)[0]:
                if compatible(freq[k], F_MEM):
                    continue
                n_hat = d[k] / (r[k] + 1e-9)
                vr = np.dot(vel[k], n_hat)
                vel[k] = vel[k] - 2 * vr * n_hat
                pos[k] = prev[k]
                r[k] = r_prev[k]
        ever_in |= (r < R_SHELL)                       # inward crossing achieved
        r_prev = r
    fc_in = float(ever_in[band == 0].mean())
    fi_in = float(ever_in[band == 1].mean())
    return fc_in, fi_in


if __name__ == "__main__":
    print("=== G25: selective permeability by inward-crossing flux ===", flush=True)
    off_c, off_i = np.mean([run(False, s) for s in range(3)], axis=0)
    on_c, on_i = np.mean([run(True, s) for s in range(3)], axis=0)
    print(f"  control (rule OFF): crossed-in compatible={off_c:.3f}  incompatible={off_i:.3f}", flush=True)
    print(f"  G25     (rule ON):  crossed-in compatible={on_c:.3f}  incompatible={on_i:.3f}", flush=True)

    G25a = (off_c > 0.5 and off_i > 0.5 and abs(off_c - off_i) < 0.15)
    G25b = on_i < 0.15
    G25c = on_c > 0.70
    G25d = (on_c - on_i) >= 0.50
    passed = G25a and G25b and G25c and G25d
    print("\n--- VERDICT ---", flush=True)
    print(f"G25a control passes both        : {G25a} (c={off_c:.3f}, i={off_i:.3f})", flush=True)
    print(f"G25b rule blocks incompatible   : {G25b} ({on_i:.3f})", flush=True)
    print(f"G25c rule passes compatible     : {G25c} ({on_c:.3f})", flush=True)
    print(f"G25d selective (gap>=0.50)      : {G25d} ({on_c-on_i:+.3f})", flush=True)
    verdict = ("PASS - a single local 8%-gated reflection rule makes the membrane "
               "SELECTIVELY PERMEABLE (compatible cross, incompatible contained)") if passed else "NULL/partial"
    print(f"\nG25: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G25"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"off_c": off_c, "off_i": off_i, "on_c": on_c, "on_i": on_i, "passed": passed}, indent=2))
    print("DONE", flush=True)
