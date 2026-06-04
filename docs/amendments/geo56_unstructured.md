# GEO-56 — QA over UNSTRUCTURED text (raw paragraphs, not pre-structured facts)

## Motivation
All prior tests used pre-structured facts. Real documents are unstructured prose. GEO-56 tests whether the
geometric layer answers questions over RAW paragraphs: split into sentences, embed, retrieve the relevant
sentence, ground the answer + abstain when unsupported. This is the real-document use case (RAG over prose).

## Pre-registration (locked BEFORE run)
- 3 short factual paragraphs (~6 sentences each) on distinct topics (a city, an animal, a technology).
- 12 questions whose answer is a specific sentence (+ 4 unanswerable questions for abstention).
- Method: sentence-split all paragraphs into one store, retrieve nearest sentence per question; abstain if
  below calibrated tau.
- Metric: (a) answerable retrieval hits@1 (correct sentence) >= 0.75; (b) unanswerable abstain >= 0.6.
  PASS if both. Tests the system on unstructured prose, not clean templates.

## Result — PARTIAL
| metric | value |
|--------|-------|
| (a) answerable retrieval hits@1 | 0.67 (bar 0.75) |
| (b) unanswerable abstain | 1.00 (bar 0.6) |

**VERDICT: PARTIAL.** On unstructured prose the system abstains perfectly (1.00) but answerable retrieval is
0.67 — below the structured-fact ~1.0, because questions align less cleanly with the answer sentence (e.g.
"Are SSDs faster than hard drives?" can retrieve a different SSD sentence). Honest: bi-encoder retrieval over
prose is harder than over templated facts. The validated cross-encoder re-ranker (GEO-40b) targets exactly
this; tested in GEO-56b.
