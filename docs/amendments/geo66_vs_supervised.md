# GEO-66 — Does the geometric framing beat a plain supervised baseline on embeddings?

## Motivation
The programme frames relation learning geometrically (offset/ranking/TransE). Honest deflation risk: maybe a
PLAIN supervised model (logistic regression / linear probe) on the same embeddings does just as well, in
which case "geometric" adds nothing over standard ML. GEO-66 compares head-to-head on (a) few-shot relation
learning and (b) zero-shot transfer to unseen entities — the cases where geometry should have an edge.

## Pre-registration (locked BEFORE run)
- (a) Few-shot ordinal (animal size): geometric ranking-offset vs logistic-regression pairwise classifier
  (trained on (emb_i - emb_j) -> sign), at k=4/8 training pairs. Held-out pair accuracy.
- (b) Zero-shot transfer to UNSEEN entities (GEO-27b setup): geometric ranking-projection vs the same
  logistic pairwise classifier, on unseen-vs-unseen pairs.
- Metric: accuracy, geometric vs supervised. Bars (honest, descriptive): report both. If supervised >=
  geometric on both, the geometric framing is NOT necessary (deflation). If geometric >= supervised
  (esp. few-shot/zero-shot), the framing earns its place. NULL/PASS/deflation all valid.
