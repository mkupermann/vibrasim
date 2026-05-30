"""BET-095: confined stimulus + truly starved field -> selective hysteresis
memory. Retry of BET-094 with the regime fixed: lambda_gen=0 at starve, no
calibrate window (inject immediately so the stimulus owns the vibration budget),
fixed flux_ref=1000.

Pre-registered bars in docs/amendments/bet_095_confined_memory.md.
"""
import sys, json, time
import numpy as np
from pathlib import Path
from world.config import WorldConfig
from world.state import World
from world.physics import tick
from tools.run_bet090 import region_mean
from tools.run_bet093 import region_flux, cull_free_vibrations
from tools._probe094_gradient import inject_confined

WARMUP = 6000
STIM_DUR = 6000
STIM_END = WARMUP + STIM_DUR
FLUX_REF = 1000.0


def make_cfg() -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=400, box_size=(30.0, 30.0, 30.0),
        r_1=5.0, r_2=10.0, freq_tolerance=0.03,
        mol_fusion_enabled=False, resonance_coupling=15.0,
        node_thermal_speed=0.3, atom_valence=3,
        node_freq_binding=False, atom_repulsion_k=1.0, curvature_k=1.0,
        bistable_rate=1.0, bistable_low=1.0, bistable_mid=3.0, bistable_high=6.0,
        bistable_well_k=0.04, bistable_flux_gain=0.3, bistable_flux_ref=FLUX_REF,
        bistable_drive_mode='absolute',
        anchor_damping=0.7, anchor_bond_min=2, anchor_age=50.0,
        fusion_bond_block=3,
        pair_decay_time=40.0, triad_decay_time=400.0, dt=0.5,
        n_nodes_max=8192, n_vibrations_max=4096, vibration_soft_cap=500,
        repulsion_k=0.0, lambda_gen=0.006, lambda_dec=0.0,
        neuron_dynamics_enabled=False, stdp_enabled=False,
        slot_recycling_enabled=False, graceful_capacity=True, rng_seed=42,
    )


def run_arm(name, uniform, wall_budget=420):
    cfg = make_cfg()
    world = World(cfg); dt = cfg.dt
    box = np.asarray(cfg.box_size)
    STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    log = []
    stim_flux_s, ctrl_flux_s = [], []
    t0 = time.time()
    for step in range(40000):
        if step == WARMUP:
            object.__setattr__(cfg, 'lambda_gen', 0.0)  # TRUE starve
            cull_free_vibrations(world, keep_frac=0.0)   # clear field
        # STIM: confined zero-velocity injection, immediately (no calibrate)
        if WARMUP <= step < STIM_END:
            if uniform:
                inject_confined(world, cfg, box, STIM_X, n=20, vel_scale=0.01)
                inject_confined(world, cfg, box, CTRL_X, n=20, vel_scale=0.01)
            else:
                inject_confined(world, cfg, box, STIM_X, n=40, vel_scale=0.01)
            if step % 200 == 199:
                stim_flux_s.extend(region_flux(world, cfg, STIM_X))
                ctrl_flux_s.extend(region_flux(world, cfg, CTRL_X))
        if step == STIM_END:
            cull_free_vibrations(world, keep_frac=0.0)  # clear field for hysteresis test
            print(f"[{name}] field cleared at STIM end", flush=True)
        tick(world, dt)
        if step % 1000 == 999:
            sim_s = round((step + 1) * dt, 1)
            sm, sn = region_mean(world, STIM_X)
            cm, cn = region_mean(world, CTRL_X)
            ph = ("WARM" if step < WARMUP else "STIM" if step < STIM_END else "POST")
            log.append({"sim_s": sim_s, "phase": ph, "stim_mean": round(sm, 2),
                        "stim_n": sn, "ctrl_mean": round(cm, 2), "ctrl_n": cn})
            print(f"[{name}] {sim_s:.0f}s [{ph}]: stim={sm:.2f}(n={sn}) ctrl={cm:.2f}(n={cn})",
                  flush=True)
        if time.time() - t0 > wall_budget:
            print(f"[{name}] wall budget hit at step {step}", flush=True)
            break
    stim_med = float(np.median(stim_flux_s)) if stim_flux_s else 0.0
    ctrl_med = float(np.median(ctrl_flux_s)) if ctrl_flux_s else 0.0
    return {"name": name, "uniform": uniform, "log": log,
            "stim_flux_median": stim_med, "ctrl_flux_median": ctrl_med,
            "stim_end_s": STIM_END * dt}


def selective(log, phase, min_s=None):
    rows = [e for e in log if e["phase"] == phase
            and (min_s is None or e["sim_s"] >= min_s)]
    return any(e["stim_mean"] > 3.0 and e["ctrl_mean"] < 3.0 for e in rows)


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 420
    print(f"=== BET-095: confined stimulus, starved field (flux_ref={FLUX_REF}) ===", flush=True)
    on = run_arm("LOC", uniform=False, wall_budget=budget)
    off = run_arm("UNI", uniform=True, wall_budget=budget)

    ratio = on["stim_flux_median"] / max(on["ctrl_flux_median"], 1e-6)
    T95a = ratio >= 1.5
    T95b = selective(on["log"], "STIM")
    post_min = on["stim_end_s"] + 2000
    T95c = selective(on["log"], "POST", min_s=post_min)
    T95d = not selective(off["log"], "POST", min_s=post_min)
    passed = T95a and T95b and T95c and T95d

    print("\n--- VERDICT ---", flush=True)
    print(f"stim_flux={on['stim_flux_median']:.0f} ctrl_flux={on['ctrl_flux_median']:.0f} "
          f"ratio={ratio:.2f}", flush=True)
    print(f"T95a contrast exists (>=1.5x) : {T95a}", flush=True)
    print(f"T95b selective latch (STIM)   : {T95b}", flush=True)
    print(f"T95c hysteresis memory (POST) : {T95c}", flush=True)
    print(f"T95d control (uniform) fails  : {T95d}", flush=True)
    print(f"\nBET-095: {'PASS' if passed else ('REGIME-NULL (no contrast)' if not T95a else 'NULL/FAIL')}",
          flush=True)

    outdir = Path.home() / '.eqmod' / 'bet' / 'BET-095'
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'result.json').write_text(json.dumps(
        {"on": on, "off": off, "T95a": T95a, "T95b": T95b, "T95c": T95c,
         "T95d": T95d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
