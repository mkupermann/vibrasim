# GEO-68 — Is "geometric multi-hop composition" anything more than a database JOIN?

## Motivation
Following GEO-66's rigorous-deflation spirit. On STRUCTURED data with subject keys, multi-hop chaining
(person->team->city) is structurally a database JOIN; the geometry only resolves the ENTRY entity, then the
hops are symbolic lookups. GEO-68 tests whether geometric chaining is equivalent to a plain symbolic DB-join,
to honestly isolate where multi-hop NEEDS geometry (semantic entry, GEO-31) vs where it is just a join.

## Pre-registration (locked BEFORE run)
- person->team + team->city structured store (12 people).
- (a) geometric chain (GEO-16: retrieve person fact -> bridge -> retrieve city).
- (b) symbolic DB-join (resolve person by key, dict-lookup team, dict-lookup city). No embeddings after entry.
- Both on NAMED-entity queries and on SEMANTIC-entry queries (epithet/description).
- Metric: accuracy. Expectation: on NAMED queries (a)==(b)==1.00 (geometric chain = DB join, geometry adds
  nothing for the JOIN). On SEMANTIC-entry queries, (b) DB-join FAILS at entry (no exact key) while (a)
  geometric succeeds -> geometry's genuine multi-hop value is the SEMANTIC ENTRY, not the composition.
- PASS-as-designed if it cleanly separates these. Honest characterization.
