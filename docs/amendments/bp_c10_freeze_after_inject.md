# BP-C10 — Free dual-band: ballistic inject then freeze velocities

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** C9 NULL (vel=0 from t=0 → no L4); moving free fails 0.90  
**Discipline:** **new mechanism** = inject with motion, after T_ball set all free vib vel=0, continue evolve

## Hypothesis
Midplane ON. Dual free inject L-low/R-high with speed 5–25 for T_ball=100 ticks (seed encounters), then zero all free velocities, evolve remaining T_rest.  
md_L < md_R ≥ **0.90**. Control continuous motion whole T ≤ **0.80**. Pop ≥0.80. χ ≤0.15 freeze arm.

## Bars
| ID | thr |
|----|-----|
| B1 freeze arm spec | ≥0.90 |
| B2 continuous motion spec | ≤0.80 |
| B3 freeze pop | ≥0.80 |
| B4 freeze χ | ≤0.15 |

Seeds {1411,1421,1431} trials 3; T_total=1000; T_ball=100.

## Prediction
🔮 LEAN NULL or borderline: freeze may leave L4 if formed in ballistic phase; may not hit 0.90.

## RESULT
**NULL** (2026-07-20). B1_freeze=**0.444**, B2_motion=**0.667**, B3_pop=**0.556**, B4_χ=0.  
Ballistic-then-freeze does not hit 0.90 specialisation; pop incomplete. Free talent still blocked under this mechanism.
