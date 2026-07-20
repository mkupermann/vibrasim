# BP-E120 — Hard dual-cut split R0a/R0b then selective soft restore 00

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E119 PASS (soft selective on split R0); E113 NULL (hard shared + selective fails)  
**Discipline:** hard silence on **non-shared** R0a/R0b + soft restore only 00 — hard analogue of E119

## Hypothesis
Same split topology as E119. Soft dual-cut all; restore all; hard-cut 00+10; soft restore **only 00**.
1. After hard dual-cut: L0→R0a OFF ∧ R1 ON; L1→R0b OFF ∧ R1 ON ≥0.80  
2. After soft restore 00: L0→R0a ON ∧ R1 ON ≥0.80  
3. After soft restore 00: L1→R0b OFF ∧ R1 ON ≥0.80  

## Bars
B1 hard silence ≥0.80 · B2 L0 fanout ≥0.80 · B3 L1 R0b still OFF ≥0.80  

Seeds {3321,3331} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS. Hard silence + non-shared endpoints should keep L-selective restore (unlike shared E113).

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard dual-cut on split R0a/R0b + soft selective restore 00 is L-selective. Soft (E119) + hard (E120) non-shared selective restore closed.
