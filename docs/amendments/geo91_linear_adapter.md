# GEO-91 — Does a learned LINEAR ADAPTER improve retrieval over the frozen embedding?

## Motivation
Retrieval quality is the system's accuracy ceiling (GEO-80). The general embedder may be suboptimal for a
specific domain where queries and facts use different vocabulary. GEO-91 tests a CHEAP domain adaptation: a
learned linear projection (adapter) on FROZEN embeddings, trained on a few query<->fact match pairs, to align
them. Does it improve held-out retrieval vs the frozen model? (Linear probes capture structure, GEO-66 — but
does an adapter help retrieval, or is the frozen space already optimal?)

## Pre-registration (locked BEFORE run)
- A domain with a query/fact VOCABULARY GAP (queries colloquial, facts formal). ~16 query-fact pairs; split
  10 train / held-out test.
- Adapter: learn W (projection) maximizing cos(W q, W f) for matched pairs vs mismatched (contrastive).
  Apply W to both, retrieve.
- Metric: held-out retrieval hits@1, frozen vs adapted. Bar: adapted >= frozen + 0.1 (adapter helps). NULL if
  no improvement (frozen already optimal / too few examples). Honest either way.
