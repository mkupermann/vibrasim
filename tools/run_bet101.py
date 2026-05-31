"""BET-101: local emission (emit_speed=2.0, was 30.0) to resolve the
write/contaminate tension by locality (Pattern 02). Otherwise identical to
BET-099 (n_emit=8 retained so co-firing pairs still form). BET-100's noise-robust
fraction-selective metric.

Pre-registered bars in docs/amendments/bet_101_local_emission.md.
"""
import sys, json
import numpy as np
from pathlib import Path
import tools.run_bet099 as b99
from tools.run_bet100 import frac_selective

_orig_make_cfg = b99.make_cfg


def make_cfg_local():
    cfg = _orig_make_cfg()
    object.__setattr__(cfg, 'emit_speed', 2.0)   # local emission (was 30.0)
    return cfg


b99.make_cfg = make_cfg_local
run_arm = b99.run_arm


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 480
    print("=== BET-101: local emission (emit_speed=2.0) ===", flush=True)
    on = run_arm("LOC", uniform=False, wall_budget=budget)
    off = run_arm("UNI", uniform=True, wall_budget=budget)

    fire_ratio = on["stim_fire"] / max(on["ctrl_fire"], 1)
    post_min = on["stim_end_s"] + 2000
    loc_stim_frac = frac_selective(on["log"], "STIM")
    loc_post_frac = frac_selective(on["log"], "POST", min_s=post_min)
    uni_post_frac = frac_selective(off["log"], "POST", min_s=post_min)

    T101a = fire_ratio >= 3.0
    T101b = loc_stim_frac >= 0.5
    T101c = loc_post_frac >= 0.5
    T101d = uni_post_frac < 0.25
    passed = T101a and T101b and T101c and T101d

    print("\n--- VERDICT ---", flush=True)
    print(f"fire ratio={fire_ratio:.1f} | LOC stim-frac={loc_stim_frac:.2f} "
          f"LOC post-frac={loc_post_frac:.2f} UNI post-frac={uni_post_frac:.2f}", flush=True)
    print(f"T101a selective firing (>=3x) : {T101a}", flush=True)
    print(f"T101b selective potentiation  : {T101b} (>=0.5)", flush=True)
    print(f"T101c persistent recall       : {T101c} (>=0.5)", flush=True)
    print(f"T101d control fails (<0.25)   : {T101d}", flush=True)
    verdict = 'PASS' if passed else 'NULL/FAIL'
    print(f"\nBET-101: {verdict}", flush=True)
    if passed:
        print(">>> MILESTONE: selective, persistent, contained correlation memory.", flush=True)

    outdir = Path.home() / '.eqmod' / 'bet' / 'BET-101'
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'result.json').write_text(json.dumps(
        {"on": on, "off": off, "fire_ratio": fire_ratio,
         "loc_stim_frac": loc_stim_frac, "loc_post_frac": loc_post_frac,
         "uni_post_frac": uni_post_frac, "T101a": T101a, "T101b": T101b,
         "T101c": T101c, "T101d": T101d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
