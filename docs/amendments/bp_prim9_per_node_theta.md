# PRIM9 — Per-node fire threshold (coincidence / AND enabler)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E38 NULL (fan-in is OR under uniform theta)

## Primitive
1. `world.k_theta_fire[i]`: if >0, overrides `cfg.theta_fire` for that node.  
2. `coincidence_and_enabled: bool = False`: bridge charge prop only deposits into a target if **≥2 distinct firers** inject to it on the **same tick** (coincidence AND).

Honest engineered coincidence gate.

## PRIM9-D0 bars
Fan-in L1–M–R, L2–M–R; `coincidence_and_enabled=True`.
| ID | Criterion | thr |
|----|-----------|-----|
| A1 | Fire L1 only: R peak latch ≤0.25 rate | ≥0.85 |
| A2 | Fire L2 only: R peak ≤0.25 rate | ≥0.85 |
| A3 | Fire L1+L2: R peak ≥1.0 rate | ≥0.85 |

Seeds {1161,1171} trials 10.

## Prediction
🔮 PASS: single-source prop blocked; dual same-tick opens M→R.

## RESULT
### PRIM9-D0 **PASS** (2026-07-20)
A1=1.0 A2=1.0 A3=1.0. Coincidence AND: single L silent at R; both L light R. Closes E38 boundary with new primitive.
