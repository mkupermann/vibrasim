"""G74 — the substrate's nonlinear element. The proto-cell controller is LINEAR in its tested range
(G58/G59). Push the sustained foreign influx far higher and find where the steady-state SATURATES
(clearance can't keep up) — a nonlinear limiter, the substrate's first computing nonlinearity.

Pre-registered bars in docs/amendments/g74_nonlinearity.md.
"""
import sys, json
from pathlib import Path
import numpy as np
from tools.run_g59_rejection import ss_for_rate

RATES = [4, 8, 16, 32, 64, 128]


if __name__ == "__main__":
    print("=== G74: nonlinear range / saturation of the proto-cell controller ===", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        for rate in RATES:
            R[(s, rate)] = ss_for_rate(s, rate)
            print(f"  seed {s} influx={rate}: ss={R[(s, rate)]:.3f}", flush=True)
    # incremental gain ss/influx; linear -> constant, saturating -> falls at high influx
    print("\n--- analysis ---", flush=True)
    sat = {}
    for s in seeds:
        gains = [R[(s, rate)] / rate for rate in RATES]
        print(f"  seed {s}: ss/influx = {[round(g, 4) for g in gains]}", flush=True)
        # saturation = high-rate gain drops to <= 0.6x the low-rate gain
        sat[s] = gains[-1] <= 0.6 * gains[0]
    G74a = all(sat[s] for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"G74a saturates at high influx (gain drops >=40%): {G74a}", flush=True)
    verdict = ("PASS - the controller SATURATES (nonlinear limiter): the substrate has a computing nonlinearity"
               if G74a else "NULL - linear across the full tested range (no saturation found)")
    print(f"\nG74: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G74"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {f"{k[0]}_r{k[1]}": v for k, v in R.items()},
                                                  "saturates": sat, "passed": G74a}, indent=2, default=str))
    print("DONE", flush=True)
