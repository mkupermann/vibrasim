# BP-E97 — Soft MUX wide y-separation full restore + soft re-cut path0

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E96 NULL; E94 DEMUX wide-sep PASS  
**Discipline:** not E96 retune — multi-L MUX with **y=10,32,48** (mid dist ≥18 > soft r=10)

## Hypothesis
Three L–M–R paths wide-spaced. Soft dual-cut all; restore all; soft re-cut path0.
1. After full restore: all three ON ≥0.80  
2. Soft-cut path0 → path0 OFF ≥0.80  
3. Path1 and path2 still ON ≥0.80  

## Bars
B1 all ON ≥0.80 · B2 p0 OFF ≥0.80 · B3 p1&p2 ON ≥0.80  

Seeds {2781,2791} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS (E94 composition on multi-L). Miss if I offsets still overlap.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Wide-sep multi-L MUX soft re-cut path0 without collateral. Closes E96 geometry diagnosis.
