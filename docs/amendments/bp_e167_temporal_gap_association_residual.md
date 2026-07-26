# BP-E167 — Temporal-gap dual association residual (non-simultaneous L then R)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E162 simultaneous dual residual PASS; residual family E162–E166 CLOSED PASS  
**Discipline:** multi-trial association without baked map; **new question** = residual after **sequential** L-write → gap → R-write (not same-tick dual)

## Hypothesis
Multislot OFF. c0: L=500, R=5000.  
**Treatment:** N_train=15 of (write L; idle T_GAP=40; write R; idle 8). Then L-only rewrite 500.  
**Control:** no R writes ever; L-only train + L-only probe.  

1. Treatment: R residual high after L-only ≥0.80  
2. Control: no R high partner ≥0.80  
3. Treatment: L mean still low ≥0.90  

Tests whether residual co-presence requires simultaneous dual ILW or survives temporal separation (honest multi-trial temporal association).

## Bars
B1 treat R residual ≥0.80 · B2 ctrl no R ≥0.80 · B3 treat L low ≥0.90  

Seeds {4461,4471} trials 8. Budget ~12 min, hard cap 24 min.

## Prediction
🔮 LEAN PASS if residual is accumulated content not coincidence-gated write. NULL if only same-tick dual co-write leaves residual (E162-class simultaneous-only).

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Temporal-gap (L → 40 ticks → R) multi-trial still leaves R residual after L-only; residual is accumulated content, not same-tick coincidence-only.
