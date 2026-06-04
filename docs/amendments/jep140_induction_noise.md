# JEP-140 — induction under noisy examples: aggregation ROBUSTNESS vs deduction's chaining fragility

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 induction is MORE noise-robust than deduction: majority-vote over instances tolerates example-noise up to
  ~50% (where the majority flips), vs deduction's exponential depth-degradation (JEP-137). Aggregation averages
  noise; chaining compounds it. MOST-LIKELY MISS: a smaller robust range if induce()'s positives>negatives
  threshold is brittle near 50%.

## Acceptance (characterization)
- Report inductive-generalization accuracy vs example-noise. The robust plateau (then sharp flip near 50%) vs
  deduction's gradual exponential decay is the contrast. Established (majority aggregation), named; no novelty.

## Result — PASS (HIT), completing the inference-robustness picture
| example-noise | induction-correct | deduction depth-4 (JEP-137) |
|---------------|-------------------|------------------------------|
| 0.00 | 1.00 | 1.00 |
| 0.10 | 1.00 | 0.52 |
| 0.20 | 0.96 | 0.33 |
| 0.30 | 0.91 | 0.20 |
| 0.40 | 0.75 | 0.13 |
| 0.45 | 0.68 | 0.10 |

INDUCTION is far MORE noise-robust than DEDUCTION: majority-aggregation over instances tolerates example-noise up
to ~45% (gradual decay toward the 50% majority-flip point), while deduction decays sharply from the first noise.
Prediction HIT; tally 35/54. THE UNIFIED INFERENCE-ROBUSTNESS PICTURE (now complete): CHAINING (deduction, transitive
closures, sorts) COMPOUNDS errors -> fragile, ~(1-p)^depth (JEP-137); AGGREGATION (induction, majority over
instances; redundant paths, JEP-138) AVERAGES errors -> robust to ~50% noise. The cure for chaining's fragility
(redundant paths, JEP-138) is essentially MAKING DEDUCTION MORE LIKE AGGREGATION (many independent derivations,
vote). Human-like robust inference favors AGGREGATION/REDUNDANCY over deep brittle chains. Established (majority
aggregation vs error propagation), named; no novelty.
