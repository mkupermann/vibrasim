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

## Result — NULL (no cheap improvement; use the shipped levers)
| method | held-out hits@1 |
|--------|-----------------|
| frozen embedding | 0.83 |
| + learned linear adapter (10 train pairs) | 0.83 |

**VERDICT: NULL.** A cheap linear adapter on frozen embeddings does not improve domain retrieval — the frozen
general space is already near-optimal for the colloquial->formal vocabulary gap, and 10 training pairs are too
few for a useful DxD projection (or it overfits). So the retrieval bottleneck (GEO-80, the system's accuracy
ceiling) is NOT cheaply improvable via few-shot linear adaptation. **The working retrieval-improvement levers
remain the ones already shipped:** (1) a better base model (all-mpnet-base-v2, GEO-36/67), (2) cross-encoder
re-ranking (GEO-40b/56b/72), (3) entity-resolution for noisy stores (GEO-44). Domain fine-tuning MIGHT help
with much more data and a proper contrastive objective (not tested — out of "cheap" scope). Honest negative:
don't expect a quick adapter to fix retrieval; invest in model choice + re-ranking. Reinforces simpler-is-
robust (GEO-87/88) — the shipped levers beat a bespoke adapter.
