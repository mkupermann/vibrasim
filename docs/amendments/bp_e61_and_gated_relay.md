# BP-E61 — Coincidence-AND gated relay

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** PRIM9 coincidence AND; E29 two-hop relay  
**Discipline:** path L–G–R where G is coincidence gate: R ON only if L **and** G fire together

## Hypothesis
Ports L, G (gate), R. Links L–G and G–R. Mid G tagged `k_coincidence_gate=1` with `coincidence_and_enabled`.
1. Fire L alone → R OFF ≥0.90 (no single-input pass)  
2. Fire L and G concurrent → R ON ≥0.90  
3. Fire G alone → R OFF ≥0.90  

## Bars
| ID | thr |
|----|-----|
| B1 L-only silent | ≥0.90 |
| B2 L+G ON | ≥0.90 |
| B3 G-only silent | ≥0.90 |

Seeds {1791,1801} trials 8. Budget ~4 min, hard cap 8 min.

## Prediction
🔮 LEAN PASS if PRIM9 blocks single-input prop on gated node. Miss if L–G–R still acts as plain OR relay.

## RESULT
*(after)*
