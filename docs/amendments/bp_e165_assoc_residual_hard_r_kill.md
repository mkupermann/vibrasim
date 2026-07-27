# BP-E165 — Association residual survives hard R-port kill

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E164 soft R kill residual PASS; E156 hard kill fails to clear dual decade  
**Discipline:** multi-trial c0 residual; hard kill R port only; L-only probe — no dual re-write of R before score

## Hypothesis
Multislot OFF. c0: L=500, R=5000.  
**Treatment:** N_train=15 dual; hard kill R port; L-only rewrite 500; idle.  
**Control:** no dual train; hard kill R; L-only 500.  

1. Treatment: R residual high after hard R kill + L-only ≥0.80  
2. Control: no R high partner ≥0.80  
3. Treatment: L mean still low ≥0.90  

Hard-kill analogue of E164 (soft). LEAN PASS if E156-class content survival extends to residual.

## Bars
B1 treat R residual ≥0.80 · B2 ctrl no R partner ≥0.80 · B3 treat L low ≥0.90  

Seeds {4421,4431} trials 8. Budget ~12 min, hard cap 24 min.

## Prediction
🔮 LEAN PASS (E156/E164 class). NULL if hard kill clears residual that soft left intact.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Hard R-port kill does not clear multi-trial association residual (matches E164 soft + E156 hard content survival).
