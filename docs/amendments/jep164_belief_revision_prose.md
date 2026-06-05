# JEP-164 — belief revision from PROSE: read() handles correcting/conflicting sources

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 routing 'X is not a/an Y' from read() to the existing revision machinery lets the engine revise beliefs from a
  correcting passage (whale: fish->mammal, is_a(whale,fish)->False), maintaining coherence. RISK: negation parsing
  interfering with the positive copula handler (must match 'is not a' BEFORE 'is a').

## Result — PASS (HIT)
Extended read() to detect 'X is not a/an Y' (matched BEFORE the positive copula) and route it to tell(), which
retracts the belief + records a negative fact (the existing JEP-96 belief-revision / JEP-145 TMS path). Now realistic
sources that CORRECT or CONFLICT are handled:
- read('A whale is a fish.') -> is_a(whale,fish) True; then read('A whale is not a fish. A whale is a mammal.') ->
  is_a(whale,fish) FALSE (retracted), is_a(whale,mammal) True, is_a(whale,animal) True (re-derived via mammal).
- negation COEXISTS with positive facts (dog is-a mammal, dog NOT reptile); pronoun+negation composes ('A whale is a
  creature. It is not a fish.' -> is_a(whale,fish) False via recency coreference + negation).
This is human-like learning-from-sources: real sources err and get corrected, and the engine maintains a COHERENT
belief set across successive prose inputs. 48/48 regression tests green (+1). Prediction HIT; tally 57/80. Established
(belief revision / truth maintenance, lexico-syntactic negation patterns); named; no novelty.
