# PRIM10 — Lateral fire inhibition

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** PRIM9 AND; E38 OR; need soft competition

## Primitive
`fire_inhibit_radius: float = 0` (0=off)  
`fire_inhibit_frac: float = 0.5`  

When a node fires in `neuron_dynamics`, for every other alive L4 within radius (not self), multiply `k_charge` by `(1 - frac)` (clamp ≥0). Does not kill bridges. Engineered WTA-ish competition.

## PRIM10-D0 bars
Two parallel chains L1–M1–R1, L2–M2–R2 (close in space). Fire **both** L1 and L2.
| ID | Criterion | thr |
|----|-----------|-----|
| I1 | inhibit ON: exactly one of {R1,R2} peak≥1.0 and other ≤0.25 rate | ≥0.80 |
| I2 | inhibit OFF: both R1 and R2 peak≥1.0 rate | ≥0.80 |
| I3 | inhibit ON: at least one R peak≥1.0 rate | ≥0.90 |

Seeds {1181,1191} trials 10.

## Prediction
🔮 LEAN NULL on I1: simultaneous fire both may still both peak before inhibit settles; or both suppressed.

## RESULT
**NULL** (2026-07-20). I1_exclusive=**0.000**, I2_off_both=1.0, I3=1.0.  
Charge-scale inhibit after fire does not produce exclusive path winner when both L fire (both R still light). Soft WTA not achieved. No bar retune.
