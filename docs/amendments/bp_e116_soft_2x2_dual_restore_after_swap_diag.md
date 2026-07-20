# BP-E116 — Soft 2×2 swap-diag cut then dual restore 01+10

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E106 PASS; E114 PASS (identity-diag dual restore); E112 dual-restore doctrine  
**Discipline:** dual restore of both cut swap-diag arms after pure-identity routing — completes dual-restore matrix

## Hypothesis
Wide 2×2. Soft dual-cut all; restore all; soft-cut 01+10 (pure identity).  
Then restore **both** 01 and 10.
1. After swap-diag cut: L0 → R0 ON R1 OFF ≥0.80  
2. After dual restore: L0 → R0 ON ∧ R1 ON ≥0.80  
3. After dual restore: L1 → R0 ON ∧ R1 ON ≥0.80  

## Bars
B1 L0 identity ≥0.80 · B2 L0 fanout ≥0.80 · B3 L1 fanout ≥0.80  

Seeds {3241,3251} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS. Completes dual-restore after both diagonals (E114 identity, E116 swap).

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Dual restore after swap-diag recovers full concurrent. Dual-restore matrix after both diagonals closed (E114 identity, E116 swap).
