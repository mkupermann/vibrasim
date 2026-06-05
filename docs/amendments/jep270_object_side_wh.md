# JEP-270 — object-side open-relation WH question ('what does a carnivore eat?')

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 'A carnivore eats meat' induces the open relation 'eats' (>=2 occ) and stores the fact, but 'what does a
  carnivore eat?' is mis-parsed (only the SUBJECT-side WH 'what is the capital of France?' existed). Adding an
  OBJECT-side handler 'what does X VERB?' -> the object of the learned verb relation fixes it.

## Result — PASS (HIT)
The open-relation WH handler only answered SUBJECT-side ('what is the capital of France?' -> Paris). Added an
OBJECT-side handler: 'what does X VERB?' -> find the object O where (X, rel, O) is a learned fact (matching the verb
to its 3rd-person relation form eat/eats/builds via verb / verb+'s' / verb+'es').
- 'what does a carnivore eat?' -> 'A carnivore eats a meat.'; 'what does a herbivore eat?' -> '...a plant.';
  'what does a robin build?' -> 'A robin builds a nest.'
- Subject-side WH 'what is the capital of France?' -> 'Paris.' unaffected (no regression).
109/109 -> 110/110 regression tests green (+1). Prediction HIT; tally 149/185. Established (relational WH question
answering, both argument positions), named; no novelty. Residue: 'a meat' (mass-noun-as-OBJECT not caught by the
bare-subject countability heuristic JEP-262, which only marks subjects) -- the answer is correct, only the article.
