"""BET-099 pre-probe: with neuron_dynamics ON, does the confined stimulus make
stim-region atoms FIRE while control stays silent? Selective firing is the
prerequisite for correlation (STDP/BTSP) memory addressing.
"""
import sys
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import tick
from tools.run_bet093 import cull_free_vibrations
from tools.run_bet098 import inject_tight

WARMUP = 6000
STIM_DUR = 4000


def make_cfg():
    return WorldConfig(
        n_initial_vibrations=400, box_size=(30.0, 30.0, 30.0),
        r_1=5.0, r_2=10.0, freq_tolerance=0.03,
        mol_fusion_enabled=False, resonance_coupling=15.0,
        node_thermal_speed=0.3, atom_valence=3,
        node_freq_binding=False, atom_repulsion_k=1.0, curvature_k=1.0,
        bistable_rate=0.0,  # bistable OFF — isolate firing
        anchor_damping=0.7, anchor_bond_min=2, anchor_age=50.0,
        fusion_bond_block=3,
        neuron_dynamics_enabled=True, theta_fire=4.0, r_integrate=5.0,
        tau_membrane=0.5, t_refractory=0.05,
        pair_decay_time=40.0, triad_decay_time=400.0, dt=0.5,
        n_nodes_max=8192, n_vibrations_max=4096, vibration_soft_cap=500,
        repulsion_k=0.0, lambda_gen=0.006, lambda_dec=0.0,
        stdp_enabled=False, slot_recycling_enabled=False,
        graceful_capacity=True, rng_seed=42,
    )


if __name__ == "__main__":
    cfg = make_cfg(); world = World(cfg); dt = cfg.dt
    box = np.asarray(cfg.box_size)
    STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    for step in range(WARMUP):
        tick(world, dt)
    object.__setattr__(cfg, 'lambda_gen', 0.0)
    cull_free_vibrations(world, keep_frac=0.0)
    print("warmup done, starved; neuron_dynamics ON, confined stim ->", flush=True)
    stim_fire = ctrl_fire = 0
    for step in range(WARMUP, WARMUP + STIM_DUR):
        inject_tight(world, cfg, box, STIM_X, n=40)
        before = len(world.firing_events)
        tick(world, dt)
        # attribute new firing events to region by firing atom x-position
        for t_f, ai in world.firing_events:
            if t_f < world.t - dt:   # only events from this tick
                continue
            if ai >= world.k_count or not world.k_alive[ai]:
                continue
            x = world.k_pos[ai][0]
            if abs(x - STIM_X) < 7:
                stim_fire += 1
            elif abs(x - CTRL_X) < 7:
                ctrl_fire += 1
        if step % 1000 == 999:
            print(f"  t={(step+1)*dt:.0f}s cumulative firings: stim={stim_fire} "
                  f"ctrl={ctrl_fire}", flush=True)
    print(f"FIRING_RESULT stim={stim_fire} ctrl={ctrl_fire} "
          f"ratio={stim_fire/max(ctrl_fire,1):.1f}", flush=True)
    print("PROBE DONE", flush=True)
