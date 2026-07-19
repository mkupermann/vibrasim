"""Always-on live 3D loop for the belief path (watch while agent works).

Cycles a dense cluster binding demo forever until you close the window or Ctrl+C.

Usage:
    python tools/run_belief_live_loop.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from world.bet_live import BetLiveView
from world.config import WorldConfig
from world.physics import tick
from world.state import World


def plant_cluster(world: World, n: int = 80, seed: int = 42) -> None:
    rng = np.random.default_rng(seed)
    box = np.asarray(world.config.box_size, dtype=np.float64)
    centre = box / 2.0
    for i in range(n):
        pos = (centre + rng.normal(0.0, 2.5, size=3)) % box
        freq = 500.0 if (i % 2 == 0) else 500.0 * 1.08
        z = rng.uniform(-1.0, 1.0)
        phi = rng.uniform(0.0, 2.0 * np.pi)
        sq = float(np.sqrt(max(1.0 - z * z, 0.0)))
        world.s_pos[i] = pos
        world.s_freq[i] = freq
        world.s_pol[i] = bool(i % 2 == 0)
        world.s_vel[i] = 15.0 * np.array([sq * np.cos(phi), sq * np.sin(phi), z])
        world.s_alive[i] = True
    world.n_alive = n


def main() -> int:
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(60.0, 60.0, 60.0),
        n_vibrations_max=2048,
        n_nodes_max=512,
        rng_seed=42,
        r_1=5.0,
        r_2=28.0,
        freq_tolerance=0.030,
        pair_decay_time=60.0,
        triad_decay_time=600.0,
        lambda_gen=0.0,
        lambda_dec=0.0,
    )
    world = World(cfg)
    plant_cluster(world, n=100, seed=7)
    view = BetLiveView(title="BELIEF LIVE — density→bind loop (space pause, q quit cycle)")
    if not view.open(world):
        print("Could not open PyVista window")
        return 1
    cycle = 0
    try:
        while view._window_alive() and not view._user_quit:
            cycle += 1
            # re-seed every ~400 ticks so structure keeps forming
            if cycle == 1 or (int(world.t / cfg.dt) % 400 == 0 and int(world.t) > 0):
                # soft reset: clear nodes, replant vibrations
                world = World(cfg)
                plant_cluster(world, n=100, seed=7 + cycle)
            view.run_ticks(
                world, 120, float(cfg.dt),
                ticks_per_frame=4,
                hud_fn=lambda w, d, n: f"cycle {cycle}  tick {d}/{n}  ALWAYS-ON LIVE",
            )
            if view._user_quit:
                break
    finally:
        view.close()
    print("live loop ended")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
