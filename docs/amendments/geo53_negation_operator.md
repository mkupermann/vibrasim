# GEO-53 — Negation queries end-to-end (symbolic set-complement closes the GEO-20 gap)

## Motivation
GEO-20: pure geometry is WEAK on negation (F1 0.50 — embeddings ignore "not"). The architecture says: detect
negation symbolically (router), answer via set-complement over the resolved store. GEO-53 builds and tests
the negation operator end-to-end: "Who is NOT on the Analytics team?", "Which people don't work in Boston?".

## Pre-registration (locked BEFORE run)
- 10 people -> team (+ team->city). Negation queries: "Who is not on the <team> team?" and "Who does not
  work in <city>?" (8 queries, known answer sets).
- Router: detect negation (not/n't/never/aren't/don't) -> NEGATE operator = set-complement of the positive
  filter. Positive filter resolves the constraint symbolically over meta.
- Baseline: pure-geometric (retrieve nearest, GEO-20 style) — expected to fail (ignores "not").
- Metric: set-F1 of returned people. Bars: symbolic >= 0.9 AND >> geometric baseline. PASS closes the gap.
