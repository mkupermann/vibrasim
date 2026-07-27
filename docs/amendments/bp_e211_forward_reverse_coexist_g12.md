# BP-E211 — Forward + reverse fire-select co-presence under G12

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E194 forward G12; E205 reverse G12; E206 reverse multi-trial  
**Discipline:** same dual train+tags; **same world** multi-trial: forward L→R then reverse R→L for both patterns without retrain. Not reverse-only or soft-kill re-probe.

## Hypothesis
Train dual train-time tags; gate ON.
1. pid1 forward L-lo → R-hi ≥0.80  
2. pid1 reverse R-hi → L-lo ≥0.80  
3. pid2 forward L-hi → R-lo ≥0.80 AND reverse R-lo → L-hi ≥0.80 (both same trial)  

## Bars
B1 fwd c0 ≥0.80 · B2 rev c0 ≥0.80 · B3 both dirs c1 ≥0.70  

Seeds {6001,6011} trials 6. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if pair-link supports bidirectional select without path destruction under sequential probes.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Same-world forward+reverse fire-select coexist under G12 multi-trial without retrain.
