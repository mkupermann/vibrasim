# PRIM11 — Fire zeros nearby latch (hard inhibit)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** PRIM10 NULL (charge-scale inhibit insufficient); need latch clear for XOR

## Primitive
`fire_zero_latch_radius: float = 0` (0=off)  
On fire, set `k_latch=0` for all other alive L4 within radius (not self).

## PRIM11-D0 + XOR app (one experiment)
Topology:
- OR: L1–Mor–R, L2–Mor–R (no coincidence on Mor)  
- AND: L1,L2 → Mand with `k_coincidence_gate=1`; Mand has zero-latch radius covering R  

Measure **end** latch at R after T_prop (not peak):
| ID | Criterion | thr |
|----|-----------|-----|
| X1 | Fire L1 only: end R latch ≥1.0 rate | ≥0.85 |
| X2 | Fire L2 only: end R latch ≥1.0 rate | ≥0.85 |
| X3 | Fire both: end R latch ≤0.25 rate | ≥0.85 |

Seeds {1231,1241} trials 10.

## Prediction
🔮 LEAN PASS if Mand fires when both L and clears R after OR path lit; miss if timing leaves residual latch.

## RESULT
**NULL** (2026-07-20). After post-prop clear fix: X1=**0**, X2=**0**, X3=**1.0**.  
Both-L clears R (X3), but single-L OR path also fails to leave end latch ≥1 (OR broken under this topology/timing). XOR not established. No bar retune.
