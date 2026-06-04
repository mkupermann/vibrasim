# GEO-44 — Mitigation: typo-robust entity resolution recovers noisy-store accuracy

## Motivation
GEO-43/43b: the noisy-store fragility is character-level typos (x near-duplicate names). The prescribed fix
is exact/fuzzy entity-ID resolution. GEO-44 validates it: add a character-n-gram fuzzy entity-resolution
front-end (match the query's entity to the closest stored entity NAME, then return that entity's fact) and
measure recovery vs pure embedding retrieval on the SAME noisy store.

## Pre-registration (locked BEFORE run)
- Reuse the GEO-43 noisy store (paraphrase + typos + near-duplicates).
- Baseline: pure embedding retrieval (GEO-43 noisy ~0.53).
- Mitigation: extract query entity name; fuzzy-match (character trigram Jaccard) to stored entity names
  (subjects, possibly typo'd); return the best-matched entity's fact. 
- Metric: 1-hop accuracy. Bar: mitigation >= 0.85 AND >= baseline + 0.25 (the front-end recovers accuracy).
  NULL if fuzzy matching doesn't help (typos too severe).

## Result — PASS (fragility solved)
| method (noisy store) | 1-hop |
|----------------------|-------|
| pure embedding | 0.53 |
| + character-trigram entity resolution | **1.00** |

**VERDICT: PASS.** A simple character-trigram fuzzy entity-resolution front-end fully recovers accuracy on
the noisy store (0.53 -> 1.00). The GEO-43 fragility is SOLVED. Validated design rule: **embeddings for
relevance/relations, fuzzy/exact NAME matching for entity identity.** Complete deployability arc: clean 1.00
-> typos 0.53 (GEO-43) -> cause = character corruption (GEO-43b) -> entity-resolution front-end 1.00
(GEO-44). The system is deployable on messy real data WITH a normalization/entity-resolution front-end — a
concrete, honest engineering prescription, not an unqualified claim.
