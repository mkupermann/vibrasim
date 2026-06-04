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

## Result — PASS-as-designed (honest sharpening)
| query type | geometric-chain | symbolic DB-join |
|------------|-----------------|------------------|
| NAMED (exact key) | 1.00 | 1.00 |
| SEMANTIC-entry (epithet) | 1.00 | 0.00 |

**VERDICT: PASS-as-designed.** On NAMED structured data, geometric multi-hop EQUALS a database join — the
hops are symbolic lookups, geometry adds nothing for the composition. Geometry's genuine multi-hop value is
ONLY the SEMANTIC ENTRY (resolving an epithet/description to an entity), where a DB-join fails (no exact key,
0.00) and geometric retrieval succeeds (1.00). **'Geometric composition' on structured data = entity-resolution
+ database JOIN.** 14th self-correction.

## Maximally-sharpened honest claim (GEO-66 + GEO-68)
The irreducibly-geometric contribution is now narrowed to SEMANTIC MATCHING: resolving meaning (descriptions,
epithets, paraphrases) to entities/facts, and analogy-by-offset — things exact lookup, lexical match, a
database join, and a linear probe all CANNOT do (GEO-25b/31/5/68). Everything else is established classical
machinery: composition = database joins; aggregation/negate/compare/conflict = set logic; relation learning =
linear probe (GEO-66); grounding/abstention = thresholded retrieval (RAG). So: **the system = LLM SEMANTIC
MATCHING + classical symbolic/database reasoning + RAG grounding + a thin generator.** The LLM's genuine,
irreducible job is mapping meaning to the right entry; the reasoning on top is classical. This is the honest
core — real and useful, entirely established methods, precisely scoped.
