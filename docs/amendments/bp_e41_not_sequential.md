# BP-E41 — Sequential NOT (light then clear)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E40 NULL (concurrent L+I re-latches R)  
**Not** E40 bar retune — **new protocol**: phase1 fire L, phase2 fire I only

## Hypothesis
Same L–M–R + I emitter as E40.
1. Phase L only (T_prop): end R ≥1.0 ≥0.90  
2. Phase L then I (T_prop each): end R after I ≤0.25 ≥0.90  
3. Phase I only: end R ≤0.25 ≥0.90  

## Bars
| ID | thr |
|----|-----|
| B1 L then measure | ≥0.90 rate R≥1 |
| B2 L then I then measure | ≥0.90 rate R≤0.25 |
| B3 I only | ≥0.90 rate R≤0.25 |

Seeds {1271,1281} trials 10.

## Prediction
🔮 PASS.

## RESULT
*(after)*
