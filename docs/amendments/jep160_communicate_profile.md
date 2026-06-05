# JEP-160 — COMMUNICATE what was learned: multi-relation English profile (closing the learn->understand->communicate loop)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the engine can generate correct multi-relation profiles by composing across is-a/part-of/causal with correct
  a/an and list aggregation; the main risk is surface-form (article/agreement) and coherently combining relation
  types — not the knowledge. MOST-LIKELY MISS: a surface-form slip or a relation-type mixed up (part-of as is-a).

## Result — PASS (HIT)
Extended describe() to include mereology (parts x has; what x is part of) and causal (effects x brings about; what
causes x), composed with the existing is-a + properties + SVO. After e.read(passage), describe() yields coherent
multi-relation English profiles, correct surface forms, relation types kept DISTINCT:
- describe('a dog')   -> "A dog is a mammal. That makes it also an animal. It has a heart."
- describe('a heart') -> "It has a cell. It is part of a dog."
- describe('a virus') -> "It causes an infection."
- describe('a fever') -> "It is caused by an infection."
Part-of is NOT rendered as is-a (a heart 'is part of a dog', never 'is a dog'). Closes the learn(read)->understand
(multi-hop/cross-relation)->communicate(profile) loop on knowledge learned FROM PROSE, no transformer. 44/44
regression tests green; wired into tools/demo_full_conversation.py. Prediction HIT; tally 53/76. Established
(template NL generation from structure); named; no novelty.
