# GEO-19 — Integrated learn-then-reason pipeline (the whole method, end-to-end, on held-out data)

## Motivation
GEO-6/11/12/15-18 each proved ONE piece. GEO-19 runs them as ONE system on held-out data to show the
"learning AND understanding method" works integrated, not just piecewise:
  (1) few-shot LEARN a new relation (city->country) as an offset in the LLM space,
  (2) APPLY it to UNSEEN cities (generalization of the learned relation),
  (3) CHAIN country->continent by geometric retrieval,
  (4) AGGREGATE "how many held-out cities are in <continent>?" with a symbolic count.

## Pre-registration (locked BEFORE run)
- 12 (city,country,continent). Split 6 train / 6 held-out cities.
- (1) learn offset r = mean(country_emb - city_emb) over the 6 TRAIN pairs.
- (2) for each HELD-OUT city: city_emb + r -> nearest country (among all 12 countries). acc1.
- (3) chain that country -> continent via retrieval over country-continent fact sentences. acc2 (on the
  predicted countries; also report oracle-country chain acc).
- (4) for each continent, symbolic count of held-out cities whose FULL chain lands there; exact-count acc.
- Bars: (2) learned-relation generalization >= 0.6; (3) chain >= 0.8 given correct country; (4) aggregate
  exact-count >= 0.6 end-to-end. Report all stages; honest about error propagation.

PASS if all three bars met (integrated method works on held-out data). PARTIAL otherwise with stage diagnosis.
