"""NSH-01 — New-Science Hunt step 1: hunt for a NATIVE structure-formation phase transition in the
substrate's own dynamics. Sweep initial vibration density; measure the largest bridged structure after
settling. Looking for a sharp critical density (a giant-component transition), not a smooth ramp.
Pre-registered bars in docs/amendments/nsh01_substrate_native_law_hunt.md.
"""
import json
from dataclasses import replace
from pathlib import Path
import numpy as np

from world.state import World
from world.physics import tick, _largest_bridged_component
from tools.run_g43_protocell import cfg, SETTLE

DENSITIES = [50, 100, 150, 200, 250, 300, 400, 500, 600]


def largest_structure(seed, n_vib):
    c = cfg(seed)
    c = replace(c, n_initial_vibrations=n_vib)
    w = World(c)
    for _ in range(SETTLE):
        tick(w, c.dt)
    comp = _largest_bridged_component(w)
    return len(comp) if comp else 0


def run(seed):
    return {n: largest_structure(seed, n) for n in DENSITIES}


if __name__ == "__main__":
    print("=== NSH-01: native structure-formation transition vs density ===", flush=True)
    seeds = [42, 7]
    S = {}
    for s in seeds:
        S[s] = run(s)
        curve = " ".join(f"{n}:{S[s][n]}" for n in DENSITIES)
        print(f"  seed {s}: S(rho) = {curve}", flush=True)

    # analysis: jumps between successive densities
    def analyze(curve):
        vals = [curve[n] for n in DENSITIES]
        steps = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
        max_jump = max(steps) if steps else 0
        mean_step = np.mean([abs(x) for x in steps]) if steps else 0.0
        jmax_i = int(np.argmax(steps)) if steps else 0
        crit_rho = DENSITIES[jmax_i + 1] if steps else None
        sharp = (max_jump / mean_step) if mean_step > 1e-9 else 0.0
        # saturation: last value >= 0.8 * max value AND growth in last step small
        sat = vals[-1] >= 0.8 * max(vals) and (vals[-1] - vals[-2]) <= 0.25 * max(vals)
        return dict(sharp=float(sharp), crit_rho=crit_rho, max_jump=int(max_jump), saturates=bool(sat), vals=vals)

    A = {s: analyze(S[s]) for s in seeds}
    for s in seeds:
        print(f"  seed {s}: sharpness(maxjump/meanstep)={A[s]['sharp']:.2f} crit_rho={A[s]['crit_rho']} "
              f"max_jump={A[s]['max_jump']} saturates={A[s]['saturates']}", flush=True)

    NSH01a = all(A[s]['sharp'] >= 3.0 for s in seeds)
    NSH01b = (A[seeds[0]]['crit_rho'] == A[seeds[1]]['crit_rho'])
    NSH01c = all(A[s]['saturates'] for s in seeds)
    passed = NSH01a and NSH01b and NSH01c

    print("\n--- VERDICT ---", flush=True)
    print(f"NSH01a sharp transition (maxjump>=3x mean) : {NSH01a}", flush=True)
    print(f"NSH01b reproducible critical density       : {NSH01b} (rho*={A[seeds[0]]['crit_rho']}/{A[seeds[1]]['crit_rho']})", flush=True)
    print(f"NSH01c saturates above critical            : {NSH01c}", flush=True)
    verdict = ("PASS - a reproducible sharp structure-formation transition exists (native phenomenon "
               "found; characterize its exponent next)") if passed else "NULL/partial - no clean native transition here"
    print(f"\nNSH-01: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "NSH01"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"S": {str(s): S[s] for s in seeds},
                                                  "analysis": {str(s): A[s] for s in seeds}, "passed": passed,
                                                  "NSH01a": NSH01a, "NSH01b": NSH01b, "NSH01c": NSH01c},
                                                 indent=2, default=str))
    print("DONE", flush=True)
