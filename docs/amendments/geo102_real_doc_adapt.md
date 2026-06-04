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
