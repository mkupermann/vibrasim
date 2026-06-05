# JEP-206 — answer natural WH questions over learned open relations

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 parsing 'what is the <relation> of <object>?' against learned relations and returning the subject answers 'what
  is the capital of France?' -> 'Paris'; generic 'what is X' unaffected. RISK: ordering vs the generic handler.

## Result — PASS (HIT)
respond() previously mis-answered open-relation WH questions ('what is the capital of France?' -> 'A capital of
france is France.'). Added an open-relation WH handler (BEFORE the generic 'what is'): parse 'what <connective>
<object>?', and if the connective is a learned relation, return the SUBJECT of the matching fact. Results (after the
relation is induced from >=2 examples):
- 'what is the capital of France?' -> 'Paris.'  ;  'what is the capital of England?' -> 'London.'
- 'what discovered relativity?' -> 'Einstein.'  (single-word learned relation 'discovered')
- 'what is the capital of Spain?' -> 'I don't know what is capital of a spain.' (relation known, object unknown)
- 'what is a dog?' -> 'A dog is a mammal.' (generic WH unaffected)
Open-relation subjects are rendered capitalized without an article (they are typically named entities — 'Paris',
'Einstein'). This COMPLETES the open-relation integration: LEARN (200) -> auto-INDUCE (201) -> query via relation_true
-> natural WH Q&A (206) -> communicate via describe (202). The engine can now learn a NEW relation from prose and
ANSWER NATURAL QUESTIONS about it, no transformer. 74/74 regression tests green (+1; the test needed >=2 'discovered'
examples for induction — caught honestly). Prediction HIT; tally 95/122. Established (template question parsing,
relational query); named; no novelty.
