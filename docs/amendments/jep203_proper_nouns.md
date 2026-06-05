# JEP-203 — proper-noun handling in generation (no article + capitalized)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 detecting mid-sentence Capitalized words as proper nouns lets _art render them without an article + capitalized
  ('France' not 'a france'); over a passage most are caught; sentence-start-only proper nouns may be missed.

## Result — PASS (HIT, with the predicted sentence-start limitation)
Added _detect_proper_nouns(): a word Capitalized MID-sentence (not at a sentence start, where capitalization is
ambiguous) is recorded as a proper noun; called from read/read_open/learn_relation. Converted _art/_join_phrases from
classmethods to instance methods so _art can consult self.proper_nouns: a proper noun renders Capitalized with NO
article. describe() now renders an open-relation object via _art too. Results:
- 'Paris is the capital of France. London is the capital of England.' -> proper_nouns = {france, england}.
- _art('france') -> 'France'; _art('dog') -> 'a dog' (common nouns + a/an phonetics unaffected).
- describe('paris') -> 'It is capital of France.' (the object proper noun capitalized; was 'a france'/'france').
HONEST LIMITATION (as predicted): SENTENCE-START proper nouns are NOT detected (capitalization is ambiguous there —
every sentence starts capitalized), so 'Germany is a country' leaves 'germany' a common noun ('A germany is a
country') unless Germany also appears mid-sentence elsewhere. Robust proper-noun detection needs NER (a learned model,
forbidden) or a gazetteer; the mid-sentence heuristic is the pragmatic no-transformer partial that catches most
proper nouns appearing as relation objects. 72/72 regression tests green (+1; updated the JEP-202 test for the now-
capitalized 'France'). Prediction HIT; tally 92/119. Established (capitalization-based proper-noun heuristic); named; no novelty.
