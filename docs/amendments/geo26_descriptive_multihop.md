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

## Result — INCONCLUSIVE (same lexical-overlap flaw)
geometric 2-hop = 1.00, lexical at descriptive hop = 1.00. Flaw: the description string was reused VERBATIM
inside the persona fact ("<desc> is Alice."), so the cue shares all its tokens with the fact and lexical
wins trivially — exactly the GEO-25 issue, not fixed here. A clean non-lexical multi-hop test needs cues the
LLM can resolve from REAL-WORLD knowledge (not restated in a fact), which is hard to construct for invented
people. **The clean non-lexical evidence therefore stands at GEO-25b (geometry 0.80 vs lexical 0.10 on real
entities).** Honest conclusion: the multi-hop CHAINING + symbolic-bridge machinery works regardless; whether
each hop needs geometry or is lexically trivial depends on the data — with genuine semantic cues geometry
adds value (GEO-25b), with shared-token cues lexical suffices. GEO-26 recorded as inconclusive, no claim.
