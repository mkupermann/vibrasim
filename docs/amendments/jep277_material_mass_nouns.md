# JEP-277 — common metals/materials as mass nouns ('an iron'->'iron'), with polysemy override

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the recurring 'an iron'/'a copper'/'a gold' residue (materials as LIST ITEMS, which the bare-SUBJECT
  countability heuristic JEP-262 doesn't catch): common metals/materials are a closed mass-noun class. Adding them to
  _MASS_NOUNS fixes the articles; the _countable (article-led, JEP-256) override preserves the countable polysemy
  ('an iron' = the appliance).

## Result — PASS (HIT)
Added common metals/materials to _MASS_NOUNS (iron, copper, gold, silver, steel, aluminum/aluminium, bronze, brass,
tin, lead, zinc, nickel, salt, sugar, oil, coal, rust, concrete, cement).
- 'Iron, copper, and gold are metals.' -> 'Iron is a metal.' / 'Gold is a metal.' (no 'an iron'); 'Copper is part of
  bronze.' Also fixes the earlier 'Oxygen causes a rust' -> 'rust'.
- POLYSEMY preserved: 'An iron is an appliance.' -> _art(iron)='an iron' (the JEP-256 usage-led countability override
  beats the mass lexicon when the source uses an article).
114/114 regression tests green (test added). Prediction HIT; tally 156/192. Established (mass-noun lexicon + usage
override), named; no novelty. This addresses the recurring material-article residue across the chemistry/geography/
list passes; the general mass-noun-as-object case (e.g. 'a meat', 'a death') remains for non-material abstracts not
introduced as bare subjects -- minor (answer correct, only the article).
