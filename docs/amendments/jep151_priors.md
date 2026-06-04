# JEP-151 — structural priors (Occam) for one-shot / ambiguous structure learning

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 an Occam/simplicity prior on MINIMAL ambiguous data picks the true structure FAR better than random-among-
  consistent WHEN the true structure is SIMPLE (typical), but WORSE when it is genuinely complex (the prior's bias)
  — the honest no-free-lunch tradeoff. MOST-LIKELY MISS: the prior helping less if many simple rules tie.

## Acceptance (characterization)
- Report accuracy of Occam vs random selection among consistent hypotheses, split by true-structure complexity.
  The simple-helps / complex-hurts tradeoff is the finding. Established (Occam/MDL priors; Bayesian Occam), named.

## Result — PASS (HIT), completing the structure-learning frontier characterization
| true-depth | n_obs | Occam-correct | random-correct |
|------------|-------|---------------|-----------------|
| 1 (simple) | 1 | 0.87 | 0.17 |
| 1 | 2 | 0.99 | 0.57 |
| 2 | 1 | 0.30 | 0.15 |
| 2 | 2 | 0.81 | 0.55 |
| 3 (complex) | 1 | 0.06 | 0.18 |
| 3 | 2 | 0.46 | 0.60 |

An Occam prior helps one-shot/minimal structure inference DRAMATICALLY when the true structure is SIMPLE (depth 1:
0.87 vs 0.17 from a single example), still helps for moderate complexity with a bit more data, but HURTS when the
true structure is genuinely COMPLEX (depth 3: 0.06 vs random 0.18 — Occam under-fits, picks too-simple a rule). The
honest NO-FREE-LUNCH tradeoff: priors buy one-shot generalization ONLY when the world matches the prior; the bias
is the price. Prediction HIT; tally 46/65. This is the genuine answer to the noisy/sparse/ONE-SHOT structure-
learning frontier (the "needs priors" piece): priors DO enable one-shot learning, with a bias cost. COMPLETES the
structure-learning frontier characterization: clean=easy (search-cost), noisy=hard (closures compound, redundancy
at cost), sparse-passive=ambiguous, sparse=active-querying solves, ONE-SHOT=priors help with a bias cost.
Established (Occam/MDL priors; Bayesian Occam razor; no-free-lunch), named; no novelty.
