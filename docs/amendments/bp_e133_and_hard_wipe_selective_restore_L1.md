# BP-E133 — Coincidence AND hard dual wipe → restore only L1 → then restore L2

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E131 NULL (soft dual wipe + L1-only restore already dual ON); E129 hard dual wipe  
**Discipline:** hard dual-kill both L then selective soft restore L1 only — hard-wipe analogue of E131

## Hypothesis
L1,L2 → gated M → R. Hard dual-cut I1+I2.  
1. After hard dual wipe: dual OFF ≥0.80  
2. After restore only L1-M (+ M-R, re-arm gate): dual still OFF ≥0.80  
3. After restore L2-M: dual ON ≥0.80  

## Bars
B1 hard dual silence ≥0.80 · B2 L1-only still silence ≥0.80 · B3 both restore dual ON ≥0.80  

Seeds {3621,3631} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS if soft residual L2 caused E131 B2 fail; LEAN NULL if L1-only restore systematically re-enables dual regardless of wipe hardness.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard dual wipe + selective L1 restore keeps dual OFF until L2 restored. Soft residual L2 caused E131 fail; hard dual wipe enables true selective AND re-arm.
