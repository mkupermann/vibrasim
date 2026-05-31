"""BET-108: consolidation (freeze-on-write). Once a bridge latches past
consol, lock it at the strong well so a written memory cannot decay in recall.
Built on BET-106's working write+containment regime (ungated bridge propagation,
charge-blank). Targets the lone gap = recall (Tc).

Usage: run_bet108.py <label> <gain> <consol> <boundary> [budget]
Pre-registered bars in docs/amendments/bet_108_consolidation.md.
"""
import sys, json
from pathlib import Path
import tools.run_bet099 as b99
from tools.run_bet100 import frac_selective

b99.WARMUP = 3000
b99.STIM_DUR = 3000
b99.STIM_END = b99.WARMUP + b99.STIM_DUR

_orig_make_cfg = b99.make_cfg


def _mk(gain, consol, boundary):
    def mk():
        cfg = _orig_make_cfg()
        object.__setattr__(cfg, 'bridge_charge_prop_rate', float(gain))
        object.__setattr__(cfg, 'bridge_consolidate_threshold', float(consol))
        object.__setattr__(cfg, 'compartment_boundary', float(boundary))
        object.__setattr__(cfg, 'n_emit', 0)
        object.__setattr__(cfg, 'tau_LTP', 1.0)
        return cfg
    return mk


if __name__ == "__main__":
    label = sys.argv[1]
    gain = float(sys.argv[2])
    consol = float(sys.argv[3])
    boundary = float(sys.argv[4])
    budget = int(sys.argv[5]) if len(sys.argv) > 5 else 800
    b99.make_cfg = _mk(gain, consol, boundary)
    run_arm = b99.run_arm

    print(f"=== BET-108{label}: gain={gain} consol={consol} "
          f"wall={'ON@'+str(boundary) if boundary>0 else 'OFF'} ===", flush=True)
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
    print(f"T108{label}a selective firing  : {Ta}", flush=True)
    print(f"T108{label}b selective potent.  : {Tb} (>=0.5)", flush=True)
    print(f"T108{label}c persistent recall  : {Tc} (>=0.5)", flush=True)
    print(f"T108{label}d containment        : {Td} (<0.25)", flush=True)
    print(f"\nBET-108{label}: {'PASS' if passed else 'NULL/FAIL'}", flush=True)
    if passed:
        print(">>> CLEAN SELECTIVE PERSISTENT MEMORY — write, consolidate, recall, contained.", flush=True)

    outdir = Path.home() / '.eqmod' / 'bet' / f'BET-108{label}'
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'result.json').write_text(json.dumps(
        {"label": label, "gain": gain, "consol": consol, "boundary": boundary,
         "fire_ratio": fire_ratio, "loc_stim_frac": loc_stim_frac,
         "loc_post_frac": loc_post_frac, "uni_post_frac": uni_post_frac,
         "Ta": Ta, "Tb": Tb, "Tc": Tc, "Td": Td, "passed": passed},
        indent=2, default=str))
    print("DONE", flush=True)
