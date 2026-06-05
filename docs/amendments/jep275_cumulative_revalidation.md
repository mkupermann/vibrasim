# JEP-275 — cumulative re-validation after JEP-272..274 (comprehensive doc + fuzz)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the latest additions (quantified subjects 272, hyphenated-adj/inheritance 273, results-in causal 274) are
  guarded -> the engine stays comprehensive (a fresh all-construction doc incl. the new constructions ~>=0.9) AND
  robust (0 crashes).

## Result — PASS (HIT)
A fresh 14-sentence document exercising the NEWEST constructions (quantified 'All dogs are mammals' / 'Every mammal
is warm-blooded' / 'No fish is a mammal', 'defined as', 'results in', mereological verbs, object-WH, etc.): 12/13 =
0.92. The single miss: 'what does a dog chase?' -- 'chases' appears ONCE, below the >=2-occurrence open-relation
induction rule (by design, same as the capital-of case in JEP-266) -- NOT a regression. Fuzz: 0 crashes / 2000
random passages x 5 queries. So the cumulative prose hardening (254..274, 20 fixes / 8 construction profiles / 6
domains + COMMUNICATE) leaves the engine COMPREHENSIVE (the only doc misses are by-design single-occurrence open
relations) AND ROBUST (0 crashes). 113 unit tests green. Prediction HIT; tally 154/190. Established (cumulative
property-based + document-scale validation), named; no novelty. The real-prose extractor covers the common
declarative construction space; the bound remains the genre wall (conditionals/narrative) + NER/multi-word wall.
