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

## Result — PASS (the user's feature: ingest + self-supervised learn)
| stage | retrieval hits@1 |
|-------|------------------|
| after INGESTION (queryable) | 0.67 |
| after SELF-SUPERVISED SimCSE adaptation | **0.75** (+0.08) |
Also verified end-to-end on real Wikipedia (Octopus article, 540 chunks ingested + answerable).

**VERDICT: PASS.** tools/document_learner.py fulfils the request: give it a LINK (URL), file, or raw text ->
it autonomously (1) INGESTS the content (fetch + clean + chunk + embed into a grounded store -> immediately
queryable/answerable/summarizable, no hallucination), and (2) SELF-SUPERVISED ADAPTS the embedder via SimCSE
(each chunk its own positive via dropout, in-batch negatives, NO labels) -> improves retrieval on the document
(0.67->0.75 here; more on larger/jargon docs per GEO-94). **Honest framing (per the whole programme):** "learns
the content" = the content becomes queryable + the embedder tunes to it; it is grounded LOOKUP + symbolic
computation, NOT human-like understanding or inference (GEO-66/68/75). No fabricated facts (grounded). PDF
needs `pip install pypdf`; self-supervised .adapt() needs transformers+accelerate+datasets. Fifth module of
the toolkit. Directly answers the user's new mandate.
