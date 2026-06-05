# JEP-163 — cross-sentence recency coreference in read() (close the 8th boundary case)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 recency-based resolution closes the common 'X is A. It is B.' pattern (-> 8/8 categories), but FAILS on
  ambiguity (two candidate antecedents, or 'it' = object not subject) — the honest bound that genuine coreference
  needs more than recency. RISK: over-eager resolution introducing false antecedents on multi-entity passages.

## Result — PASS (HIT, with the predicted honest bound)
read() now tracks the most-recent subject and resolves a sentence-initial pronoun (it/they/this/these/he/she) to it.
- WORKS (common case): 'A wolf is a canine. It is a mammal.' -> is_a(wolf,mammal) True; multi-hop to animal True.
  Closes the 8th prose-variation category -> read() handles 8/8 common variations.
- FP guard survives: 'A cat is a feline. It is independent.' adds NO is-a (adjective skipped post-resolution).
- HONEST BOUND (as predicted): recency is a heuristic. 'A dog is a mammal. A kennel is a shelter. It is an animal.'
  -> recency WRONGLY binds 'It'->kennel (FALSE POSITIVE is_a(kennel,animal)=True) and MISSES the intended
  is_a(dog,animal). Genuine multi-entity coreference needs semantics/agreement (gender, animacy, selectional
  restrictions), not recency — deferred (hard under no-transformer). So read() is robust on UNAMBIGUOUS prose and
  documents its coreference bound honestly. 47/47 regression tests green (+1). Prediction HIT; tally 56/79.
  This COMPLETES the read() robustness arc (JEP-161 boundary -> 162 shallow parse -> 163 coreference): 8/8 common
  prose-variation categories, with the genre gate (156), the compounding-under-extraction-noise bound (157b), and
  the multi-entity coreference bound (163) all characterized. Established (recency coreference / anaphora
  resolution heuristics); named; no novelty.
