# JEP-217 — enumeration query ('what are all the X?')

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 'what are all the X?' lists all known concepts that is-a X (the inverse of multi-hop is-a). RISK: ordering vs the
  generic 'what' handlers.

## Result — PASS (HIT)
Added an enumeration handler: 'what are all the X?' / 'what are the kinds of X?' -> every concept c with is_a(c, X)
(transitively). 'A dog is a mammal. A cat is a mammal. A poodle is a kind of dog. A mammal is an animal. A robin is a
bird...' -> 'what are all the mammals?' -> 'A cat, a dog and a poodle.' (poodle included via MULTI-HOP poodle->dog->
mammal); 'what are all the animals?' -> all six (everything that is-a animal). Unknown category -> 'I don't know any
Xs.' Matched before the generic 'what' handlers ('what are' specifically). A genuinely-useful query type (enumerate a
category's members) = the inverse of the is_a closure. Minor cosmetic: irregular plurals ('fishs') in the not-found
message. 84/84 regression tests green (+1). Prediction HIT; tally 106/133. Established (inverse transitive-closure
enumeration); named; no novelty.
