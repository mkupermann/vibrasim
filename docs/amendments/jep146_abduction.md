# JEP-146 — abduction (inference to the best explanation), the third inference mode

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: abduce(effect) returns candidate causes (reverse causal closure) ranked by causal DISTANCE (most direct
  first = most parsimonious). abduce(slippery) -> [wetgrass, rain, sprinkler]. MOST-LIKELY MISS: ranking when
  multiple causes tie.

## Acceptance
- PASS: abduction battery = 100% (correct candidate set + directness ranking). Established (abductive reasoning,
  Peirce; diagnosis), named; no novelty. HONEST: qualitative ranking by directness/parsimony, not probabilistic
  posterior (that needs priors + likelihoods).

## Result — PASS (HIT), completing Peirce's inference triad
Abduction battery 4/4: abduce(slippery) -> [wetgrass, rain, sprinkler] (ranked by causal directness, wetgrass most
direct/parsimonious); abduce(wetgrass) -> [rain, sprinkler]; most-direct explanation of slippery = wetgrass; roots
return []. Prediction HIT; tally 41/60; 37 tests gated green. The engine now does ALL THREE classical inference
modes (Peirce): DEDUCTION (cause->effect, transitive closure), INDUCTION (instances->rule, JEP-105), ABDUCTION
(effect->best cause, this). A hallmark of human reasoning (diagnosis, explanation). Established (abductive reasoning,
Peirce 1903; diagnostic reasoning), named; no novelty. HONEST: qualitative ranking by directness/parsimony — not a
probabilistic posterior (which needs priors + likelihoods over causes; the noisy-OR layer JEP-142 could supply that
in a richer tier).
