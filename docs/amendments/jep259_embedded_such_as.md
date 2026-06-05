# JEP-259 — embedded ', such as X,' interjection ('Snakes, such as the cobra, are reptiles')

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 QA showed 'Snakes, such as the cobra, are reptiles' extracted NOTHING for snakes (the trailing such-as regex
  needs whitespace before 'such as' but the COMMA breaks it, and the embedded ', such as the cobra,' breaks the copula
  subject parse). Preprocessing the embedded interjection -> extract 'cobra is-a snake' + rebuild 'Snakes are reptiles'
  fixes both, without disturbing the trailing 'X such as A and B' form.

## Result — PASS (HIT)
The trailing-such-as handler (`{np}\s+such as ...`) failed on the comma ('snakes, such as'), and the copula handler
saw a non-bare-NP subject ('Snakes, such as the cobra'), so the sentence yielded NOTHING. Added an EMBEDDED-interjection
preprocessor: `^{np},\s*such as (.+?),\s*(.+)$` -> tell(example is-a subject) + rebuild `s = '{subject} {rest}'` and
fall through to the copula.
- 'Snakes, such as the cobra, are reptiles. A reptile is an animal.' -> cobra is-a snake (example), snake is-a reptile
  (main clause survives), so 'is a cobra an animal?' -> 'Yes. A cobra is a snake, a snake is a reptile, a reptile is
  an animal.' (a 4-hop chain THROUGH the example link).
- 'Birds, such as the eagle, can fly.' -> eagle is-a bird. No regression on trailing 'Reptiles such as snakes ...'.
100/100 -> 101/101 regression tests green (+1). Prediction HIT; tally 138/174. Established (appositive exemplification
parsing), named; no novelty. Residual real-prose items from this QA pass still open: 'can X fly?' singular ability
question; bare-subject-material mass nouns (the NER wall).
