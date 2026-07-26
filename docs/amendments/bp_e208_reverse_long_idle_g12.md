# BP-E208 — Reverse fire-select long-idle durability under G12

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E205–E207 reverse+G12; E184/E193 forward long-idle  
**Discipline:** train-time tags; idle T=400; reverse c0 and c1 still select under G12. Not multi-trial switch re-probe.

## Hypothesis
Train dual with active_pattern_id; idle 400 ticks; no retrain.
1. pid1; fire R-hi → L-lo reverse ≥0.80  
2. pid2; fire R-lo → L-hi reverse ≥0.80  
3. Both arms succeed same trial ≥0.70  

## Bars
B1 reverse c0 after idle ≥0.80 · B2 reverse c1 after idle ≥0.80 · B3 both ≥0.70  

Seeds {5881,5891} trials 6. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if reverse pair-link durable like cascade long-idle E193.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Reverse fire-select under G12 durable after idle T=400 without retrain.
