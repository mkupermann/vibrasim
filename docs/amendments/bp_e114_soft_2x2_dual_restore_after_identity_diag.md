# BP-E114 — Soft 2×2 identity-diag cut then dual restore 00+11

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E105 PASS; E111 NULL (selective 00); E112 PASS (dual restore after R0 silence)  
**Discipline:** dual restore of both cut diagonal arms after pure-swap routing — control analogue of E112

## Hypothesis
Wide 2×2. Soft dual-cut all; restore all; soft-cut 00+11 (pure swap).  
Then restore **both** 00 and 11.
1. After diag cut: L0 → R1 ON R0 OFF ≥0.80  
2. After dual restore: L0 → R0 ON ∧ R1 ON ≥0.80  
3. After dual restore: L1 → R0 ON ∧ R1 ON ≥0.80  

## Bars
B1 L0 swap ≥0.80 · B2 L0 fanout ≥0.80 · B3 L1 fanout ≥0.80  

Seeds {3201,3211} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS. Selective failed (E111); dual restore both cut arms should recover full concurrent.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Dual restore of both identity-diag cut arms recovers full concurrent fanout. Selective (E111) fails; dual succeeds.
