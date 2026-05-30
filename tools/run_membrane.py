"""BET-086: membrane closure via spontaneous curvature. Background run."""
import numpy as np, time, json
from pathlib import Path
from collections import deque, defaultdict
from numpy.linalg import svd
from world.config import WorldConfig
from world.state import World
from world.physics import tick

cfg = WorldConfig(
    n_initial_vibrations=400, box_size=(28.0, 28.0, 28.0),
    r_1=5.0, r_2=10.0, freq_tolerance=0.03,
    mol_fusion_enabled=False, resonance_coupling=15.0,
    node_thermal_speed=2.0, atom_valence=3,
    node_freq_binding=False, bridge_cooldown=0.0,
    atom_repulsion_k=1.0, curvature_k=2.0,
    pair_decay_time=40.0, triad_decay_time=400.0, dt=0.5,
    n_nodes_max=8192, n_vibrations_max=2048, vibration_soft_cap=500,
    repulsion_k=0.0, lambda_gen=0.012, lambda_dec=0.0,
    neuron_dynamics_enabled=False, stdp_enabled=False,
    slot_recycling_enabled=False, graceful_capacity=True, rng_seed=42,
)
world = World(cfg)
dt = cfg.dt

def biggest(world):
    adj = defaultdict(set)
    for b in range(world.b_count):
        if world.b_alive[b]:
            i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
            adj[i].add(j); adj[j].add(i)
    visited = set(); comps = []
    for s in adj:
        if s in visited: continue
        comp = set(); q = deque([s])
        while q:
            n = q.popleft()
            if n in comp: continue
            comp.add(n)
            for nb in adj[n]:
                if nb not in comp: q.append(nb)
        visited |= comp
        comps.append(comp)
    comps.sort(key=len, reverse=True)
    return (comps[0] if comps else set()), adj

log = []
t0 = time.time()
best_size = 0; best_sv = 0.0
for step in range(60000):
    tick(world, dt)
    if step % 2000 == 1999:
        comp, adj = biggest(world)
        n_atoms = int(np.sum(world.k_alive[:world.k_count] & (world.k_level[:world.k_count] == 4)))
        size = len(comp); deg = 0.0; svr = 0.0; inside = 0
        if size >= 6:
            nodes = list(comp)
            deg = float(np.mean([len(adj[n]) for n in nodes]))
            pos = world.k_pos[nodes]; c = pos.mean(0); _, sv, _ = svd(pos - c)
            svr = float(sv[2] / sv[0])
            radii = np.sqrt(((pos - c) ** 2).sum(1))
            vp = world.s_pos[world.s_alive[:world.s_pos.shape[0]]]
            vd = np.sqrt(((vp - c) ** 2).sum(1))
            inside = int((vd < radii.mean() * 0.6).sum())
        best_size = max(best_size, size)
        best_sv = max(best_sv, svr)
        e = {"sim_s": round((step + 1) * dt, 1), "wall_s": round(time.time() - t0, 1),
             "atoms": n_atoms, "comp": size, "deg": round(deg, 2),
             "sv_ratio": round(svr, 3), "inside": inside}
        log.append(e)
        print(f"{e['sim_s']:.0f}s ({e['wall_s']:.0f}s): atoms={n_atoms} comp={size} deg={deg:.1f} sv={svr:.2f} inside={inside} | best_size={best_size} best_sv={best_sv:.2f}", flush=True)
        Path(Path.home() / ".eqmod" / "bet" / "BET-086").mkdir(parents=True, exist_ok=True)
        (Path.home() / ".eqmod" / "bet" / "BET-086" / "log.json").write_text(json.dumps(log, indent=2))
    if time.time() - t0 > 600:
        break

print(f"\nDONE: best_size={best_size} best_sv_ratio={best_sv:.2f}", flush=True)
