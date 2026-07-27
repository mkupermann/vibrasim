"""BP-B6 two species coexistence — headless continuous lab."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from tools.classify_molecules import _ground_atom_decades, species_fingerprint
from world.config import WorldConfig
from world.physics import tick
from world.state import World

SEEDS, N, T = (121, 123), 15, 500


def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80., 80., 80.),
        n_vibrations_max=128, n_nodes_max=256, rng_seed=seed,
        lambda_gen=0., lambda_dec=0., lambda_dec_mol=0.,
        node_thermal_speed=0., mol_fusion_enabled=False,
        repulsion_k=0., speed_min=0., speed_max=0.,
    )


def fdec(d, o=0.0):
    return float(10**d * 3 + o)


def plant_one(w, decades, pos):
    f0, f1 = fdec(decades[0]), fdec(decades[1], 120.0)
    box = np.array(w.config.box_size)
    a0 = w.allocate_node(pos=(pos+[box[0]*0.25,0,0])%box, freq=f0, pol=True, level=4,
                         constituents=np.array([], dtype=np.int32), comp_kind=1)
    a1 = w.allocate_node(pos=(pos+[0,box[1]*0.25,0])%box, freq=f1, pol=True, level=4,
                         constituents=np.array([], dtype=np.int32), comp_kind=1)
    m = w.allocate_node(pos=pos.copy(), freq=f0+f1, pol=True, level=5,
                        constituents=np.array([a0, a1], dtype=np.int32), comp_kind=1)
    w.k_strength[m] = 10.0
    return m


def fp(w, m):
    if m < 0 or not w.k_alive[m]:
        return "A?"
    return species_fingerprint(_ground_atom_decades(w, m))


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, n, t = ((121,), 4, 80) if args.smoke else (SEEDS, N, T)
    print(f"BP-B6 start smoke={args.smoke} N={n} T={t} seeds={seeds}")
    joint, both_surv, empty_fail = [], [], []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        box = np.array([80., 80., 80.])
        for i in range(n):
            w = World(cfg(seed))
            p0 = rng.uniform(0, 1, 3) * box
            p1 = rng.uniform(0, 1, 3) * box
            m0 = plant_one(w, (3, 3), p0)
            m1 = plant_one(w, (3, 4), p1)
            dt = float(w.config.dt)
            for _ in range(t):
                tick(w, dt); w.t += dt
            f0, f1 = fp(w, m0), fp(w, m1)
            joint.append(f0 == "A33" and f1 == "A34")
            both_surv.append(w.k_alive[m0] and w.k_alive[m1] and f0 != "A?" and f1 != "A?")
            # empty control
            w2 = World(cfg(seed))
            e0 = w2.allocate_node(pos=rng.uniform(0,1,3)*box, freq=5000., pol=True, level=5,
                                  constituents=np.array([], dtype=np.int32), comp_kind=1)
            e1 = w2.allocate_node(pos=rng.uniform(0,1,3)*box, freq=6000., pol=True, level=5,
                                  constituents=np.array([], dtype=np.int32), comp_kind=1)
            for _ in range(t):
                tick(w2, dt); w2.t += dt
            # "correct" would be A33 and A34 — empty should NOT both match
            empty_fail.append(not (fp(w2, e0) == "A33" and fp(w2, e1) == "A34"))
    aJ = float(sum(joint)/len(joint)); aS = float(sum(both_surv)/len(both_surv)); aE = float(sum(empty_fail)/len(empty_fail))
    b1, b2, b5 = aJ >= 0.90, aE >= 0.90, aS >= 0.80
    verdict = "PASS" if (b1 and b2 and b5) else "NULL"
    result = {"id": "BP-B6", "bars": {
        "B1_joint": {"value": aJ, "threshold": 0.90, "pass": b1},
        "B2_empty_not_both": {"value": aE, "threshold": 0.90, "pass": b2},
        "B5_surv": {"value": aS, "threshold": 0.80, "pass": b5},
    }, "verdict": verdict}
    out = Path.home()/".eqmod"/"bet"/"BP-B6"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-B6: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
