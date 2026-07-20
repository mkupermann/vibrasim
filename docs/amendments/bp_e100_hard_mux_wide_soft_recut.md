# BP-E100 — Hard MUX dual-kill full restore then soft re-cut path0 (wide sep)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E99; E97 soft wide-sep re-cut  
**Discipline:** hard wipe + full restore on wide-sep multi-L MUX; **soft** re-cut path0 (dist > r)

## Hypothesis
Paths y=10,32,48. Hard dual-kill all; full restore; soft re-cut path0 (r=10).
1. After full restore: all three ON ≥0.80  
2. Soft-cut path0 → OFF ≥0.80  
3. Path1&2 ON ≥0.80  

## Bars
B1 all ON ≥0.80 · B2 p0 OFF ≥0.80 · B3 others ON ≥0.80  

Seeds {2841,2851} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS (hard wipe + wide soft re-cut). Completes soft re-cut after hard wipe.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard MUX dual-kill full restore + soft re-cut path0 on wide-sep. Soft re-cut works after hard wipe when mid dist > soft radius.
