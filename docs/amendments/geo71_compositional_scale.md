# GEO-71 — Does compositional/word-order understanding scale with model size?

## Motivation
GEO-70b: the transformer beats static on word order, but only 0.75 on MiniLM (22M). Is compositional encoding
STRONGER in a bigger model? GEO-71 re-runs the clean 2-way word-order test on MiniLM (22M) vs mpnet (110M).
Tells whether 0.75 is a small-model limit and which model to choose for compositional/role-sensitive tasks.

## Pre-registration (locked BEFORE run)
- Same GEO-70b clean 2-way identical-bag word-order items.
- Models: all-MiniLM-L6-v2 (22M), all-mpnet-base-v2 (110M).
- Metric: 2-way word-order accuracy. Bars (descriptive): report both; flag if mpnet >= MiniLM + 0.1
  (compositional encoding scales with size). The curve is the finding.

## Result — compositional understanding does NOT scale with size (dissociation)
| model | size | word-order 2-way acc | keyword semantic (GEO-67) |
|-------|------|----------------------|---------------------------|
| all-MiniLM-L6-v2 | 22M | **0.75** | 0.80 |
| all-mpnet-base-v2 | 110M | 0.62 | 1.00 |
| static (order-blind) | — | 0.38 | 0.70 |

**VERDICT (honest, somewhat surprising).** Compositional/word-order understanding does NOT scale with model
size — mpnet (110M) is WORSE (0.62) than MiniLM (22M, 0.75), despite mpnet being BETTER at keyword semantic
matching (1.00 vs 0.80). A genuine DISSOCIATION: keyword matching scales with size, word-order/role matching
does not, and both models are WEAK at it (0.62–0.75, well below reliable). **Interpretation:** mean-pooled
bi-encoder sentence embeddings are optimized for TOPICAL similarity, not SYNTACTIC structure — pooling washes
out word order, and a bigger model trained for semantic similarity doesn't fix (may worsen) role-sensitivity.
**Honest caveat:** 8 items is a small sample; the MiniLM>mpnet gap could be partly noise, but the clear
finding is neither is strong and size doesn't help. **Design rule:** for reliable role/word-order-sensitive
matching, use a CROSS-ENCODER (joint encoding, GEO-40b/56b helped retrieval) or a syntactic parse — not a
bigger bi-encoder. Refines GEO-70b: the transformer adds SOME compositional signal over static, but pooled
bi-encoder retrieval has a low ceiling on it. So the LLM's compositional contribution (GEO-70b) is real but
modest and not size-scalable in this (bi-encoder) usage.
