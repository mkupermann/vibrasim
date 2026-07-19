# BP-A2 — Density ratio robustness (Rung A depth)

**PRE-REGISTERED** 2026-07-19 · headless  

## Hypothesis
At N∈{20,40,80}, cluster/sparse electron-count ratio ≥ **2.0** mean across seeds, and scramble/cluster ratio ≤ **0.55** (pair rule still required). Extends A1 across N grid.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | mean_N (e_cluster / max(e_sparse,1)) | ≥ 2.0 |
| B2 | mean_N (e_scramble / max(e_cluster,1)) | ≤ 0.55 |
| B3 | all N have e_cluster ≥ 3 | PASS |

## Protocol
N grid {20,40,80}, seeds {101,103}, T=200, same plant as A1, 3 trials per N×seed.

## RESULT
*(after)*
