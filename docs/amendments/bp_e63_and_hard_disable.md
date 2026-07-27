# BP-E63 — Hard-kill one input of coincidence AND

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** PRIM9 PASS; E62 NULL (soft mid fail); PRIM12  
**Discipline:** not E62 soft retune — **hard kill at L1** (r=8 covers L1–M only, not L2)

## Hypothesis
L1–M, L2–M, M–R. M coincidence gate. Hard I at L1 with `fire_kill_bridge_radius=8`.
1. Fire L1+L2 → R ON ≥0.90  
2. Fire I → fire L1+L2 → R OFF ≥0.90  
3. Restore L1–M → fire L1+L2 → R ON ≥0.85  

## Bars
| ID | thr |
|----|-----|
| B1 both-on | ≥0.90 |
| B2 hard-disable OFF | ≥0.90 |
| B3 restore ON | ≥0.85 |

Seeds {1861,1871} trials 8. Budget ~4 min, hard cap 8 min.

## Prediction
🔮 LEAN PASS (endpoint-local hard kill at L1). Miss if kill also destroys M–R via shared nodes.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard kill at L1 (r=8) disables dual-input AND; restore L1–M re-enables. Closes E62 soft-mid miss with endpoint-local hard cut.
