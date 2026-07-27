# BP-E83 — Soft 2×2 dual-cut → swap restore → identity reconfig

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E82 id→swap PASS  
**Discipline:** mirror of E82 — total soft-cut; restore swap; then reconfig to identity

## Hypothesis
1. Dual-cut all → OFF ≥0.80  
2. Restore swap 01+10 → L0→R1 only ≥0.80  
3. Soft-cut swap; restore identity 00+11 → L0→R0 only ≥0.75  

## Bars
B1 OFF ≥0.80 · B2 swap state ≥0.80 · B3 identity state ≥0.75  

Seeds {2501,2511} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS (E82 mirror). Miss if order-asymmetric residual.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Dual soft-cut → swap restore → identity reconfig (E82 mirror).
