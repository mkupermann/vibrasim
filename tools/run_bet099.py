"""BET-099: firing-coincidence (Hebbian) bridge plasticity -> selective,
persistent, turnover-robust memory. neuron_dynamics ON; co-firing of bridged
atoms drives the bistable well (write); the well holds (recall). Flux bistable
OFF. Two arms: localized vs uniform stimulus.

Pre-registered bars in docs/amendments/bet_099_correlation_memory.md.
"""
import sys, json, time
import numpy as np
from pathlib import Path
from world.config import WorldConfig
from world.state import World
from world.physics import tick
from tools.run_bet090 import region_mean
from tools.run_bet093 import cull_free_vibrations
from tools.run_bet098 import inject_tight, blank_bridges

WARMUP = 6000
STIM_DUR = 6000
STIM_END = WARMUP + STIM_DUR
HALF = 3.0


def make_cfg() -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=400, box_size=(30.0, 30.0, 30.0),
        r_1=5.0, r_2=10.0, freq_tolerance=0.03,
        mol_fusion_enabled=False, resonance_coupling=15.0,
        node_thermal_speed=0.3, atom_valence=3,
        node_freq_binding=False, atom_repulsion_k=1.0, curvature_k=1.0,
        # bistable well params used by correlation plasticity; flux drive OFF
        bistable_rate=0.0, bistable_low=1.0, bistable_mid=3.0, bistable_high=6.0,
        bistable_well_k=0.04,
        corr_plasticity_rate=1.0, corr_potentiation=1.0,
        neuron_dynamics_enabled=True, theta_fire=4.0, r_integrate=5.0,
        tau_membrane=0.5, t_refractory=0.05, tau_LTP=0.02,
        anchor_damping=0.7, anchor_bond_min=2, anchor_age=50.0,
        fusion_bond_block=3,
        pair_decay_time=40.0, triad_decay_time=400.0, dt=0.5,
        n_nodes_max=8192, n_vibrations_max=4096, vibration_soft_cap=500,
        repulsion_k=0.0, lambda_gen=0.006, lambda_dec=0.0,
        stdp_enabled=False, slot_recycling_enabled=False,
        graceful_capacity=True, rng_seed=42,
    )


def run_arm(name, uniform, wall_budget=480):
    cfg = make_cfg()
    world = World(cfg); dt = cfg.dt
    box = np.asarray(cfg.box_size)
    STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    log = []
    stim_fire = ctrl_fire = 0
    t0 = time.time()
    for step in range(40000):
        if step == WARMUP:
            object.__setattr__(cfg, 'lambda_gen', 0.0)
            cull_free_vibrations(world, keep_frac=0.0)
            blank_bridges(world, cfg.bistable_low)
        if WARMUP <= step < STIM_END:
            if uniform:
                inject_tight(world, cfg, box, STIM_X, n=20)
                inject_tight(world, cfg, box, CTRL_X, n=20)
            else:
                inject_tight(world, cfg, box, STIM_X, n=40)
        if step == STIM_END:
            cull_free_vibrations(world, keep_frac=0.0)
            print(f"[{name}] field cleared at STIM end", flush=True)
        tick(world, dt)
        # tally selective firing during STIM
        if WARMUP <= step < STIM_END:
            for t_f, ai in world.firing_events:
                if t_f < world.t - dt or ai >= world.k_count or not world.k_alive[ai]:
                    continue
                x = world.k_pos[ai][0]
                if abs(x - STIM_X) < HALF:
                    stim_fire += 1
                elif abs(x - CTRL_X) < HALF:
                    ctrl_fire += 1
        if step % 1000 == 999:
            sim_s = round((step + 1) * dt, 1)
            sm, sn = region_mean(world, STIM_X, half=HALF)
            cm, cn = region_mean(world, CTRL_X, half=HALF)
            ph = ("WARM" if step < WARMUP else "STIM" if step < STIM_END else "POST")
            log.append({"sim_s": sim_s, "phase": ph, "stim_mean": round(sm, 2),
                        "stim_n": sn, "ctrl_mean": round(cm, 2), "ctrl_n": cn})
            print(f"[{name}] {sim_s:.0f}s [{ph}]: stim={sm:.2f}(n={sn}) ctrl={cm:.2f}(n={cn})",
                  flush=True)
        if time.time() - t0 > wall_budget:
            print(f"[{name}] wall budget hit at step {step}", flush=True)
            break
    return {"name": name, "uniform": uniform, "log": log,
            "stim_fire": stim_fire, "ctrl_fire": ctrl_fire,
            "stim_end_s": STIM_END * dt}


def selective(log, phase, min_s=None):
    rows = [e for e in log if e["phase"] == phase
            and (min_s is None or e["sim_s"] >= min_s)]
    return any(e["stim_mean"] > 3.0 and e["ctrl_mean"] < 3.0 for e in rows)


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 480
    print("=== BET-099: firing-coincidence correlation memory ===", flush=True)
    on = run_arm("LOC", uniform=False, wall_budget=budget)
    off = run_arm("UNI", uniform=True, wall_budget=budget)

    fire_ratio = on["stim_fire"] / max(on["ctrl_fire"], 1)
    T99a = fire_ratio >= 3.0
    T99b = selective(on["log"], "STIM")
    post_min = on["stim_end_s"] + 2000
    T99c = selective(on["log"], "POST", min_s=post_min)
    T99d = not selective(off["log"], "POST", min_s=post_min)
    passed = T99a and T99b and T99c and T99d

    print("\n--- VERDICT ---", flush=True)
    print(f"stim_fire={on['stim_fire']} ctrl_fire={on['ctrl_fire']} ratio={fire_ratio:.1f}", flush=True)
    print(f"T99a selective firing (>=3x)  : {T99a}", flush=True)
    print(f"T99b selective potentiation   : {T99b}", flush=True)
    print(f"T99c persistent recall (POST) : {T99c}", flush=True)
    print(f"T99d control (uniform) fails  : {T99d}", flush=True)
    verdict = 'PASS' if passed else 'NULL/FAIL'
    print(f"\nBET-099: {verdict}", flush=True)
    if passed:
        print(">>> SELECTIVE PERSISTENT CORRELATION MEMORY — write by co-firing, read back after.", flush=True)

    outdir = Path.home() / '.eqmod' / 'bet' / 'BET-099'
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'result.json').write_text(json.dumps(
        {"on": on, "off": off, "T99a": T99a, "T99b": T99b, "T99c": T99c,
         "T99d": T99d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
