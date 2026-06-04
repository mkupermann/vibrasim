# JEP-129 — learning a relation COMPOSITION rule from observation (the deepest structure frontier)

## Why
JEP-76 COMPOSED given relations; JEP-128 learned a relation's transitivity. The deepest frontier (JEP-69/70): learn
the COMPOSITION RULE itself from data — discover 'uncle = parent o sibling' from observed parent/sibling/uncle
facts, then predict unobserved uncle facts.

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 PARTIAL/PASS (>=0.85 held-out in the clean/dense regime): search candidate compositions R1 o R2 against
  observed target facts, pick the best-matching rule, apply to held-out. Degrades with sparsity / spurious
  matches. MOST-LIKELY MISS: a spurious composition coincidentally matching, or sparse data.

## Acceptance
- PASS: discovers the correct composition AND predicts held-out target facts >= 0.85 in the favorable regime.
  Established (inductive logic programming / rule discovery, simplest form), named; no novelty.

## Result — PASS (robust; I over-predicted the difficulty)
Clean: discovered 'uncle = parent o sibling' 1.00, held-out prediction 1.00. JEP-129b STRESS (distractor relations
+ noise):
| #distractors | correct-rule | held-out-acc |
|--------------|--------------|--------------|
| 0  | 1.00 | 1.00 |
| 3  | 1.00 | 1.00 |
| 8  | 1.00 | 1.00 |
| 15 | 1.00 | 1.00 |
| 8 + 20% label noise | 1.00 | 1.00 |

Composition-rule discovery is ROBUST: even with 15 spurious distractor relations and 20% label noise, the correct
rule wins (its composition matches the target with high F1 while random compositions match poorly — the signal
dominates). CALIBRATION: I predicted spurious matches as the most-likely miss; they did NOT fool it (over-predicted
the difficulty, like JEP-76/107). HONEST BOUNDS (the real frontier, untested): searches a SMALL space of 2-relation
compositions over GIVEN base relations; deeper/longer rules (3+ relations), a much larger relation vocabulary
(combinatorial blow-up), and LEARNING the base relations are the open limits. Within 2-composition discovery from
given relations, it's robust. A genuine, positive step on the JEP-69/70 'learn arbitrary structure' frontier. Tally
HIT (28/43). Established (rule discovery / ILP simplest form; consistency-based), named; no novelty.
