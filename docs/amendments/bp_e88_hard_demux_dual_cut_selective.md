# BP-E88 — Hard DEMUX dual-kill all arms then selective arm restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E86 soft DEMUX dual-cut; E85 hard 2x2  
**Discipline:** shared L three R; hard kill all arms; disarm; restore arm0 then arm1

## Hypothesis
1. Hard-kill all → fire L → all R OFF ≥0.80  
2. Disarm; restore arm0 → R0 ON others OFF ≥0.80  
3. Hard-kill arm0; restore arm1 → R1 ON others OFF ≥0.75  

## Bars
B1 all OFF ≥0.80 · B2 sel0 ≥0.80 · B3 sel1 ≥0.75  

Seeds {2601,2611} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS. Miss if hard kill at I damages shared L ports.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard DEMUX dual-kill all OFF; selective arm0 then arm1 restore.
