"""Run binding cascade for chain/molecule formation. Writes results to JSON."""
import numpy as np
import time
import json
import gc
from pathlib import Path
from world.config import WorldConfig
from world.state import World
from world.physics import (move_vibrations, bind_vibrations_to_electrons,
    bind_nodes_upward, decay_unstable_nodes, ambient_regeneration,
    apply_node_resonance, cull_excess_vibrations, move_nodes)

print("Starting", flush=True)

cfg = WorldConfig(
    n_initial_vibrations=80, box_size=(25.0, 25.0, 25.0),
    r_1=5.0, r_2=10.0, freq_tolerance=0.03,
    mol_fusion_enabled=True, resonance_coupling=15.0,
    node_thermal_speed=5.0,
    pair_decay_time=30.0, triad_decay_time=300.0, dt=0.5,
    n_nodes_max=1024, n_vibrations_max=512, vibration_soft_cap=120,
    repulsion_k=0.0, lambda_gen=0.0005, lambda_dec=0.0,
    neuron_dynamics_enabled=False, stdp_enabled=False,
    numba_jit_enabled=True,
    rng_seed=42,
)
world = World(cfg)
dt = cfg.dt
box = np.asarray(cfg.box_size, dtype=np.float64)

results = []
t0 = time.time()
step = 0
max_wall = 300  # 5 min

while time.time() - t0 < max_wall:
    cull_excess_vibrations(world)
    move_vibrations(world.s_pos, world.s_vel, world.s_alive, box, dt)
    move_nodes(world, dt)
    bind_vibrations_to_electrons(world)
    if step % 5 == 0:
        apply_node_resonance(world, dt * 5)
    bind_nodes_upward(world)
    decay_unstable_nodes(world, dt)
    ambient_regeneration(world, dt)
    world.t += dt
    step += 1

    if step % 50 == 0:
        gc.collect()
    if step % 500 == 0:
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
        entry = {"step": step, "sim_s": round(step * dt, 1), "wall_s": round(wall, 1),
                 "max_level": mx, "counts": counts}
        results.append(entry)
        print(f"{step*dt:.0f}s ({wall:.0f}s wall): max={mx} {counts}", flush=True)

# Save
K = world.k_count
alive = world.k_alive[:K]
levels = world.k_level[:K][alive]
counts = {str(l): int(np.sum(levels == l)) for l in range(1, 20) if np.sum(levels == l) > 0}
mx = int(levels.max()) if len(levels) > 0 else 0
final = {"total_steps": step, "sim_s": round(step * dt, 1),
         "wall_s": round(time.time() - t0, 1),
         "max_level": mx, "counts": counts, "snapshots": results}
outpath = Path.home() / ".eqmod" / "bet" / "BET-085" / "chain_test.json"
outpath.parent.mkdir(parents=True, exist_ok=True)
outpath.write_text(json.dumps(final, indent=2))
print(f"\nFINAL: {step} ticks, {step*dt:.0f}s sim, max={mx} {counts}", flush=True)
print(f"Saved: {outpath}", flush=True)
