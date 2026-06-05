# JEP-283 — bare mass nouns (subjects AND connective-objects) take no article

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the recurring 'a flooding'/'a rain'/'a bacteria' residue: these are bare (article-less) mass/abstract nouns. The
  bare-SUBJECT scan (JEP-262) only matched a fixed verb list (missed 'Flooding happens') and didn't cover OBJECTS.
  Broadening to any verb + scanning bare objects of causal/mereological connectives (skipping article-led ones) fixes
  it, without breaking plurals or article-led countables ('a fever').

## Result — PASS (HIT)
Two scan extensions to the usage-learned no-article set: (1) a capitalized sentence-start word + ANY lowercase verb
is a bare singular subject (was a fixed verb list) -- catches 'Flooding happens', 'Disease spreads'; (2) a bare
(non-article-led, via negative lookahead) OBJECT of a causal/mereological connective ('because of rain', 'causes
erosion', 'consists of water') is mass/proper -> no article.
- 'Flooding happens because of rain. Disease spreads due to bacteria.' -> _no_article = {flooding, rain, disease,
  bacteria}; 'does rain cause flooding?' -> 'Rain causes flooding.' (both article-less, was 'A rain causes flooding').
- ARTICLE-LED PRESERVED: 'A virus causes a fever.' -> 'what causes a fever?' -> 'A virus causes a fever.' (the
  negative lookahead skips the article-led 'a fever' -> _countable keeps it countable). Plurals/countables unaffected.
120/120 regression tests green (test added). Prediction HIT; tally 162/198. This substantially closes the article
long-tail for mass/abstract nouns (the recurring 'a flooding'/'a death'/'a rust'-style residue across the causal/
functional passes). Established (usage-based article assignment), named; no novelty. The remaining residue is
gerund/abstract OBJECTS not adjacent to a scanned connective -- rare, cosmetic.
