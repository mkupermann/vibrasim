# BP-E25 — Table-free map; bridge ablation control

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E24 NULL (rewire cons 0.63)  
**Not** E24 B3 retune — **new control**: kill all cross bridges before probe

## Hypothesis
Same train as E24 (K=3 multi-sample PRIM5). Treat: self-cons ≥0.80, min gap ≥0.20.  
**Ablation:** after train, set all bridges dead; latch probe self-cons ≤ **0.40** (no graph → no consistent partners). Multi-sample ≥0.90 treat.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Treat self-cons | ≥0.80 |
| B2 | Treat min gap | ≥0.20 |
| B3 | Ablation self-cons | ≤0.40 |
| B4 | Treat multi-sample | ≥0.90 |

Seeds {801,811} trials 8. Smoke 1×3.

## Prediction
🔮 PASS: ablation zeros routing; treat keeps E24-level cons.

## RESULT
**PASS** (2026-07-20). B1=1.0 B2=0.643 B3_ablation=0.0 B4=1.0.  
Table-free map defensible with **bridge ablation** control (rewire was weak).
