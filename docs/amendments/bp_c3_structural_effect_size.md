# BP-C3 — Dual-drive structural effect size (Rung C, different claim)

**PRE-REGISTERED** 2026-07-19 · headless  
**Not** a retune of C1b’s 0.90 accuracy bar — new metric: **effect size**.

## Hypothesis
Under dual drive (L low-band, R high-band), mean decade left is **systematically lower** than mean decade right:  
mean over trials of (mean_R − mean_L) ≥ **0.40**, with both sides populated ≥80% of trials, and same-band control mean |Δ| ≤ **0.20**.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | mean(Δ) = mean(md_R − md_L) on dual | ≥ 0.40 |
| B2 | same-band mean\|Δ\| | ≤ 0.20 |
| B3 | both populated fraction (dual) | ≥ 0.80 |
| B4 | fraction of dual trials with Δ>0 | ≥ 0.70 |

## Protocol
Reuse C1b geometry: N=400/side, T=1200, box 80×50×50, r_2=28, seeds **{91,93,97}**, 3 trials/seed.

## RESULT
*(after)*
