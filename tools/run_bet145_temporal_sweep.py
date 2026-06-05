"""BET-145 — delay sweep: locate the reservoir's memory horizon and test whether RTRL (exact) and e-prop
(eligibility) extend past it. Reuses BET-144's trainers; only D is swept, N_TRAIN reduced for the sweep.

Pre-registered bars in docs/amendments/bet_145_temporal_credit_sweep.md.
"""
import json
from pathlib import Path
import numpy as np
import tools.run_bet144_temporal_credit as B

B.N_TRAIN = 2000   # sweep budget (was 3000)

if __name__ == "__main__":
    print("=== BET-145: temporal-credit delay sweep (reservoir vs RTRL vs e-prop) ===", flush=True)
    Ds = [8, 16, 24, 32]
    rows = {}
    for D in Ds:
        rng = np.random.default_rng(0)
        res = B.run_reservoir(rng, D=D, distractors=True)
        rtrl = B.run_rtrl(rng, D=D, distractors=True)
        eprop = B.run_eprop(rng, D=D, distractors=True)
        rows[D] = dict(res=res, rtrl=rtrl, eprop=eprop)
        print(f"  D={D:2d}: RESERVOIR={res:.3f}  RTRL={rtrl:.3f}  E-PROP={eprop:.3f}  (chance 0.25)", flush=True)

    # 145a: reservoir breaks by D=32
    a = rows[32]['res'] <= 0.45
    # smallest D where reservoir <= 0.45
    broke = [D for D in Ds if rows[D]['res'] <= 0.45]
    Dstar = broke[0] if broke else None
    if Dstar is not None:
        b = rows[Dstar]['rtrl'] >= 0.80
        c = (rows[Dstar]['eprop'] >= 0.70) and (rows[Dstar]['eprop'] >= rows[Dstar]['res'] + 0.25)
    else:
        b = c = False

    if a and b and c:
        verdict = "PASS - e-prop eligibility achieves deep temporal credit past the reservoir memory horizon (no BPTT)"
    elif a and b and not c:
        verdict = "PARTIAL - exact RTRL extends past the reservoir horizon but e-prop does NOT; substrate-native eligibility is insufficient for deep temporal credit (the honest boundary)"
    elif not a:
        verdict = "NULL - reservoir never breaks within D<=32 (echo-state capacity too high to create the deep-credit regime here)"
    else:
        verdict = "PARTIAL/mixed"

    print("\n--- VERDICT ---", flush=True)
    print(f"145a reservoir breaks by D=32 (<=0.45) : {a}  (res@32={rows[32]['res']:.3f})", flush=True)
    print(f"145b RTRL past horizon (>=0.80)        : {b}  (D*={Dstar})", flush=True)
    print(f"145c e-prop past horizon (>=0.70,+0.25): {c}", flush=True)
    print(f"\nBET-145: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "BET145"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(dict(rows={str(k): v for k, v in rows.items()},
                                                      Dstar=Dstar, a=a, b=b, c=c, verdict=verdict),
                                                 indent=2, default=str))
    print("DONE", flush=True)
