# BP-E206 — Reverse multi-trial switch under G12 (1→2→1)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E205 PASS reverse+G12; E195 forward multi-trial switch  
**Discipline:** reverse R→L fire-select multi-trial switch pid1→pid2→pid1 without retrain. Not E205 single-probe.

## Hypothesis
Train dual + tag both ends; gate ON. No retrain between probes.
1. pid1; fire R-hi → L-lo reverse ≥0.80  
2. pid2; fire R-lo → L-hi reverse ≥0.80  
3. pid1 again; fire R-hi → L-lo reverse ≥0.80  

## Bars
B1 reverse c0 ≥0.80 · B2 reverse c1 ≥0.80 · B3 reverse c0 again ≥0.80  

Seeds {5801,5811} trials 6. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN PASS if reverse+G12 multi-trial durable like E195 forward path.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Reverse multi-trial switch pid1→pid2→pid1 durable without retrain under G12.
