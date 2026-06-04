# JEP-130 — close the loop: install a LEARNED composition rule into the engine, reason with it

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: discover 'uncle = parent o sibling' (JEP-129), install via add_rule, and the engine derives uncle for
  NEW entities by composing stored parent+sibling facts; relation_holds correct on held-out. MOST-LIKELY MISS: the
  rule-derivation interface.

## Acceptance
- PASS: engine answers learned-rule relation queries 100% (derived correctly, no false positives). Established
  (Datalog-style rule application over learned rules), named; no novelty.

## Result — PASS (HIT)
Learned-rule reasoning 7/7: uncle derived via parent o sibling for NEW entities (alice->ann, bob->sue, alice->tom),
never stored; negatives correct (alice->sue, bob->tom, alice->carol, tom->ann all False). Prediction HIT; tally
29/44; 31 tests gated green. THE STRUCTURE-LEARNING THREAD IS UNIFIED with the engine: JEP-128 learns a relation's
transitivity, JEP-129 discovers a composition rule (robustly), JEP-130 INSTALLS the learned rule and the engine
derives new facts with it (Datalog-style rule application over LEARNED rules). Genuine, coherent progress on the
JEP-69/70 'learn arbitrary structure' frontier (mapped as NULL earlier) — the engine now learns relational
structure from observation AND reasons with it. HONEST: 2-relation composition rules over given base relations;
deeper rules + learned base relations remain the open frontier. Established (rule learning + Datalog application),
named; no novelty.
