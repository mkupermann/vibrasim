# BP-E98 — Soft MUX full restore then hard re-cut path0

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E96 NULL soft re-cut; E93 DEMUX hard re-cut PASS  
**Discipline:** tight-sep multi-L MUX (y=12,25,38); soft dual-cut full restore; **hard** re-cut path0 r=8

## Hypothesis
1. After full soft-wipe+restore: all three paths ON ≥0.80  
2. Hard-cut path0 → path0 OFF ≥0.80  
3. Path1 and path2 still ON ≥0.80  

## Bars
B1 all ON ≥0.80 · B2 p0 OFF ≥0.80 · B3 p1&p2 ON ≥0.80  

Seeds {2801,2811} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS (E93 composition). Miss if hard kill at I0 still reaches path1 mid.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Tight-sep multi-L MUX: hard re-cut path0 local after full soft wipe+restore.
