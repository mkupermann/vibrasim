# JEP-142 — probabilistic reasoning that QUANTIFIES the compounding/aggregation insight

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 P(is_a) decays MULTIPLICATIVELY with chain depth (3 edges @0.9 -> 0.729, compounding) and noisy-OR over
  MULTIPLE paths exceeds any single path (aggregation). 100% on the battery. MOST-LIKELY MISS: shared-edge paths
  not independent -> noisy-OR over-counts (note the independence assumption).

## Acceptance
- PASS: chain probabilities match products, DAG noisy-OR exceeds single-path, within tolerance. Established
  (probabilistic inference, noisy-OR; Pearl), named; no novelty.

## Result — PASS (HIT)
Probabilistic battery 4/4: chain P(a->b)=0.9, P(a->c)=0.81, P(a->d)=0.729 (multiplicative COMPOUNDING decay,
quantifying JEP-137); DAG with 2 independent paths @0.81 each -> noisy-OR 0.964 > single 0.81 (AGGREGATION
robustness, quantifying JEP-138). Prediction HIT; tally 37/56; 34 tests gated green. The probabilistic layer makes
the qualitative inference-robustness insight QUANTITATIVE: chains MULTIPLY edge-probabilities (decay with depth),
redundant DAG paths NOISY-OR to higher confidence. Rounds out the engine's reasoning faculties (deduction,
induction, Boolean, three-valued, contradiction, quantification, comparison, compositional, analogy, hypothetical,
causal/interventional, probabilistic). HONEST: noisy-OR assumes INDEPENDENT paths — shared edges over-count (a known
approximation; exact correlated inference needs full belief propagation). Established (probabilistic inference /
noisy-OR, Pearl), named; no novelty.
