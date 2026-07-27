# BP-E55 — Soft cut + idle hold without retrain

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E44 soft full restore PASS; PRIM13 soft weaken  
**Discipline:** tests whether soft silence is **spontaneously reversible** or only via ILW rewrite

## Hypothesis
Path L–M–R (two-hop, E44 geometry). Soft weaken I at M (frac=1, r=18).
1. Fire L → R ON ≥0.90  
2. Fire I → fire L → R OFF ≥0.90  
3. Idle **T_hold=80** ticks (no retrain) → fire L → R still OFF ≥0.90  

If soft weaken zeros bridge strength permanently until rewrite, silence holds without retrain.

## Bars
| ID | thr |
|----|-----|
| B1 initial ON | ≥0.90 |
| B2 cut OFF | ≥0.90 |
| B3 hold still OFF | ≥0.90 |

Seeds {1621,1631} trials 8. Budget ~3 min, hard cap 6 min.

## Prediction
🔮 LEAN PASS (strength stays ~0; no spontaneous recovery).  
NULL if strength rebounds or latch ghosts path.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Soft silence persists through idle hold without retrain. Soft inhibit is **retrain-reversible** (E44), not spontaneously reversible.
