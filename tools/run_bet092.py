"""BET-092: fixed-reference latch drive on the populated, persistent lattice.
Two arms differ ONLY in bistable_drive_mode: 'absolute' (drive vs fixed
flux_ref) vs 'relative' (vs moving mean, the BET-091 setting = negative control).

Pre-registered bars in docs/amendments/bet_092_populated_latch_drive.md.
flux_ref = 9785.0 (resting p90 from tools/_probe092_flux.py, recorded pre-run).
"""
import sys, json, time
import numpy as np
from pathlib import Path
from world.config import WorldConfig
from world.state import World
from world.physics import tick
from tools.run_bet090 import inject, region_mean

STIM_STEPS = 12000
FLUX_REF = 9785.0


def make_cfg(drive_mode: str) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=400, box_size=(30.0, 30.0, 30.0),
        r_1=5.0, r_2=10.0, freq_tolerance=0.03,
        mol_fusion_enabled=False, resonance_coupling=15.0,
        node_thermal_speed=0.3, atom_valence=3,
        node_freq_binding=False, atom_repulsion_k=1.0, curvature_k=1.0,
        bistable_rate=1.0, bistable_low=1.0, bistable_mid=3.0, bistable_high=6.0,
        bistable_well_k=0.04, bistable_flux_gain=0.3, bistable_flux_ref=FLUX_REF,
        bistable_drive_mode=drive_mode,
        anchor_damping=0.7, anchor_bond_min=2, anchor_age=50.0,
        fusion_bond_block=3,
        pair_decay_time=40.0, triad_decay_time=400.0, dt=0.5,
        n_nodes_max=8192, n_vibrations_max=4096, vibration_soft_cap=500,
        repulsion_k=0.0, lambda_gen=0.006, lambda_dec=0.0,
        neuron_dynamics_enabled=False, stdp_enabled=False,
        slot_recycling_enabled=False, graceful_capacity=True, rng_seed=42,
    )


def run_arm(name, drive_mode, wall_budget=360):
    cfg = make_cfg(drive_mode)
    world = World(cfg)
    dt = cfg.dt
    box = np.asarray(cfg.box_size)
    STIM_X, CTRL_X = box[0] * 0.25, box[0] * 0.75
    log = []
    t0 = time.time()
    for step in range(40000):
        if step < STIM_STEPS and step % 4 == 0:
            inject(world, cfg, box, STIM_X, n=20)
        tick(world, dt)
        if step % 2000 == 1999:
            sim_s = round((step + 1) * dt, 1)
            sm, sn = region_mean(world, STIM_X)
            cm, cn = region_mean(world, CTRL_X)
            allv = np.array([world.b_strength[b] for b in range(world.b_count)
                             if world.b_alive[b]])
            ph = "STIM" if step < STIM_STEPS else "POST"
            frac_strong = float(np.mean(allv > cfg.bistable_mid)) if len(allv) else 0.0
            # bimodality: fraction near low vs near high well
            frac_low = float(np.mean(allv < 2.0)) if len(allv) else 0.0
            frac_mid = float(np.mean((allv >= 2.0) & (allv <= 4.0))) if len(allv) else 0.0
            e = {"sim_s": sim_s, "phase": ph, "stim_mean": round(sm, 2), "stim_n": sn,
                 "ctrl_mean": round(cm, 2), "ctrl_n": cn,
                 "frac_strong": round(frac_strong, 2), "frac_low": round(frac_low, 2),
                 "frac_mid": round(frac_mid, 2)}
            log.append(e)
            print(f"[{name}] {sim_s:.0f}s [{ph}]: stim={sm:.2f}(n={sn}) "
                  f"ctrl={cm:.2f}(n={cn}) strong={frac_strong:.2f} mid={frac_mid:.2f}",
                  flush=True)
        if time.time() - t0 > wall_budget:
            print(f"[{name}] wall budget hit at step {step}", flush=True)
            break
    return {"name": name, "drive_mode": drive_mode, "log": log}


def selective(log, phase, min_s=None):
    rows = [e for e in log if e["phase"] == phase
            and (min_s is None or e["sim_s"] >= min_s)]
    return any(e["stim_mean"] > 3.0 and e["ctrl_mean"] < 3.0 for e in rows)


def bimodal(log):
    # strengths sit near low or high, not the middle: low mid-band occupancy
    rows = [e for e in log if e.get("frac_mid") is not None]
    if not rows:
        return False
    return float(np.mean([e["frac_mid"] for e in rows])) < 0.34


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 360
    print(f"=== BET-092: fixed-reference latch drive (flux_ref={FLUX_REF}) ===", flush=True)
    on = run_arm("ABS", drive_mode="absolute", wall_budget=budget)
    off = run_arm("REL", drive_mode="relative", wall_budget=budget)

    T92a = selective(on["log"], "STIM")
    T92b = selective(on["log"], "POST", min_s=8000)
    T92c = bimodal(on["log"])
    T92d = not selective(off["log"], "POST", min_s=8000)
    passed = T92a and T92b and T92c and T92d

    print("\n--- VERDICT ---", flush=True)
    print(f"T92a selective latch (STIM)   : {T92a}", flush=True)
    print(f"T92b selective memory (POST)  : {T92b}", flush=True)
    print(f"T92c bimodal                  : {T92c}", flush=True)
    print(f"T92d control (relative) fails : {T92d}", flush=True)
    print(f"\nBET-092: {'PASS' if passed else 'NULL/FAIL'}", flush=True)

    outdir = Path.home() / '.eqmod' / 'bet' / 'BET-092'
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'result.json').write_text(json.dumps(
        {"on": on, "off": off, "T92a": T92a, "T92b": T92b, "T92c": T92c,
         "T92d": T92d, "passed": passed, "flux_ref": FLUX_REF}, indent=2, default=str))
    print("DONE", flush=True)
