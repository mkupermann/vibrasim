# BP-E118 — Hard multi-trial R0 silence → dual soft restore → hard silence again

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E117 PASS (soft multi-trial); E115 PASS (hard silence + dual soft restore)  
**Discipline:** hard analogue of E117 multi-trial shared-endpoint silence cycle

## Hypothesis
Wide 2×2. Soft dual-cut all; restore all.  
1. Hard-cut 00+10 → L0 and L1 R0 OFF ∧ R1 ON ≥0.80  
2. Dual soft restore 00+10 → both L full fanout ≥0.80  
3. Hard-cut 00+10 again → silence again ≥0.80  

## Bars
B1 first hard silence ≥0.80 · B2 dual restore fanout ≥0.80 · B3 second hard silence ≥0.80  

Seeds {3281,3291} trials 6. Budget ~12 min, hard cap 24 min.

## Prediction
🔮 LEAN PASS. Hard multi-trial shared silence matches soft E117.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard multi-trial R0 silence ↔ dual soft restore ↔ hard silence. Soft (E117) + hard multi-trial shared silence closed.
