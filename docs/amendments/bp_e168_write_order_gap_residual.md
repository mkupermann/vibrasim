# BP-E168 — Write-order temporal residual (L-first gap R vs R-first gap L)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E167 temporal-gap residual (if PASS); E3 order-without-decay CLOSED  
**Discipline:** same freqs; only within-trial **order** of port writes differs; residual after L-only

## Hypothesis
Multislot OFF. F_L=500, F_R=5000, T_GAP=40.  
**Arm A:** multi-trial L → gap → R then L-only probe.  
**Arm B:** multi-trial R → gap → L then L-only probe.  

1. Arm A: R residual high ≥0.80  
2. Arm B: R residual high ≥0.80  
3. |rate_A − rate_B| ≤ 0.25 (order does not flip residual availability)

Tests order-independence of temporal association residual (E3 class for engineered ports).

## Bars
B1 arm A residual ≥0.80 · B2 arm B residual ≥0.80 · B3 |Δ| ≤0.25  

Seeds {4481,4491} trials 8. Budget ~14 min, hard cap 28 min.

## Prediction
🔮 LEAN PASS both arms residual if E167 PASS (content accumulation order-blind). NULL if only L-first leaves residual.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=0.0. Write order L-first vs R-first does not affect residual availability after L-only (order-blind content accumulation; E3 class for ports).
