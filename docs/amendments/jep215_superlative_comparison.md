# JEP-215 — superlative comparison ('what is the biggest/oldest?')

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 'what is the biggest?' maps superlative->comparative ('biggest'->'bigger') and returns the top of that order
  (nothing exceeds it). RISK: irregular superlative->comparative mapping.

## Result — PASS (HIT)
Added a superlative-comparison handler: 'what is the <X>est?' -> map to the stored comparative (Xest -> X+'er', the
regular form) and return the TOP of that order (the item nothing exceeds). 'An elephant is bigger than a dog. A dog
is bigger than a cat... A grandfather is older than a father...' -> 'what is the biggest?' -> 'An elephant.'; 'what
is the oldest?' -> 'A grandfather.' (two distinct order relations, each with its superlative; partial order honestly
reported). Parallels superlative temporal (JEP-214); both reuse the transitive-order source/top computation. HONEST
LIMIT: regular superlative morphology only (biggest/oldest/smallest); irregular forms (best/worst/most) need a lexicon.
83/83 regression tests green (+1). Prediction HIT; tally 104/131. Established (extremum of a transitive order); named; no novelty.
