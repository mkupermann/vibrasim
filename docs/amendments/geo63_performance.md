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

## Result — INTERACTIVE on CPU
| N facts | index build | per-query (embed+retrieve) | throughput |
|---------|-------------|----------------------------|------------|
| 10 | 25 ms | 6.5 ms | 154 q/s |
| 100 | 121 ms | 7.1 ms | 142 q/s |
| 1000 | 1102 ms | 6.8 ms | 148 q/s |
| 1000 + rerank_k=10 | — | 23.9 ms | ~42 q/s |

**FINDING (characterization).** The system is INTERACTIVE on CPU at PC scale. Per-query latency is FLAT (~7ms,
~150 q/s) from 10 to 1000 facts — dominated by the query-embedding forward pass (~6ms), with the cosine
retrieval matmul negligible (1000x384 is tiny). Re-ranking adds ~17ms (24ms total, still interactive). Index
build is linear (~1ms/fact; 1000 facts = 1.1s, one-time). **Honest scope:** the flat per-query holds because
at N<=1000 the matmul is dwarfed by the embedding pass; at very large N (100k+) the linear scan would dominate
and need an ANN index (the GEO-22 scale note). At PC scale (hundreds-thousands of facts) the system answers in
real time (<25ms) on CPU — practical for interactive use.
