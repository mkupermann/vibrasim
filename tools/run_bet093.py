"""BET-093: starve the ambient field to create a real spatial flux gradient,
then test whether the absolute-drive latch reads it selectively.

Two arms: localized stimulus (ON, creates contrast) vs uniform stimulus
(control, no contrast). Pre-registered bars in
docs/amendments/bet_093_flux_contrast.md.
"""
import sys, json, time
import numpy as np
from pathlib import Path
from world.config import WorldConfig
from world.state import World
from world.physics import tick
from tools.run_bet090 import inject, region_mean
from tools._probe092_flux import per_bridge_flux

WARMUP = 6000          # 3000 sim-s to build the lattice
STIM_DUR = 6000        # 3000 sim-s of stimulus
SETTLE = 500           # steps after starving, before measuring flux_ref / stim
LAMBDA_STARVED = 0.0005


def make_cfg() -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=400, box_size=(30.0, 30.0, 30.0),
        r_1=5.0, r_2=10.0, freq_tolerance=0.03,
        mol_fusion_enabled=False, resonance_coupling=15.0,
        node_thermal_speed=0.3, atom_valence=3,
        node_freq_binding=False, atom_repulsion_k=1.0, curvature_k=1.0,
        bistable_rate=1.0, bistable_low=1.0, bistable_mid=3.0, bistable_high=6.0,
        bistable_well_k=0.04, bistable_flux_gain=0.3, bistable_flux_ref=9785.0,
        bistable_drive_mode='absolute',
        anchor_damping=0.7, anchor_bond_min=2, anchor_age=50.0,
        fusion_bond_block=3,
        pair_decay_time=40.0, triad_decay_time=400.0, dt=0.5,
        n_nodes_max=8192, n_vibrations_max=4096, vibration_soft_cap=500,
        repulsion_k=0.0, lambda_gen=0.006, lambda_dec=0.0,
        neuron_dynamics_enabled=False, stdp_enabled=False,
        slot_recycling_enabled=False, graceful_capacity=True, rng_seed=42,
    )


def region_flux(world, cfg, cx, half=7.0):
    """Per-bridge flux for bridges whose midpoint x is within `half` of cx."""
    box = np.asarray(cfg.box_size, dtype=np.float64)
    r_sense_sq = cfg.r_2 * cfg.r_2
    K = world.k_count
    # local density per atom (cached over atoms that appear in nearby bridges)
    out = []
    for b in range(world.b_count):
        if not world.b_alive[b]:
            continue
        i, j = int(world.b_atom_i[b]), int(world.b_atom_j[b])
        if i >= K or j >= K:
            continue
        mx = (world.k_pos[i][0] + world.k_pos[j][0]) / 2
        if abs(mx - cx) >= half:
            continue
        di = world.s_pos - world.k_pos[i]; di -= box * np.round(di / box)
        dj = world.s_pos - world.k_pos[j]; dj -= box * np.round(dj / box)
        ni = float(np.sum(world.s_alive & ((di * di).sum(axis=1) < r_sense_sq)))
        nj = float(np.sum(world.s_alive & ((dj * dj).sum(axis=1) < r_sense_sq)))
        out.append(ni * nj)
    return out


def cull_free_vibrations(world, keep_frac=0.1):
    alive = np.where(world.s_alive[:world.config.n_vibrations_max])[0]
    n_keep = int(len(alive) * keep_frac)
    if n_keep < len(alive):
        world.rng.shuffle(alive)
        world.s_alive[alive[n_keep:]] = False


def run_arm(name, uniform, wall_budget=360):
    cfg = make_cfg()
    world = World(cfg)
    dt = cfg.dt
    box = np.asarray(cfg.box_size)
    STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    log = []
    stim_flux_samples, ctrl_flux_samples = [], []
    t0 = time.time()
    starved = False
    stim_end = WARMUP + STIM_DUR
    for step in range(40000):
        # phase transition: starve ambient at end of warmup
        if step == WARMUP and not starved:
            object.__setattr__(cfg, 'lambda_gen', LAMBDA_STARVED)  # frozen dataclass
            cull_free_vibrations(world, keep_frac=0.1)
            starved = True
        # measure flux_ref from starved control region after settle, before stim
        if step == WARMUP + SETTLE:
            rf = region_flux(world, cfg, CTRL_X)
            object.__setattr__(cfg, 'bistable_flux_ref',
                               float(np.percentile(rf, 90)) if rf else 9785.0)
            print(f"[{name}] starved flux_ref(ctrl p90)={cfg.bistable_flux_ref:.1f}", flush=True)
        # stimulus during stim window (after settle)
        if WARMUP + SETTLE <= step < stim_end and step % 4 == 0:
            if uniform:
                inject(world, cfg, box, STIM_X, n=10)
                inject(world, cfg, box, CTRL_X, n=10)
            else:
                inject(world, cfg, box, STIM_X, n=20)
        tick(world, dt)
        # collect flux contrast samples during stim
        if WARMUP + SETTLE <= step < stim_end and step % 200 == 199:
            stim_flux_samples.extend(region_flux(world, cfg, STIM_X))
            ctrl_flux_samples.extend(region_flux(world, cfg, CTRL_X))
        if step % 1000 == 999:
            sim_s = round((step + 1) * dt, 1)
            sm, sn = region_mean(world, STIM_X)
            cm, cn = region_mean(world, CTRL_X)
            if step < WARMUP:
                ph = "WARM"
            elif step < stim_end:
                ph = "STIM"
            else:
                ph = "POST"
            e = {"sim_s": sim_s, "phase": ph, "stim_mean": round(sm, 2), "stim_n": sn,
                 "ctrl_mean": round(cm, 2), "ctrl_n": cn}
            log.append(e)
            print(f"[{name}] {sim_s:.0f}s [{ph}]: stim={sm:.2f}(n={sn}) ctrl={cm:.2f}(n={cn})",
                  flush=True)
        if time.time() - t0 > wall_budget:
            print(f"[{name}] wall budget hit at step {step}", flush=True)
            break
    stim_med = float(np.median(stim_flux_samples)) if stim_flux_samples else 0.0
    ctrl_med = float(np.median(ctrl_flux_samples)) if ctrl_flux_samples else 0.0
    return {"name": name, "uniform": uniform, "log": log,
            "stim_flux_median": stim_med, "ctrl_flux_median": ctrl_med,
            "flux_ref": cfg.bistable_flux_ref,
            "stim_end_s": stim_end * dt}


def selective(log, phase, min_s=None):
    rows = [e for e in log if e["phase"] == phase
            and (min_s is None or e["sim_s"] >= min_s)]
    return any(e["stim_mean"] > 3.0 and e["ctrl_mean"] < 3.0 for e in rows)


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 360
    print("=== BET-093: flux contrast via starved ambient ===", flush=True)
    on = run_arm("LOC", uniform=False, wall_budget=budget)
    off = run_arm("UNI", uniform=True, wall_budget=budget)

    contrast = (on["stim_flux_median"] >= 1.5 * max(on["ctrl_flux_median"], 1e-6))
    T93a = contrast
    post_min = on["stim_end_s"] + 2000
    T93b = selective(on["log"], "STIM")
    T93c = selective(on["log"], "POST", min_s=post_min)
    T93d = not selective(off["log"], "POST", min_s=post_min)
    passed = T93a and T93b and T93c and T93d

    print("\n--- VERDICT ---", flush=True)
    print(f"stim flux median={on['stim_flux_median']:.0f} "
          f"ctrl flux median={on['ctrl_flux_median']:.0f} "
          f"ratio={on['stim_flux_median']/max(on['ctrl_flux_median'],1e-6):.2f}", flush=True)
    print(f"T93a contrast exists (>=1.5x) : {T93a}", flush=True)
    print(f"T93b selective latch (STIM)   : {T93b}", flush=True)
    print(f"T93c selective memory (POST)  : {T93c}", flush=True)
    print(f"T93d control (uniform) fails  : {T93d}", flush=True)
    print(f"\nBET-093: {'PASS' if passed else ('REGIME-NULL (no contrast)' if not T93a else 'NULL/FAIL')}",
          flush=True)

    outdir = Path.home() / '.eqmod' / 'bet' / 'BET-093'
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'result.json').write_text(json.dumps(
        {"on": on, "off": off, "T93a": T93a, "T93b": T93b, "T93c": T93c,
         "T93d": T93d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
