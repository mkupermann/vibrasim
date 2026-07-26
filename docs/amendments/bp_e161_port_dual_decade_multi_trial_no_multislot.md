# BP-E161 — Port dual decade multi-trial switch with **multislot OFF**

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E159 NULL (multi-trial under multislot ON); E160 reverse no-multislot  
**Discipline:** multi-trial forward→reverse→forward under multislot OFF

## Hypothesis
`ilw_multislot_enabled=False`.  
1. L-low R-high → ordered ≥0.90  
2. L-high R-low → reverse ≥0.80  
3. L-low R-high again → ordered ≥0.80  

## Bars
B1 first ordered ≥0.90 · B2 reverse ≥0.80 · B3 final ordered ≥0.80  

Seeds {4261,4271} trials 8. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN PASS if E160 reverse works; completes multi-trial reconfig without multislot.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Multislot OFF multi-trial dual decade switch closed. Doctrine: dual decade reconfig requires multislot OFF (E160/E161); multislot ON retains bands (E157/E158/E159).
