# JEP-174 — the full reasoning-faculty set composes with learn-from-prose (read knowledge is first-class)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the rich faculties (hypothetical, quantification, analogy, Boolean, three-valued, contradiction) work over
  read-knowledge identically to told-knowledge (read() populates the same structures). RISK: a faculty relying on
  structures read() doesn't populate.

## Result — PASS (HIT)
All probed faculties work over knowledge learned via e.read() identically to told facts, no code change needed:
- QUANTIFICATION: 'is every poodle an animal?' -> 'Yes.'
- HYPOTHETICAL: 'if a poodle were a fish, would it be an animal?' -> 'Yes. A poodle is a fish, a fish is an animal.'
  (with clean RETRACTION — 'fish' not left in the KB).
- BOOLEAN composition: 'is a poodle an animal and is a poodle not a fish' -> True.
- THREE-VALUED: 'is a poodle a vegetable?' -> 'I don't know whether a poodle is a vegetable.'
- CONTRADICTION detection: would_contradict('A poodle is not a dog.') -> flagged.
This confirms prose-learned knowledge is FIRST-CLASS: read() populates the same underlying structures (parents, the
is-a DAG, negatives) that tell() does, so the ENTIRE faculty set (not just is-a/part-of/causal queries) composes with
learn-from-sources. The engine doesn't just retrieve what it read — it reasons over it with the full cognitive
repertoire (quantification, counterfactual, Boolean, epistemic humility, belief-consistency). 56/56 regression tests
green (+1). Prediction HIT; tally 66/90. Established (uniform knowledge representation); named; no novelty.
