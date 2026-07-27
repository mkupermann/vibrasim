# BP-E162 — Multi-trial dual-port association without baked readout map

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E4 write-time association (map in readout); E12 no generative partner after R kill  
**Discipline:** multi-trial joint train of **one** fixed association; probe L-only **without** external class map — score residual R partner co-presence (not generation after kill)

## Hypothesis
Multislot OFF. Fixed association c0: L=500, R=5000.  
**Treatment:** N_train=15 joint dual writes with short idle between; then L-only rewrite 500 (no R write).  
**Control:** no dual train; L-only write 500.  

1. Treatment: after L-only rewrite, R mean high (partner residual) ≥0.80  
2. Control: after L-only, R mean high ≤0.20  
3. Treatment: L mean still low ≥0.90  

Not generative (E12); tests multi-trial co-presence residual without baked map in readout.

## Bars
B1 treat R partner residual ≥0.80 · B2 ctrl R partner ≤0.20 · B3 treat L low ≥0.90  

Seeds {4341,4351} trials 8. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN PASS for residual co-presence (R survives L-only rewrite). NULL if L rewrite disrupts R under multislot OFF.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Multi-trial dual-port train leaves R-side high-freq residual after L-only probe; control L-only has no R partner. Not generative (E12); co-presence residual without baked class map.
