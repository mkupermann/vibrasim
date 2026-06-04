# JEP-138 — noise-robust reasoning via redundant paths (constructive answer to the compounding fragility)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 under edge-noise, a DAG (redundant independent paths per conclusion) degrades SLOWER than a chain (single
  path) — a true conclusion survives if ANY path does. MOST-LIKELY MISS: noisy edges add SPURIOUS paths raising
  the DAG's false-positive rate, offsetting the true-positive gain.

## Acceptance (characterization)
- Report true-positive recall AND false-positive rate for chain vs DAG under noise. The redundancy-robustness
  tradeoff is the finding. Established (redundancy/error-correction), named; no novelty.

## Result — PASS (HIT, incl the predicted tradeoff)
| noise | chain TPR / FPR | DAG TPR / FPR |
|-------|-----------------|----------------|
| 0.05 | 0.92 / 0.02 | 0.90 / 0.04 |
| 0.10 | 0.83 / 0.05 | 0.88 / 0.05 |
| 0.20 | 0.73 / 0.08 | 0.89 / 0.14 |

DAG (redundant independent paths) has HIGHER true-positive recall under noise than a chain — markedly so at high
noise (0.89 vs 0.73 at 20%) — because a true conclusion survives if ANY of its paths does: redundant STRUCTURE
error-corrects broken edges. The predicted TRADEOFF materialized: more edges -> more spurious paths -> higher
false-positive rate (0.14 vs 0.08 at 20%). Prediction HIT on both the recall gain and the precision cost; tally
34/52. CONSTRUCTIVE ANSWER to the compounding fragility (JEP-137): build/seek REDUNDANT paths — redundancy buys
noise-robustness for what you want to CONCLUDE, at the cost of some over-conclusion. This CLOSES a coherent arc:
multi-step inference COMPOUNDS errors (137) -> redundant paths are the cure WITH a precision/recall tradeoff (138),
unifying structure-learning (128-136), reasoning (137), and noise-robustness. The deep lesson: human-like robust
inference under noise = many independent derivation paths + aggregation, not a single deep chain. Established
(redundancy / error-correcting inference), named; no novelty.
