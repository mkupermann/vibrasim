"""BET-100: contain firing propagation (n_emit=0) + noise-robust selectivity
(fraction of checkpoints). Otherwise identical to BET-099.

Pre-registered bars in docs/amendments/bet_100_robust_selective_recall.md.
"""
import sys, json
import numpy as np
from pathlib import Path
import tools.run_bet099 as b99

_orig_make_cfg = b99.make_cfg


def make_cfg_contained():
    cfg = _orig_make_cfg()
    object.__setattr__(cfg, 'n_emit', 0)   # contain firing propagation
    return cfg


b99.make_cfg = make_cfg_contained
run_arm = b99.run_arm


def frac_selective(log, phase, min_s=None):
    rows = [e for e in log if e["phase"] == phase
            and (min_s is None or e["sim_s"] >= min_s)]
    if not rows:
        return 0.0
    sel = sum(1 for e in rows if e["stim_mean"] > 3.0 and e["ctrl_mean"] < 3.0)
    return sel / len(rows)


if __name__ == "__main__":
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 480
    print("=== BET-100: contained propagation + robust selectivity ===", flush=True)
    on = run_arm("LOC", uniform=False, wall_budget=budget)
    off = run_arm("UNI", uniform=True, wall_budget=budget)

    fire_ratio = on["stim_fire"] / max(on["ctrl_fire"], 1)
    post_min = on["stim_end_s"] + 2000
    loc_stim_frac = frac_selective(on["log"], "STIM")
    loc_post_frac = frac_selective(on["log"], "POST", min_s=post_min)
    uni_post_frac = frac_selective(off["log"], "POST", min_s=post_min)

    T100a = fire_ratio >= 3.0
    T100b = loc_stim_frac >= 0.5
    T100c = loc_post_frac >= 0.5
    T100d = uni_post_frac < 0.25
    passed = T100a and T100b and T100c and T100d

    print("\n--- VERDICT ---", flush=True)
    print(f"fire ratio={fire_ratio:.1f} | LOC stim-frac={loc_stim_frac:.2f} "
          f"LOC post-frac={loc_post_frac:.2f} UNI post-frac={uni_post_frac:.2f}", flush=True)
    print(f"T100a selective firing (>=3x)  : {T100a}", flush=True)
    print(f"T100b selective potentiation   : {T100b} (>=0.5)", flush=True)
    print(f"T100c persistent recall        : {T100c} (>=0.5)", flush=True)
    print(f"T100d control fails (<0.25)    : {T100d}", flush=True)
    verdict = 'PASS' if passed else 'NULL/FAIL'
    print(f"\nBET-100: {verdict}", flush=True)
    if passed:
        print(">>> ROBUST SELECTIVE PERSISTENT CORRELATION MEMORY.", flush=True)

    outdir = Path.home() / '.eqmod' / 'bet' / 'BET-100'
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'result.json').write_text(json.dumps(
        {"on": on, "off": off, "fire_ratio": fire_ratio,
         "loc_stim_frac": loc_stim_frac, "loc_post_frac": loc_post_frac,
         "uni_post_frac": uni_post_frac, "T100a": T100a, "T100b": T100b,
         "T100c": T100c, "T100d": T100d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
