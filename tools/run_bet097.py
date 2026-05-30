"""BET-097: rectified (one-sided) drive so the selective latch HOLDS after the
field is cleared. Identical to BET-096 plus bistable_drive_rectified=True.

Pre-registered bars in docs/amendments/bet_097_rectified_hold.md.
"""
import sys, json
import numpy as np
from pathlib import Path
import tools.run_bet096 as b96

# Patch make_cfg to enable the rectified drive; run_bet096.run_arm reads the
# module global make_cfg, so this propagates.
_orig_make_cfg = b96.make_cfg


def make_cfg_rectified():
    cfg = _orig_make_cfg()
    object.__setattr__(cfg, 'bistable_drive_rectified', True)
    return cfg


b96.make_cfg = make_cfg_rectified

run_arm = b96.run_arm
selective = b96.selective


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 420
    print("=== BET-097: rectified drive (one-sided write) — does the latch HOLD? ===",
          flush=True)
    on = run_arm("LOC", uniform=False, wall_budget=budget)
    off = run_arm("UNI", uniform=True, wall_budget=budget)

    ratio = on["stim_flux_median"] / max(on["ctrl_flux_median"], 1e-6)
    T97a = ratio >= 1.5
    T97b = selective(on["log"], "STIM")
    post_min = on["stim_end_s"] + 2000
    T97c = selective(on["log"], "POST", min_s=post_min)
    T97d = not selective(off["log"], "POST", min_s=post_min)
    passed = T97a and T97b and T97c and T97d

    print("\n--- VERDICT ---", flush=True)
    print(f"stim_flux={on['stim_flux_median']:.0f} ctrl_flux={on['ctrl_flux_median']:.0f} "
          f"ratio={ratio:.2f}", flush=True)
    print(f"T97a contrast exists (>=1.5x) : {T97a}", flush=True)
    print(f"T97b selective latch (STIM)   : {T97b}", flush=True)
    print(f"T97c hysteresis memory (POST) : {T97c}", flush=True)
    print(f"T97d control (uniform) fails  : {T97d}", flush=True)
    verdict = 'PASS' if passed else ('REGIME-NULL (no contrast)' if not T97a else 'NULL/FAIL')
    print(f"\nBET-097: {verdict}", flush=True)
    if passed:
        print(">>> FIRST SELECTIVE PERSISTENT MEMORY — write, clear field, read back.", flush=True)

    outdir = Path.home() / '.eqmod' / 'bet' / 'BET-097'
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'result.json').write_text(json.dumps(
        {"on": on, "off": off, "T97a": T97a, "T97b": T97b, "T97c": T97c,
         "T97d": T97d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
