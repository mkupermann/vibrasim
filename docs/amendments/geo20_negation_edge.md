# GEO-20 — Finding the EDGE: negation & comparison queries (designed to expose the weakness)

## Motivation
GEO-15–19 all saturated at 1.00 on clean facts — uninformative about limits. GEO-20 is designed to FIND a
failure: embedding-similarity retrieval is known to ignore NEGATION ("not in Europe" embeds ~like "in
Europe") and to be weak on COMPARISON (bigger/smaller). If the method fails here, that is the honest ceiling
and motivates the symbolic layer; if it survives, that is a surprising positive. Either outcome is a finding.

## Pre-registration (locked BEFORE run)
- 12 (city,country,continent) as GEO-19.
- (A) NEGATION query: "Which cities are NOT in Europe?" Pure geometric retrieval of the non-European set vs
  a symbolic-filter baseline. Score = set-F1 of returned non-European cities.
  - Pure-geometry method: rank cities by similarity to the query embedding; take those NOT nearest the
    'Europe' concept. (Tests whether geometry honours 'NOT'.)
  - Expected: pure geometry FAILS (low F1) because negation isn't encoded; symbolic filter over resolved
    continents = 1.0.
- (B) COMPARISON: 8 items with a numeric attribute (population, given as text). "Which has the larger
  population, X or Y?" over 12 pairs. Pure embedding similarity of the question to the two facts. Expected
  near-chance (embeddings don't compute >).
- Bars: this is an EDGE rung. PASS-as-designed if pure geometry is WEAK (negation F1 < 0.6 OR comparison <
  0.65) AND the symbolic layer fixes negation (F1 >= 0.9). Report raw numbers; NULL/positive both valid.
