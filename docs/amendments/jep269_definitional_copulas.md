# JEP-269 — definitional copulas 'X is defined as / means / is known as Y' -> X is-a Y

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 a definitions QA pass showed 'A mammal is defined as a warm-blooded animal' / 'A puppy means a young dog' / 'A
  dog is also known as a canine' extracted nothing -> the questions returned No/unknown. These definitional copulas
  all map to IS-A (the genus head noun); adding them + reducing the definiens to its head noun fixes it.

## Result — PASS (HIT)
Added a definitional-copula pattern BEFORE the general copula: 'X is defined as Y' / 'X means Y' / 'X is (also) known
as Y' / 'X refers to Y' -> tell(X is-a Y), with the definiens reduced to its GENUS head noun ('a warm-blooded
animal'->'animal', 'a young dog'->'dog').
- 'A mammal is defined as a warm-blooded animal.' -> mammal is-a animal. 'A puppy means a young dog.' -> puppy is-a
  dog. 'A dog is also known as a canine.' -> dog is-a canine.
- TRANSITIVE: 'is a puppy an animal?' -> 'Yes. A puppy is a dog, a dog is a mammal, a mammal is an animal.'
- Regular is-a + adjective-not-is-a unaffected (108/108 -> 109/109 tests green, +1).
Prediction HIT; tally 148/184. Established (definitional/genus-differentia subsumption, lexico-syntactic patterns),
named; no novelty. Honest residue from this pass: 'eats' as an open relation question ('what does a carnivore eat?'),
and relative-clause 'an animal that eats plants' (the 'eats' VP). NL-wall residuals unchanged.
