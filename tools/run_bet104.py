"""BET-104 parallel sweep variant runner.

Usage: run_bet104.py <label> <n_emit> <compartment_boundary> [budget]
Writes verdict to bet104<label>_out.txt-style stream (stdout) and result.json.
Each variant runs LOC + UNI arms with shortened phases so 5 can run concurrently.

Pre-registered bars in docs/amendments/bet_104_parallel_sweep.md.
"""
import sys, json
from pathlib import Path
import tools.run_bet099 as b99
from tools.run_bet100 import frac_selective

# shortened phases so 5 variants fit concurrently
b99.WARMUP = 3000
b99.STIM_DUR = 3000
b99.STIM_END = b99.WARMUP + b99.STIM_DUR

_orig_make_cfg = b99.make_cfg


def _patched_make_cfg(n_emit, boundary):
    def mk():
        cfg = _orig_make_cfg()
        object.__setattr__(cfg, 'n_emit', int(n_emit))
        object.__setattr__(cfg, 'compartment_boundary', float(boundary))
        return cfg
    return mk


if __name__ == "__main__":
    label = sys.argv[1]
    n_emit = int(sys.argv[2])
    boundary = float(sys.argv[3])
    budget = int(sys.argv[4]) if len(sys.argv) > 4 else 360
    b99.make_cfg = _patched_make_cfg(n_emit, boundary)
    run_arm = b99.make_cfg and b99.run_arm

    print(f"=== BET-104{label}: n_emit={n_emit} wall={'ON@'+str(boundary) if boundary>0 else 'OFF'} ===",
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
    print(f"T104{label}a selective firing  : {Ta}", flush=True)
    print(f"T104{label}b selective potent.  : {Tb} (>=0.5)", flush=True)
    print(f"T104{label}c persistent recall  : {Tc} (>=0.5)", flush=True)
    print(f"T104{label}d containment        : {Td} (<0.25)", flush=True)
    print(f"\nBET-104{label}: {'PASS' if passed else 'NULL/FAIL'}", flush=True)

    outdir = Path.home() / '.eqmod' / 'bet' / f'BET-104{label}'
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'result.json').write_text(json.dumps(
        {"label": label, "n_emit": n_emit, "boundary": boundary,
         "fire_ratio": fire_ratio, "loc_stim_frac": loc_stim_frac,
         "loc_post_frac": loc_post_frac, "uni_post_frac": uni_post_frac,
         "Ta": Ta, "Tb": Tb, "Tc": Tc, "Td": Td, "passed": passed},
        indent=2, default=str))
    print("DONE", flush=True)
