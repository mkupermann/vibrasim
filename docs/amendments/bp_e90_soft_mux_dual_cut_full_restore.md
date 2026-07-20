# BP-E90 — Soft 3-path MUX dual-cut then full restore all paths

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E87 selective; E81 full 2x2 restore  
**Discipline:** soft-cut all three paths; disarm; restore paths 0+1+2; all three ON

## Hypothesis
1. Soft-cut all → all OFF ≥0.80  
2. Disarm; restore all three → each path ON ≥0.80  
3. Path isolation still holds: L0 lights only R0 ≥0.80  

## Bars
B1 all OFF ≥0.80 · B2 all three ON ≥0.80 · B3 L0 isolation ≥0.80  

Seeds {2641,2651} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS. Miss if full restore after wipe causes crosstalk.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Soft 3-path MUX dual-cut then full restore all paths; isolation holds.
