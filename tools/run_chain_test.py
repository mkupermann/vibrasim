"""Run binding cascade to test molecule formation. 2 min wall limit."""
import numpy as np
import time
import json
from pathlib import Path
from world.config import WorldConfig
from world.state import World
from world.physics import (move_vibrations, bind_vibrations_to_electrons,
    bind_nodes_upward, decay_unstable_nodes, ambient_regeneration,
    apply_node_resonance, cull_excess_vibrations)

# JIT warmup
w = World(WorldConfig(n_initial_vibrations=10, rng_seed=1, resonance_coupling=1.0, mol_fusion_enabled=True))
box_w = np.asarray(w.config.box_size, dtype=np.float64)
move_vibrations(w.s_pos, w.s_vel, w.s_alive, box_w, w.config.dt)
bind_vibrations_to_electrons(w)
bind_nodes_upward(w)
ambient_regeneration(w, w.config.dt)
apply_node_resonance(w, 0.1)
del w
print("JIT warm", flush=True)

cfg = WorldConfig(
    n_initial_vibrations=200, box_size=(30.0, 30.0, 30.0),
    r_1=5.0, r_2=10.0, freq_tolerance=0.02,
    mol_fusion_enabled=True, resonance_coupling=10.0,
    pair_decay_time=15.0, triad_decay_time=120.0, dt=0.1,
    n_nodes_max=4096, n_vibrations_max=2048, vibration_soft_cap=300,
    repulsion_k=0.0, lambda_gen=0.001, lambda_dec=0.0,
    neuron_dynamics_enabled=False, stdp_enabled=False, rng_seed=42,
)
world = World(cfg)
dt = cfg.dt
box = np.asarray(cfg.box_size, dtype=np.float64)

results = []
t0 = time.time()
step = 0

# Minimal tick loop — only essential physics
while time.time() - t0 < 120:  # 2 min wall
    cull_excess_vibrations(world)
    move_vibrations(world.s_pos, world.s_vel, world.s_alive, box, dt)
    bind_vibrations_to_electrons(world)
    if step % 10 == 0:
        apply_node_resonance(world, dt * 10)
    bind_nodes_upward(world)
    decay_unstable_nodes(world, dt)
    ambient_regeneration(world, dt)
    world.t += dt
    step += 1

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
                 "t_per_s": round(step / wall), "max_level": mx, "counts": counts,
                 "k_count": int(K), "n_alive": int(alive.sum())}
        results.append(entry)
        print(f"{step*dt:.0f}s ({wall:.0f}s wall, {step/wall:.0f}t/s): max={mx} {counts} "
              f"[k={K} alive={int(alive.sum())}]", flush=True)

# Save
final = {"total_steps": step, "sim_s": round(step * dt, 1),
         "wall_s": round(time.time() - t0, 1),
         "max_level": results[-1]["max_level"] if results else 0,
         "counts": results[-1]["counts"] if results else {},
         "snapshots": results}
outpath = Path.home() / ".eqmod" / "bet" / "BET-084" / "chain_test.json"
outpath.parent.mkdir(parents=True, exist_ok=True)
outpath.write_text(json.dumps(final, indent=2))
print(f"\nSaved: {outpath}", flush=True)
