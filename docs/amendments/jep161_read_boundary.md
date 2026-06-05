# JEP-161 — locating the NEXT boundary of read() on realistic prose variation

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 read() holds high precision on simple declaratives + 'such as' lists, but recall drops on conjoined subjects,
  plural-category 'X are Y', appositives, pronoun anaphora, multi-fact predicates. Boundary = SENTENCE COMPLEXITY
  (one-fact-per-bare-NP-clause works; multi-fact/embedded don't — the no-transformer constituency limit).
  MOST-LIKELY MISS: conjoined subjects or plural categories already handled.

## Result — PASS (HIT)
| variation | read() result |
|-----------|---------------|
| simple declarative ('A dog is a mammal') | OK 1/1 |
| kind-of ('A poodle is a kind of dog') | OK 1/1 |
| such-as list (3+ items) | PARTIAL 1/2 (a list-handling edge) |
| conjoined subject ('A lion and a tiger are cats') | MISS 0/2 |
| plural category ('Dogs are mammals') | MISS 0/1 |
| appositive ('A beagle, a kind of dog, is friendly') | MISS 0/1 |
| pronoun anaphora ('A wolf is a canine. It is a mammal') | MISS 1/2 |
| multi-fact predicate ('A whale is a mammal and an animal') | MISS 0/2 |

The boundary is SENTENCE COMPLEXITY, as predicted. read() extracts one fact per bare-NP clause but not multi-fact
or embedded structures. CRUCIAL NUANCE: several boundary cases — conjoined subjects, plural-category 'X are Y',
multi-fact predicates — are addressable with SHALLOW PARSING within the no-transformer constraint (split conjunctions,
treat bare-plural 'are' as is-a); appositives need light constituency; pronoun anaphora needs coreference (the engine
HAS _resolve_pronoun for tell() but read() splits sentences, losing the antecedent). So the next gate is partly
tractable (shallow parse) and partly genuinely hard (coreference/constituency under no-transformer). Prediction HIT;
tally 54/77. Established (shallow parsing / chunking limits); named; no novelty. Follow-up JEP-162 implements the
tractable shallow-parse extensions.
