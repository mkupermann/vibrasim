# BP-E84 — Hard 2×2 dual-kill all arms then selective identity restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E79 soft dual-cut identity; E60 hard crossbar; E73 disarm kill  
**Discipline:** hard kill all four arms; disarm kill emitters; restore 00+11 only

## Hypothesis
1. Hard-kill all arms → concurrent both R OFF ≥0.80  
2. Disarm kill emitters; restore identity → concurrent both ON ≥0.80  
3. L0 only → R0 ON R1 OFF ≥0.80  

## Bars
B1 OFF ≥0.80 · B2 identity restore ≥0.80 · B3 L0 isolation ≥0.80  

Seeds {2521,2531} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS if hard wipe is restorable like soft. Miss if hard kill removes nodes needed for rewrite.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard dual-kill all arms + disarm + identity restore recovers concurrent routing and isolation.
