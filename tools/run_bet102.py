"""BET-102: the scale test. Bigger box (50^3) so control-distance >> neighbour-
distance, plus longer charge integration (tau_membrane=2.0) so slow local
emission (emit_speed=6) can write to near neighbours but not reach far control.
Directly tests whether scale/geometry was the limit on selective persistent
recall. Reuses BET-099 run loop + BET-100 metric.

Pre-registered bars in docs/amendments/bet_102_scale_test.md.
"""
import sys, json
import numpy as np
from pathlib import Path
from world.config import WorldConfig
import tools.run_bet099 as b99
from tools.run_bet100 import frac_selective


def make_cfg_big() -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=1800, box_size=(50.0, 50.0, 50.0),
        r_1=5.0, r_2=10.0, freq_tolerance=0.03,
        mol_fusion_enabled=False, resonance_coupling=15.0,
        node_thermal_speed=0.3, atom_valence=3,
        node_freq_binding=False, atom_repulsion_k=1.0, curvature_k=1.0,
        bistable_rate=0.0, bistable_low=1.0, bistable_mid=3.0, bistable_high=6.0,
        bistable_well_k=0.04,
        corr_plasticity_rate=1.0, corr_potentiation=1.0,
        neuron_dynamics_enabled=True, theta_fire=4.0, r_integrate=5.0,
        tau_membrane=2.0, t_refractory=0.05, tau_LTP=0.02,   # longer integration
        n_emit=8, emit_speed=6.0,                            # moderate local emission
        anchor_damping=0.7, anchor_bond_min=2, anchor_age=50.0,
        fusion_bond_block=3,
        pair_decay_time=40.0, triad_decay_time=400.0, dt=0.5,
        n_nodes_max=8192, n_vibrations_max=8192, vibration_soft_cap=2000,
        repulsion_k=0.0, lambda_gen=0.006, lambda_dec=0.0,
        stdp_enabled=False, slot_recycling_enabled=False,
        graceful_capacity=True, rng_seed=42,
    )


b99.make_cfg = make_cfg_big
# Big box runs ~3x slower; shorten phases so the run reaches POST within budget.
# Lattice forms by ~1000s, so 3000s warmup suffices; 3000s STIM; POST to >=2000s
# after stim end. (Run 1 used 6000/6000 and hit wall budget mid-STIM.)
b99.WARMUP = 3000
b99.STIM_DUR = 3000
b99.STIM_END = b99.WARMUP + b99.STIM_DUR
run_arm = b99.run_arm


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 700
    print("=== BET-102: scale test (box 50^3, tau=2.0, emit_speed=6) ===", flush=True)
    on = run_arm("LOC", uniform=False, wall_budget=budget)
    off = run_arm("UNI", uniform=True, wall_budget=budget)

    fire_ratio = on["stim_fire"] / max(on["ctrl_fire"], 1)
    post_min = on["stim_end_s"] + 2000
    loc_stim_frac = frac_selective(on["log"], "STIM")
    loc_post_frac = frac_selective(on["log"], "POST", min_s=post_min)
    uni_post_frac = frac_selective(off["log"], "POST", min_s=post_min)

    T102a = fire_ratio >= 3.0
    T102b = loc_stim_frac >= 0.5
    T102c = loc_post_frac >= 0.5
    T102d = uni_post_frac < 0.25
    passed = T102a and T102b and T102c and T102d

    print("\n--- VERDICT ---", flush=True)
    print(f"fire ratio={fire_ratio:.1f} | LOC stim-frac={loc_stim_frac:.2f} "
          f"LOC post-frac={loc_post_frac:.2f} UNI post-frac={uni_post_frac:.2f}", flush=True)
    print(f"T102a selective firing (>=3x) : {T102a}", flush=True)
    print(f"T102b selective potentiation  : {T102b} (>=0.5)", flush=True)
    print(f"T102c persistent recall       : {T102c} (>=0.5)", flush=True)
    print(f"T102d control fails (<0.25)   : {T102d}", flush=True)
    verdict = 'PASS' if passed else 'NULL/FAIL'
    print(f"\nBET-102: {verdict}", flush=True)
    if passed:
        print(">>> SCALE WAS THE LIMIT — selective persistent correlation memory CONFIRMED.", flush=True)

    outdir = Path.home() / '.eqmod' / 'bet' / 'BET-102'
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'result.json').write_text(json.dumps(
        {"on": on, "off": off, "fire_ratio": fire_ratio,
         "loc_stim_frac": loc_stim_frac, "loc_post_frac": loc_post_frac,
         "uni_post_frac": uni_post_frac, "T102a": T102a, "T102b": T102b,
         "T102c": T102c, "T102d": T102d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
