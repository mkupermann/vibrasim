# GEO-63 — Performance benchmark: indexing + query latency at scale

## Motivation
The programme assumes embedding retrieval is cheap but never measured it. GEO-63 benchmarks the practical
performance envelope on this CPU: index-build time and per-query latency (embed query + retrieve) at
N=10/100/1000 facts, with and without re-ranking. Tells the user whether it is real-time or batch.

## Pre-registration (locked BEFORE run)
- Build stores of N=10/100/1000 synthetic facts; measure: (a) one-time index build (embed all facts),
  (b) per-query latency = embed query + cosine retrieve (mean of 20 queries), (c) per-query with rerank_k=10.
- Characterization rung: report the numbers (the curve is the finding). Flag if per-query > 100ms (not
  interactive) or index build superlinear. No pass/fail tuning.
