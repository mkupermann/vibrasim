# BP-E117 — Soft 2×2 multi-trial R0 silence → dual restore → silence again

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E112 PASS; E107 multi-trial diagonal  
**Discipline:** multi-trial shared-endpoint silence/restore cycle — not free talent

## Hypothesis
Wide 2×2. Soft dual-cut all; restore all.  
1. Soft-cut 00+10 → L0 and L1 R0 OFF ∧ R1 ON ≥0.80  
2. Dual restore 00+10 → L0 and L1 both R ON ≥0.80  
3. Soft-cut 00+10 again → L0 and L1 R0 OFF ∧ R1 ON ≥0.80  

## Bars
B1 first silence ≥0.80 · B2 dual restore fanout ≥0.80 · B3 second silence ≥0.80  

Seeds {3261,3271} trials 6. Budget ~12 min, hard cap 24 min.

## Prediction
🔮 LEAN PASS. Multi-trial reconfig of shared R0 silence (E112 + re-cut).

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Multi-trial shared R0 silence → dual restore → silence again works. Multi-trial shared-endpoint reconfig closed.
