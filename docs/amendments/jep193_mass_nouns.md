# JEP-193 — extract mass/uncountable nouns as is-a parents (the JEP-192 caveat)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 a curated mass-noun set lets 'A seat is furniture' extract (stool->seat->furniture chains), no precision
  regression (mass nouns are unambiguously nouns). RISK: an adjective/mass-noun ambiguous word.

## Result — PASS (HIT)
Added a curated _MASS_NOUNS set (furniture/water/information/equipment/music/matter/energy/metal/glass/data/... 26
common uncountables) and accept a bare predicate as an is-a parent if it is plural (-s) OR a known mass noun. Results:
- 'A seat is furniture. Furniture is an object. A stool is a seat.' -> seat is_a furniture True; stool is_a object
  True (chains stool->seat->furniture->object, fixing the JEP-192 'is a stool furniture?' miss).
- 'Ice is water', 'A cpu is hardware' -> extracted.
- PRECISION preserved: adjective predicates still rejected ('Dogs are loyal' -> is_a(dog,loyal) False; 'A cat is
  friendly' -> False) — the plural-noun heuristic + curated mass-noun set together separate nouns from adjectives
  without a POS tagger. 62/62 regression tests green (+1). A real recall gain on the mass-noun class at no precision
  cost. Prediction HIT; tally 82/109. Established (NP chunking, mass/count distinction via lexicon); named; no novelty.
