# JEP-278 — 'what are X?' (plural): subtypes-or-category + double-pluralization fix

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 a plural-question QA pass showed 'what are dogs?' -> 'I don't know any dogss.' -- a DOUBLE-pluralization
  ('dogs'+'s') in the enumeration fallback (it used m.group(1) raw, not the singularized cat) and no category answer.
  Using the singularized cat + answering the parent category when no subtypes exist fixes it.

## Result — PASS (HIT)
The enumeration handler answered 'what are X?' by listing subtypes, but for a plural X with no subtypes it returned
'I don't know any {raw}s' -> 'dogss' (double-plural). Two fixes: (1) the fallback now uses the singularized `cat`
(-> 'I don't know any dogs', not 'dogss'); (2) when X has no subtypes, answer the parent CATEGORY: 'what are whales?'
-> 'Whales are mammals.'
- 'what are whales?' -> 'Whales are mammals.' (no subtypes -> category). 'what are dogs?' -> 'A poodle.' (subtypes,
  members-first). 'what are mammals?' -> enumeration. 'what are zebras?' -> 'I don't know any zebras.' (no 'zebrass').
- Plural copula questions confirmed working: 'are dogs mammals?', 'are dogs animals?' (transitive), 'do dogs have
  hearts?', 'are hearts part of dogs?', 'how many legs do dogs have?' all answered correctly.
115/115 -> 116/116 regression tests green (+1). Prediction HIT; tally 157/193. Established (plural WH enumeration +
number morphology), named; no novelty.
