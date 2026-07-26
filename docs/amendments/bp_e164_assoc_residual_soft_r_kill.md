# BP-E164 — Association residual survives soft R-port kill

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E162 residual; E155 soft wipe fails to clear dual decade content  
**Discipline:** multi-trial c0 residual; soft kill R port only; L-only probe — no dual re-write of R before score

## Hypothesis
Multislot OFF. c0: L=500, R=5000.  
**Treatment:** N_train=15 dual; soft kill R port (weaken-bridge fire); L-only rewrite 500; idle.  
**Control:** no dual train; soft kill R; L-only 500.  

1. Treatment: R residual high after soft R kill + L-only ≥0.80  
2. Control: no R high partner ≥0.80  
3. Treatment: L mean still low ≥0.90  

Tests residual co-presence durability under soft port kill (E155 class content survival vs residual).

## Bars
B1 treat R residual ≥0.80 · B2 ctrl no R partner ≥0.80 · B3 treat L low ≥0.90  

Seeds {4401,4411} trials 8. Budget ~12 min, hard cap 24 min.

## Prediction
🔮 LEAN PASS for residual survival (E155 soft kill leaves content). NULL if residual is more fragile than decade specialisation.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Soft R-port kill does not clear multi-trial association residual; L-only probe still finds R-high co-presence. Aligns with E155 soft-kill content survival.
