# BP-E92 — Soft DEMUX dual-cut then full restore all three arms

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E86 selective DEMUX; E90 full MUX  
**Discipline:** shared L three R; soft-cut all; disarm; restore arms 0+1+2; L lights all three R

## Hypothesis
1. Soft-cut all → fire L → all R OFF ≥0.80  
2. Disarm; restore all three → fire L → all three R ON ≥0.80  
3. After full restore, single-arm cut still works: soft-cut arm0 → R0 OFF others ON ≥0.75  

## Bars
B1 all OFF ≥0.80 · B2 all three ON ≥0.80 · B3 selective cut arm0 after full ≥0.75  

Seeds {2681,2691} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS. Miss if full restore after wipe loses fan-out independence.

## RESULT
*(after)*
