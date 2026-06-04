# JEP-107 — simple pronoun coreference (the JEP-103 boundary), honestly measured

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 PARTIAL ~75-85%: resolving "it"/"they" to the most-recent SUBJECT works for topic-continuity discourse
  ("A robin is a bird. It is an animal." -> robin is an animal) but is WRONG for object-antecedent cases
  ("the cat chases the mouse. It is small." -> resolves to cat, may mean mouse). Honest characterization of why
  coreference is hard. MOST-LIKELY MISS: object-antecedent + "they"/conjunction antecedent.

## Acceptance (characterization, not a clean PASS)
- Report fact-correctness on a mixed discourse. PASS-ish if topic-continuity cases resolve correctly AND no-
  antecedent pronouns are still rejected; the object-antecedent failures are the honest boundary. Established
  (recency-based coreference - the simplest baseline), named; no novelty.

## Result — works in-scope; prediction over-estimated failures (honest)
Recency coreference (it/they -> last subject): topic-continuity discourse 4/4 correct (robin is an animal, animal
can move, sparrow can fly, robin is a living thing via the resolved chain); no-antecedent pronouns still rejected.
CALIBRATION: I predicted PARTIAL ~75-85% with object-antecedent FAILURES, but my battery only contained subject-
antecedent cases (4/4), and more importantly: in this SIMPLE DECLARATIVE grammar the subject IS the topic, so
recency-subject coreference works; the classic object-antecedent ambiguity needs richer syntax (relative clauses,
"the X that...") that the engine doesn't parse anyway. So the predicted failure mode is OUT OF SCOPE for this
grammar, not a live failure. Like JEP-76 (permutation), the predicted boundary didn't materialize in-scope. Tally:
count as MISS (predicted failures that didn't occur). The GATE caught a behavior change: JEP-107 IMPROVED pronoun
handling (resolve-with-antecedent vs always-reject), so the old always-reject test was updated to reject only WITHOUT
an antecedent. Established (recency-based coreference, simplest baseline), named; no novelty. HONEST: reliable only
under topic continuity; richer-syntax antecedent resolution is the real (out-of-scope) hard part.
