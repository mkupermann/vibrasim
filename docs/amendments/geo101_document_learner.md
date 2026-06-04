# GEO-101 — Autonomous document learning + SELF-SUPERVISED adaptation (user request)

## Motivation
User request: "give the substrate a link/book/document and it learns the content with self-supervised
learning." GEO-101 builds + tests tools/document_learner.py: (1) INGEST a link/file/text (chunk + embed into a
queryable grounded store) — works end-to-end on real Wikipedia; (2) SELF-SUPERVISED ADAPTATION (SimCSE:
each chunk its own positive via dropout, in-batch negatives, NO labels) to tune the embedder to the document.
Honest test: does self-supervised adaptation IMPROVE retrieval over plain ingestion?

## Pre-registration (locked BEFORE run)
- A controlled document (~30 factual sentences) + 12 questions with known answer-sentences (so retrieval is
  measurable). Ingest -> measure retrieval hits@1. Then .adapt() (SimCSE, few epochs) -> re-measure.
- Metric: retrieval hits@1 before vs after self-supervised adaptation. Bars (honest): report both. If
  adaptation >= +0.05, it helps; if neutral/negative, plain ingestion is enough (consistent with GEO-91/92
  data-limits). Either way the INGESTION (queryable content) is the deliverable; adaptation is the bonus.
