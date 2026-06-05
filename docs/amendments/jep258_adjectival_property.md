# JEP-258 — capture 'X is <adjective>' as a PROPERTY (completing JEP-257)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 JEP-257 stopped '-ous' adjectives becoming spurious is-a parents but left 'X is venomous' uncaptured ('is a
  cobra venomous?' -> unknown). Capturing a bare adjectival copula predicate as a PROPERTY (properties[X].add(adj))
  + answering 'is X <adj>?' from properties makes it 'Yes. A cobra is venomous.', without disturbing is-a.

## Result — PASS (HIT)
read()'s copula handler now routes a bare ADJECTIVE predicate (matching an adjective-suffix shape -ous/-less/-ful/
-ive/-ic/-al/-ent/-ant/-y) to PROPERTIES instead of skipping it; explain()/respond() answer 'is X <adj>?' from
properties when the is-a verdict is not 'yes'.
- 'The cobra is venomous. A dog is friendly.' -> properties {cobra:{venomous}, dog:{friendly}}.
- 'is a cobra venomous?' -> 'Yes. A cobra is venomous.'; 'is a dog friendly?' -> 'Yes. A dog is friendly.'
- 'is a cobra friendly?' -> unknown (correct: not a property of cobra). is-a unaffected (is_a count excludes the adjectives).
99/99 -> 100/100 regression tests green (+1). Prediction HIT; tally 137/173. The 257->258 pair fully fixes adjectival
predicates: NOT a false is-a (257) AND captured as a queryable property (258). Honest residue: the negative rendering
'is a cobra friendly?' -> 'I don't know whether a cobra is a friendly' still articleizes the adjective (cosmetic).
Established (copula property predication + adjective morphology), named; no novelty.
