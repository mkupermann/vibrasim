"""BET-088: does a membrane shell with plastic bridges develop a
stable, non-uniform bridge-strength pattern (proto-memory)?"""
import numpy as np, time, json
from pathlib import Path
from world.config import WorldConfig
from world.state import World
from world.physics import tick

cfg = WorldConfig(
    n_initial_vibrations=400, box_size=(28.0, 28.0, 28.0),
    r_1=5.0, r_2=10.0, freq_tolerance=0.03,
    mol_fusion_enabled=False, resonance_coupling=15.0,
    node_thermal_speed=2.0, atom_valence=3,
    node_freq_binding=False, atom_repulsion_k=1.0, curvature_k=2.0,
    flux_plasticity_rate=0.2, flux_max_strength=10.0,
    pair_decay_time=40.0, triad_decay_time=400.0, dt=0.5,
    n_nodes_max=8192, n_vibrations_max=2048, vibration_soft_cap=500,
    repulsion_k=0.0, lambda_gen=0.012, lambda_dec=0.0,
    neuron_dynamics_enabled=False, stdp_enabled=False,
    slot_recycling_enabled=False, graceful_capacity=True, rng_seed=99,
)
world = World(cfg)
dt = cfg.dt

def shell_strengths(world):
    """Return (bridge_key -> strength) for alive bridges, keyed by atom pair."""
    out = {}
    for b in range(world.b_count):
        if world.b_alive[b]:
            i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
            if i < world.k_count and j < world.k_count and world.k_alive[i] and world.k_alive[j]:
                out[(min(i, j), max(i, j))] = float(world.b_strength[b])
    return out

log = []
t0 = time.time()
prev = None
for step in range(40000):
    tick(world, dt)
    if step % 2000 == 1999:
        s = shell_strengths(world)
        if len(s) < 5:
            print(f"{(step+1)*dt:.0f}s: only {len(s)} bridges", flush=True)
            continue
        vals = np.array(list(s.values()))
        cv = float(vals.std() / max(vals.mean(), 1e-6))
        max_frac = float(np.mean(vals >= cfg.flux_max_strength * 0.99))
        # autocorrelation with previous snapshot (shared bridges)
        autocorr = None
        if prev is not None:
            shared = set(s) & set(prev)
            if len(shared) >= 5:
                a = np.array([s[k] for k in shared])
                bb = np.array([prev[k] for k in shared])
                if a.std() > 1e-6 and bb.std() > 1e-6:
                    autocorr = float(np.corrcoef(a, bb)[0, 1])
        e = {"sim_s": round((step+1)*dt,1), "n_bridges": len(s),
             "cv": round(cv,3), "max_frac": round(max_frac,3),
             "autocorr": round(autocorr,3) if autocorr is not None else None}
        log.append(e)
        ac = f"{autocorr:.2f}" if autocorr is not None else "--"
        print(f"{e['sim_s']:.0f}s: bridges={len(s)} cv={cv:.2f} max_frac={max_frac:.2f} autocorr={ac}", flush=True)
        Path(Path.home()/'.eqmod'/'bet'/'BET-088').mkdir(parents=True, exist_ok=True)
        (Path.home()/'.eqmod'/'bet'/'BET-088'/'log.json').write_text(json.dumps(log, indent=2))
        prev = s
    if time.time()-t0 > 400:
        break
print("DONE", flush=True)
