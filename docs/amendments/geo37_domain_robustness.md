# GEO-37 — Domain robustness: do the core findings replicate on DIFFERENT domains?

## Motivation
GEO-36 showed model-robustness. The findings also used one domain family (geography/animals). GEO-37 tests
DOMAIN robustness: replicate (1) zero-shot relational transfer on MATERIALS ordered by hardness (a different
ordinal attribute) and (2) semantic descriptive retrieval on INSTRUMENTS/TOOLS (different domain). If they
hold, the core claims generalize across domains; if not, they were geography/animal specific.

## Pre-registration (locked BEFORE run)
- (1) Zero-shot transfer: 20 materials ordered by Mohs-like hardness (talc..diamond); learn hardness-score on
  SEEN, test unseen-vs-unseen ordering; LLM-init vs random-init. Bar: LLM >= 0.70 AND >= random + 0.15.
- (2) Semantic retrieval: 10 "<tool> is used to <action>." facts; descriptive queries sharing no tool-name
  token ("the implement for driving nails" -> hammer fact). geometric vs lexical. Bar: geo >= 0.7 AND
  geo - lexical >= 0.3.
- PASS if both replicate on the new domains. PARTIAL/NULL honestly otherwise.
