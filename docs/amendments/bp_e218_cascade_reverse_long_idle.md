# BP-E218 — Cascade reverse long-idle durability

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E214–E217 cascade reverse; E208 reverse long-idle; E193 cascade long-idle forward  
**Discipline:** dual cascade train; idle T=400; reverse both paths still select. Completes cascade reverse durability.

## Hypothesis
Train dual cascade; idle 400; no retrain.
1. Fire R0 → L0 reverse ≥0.80  
2. Fire R1 → L1 reverse ≥0.80  
3. Both same trial ≥0.70  

## Bars
B1 rev p0 idle ≥0.80 · B2 rev p1 idle ≥0.80 · B3 both ≥0.70  

Seeds {6281,6291} trials 6. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if cascade reverse durable like forward cascade long-idle E193.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Cascade reverse both paths durable after idle T=400.
