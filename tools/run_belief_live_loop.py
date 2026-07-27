"""Always-on live 3D — continuous vibration FIELD layers + bound matter.

Usage:
    python tools/run_belief_live_loop.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# Safe OpenGL by default (no MSAA) — set EQMOD_GL_QUALITY=1 only if stable
os.environ.setdefault("EQMOD_FIELD_RES", "40")
os.environ.setdefault("AMD_POWERXPRESS_REQUEST_HIGH_PERFORMANCE", "1")
os.environ.setdefault("EQMOD_GL_QUALITY", "0")

from world.gpu_viz import configure_pyvista_gpu, print_gpu_help, request_high_performance_gpu
from world.bet_live import BetLiveView
from world.config import WorldConfig
from world.state import World
from world.physics import tick

request_high_performance_gpu()


def plant_cluster(world: World, n: int = 160, seed: int = 42) -> None:
    rng = np.random.default_rng(seed)
    box = np.asarray(world.config.box_size, dtype=np.float64)
    centre = box / 2.0
    sigma = 8.0  # wider so field covers the sheets
    for i in range(n):
        pos = (centre + rng.normal(0.0, sigma, size=3)) % box
        # spread frequencies across layers (decades)
        decade = 2 + (i % 4)  # 100s .. 10000s-ish
        base = 10.0 ** decade
        freq = base * float(rng.uniform(1.0, 3.0))
        if i % 2 == 1:
            freq *= 1.08  # binding-eligible partners
        z = rng.uniform(-1.0, 1.0)
        phi = rng.uniform(0.0, 2.0 * np.pi)
        sq = float(np.sqrt(max(1.0 - z * z, 0.0)))
        world.s_pos[i] = pos
        world.s_freq[i] = freq
        world.s_pol[i] = bool(i % 2 == 0)
        world.s_vel[i] = 10.0 * np.array([sq * np.cos(phi), sq * np.sin(phi), z])
        world.s_alive[i] = True
    world.n_alive = n


def main() -> int:
    cfg = WorldConfig(
        n_initial_vibrations=0,
        box_size=(50.0, 50.0, 50.0),
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
    print("BELIEF LIVE — continuous field layers (not particles)")
    print("  SHEETS = free vibration field by frequency dimension")
    print("  ORANGE = electrons   WHITE = atoms")
    print("  space=pause  s=step  r=camera  q=quit")
    configure_pyvista_gpu(8, True)
    print_gpu_help()

    world = World(cfg)
    plant_cluster(world, n=160, seed=7)
    # Warm a few ticks so field has phase motion before show
    for _ in range(5):
        tick(world, cfg.dt)
        world.t += cfg.dt

    view = BetLiveView(title="BELIEF LIVE — field layers [stable, no flicker]")
    if not view.open(world):
        print("Could not open window")
        return 1

    cycle = 0
    try:
        while view._window_alive() and not view._user_quit:
            cycle += 1
            n_free = int(world.s_alive.sum())
            # Replant when field sources nearly gone — keep field alive
            if n_free < 20:
                world = World(cfg)
                plant_cluster(world, n=160, seed=7 + cycle * 5)
                print(f"[live] cycle {cycle}: replanted field sources ({160})")
            view.run_ticks(
                world,
                300,
                float(cfg.dt),
                ticks_per_frame=2,
                hud_fn=lambda w, d, n, c=cycle: (
                    f"cycle {c}  {d}/{n}  WATCH sheets undulate; orange=electrons"
                ),
            )
            if view._user_quit:
                break
    finally:
        view.close()
    print("live loop ended")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
