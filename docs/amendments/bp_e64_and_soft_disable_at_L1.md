# BP-E64 — Soft-weaken one AND input at L1 endpoint

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E62 NULL (soft mid fail); E63 PASS (hard at L1)  
**Discipline:** not E62 retune — **soft weaken at L1** (same geometry as E63 hard, different prim)

## Hypothesis
L1–M, L2–M, M–R. Coincidence gate on M. Soft I at L1, `fire_weaken_bridge_radius=8`, frac=1.
1. Fire L1+L2 → R ON ≥0.90  
2. Fire I → fire L1+L2 → R OFF ≥0.90  
3. Restore L1–M → fire L1+L2 → R ON ≥0.85  

## Bars
| ID | thr |
|----|-----|
| B1 both-on | ≥0.90 |
| B2 soft-disable OFF | ≥0.90 |
| B3 restore ON | ≥0.85 |

Seeds {1911,1921} trials 8. Budget ~4 min, hard cap 8 min.

## Prediction
🔮 LEAN PASS if soft endpoint hit equals hard (E63). Miss if residual strength still satisfies coincidence.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Soft weaken at L1 endpoint disables AND; restore re-enables. Soft mid (E62) failed; soft endpoint (E64) works like hard (E63).
