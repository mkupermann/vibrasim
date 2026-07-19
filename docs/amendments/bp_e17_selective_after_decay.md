# BP-E17 — Selective recall after strength decay

**PRE-REGISTERED 2026-07-20 before data (night)**  
**Depends on:** E16 PASS, PRIM3 decay

## Hypothesis

Store pairs 0+1 with PRIM5 pair-link + multislot. Enable `ilw_strength_decay_tau=3.0`. Idle **T_hold=500** (strength leaks). Then selective fire L0 → peak_R0 > peak_R1 in ≥ **0.75** trials.  
Control: no pair_link → selective fraction ≤ **0.55**.  
Both bridges still alive after hold ≥ **0.80**.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Pair-link: selective after hold | ≥ **0.75** |
| B2 | No pair-link control selective | ≤ **0.55** |
| B3 | Pair-link: 2 cross bridges after hold | ≥ **0.80** |

Seeds {561, 571}, trials 10. Budget 180s / hard 360s.

## Prediction
🔮 LEAN NULL or borderline: atoms survive (L4 permanent) but charge prop may weaken if strength leak affects something else; bridges stay. Selectivity may hold because freqs remain.

## RESULT
**PASS** (2026-07-20 night). B1=**1.000**, B2=**0.000**, B3=**1.000**. Selective recall survives strength-decay hold; bridges persist.
