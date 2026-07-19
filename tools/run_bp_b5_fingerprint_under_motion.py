"""BP-B5 fingerprint under thermal motion — headless."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from tools.classify_molecules import _ground_atom_decades, species_fingerprint
from world.config import WorldConfig
from world.physics import tick
from world.state import World

SEEDS, N, T = (111, 113), 20, 500


def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(80., 80., 80.),
        n_vibrations_max=128, n_nodes_max=256, rng_seed=seed,
        lambda_gen=0., lambda_dec=0., lambda_dec_mol=0.,
        node_thermal_speed=2.0, mol_fusion_enabled=False,
        repulsion_k=0., speed_min=0., speed_max=0.,
    )


def fdec(d, o=0.0):
    return float(10**d * 3.0 + o)


def plant(w, lab, pos):
    decades = (3, 3) if lab == 0 else (3, 4)
    f0, f1 = fdec(decades[0]), fdec(decades[1], 100.0)
    box = np.array(w.config.box_size)
    a0 = w.allocate_node(pos=(pos + [box[0]*0.3, 0, 0]) % box, freq=f0, pol=True, level=4,
                         constituents=np.array([], dtype=np.int32), comp_kind=1)
    a1 = w.allocate_node(pos=(pos + [0, box[1]*0.3, 0]) % box, freq=f1, pol=True, level=4,
                         constituents=np.array([], dtype=np.int32), comp_kind=1)
    m = w.allocate_node(pos=pos.copy(), freq=f0+f1, pol=True, level=5,
                        constituents=np.array([a0, a1], dtype=np.int32), comp_kind=1)
    w.k_strength[m] = 10.0
    return m


def fp(w, m):
    if not w.k_alive[m]:
        return "A?"
    return species_fingerprint(_ground_atom_decades(w, m))


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    seeds, n, t = ((111,), 6, 100) if args.smoke else (SEEDS, N, T)
    print(f"BP-B5 start smoke={args.smoke} N={n} T={t}")
    ok_t, ok_c, surv = [], [], []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        labs = [0]*(n//2) + [1]*(n - n//2)
        rng.shuffle(labs)
        box = np.array([80., 80., 80.])
        for i, lab in enumerate(labs):
            w = World(cfg(seed))
            pos = rng.uniform(0, 1, 3) * box
            m = plant(w, lab, pos)
            dt = float(w.config.dt)
            for _ in range(t):
                tick(w, dt); w.t += dt
            f = fp(w, m)
            pred = 0 if f == "A33" else (1 if f == "A34" else None)
            ok_t.append(pred == lab)
            surv.append(bool(w.k_alive[m]) and f not in ("A?", ""))
            # scramble control
            w2 = World(cfg(seed))
            m2 = plant(w2, lab, rng.uniform(0, 1, 3) * box)
            st, en = int(w2.k_comp_offset[m2]), int(w2.k_comp_end[m2])
            kids = [int(w2.k_comp_indices[j]) for j in range(st, en)]
            if len(kids) >= 2:
                other = 1 - lab
                d0, d1 = ((3, 3) if other == 0 else (3, 4))
                w2.k_freq[kids[0]] = fdec(d0)
                w2.k_freq[kids[1]] = fdec(d1, 200)
            for _ in range(t):
                tick(w2, dt); w2.t += dt
            f2 = fp(w2, m2)
            p2 = 0 if f2 == "A33" else (1 if f2 == "A34" else None)
            ok_c.append(p2 == lab)
    aT = float(sum(ok_t)/len(ok_t)); aC = float(sum(ok_c)/len(ok_c)); sv = float(sum(surv)/len(surv))
    b1, b2, b5 = aT >= 0.90, aC <= 0.60, sv >= 0.75
    verdict = "PASS" if (b1 and b2 and b5) else "NULL"
    result = {"id": "BP-B5", "bars": {
        "B1_T": {"value": aT, "threshold": 0.90, "pass": b1},
        "B2_scramble": {"value": aC, "threshold": 0.60, "pass": b2},
        "B5_surv": {"value": sv, "threshold": 0.75, "pass": b5},
    }, "verdict": verdict}
    out = Path.home()/".eqmod"/"bet"/"BP-B5"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-B5: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
