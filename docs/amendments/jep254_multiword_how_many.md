# JEP-254 — multi-word attribute in the 'how many' QUESTION (completing the fix-in-every-parser set)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 real-usage QA on a new-domain (chemistry) passage surfaced 'how many hydrogen atoms does water have?' -> 'I
  cannot parse': the 'how many (\w+)' question captures ONE word. Extending it to a multi-word attribute keyed by the
  HEAD noun (as JEP-229 capture + JEP-231 comparison already do) fixes it, no regression on single-word 'how many legs'.

## Result — PASS (HIT)
Surfaced by real-usage QA (the mode that found JEP-228..231): the multi-word-attribute handling was added to numeric
CAPTURE (229) and COMPARISON (231) but the 'how many X' QUESTION parser was MISSED — the recurring 'fix a surface
pattern in EVERY parser' lesson (error-class 1/8, JEP-94/99). Changed `how many (\w+) does` to
`how many ((?:\w+\s+)*\w+) does`, keyed by the head noun (last word).
- 'how many hydrogen atoms does water have?' -> 'Water has 2 hydrogen atoms.' (multi-word, head 'atom').
- No regression: 'how many legs does a dog have?' -> 'A dog has 4 legs.'; 'how many moons does Jupiter have?' ->
  '...4 large moons.' (JEP-229 modifier rendering intact).
95/95 -> 96/96 regression tests green (+1). Prediction HIT; tally 133/169. The multi-word-attribute handling is now
consistent across all THREE numeric parsers (capture 229 / comparison 231 / question 254). Established (NP head-noun
extraction), named; no novelty. Honest residue from the same QA pass (logged for follow-up): polysemous mass nouns
used as countable taxonomy categories ('a metal is an element' -> 'metal' is in _MASS_NOUNS so renders article-less),
mass-noun articles in open-relation/causal rendering ('the bronze', 'a corrosion'), and PASSIVE causal 'X is caused
by Y' not extracted (-> JEP-255).
