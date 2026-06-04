# GEO-70 — Where the transformer genuinely beats static: word-order / compositional meaning

## Motivation
GEO-69: static word vectors match the transformer on BAG-OF-KEYWORD descriptions (0.70 vs 0.80). But static
mean-pooling is order-blind — it should FAIL where word ORDER changes meaning (same words, different
relation), while the transformer captures syntax. GEO-70 isolates the transformer's genuine irreducible
contribution: compositional / word-order-sensitive matching.

## Pre-registration (locked BEFORE run)
- Pairs of queries with the SAME content words but different ORDER/role, mapping to DIFFERENT facts
  (e.g. "X is north of Y" vs "Y is north of X"; "the teacher of Z" vs "the student of Z").
- ~8 such order-sensitive query/fact pairs. Static (mean-pooled, order-blind) vs contextual transformer.
- Metric: hits@1 on the order-sensitive set. Bars: contextual >= 0.7 AND contextual >> static (static ~ 0.5,
  order-blind coin-flip between the two orderings). PASS-as-designed if the transformer genuinely beats static
  on word order — isolating its irreducible value.

## Result — INCONCLUSIVE (fact set too diverse)
contextual 0.88 = static 0.88. The facts differ in CONTENT words (Mexico vs US, etc.), so bag-of-words
distinguishes them even when order also differs — the test did not isolate word order. A clean test needs
2-way retrieval between facts with IDENTICAL bags differing only in order (GEO-70b).
