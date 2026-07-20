# PRIM12 — Fire kills nearby bridges (structural inhibit)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** latch-clear NOT CLOSED; need new inhibit class  
**Discipline:** not latch-zero farm

## Primitive
`fire_kill_bridge_radius: float = 0` (0=off)  
When a node with `k_kill_bridge_emitter[i]=1` fires, kill all alive bridges that have an endpoint within radius of the emitter (or any bridge touching a node within radius).

Honest structural cut for NOT/path disable.

## PRIM12-D0 / structural NOT
L–M–R path; I near M tagged kill-emitter, radius covers M.
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Fire L only: end R latch ≥1.0 | ≥0.90 |
| B2 | After I-fire: n_bridges < n_before | ≥0.90 |
| B3 | After cut, clear latch, fire L again: end R ≤0.25 | ≥0.90 |

Seeds {1291,1301} trials 10.

## Prediction
🔮 PASS: killing M–R bridge silences R permanently until retrain.

## RESULT
### PRIM12-D0 **PASS** (2026-07-20)
B1=1.0 B2=1.0 B3=1.0. Structural NOT: I-fire kills bridges; subsequent L silent at R.
