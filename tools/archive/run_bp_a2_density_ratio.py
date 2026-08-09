"""BP-A2 density ratio robustness — headless."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from world.config import WorldConfig
from world.physics import tick
from world.state import World

NS, SEEDS, TRIALS, T = (20, 40, 80), (101, 103), 3, 200


def cfg(seed):
    return WorldConfig(
        n_initial_vibrations=0, box_size=(60., 60., 60.),
        n_vibrations_max=2048, n_nodes_max=512, rng_seed=seed,
        r_1=5., r_2=28., freq_tolerance=0.03,
        pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0.,
    )


def plant(w, n, mode, scramble, seed):
    rng = np.random.default_rng(seed)
    box = np.array(w.config.box_size)
    c = box / 2
    for i in range(n):
        pos = (c + rng.normal(0, 2.0, 3)) % box if mode == "cluster" else rng.uniform(0, 1, 3) * box
        if scramble:
            f = float(np.exp(rng.uniform(np.log(100), np.log(10000))))
        else:
            f = 500.0 if i % 2 == 0 else 500.0 * 1.08
        z, phi = rng.uniform(-1, 1), rng.uniform(0, 2 * np.pi)
        sq = float(np.sqrt(max(1 - z * z, 0)))
        w.s_pos[i] = pos
        w.s_freq[i] = f
        w.s_pol[i] = i % 2 == 0
        w.s_vel[i] = 15 * np.array([sq * np.cos(phi), sq * np.sin(phi), z])
        w.s_alive[i] = True
    w.n_alive = n


def electrons(w):
    return int(((w.k_level[: w.k_count] == 1) & w.k_alive[: w.k_count]).sum())


def arm(seed, ti, n, mode, scramble, ticks):
    w = World(cfg(seed))
    plant(w, n, mode, scramble, seed * 10007 + ti * 13 + n + (1 if scramble else 0) + (2 if mode == "sparse" else 0))
    dt = float(w.config.dt)
    for _ in range(ticks):
        tick(w, dt); w.t += dt
    return electrons(w)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    ns = (20, 40) if args.smoke else NS
    seeds = (101,) if args.smoke else SEEDS
    trials = 1 if args.smoke else TRIALS
    ticks = 100 if args.smoke else T
    print(f"BP-A2 start smoke={args.smoke} N={ns} seeds={seeds}")
    ratios_cs, ratios_sc = [], []
    all_cluster_ok = True
    detail = []
    for n in ns:
        ec, es, escr = [], [], []
        for s in seeds:
            for ti in range(trials):
                c = arm(s, ti, n, "cluster", False, ticks)
                sp = arm(s, ti, n, "sparse", False, ticks)
                sc = arm(s, ti, n, "cluster", True, ticks)
                ec.append(c); es.append(sp); escr.append(sc)
        mc, ms, msc = float(np.mean(ec)), float(np.mean(es)), float(np.mean(escr))
        rcs = mc / max(ms, 1.0)
        rsc = msc / max(mc, 1.0)
        ratios_cs.append(rcs); ratios_sc.append(rsc)
        if mc < 3:
            all_cluster_ok = False
        detail.append({"N": n, "cluster": mc, "sparse": ms, "scramble": msc, "c/s": rcs, "sc/c": rsc})
    m1, m2 = float(np.mean(ratios_cs)), float(np.mean(ratios_sc))
    b1, b2, b3 = m1 >= 2.0, m2 <= 0.55, all_cluster_ok
    verdict = "PASS" if (b1 and b2 and b3) else "NULL"
    result = {
        "id": "BP-A2", "smoke": args.smoke,
        "bars": {
            "B1_cluster_sparse": {"value": m1, "threshold": 2.0, "pass": b1},
            "B2_scramble_cluster": {"value": m2, "threshold": 0.55, "pass": b2},
            "B3_cluster_ge3": {"value": all_cluster_ok, "threshold": True, "pass": b3},
        },
        "detail": detail, "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-A2"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if args.smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-A2: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
