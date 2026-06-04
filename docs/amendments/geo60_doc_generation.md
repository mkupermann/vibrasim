# GEO-60 — Grounded GENERATION over an unstructured document (full document-QA stack)

## Motivation
GEO-56 did retrieval over prose; GEO-34 did grounded generation over structured facts. GEO-60 combines them:
ingest an unstructured paragraph, retrieve the relevant sentence, and have the 0.5B LLM GENERATE a grounded,
faithful answer — the full document-QA-with-generation stack a user would actually use on a document.

## Pre-registration (locked BEFORE run)
- 1 factual paragraph (~6 sentences). 6 questions (answer in the text) + 2 unanswerable.
- Pipeline: sentence-split (add_document) -> retrieve (rerank) -> if grounded, LLM generates from the
  retrieved sentence with the faithfulness prompt; else abstain.
- Metric: (a) answerable answers contain the correct fact >= 0.7; (b) unanswerable abstain (no generation).
  PASS if both. NULL if generation breaks grounding.
