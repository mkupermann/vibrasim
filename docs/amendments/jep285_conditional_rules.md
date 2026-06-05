# JEP-285 — conditional RULES 'If X is a Y, then it is/can Z' (the structured edge of the conditional genre)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 conditionals are the genre wall, but a UNIVERSAL RULE 'If [something] is a Y, then it is/can Z' is structured:
  it means category Y has the consequent property/is-a. Rewriting it to 'a Y <consequent>' feeds the existing
  handlers, so the rule becomes a category property that INHERITS to subtypes (JEP-273).

## Result — PASS (HIT)
Added a conditional-rule preprocessor: 'If [something/an X/it/the X] is a Y, [then] it <consequent>' -> rewrite to
'a Y <consequent>' (the universal rule attaches the consequent to category Y), then the existing copula/ability/
property handlers process it.
- 'If an animal is a mammal, then it is warm-blooded.' -> mammal property warm-blooded; 'is a dog warm-blooded?' Yes
  (INHERITED dog->mammal). 'If something is a bird, it can fly.' -> bird ability fly; 'can a robin fly?' Yes
  (inherited robin->bird).
121/121 regression tests green (test added). Prediction HIT; tally 164/200. This cracks the STRUCTURED, universal
edge of the conditional 'if-then' genre (rules over categories); FULL propositional conditionals about specific
events ('if it rains then the ground gets wet') remain the genre wall (propositions, not concept-relations).
Established (universal conditional rules = category predication; defeasible inheritance), named; no novelty.
