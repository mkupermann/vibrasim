# JEP-141 — causal reasoning with intervention (Pearl's do-operator), a distinct human faculty

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: causal transitive reasoning (X->Y->Z so X causes Z) by closure; intervention do(Y) cuts Y's INCOMING
  edges so X no longer affects Z THROUGH Y. MOST-LIKELY MISS: the intervention edge-cutting semantics.

## Acceptance
- PASS: causal battery = 100% (transitive causation + correct intervention). Established (causal graphs + do-
  calculus, simplest form; Pearl), named; no novelty. HONEST: a qualitative causal graph (no probabilities);
  intervention cuts incoming edges only (a single-node do).

## Result — PASS (HIT)
Causal battery 7/7: transitive causation (rain -> wetgrass -> slippery => rain causes slippery), asymmetry
(slippery does NOT cause rain), and INTERVENTION (do-operator): do(wetgrass) cuts wetgrass's incoming edges so rain
no longer causes slippery THROUGH it (and rain no longer causes wetgrass); an unrelated do(sprinkler) leaves rain
-> slippery intact. Prediction HIT; tally 36/55; 33 tests gated green. A genuinely distinct human faculty —
interventional/causal reasoning (Pearl's do-calculus, simplest qualitative form) — distinct from taxonomy because
intervention CUTS upstream causes. Established (causal graphs + do-operator), named; no novelty. HONEST: qualitative
graph (no probabilities); single-node intervention cutting incoming edges; confounding / counterfactual-probability
are a richer tier.
