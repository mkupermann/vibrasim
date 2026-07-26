# BP-E207 — Reverse fire-select with train-time pattern_id (no post-hoc tag)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E205–E206 reverse+G12; E196 train-time forward  
**Discipline:** train with `active_pattern_id` set during ILW (pid1 c0, pid2 c1); **no post-hoc tag**. Reverse R→L under G12.

## Hypothesis
1. pid1; fire R-hi → L-lo reverse ≥0.80  
2. pid2; fire R-hi → L-lo reverse **fails** ≥0.70  
3. pid2; fire R-lo → L-hi reverse ≥0.80  

## Bars
B1 correct rev c0 ≥0.80 · B2 wrong rev fail ≥0.70 · B3 correct rev c1 ≥0.80  

Seeds {5841,5851} trials 6. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN PASS if train-time tags on both ends (via ILW active_pattern_id) suffice for reverse G12 like E196 forward.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Train-time active_pattern_id tags suffice for reverse G12; no post-hoc tag needed.
