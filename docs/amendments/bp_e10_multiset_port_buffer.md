# BP-E10 — Multiset port buffer (K=3 bands one side)

**PRE-REGISTERED 2026-07-20 before data (night)**  
**Depends on:** PRIM4-D0 PASS

## Hypothesis
With multislot ON, sequential ILW of three bands {400, 1500, 5000} on L only leaves **all three** nearest-centroid bins occupied on L ≥ **0.85**. Legacy OFF: all-three rate ≤ **0.15**.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Multislot: fraction trials with 3/3 bins occupied | ≥ **0.85** |
| B2 | Legacy: fraction with 3/3 bins | ≤ **0.15** |
| B3 | Multislot: n_L4 on L ≥ 3 | ≥ **0.85** |

Seeds {401, 411}, trials 10; N_write=10/band; T_idle=40.

## Prediction
🔮 PASS

## RESULT
**PASS** (2026-07-20 night). B1=1.0 B2=0.0 B3=1.0. Multiset K=3 holds under PRIM4.
