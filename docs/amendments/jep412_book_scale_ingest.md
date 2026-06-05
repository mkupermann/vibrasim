# JEP-412 — Book-scale ingestion: performance + correctness on a large factual English text

## Motivation
Michael will ingest a real English book through the GUI. The largest test so far was ~50 sentences (JEP-395); a book
is 10–100× that. `read_text` reads every sentence and consolidates once at the end (closure materialization rebuilds at
a scaled dimension), so book scale could be slow or degrade reasoning. This tests a large factual English document
(~400 sentences) end-to-end: completion time, facts captured, coverage, and post-ingest Q&A reliability. No transformer.

## Method
Generate a large factual English document (~400 clear sentences: a deep taxonomy + properties + part-of + causal),
ingest via `Conversation.read_text` (auto-consolidates), and measure wall-clock time, facts learned, coverage, and a
deep multi-hop Q&A set, plus abstention.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: completes in reasonable time (< 60 s), high coverage, deep Q&A reliable after the single end-of-read
consolidation, abstention intact.

- **J412a (completes + scale):** ingest of ~400 sentences completes in < 60 s and learns ≥ 300 facts (consolidated to
  more), single seed (deterministic enough; report time).
- **J412b (Q&A reliable at book scale):** deep multi-hop is-a Q&A accuracy ≥ 0.90 on the ingested document, and OOD
  abstention = 1.0.
- **J412c (coverage):** sentence coverage ≥ 0.80.

If ingestion is too slow (> 60 s) or Q&A degrades at book scale, that is the honest finding to report (and a perf fix
to pre-register next). Bars fixed; no retuning. No transformer.

## Result
(filled after the run)
