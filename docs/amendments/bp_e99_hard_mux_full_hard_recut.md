# BP-E99 — Hard MUX full restore then hard re-cut path0

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E91 hard MUX full restore; E98 soft full + hard re-cut  
**Discipline:** hard dual-kill all three paths; full restore; hard re-cut path0 only

## Hypothesis
1. Hard-kill all → all OFF ≥0.80  
2. Full restore → all three ON ≥0.80  
3. Hard re-cut path0 → path0 OFF, path1&2 ON ≥0.80  

## Bars
B1 all OFF ≥0.80 · B2 all ON ≥0.80 · B3 selective re-cut ≥0.80  

Seeds {2821,2831} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS (E95/E98 composition on multi-L hard wipe). Completes hard MUX wipe-restore-recut.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard MUX dual-kill full restore + hard re-cut path0 selective.
