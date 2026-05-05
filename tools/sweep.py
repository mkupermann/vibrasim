"""Parameter sweep harness with grid, random, and Optuna backends."""
from __future__ import annotations
import argparse
import itertools
import json
import math
import time
from dataclasses import replace
from pathlib import Path
from typing import Iterable

import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import tick


def grid_configs(param_ranges: dict) -> Iterable[dict]:
    keys = list(param_ranges.keys())
    for values in itertools.product(*[param_ranges[k] for k in keys]):
        yield dict(zip(keys, values))


def random_configs(param_bounds: dict, n: int, rng_seed: int = 42) -> Iterable[dict]:
    rng = np.random.default_rng(rng_seed)
    for _ in range(n):
        cfg = {}
        for key, (low, high) in param_bounds.items():
            cfg[key] = float(rng.uniform(low, high))
        yield cfg


def run_one_trial(params: dict, snapshot_dir: Path | None = None) -> dict:
    """Run a simulation with `params` overlaid on default WorldConfig.

    Returns a dict with `params`, `objective`, `wall_s`, `final_counts`.
    """
    params = dict(params)  # copy so pop doesn't mutate caller's dict
    duration = float(params.pop("duration", 60.0))
    objective_name = params.pop("objective", "time_to_first_atom")
    base = WorldConfig()
    if "box_size" in params and isinstance(params["box_size"], list):
        params["box_size"] = tuple(params["box_size"])
    cfg = replace(base, **{k: v for k, v in params.items() if hasattr(base, k)})
    w = World(cfg)
    n_ticks = int(duration / cfg.dt)
    start = time.time()
    first_atom_t = math.inf
    for _ in range(n_ticks):
        tick(w, cfg.dt)
        if first_atom_t == math.inf and ((w.k_level == 4) & w.k_alive).any():
            first_atom_t = w.t
    wall = time.time() - start

    counts = {
        "vibr": int(w.s_alive.sum()),
        "e_": int(((w.k_level == 1) & w.k_alive).sum()),
        "pair": int(((w.k_level == 2) & w.k_alive).sum()),
        "triad": int(((w.k_level == 3) & w.k_alive).sum()),
        "atom": int(((w.k_level == 4) & w.k_alive).sum()),
    }

    objective = {
        "time_to_first_atom": first_atom_t,
    }.get(objective_name, math.inf)

    return {
        "params": params,
        "objective": float(objective) if math.isfinite(objective) else None,
        "wall_s": wall,
        "final_counts": counts,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools/sweep.py")
    parser.add_argument("--backend", choices=["grid", "random"], default="grid")
    parser.add_argument("--params-toml", type=Path, required=True,
                        help="TOML defining grid/random ranges")
    parser.add_argument("--duration", type=float, default=60.0)
    parser.add_argument("--objective", type=str, default="time_to_first_atom")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--n-trials", type=int, default=20,
                        help="for random backend")
    args = parser.parse_args(argv)

    import tomllib
    with open(args.params_toml, "rb") as f:
        ranges = tomllib.load(f)

    if args.backend == "grid":
        configs = list(grid_configs(ranges))
    else:
        # ranges are 2-element [low, high] lists for random
        bounds = {k: tuple(v) for k, v in ranges.items()}
        configs = list(random_configs(bounds, args.n_trials))

    args.output.parent.mkdir(parents=True, exist_ok=True)

    if args.workers == 1:
        for cfg in configs:
            cfg["duration"] = args.duration
            cfg["objective"] = args.objective
            result = run_one_trial(cfg)
            with open(args.output, "a") as f:
                f.write(json.dumps(result) + "\n")
            print(f"[{cfg}] objective={result['objective']} counts={result['final_counts']}")
    else:
        from multiprocessing import Pool
        configs_with_meta = [{**c, "duration": args.duration, "objective": args.objective}
                             for c in configs]
        with Pool(args.workers) as pool:
            for result in pool.imap_unordered(run_one_trial, configs_with_meta):
                with open(args.output, "a") as f:
                    f.write(json.dumps(result) + "\n")
                print(f"objective={result['objective']} counts={result['final_counts']}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
