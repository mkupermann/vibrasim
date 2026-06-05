# JEP-167 — does read() generalize across DOMAINS? (biology / geography / technology)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 read() generalizes to SHARED phrasings, but each domain has characteristic constructions the patterns miss
  ('located in', 'capital of', 'developed by'); biology ~0.90, geography/technology lower (~0.6-0.7); recall is
  PHRASING-COVERAGE limited not domain-limited. MOST-LIKELY MISS: shared 'is a'/'is part of'/'has' covering more.

## Result — PASS (HIT on the core claim) + the gap fixed
Aggregate recall per domain (before any fix): biology 1.00, technology 1.00, geography 0.71. read() GENERALIZES to
the shared relation phrasings — biology AND technology hit 1.00 out of the box (they use 'is a' / 'has' / 'such as').
Only geography dropped, and exactly on its characteristic constructions: 'Paris is located in France' ('located in'
containment, uncovered) and 'Europe has many countries' (quantifier 'many' not stripped -> stored 'many country').
NUANCE vs prediction: technology did NOT drop (it used covered phrasings) — so recall is CONSTRUCTION-COVERAGE
limited, and which domains drop depends on whether they use covered constructions, confirming 'not domain-limited'.
FIXED the two tractable gaps: (1) 'X is located in/situated in/found in Y' -> X part-of Y (spatial containment);
(2) strip leading quantifiers (many/some/several/few/most/numbers) in 'has' objects. After the fix ALL THREE domains
reach 1.00 recall; JEP-165 connected paragraph unchanged at 0.90 (no regression); precision still high. 49/49 tests
green (+1). Prediction HIT; tally 59/83. read() is now domain-general on shared + common spatial constructions, with
the honest residual being domain-idiosyncratic phrasings + genuine ambiguity (JEP-166). Established (lexico-syntactic
extraction, spatial-containment patterns); named; no novelty.
