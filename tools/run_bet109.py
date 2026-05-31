"""BET-109: BET-108 consolidation sweep re-run with the blank-clears-consolidation
fix (blank_bridges now clears world._consolidated), so consolidation locks ONLY
bridges written DURING stim.

Usage: run_bet109.py <label> <gain> <consol> <boundary> [budget]
Pre-registered bars in docs/amendments/bet_109_consolidation_fixed.md.
"""
import sys, json
from pathlib import Path
import tools.run_bet099 as b99
from tools.run_bet100 import frac_selective
from tools.run_bet108 import _mk   # reuse cfg builder (gain, consol, boundary)

b99.WARMUP = 3000
b99.STIM_DUR = 3000
b99.STIM_END = b99.WARMUP + b99.STIM_DUR


if __name__ == "__main__":
    label = sys.argv[1]
    gain = float(sys.argv[2])
    consol = float(sys.argv[3])
    boundary = float(sys.argv[4])
    budget = int(sys.argv[5]) if len(sys.argv) > 5 else 800
    b99.make_cfg = _mk(gain, consol, boundary)
    run_arm = b99.run_arm

    print(f"=== BET-109{label}: gain={gain} consol={consol} "
          f"wall={'ON@'+str(boundary) if boundary>0 else 'OFF'} (blank-clears-consol fix) ===",
          flush=True)
    on = run_arm("LOC", uniform=False, wall_budget=budget)
    off = run_arm("UNI", uniform=True, wall_budget=budget)

    fire_ratio = on["stim_fire"] / max(on["ctrl_fire"], 1)
    post_min = on["stim_end_s"] + 2000
    loc_stim_frac = frac_selective(on["log"], "STIM")
    loc_post_frac = frac_selective(on["log"], "POST", min_s=post_min)
    uni_post_frac = frac_selective(off["log"], "POST", min_s=post_min)

    Ta = fire_ratio >= 3.0
    Tb = loc_stim_frac >= 0.5
    Tc = loc_post_frac >= 0.5
    Td = uni_post_frac < 0.25
    passed = Ta and Tb and Tc and Td

    print("\n--- VERDICT ---", flush=True)
    print(f"fire ratio={fire_ratio:.1f} | LOC stim-frac={loc_stim_frac:.2f} "
          f"LOC post-frac={loc_post_frac:.2f} UNI post-frac={uni_post_frac:.2f}", flush=True)
    print(f"T109{label}a selective firing  : {Ta}", flush=True)
    print(f"T109{label}b selective potent.  : {Tb} (>=0.5)", flush=True)
    print(f"T109{label}c persistent recall  : {Tc} (>=0.5)", flush=True)
    print(f"T109{label}d containment        : {Td} (<0.25)", flush=True)
    print(f"\nBET-109{label}: {'PASS' if passed else 'NULL/FAIL'}", flush=True)
    if passed:
        print(">>> MILESTONE: clean selective persistent memory — write, consolidate, recall, contained.", flush=True)

    outdir = Path.home() / '.eqmod' / 'bet' / f'BET-109{label}'
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'result.json').write_text(json.dumps(
        {"label": label, "gain": gain, "consol": consol, "boundary": boundary,
         "fire_ratio": fire_ratio, "loc_stim_frac": loc_stim_frac,
         "loc_post_frac": loc_post_frac, "uni_post_frac": uni_post_frac,
         "Ta": Ta, "Tb": Tb, "Tc": Tc, "Td": Td, "passed": passed},
        indent=2, default=str))
    print("DONE", flush=True)
