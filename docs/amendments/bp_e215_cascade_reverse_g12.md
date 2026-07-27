# BP-E215 — Cascade reverse fire-select under G12 pattern gate

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E214 cascade reverse PASS; E205 reverse+G12  
**Discipline:** dual L-M-R cascade train-time tags; reverse fire R→L under G12. Correct reverse OK; wrong-pattern reverse blocked.

## Hypothesis
Train path0 pid1, path1 pid2 via active_pattern_id. Gate ON.
1. pid1; fire R0 → L0 reverse ≥0.80  
2. pid2; fire R0 → L0 reverse **fails** ≥0.70  
3. pid2; fire R1 → L1 reverse ≥0.80  

## Bars
B1 correct rev p0 ≥0.80 · B2 wrong rev fail ≥0.70 · B3 correct rev p1 ≥0.80  

Seeds {6161,6171} trials 6. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if multi-hop reverse respects G12 like single-hop reverse E205.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Cascade reverse under G12: correct reverse OK; wrong-pattern reverse blocked; reverse p1 OK.
