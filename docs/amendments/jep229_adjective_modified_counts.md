# JEP-229 — adjective-modified count nouns ('4 large moons', 'two small parts')

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 allowing optional adjectives before the head noun (keyed by last word, connective-guarded) captures
  '4 large moons'->moon=4 and renders '4 large moons', with no regression on '4 legs'/'1 moon'. RISK: the
  connective guard or head-noun choice mis-fires on a list ('4 legs and a tail').

## Result — PASS (HIT)
Extended the numeric-attribute regex from 'has N <word>' to 'has N <modifier>* <head>', keyed by the HEAD noun
(last word, singularized) with the modifier phrase stored for faithful rendering. Surfaced as residue by JEP-228;
adjective-modified count nouns are extremely common in real prose ('two small cells', 'three large planets').
- 'Jupiter has 4 large moons.' -> num_attrs[(jupiter,moon)]=4; 'how many moons does Jupiter have?' -> '...4 large moons.'
- 'A cell has two small parts.' (number-word + adjective) -> (cell,part)=2; renders '2 small parts'.
- No regression: '4 legs' -> 4, '1 moon' -> singular.
- CONNECTIVE GUARD works: 'A spider has 8 legs and a tail' is NOT captured as a count (and/or/of/with/that/which/but
  in the remainder -> it's a list/clause, falls through to the part-of-via-possession handler, exactly as before).
  Predicted-risk verified safe: the guard prevents the wrong 'spider has 8 tails'.

92/92 -> 93/93 regression tests green (+1). Prediction HIT; tally 117/144. Honest residue still open (logged): mass-noun
'gravity'->'a gravity'; sentence-start proper nouns ('A jupiter'). Established (NP head-noun extraction with premodifiers);
named; no novelty.
