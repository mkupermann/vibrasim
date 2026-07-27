# BP-E106 — Soft 2×2 full restore then soft-cut swap diagonal (01+10)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E105 identity-diag cut; E79 identity  
**Discipline:** after full restore, soft-cut **swap diagonal** → pure identity routing

## Hypothesis
Wide 2×2. Soft dual-cut all; restore all; soft-cut 01 and 10.
1. After full restore: concurrent both R ON ≥0.80  
2. Soft-cut 01+10: L0 → R0 ON R1 OFF ≥0.80 (identity)  
3. L1 → R1 ON R0 OFF ≥0.80 (identity)  

## Bars
B1 concurrent ≥0.80 · B2 L0 identity ≥0.80 · B3 L1 identity ≥0.80  

Seeds {3021,3031} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS (E105 mirror). Completes post-full-restore diagonal select on 2×2.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Soft-cut swap diagonal after full restore yields pure identity routing.
