# JEP-199 — mass nouns take no article in GENERATION (communication grammaticality)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 making _art omit the article for mass nouns ('tiredness' not 'a tiredness') improves describe/summarize
  grammaticality with no regression. RISK: a word both count and mass, but the curated set is conservative.

## Result — PASS (HIT)
Extended _MASS_NOUNS (added tiredness/happiness/health/evidence/research/pain/... the common abstract+uncountable
mass nouns) and made _art() omit the article when the head (last) word is a mass noun:
- _art('tiredness') -> 'tiredness'; _art('water') -> 'water' (no article).
- _art('dog') -> 'a dog'; _art('animal') -> 'an animal' (countable nouns unaffected, a/an phonetics preserved).
- 'what does a fever cause?' -> 'A fever causes tiredness.' (was the ungrammatical 'a tiredness'); describe/summarize
  likewise corrected.
NOTE: used a CURATED set, NOT suffix rules — suffix-based mass detection is unreliable (-ity: city/entity are
COUNTABLE; -ism: organism/mechanism countable; -ness: witness/harness/business countable). Improves the engine's
COMMUNICATION grammaticality (Michael's third verb) across all generative output. 68/68 regression tests green (+1).
Prediction HIT; tally 88/115. Established (mass/count distinction via lexicon, English article generation); named; no novelty.
