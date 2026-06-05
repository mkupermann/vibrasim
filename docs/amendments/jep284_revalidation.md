# JEP-284 — cumulative re-validation after JEP-281..283 (comprehensive doc + fuzz)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the newest additions (equivalence 281, subordinate causal 282, article long-tail 283) are guarded -> the engine
  stays comprehensive (a doc exercising them at ~1.0) AND robust (0 crashes).

## Result — PASS (HIT)
A fresh 12-sentence document exercising the NEWEST constructions (equivalence 'is the same as' + transitive,
quantified, possessive "dog's tail", functional 'used for', subordinate causal 'because of', 'results in', 3-item
lists): 10/10 = 1.00. Fuzz: 0 crashes / 2000 random passages x 4 queries. The cumulative prose hardening (254..283,
28 fixes / 12 construction profiles / 6 domains + COMMUNICATE + comprehensive article handling) leaves the engine
COMPREHENSIVE (1.00 on a fresh all-newest-construction doc) AND ROBUST (0 crashes). 121 unit tests green. Prediction
HIT; tally 163/199. Established (cumulative validation), named; no novelty. The real-prose extractor comprehensively
covers the common declarative construction space; the only remaining bounds are the genre wall (conditionals/
narrative) and the NER/multi-word-entity wall -- both bounded by the no-pretrained constraint.
