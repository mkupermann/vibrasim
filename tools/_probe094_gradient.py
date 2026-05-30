"""BET-094 pre-probe: can a CONFINED stimulus sustain a spatial flux gradient?
Best-case test: starve ambient, then inject zero-velocity vibrations at high
rate into the stim region only. Measure stim/ctrl flux ratio over time. If even
this homogenizes, spatial-flux addressing is dead -> pivot to STDP/BTSP.
"""
import sys
import numpy as np
import tools.run_bet093 as r93
from tools.run_bet093 import region_flux, cull_free_vibrations
from world.state import World
from world.physics import tick

WARMUP = 6000


def inject_confined(world, cfg, box, cx, n, vel_scale):
    rng = world.rng
    free = np.where(~world.s_alive[:cfg.n_vibrations_max])[0]
    k = min(n, len(free))
    if k == 0:
        return
    sl = free[:k]
    world.s_pos[sl] = np.column_stack([
        rng.normal(cx, 2.0, k) % box[0],
        rng.normal(box[1] / 2, 3, k) % box[1],
        rng.normal(box[2] / 2, 3, k) % box[2]])
    world.s_vel[sl] = rng.normal(0, vel_scale, (k, 3))
    world.s_freq[sl] = world._sample_frequencies(k)
    world.s_pol[sl] = rng.random(k) < 0.5
    world.s_alive[sl] = True
    world.n_alive = max(world.n_alive, int(sl.max()) + 1)


if __name__ == "__main__":
    vel = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    rate = int(sys.argv[2]) if len(sys.argv) > 2 else 40   # per step
    cfg = r93.make_cfg()
    world = World(cfg); dt = cfg.dt
    box = np.asarray(cfg.box_size)
    STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    for step in range(WARMUP):
        tick(world, dt)
    object.__setattr__(cfg, 'lambda_gen', 0.0005)
    cull_free_vibrations(world, keep_frac=0.1)
    print(f"probe vel={vel} rate={rate}/step", flush=True)
    for step in range(WARMUP, WARMUP + 4000):
        inject_confined(world, cfg, box, STIM_X, n=rate, vel_scale=vel)
        tick(world, dt)
        if step % 500 == 499:
            sf = region_flux(world, cfg, STIM_X)
            cf = region_flux(world, cfg, CTRL_X)
            sm = float(np.median(sf)) if sf else 0.0
            cm = float(np.median(cf)) if cf else 0.0
            n_alive = int(world.s_alive[:cfg.n_vibrations_max].sum())
            print(f"  t={(step+1)*dt:.0f}s stim_flux={sm:.0f} ctrl_flux={cm:.0f} "
                  f"ratio={sm/max(cm,1e-6):.2f} free_vib={n_alive}", flush=True)
    print("PROBE DONE", flush=True)
