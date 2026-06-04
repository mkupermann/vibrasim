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

## Result — brute-force interactive to ~200k facts
| N | retrieval scan | total (+6ms embed) | |
|---|----------------|--------------------|--|
| 1,000 | 0.02 ms | 6.0 ms | INTERACTIVE |
| 10,000 | 0.18 ms | 6.2 ms | INTERACTIVE |
| 50,000 | 1.45 ms | 7.4 ms | INTERACTIVE |
| 200,000 | 6.05 ms | 12.0 ms | INTERACTIVE |

**FINDING — speed and accuracy ceilings are DIFFERENT.** Brute-force cosine retrieval stays interactive to
~200k facts (12ms/query; the BLAS matmul is ~6ms even at 200k x 384, where the scan finally equals the
query-embed cost). ANN is not needed for SPEED until ~1M+ facts. **The real scale limiter is ACCURACY, not
latency:** multi-hop retrieval precision degrades much earlier (GEO-22, 2-hop 0.87 at 400) — fixable with
re-ranking (GEO-40b). So the earlier "few hundred facts" envelope was about retrieval PRECISION, not speed.
Honest corrected picture: hold 100k+ facts and query in real time on CPU; invest in re-ranking / better
embeddings for precision, not in ANN, until you exceed ~1M facts.
