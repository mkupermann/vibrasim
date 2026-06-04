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
