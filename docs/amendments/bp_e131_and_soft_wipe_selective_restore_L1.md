# BP-E131 — Coincidence AND soft dual wipe → restore only L1 → then restore L2

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E128 PASS (dual restore); E63/E64 single-arm disable  
**Discipline:** selective single-arm restore after dual AND wipe — not dual restore, not free talent

## Hypothesis
L1,L2 → gated M → R. Soft dual-cut I1+I2.  
1. After dual wipe: dual fire OFF ≥0.80  
2. After restore **only L1-M** (+ re-arm gate, M-R if needed): dual fire still OFF ≥0.80 (AND needs both)  
3. After restore L2-M as well: dual fire ON ≥0.80  

## Bars
B1 dual wipe silence ≥0.80 · B2 selective L1-only still silence ≥0.80 · B3 full both restore dual ON ≥0.80  

Seeds {3581,3591} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS. AND semantics: one arm restore insufficient; both required.

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=0.0 B3=1.0. Dual wipe silences; L1-only restore already allows dual fire (B2 fails — residual L2 or AND not requiring both after partial restore). Both restore dual ON.
