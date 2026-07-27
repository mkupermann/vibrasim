# BP-E14 — Peak cross-mid charge transfer (transient)

**PRE-REGISTERED 2026-07-20 before data (night)**  
**Not** E13 bar retune — new metric: **peak** R charge during prop, not end-state.

## Hypothesis

Same setup as E13 (dual ILW, valence=4, bridge_charge_prop_rate=2, force-fire L).  
During T_prop ticks, **max** mean R-side charge ≥ **1.0** in ≥ **0.85** trials.  
No-bridge (valence=0): max mean R charge ≤ **0.25** in ≥ **0.85** trials.  
Treat has cross bridge ≥ **0.90**.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Treat: fraction max_R_charge ≥ 1.0 | ≥ **0.85** |
| B2 | No-bridge: fraction max_R_charge ≤ 0.25 | ≥ **0.85** |
| B3 | Treat cross bridge | ≥ **0.90** |

Seeds {481, 491}, trials 10; T_prop=60. Budget 90s / hard 180s.

## Prediction
🔮 PASS from E13 diagnosis (R hit 2.0 on fire tick).

## RESULT
**PASS** (2026-07-20 night). B1=1.0 B2=1.0 B3=1.0. Peak cross charge; prediction HIT after E13 miss.
