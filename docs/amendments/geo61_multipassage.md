# GEO-61 — Multi-passage context recovers document generation (top-k, not top-1)

## Motivation
GEO-60's main failure was retrieval picking the WRONG single sentence (then confident-wrong generation). The
standard RAG fix: give the generator the TOP-K retrieved sentences as context, so the right sentence is
present even if not ranked #1. GEO-61 tests whether top-3 multi-passage context recovers document generation.

## Pre-registration (locked BEFORE run)
- Same octopus paragraph + 6 answerable questions + 2 unanswerable (GEO-60).
- Pipeline: retrieve TOP-3 sentences -> concatenate as context -> 0.5B LLM generates with faithfulness
  prompt; abstain if top-1 sim < tau.
- Answer match: fair — accept numeric synonyms (8==eight, 3==three) since those are the same answer.
- Metric: (a) answerable correct >= 0.7; (b) unanswerable abstain. Compare to GEO-60 single-passage (0.17).
  PASS if multi-passage >= 0.7. Report the lift.
