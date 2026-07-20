# BP-E44 — Soft weaken + full path restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** PRIM13-D0 NULL B3 (M–R-only restore failed)  
**Not** PRIM13 B3 retune — restore **both** L–M and M–R

## Hypothesis
Same soft weaken as PRIM13. After I, retrain full path N_RESTORE=6 on L–M and M–R → L→R ON ≥0.85. Silence still ≥0.90.

## Bars
| ID | thr |
|----|-----|
| B1 L ON initial | ≥0.90 |
| B2 after I, L OFF | ≥0.90 |
| B3 full soft restore L ON | ≥0.85 |

Seeds {1371,1381} trials 10.

## Prediction
🔮 PASS.

## RESULT
**PASS** (2026-07-20). B1=1.0 B2=1.0 B3=1.0. Soft silence + full-path re-strengthen restores.
