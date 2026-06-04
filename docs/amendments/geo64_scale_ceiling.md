# GEO-64 — Interactive scale ceiling: where does the linear scan dominate?

## Motivation
GEO-63: per-query latency flat (~7ms) to 1000 facts. Beyond that the linear cosine scan (N x 384) grows.
GEO-64 finds the crossover — at what N does per-query latency leave the interactive range, telling the user
the honest ceiling for brute-force retrieval before an ANN index is needed.

## Pre-registration (locked BEFORE run)
- Build embedding matrices of N=1k/10k/50k (synthetic random unit vectors, skip text to isolate retrieval).
- Measure per-query retrieval (one matvec + argmax), mean of 50 queries, plus the fixed query-embed cost.
- Characterization: report latency vs N; flag the N where retrieval matmul ~ embed cost (~6ms) and where
  total > 100ms (interactive ceiling). The curve is the finding.
