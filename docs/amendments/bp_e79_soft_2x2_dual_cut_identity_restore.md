# BP-E79 — Soft 2×2 dual-cut then selective identity restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E69 reconfig; E75 dual-cut selective; E72 disarm  
**Discipline:** soft-cut all four arms; disarm; restore **only 00+11**; concurrent probe

## Hypothesis
1. Soft-cut all arms → concurrent L0+L1 both R OFF ≥0.80  
2. Disarm; restore identity arms 00+11 → concurrent both R ON ≥0.80  
3. Single L0 → R0 ON R1 OFF ≥0.80  

## Bars
B1 both OFF ≥0.80 · B2 identity concurrent ON ≥0.80 · B3 L0 isolation ≥0.80  

Seeds {2421,2431} trials 6. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN PASS with disarm doctrine. Miss if dual cut destroys restore capacity.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Dual soft-cut all arms OFF; selective identity restore recovers concurrent routing and L0 isolation.
