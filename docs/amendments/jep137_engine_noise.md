# JEP-137 — the engine under NOISY knowledge: does multi-hop reasoning compound errors? (connects the structure insight)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 is_a accuracy degrades with fact-noise p, and DEEPER chains degrade FASTER (~1-(1-p)^depth: any wrong edge
  breaks the chain), confirming compounding applies to REASONING not just learning. MOST-LIKELY MISS: noise also
  creating spurious false-positive paths, complicating the shape.

## Acceptance (characterization)
- Report is_a accuracy by query depth across fact-noise levels. The depth-dependent degradation IS the finding
  (the compounding insight, JEP-134/136, applied to the validated engine). Established, named; no novelty.

## Result — PASS (HIT); the UNIFIED compounding insight
| noise | depth1 | depth2 | depth3 | depth4+ |
|-------|--------|--------|--------|---------|
| 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 0.05 | 0.95 | 0.90 | 0.86 | 0.68 |
| 0.10 | 0.90 | 0.82 | 0.75 | 0.52 |
| 0.20 | 0.81 | 0.66 | 0.56 | 0.33 |

Clean knowledge -> perfect at every depth (validated, JEP-124). Under fact-noise, accuracy degrades and DEEPER
chains degrade FASTER (~(1-p)^depth: a true k-hop ancestor is recalled only if ALL k edges survived the noise).
Prediction HIT; tally 33/51. THE UNIFIED INSIGHT: reasoning COMPOUNDS errors exactly like structure LEARNING
(JEP-134/136) — ANY multi-step inference (learning structure OR reasoning over it) is fragile under noise because
it needs EVERY step correct, so reliability decays exponentially with inferential DEPTH. The engine is sound on
clean data (JEP-124) but inherits this compounding fragility under noisy knowledge: deeper conclusions are less
reliable. This is WHY human-like robustness needs error-correction / redundancy / re-derivation that scales with
inferential depth — a single clean pass over noisy knowledge gives shallow-reliable, deep-unreliable conclusions.
Honest characterization unifying the learning and reasoning frontiers. Established (error propagation in inference
chains), named; no novelty.
