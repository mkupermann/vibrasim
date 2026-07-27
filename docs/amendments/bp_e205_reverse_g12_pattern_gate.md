# BP-E205 — Reverse fire-select under G12 pattern-id gate

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E204 reverse pair-link-native; E194–E197 G12; E201 L-tags  
**Discipline:** dual ILW train + post-hoc both-end tags; reverse fire R-band under active_pattern_id. Correct reverse OK; wrong-pattern reverse blocked.

## Hypothesis
Train c0 (L-lo→R-hi) + c1 (L-hi→R-lo) ambient; tag both ends (E194 style). Gate ON. No G6 required.
1. active_pattern_id=1; fire R-hi → L-lo reverse select ≥0.80  
2. active_pattern_id=2; fire R-hi → L-lo reverse **fails** ≥0.70  
3. active_pattern_id=2; fire R-lo → L-hi reverse select ≥0.80  

## Bars
B1 correct reverse c0 ≥0.80 · B2 wrong reverse fail ≥0.70 · B3 correct reverse c1 ≥0.80  

Seeds {5761,5771} trials 6. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN PASS if reverse path respects G12 gate on firing R atom tags (symmetric to forward E194).

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Reverse fire-select respects G12 gate: correct reverse OK; wrong-pattern reverse blocked; reverse c1 OK.
