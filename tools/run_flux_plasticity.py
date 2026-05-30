"""BET-087: flux-driven bridge plasticity. Does a stimulated region's
bridges strengthen relative to control, and persist after stimulus?"""
import numpy as np, time, json
from pathlib import Path
from world.config import WorldConfig
from world.state import World
from world.physics import tick

cfg = WorldConfig(
    n_initial_vibrations=300, box_size=(30.0, 30.0, 30.0),
    r_1=5.0, r_2=10.0, freq_tolerance=0.03,
    mol_fusion_enabled=False, resonance_coupling=15.0,
    node_thermal_speed=1.0, atom_valence=3,
    node_freq_binding=False, atom_repulsion_k=1.0, curvature_k=1.0,
    flux_plasticity_rate=0.5, flux_threshold=3.0, flux_decay=0.02,
    pair_decay_time=40.0, triad_decay_time=400.0, dt=0.5,
    n_nodes_max=8192, n_vibrations_max=4096, vibration_soft_cap=600,
    repulsion_k=0.0, lambda_gen=0.012, lambda_dec=0.0,
    neuron_dynamics_enabled=False, stdp_enabled=False,
    slot_recycling_enabled=False, graceful_capacity=True, rng_seed=42,
)
world = World(cfg)
dt = cfg.dt
box = np.asarray(cfg.box_size)

# Stimulus region: left third of box. Control: right third.
def stim_region_x(): return box[0] * 0.25
def ctrl_region_x(): return box[0] * 0.75

def inject_stimulus(world, cx, n=20):
    """Inject n vibrations clustered near x=cx."""
    rng = world.rng
    free = np.where(~world.s_alive[:cfg.n_vibrations_max])[0]
    k = min(n, len(free))
    if k == 0: return
    slots = free[:k]
    world.s_pos[slots] = np.column_stack([
        rng.normal(cx, 3.0, k) % box[0],
        rng.uniform(0, box[1], k),
        rng.uniform(0, box[2], k),
    ])
    world.s_vel[slots] = world._sample_velocities_3d(k)
    world.s_freq[slots] = world._sample_frequencies(k)
    world.s_pol[slots] = rng.random(k) < 0.5
    world.s_alive[slots] = True
    world.n_alive = max(world.n_alive, int(slots.max()) + 1)

def region_bridge_strength(world, cx, half=6.0):
    """Mean strength of bridges whose midpoint is near x=cx."""
    strs = []
    for b in range(world.b_count):
        if not world.b_alive[b]: continue
        i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
        if i >= world.k_count or j >= world.k_count: continue
        mx = (world.k_pos[i][0] + world.k_pos[j][0]) / 2
        if abs(mx - cx) < half:
            strs_val = world.b_strength[b]
            strs.append(strs_val)
    return (float(np.mean(strs)), len(strs)) if strs else (0.0, 0)

log = []
t0 = time.time()
phase = "stimulus"
for step in range(40000):
    # Phase 1 (0-10000 steps): stimulate left region every 5 ticks
    # Phase 2 (10000+): stop stimulus, measure persistence
    if step < 10000 and step % 5 == 0:
        inject_stimulus(world, stim_region_x(), n=15)
    tick(world, dt)
    if step % 2000 == 1999:
        s_str, s_n = region_bridge_strength(world, stim_region_x())
        c_str, c_n = region_bridge_strength(world, ctrl_region_x())
        ratio = s_str / max(c_str, 0.01)
        ph = "STIM" if step < 10000 else "POST"
        e = {"sim_s": round((step+1)*dt,1), "phase": ph,
             "stim_str": round(s_str,2), "stim_n": s_n,
             "ctrl_str": round(c_str,2), "ctrl_n": c_n, "ratio": round(ratio,2)}
        log.append(e)
        print(f"{e['sim_s']:.0f}s [{ph}]: stim={s_str:.2f}(n={s_n}) ctrl={c_str:.2f}(n={c_n}) ratio={ratio:.2f}", flush=True)
        Path(Path.home()/'.eqmod'/'bet'/'BET-087').mkdir(parents=True, exist_ok=True)
        (Path.home()/'.eqmod'/'bet'/'BET-087'/'log.json').write_text(json.dumps(log, indent=2))
    if time.time() - t0 > 400:
        break

print(f"\nDONE", flush=True)
