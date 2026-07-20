# BP-E91 — Hard 3-path MUX dual-kill then full restore all paths

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E90 soft full restore; E89 hard selective  
**Discipline:** hard kill all three paths; disarm; restore all three; isolation holds

## Hypothesis
1. Hard-kill all → all OFF ≥0.80  
2. Disarm; restore all three → all three ON ≥0.80  
3. Isolation: each L_j lights only R_j ≥0.80  

## Bars
B1 all OFF ≥0.80 · B2 all ON ≥0.80 · B3 isolation ≥0.80  

Seeds {2661,2671} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS (E90 hard analogue). Miss if structural wipe permanently damages multi-path rewrite.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard 3-path MUX dual-kill then full restore; isolation holds.
