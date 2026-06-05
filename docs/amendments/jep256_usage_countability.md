# JEP-256 — learn COUNTABILITY from usage (mass/count polysemy: 'a metal is an element')

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the chemistry QA showed 'metal' (in _MASS_NOUNS) used as a COUNTABLE taxonomy node renders article-less ('metal
  is an element'). Recording article-led concepts ('a metal') as countable, overriding _MASS_NOUNS in _art, fixes it
  without breaking genuine bare mass nouns ('water is a liquid'); residue = bare-subject materials ('copper') +
  sentence-start caps (the NL polysemy/NER wall).

## Result — PASS (HIT)
Mass/count is CONTEXT-DEPENDENT polysemy ('some metal' mass vs 'a metal' = a kind of metal, countable). The static
_MASS_NOUNS lexicon can't disambiguate. FIX: learn countability from the SOURCE's article usage — read() records every
concept introduced with 'a/an' into self._countable, and _art treats _countable heads as countable, OVERRIDING the
mass-noun list.
- 'A metal is an element. Copper is a metal.' -> 'a metal is an element' (metal countable, learned); _art(metal)='a metal'.
- 'Water is a liquid.' -> 'Water is a liquid' (water never article-led -> stays mass); _art(liquid)='a liquid'.
- Counter-examples hold: bare mass nouns unaffected -- _art(gravity)='gravity', _art(tiredness)='tiredness'.
97/97 -> 98/98 regression tests green (+1). Prediction HIT; tally 135/171. HONEST RESIDUE (exactly as predicted, the
NL wall): a bare-subject material introduced without an article ('Copper is a metal' -> sentence-start, no article to
learn from) still renders 'a copper' -- distinguishing it from a sentence-start proper noun or a countable needs a
lexicon/NER, the known limit (cf. JEP-203 sentence-start proper nouns). Established (usage-based countability,
data-driven lexical feature), named; no novelty.
