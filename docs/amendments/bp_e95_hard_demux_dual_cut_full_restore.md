# BP-E95 — Hard DEMUX dual-kill then full restore all three arms

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E88 hard selective DEMUX; E91 hard MUX full  
**Discipline:** shared L three R; hard kill all; disarm; restore all three; fire L lights all R

## Hypothesis
1. Hard-kill all → all R OFF ≥0.80  
2. Disarm; restore all three → all R ON ≥0.80  
3. Hard re-cut arm0 → R0 OFF R1&R2 ON ≥0.80  

## Bars
B1 all OFF ≥0.80 · B2 all ON ≥0.80 · B3 hard re-cut0 selective ≥0.80  

Seeds {2741,2751} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS. Miss if hard kill at I damages shared L ports for restore.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard DEMUX dual-kill full restore + hard re-cut arm0 selective.
