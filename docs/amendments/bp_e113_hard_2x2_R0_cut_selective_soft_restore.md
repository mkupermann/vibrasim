# BP-E113 — Hard dual-cut R0 in-edges then selective soft restore 00 only

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E110 NULL (soft dual-cut + soft selective restore leaks); E104  
**Discipline:** hard structural silence of both R0 in-edges, then soft restore **only** 00 — hard-cut analogue of E110

## Hypothesis
Wide 2×2. Soft dual-cut all; restore all; **hard-cut** 00+10 (r=8 kill).  
Then soft restore **only arm 00** (disarm first).
1. After hard R0 dual-cut: L0 and L1 → R0 OFF ∧ R1 ON ≥0.80  
2. After soft restore 00: L0 → R0 ON ∧ R1 ON ≥0.80  
3. After soft restore 00: L1 → R0 OFF ∧ R1 ON ≥0.80  

## Bars
B1 hard silence ≥0.80 · B2 L0 fanout ≥0.80 · B3 L1 still R0-silent ≥0.80  

Seeds {3181,3191} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN NULL or lean PASS. Hard kill may remove residual 10 bridges that soft restore of 00 re-amplified in E110. If shared R0 still couples, NULL again.

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=1.0 B3=0.0. Hard dual-cut silences R0; soft restore 00 still revives L1→R0. Hard silence does **not** fix E110 selective-restore leak.
