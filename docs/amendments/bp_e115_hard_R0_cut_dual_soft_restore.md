# BP-E115 — Hard dual-cut R0 then dual soft restore 00+10

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E112 PASS (soft silence + dual soft restore); E113 NULL (hard silence + selective)  
**Discipline:** hard shared-endpoint silence + dual soft restore of both in-edges — not selective

## Hypothesis
Wide 2×2. Soft dual-cut all; restore all; hard-cut 00+10.  
Then soft restore **both** 00 and 10.
1. After hard R0 dual-cut: L0 and L1 → R0 OFF ∧ R1 ON ≥0.80  
2. After dual soft restore: L0 → R0 ON ∧ R1 ON ≥0.80  
3. After dual soft restore: L1 → R0 ON ∧ R1 ON ≥0.80  

## Bars
B1 hard silence ≥0.80 · B2 L0 fanout ≥0.80 · B3 L1 fanout ≥0.80  

Seeds {3221,3231} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS. Dual restore after hard silence should match E112 after soft silence.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard dual-cut R0 silence + dual soft restore recovers full fanout. Hard silence recoverable when **both** in-edges restored (selective E113 fails).
