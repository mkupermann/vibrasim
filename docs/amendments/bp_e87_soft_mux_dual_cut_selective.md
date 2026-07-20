# BP-E87 — Soft 3-path MUX dual-cut all then selective path restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E49 soft MUX; E86 DEMUX dual-cut  
**Discipline:** three separate L–M–R paths; soft-cut all; restore path0 then path1

## Hypothesis
1. Soft-cut all three paths → each probe L_k → R_k OFF ≥0.80  
2. Disarm; restore path0 only → only path0 ON ≥0.80  
3. Soft-cut path0; restore path1 → only path1 ON ≥0.75  

## Bars
B1 all OFF ≥0.80 · B2 sel0 ≥0.80 · B3 sel1 ≥0.75  

Seeds {2581,2591} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS (E49+E86 composition). Miss if path I radii overlap on cut.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Soft 3-path MUX dual-cut all OFF; selective path0 then path1 restore.
