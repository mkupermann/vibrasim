# BP-E78 — Hybrid path-switch curriculum (AND ↔ OR)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E75–E77 selective restores; E46 path-switch  
**Discipline:** multi-trial: prefer OR-only then AND-only via soft-cut + disarm restore

## Hypothesis
Start with full hybrid trained.
1. Soft-cut L1 (AND), disarm; restore L3 if needed — probe: L3 ON, L1+L2 OFF ≥0.80  
2. Soft-cut L3 (OR), disarm; restore L1–M — probe: L1+L2 ON, L3 OFF ≥0.80  
3. Soft-cut L1 again, disarm; restore L3–R — probe: L3 ON, L1+L2 OFF ≥0.75  

## Bars
| ID | thr |
|----|-----|
| B1 OR-only state | ≥0.80 |
| B2 AND-only state | ≥0.80 |
| B3 OR-only again | ≥0.75 |

Seeds {2251,2261} trials 6. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN PASS with disarm doctrine. Miss if multi-step residual state accumulates.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hybrid path-switch OR-only → AND-only → OR-only multi-trial.
