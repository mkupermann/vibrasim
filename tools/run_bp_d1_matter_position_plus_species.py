"""BP-D1 joint position+species — continuous lab headless."""
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

SEEDS, N, T, MID = (141, 143), 16, 400, 40.0


def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80., 80., 80.),
        n_vibrations_max=128, n_nodes_max=256, rng_seed=seed,
        lambda_gen=0., lambda_dec=0., lambda_dec_mol=0.,
        node_thermal_speed=0., mol_fusion_enabled=False,
        repulsion_k=0., speed_min=0., speed_max=0.,
    )


def fdec(d, o=0.):
    return float(10**d * 3 + o)


def plant(w, lab, side, rng):
    x = rng.uniform(10, 30) if side == 0 else rng.uniform(50, 70)
    pos = np.array([x, rng.uniform(20, 60), rng.uniform(20, 60)])
    d0, d1 = (3, 3) if lab == 0 else (3, 4)
    f0, f1 = fdec(d0), fdec(d1, 100)
    box = np.array(w.config.box_size)
    a0 = w.allocate_node(pos=(pos + [5, 0, 0]) % box, freq=f0, pol=True, level=4,
                         constituents=np.array([], dtype=np.int32), comp_kind=1)
    a1 = w.allocate_node(pos=(pos + [0, 5, 0]) % box, freq=f1, pol=True, level=4,
                         constituents=np.array([], dtype=np.int32), comp_kind=1)
    m = w.allocate_node(pos=pos.copy(), freq=f0 + f1, pol=True, level=5,
                        constituents=np.array([a0, a1], dtype=np.int32), comp_kind=1)
    w.k_strength[m] = 10.0
    return m


def read_species(w, m):
    if not w.k_alive[m]:
        return None
    f = species_fingerprint(_ground_atom_decades(w, m))
    return 0 if f == "A33" else (1 if f == "A34" else None)


def read_side(w, m):
    if not w.k_alive[m]:
        return None
    return 0 if float(w.k_pos[m, 0]) < MID else 1


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, n, t = ((141,), 4, 80) if args.smoke else (SEEDS, N, T)
    print(f"BP-D1 start smoke={args.smoke} N={n} T={t}")
    jnt, pos_mis, sp_only, surv = [], [], [], []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        for i in range(n):
            lab, side = i % 2, (i // 2) % 2
            w = World(cfg(seed))
            m = plant(w, lab, side, rng)
            dt = float(w.config.dt)
            for _ in range(t):
                tick(w, dt)
                w.t += dt
            ps, sd = read_species(w, m), read_side(w, m)
            jnt.append(ps == lab and sd == side)
            pos_mis.append(sd == lab)
            sp_only.append(ps == lab)
            surv.append(ps is not None and bool(w.k_alive[m]))
    aJ = float(sum(jnt) / len(jnt))
    aP = float(sum(pos_mis) / len(pos_mis))
    aS = float(sum(sp_only) / len(sp_only))
    aV = float(sum(surv) / len(surv))
    b1, b2, b3, b5 = aJ >= 0.85, aP <= 0.60, aS >= 0.90, aV >= 0.80
    verdict = "PASS" if all([b1, b2, b3, b5]) else "NULL"
    result = {"id": "BP-D1", "bars": {
        "B1_joint": {"value": aJ, "threshold": 0.85, "pass": b1},
        "B2_pos_as_species": {"value": aP, "threshold": 0.60, "pass": b2},
        "B3_species": {"value": aS, "threshold": 0.90, "pass": b3},
        "B5_surv": {"value": aV, "threshold": 0.80, "pass": b5},
    }, "verdict": verdict}
    out = Path.home() / ".eqmod" / "bet" / "BP-D1"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-D1: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
