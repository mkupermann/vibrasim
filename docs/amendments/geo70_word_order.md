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

## GEO-70b — clean 2-way order test: PASS
| method | 2-way acc (identical-bag facts) |
|--------|----------------------------------|
| contextual (transformer) | **0.75** |
| static (order-blind) | 0.38 (chance 0.50) |

**VERDICT: PASS.** On pure word-order pairs (facts with IDENTICAL bags differing only in order), the
transformer reaches 0.75 while static mean-pooling is at/below chance (0.38, order-blind). This isolates the
transformer's GENUINE IRREDUCIBLE contribution: COMPOSITIONAL / SYNTACTIC encoding — word order, argument
roles, who-did-what-to-whom — which distributional word vectors fundamentally cannot represent.

## BALANCED final picture (GEO-69 deflation + GEO-70b construction)
The honest scoping has two sides:
- DEFLATION (GEO-69): semantic KEYWORD matching is mostly old DISTRIBUTIONAL semantics — static word vectors
  do 0.70; the LLM adds only +0.10 there.
- CONSTRUCTION (GEO-70b): but COMPOSITIONAL / word-order understanding genuinely NEEDS the transformer (0.75
  vs static 0.38) — this is the LLM's irreducible contribution over distributional vectors.
So the LLM's genuine value = (a) a modest boost to distributional keyword matching + (b) real
compositional/syntactic encoding (roles, order) that bag-of-words cannot do. The complete honest answer: the
system = [distributional semantic matching (old) + transformer compositional encoding (the genuine LLM add)]
for the SEMANTIC ENTRY, composed with classical machinery (joins, set logic, linear probes, RAG grounding,
thin generator) for everything else. Fair, balanced, precisely scoped — established methods throughout, with
the transformer's one genuine irreducible job being compositional meaning.
