# BP-E112 — Soft 2×2 full restore, dual-cut R0, restore BOTH 00+10

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E104 PASS; E110 NULL (selective 00 leaks)  
**Discipline:** dual-arm restore control after shared-endpoint silence — not selective, not free talent

## Hypothesis
Wide 2×2. Soft dual-cut all; restore all; soft-cut 00+10 (R0 silent).  
Then restore **both** 00 and 10 (disarm first).
1. After R0 dual-cut: L0 and L1 → R0 OFF ∧ R1 ON ≥0.80  
2. After dual restore: L0 → R0 ON ∧ R1 ON ≥0.80  
3. After dual restore: L1 → R0 ON ∧ R1 ON ≥0.80  

## Bars
B1 silence ≥0.80 · B2 L0 full fanout ≥0.80 · B3 L1 full fanout ≥0.80  

Seeds {3161,3171} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS. E110 failed selective; dual restore should recover both L paths into R0.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Dual restore of both R0 in-edges after shared silence recovers full fanout for L0 and L1. Selective (E110) fails; dual succeeds.
