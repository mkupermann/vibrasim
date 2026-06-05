# JEP-280 — functional/purpose relations ('X is used for Y') + 'what is X used for?'

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 a functional QA pass showed 'A knife is used for cutting' NOT captured -- 'is used for' has the preposition
  'for', but 'for' was missing from the JEP-228 relational-preposition list, so 'is used for' was mis-treated as an
  is-a copula instead of an open relation. Adding 'for' (so it induces) + a 'what is X used for?' question handler
  fixes it.

## Result — PASS (HIT)
Two fixes: (1) added 'for' to the is_fixed copula-vs-open preposition list (JEP-228) -> 'is used for' is now an OPEN
relation (induced at >=2 occurrences), not a mis-parsed is-a. (2) Added a 'what is X <tail>?' handler that matches a
learned 'is <tail>' relation (e.g. 'is used for') and returns the object.
- 'A knife is used for cutting. A pen is used for writing. A car is used for transport.' -> 'is used for' induced;
  'what is a knife used for?' -> 'A knife is used for a cutting.' (cutting/writing/transport correct).
- Subject-side WH 'what is the capital of France?' -> 'Paris.' unaffected (the 'is <tail>' handler only fires for a
  learned relation; 'is of france' is not one, so it falls through).
117/117 regression tests green (test added). Prediction HIT; tally 159/195. Established (functional/purpose relations
as open relations; relational WH), named; no novelty. Residue: 'a cutting'/'a writing' (gerund objects get an article
-- the mass/gerund-as-object article long tail) -- answer correct, only the article.
