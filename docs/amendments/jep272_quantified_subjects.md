# JEP-272 — quantified subjects 'All/Every/Each X are Y' / 'No X is Y'

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 a quantified/negated QA pass showed 'All dogs are mammals' / 'Every mammal is warm-blooded' extracted NOTHING
  (the quantifier breaks the subject parse) and 'No fish is a mammal' uncaptured. Stripping universal-affirmative
  quantifiers (all/every/each -> is-a) + converting universal-negative 'No X is Y' -> 'X is not a Y' fixes them.

## Result — PASS (HIT)
Added quantifier preprocessing at the start of the sentence loop: 'No X is/are Y' -> 'X is not a Y' (universal
negative -> the engine's negative-fact path, JEP-164); else strip a leading 'all/every/each' (universal affirmative
-> the existing is-a path). 'Some' left as-is (existential, not universal).
- 'All dogs are mammals. A mammal is an animal.' -> dog is-a mammal; 'is a dog an animal?' -> Yes (transitive).
- 'No fish is a mammal.' -> fish is-NOT-a mammal; 'is a fish a mammal?' -> No.
- Regular is-a ('A shark is a fish') unaffected. 110/110 -> 111/111 regression tests green (+1).
Prediction HIT; tally 151/187. Established (quantifier handling, universal affirmative/negative), named; no novelty.
Residue: 'Every mammal is warm-blooded' -> the quantifier strips fine, but 'warm-blooded' (a HYPHENATED -ed adjective)
is not matched by the JEP-258 adjective-suffix property shape (-ous/-less/-ful/-ive/-ic/-al/-ent/-ant/-y) -> not yet
captured as a property. Narrow follow-up.
