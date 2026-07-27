# BP-E109 — Soft 2×2 full restore then hard-cut swap diagonal (01+10)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E106 soft swap-diag PASS; E108 hard identity-diag  
**Discipline:** hard kill 01+10 after full restore → pure identity (hard analogue of E106)

## Hypothesis
Wide 2×2. Soft dual-cut all; restore all; hard-cut 01 and 10 (r=8).
1. After full restore: concurrent both R ON ≥0.80  
2. Hard-cut 01+10: L0 → R0 ON R1 OFF ≥0.80  
3. L1 → R1 ON R0 OFF ≥0.80  

## Bars
B1 concurrent ≥0.80 · B2 L0 identity ≥0.80 · B3 L1 identity ≥0.80  

Seeds {3081,3091} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS. Completes hard diagonal select matrix (identity+swap).

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard-cut swap diagonal after full restore yields pure identity. Soft+hard diagonal select matrix closed (E105–E109).
