"""BET-098: sharp spatial separation to remove boundary contamination.
Tighter injection (sigma=1.0) + region cores only (half=3.0). Rectified drive.

Pre-registered bars in docs/amendments/bet_098_sharp_separation.md.
"""
import sys, json, time
import numpy as np
from pathlib import Path
from world.config import WorldConfig
from world.state import World
from world.physics import tick
from tools.run_bet090 import region_mean
from tools.run_bet093 import region_flux, cull_free_vibrations

WARMUP = 6000
STIM_DUR = 6000
STIM_END = WARMUP + STIM_DUR
FLUX_REF = 1000.0
HALF = 3.0          # measure region cores only
SIGMA = 1.0         # tight injection


def make_cfg() -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=400, box_size=(30.0, 30.0, 30.0),
        r_1=5.0, r_2=10.0, freq_tolerance=0.03,
        mol_fusion_enabled=False, resonance_coupling=15.0,
        node_thermal_speed=0.3, atom_valence=3,
        node_freq_binding=False, atom_repulsion_k=1.0, curvature_k=1.0,
        bistable_rate=1.0, bistable_low=1.0, bistable_mid=3.0, bistable_high=6.0,
        bistable_well_k=0.04, bistable_flux_gain=0.3, bistable_flux_ref=FLUX_REF,
        bistable_drive_mode='absolute', bistable_drive_rectified=True,
        anchor_damping=0.7, anchor_bond_min=2, anchor_age=50.0,
        fusion_bond_block=3,
        pair_decay_time=40.0, triad_decay_time=400.0, dt=0.5,
        n_nodes_max=8192, n_vibrations_max=4096, vibration_soft_cap=500,
        repulsion_k=0.0, lambda_gen=0.006, lambda_dec=0.0,
        neuron_dynamics_enabled=False, stdp_enabled=False,
        slot_recycling_enabled=False, graceful_capacity=True, rng_seed=42,
    )


def inject_tight(world, cfg, box, cx, n, sigma=SIGMA):
    rng = world.rng
    free = np.where(~world.s_alive[:cfg.n_vibrations_max])[0]
    k = min(n, len(free))
    if k == 0:
        return
    sl = free[:k]
    world.s_pos[sl] = np.column_stack([
        rng.normal(cx, sigma, k) % box[0],
        rng.normal(box[1] / 2, sigma, k) % box[1],
        rng.normal(box[2] / 2, sigma, k) % box[2]])
    world.s_vel[sl] = np.zeros((k, 3))          # frozen (vel exactly 0)
    world.s_freq[sl] = world._sample_frequencies(k)
    world.s_pol[sl] = rng.random(k) < 0.5
    world.s_alive[sl] = True
    world.n_alive = max(world.n_alive, int(sl.max()) + 1)


def blank_bridges(world, low):
    for b in range(world.b_count):
        if world.b_alive[b]:
            world.b_strength[b] = float(low)


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
            object.__setattr__(cfg, 'lambda_gen', 0.0)
            cull_free_vibrations(world, keep_frac=0.0)
            blank_bridges(world, cfg.bistable_low)
        if WARMUP <= step < STIM_END:
            if uniform:
                inject_tight(world, cfg, box, STIM_X, n=20)
                inject_tight(world, cfg, box, CTRL_X, n=20)
            else:
                inject_tight(world, cfg, box, STIM_X, n=40)
            if step % 200 == 199:
                stim_flux_s.extend(region_flux(world, cfg, STIM_X, half=HALF))
                ctrl_flux_s.extend(region_flux(world, cfg, CTRL_X, half=HALF))
        if step == STIM_END:
            cull_free_vibrations(world, keep_frac=0.0)
            print(f"[{name}] field cleared at STIM end", flush=True)
        tick(world, dt)
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
    print(f"=== BET-098: sharp separation (sigma={SIGMA}, half={HALF}) ===", flush=True)
    on = run_arm("LOC", uniform=False, wall_budget=budget)
    off = run_arm("UNI", uniform=True, wall_budget=budget)

    ratio = on["stim_flux_median"] / max(on["ctrl_flux_median"], 1e-6)
    T98a = ratio >= 1.5
    T98b = selective(on["log"], "STIM")
    post_min = on["stim_end_s"] + 2000
    T98c = selective(on["log"], "POST", min_s=post_min)
    T98d = not selective(off["log"], "POST", min_s=post_min)
    passed = T98a and T98b and T98c and T98d

    print("\n--- VERDICT ---", flush=True)
    print(f"stim_flux={on['stim_flux_median']:.0f} ctrl_flux={on['ctrl_flux_median']:.0f} "
          f"ratio={ratio:.2f}", flush=True)
    print(f"T98a contrast exists (>=1.5x) : {T98a}", flush=True)
    print(f"T98b selective latch (STIM)   : {T98b}", flush=True)
    print(f"T98c hysteresis memory (POST) : {T98c}", flush=True)
    print(f"T98d control (uniform) fails  : {T98d}", flush=True)
    verdict = 'PASS' if passed else ('REGIME-NULL (no contrast)' if not T98a else 'NULL/FAIL')
    print(f"\nBET-098: {verdict}", flush=True)
    if passed:
        print(">>> FIRST SELECTIVE PERSISTENT MEMORY — write, clear field, read back.", flush=True)

    outdir = Path.home() / '.eqmod' / 'bet' / 'BET-098'
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'result.json').write_text(json.dumps(
        {"on": on, "off": off, "T98a": T98a, "T98b": T98b, "T98c": T98c,
         "T98d": T98d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
