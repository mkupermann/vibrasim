# BP-C20 — Strength-decay free dual without midplane wall

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** C16/C17 provisional; C18 PASS  
**Discipline:** same dual-band + tau=30 as C16, but **midplane_wall_enabled=False** — tests wall dependence

## Hypothesis
Without midplane wall, free particles mix; decay alone insufficient for ≥0.80 specialisation (mean_L < mean_R ∧ both n≥1). With wall OFF and decay ON, success ≤0.70; with wall ON and decay ON (matched seeds positive), ≥0.70.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | No-wall + decay specialisation | ≤0.70 |
| B2 | Wall + decay specialisation (same seeds) | ≥0.70 |
| B3 | No-wall both populated | ≥0.70 |

Seeds {2391,2401,2411} trials 3. T=1200. Budget ~15 min, hard cap 30 min.

## Prediction
🔮 LEAN PASS (wall required for spatial segregation). NULL if decay alone segregates without wall.

## RESULT
**PASS** (2026-07-20). B1_nowall=0.333 B2_wall=0.889 B3_pop=1.0.  
Midplane wall required for dual-band specialisation under decay; without wall, mix kills decade structure.
