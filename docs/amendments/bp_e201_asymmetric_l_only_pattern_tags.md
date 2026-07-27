# BP-E201 — Asymmetric L-only pattern tags for G12 wrong-arm block

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E194–E197 G12; E197 tags load-bearing for wrong-arm block (both ends)  
**Discipline:** **new question** — after dual ILW train ambient, tag **only L** endpoints by band; R stays pid=0. Does wrong-arm block still hold?

## Hypothesis
Train c0 (L-lo→R-hi) + c1 (L-hi→R-lo) ambient. Post-hoc: L-lo→pid1, L-hi→pid2; R untagged (0). Gate ON.
1. active_pattern_id=1; fire L-lo → R-hi select ≥0.90  
2. active_pattern_id=2; fire L-lo → R-hi select **fails** ≥0.70  
3. Sanity: both-end tags wrong-arm fail ≥0.70 (matched protocol subset)

## Bars
B1 correct L-only ≥0.90 · B2 wrong-arm L-only ≥0.70 · B3 both-end wrong fail ≥0.70  

Seeds {5601,5611} trials 8. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN PASS if gate checks firing atom (L) pattern_id only; LEAN NULL if partner R tags also required.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. L-only pattern tags sufficient for correct select and wrong-arm block; R partner tags not required.
