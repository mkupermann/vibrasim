# BP-E96 — Soft MUX dual-cut full restore then soft re-cut path0

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E90 soft MUX full restore; E92 DEMUX soft re-cut NULL  
**Discipline:** multi-L MUX (separate L per path) — soft re-cut path0 after full restore should NOT collateral other paths

## Hypothesis
Three L–M–R (y=12,25,38). Soft dual-cut all; restore all; soft re-cut path0 only.
1. After full restore: all three paths ON ≥0.80  
2. Soft-cut path0 → path0 OFF ≥0.80  
3. Path1 and path2 still ON ≥0.80  

## Bars
B1 all ON ≥0.80 · B2 path0 OFF ≥0.80 · B3 path1&2 ON ≥0.80  

Seeds {2761,2771} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS (separate L isolates soft cut). Miss if I radii still overlap mids.

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=1.0 B3=0.0.  
Full restore works; path0 soft re-cut silences path0 but **path1/path2 also fail**. Separate-L does not prevent soft-radius mid collateral (same y-sep=13, r=10 as E92).
