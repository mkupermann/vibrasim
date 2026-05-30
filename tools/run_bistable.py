"""BET-089: bistable bridge latch. Localized stimulus → do those bridges
latch STRONG and STAY strong after the stimulus stops (memory)?"""
import numpy as np, time, json
from pathlib import Path
from world.config import WorldConfig
from world.state import World
from world.physics import tick

cfg = WorldConfig(
    n_initial_vibrations=400, box_size=(30.0, 30.0, 30.0),
    r_1=5.0, r_2=10.0, freq_tolerance=0.03,
    mol_fusion_enabled=False, resonance_coupling=15.0,
    node_thermal_speed=1.0, atom_valence=3,
    node_freq_binding=False, atom_repulsion_k=1.0, curvature_k=1.0,
    bistable_rate=1.0, bistable_low=1.0, bistable_mid=3.0, bistable_high=6.0,
    bistable_well_k=0.03, bistable_flux_gain=0.05, bistable_flux_ref=40.0,
    pair_decay_time=40.0, triad_decay_time=400.0, dt=0.5,
    n_nodes_max=8192, n_vibrations_max=4096, vibration_soft_cap=500,
    repulsion_k=0.0, lambda_gen=0.006, lambda_dec=0.0,
    neuron_dynamics_enabled=False, stdp_enabled=False,
    slot_recycling_enabled=False, graceful_capacity=True, rng_seed=42,
)
world = World(cfg)
dt = cfg.dt
box = np.asarray(cfg.box_size)
STIM_X = box[0] * 0.25
CTRL_X = box[0] * 0.75

def inject(world, cx, n=25):
    rng = world.rng
    free = np.where(~world.s_alive[:cfg.n_vibrations_max])[0]
    k = min(n, len(free))
    if k == 0: return
    sl = free[:k]
    world.s_pos[sl] = np.column_stack([
        rng.normal(cx, 2.5, k) % box[0],
        rng.normal(box[1]/2, 4, k) % box[1],
        rng.normal(box[2]/2, 4, k) % box[2]])
    world.s_vel[sl] = rng.normal(0, 0.8, (k, 3))
    world.s_freq[sl] = world._sample_frequencies(k)
    world.s_pol[sl] = rng.random(k) < 0.5
    world.s_alive[sl] = True
    world.n_alive = max(world.n_alive, int(sl.max())+1)

def region_mean(world, cx, half=7.0):
    vals = []
    for b in range(world.b_count):
        if not world.b_alive[b]: continue
        i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
        if i >= world.k_count or j >= world.k_count: continue
        mx = (world.k_pos[i][0] + world.k_pos[j][0]) / 2
        if abs(mx - cx) < half:
            vals.append(world.b_strength[b])
    return (float(np.mean(vals)), len(vals)) if vals else (0.0, 0)

log = []; t0 = time.time()
for step in range(40000):
    if step < 12000 and step % 4 == 0:   # STIM phase: drive left region
        inject(world, STIM_X, n=20)
    tick(world, dt)
    if step % 2000 == 1999:
        sm, sn = region_mean(world, STIM_X)
        cm, cn = region_mean(world, CTRL_X)
        # bimodality: fraction near low / near high
        allv = np.array([world.b_strength[b] for b in range(world.b_count) if world.b_alive[b]])
        ph = "STIM" if step < 12000 else "POST"
        frac_strong = float(np.mean(allv > cfg.bistable_mid)) if len(allv) else 0
        e = {"sim_s": round((step+1)*dt,1), "phase": ph,
             "stim_mean": round(sm,2), "stim_n": sn,
             "ctrl_mean": round(cm,2), "ctrl_n": cn,
             "frac_strong": round(frac_strong,2)}
        log.append(e)
        print(f"{e['sim_s']:.0f}s [{ph}]: stim={sm:.2f}(n={sn}) ctrl={cm:.2f}(n={cn}) frac_strong={frac_strong:.2f}", flush=True)
        Path(Path.home()/'.eqmod'/'bet'/'BET-089').mkdir(parents=True, exist_ok=True)
        (Path.home()/'.eqmod'/'bet'/'BET-089'/'log.json').write_text(json.dumps(log, indent=2))
    if time.time()-t0 > 400: break
print("DONE", flush=True)
