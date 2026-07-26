# BP-E202 — Asymmetric R-only pattern tags for G12 wrong-arm block

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E201 PASS L-only tags suffice  
**Discipline:** complement — tag **only R** endpoints; L stays pid=0. Same bars as E201. Tests whether partner tags alone block wrong-arm (E201 implies no).

## Hypothesis
Train c0+c1 ambient. Post-hoc: R-hi→pid1, R-lo→pid2; L untagged (0). Gate ON.
1. active_pattern_id=1; fire L-lo → R-hi select ≥0.90  
2. active_pattern_id=2; fire L-lo → R-hi select **fails** ≥0.70  
3. Sanity both-end wrong fail ≥0.70  

## Bars
B1 correct R-only ≥0.90 · B2 wrong-arm R-only ≥0.70 · B3 both-end wrong fail ≥0.70  

Seeds {5641,5651} trials 8. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN NULL on B2 (wrong-arm). L fires ambient under gate (E197/E201); R tags alone should not suppress wrong-arm select. B1/B3 may still pass.

## RESULT
**NULL** (2026-07-26). B1=1.0 B2=0.0 B3=1.0. R-only tags: correct select OK; wrong-arm block fails (ambient L fires). Complements E201 — firing-side tags required for suppression.
