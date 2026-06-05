# JEP-227 — alphanumeric concept names ('covid19', 'mp3', 'h2o') — the JEP-226 limitation, fixed

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 changing the concept regex from [a-z][a-z\- ]* to [a-z][a-z0-9\- ]* handles covid19/mp3/h2o while pure numbers
  ('4') stay non-concepts; no regression on numeric/comparison/temporal. RISK: a digit-containing token mis-parsed.

## Result — PASS (HIT)
Changed read()'s concept NP regex to LETTER-FIRST then alphanumeric. Now real concepts with digits are extracted:
- 'Covid19 is a virus. A virus is a microbe.' -> is_a(covid19, microbe) True (2-hop with an alphanumeric concept).
- 'Mp3 is a format.' -> is_a(mp3, format) True.
- Pure numbers stay numbers (the concept NP requires a LETTER first, so '4' in 'A dog has 4 legs' is not a concept —
  it's still parsed as the numeric attribute, num_attrs[(dog,leg)]=4). No regression on part-of/numeric/comparison/
  temporal (they match before, or require letter-first). This fixes the genuine limitation surfaced by JEP-226 (the
  [a-z]-only regex rejected alphanumeric names) — real prose has covid-19, mp3, h2o, b2b, 3d, etc. 90/90 regression
  tests green (+1). Prediction HIT; tally 115/142. Established (lexico-syntactic NP with alphanumeric tokens); named; no novelty.
