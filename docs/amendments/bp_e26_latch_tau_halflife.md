# BP-E26 — Latch half-life (charge_latch_tau>0)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** PRIM6-D0 (tau=0 hold PASS)

## Hypothesis
With `charge_latch_tau=2.0`, after dual write + fire L + idle T_end=200 (~3.3s): max R latch ≤ **0.5×** peak latch measured mid-prop.  
Control tau=0: end latch ≥ **0.90×** mid-peak.  
Both: peak R latch during prop ≥1.0.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | tau=2: end/peak ≤0.50 | ≥0.90 of trials |
| B2 | tau=0: end/peak ≥0.90 | ≥0.90 of trials |
| B3 | both arms peak≥1.0 | ≥0.90 |

Seeds {821,831} trials 8. Smoke 1×3.

## Prediction
🔮 PASS — exponential latch decay is deterministic.

## RESULT
**NULL** (2026-07-20). B1_tau2=**0.000** (end/peak≤0.5 fails), B2_tau0=1.0, B3=1.0.  
tau=0 holds; tau=2 did not meet 0.5× residual under T_end=200. No bar retune.
