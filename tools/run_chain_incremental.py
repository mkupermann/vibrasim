"""Incremental chain test: short runs with checkpoint/resume.

Each invocation runs for ~60s wall, saves state, exits.
Call repeatedly to accumulate sim time without Numba memory leak.

Usage: python tools/run_chain_incremental.py
"""
import numpy as np
import pickle
import time
import json
import gc
from pathlib import Path
from world.config import WorldConfig
from world.state import World, LEVEL_TO_VIBRATIONS
from world.physics import (move_vibrations, bind_vibrations_to_electrons,
    bind_nodes_upward, decay_unstable_nodes, ambient_regeneration,
    apply_node_resonance, cull_excess_vibrations, move_nodes)

BET_DIR = Path.home() / ".eqmod" / "bet" / "BET-085"
STATE_PATH = BET_DIR / "chain_state.pkl"
LOG_PATH = BET_DIR / "chain_log.json"
RUN_WALL = 60  # seconds per invocation

CFG = WorldConfig(
    n_initial_vibrations=80, box_size=(25.0, 25.0, 25.0),
    r_1=5.0, r_2=10.0, freq_tolerance=0.03,
    mol_fusion_enabled=True, resonance_coupling=15.0,
    node_thermal_speed=5.0,
    pair_decay_time=30.0, triad_decay_time=300.0, dt=0.5,
    n_nodes_max=1024, n_vibrations_max=512, vibration_soft_cap=120,
    repulsion_k=0.0, lambda_gen=0.0005, lambda_dec=0.0,
    neuron_dynamics_enabled=False, stdp_enabled=False, rng_seed=42,
)


def save_state(world, total_steps):
    """Save minimal state for resume."""
    state = {
        'total_steps': total_steps,
        't': world.t,
        'k_count': world.k_count,
        'k_pos': world.k_pos[:world.k_count].copy(),
        'k_vel': world.k_vel[:world.k_count].copy(),
        'k_freq': world.k_freq[:world.k_count].copy(),
        'k_pol': world.k_pol[:world.k_count].copy(),
        'k_level': world.k_level[:world.k_count].copy(),
        'k_alive': world.k_alive[:world.k_count].copy(),
        's_pos': world.s_pos.copy(),
        's_vel': world.s_vel.copy(),
        's_freq': world.s_freq.copy(),
        's_pol': world.s_pol.copy(),
        's_alive': world.s_alive.copy(),
        'n_alive': world.n_alive,
    }
    BET_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, 'wb') as f:
        pickle.dump(state, f)


def load_state(world, state):
    """Restore state into world."""
    K = state['k_count']
    world.t = state['t']
    world.k_count = K
    world.k_pos[:K] = state['k_pos']
    world.k_vel[:K] = state['k_vel']
    world.k_freq[:K] = state['k_freq']
    world.k_pol[:K] = state['k_pol']
    world.k_level[:K] = state['k_level']
    world.k_alive[:K] = state['k_alive']
    world.s_pos[:] = state['s_pos']
    world.s_vel[:] = state['s_vel']
    world.s_freq[:] = state['s_freq']
    world.s_pol[:] = state['s_pol']
    world.s_alive[:] = state['s_alive']
    world.n_alive = state['n_alive']


def main():
    BET_DIR.mkdir(parents=True, exist_ok=True)
    world = World(CFG)
    dt = CFG.dt
    box = np.asarray(CFG.box_size, dtype=np.float64)

    total_steps = 0
    if STATE_PATH.exists():
        state = pickle.load(open(STATE_PATH, 'rb'))
        load_state(world, state)
        total_steps = state['total_steps']
        print(f"Resumed at step {total_steps} (sim {total_steps*dt:.0f}s)", flush=True)
    else:
        print("Fresh start", flush=True)

    # Load existing log
    log = []
    if LOG_PATH.exists():
        log = json.loads(LOG_PATH.read_text())

    t0 = time.time()
    steps_this_run = 0

    while time.time() - t0 < RUN_WALL:
        cull_excess_vibrations(world)
        move_vibrations(world.s_pos, world.s_vel, world.s_alive, box, dt)
        move_nodes(world, dt)
        bind_vibrations_to_electrons(world)
        if total_steps % 5 == 0:
            apply_node_resonance(world, dt * 5)
        bind_nodes_upward(world)
        decay_unstable_nodes(world, dt)
        ambient_regeneration(world, dt)
        world.t += dt
        total_steps += 1
        steps_this_run += 1

    # Snapshot
    K = world.k_count
    alive = world.k_alive[:K]
    levels = world.k_level[:K][alive]
    counts = {}
    for l in range(1, 20):
        c = int(np.sum(levels == l))
        if c > 0:
            counts[str(l)] = c
    mx = int(levels.max()) if len(levels) > 0 else 0
    wall = time.time() - t0

    entry = {"total_steps": total_steps, "sim_s": round(total_steps * dt, 1),
             "this_run_steps": steps_this_run, "wall_s": round(wall, 1),
             "max_level": mx, "counts": counts}
    log.append(entry)
    LOG_PATH.write_text(json.dumps(log, indent=2))

    # Save checkpoint
    save_state(world, total_steps)

    print(f"Run: +{steps_this_run} ticks in {wall:.0f}s wall | "
          f"Total: {total_steps} ({total_steps*dt:.0f}s sim) | "
          f"max={mx} {counts}", flush=True)


if __name__ == "__main__":
    main()
