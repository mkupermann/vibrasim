# BP-E89 — Hard 3-path MUX dual-kill all then selective path restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E87 soft MUX dual-cut; E58 hard MUX  
**Discipline:** three L–M–R paths; hard kill all; disarm; restore path0 then path1

## Hypothesis
1. Hard-kill all three → each L_k → R_k OFF ≥0.80  
2. Disarm; restore path0 only → only path0 ON ≥0.80  
3. Hard-kill path0; restore path1 → only path1 ON ≥0.75  

## Bars
B1 all OFF ≥0.80 · B2 sel0 ≥0.80 · B3 sel1 ≥0.75  

Seeds {2621,2631} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS (E87 hard analogue). Miss if hard kill damages restore capacity across paths.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard 3-path MUX dual-kill all OFF; selective path0 then path1 restore.
