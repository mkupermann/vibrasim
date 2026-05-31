"""BET-107: graded bridge-graph write — only latched bridges (strength >=
prop_min) propagate, so recall rides only on the written pattern and blank
control bridges carry nothing. Charge-blank (BET-106) retained.

Usage: run_bet107.py <label> <gain> <prop_min> <boundary> <n_emit> [budget]
Pre-registered bars in docs/amendments/bet_107_graded_propagation.md.
"""
import sys, json
from pathlib import Path
import tools.run_bet099 as b99
from tools.run_bet100 import frac_selective

b99.WARMUP = 3000
b99.STIM_DUR = 3000
b99.STIM_END = b99.WARMUP + b99.STIM_DUR

_orig_make_cfg = b99.make_cfg


def _mk(gain, prop_min, boundary, n_emit):
    def mk():
        cfg = _orig_make_cfg()
        object.__setattr__(cfg, 'bridge_charge_prop_rate', float(gain))
        object.__setattr__(cfg, 'bridge_prop_min_strength', float(prop_min))
        object.__setattr__(cfg, 'compartment_boundary', float(boundary))
        object.__setattr__(cfg, 'n_emit', int(n_emit))
        object.__setattr__(cfg, 'tau_LTP', 1.0)
        return cfg
    return mk


if __name__ == "__main__":
    label = sys.argv[1]
    gain = float(sys.argv[2])
    prop_min = float(sys.argv[3])
    boundary = float(sys.argv[4])
    n_emit = int(sys.argv[5])
    budget = int(sys.argv[6]) if len(sys.argv) > 6 else 800
    b99.make_cfg = _mk(gain, prop_min, boundary, n_emit)
    run_arm = b99.run_arm

    print(f"=== BET-107{label}: gain={gain} prop_min={prop_min} "
          f"wall={'ON@'+str(boundary) if boundary>0 else 'OFF'} n_emit={n_emit} ===", flush=True)
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
    print(f"T107{label}a selective firing  : {Ta}", flush=True)
    print(f"T107{label}b selective potent.  : {Tb} (>=0.5)", flush=True)
    print(f"T107{label}c persistent recall  : {Tc} (>=0.5)", flush=True)
    print(f"T107{label}d containment        : {Td} (<0.25)", flush=True)
    print(f"\nBET-107{label}: {'PASS' if passed else 'NULL/FAIL'}", flush=True)
    if passed:
        print(">>> CLEAN SELECTIVE PERSISTENT MEMORY — graded modular bridge-graph write.", flush=True)

    outdir = Path.home() / '.eqmod' / 'bet' / f'BET-107{label}'
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'result.json').write_text(json.dumps(
        {"label": label, "gain": gain, "prop_min": prop_min, "boundary": boundary,
         "n_emit": n_emit, "fire_ratio": fire_ratio, "loc_stim_frac": loc_stim_frac,
         "loc_post_frac": loc_post_frac, "uni_post_frac": uni_post_frac,
         "Ta": Ta, "Tb": Tb, "Tc": Tc, "Td": Td, "passed": passed},
        indent=2, default=str))
    print("DONE", flush=True)
