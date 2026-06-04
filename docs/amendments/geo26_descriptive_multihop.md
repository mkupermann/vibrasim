# GEO-26 — Does MULTI-HOP reasoning survive the lexical critique? (descriptive, non-lexical cues)

## Motivation
GEO-25 showed named-entity retrieval is lexically solvable. The strongest programme claim is multi-hop
reasoning (GEO-16/17). Its hop-1 used a shared person NAME — so was it just string matching? GEO-26 re-runs
2-hop with a DESCRIPTIVE cue that shares NO token with the person's fact, forcing semantic resolution at
hop-1. If the chain still works, multi-hop reasoning genuinely rests on the LLM geometry, not lexical
overlap.

## Pre-registration (locked BEFORE run)
- 10 people, each with a unique DESCRIPTION (role/trait, no name) + works-at + company-in-city facts.
- Query: a description -> resolve the person (hop0 semantic, no shared token) -> company (hop1) -> city
  (hop2). Compare geometric vs lexical token-overlap at the descriptive hop.
- Bars: geometric end-to-end >= 0.6; lexical at the descriptive hop << geometric (by >=0.3). Honest: if
  geometry fails too, multi-hop's headline was lexical — a valid deflation.

PASS if descriptive multi-hop holds for geometry and lexical collapses (the chain is semantic, not lexical).
