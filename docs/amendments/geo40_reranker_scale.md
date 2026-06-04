# GEO-40 — Cross-encoder re-ranking to recover retrieval accuracy at scale

## Motivation
GEO-22: 1-hop holds (0.98 at 400 facts) but multi-hop degrades (2-hop 0.87) as the candidate pool grows,
because bi-encoder retrieval picks wrong among many similar entities. The standard fix is a CROSS-ENCODER
RE-RANKER: retrieve top-k by embedding (fast), then re-score those k with a cross-encoder (accurate). GEO-40
tests whether re-ranking recovers accuracy at scale, extending the practical envelope.

## Pre-registration (locked BEFORE run)
- Reuse the GEO-22 synthetic store at N=400 (person->company, company->city).
- Bi-encoder baseline: nearest fact (as GEO-22).
- Re-ranked: bi-encoder top-k=10 -> cross-encoder (cross-encoder/ms-marco-MiniLM-L-6-v2) re-scores -> top-1.
- Metric: 1-hop and 2-hop accuracy, baseline vs re-ranked.
- Bar: re-ranked 2-hop >= baseline 2-hop + 0.05 (re-ranking helps) OR both already ~1.0 (no headroom).
  Report latency note. NULL if re-ranking does not help.
