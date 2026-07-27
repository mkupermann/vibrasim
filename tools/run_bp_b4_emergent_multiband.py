"""BP-B4 — emergent multi-band content decode. Headless lab."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from world.config import WorldConfig
from world.physics import tick
from world.state import World

DRIVES = {0: (100.0, 800.0), 1: (800.0, 3000.0), 2: (3000.0, 12000.0)}
SAME = (100.0, 12000.0)
SEEDS, N_FULL, T_FULL = (81, 83), 15, 1000
BARS = dict(B1=0.75, B2=0.45, B3=0.45, B4=0.50, B5=0.80)


def cfg(seed, flo, fhi):
    return WorldConfig(
        n_initial_vibrations=600, box_size=(60., 60., 60.),
        n_vibrations_max=2048, n_nodes_max=2048, rng_seed=seed,
        freq_min=flo, freq_max=fhi, freq_distribution="log",
        r_1=5.0, r_2=28.0, freq_tolerance=0.030,
        pair_decay_time=60., triad_decay_time=600.,
        lambda_gen=0., lambda_dec=0., lambda_dec_mol=0.,
    )


def run_world(seed, flo, fhi, ticks):
    w = World(cfg(seed, flo, fhi))
    dt = float(w.config.dt)
    for _ in range(ticks):
        tick(w, dt); w.t += dt
    return w


def mean_decade(w):
    ds = []
    for i in range(w.k_count):
        if w.k_alive[i] and int(w.k_level[i]) >= 4:
            ds.append(int(math.floor(math.log10(max(float(w.k_freq[i]), 1.0)))))
    if not ds:
        return None, 0
    return float(np.mean(ds)), len(ds)


def decode_md(md):
    if md is None:
        return None
    if md < 2.7:
        return 0
    if md < 3.5:
        return 1
    return 2


def schedule(n, rng):
    per = n // 3
    labs = [0]*per + [1]*per + [2]*(n - 2*per)
    rng.shuffle(labs)
    return labs


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args(argv)
    if args.smoke:
        seeds, n, t, smoke = (81,), 6, 400, True
    else:
        seeds, n, t, smoke = SEEDS, N_FULL, T_FULL, False
    print(f"BP-B4 start smoke={smoke} N={n} T={t} seeds={seeds}")

    T_rows, C1_rows = [], []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        labs = schedule(n, rng)
        for i, lab in enumerate(labs):
            ts = int(seed * 1000003 + i * 97 + lab)
            flo, fhi = DRIVES[lab]
            w = run_world(ts, flo, fhi, t)
            md, n4 = mean_decade(w)
            pred = decode_md(md)
            T_rows.append({"lab": lab, "md": md, "n4": n4, "pred": pred,
                           "ok": pred == lab, "pop": n4 >= 1})
            w1 = run_world(ts + 11, SAME[0], SAME[1], t)
            md1, n41 = mean_decade(w1)
            p1 = decode_md(md1)
            C1_rows.append({"lab": lab, "ok": p1 == lab, "pop": n41 >= 1})

    # C2 shuffle
    rng2 = np.random.default_rng(20260719)
    sh = [r["lab"] for r in T_rows]
    rng2.shuffle(sh)
    c2 = [decode_md(r["md"]) == lab for r, lab in zip(T_rows, sh)]
    # C3 n4 tercile
    n4s = [r["n4"] for r in T_rows]
    qs = np.quantile(n4s, [0.33, 0.66]) if n4s else [0, 0]

    def terc(n4):
        if n4 <= qs[0]:
            return 0
        if n4 <= qs[1]:
            return 1
        return 2

    c3 = [terc(r["n4"]) == r["lab"] for r in T_rows]

    def acc(flags):
        return float(sum(flags) / len(flags)) if flags else 0.0

    aT = acc([r["ok"] for r in T_rows])
    aC1 = acc([r["ok"] for r in C1_rows])
    aC2 = acc(c2)
    aC3 = acc(c3)
    pop = acc([r["pop"] for r in T_rows])
    b1, b2, b3, b4, b5 = aT >= BARS["B1"], aC1 <= BARS["B2"], aC2 <= BARS["B3"], aC3 <= BARS["B4"], pop >= BARS["B5"]
    verdict = "PASS" if all([b1, b2, b3, b4, b5]) else "NULL"
    result = {
        "id": "BP-B4", "smoke": smoke, "seeds": list(seeds),
        "bars": {
            "B1_T": {"value": aT, "threshold": BARS["B1"], "pass": b1},
            "B2_C1": {"value": aC1, "threshold": BARS["B2"], "pass": b2},
            "B3_C2": {"value": aC2, "threshold": BARS["B3"], "pass": b3},
            "B4_C3": {"value": aC3, "threshold": BARS["B4"], "pass": b4},
            "B5_pop": {"value": pop, "threshold": BARS["B5"], "pass": b5},
        },
        "sample": T_rows[:6], "verdict": verdict,
    }
    out = Path.home() / ".eqmod" / "bet" / "BP-B4"
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("result_smoke.json" if smoke else "result.json")
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for k, v in result["bars"].items():
        print(f"  {k}: {v['value']:.4f} thr={v['threshold']} pass={v['pass']}")
    print(f"--- VERDICT ---\nBP-B4: {verdict}\nwrote {path}\nDONE")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
