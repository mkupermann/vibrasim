# BP-E58 — Three-path hard MUX curriculum

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E49 soft MUX PASS; E56 selective hard; PRIM12  
**Discipline:** same three separate L–M–R paths as E49; **hard kill** (not soft) to select

## Hypothesis
Three parallel L_k–M_k–R_k (y=12,25,38). Hard I_k near each M_k, `fire_kill_bridge_radius=12`.  
Curriculum: restore all, hard-kill all but path k; probe only R_k ON.

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Select path0 only | ≥0.80 |
| B2 | Select path1 only | ≥0.80 |
| B3 | Select path2 only | ≥0.80 |

Seeds {1681,1691} trials 6. Budget ~5 min, hard cap 10 min.

## Prediction
🔮 LEAN PASS (E49+E56 composition). Miss if hard kill over-destroys restore capacity across trials.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard-kill 3-path MUX curriculum; restore recovers selected path each step.
