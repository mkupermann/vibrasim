# GEO-102 — Self-supervised adaptation on a LARGER real technical document

## Motivation
GEO-101 showed self-supervised adaptation helps modestly (+0.08) on a small controlled doc. The user's real
use is whole books/articles. GEO-102 tests adaptation on a LARGER real technical Wikipedia article (more
chunks, specialized vocabulary = genuine headroom) — does self-supervised SimCSE adaptation help MORE on a
realistic document?

## Pre-registration (locked BEFORE run)
- Fetch a real technical Wikipedia article (Mitochondrion). Ingest (chunk + embed). ~12 hand-written
  questions with known answer-snippets present in the article.
- Measure retrieval hits@1 over the article's chunks, BEFORE vs AFTER self-supervised adaptation (SimCSE, few
  epochs). rerank off (isolate the embedder).
- Metric: hits@1 before vs after. Bar: report both; adaptation helps if >= +0.05. Honest: ingestion =
  queryable (the deliverable); adaptation is the bonus, expected to help more here than on the small doc.

## Result — NULL (adaptation HURT on the large noisy doc)
| stage | retrieval hits@1 |
|-------|------------------|
| ingestion (864 chunks) before adaptation | 0.33 |
| after 3-epoch SimCSE adaptation | 0.17 |

**VERDICT: NULL/CAUTION.** On a large real article (864 chunks, much HTML noise), 3 epochs of SimCSE
adaptation HURT retrieval (0.33->0.17) — overfitting/representation collapse, and the noisy chunks degrade the
contrastive signal. The BEFORE (0.33) is already low (864 noisy chunks, no re-ranking). **Honest conclusion:**
self-supervised adaptation is FRAGILE — it helped the small clean doc (+0.08, GEO-101) but hurt the large
noisy one (-0.16). Naive adaptation is NOT a safe default. Ingestion-alone (queryable, + re-ranking GEO-56b)
is the robust path; adaptation needs careful tuning (1 epoch, clean chunks, dropout regularization) and is
risky on noisy real documents. So the DocumentLearner's reliable value is INGESTION (the content becomes
queryable); the self-supervised .adapt() is an experimental bonus that can hurt — use with care.
