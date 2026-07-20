# BP-E108 — Soft 2×2 full restore then hard-cut identity diagonal (00+11)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E105 soft identity-diag PASS  
**Discipline:** hard kill 00+11 after full restore → pure swap (hard analogue of E105)

## Hypothesis
Wide 2×2. Soft dual-cut all; restore all; hard-cut 00 and 11 (r=8).
1. After full restore: concurrent both R ON ≥0.80  
2. Hard-cut 00+11: L0 → R1 ON R0 OFF ≥0.80  
3. L1 → R0 ON R1 OFF ≥0.80  

## Bars
B1 concurrent ≥0.80 · B2 L0 swap ≥0.80 · B3 L1 swap ≥0.80  

Seeds {3061,3071} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS. Completes hard diagonal select after full restore.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard-cut identity diagonal after full restore yields pure swap.
