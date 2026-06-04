# GEO-57 — Long-document QA: does retrieval+rerank hold as the document grows?

## Motivation
GEO-56 tested ~18 sentences. Real documents are longer; more sentences = more distractors. GEO-57 tests
whether document QA holds at ~40 sentences across many topics — combining the prose finding (GEO-56) with
the scale finding (GEO-22/40b). Uncertain: does accuracy degrade with document length, and does re-ranking
keep it up?

## Pre-registration (locked BEFORE run)
- ~40 sentences across 7 topics (cities, animals, tech, science). 14 questions with a known answer sentence.
- bi-encoder hits@1 vs bi-encoder+cross-encoder-rerank hits@1, over the 40-sentence pool.
- Bars: rerank hits@1 >= 0.8 AND >= bi-encoder (rerank holds accuracy at document length). Report both.
  NULL if accuracy collapses with length.
