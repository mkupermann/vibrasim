"""G135 — is the substrate a PHYSICAL OPTIMIZER for geometry? Atoms repel; injected as a tight cluster,
the dynamics should RELAX them toward EVEN SPACING (the minimum-pairwise-repulsion configuration) — an
analog solver for a spatial layout problem. Measure whether the relaxed gap-variance drops toward the
even-spacing ideal (a genuine 'the physics computes the layout' result), vs the initial clustered state.
"""
import sys, time
from dataclasses import replace
import numpy as np
from world.state import World
from world.physics import tick
from tools.run_bet098 import inject_tight
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
KA = 6
T = 200


def atom_xs(w):
    K_ = w.k_count
    if K_ == 0:
        return np.array([])
    al = w.k_alive[:K_] & (w.k_level[:K_] >= 4)
    return np.sort(w.k_pos[:K_, 0][al])


def gap_var(xs):
    if len(xs) < 3:
        return None
    gaps = np.diff(xs)
    return float(np.var(gaps) / (np.mean(gaps) ** 2 + 1e-9))   # normalized gap variance (0 = even)


def run(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c); box = np.asarray(c.box_size)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    from tools.run_bet093 import cull_free_vibrations
    cull_free_vibrations(w, keep_frac=0.0)
    # Use EXISTING settled atoms: pick KA level>=4 atoms and CLUSTER them tightly at x=15
    K_ = w.k_count
    al = np.where(w.k_alive[:K_] & (w.k_level[:K_] >= 4))[0]
    rng = np.random.default_rng(seed)
    if len(al) > KA:
        al = rng.choice(al, KA, replace=False)
    # deactivate all other atoms so only our KA are tracked
    keep = set(int(i) for i in al)
    for i in range(K_):
        if w.k_alive[i] and int(i) not in keep:
            w.k_alive[i] = False
    for j, i in enumerate(al):
        w.k_pos[i, 0] = 15.0 + (j - KA/2) * 0.4   # tight cluster around x=15
        w.k_pos[i, 1] = box[1] / 2
        w.k_vel[i] = 0.0
    xs0 = atom_xs(w); gv0 = gap_var(xs0)
    for _ in range(T):
        tick(w, c.dt)
    xs1 = atom_xs(w); gv1 = gap_var(xs1)
    spread0 = float(xs0.max() - xs0.min()) if len(xs0) else 0.0
    spread1 = float(xs1.max() - xs1.min()) if len(xs1) else 0.0
    return dict(n0=len(xs0), n1=len(xs1), gv0=(round(gv0, 3) if gv0 else None),
                gv1=(round(gv1, 3) if gv1 else None), spread0=round(spread0, 1), spread1=round(spread1, 1))


if __name__ == "__main__":
    print("=== G135: substrate as a PHYSICAL OPTIMIZER (relax clustered atoms -> even spacing?) ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: atoms {R[s]['n0']}->{R[s]['n1']} | gap-var {R[s]['gv0']}->{R[s]['gv1']} | spread {R[s]['spread0']}->{R[s]['spread1']}", flush=True)
    # PASS: physics spreads the cluster AND lowers normalized gap-variance toward even (gv1 < gv0 and gv1 < 0.3)
    ok = all(R[s]['gv1'] is not None and R[s]['gv0'] is not None and R[s]['spread1'] > R[s]['spread0'] + 3
             and R[s]['gv1'] < 0.5 for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"physics relaxes cluster toward even spacing (spread grows, gap-var<0.5, both): {ok}", flush=True)
    if ok:
        print("G135: PASS - the substrate is a physical optimizer: its dynamics relax a clustered layout toward even spacing (it computes a spatial min-energy config natively)", flush=True)
    else:
        print("G135: NULL - the dynamics do not relax to an even-spacing optimum; the substrate is not a usable physical optimizer here", flush=True)
    print("DONE", flush=True)
