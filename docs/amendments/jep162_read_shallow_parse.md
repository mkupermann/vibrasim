# JEP-162 — shallow-parse extensions to read() (push past the JEP-161 boundary, no transformer)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 after the fixes read() handles conjoined subjects, plural-category, multi-fact predicates, appositives, and full
  such-as lists (recall 4/8 -> 7/8 categories), with PRONOUN ANAPHORA the lone remaining miss (needs cross-sentence
  coreference). KEY RISK: the permissive copula handler introducing FALSE POSITIVES (adjective predicates like 'are
  common' read as is-a) — guarded by 'bare predicate must be plural-noun (ends -s) or article-led'.

## Result — PASS (HIT)
read() boundary categories now handled: 7/8 (was 4/8). Added a general copula handler (conjoined subjects split on
'and'; multi-fact predicates split on 'and'; bare plural-noun predicate = is-a, article-led = is-a) + an appositive
rule + a pronoun-subject exclusion. Re-measured:
| variation | before | after |
|-----------|--------|-------|
| simple / kind-of / such-as | OK / OK / PARTIAL | OK / OK / OK |
| conjoined subject | MISS | OK (2/2) |
| plural category ('Dogs are mammals') | MISS | OK |
| multi-fact predicate ('a mammal and an animal') | MISS | OK (2/2) |
| appositive ('A beagle, a kind of dog, ...') | MISS | OK |
| pronoun anaphora ('It is a mammal') | MISS | MISS (lone gap) |

FALSE-POSITIVE GUARD verified: 'Dogs are loyal' / 'A cat is friendly' / 'Birds are warm-blooded' produce NO is-a
edges (adjectives don't end in -s, so the plural-noun heuristic correctly skips them) — a POS-free way to separate
noun is-a predicates from adjective property predicates. Also fixed ANOTHER singularization over-strip: '-ses' wrongly
stripped 'es' (horses->hors); now 'sses'->-es (glasses->glass) but '-ses'->-s (horses->horse, roses->rose). The lone
remaining boundary case (pronoun anaphora) needs cross-sentence coreference — read() splits sentences and loses the
antecedent; the engine HAS _resolve_pronoun for tell() but it is within-sentence. Deferred (genuinely harder under
no-transformer). 46/46 regression tests green (+2). Prediction HIT; tally 55/78. Established (shallow parsing /
lexico-syntactic patterns, POS-free heuristics); named; no novelty.
