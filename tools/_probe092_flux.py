"""BET-092 baseline flux probe. No stimulus. Measures resting per-bridge flux
on the persistent lattice and reports the 90th percentile -> flux_ref, per the
pre-registered rule in docs/amendments/bet_092_populated_latch_drive.md.
"""
import sys, json
import numpy as np
from pathlib import Path
import tools.run_bet091 as r
from world.state import World
from world.physics import tick


def per_bridge_flux(world, cfg):
    """Replicate apply_bistable_plasticity's flux: density_i * density_j."""
    box = np.asarray(cfg.box_size, dtype=np.float64)
    r_sense_sq = cfg.r_2 * cfg.r_2
    K = world.k_count
    atoms = set()
    for b in range(world.b_count):
        if world.b_alive[b]:
            atoms.add(int(world.b_atom_i[b])); atoms.add(int(world.b_atom_j[b]))
    density = {}
    for a in atoms:
        if a >= K or not world.k_alive[a]:
            density[a] = 0.0
            continue
        d = world.s_pos - world.k_pos[a]
        d -= box * np.round(d / box)
        density[a] = float(np.sum(world.s_alive & ((d * d).sum(axis=1) < r_sense_sq)))
    fluxes = []
    for b in range(world.b_count):
        if not world.b_alive[b]:
            continue
        i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
        fluxes.append(density.get(i, 0.0) * density.get(j, 0.0))
    return fluxes


if __name__ == "__main__":
    nsteps = int(sys.argv[1]) if len(sys.argv) > 1 else 8000  # 4000 sim-s
    cfg = r.make_cfg(3)  # persistent lattice, anchoring on, NO stimulus
    world = World(cfg); dt = cfg.dt
    collect_after = nsteps - 4000  # last 2000 sim-s
    resting = []
    for step in range(nsteps):
        # NO injection — resting substrate
        tick(world, dt)
        if step >= collect_after and step % 50 == 0:
            resting.extend(per_bridge_flux(world, cfg))
    resting = np.array(resting, dtype=np.float64)
    if len(resting) == 0:
        print("FLUX_REF_RESULT " + json.dumps({"error": "no bridges"}), flush=True)
        sys.exit(0)
    p90 = float(np.percentile(resting, 90))
    out = {"n_samples": len(resting), "mean": float(resting.mean()),
           "p50": float(np.percentile(resting, 50)),
           "p90": p90, "p99": float(np.percentile(resting, 99)),
           "max": float(resting.max()), "flux_ref": round(p90, 2)}
    print("FLUX_REF_RESULT " + json.dumps(out), flush=True)
    Path(Path.home() / '.eqmod' / 'bet' / 'BET-092').mkdir(parents=True, exist_ok=True)
    (Path.home() / '.eqmod' / 'bet' / 'BET-092' / 'baseline_flux.json').write_text(
        json.dumps(out, indent=2))
    print("PROBE DONE", flush=True)
