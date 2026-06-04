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

## Result — NULL/PARTIAL (incomplete application; clean diagnosis)
| method | 1-hop | 2-hop |
|--------|-------|-------|
| bi-encoder | 0.98 | 0.87 |
| re-ranked (hop-1 only) | **1.00** | 0.89 (+0.02) |

**VERDICT: NULL/PARTIAL** by the +0.05 2-hop bar. Diagnosis: re-ranking FIXED the hop it was applied to
(1-hop 0.98 -> 1.00) but I only re-ranked HOP-1; the 2-hop number is capped by the un-re-ranked HOP-2
retrieval, so it barely moved. Not a failure of re-ranking — an incomplete application. Re-ranking every hop
should recover 2-hop. Tested in GEO-40b. (Cross-encoder: ~8s for 400 queries x top-10 on CPU — modest.)

## GEO-40b result — PASS (re-rank EVERY hop -> scale limit mitigated)
| method | 2-hop @ N=400 |
|--------|---------------|
| bi-encoder | 0.87 |
| re-ranked BOTH hops | **1.00** |

**VERDICT: PASS.** Applying the cross-encoder re-ranker at EVERY hop recovers 2-hop accuracy from 0.87 to
1.00 at 400 facts. The GEO-22 scale degradation is MITIGABLE: bi-encoder retrieve top-k (fast) + cross-
encoder re-rank per hop (accurate) keeps multi-hop accuracy high as the store grows, at modest CPU latency
(~8s/400 queries/hop). Practical envelope extended beyond the bi-encoder-only few-hundred-fact limit.
Recommended for deployment when accuracy at scale matters (the earlier GEO-40 NULL was just hop-1-only).
