# BP-E75 — Soft-cut AND + OR, selective AND-only restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E74; E72; E66  
**Discipline:** dual soft-cut (L1 AND + L3 OR); disarm; restore **only L1–M**; bypass stays OFF

## Hypothesis
1. Soft-cut L1 then L3 → L1+L2 OFF and L3 OFF ≥0.90  
2. Disarm all weaken emitters; restore L1–M only → L1+L2 ON ≥0.85  
3. L3 still OFF ≥0.90 (no accidental bypass restore)  

## Bars
| ID | thr |
|----|-----|
| B1 both OFF after dual cut | ≥0.90 |
| B2 AND ON after selective restore | ≥0.85 |
| B3 bypass still OFF | ≥0.90 |

Seeds {2191,2201} trials 8. Budget ~5 min, hard cap 10 min.

## Prediction
🔮 LEAN PASS. Miss if dual cut collaterally zeros shared R or restore bleeds.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Dual soft-cut both OFF; selective L1–M restore recovers AND only; bypass stays silent.
