# BP-E85 — Hard 2×2 dual-kill all arms then selective swap restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E84 hard identity restore; E80 soft swap restore  
**Discipline:** hard kill all four arms; disarm; restore **01+10** only

## Hypothesis
1. Hard-kill all → concurrent both R OFF ≥0.80  
2. Disarm; restore swap → concurrent both ON ≥0.80  
3. L0 only → R1 ON R0 OFF ≥0.80  

## Bars
B1 OFF ≥0.80 · B2 swap restore ≥0.80 · B3 L0→R1 ≥0.80  

Seeds {2541,2551} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS (E84 mirror for swap). Miss if hard kill asymmetric.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard dual-kill all arms + swap restore; L0→R1 isolation holds.
