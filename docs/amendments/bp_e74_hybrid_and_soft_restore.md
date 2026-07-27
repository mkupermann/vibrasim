# BP-E74 — Soft-disable AND input on hybrid + disarm restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E65 hybrid; E64 soft AND disable; E72 disarm doctrine  
**Discipline:** soft-cut L1 on hybrid AND branch; disarm; restore L1–M; bypass must stay ON

## Hypothesis
AND L1/L2–M–R + OR L3–R. Soft I at L1, r=8.
1. Soft-cut L1 → L1+L2 OFF ≥0.90  
2. Disarm weaken emitters; restore L1–M → L1+L2 ON ≥0.85  
3. L3 bypass still ON ≥0.90  

## Bars
| ID | thr |
|----|-----|
| B1 AND OFF after cut | ≥0.90 |
| B2 AND ON after disarm+restore | ≥0.85 |
| B3 bypass still ON | ≥0.90 |

Seeds {2171,2181} trials 8. Budget ~4 min, hard cap 8 min.

## Prediction
🔮 LEAN PASS (E64+E72 on hybrid). Miss if L1 soft cut collaterally weakens L3–R.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Soft-disable AND on hybrid + disarm + L1–M restore; OR bypass stays ON.
