import sys, time
import numpy as np
import tools.run_bet091 as r
from world.state import World
from world.physics import tick

block = int(sys.argv[1]) if len(sys.argv) > 1 else 1
nsteps = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
cfg = r.make_cfg(block); world = World(cfg); dt = cfg.dt
box = np.asarray(cfg.box_size)
t0 = time.time()
for step in range(nsteps):
    if step % 4 == 0:
        r.inject(world, cfg, box, box[0] * 0.25, n=20)
    tick(world, dt)
    if step % 200 == 199:
        n_alive = int(world.k_alive[:world.k_count].sum())
        n4 = int(sum(1 for a in range(world.k_count)
                     if world.k_alive[a] and world.k_level[a] == 4))
        nb = int(sum(1 for a in range(world.k_count)
                     if world.k_alive[a] and world.k_level[a] == 4
                     and world.k_bond_count[a] >= 1))
        print(f"block={block} step={step+1} t={(step+1)*dt:.0f}s "
              f"alive_nodes={n_alive} level4={n4} bonded4={nb} "
              f"elapsed={time.time()-t0:.1f}s", flush=True)
print("PROBE DONE", flush=True)
