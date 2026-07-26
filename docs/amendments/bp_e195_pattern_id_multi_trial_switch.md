# BP-E195 — Pattern-id gated multi-trial switch (pid1→pid2→pid1)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E194 PASS G12 gated fire-select  
**Discipline:** same train+tag as E194; sequential probes active_pattern_id=1, then 2, then 1 again without retrain

## Hypothesis
1. active_pattern_id=1; fire L-lo → R-hi select ≥0.80  
2. active_pattern_id=2; fire L-hi → R-lo select ≥0.80  
3. active_pattern_id=1 again; fire L-lo → R-hi select ≥0.80  

## Bars
B1 first pid1 ≥0.80 · B2 pid2 ≥0.80 · B3 second pid1 ≥0.80  

Seeds {5401,5411} trials 8. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN PASS if E194 gate is multi-trial durable (E172 class for pattern_id).

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Pattern-id gate multi-trial switch 1→2→1 without retrain closed.
