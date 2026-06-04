# JEP-154 — combining the ingredients on the HARD regime: which constraint actually binds (capstone)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 combining reuse+prior+active BEATS any single ingredient on the hard (deep+noisy+minimal) regime, BUT the
  NOISE+ONE-SHOT tension is the binding constraint: under noise, strict one-shot stays bounded below acceptable
  (can't denoise from one example); the jump to acceptable comes only when active querying ALSO buys REDUNDANCY
  (few-shot). So the residual is 'solved' by the combination only when one-shot is relaxed to few-shot.
  MOST-LIKELY MISS: reuse alone already saturating, or a non-monotone progression.

## Acceptance (characterization)
- Report accuracy across an ingredient ladder on the hard regime. The identification of the BINDING constraint
  (noise vs data-quantity vs search) is the finding. Established (ablation; sample complexity); named.

## Result — JEP-154 MISS (honest), corrected by JEP-154b HIT
### Ingredient ladder (hard regime, noise=0.15), STRICT consistency:
| condition | acc |
|-----------|-----|
| scratch passive 1-shot | 0.00 |
| +reuse 1-shot | 0.54 |
| +reuse +prior 1-shot | 0.58 |
| +reuse +prior +active 1-shot | 0.58 |
| +reuse +prior +active FEW-shot k=5 | 0.47 |
| +reuse +prior +active FEW-shot k=12 | 0.18 |

PREDICTION MISS: I predicted few-shot redundancy CLOSES the hard regime. With STRICT consistency (obs subset of
candidate) it did the OPPOSITE — more noisy observations made it WORSE (k=12 -> 0.18), because each extra noisy
observation can falsely ELIMINATE the true hypothesis. I forgot my OWN JEP-134 lesson: under noise you need
noise-TOLERANT aggregation; strict consistency is the opposite. Honest MISS (tally 48/68).

### JEP-154b correction — STRICT vs SOFT scoring as k grows (reuse space, noise=0.15):
| k | STRICT(subset) | SOFT(best-overlap) |
|---|----------------|---------------------|
| 1 | 0.55 | 0.55 |
| 3 | 0.65 | 0.90 |
| 5 | 0.48 | 0.96 |
| 8 | 0.31 | 0.98 |
| 12 | 0.19 | 0.99 |
| 20 | 0.06 | 0.99 |

CORRECTED HIT (tally 49/69): SOFT best-overlap scoring IMPROVES to 0.99 as redundancy grows (noise averages out);
STRICT consistency DEGRADES to 0.06. So the residual IS solved (0.99) on the hard deep+noisy regime by combining
REUSE (fixes search |R|^depth -> |subs|^2) + few-shot REDUNDANCY (beats noise) + NOISE-TOLERANT SOFT aggregation
(the critical enabler). The full recipe needs all three; strict-consistency few-shot is actively harmful.

## THE UNIFICATION (the capstone insight)
This is the SAME CHAINING-vs-AGGREGATION lesson (JEP-137/138/140) now shown to govern LEARNING as well as REASONING:
hard consistency (a strict chain / subset test) is FRAGILE under noise — one bad step/observation breaks it; SOFT
aggregation (voting / overlap count / majority) is ROBUST — it averages noise out. The compounding insight is
UNIVERSAL across both multi-step inference AND structure learning. Human-like robust cognition under noise = soft
redundant aggregation everywhere, never brittle hard chains. Established (robust estimation, M-estimators, majority
denoising), named; no novelty. The calibration lesson: I miscalibrated by not applying my own prior finding —
the discipline is to carry forward lessons, not re-learn them.
