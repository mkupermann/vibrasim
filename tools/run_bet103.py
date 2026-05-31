"""BET-103: engineered modular compartment (x-plane wall at box midline) to
contain activity percolation. BET-099 setup + compartment_boundary=15.0.
BET-100 fraction-selective metric.

Pre-registered bars in docs/amendments/bet_103_modular_compartment.md.
"""
import sys, json
from pathlib import Path
import tools.run_bet099 as b99
from tools.run_bet100 import frac_selective

_orig_make_cfg = b99.make_cfg


def make_cfg_compartment():
    cfg = _orig_make_cfg()                       # box 30, neuron + correlation
    object.__setattr__(cfg, 'compartment_boundary', 15.0)  # wall at midline
    return cfg


b99.make_cfg = make_cfg_compartment
run_arm = b99.run_arm


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 480
    print("=== BET-103: engineered modular compartment (wall at x=15) ===", flush=True)
    on = run_arm("LOC", uniform=False, wall_budget=budget)
    off = run_arm("UNI", uniform=True, wall_budget=budget)

    fire_ratio = on["stim_fire"] / max(on["ctrl_fire"], 1)
    post_min = on["stim_end_s"] + 2000
    loc_stim_frac = frac_selective(on["log"], "STIM")
    loc_post_frac = frac_selective(on["log"], "POST", min_s=post_min)
    uni_post_frac = frac_selective(off["log"], "POST", min_s=post_min)

    T103a = fire_ratio >= 3.0
    T103b = loc_stim_frac >= 0.5
    T103c = loc_post_frac >= 0.5
    T103d = uni_post_frac < 0.25
    passed = T103a and T103b and T103c and T103d

    print("\n--- VERDICT ---", flush=True)
    print(f"fire ratio={fire_ratio:.1f} | LOC stim-frac={loc_stim_frac:.2f} "
          f"LOC post-frac={loc_post_frac:.2f} UNI post-frac={uni_post_frac:.2f}", flush=True)
    print(f"T103a selective firing (>=3x) : {T103a}", flush=True)
    print(f"T103b selective potentiation  : {T103b} (>=0.5)", flush=True)
    print(f"T103c persistent recall       : {T103c} (>=0.5)", flush=True)
    print(f"T103d control fails (<0.25)   : {T103d}", flush=True)
    verdict = 'PASS' if passed else 'NULL/FAIL'
    print(f"\nBET-103: {verdict}", flush=True)
    if passed:
        print(">>> CLEAN SELECTIVE PERSISTENT MEMORY — engineered modularity contains it.", flush=True)

    outdir = Path.home() / '.eqmod' / 'bet' / 'BET-103'
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'result.json').write_text(json.dumps(
        {"on": on, "off": off, "fire_ratio": fire_ratio,
         "loc_stim_frac": loc_stim_frac, "loc_post_frac": loc_post_frac,
         "uni_post_frac": uni_post_frac, "T103a": T103a, "T103b": T103b,
         "T103c": T103c, "T103d": T103d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
